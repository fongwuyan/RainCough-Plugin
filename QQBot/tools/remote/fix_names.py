#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回填历史昵称：去掉 BOM / 零宽字符等不可见字符。

2026-11-06：发现有些昵称是 '\\ufeff \\ufeffjvwoOIAO' 这种开头，
Python 的 str.split() 不把 BOM 当空白，所以旧清洗逻辑没清掉，
界面上看起来就是"昵称不见了"。

用法：python3 fix_names.py
"""
import os
import sqlite3
import sys

sys.path.insert(0, '/opt/rcbot')
from rcbot import profile  # noqa: E402

DB = '/opt/rcbot/data/rcbot.db'


def main():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    total = 0

    # chat_logs：昵称 + 撤回人
    rows = c.execute('select id, sender_id, sender_name from chat_logs').fetchall()
    for r in rows:
        old = r['sender_name'] or ''
        new = profile.clean_name(old)
        if not new:
            new = str(r['sender_id'] or '').strip()   # 全是不可见字符 → 退回 QQ 号
        if new != old:
            c.execute('update chat_logs set sender_name=? where id=?', (new, r['id']))
            total += 1
    c.commit()
    print('chat_logs 清理', total)

    n2 = 0
    try:
        rows = c.execute('select id, sender_id, sender_name from media_files').fetchall()
        for r in rows:
            old = r['sender_name'] or ''
            new = profile.clean_name(old)
            if not new:
                new = str(r['sender_id'] or '').strip()
            if new != old:
                c.execute('update media_files set sender_name=? where id=?', (new, r['id']))
                n2 += 1
        c.commit()
    except Exception as e:
        print('media_files 跳过：%s' % str(e)[:120])
    print('media_files 清理', n2)

    # 复核：还剩多少带不可见字符的
    bad = 0
    for r in c.execute('select sender_name from chat_logs'):
        v = r['sender_name'] or ''
        if v != v.strip() or any(ch in v for ch in ('﻿', '')):
            bad += 1
    print('剩余可疑昵称', bad)


if __name__ == '__main__':
    main()
