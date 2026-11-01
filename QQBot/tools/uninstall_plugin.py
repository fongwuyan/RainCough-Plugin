#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调用面板的插件卸载接口（正规卸载：停进程 + 删目录 + 清注册表）。

用法:
    MSYS_NO_PATHCONV=1 python tools/uninstall_plugin.py --target prod QQBot
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description='面板插件卸载')
    ap.add_argument('name', nargs='+', help='插件名')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--base', default='')
    ap.add_argument('--password', default='1')
    args = ap.parse_args()

    preset = PRESETS[args.target]
    api = Api(args.base or preset['base'], args.password)

    for name in args.name:
        r = api.post('/api/store/plugin/remove', {'name': name})
        print('remove %s -> %s' % (name, r))
        time.sleep(2)

    pl = api.get('/api/plugins')
    if isinstance(pl, list):
        names = [p.get('name') for p in pl]
        print('剩余插件: %s' % names)
    else:
        print('插件列表读取失败: %s' % pl)


if __name__ == '__main__':
    sys.exit(main())
