#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键清空会话 —— 端到端验证（测完从备份恢复）。"""
import json
import os
import subprocess
import sys
import urllib.request

BASE = 'http://127.0.0.1:6710'
DB = '/opt/rcbot/data/rcbot.db'


def api(path, data=None):
    if data is None:
        req = urllib.request.Request(BASE + path)
    else:
        req = urllib.request.Request(BASE + path,
                                     data=json.dumps(data).encode(),
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode('utf-8'))


def sessions():
    return api('/api/chat/sessions')['data']['items']


def count(sid):
    return api('/api/chat/messages?session_id=%s&limit=500' % sid)['data']['count']


def main():
    print('=== 清空前 ===')
    ss = sessions()
    for s in ss:
        print('  %-42s %-10s %d 条' % (s['session_id'], s.get('display') or s['target_id'],
                                       s['msg_count']))
    if not ss:
        print('没有会话可测')
        return 1
    sid = ss[0]['session_id']
    before = count(sid)
    print('\n选中的会话: %s（%d 条）' % (sid, before))

    # 备份
    bak = '/root/qqbot-reinstall/db-before-clear.db'
    subprocess.run(['cp', DB, bak], check=True)
    print('已备份数据库 -> %s' % bak)

    print('\n=== 执行清空（只删文字，保留媒体）===')
    r = api('/api/chat/session-clear',
            {'session_id': sid, 'with_media': False, 'confirm': True})
    print('  结果:', json.dumps(r['data'], ensure_ascii=False))

    after = count(sid)
    print('\n=== 清空后 ===')
    print('  该会话剩余消息: %d 条 %s' % (after, 'OK' if after == 0 else '!! 没清掉'))
    print('  会话列表:')
    for s in sessions():
        print('    %-42s %d 条' % (s['session_id'], s['msg_count']))

    print('\n=== 恢复数据库 ===')
    subprocess.run(['systemctl', 'stop', 'rcbot'], check=True)
    subprocess.run(['cp', bak, DB], check=True)
    subprocess.run(['systemctl', 'start', 'rcbot'], check=True)
    import time
    time.sleep(6)
    print('  恢复后该会话消息数: %d' % count(sid))
    print('=== 测试结束 ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
