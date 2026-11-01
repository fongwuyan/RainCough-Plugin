#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调用插件的 inst.action repair 修复实例（重写 env/单元并重启）。

用法:
    MSYS_NO_PATHCONV=1 python tools/repair_inst.py --target prod 1132096843
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('uin')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)
    r = api.post('/api/plugins/QQBot/invoke', {
        'iface': 'qqbot.inst.action',
        'params': {'uin': args.uin, 'action': 'repair'},
        'timeout_ms': 120000,
    }, timeout=150)
    print('repair -> %s' % json.dumps(r, ensure_ascii=False)[:600])

    time.sleep(5)
    pl = api.get('/api/plugins')
    lst = api.post('/api/plugins/QQBot/invoke', {
        'iface': 'qqbot.inst.list', 'params': {}, 'timeout_ms': 30000,
    }, timeout=60)
    print('inst.list -> %s' % json.dumps(lst, ensure_ascii=False)[:600])


if __name__ == '__main__':
    sys.exit(main())
