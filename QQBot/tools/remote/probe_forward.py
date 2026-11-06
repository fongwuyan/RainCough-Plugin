#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测合并转发消息的结构。

1) 从库里捞出带 forward 段的原始 JSON
2) 调 OneBot 的 get_forward_msg 看返回结构
3) 把结论打印到 stdout
"""
import json
import os
import sqlite3
import subprocess
import sys

DB = '/opt/rcbot/data/rcbot.db'
TOKEN = 'rcsnow'
OB = 'http://127.0.0.1:3000'


def onebot(action, payload):
    body = json.dumps(payload)
    cmd = ['curl', '-s', '-m', '20',
           '-H', 'Authorization: Bearer ' + TOKEN,
           '-H', 'Content-Type: application/json',
           '-X', 'POST', OB + '/' + action,
           '-d', body]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
        return json.loads(out)
    except Exception as e:
        return {'error': str(e)}


def main():
    c = sqlite3.connect(DB)
    rows = c.execute(
        "select id,session_id,msg_id,segs from chat_logs "
        "where segs like '%forward%' order by id desc limit 5").fetchall()
    print('== forward rows:', len(rows))
    ids = []
    for r in rows:
        print('--- row', r[0], r[1], r[2])
        print(json.dumps(json.loads(r[3]), ensure_ascii=False)[:1200])
        try:
            segs = json.loads(r[3])
        except Exception:
            continue
        for s in segs:
            if isinstance(s, dict) and s.get('type') in ('forward', 'node'):
                ids.append((s.get('data') or {}).get('id'))

    print('== forward ids:', ids)
    for fid in ids[:2]:
        if not fid:
            continue
        res = onebot('get_forward_msg', {'id': str(fid)})
        print('== get_forward_msg', fid)
        txt = json.dumps(res, ensure_ascii=False)
        print(txt[:2500])


if __name__ == '__main__':
    main()
