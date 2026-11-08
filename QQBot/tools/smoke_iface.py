#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雨咯Bot 插件接口冒烟测试（走面板 invoke，模拟真实使用路径）。

用法:
    MSYS_NO_PATHCONV=1 python tools/smoke_iface.py --target prod
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402

IFACES = [
    ('qqbot.health', {}),
    ('qqbot.conn.get', {}),
    ('qqbot.overview', {}),
    # 单账户
    ('qqbot.account.info', {}),
    ('qqbot.account.qrcode', {}),
    ('qqbot.account.status', {}),
    ('qqbot.account.logs', {}),
    ('rcbot.status', {}),
    ('rcbot.providers', {}),
    ('rcbot.personas', {}),
    ('rcbot.config.get', {}),
    ('qqbot.chat.sessions', {}),
    ('qqbot.chat.stats', {}),
    # 查询 / 媒体库 / 清空会话
    ('qqbot.chat.query', {}),
    ('qqbot.chat.senders', {}),
    ('qqbot.chat.media_list', {}),
    ('qqbot.chat.media_reindex', {}),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--base', default='')
    ap.add_argument('--only', default='', help='只测指定接口（逗号分隔）')
    args = ap.parse_args()

    api = Api(args.base or PRESETS[args.target]['base'], args.password)
    only = set(x.strip() for x in args.only.split(',') if x.strip())

    bad = 0
    for iface, params in IFACES:
        if only and iface not in only:
            continue
        r = api.post('/api/plugins/QQBot/invoke',
                     {'iface': iface, 'params': params, 'timeout_ms': 25000},
                     timeout=40)
        ok = isinstance(r, dict) and r.get('ok')
        if not ok:
            bad += 1
        detail = ''
        if ok:
            d = (r.get('result') or {}).get('data')
            detail = json.dumps(d, ensure_ascii=False)[:300]
        else:
            detail = json.dumps(r, ensure_ascii=False)[:300]
        print('%-24s %-4s %s' % (iface, 'OK' if ok else 'FAIL', detail))
    print('\n失败 %d 项' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
