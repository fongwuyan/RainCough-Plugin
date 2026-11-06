#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读 QQ 客户端的 group_info.db，找群头像字段。"""
import os
import sqlite3
import sys

DB = '/app/.config/QQ/nt_qq_5936b508aa1002bec8b21c50ce38cc5c/nt_db/group_info.db'
GIDS = ['231712193', '1074471035', '985854527', '428313068', '1064029991']


def main():
    if not os.path.exists(DB):
        print('没有 group_info.db')
        return
    c = sqlite3.connect('file:%s?mode=ro' % DB, uri=True)
    c.text_factory = bytes
    tabs = [r[0].decode() for r in c.execute(
        "select name from sqlite_master where type='table'")]
    print('表:', tabs)
    for t in tabs:
        try:
            cols = [(r[1].decode(), (r[2] or b'').decode()) for r in
                    c.execute('pragma table_info("%s")' % t)]
            n = c.execute('select count(*) from "%s"' % t).fetchone()[0]
        except Exception as e:
            print('表 %s 出错 %s' % (t, str(e)[:80]))
            continue
        print('== %s (%d 行)' % (t, n))
        for name, typ in cols:
            print('    %-28s %s' % (name, typ))
        # 找含 avatar / url / md5 的列
        for name, typ in cols:
            low = name.lower()
            if any(k in low for k in ('avatar', 'url', 'md5', 'image', 'pic')):
                try:
                    for row in c.execute(
                            'select "%s" from "%s" limit 3' % (name, t)):
                        print('      %s 样例: %r' % (name, row[0][:160] if row[0] else row[0]))
                except Exception as e:
                    print('      %s 取样失败 %s' % (name, str(e)[:60]))


if __name__ == '__main__':
    main()
