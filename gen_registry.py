#!/usr/bin/env python3
"""生成 RainCough-Plugin 仓库的 registry.json(v4 接口库时代)。

扫描根目录下含 plugin.json(v4) 的插件目录, 读取 name/label/version/description/interfaces。
要求: 面板 v4 接口库(pluginx); 插件=独立 systemd 单元, 无端口。
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
        plugins.append({
            'name': m['name'],
            'label': m.get('label') or m['name'],
            'version': m.get('version') or '0.1.0',
            'path': name,
            'author': m.get('author') or '',
            'description': m.get('description') or m['name'],
            'interfaces': [i.get('id') for i in ifaces],
        })
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
