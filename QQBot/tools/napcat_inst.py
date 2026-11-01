#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NapCat 多实例管理（systemd 模板）。

一个 QQ 号 = 一个 NapCat 实例 = 一套 systemd 单元：
    napcat@<uin>.service   QQ 主进程
    xvfb@<n>.service       该实例专属的虚拟显示

★ 为什么能这样隔离（实测 napcat.mjs:30463-30472 的路径解析链）：
    process.env.NAPCAT_WORKDIR ? r = WORKDIR
      : n ? r = join(NAPCAT_QQ_DATA_DIR, "NapCat")
      : darwin ? ...
      : r = binaryPath
    configPath = join(r, "config")     ← 配置跟着 WORKDIR 走
    staticPath = join(binaryPath, "static")  ← 静态资源恒定，QQ 本体可共享

  ⇒ QQ 的 614MB 本体只需一份；每实例独立 HOME（隔离登录态）+ WORKDIR（隔离配置）
    + DISPLAY（隔离 X 会话）。

★ 端口分配（避开 rcbot 的 6710）：
    WebUI  = 6099 + index
    OneBot = 6700 + 2 * index      ← 6700/6702/6704… 永远碰不到 6710

用法：
    python3 tools/napcat_inst.py plan                 列出计划
    python3 tools/napcat_inst.py add <uin>            新增实例（建目录+写配置+启动）
    python3 tools/napcat_inst.py remove <uin>         移除实例
    python3 tools/napcat_inst.py migrate <uin>        把现有实例迁到模板
    python3 tools/napcat_inst.py status               所有实例状态
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

BASE = '/opt/napcat'
INST = os.path.join(BASE, 'instances')
QQ_BIN = os.path.join(BASE, 'QQ', 'qq')
NATCAT_DIR = os.path.join(BASE, 'napcat')
UNIT_DIR = '/etc/systemd/system'

WEBUI_BASE = 6099
ONEBOT_BASE = 6700

XVFB_UNIT = '''[Unit]
Description=Xvfb display :%i (for napcat@%i)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :%i -screen 0 1080x760x16 +extension GLX +render
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
'''

NAPCAT_UNIT = '''[Unit]
Description=NapCat instance %i (QQ %i)
After=network-online.target xvfb@%i.service
Wants=network-online.target
Requires=xvfb@%i.service

[Service]
Type=simple
User=root
Environment=HOME=/opt/napcat/instances/%i/home
Environment=NAPCAT_WORKDIR=/opt/napcat/instances/%i/work
Environment=NAPCAT_QUICK_ACCOUNT=%i
Environment=DISPLAY=:%i
EnvironmentFile=-/opt/napcat/instances/%i/env
WorkingDirectory=/opt/napcat/napcat
ExecStart=/opt/napcat/QQ/qq --no-sandbox
Restart=always
RestartSec=5
LimitNOFILE=65535
TimeoutStopSec=30
KillMode=mixed

[Install]
WantedBy=multi-user.target
'''


def sh(cmd, check=False):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = (p.stdout or '') + (p.stderr or '')
    if check and p.returncode != 0:
        raise RuntimeError('命令失败: %s\n%s' % (cmd, out[-2000:]))
    return p.returncode, out


def list_instances():
    """返回已存在的实例目录列表。"""
    if not os.path.isdir(INST):
        return []
    out = []
    for n in sorted(os.listdir(INST)):
        d = os.path.join(INST, n)
        if os.path.isdir(d):
            out.append(n)
    return out


def used_ports():
    """已被占用的端口集合。"""
    _, out = sh("ss -ltn 2>/dev/null | awk 'NR>1{print $4}'")
    ports = set()
    for line in out.splitlines():
        m = re.search(r':(\d+)$', line.strip())
        if m:
            ports.add(int(m.group(1)))
    return ports


def alloc_index(ports):
    """给新实例分配 index：找一对没被占用的 (WebUI, OneBot) 端口。

    端口必须实测空闲 —— 不能只看目录里有没有，因为别的程序也可能占着。
    """
    idx = 0
    while True:
        webui = WEBUI_BASE + idx
        onebot = ONEBOT_BASE + 2 * idx
        # OneBot 端口不能是 6710（rcbot 的）
        if onebot == 6710:
            idx += 1
            continue
        if webui not in ports and onebot not in ports:
            return idx, webui, onebot
        idx += 1


def instance_paths(uin):
    d = os.path.join(INST, uin)
    return {
        'dir': d,
        'home': os.path.join(d, 'home'),
        'work': os.path.join(d, 'work'),
        'logs': os.path.join(d, 'logs'),
        'env': os.path.join(d, 'env'),
    }


