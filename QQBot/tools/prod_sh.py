#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在面板终端通道里执行 shell 命令并打印输出（一次性运维排查用）。

用法（Git Bash 必须带 MSYS_NO_PATHCONV=1，否则 /opt/... 会被改写成本机路径）:

    MSYS_NO_PATHCONV=1 python tools/prod_sh.py "uname -a" "ls /opt"
    MSYS_NO_PATHCONV=1 python tools/prod_sh.py --target dev "systemctl status rcbot"
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description='面板终端执行命令')
    ap.add_argument('cmd', nargs='+', help='要执行的 shell 命令（多个则依次执行）')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--base', default='')
    ap.add_argument('--password', default='1')
    ap.add_argument('--timeout', type=int, default=180)
    args = ap.parse_args()

    preset = PRESETS[args.target]
    base = args.base or preset['base']
    api = Api(base, args.password)
    for c in args.cmd:
        print('\n$ %s' % c)
        print(api.run(c, timeout=args.timeout).rstrip())


if __name__ == '__main__':
    sys.exit(main())
