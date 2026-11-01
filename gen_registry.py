#!/usr/bin/env python3
"""生成 RainCough-Plugin 仓库的 registry.json(v4 接口库时代)。

扫描根目录下含 plugin.json(v4) 的插件目录, 读取 name/label/version/description/interfaces,
以及清单里的 environment 块 —— 面板据此在装之前就告诉用户"还差什么"。

★ 2026-11-01 修正: 旧注释写着"插件=独立 systemd 单元, 无端口", 那是在
  environment 机制出现之前的假设。现在插件可以声明:
    · ports   需要占用的端口(面板预检时查占用者)
    · auto    面板能在用户确认后代为准备的步骤
    · manual  只能用户自己弄的(第三方客户端、扫码之类)
  写进注册表, 市场列表就能提前说明前置条件, 而不是装完才发现少东西。

运行: python gen_registry.py
     python gen_registry.py --stdout   # 只打印 JSON 不写盘(受限环境/需要调用方落盘时用)
"""
import os
import sys
import json
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'registry.json')


def parse_plugin_json(plugin_dir):
    p = os.path.join(plugin_dir, 'plugin.json')
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding='utf-8') as f:
            m = json.load(f)
        if not isinstance(m, dict) or not m.get('name'):
            return None
        return m
    except Exception:
        return None


def summarize_environment(env):
    """把清单里的 environment 块压成市场列表能用的摘要。

    面板据此在装之前就说明前置条件:
      ports   要占用的端口
      auto    面板能在用户确认后代为准备的步骤
      manual  只能用户自己弄的(第三方客户端、扫码之类)
    """
    if not isinstance(env, dict):
        return None
    checks = env.get('check') or []
    applies = env.get('apply') or []
    apply_ids = set()
    for a in applies:
        if not isinstance(a, dict):
            continue
        aid = a.get('id')
        if aid:
            apply_ids.add(aid)
        chk = a.get('check')
        if chk:
            apply_ids.add(chk)

    ports, auto, manual = [], [], []
    for c in checks:
        if not isinstance(c, dict):
            continue
        cid = c.get('id') or ''
        if c.get('type') == 'port' and c.get('port'):
            ports.append({'id': cid, 'label': c.get('label') or cid,
                          'port': c.get('port'), 'bind': c.get('bind') or '127.0.0.1'})
        # 有 apply 步骤能修 → 面板能代劳; 否则(有指引)只能用户自己弄
        if cid in apply_ids:
            auto.append(cid)
        elif c.get('guide'):
            manual.append({'id': cid, 'label': c.get('label') or cid, 'guide': c.get('guide')})

    out = {'level': env.get('level') or 'check'}
    if ports:
        out['ports'] = ports
    if auto:
        out['auto'] = auto
    if manual:
        out['manual'] = manual
    if not (ports or auto or manual):
        return None
    return out


def main():
    plugins = []
    for name in sorted(os.listdir(ROOT)):
        d = os.path.join(ROOT, name)
        if not os.path.isdir(d) or name.startswith('.') or name in ('assets', 'docs', 'testdata'):
            continue
        m = parse_plugin_json(d)
        if not m:
            continue
        ifaces = (m.get('interfaces') or [])
        entry = {
            'name': m['name'],
            'label': m.get('label') or m['name'],
            'version': m.get('version') or '0.1.0',
            'path': name,
            'author': m.get('author') or '',
            'description': m.get('description') or m['name'],
            'lang': ((m.get('backend') or {}).get('lang')) or '',
            'interfaces': [i.get('id') for i in ifaces],
        }
        env = summarize_environment(m.get('environment'))
        if env:
            entry['environment'] = env
        plugins.append(entry)
    registry = {
        'name': 'RainCough 插件集(v4)',
        'updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'plugins': plugins,
    }
    if '--stdout' in sys.argv:
        # 不写盘: 交给调用方落盘(如 Windows 沙箱里 python 写盘被拦)
        json.dump(registry, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write('\n')
        return
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print('generated %s with %d plugins' % (OUT, len(plugins)))


if __name__ == '__main__':
    main()
