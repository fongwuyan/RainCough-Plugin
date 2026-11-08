#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""短轮询生产机上的后台日志（Bash 工具有 10 分钟上限，长任务要分段等）。"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--log', required=True)
    ap.add_argument('--marker', default='')
    ap.add_argument('--seconds', type=int, default=240)
    ap.add_argument('--interval', type=int, default=20)
    ap.add_argument('--tail', type=int, default=40)
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)
    t0 = time.time()
    while time.time() - t0 < args.seconds:
        time.sleep(args.interval)
        out = api.run('tail -%d %s 2>/dev/null; echo "---MARK---"; ps aux | grep -c "[s]nowluma_deploy"' % (args.tail, args.log), timeout=60)
        text = out or ''
        if args.marker and args.marker in text:
            print('== 标记 %s 出现 ==' % args.marker)
            print(text)
            return 0
        if 'INSTALL_DONE' in text or 'EXIT_CODE=' in text:
            print(text)
            return 0
    print(text)
    return 1


if __name__ == '__main__':
    sys.exit(main())
