#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 QQ 进程内存里找「群号 ↔ 头像缓存 md5」的对应关系。

思路：缓存文件名是 s_<md5>，md5 来自 QQ 服务端下发的头像信息。
      群号（十进制字符串）和 md5 在 protobuf 里通常**相邻**，
      所以在内存里找到 md5，往前后各找 512 字节，
      看有没有群号字符串。

同时打印 group_info.db 的文件头，确认它是不是加密的。
"""
import os
import re
import subprocess

DB = '/app/.config/QQ/nt_qq_5936b508aa1002bec8b21c50ce38cc5c/nt_db/group_info.db'
AVA = '/app/.config/QQ/nt_qq_5936b508aa1002bec8b21c50ce38cc5c/nt_data/avatar/group'
GID_RE = re.compile(rb'(?<![0-9])([0-9]{9,11})(?![0-9])')


def head():
    try:
        with open(DB, 'rb') as f:
            h = f.read(32)
        print('group_info.db 头:', h[:16])
        print('  是 SQLite 吗:', h[:15] == b'SQLite format 3')
    except Exception as e:
        print('读 db 头失败:', str(e)[:80])


def avatar_names():
    out = []
    try:
        for f in os.listdir(AVA):
            if f.startswith('s_'):
                out.append(f[2:])
    except Exception as e:
        print('列头像目录失败:', str(e)[:80])
    return out


def qq_pids():
    r = subprocess.run(['pgrep', '-af', 'qq'], capture_output=True, text=True)
    pids = []
    for line in r.stdout.splitlines():
        parts = line.split(' ', 1)
        if parts and parts[0].isdigit():
            pids.append(int(parts[0]))
    return pids


def scan(pid, names):
    try:
        maps = open('/proc/%d/maps' % pid).read().splitlines()
    except Exception as e:
        print('  读 maps 失败:', str(e)[:60])
        return
    regions = []
    for m in maps:
        if 'r' not in m.split()[1]:
            continue
        rng = m.split()[0]
        if '-' not in rng:
            continue
        a, b = rng.split('-')
        try:
            start, end = int(a, 16), int(b, 16)
        except Exception:
            continue
        if end - start > 400 * 1024 * 1024:
            continue
        regions.append((start, end, m))
    print('  可读区域 %d 个' % len(regions))
    try:
        mem = open('/proc/%d/mem' % pid, 'rb', 0)
    except Exception as e:
        print('  打开 mem 失败:', str(e)[:80])
        return
    found = {}
    needles = [n.encode() for n in names]
    for start, end, desc in regions:
        try:
            mem.seek(start)
            data = mem.read(end - start)
        except Exception:
            continue
        for nd in needles:
            pos = 0
            while True:
                i = data.find(nd, pos)
                if i < 0:
                    break
                ctx = data[max(0, i - 512):i + 512]
                gids = set()
                for g in GID_RE.findall(ctx):
                    try:
                        gs = g.decode()
                    except Exception:
                        continue
                    if len(gs) >= 9:
                        gids.add(gs)
                if gids:
                    key = (nd.decode(), tuple(sorted(gids)))
                    found.setdefault(key, 0)
                    found[key] += 1
                pos = i + 1
    mem.close()
    print('  命中 %d 组' % len(found))
    for (md5, gids), cnt in list(found.items())[:40]:
        print('    %s  邻近群号: %s  (%d 次)' % (md5, ', '.join(gids), cnt))


def main():
    head()
    names = avatar_names()
    print('缓存群头像 %d 个: %s' % (len(names), names[:4]))
    for pid in qq_pids():
        cmd = subprocess.run(['cat', '/proc/%d/cmdline' % pid],
                             capture_output=True, text=True).stdout.replace('\x00', ' ')
        print('== pid %d %s' % (pid, cmd[:70]))
        if 'node' in cmd or 'qq' in cmd.lower():
            scan(pid, names)


if __name__ == '__main__':
    main()
