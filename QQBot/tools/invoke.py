#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调插件接口的通用小工具（带面板登录态）。

用法:
    MSYS_NO_PATHCONV=1 python tools/invoke.py --target prod qqbot.inst.scan_status '{"slug":"_pending_xxx"}'
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('iface')
    ap.add_argument('params', nargs='?', default='{}')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--timeout', type=int, default=60)
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)
    params = json.loads(args.params)
    r = api.post('/api/plugins/QQBot/invoke', {
        'iface': args.iface, 'params': params,
        'timeout_ms': args.timeout * 1000,
    }, timeout=args.timeout + 20)
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.exit(main())
