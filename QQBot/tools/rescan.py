#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""触发面板插件重扫（/api/plugins/rescan），并可选启动/重启插件。

用法:
    MSYS_NO_PATHCONV=1 python tools/rescan.py --target prod QQBot --action start
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('name', nargs='*', default=['QQBot'])
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--action', default='start', choices=['start', 'stop', 'restart', 'none'])
    ap.add_argument('--wait', type=int, default=8)
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)

    r = api.post('/api/plugins/rescan', {})
    print('rescan -> ok=%s' % r.get('ok'))
    time.sleep(1)

    for name in args.name:
        if args.action != 'none':
            res = api.post('/api/services/action', {'name': name, 'action': args.action})
            print('action %s %s -> %s' % (args.action, name, res))
            time.sleep(args.wait)

    pl = api.get('/api/plugins')
    if isinstance(pl, list):
        for p in pl:
            if isinstance(p, dict) and p.get('name') in args.name:
                print('插件 %s: version=%s alive=%s' % (p.get('name'), p.get('version'), p.get('alive')))
    else:
        print('插件列表异常: %s' % pl)


if __name__ == '__main__':
    sys.exit(main())