def write_unit(name, content):
    path = os.path.join(UNIT_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


def cmd_plan(args):
    ports = used_ports()
    print('== 已占用端口（节选） ==')
    for p in sorted(ports):
        if 6090 <= p <= 6120 or 6690 <= p <= 6720:
            print('   %d' % p)
    print()
    print('== 已存在实例 ==')
    for uin in list_instances():
        p = instance_paths(uin)
        env = read_env(p['env'])
        print('   %-14s webui=%s onebot=%s display=%s'
              % (uin, env.get('WEBUI_PORT', '?'), env.get('ONEBOT_PORT', '?'),
                 env.get('DISPLAY', '?')))
    if not list_instances():
        print('   （无）')
    print()
    idx, webui, onebot = alloc_index(ports)
    print('== 下一个可用 index ==')
    print('   index=%d → WebUI %d, OneBot %d（OneBot 用 6700+2*index，避开 rcbot 的 6710）'
          % (idx, webui, onebot))
    return 0


def read_env(path):
    out = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    out[k.strip()] = v.strip()
    except Exception:
        pass
    return out


def cmd_add(args):
    uin = str(args.uin).strip()
    if not uin.isdigit():
        print('uin 必须是数字')
        return 1
    p = instance_paths(uin)
    if os.path.isdir(p['dir']):
        print('实例已存在：%s' % p['dir'])
        return 1

    ports = used_ports()
    idx, webui, onebot = alloc_index(ports)
    # display 号也要避开已在用的
    disp = 1
    while disp in [int(v) for v in _used_displays()]:
        disp += 1

    for sub in ('home', 'work', 'logs'):
        os.makedirs(os.path.join(p['dir'], sub), exist_ok=True)
    os.makedirs(os.path.join(p['work'], 'config'), exist_ok=True)

    with open(p['env'], 'w', encoding='utf-8') as f:
        f.write('# 由 napcat_inst.py 生成 —— 每个实例一份\n')
        f.write('WEBUI_PORT=%d\n' % webui)
        f.write('ONEBOT_PORT=%d\n' % onebot)
        f.write('DISPLAY=:%d\n' % disp)
        f.write('INDEX=%d\n' % idx)

    # 写 WebUI 配置（token 与现有一致）
    webui_cfg = os.path.join(p['work'], 'config', 'webui.json')
    if not os.path.exists(webui_cfg):
        with open(webui_cfg, 'w', encoding='utf-8') as f:
            json.dump({'host': '0.0.0.0', 'port': webui,
                       'token': 'rcnapcat', 'loginRate': 100}, f, ensure_ascii=False)

    write_unit('xvfb@.service', XVFB_UNIT)
    write_unit('napcat@.service', NAPCAT_UNIT)
    sh('systemctl daemon-reload')

    print('实例目录：%s' % p['dir'])
    print('WebUI  : http://127.0.0.1:%d' % webui)
    print('OneBot : ws://127.0.0.1:%d' % onebot)
    print('DISPLAY: :%d' % disp)
    print()
    print('启动：systemctl enable --now napcat@%s' % uin)
    print('首次登录需要扫码（每个新号都要扫一次，这个躲不掉）')
    return 0


def _used_displays():
    _, out = sh("ps aux 2>/dev/null | grep -o 'Xvfb :[0-9]*' | grep -o '[0-9]*'")
    return [x for x in out.split() if x]


def cmd_remove(args):
    uin = str(args.uin).strip()
    p = instance_paths(uin)
    if not os.path.isdir(p['dir']):
        print('实例不存在：%s' % uin)
        return 1
    sh('systemctl disable --now napcat@%s 2>/dev/null' % uin)
    sh('systemctl stop xvfb@%s 2>/dev/null' % _disp_of(p))
    if args.keep_data:
        print('已停服务，保留目录：%s' % p['dir'])
    else:
        shutil.rmtree(p['dir'], ignore_errors=True)
        print('已删除实例目录：%s' % p['dir'])
    return 0


def _disp_of(p):
    env = read_env(p['env'])
    return (env.get('DISPLAY') or ':1').lstrip(':')


def cmd_migrate(args):
    """把现有的 napcat.service 迁到 napcat@<uin> 模板。

    停机窗口不可避免（要搬 home 目录），但旧 unit 保留可回滚。
    """
    uin = str(args.uin).strip()
    p = instance_paths(uin)
    if os.path.isdir(p['dir']):
        print('实例目录已存在，先手工确认：%s' % p['dir'])
        return 1

    # 1) 备份现有配置与 home
    backup = '/opt/napcat/.backup-%s' % time.strftime('%Y%m%d-%H%M%S')
    os.makedirs(backup, exist_ok=True)
    if os.path.isdir(os.path.join(BASE, 'napcat', 'config')):
        shutil.copytree(os.path.join(BASE, 'napcat', 'config'),
                        os.path.join(backup, 'config'))
    if os.path.isdir(os.path.join(BASE, 'home')):
        shutil.copytree(os.path.join(BASE, 'home'), os.path.join(backup, 'home'))
    print('已备份到 %s' % backup)

    # 2) 停旧服务
    sh('systemctl stop napcat 2>/dev/null')

    # 3) 建目录并搬 home（登录态在这里，搬了才不用重扫码）
    for sub in ('home', 'work', 'logs'):
        os.makedirs(os.path.join(p['dir'], sub), exist_ok=True)
    src_home = os.path.join(BASE, 'home')
    dst_home = p['home']
    if os.path.isdir(src_home) and not os.path.isdir(os.path.join(dst_home, '.config')):
        for name in os.listdir(src_home):
            s = os.path.join(src_home, name)
            d = os.path.join(dst_home, name)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        print('已复制 home（登录态）→ %s' % dst_home)

    # 4) 配置目录：沿用现有 onebot 配置，只改端口
    src_cfg = os.path.join(BASE, 'napcat', 'config')
    dst_cfg = os.path.join(p['work'], 'config')
    os.makedirs(dst_cfg, exist_ok=True)
    if os.path.isdir(src_cfg):
        for name in os.listdir(src_cfg):
            shutil.copy2(os.path.join(src_cfg, name), os.path.join(dst_cfg, name))

    ports = used_ports()
    idx, webui, onebot = alloc_index(ports)
    disp = 1
    used_d = [int(x) for x in _used_displays()]
    while disp in used_d:
        disp += 1

    # 5) 改 onebot 配置里的 WS 端口
    obfile = os.path.join(dst_cfg, 'onebot11_%s.json' % uin)
    if not os.path.exists(obfile):
        obfile = os.path.join(dst_cfg, 'onebot11.json')
    if os.path.exists(obfile):
        try:
            with open(obfile, 'r', encoding='utf-8') as f:
                d = json.load(f)
            for ws in (d.get('network') or {}).get('websocketServers') or []:
                if ws.get('enable'):
                    ws['port'] = onebot
                    ws['host'] = '127.0.0.1'
            with open(obfile, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
            print('已把 OneBot WS 端口改为 %d（%s）' % (onebot, obfile))
        except Exception as e:
            print('改 OneBot 配置失败：%s' % str(e)[:200])

    # webui 端口
    webui_cfg = os.path.join(dst_cfg, 'webui.json')
    try:
        with open(webui_cfg, 'r', encoding='utf-8') as f:
            w = json.load(f)
        w['port'] = webui
        with open(webui_cfg, 'w', encoding='utf-8') as f:
            json.dump(w, f, ensure_ascii=False)
    except Exception as e:
        print('改 webui 配置失败：%s' % str(e)[:200])

    with open(p['env'], 'w', encoding='utf-8') as f:
        f.write('# 由 napcat_inst.py migrate 生成\n')
        f.write('WEBUI_PORT=%d\n' % webui)
        f.write('ONEBOT_PORT=%d\n' % onebot)
        f.write('DISPLAY=:%d\n' % disp)
        f.write('INDEX=%d\n' % idx)

    write_unit('xvfb@.service', XVFB_UNIT)
    write_unit('napcat@.service', NAPCAT_UNIT)
    sh('systemctl daemon-reload')

    print()
    print('迁移准备完成：')
    print('  实例目录 %s' % p['dir'])
    print('  WebUI  %d   OneBot %d   DISPLAY :%d' % (webui, onebot, disp))
    print('  备份   %s' % backup)
    print()
    print('接下来执行：')
    print('  systemctl enable --now napcat@%s' % uin)
    print('  （旧 napcat.service 保留未删，确认无误后可 disable）')
    return 0


def cmd_status(args):
    units = []
    _, out = sh("systemctl list-units --type=service --all --no-legend 2>/dev/null")
    for line in out.splitlines():
        if 'napcat@' in line or 'xvfb@' in line:
            units.append(line.strip())
    if not units:
        print('（没有 napcat/xvfb 实例单元）')
    for u in units:
        print(u)
    print()
    for uin in list_instances():
        p = instance_paths(uin)
        env = read_env(p['env'])
        rc, o = sh('systemctl is-active napcat@%s 2>/dev/null' % uin)
        state = (o or '').strip()
        print('napcat@%-14s %-10s webui=%s onebot=%s'
              % (uin, state, env.get('WEBUI_PORT', '?'), env.get('ONEBOT_PORT', '?')))
    return 0


def main():
    ap = argparse.ArgumentParser(description='NapCat 多实例管理')
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('plan')
    p_add = sub.add_parser('add')
    p_add.add_argument('uin')
    p_rm = sub.add_parser('remove')
    p_rm.add_argument('uin')
    p_rm.add_argument('--keep-data', action='store_true')
    p_mg = sub.add_parser('migrate')
    p_mg.add_argument('uin')
    sub.add_parser('status')
    args = ap.parse_args()

    cmd = args.cmd or 'plan'
    fn = {'plan': cmd_plan, 'add': cmd_add, 'remove': cmd_remove,
          'migrate': cmd_migrate, 'status': cmd_status}.get(cmd)
    if not fn:
        print('未知命令')
        return 1
    return fn(args)


if __name__ == '__main__':
    sys.exit(main())
