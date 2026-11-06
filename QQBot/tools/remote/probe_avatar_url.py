#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三路找"真正的群头像 URL"：

1. OneBot 有没有现成的群头像动作（get_group_avatar 之类）
2. SnowLuma 自己的 WebUI（5099）有没有头像接口
3. QQ 客户端日志里有没有头像下载 URL（日志可能是 gzip）
"""
import gzip
import json
import os
import re
import subprocess

TOKEN = 'rcsnow'
OB = 'http://127.0.0.1:3000'
UI = 'http://127.0.0.1:5099'
D = '/app/.config/QQ/nt_qq_5936b508aa1002bec8b21c50ce38cc5c/nt_data'
GID = 231712193

URL_RE = re.compile(rb'https?://[!-~]{12,400}')


def curl(url, extra=None, timeout=15):
    cmd = ['curl', '-s', '-m', str(timeout), url]
    if extra:
        cmd[3:3] = extra
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout
    except Exception as e:
        return 'ERR %s' % str(e)[:80]


def ob(action, payload=None):
    cmd = ['curl', '-s', '-m', '15', '-H', 'Authorization: Bearer ' + TOKEN,
           '-H', 'Content-Type: application/json', '-X', 'POST', OB + '/' + action]
    if payload is not None:
        cmd += ['-d', json.dumps(payload)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
        return out[:300]
    except Exception as e:
        return 'ERR %s' % str(e)[:60]


def main():
    print('===== 1. OneBot 候选动作 =====')
    for act in ('get_group_avatar', 'get_avatar', 'get_user_avatar',
                'get_group_info_v2', 'get_group_detail_info', 'get_avatar_url'):
        print('  %-22s %s' % (act, ob(act, {'group_id': GID, 'user_id': 3975339260})))

    print('===== 2. SnowLuma WebUI 5099 =====')
    for path in ('/', '/api', '/api/avatar', '/api/group/avatar', '/avatar'):
        body = curl(UI + path, timeout=10)
        print('  %-18s %s' % (path, body.replace('\n', ' ')[:180]))

    print('===== 3. 日志里的头像 URL =====')
    logdir = os.path.join(D, 'log')
    files = []
    for root, dirs, fns in os.walk(logdir):
        for fn in fns:
            files.append(os.path.join(root, fn))
    print('  日志文件 %d 个' % len(files))
    hits = []
    for p in files[:400]:
        try:
            if os.path.getsize(p) > 8 * 1024 * 1024:
                continue
            data = open(p, 'rb').read()
        except Exception:
            continue
        if data[:2] == b'\x1f\x8b':
            try:
                data = gzip.decompress(data)
            except Exception:
                continue
        for m in URL_RE.findall(data):
            u = m.decode('utf-8', 'ignore')
            low = u.lower()
            if ('avatar' in low or '/gh/' in low or 'group' in low) and u not in hits:
                hits.append(u)
    print('  候选 URL %d 个' % len(hits))
    for u in hits[:20]:
        print('   ', u[:190])


if __name__ == '__main__':
    main()
