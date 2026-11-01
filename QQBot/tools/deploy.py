#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QQ Bot 一键部署（插件 / rcbot）。

面板没有 SSH，所有落盘都走面板 HTTP：
  · 文件   POST /api/fm/save  {"path","content"}
  · 目录   POST /api/fm/mkdir {"path"}
  · 插件   POST /api/services/action {"name":"QQBot","action":"restart"}
  · 命令   /api/terminal/open|input|stream|close（SSE 里 data 是 base64）

用法（Git Bash 里必须带 MSYS_NO_PATHCONV=1，否则 /opt/... 会被改写成本机路径）:

    MSYS_NO_PATHCONV=1 python tools/deploy.py plugin --target prod
    MSYS_NO_PATHCONV=1 python tools/deploy.py rcbot
    MSYS_NO_PATHCONV=1 python tools/deploy.py plugin --target prod --no-restart

前置：改了前端源码要先构建产物
    cd ../../RainCough-Core && node tools/build-plugin-frontend.js QQBot
"""

import argparse
import base64
import json
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
import http.cookiejar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # RainCough-Plugin/QQBot

PRESETS = {
    'prod': {'base': 'http://192.168.2.200:3900', 'dir': '/opt/raincough/plugins/QQBot'},
    # ★ 开发机（rcbot-dev 虚拟机）已于 2026-11-02 删除，3910 已下线。
    #   只保留生产机一个目标。
}

PLUGIN_FILES = [
    'plugin.json', 'server_v4.py', 'rcplugin.py', 'VERSION',
    'assets/plugin.js', 'frontend/plugin.js', 'frontend/qrcode.mjs',
]

# rcbot 运行时源码也打进插件包。
#
# 为什么要它: 插件包要能"自举" —— 环境准备步骤从插件目录里取源码装到 /opt/rcbot,
# 否则用户装完插件还得另外找地方下载机器人本体, 市场安装就断链了。
# 插件进程只跑 server_v4.py, 多带的 rcbot/ 只是磁盘上的文件, 不影响运行。
RCBOT_SRC_FILES = ['rcbot.py'] + [
    'rcbot/' + f for f in sorted(os.listdir(os.path.join(ROOT, 'rcbot')))
    if f.endswith('.py')
]
PLUGIN_FILES += RCBOT_SRC_FILES

# 多实例管理脚本（面板调它增删 NapCat 实例）
PLUGIN_FILES += ['tools/napcat_inst.py', 'tools/smoke_chat.py']

RCBOT_REMOTE = '/opt/rcbot'


class Api(object):
    def __init__(self, base, password):
        self.base = base.rstrip('/')
        self.cj = http.cookiejar.CookieJar()
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        r = self.post('/api/auth/login', {'password': password})
        if not r.get('ok'):
            raise SystemExit('登录失败：%s' % r)

    def post(self, path, obj, timeout=120):
        try:
            raw = self.op.open(urllib.request.Request(
                self.base + path, json.dumps(obj).encode('utf-8'),
                {'Content-Type': 'application/json'}), timeout=timeout).read()
            return json.loads(raw)
        except Exception as e:
            return {'ok': False, 'error': str(e)[:200]}

    def get(self, path, timeout=120):
        try:
            return json.loads(self.op.open(self.base + path, timeout=timeout).read())
        except Exception as e:
            return {'ok': False, 'error': str(e)[:200]}

    # ---------------- 终端通道：跑 shell 命令

    def run(self, cmd, timeout=120):
        r = self.post('/api/terminal/open', {'rows': 60, 'cols': 400})
        sid = r.get('sid')
        if not sid:
            raise SystemExit('打不开终端：%s' % r)
        buf = []
        stop = threading.Event()

        def reader():
            try:
                resp = self.op.open(
                    self.base + '/api/terminal/stream?sid=' + urllib.parse.quote(sid),
                    timeout=timeout + 30)
                for line in resp:
                    if stop.is_set():
                        break
                    s = line.decode('utf-8', 'replace')
                    if s.startswith('data: '):
                        chunk = s[6:].strip()
                        if chunk:
                            try:
                                buf.append(base64.b64decode(chunk).decode('utf-8', 'replace'))
                            except Exception:
                                buf.append(chunk)
            except Exception:
                pass

        threading.Thread(target=reader, daemon=True).start()
        time.sleep(0.6)
        self.post('/api/terminal/input', {
            'sid': sid,
            'data': base64.b64encode((cmd + ' ; echo "___RC_DONE___"\n').encode()).decode(),
        })
        end = time.time() + timeout
        while time.time() < end:
            if ''.join(buf).count('___RC_DONE___') >= 2:
                break
            time.sleep(0.3)
        time.sleep(0.4)
        stop.set()
        try:
            self.post('/api/terminal/close', {'sid': sid}, timeout=10)
        except Exception:
            pass
        return ''.join(buf)


def save_tree(api, remote_dir, files, label):
    dirs = {remote_dir}
    for rel in files:
        if '/' in rel:
            dirs.add(remote_dir + '/' + rel.rsplit('/', 1)[0])
    for d in sorted(dirs):
        api.post('/api/fm/mkdir', {'path': d})

    ok = 0
    for rel in files:
        p = os.path.join(ROOT, rel.replace('/', os.sep))
        if not os.path.isfile(p):
            print('  跳过（本地没有）%s' % rel)
            continue
        with open(p, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
        res = api.post('/api/fm/save', {'path': remote_dir + '/' + rel, 'content': content})
        good = res.get('status') is True
        ok += 1 if good else 0
        print('  %-26s %8d  %s' % (rel, len(content), 'OK' if good else res))
    print('%s：%d/%d' % (label, ok, len(files)))
    return ok == len(files)


def deploy_plugin(args):
    preset = PRESETS[args.target]
    base = args.base or preset['base']
    api = Api(base, args.password)
    print('== 部署插件 → %s %s' % (base, preset['dir']))
    if not save_tree(api, preset['dir'], PLUGIN_FILES, '插件文件'):
        raise SystemExit('有文件没写成功，中止')
    if args.no_restart:
        print('== 跳过重启')
        return
    r = api.post('/api/services/action', {'name': 'QQBot', 'action': 'restart'})
    print('== 重启插件：%s' % r)
    time.sleep(3)
    pl = api.get('/api/plugins')
    if isinstance(pl, list):
        me = [p for p in pl if p.get('name') == 'QQBot']
        if me:
            print('== 现在版本 %s，alive=%s' % (me[0].get('version'), me[0].get('alive')))


def deploy_rcbot(args):
    preset = PRESETS[args.target]
    base = args.base or preset['base']
    api = Api(base, args.password)
    files = ['rcbot.py'] + ['rcbot/' + f for f in sorted(os.listdir(os.path.join(ROOT, 'rcbot')))
                            if f.endswith('.py')]
    print('== 部署 rcbot → %s %s' % (base, RCBOT_REMOTE))
    if not save_tree(api, RCBOT_REMOTE, files, 'rcbot 源码'):
        raise SystemExit('有文件没写成功，中止')
    if args.no_restart:
        print('== 跳过重启')
        return
    out = api.run('systemctl restart rcbot && sleep 4 && systemctl is-active rcbot')
    state = 'unknown'
    for ln in out.splitlines():
        t = ln.strip()
        if t in ('active', 'inactive', 'failed', 'activating', 'deactivating'):
            state = t
    print('== 重启 rcbot：%s' % state)
    st = api.post('/api/plugins/QQBot/invoke', {'iface': 'rcbot.status', 'params': {}}, timeout=40)
    if isinstance(st, dict) and st.get('ok'):
        d = (st.get('result') or {}).get('data') or {}
        print('== 机器人：%s' % json.dumps(d.get('onebot'), ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description='QQ Bot 部署')
    ap.add_argument('what', choices=['plugin', 'rcbot', 'all'])
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--base', default='', help='面板地址，覆盖预设')
    ap.add_argument('--password', default='1')
    ap.add_argument('--no-restart', action='store_true')
    args = ap.parse_args()

    if args.what in ('plugin', 'all'):
        deploy_plugin(args)
    if args.what in ('rcbot', 'all'):
        deploy_rcbot(args)


if __name__ == '__main__':
    sys.exit(main())
