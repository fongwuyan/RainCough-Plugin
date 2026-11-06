#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在容器里找「群号 → 群头像缓存文件」的映射。

QQ 客户端把头像缓存成 `avatar/{group,user,cover}/s_<md5>`，
其中 md5 很可能是**头像下载 URL 的 md5**。
所以只要在 QQ 的数据/日志里把 URL 捞出来，算 md5 与文件名比对即可。

用法（容器内）：python3 probe_avatar_map.py
"""
import hashlib
import os
import re
import sys

D = '/app/.config/QQ/nt_qq_5936b508aa1002bec8b21c50ce38cc5c/nt_data'
AVA = os.path.join(D, 'avatar')
URL_RE = re.compile(rb'https?://[!-~]{12,400}')


def cached(sub):
    out = set()
    p = os.path.join(AVA, sub)
    try:
        for f in os.listdir(p):
            if f.startswith('s_'):
                out.add(f[2:])
    except Exception as e:
        print('list %s failed: %s' % (p, str(e)[:80]))
    return out


def main():
    names = {}
    for sub in ('group', 'user'):
        names[sub] = cached(sub)
        print('%s cached: %d' % (sub, len(names[sub])))
    allnames = set().union(*names.values()) if names else set()

    urls = set()
    scanned = 0
    for root, dirs, files in os.walk(D):
        if root.startswith(AVA):
            continue
        if 'Emoji' in root:
            continue
        for fn in files:
            p = os.path.join(root, fn)
            try:
                sz = os.path.getsize(p)
            except Exception:
                continue
            if sz > 30 * 1024 * 1024:
                continue
            try:
                data = open(p, 'rb').read()
            except Exception:
                continue
            scanned += 1
            for m in URL_RE.findall(data):
                u = m.decode('utf-8', 'ignore')
                urls.add(u)
    print('scanned %d files, urls %d' % (scanned, len(urls)))

    # 1) 直接 md5(url) 命中
    hits = []
    for u in urls:
        for cand in (u, u.split('?')[0], u.replace('https://', ''),
                     u.replace('https://', 'http://')):
            h = hashlib.md5(cand.encode('utf-8', 'ignore')).hexdigest()
            if h in allnames:
                hits.append((u, h))
    print('md5(url) 命中:', len(hits))
    for u, h in hits[:10]:
        print('   ', h, u[:170])

    # 2) URL 里含群号的（说明我们直接拿到带群号的地址）
    gids = [b'231712193', b'985854527', b'1074471035', b'428313068',
            b'1064029991', b'2157073082', b'286975887', b'773110453']
    print('--- 含群号的 URL ---')
    n = 0
    for u in sorted(urls):
        if any(g in u.encode() for g in gids):
            print('   ', u[:200])
            n += 1
            if n >= 12:
                break

    # 3) 含 avatar / gh 的 URL 样例
    print('--- 含 avatar 或 /gh/ 的 URL 样例 ---')
    n = 0
    for u in sorted(urls):
        if 'avatar' in u.lower() or '/gh/' in u:
            print('   ', u[:200])
            n += 1
            if n >= 12:
                break
    if n == 0:
        print('   （没有）')
        print('--- URL 样例（前 10）---')
        for u in sorted(urls)[:10]:
            print('   ', u[:160])


if __name__ == '__main__':
    main()
