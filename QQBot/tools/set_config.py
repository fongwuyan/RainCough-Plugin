#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""写插件配置（NapCat 连接地址等）。

用法:
    MSYS_NO_PATHCONV=1 python tools/set_config.py --target prod \
        --napcat-base http://127.0.0.1:6099
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
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--base', default='')
    ap.add_argument('--napcat-base', default='http://127.0.0.1:6099')
    ap.add_argument('--napcat-token', default='rcnapcat')
    args = ap.parse_args()

    api = Api(args.base or PRESETS[args.target]['base'], args.password)
    cfg = {
        'default': 'napcat',
        'napcat': {
            'base': args.napcat_base,
            'path': '/webui',
            'token': args.napcat_token,
        },
    }
    r = api.post('/api/plugins/QQBot/invoke', {
        'iface': 'qqbot.conn.save',
        'params': {'base': args.napcat_base, 'token': args.napcat_token},
        'timeout_ms': 20000,
    }, timeout=40)
    print('conn.save -> %s' % json.dumps(r, ensure_ascii=False)[:400])

    g = api.post('/api/plugins/QQBot/invoke', {
        'iface': 'qqbot.conn.get', 'params': {}, 'timeout_ms': 20000,
    }, timeout=40)
    print('conn.get  -> %s' % json.dumps(g, ensure_ascii=False)[:400])


if __name__ == '__main__':
    sys.exit(main())
