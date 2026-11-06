#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 QQ 客户端的数据目录里定位"群头像映射"存在哪个文件。

思路：全目录扫描（排除 Emoji / avatar 自身），
  · 找含 'avatar' 字符串的文件
  · 找含群号（十进制字符串）的文件
然后人工看哪个文件最可能是映射表（群号 + md5 文件名）。
"""
import os
import re

ROOT = '/app/.config/QQ/nt_qq_5936b508aa1002bec8b21c50ce38cc5c'
GIDS = [b'231712193', b'1074471035', b'985854527', b'428313068']
HASH_RE = re.compile(rb's_[0-9a-f]{32}')


def main():
    print('=== QQ 配置目录结构（两层） ===')
    for base, dirs, files in os.walk(ROOT):
        depth = base[len(ROOT):].count('/')
        if depth > 1:
            dirs[:] = []
            continue
        try:
            sz = sum(os.path.getsize(os.path.join(base, f)) for f in files)
        except Exception:
            sz = 0
        if sz or files:
            print('  %-46s files=%-4d %8.1fKB' % (base[len(ROOT):] or '/', len(files), sz / 1024.0))

    print('=== 扫描含关键字的文件 ===')
    hits = []
    for base, dirs, files in os.walk(ROOT):
        if '/Emoji' in base or '/avatar' in base:
            continue
        for fn in files:
            p = os.path.join(base, fn)
            try:
                sz = os.path.getsize(p)
            except Exception:
                continue
            if sz > 40 * 1024 * 1024:
                continue
            try:
                data = open(p, 'rb').read()
            except Exception:
                continue
            if not data:
                continue
            has_ava = b'avatar' in data
            has_gid = any(g in data for g in GIDS)
            hashes = set(HASH_RE.findall(data))
            if has_ava or has_gid or hashes:
                hits.append((p[len(ROOT):], len(data), has_ava, has_gid, len(hashes)))
    for p, sz, a, g, h in sorted(hits, key=lambda x: -x[1])[:40]:
        print('  %-58s %8d  avatar=%-5s gid=%-5s s_md5=%d' % (p, sz, a, g, h))


if __name__ == '__main__':
    main()
