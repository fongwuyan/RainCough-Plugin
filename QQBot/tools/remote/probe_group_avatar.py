#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测 QQ 群头像的正确取法。

问题：现在群头像用的是个人头像接口
    https://q1.qlogo.cn/g?b=qq&nk=<群号>&s=100
群号也是 9~10 位数字，落在合法 QQ 号区间，qlogo 会返回**某个陌生人的头像**，
所以群列表里全是随机头像。

群里头像的正确格式是：
    https://p.qlogo.cn/gh/<群号>/<群主QQ号>/<尺寸>
    https://qun.qlogo.cn/gh/<群号>/<群主QQ号>/<尺寸>
本脚本找出哪种可用、第二个参数该填谁。
"""
import hashlib
import json
import subprocess
import sys

TOKEN = 'rcsnow'
OB = 'http://127.0.0.1:3000'


def onebot(action, payload=None):
    cmd = ['curl', '-s', '-m', '20',
           '-H', 'Authorization: Bearer ' + TOKEN,
           '-H', 'Content-Type: application/json',
           '-X', 'POST', OB + '/' + action]
    if payload is not None:
        cmd += ['-d', json.dumps(payload)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
        return json.loads(out)
    except Exception as e:
        return {'error': str(e)}


def head(url):
    cmd = ['curl', '-s', '-m', '15', '-o', '/tmp/_ga.bin', '-w',
           '%{http_code} %{content_type} %{size_download}', url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25).stdout.strip()
        h = hashlib.md5(open('/tmp/_ga.bin', 'rb').read()).hexdigest()[:8]
        return '%s md5=%s' % (r, h)
    except Exception as e:
        return 'ERR %s' % str(e)[:60]


def main():
    gl = onebot('get_group_list')
    groups = (gl.get('data') or [])[:3]
    print('== get_group_list 条目字段:', sorted(groups[0].keys()) if groups else '无')
    for g in groups[:2]:
        print('   ', json.dumps(g, ensure_ascii=False)[:220])

    for g in groups[:2]:
        gid = str(g.get('group_id'))
        info = onebot('get_group_info', {'group_id': int(gid)})
        d = info.get('data') or {}
        print('== get_group_info', gid, '字段:', sorted(d.keys()))
        print('   ', json.dumps(d, ensure_ascii=False)[:300])

        ml = onebot('get_group_member_list', {'group_id': int(gid)})
        members = ml.get('data') or []
        owner = ''
        for m in members:
            if str(m.get('role')) == 'owner':
                owner = str(m.get('user_id'))
                break
        first = members[0] if members else {}
        print('== 群成员 %d 个，owner=%s，成员样例=%s'
              % (len(members), owner, json.dumps(first, ensure_ascii=False)[:180]))

        for label, uin in (('owner', owner), ('member', str(first.get('user_id') or ''))):
            if not uin:
                continue
            for host in ('p.qlogo.cn', 'qun.qlogo.cn'):
                url = 'https://%s/gh/%s/%s/100' % (host, gid, uin)
                print('   %-6s %-14s %s' % (label, host, head(url)))
        # 对照：现在用的个人头像接口
        print('   %-6s %-14s %s' % ('-', 'q1.qlogo.cn(现用)',
                                   head('https://q1.qlogo.cn/g?b=qq&nk=%s&s=100' % gid)))


if __name__ == '__main__':
    main()
