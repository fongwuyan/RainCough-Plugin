#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地文件上传到生产机（走面板 /api/fm/save）。

用法（Git Bash 必须带 MSYS_NO_PATHCONV=1）:

    MSYS_NO_PATHCONV=1 python tools/put_file.py --target prod tools/remote/01_backup.sh /root/qqbot-reinstall/01_backup.sh
    MSYS_NO_PATHCONV=1 python tools/put_file.py --target prod --chmod 755 /root/x.sh
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description='上传文件到面板机器')
    ap.add_argument('src', nargs='?', default='', help='本地文件（省略则只创建目录）')
    ap.add_argument('dst', help='远端绝对路径')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--base', default='')
    ap.add_argument('--password', default='1')
    ap.add_argument('--chmod', default='', help='chmod 权限，如 755')
    args = ap.parse_args()

    preset = PRESETS[args.target]
    base = args.base or preset['base']
    api = Api(base, args.password)

    parent = os.path.dirname(args.dst)
    if parent:
        api.post('/api/fm/mkdir', {'path': parent})

    content = ''
    if args.src:
        with open(args.src, 'r', encoding='utf-8', newline='') as f:
            content = f.read()
    res = api.post('/api/fm/save', {'path': args.dst, 'content': content})
    ok = res.get('status') is True
    print('save %s -> %s : %s' % (args.src or '(空文件)', args.dst, 'OK' if ok else res))

    if ok and args.chmod:
        r = api.run('chmod %s %s && ls -la %s' % (args.chmod, args.dst, args.dst), timeout=60)
        print(r.rstrip())
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    sys.exit(main())
