#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""再探一次群头像：换更大的群、换尺寸，看是不是全都返回同一张默认图。"""
import hashlib
import json
import subprocess

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


def head(url, out='/tmp/_ga.bin'):
    cmd = ['curl', '-s', '-m', '15', '-o', out, '-w',
           '%{http_code} %{content_type} %{size_download}', url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25).stdout.strip()
        h = hashlib.md5(open(out, 'rb').read()).hexdigest()[:8]
        return '%s md5=%s' % (r, h)
    except Exception as e:
        return 'ERR %s' % str(e)[:60]


GIDS = [231712193, 985854527, 1074471035, 428313068, 1064029991, 2157073082]


def main():
    for gid in GIDS:
        ml = onebot('get_group_member_list', {'group_id': gid})
        members = ml.get('data') or []
        owner = ''
        for m in members:
            if str(m.get('role')) == 'owner':
                owner = str(m.get('user_id'))
                break
        print('== 群 %s 成员 %d owner=%s' % (gid, len(members), owner))
        for size in (40, 100, 240):
            u = 'https://p.qlogo.cn/gh/%s/%s/%d' % (gid, owner, size)
            print('   p.qlogo  %-3d %s' % (size, head(u)))
        # 换 host 再试
        u = 'https://qun.qlogo.cn/gh/%s/%s/100' % (gid, owner)
        print('   qun.qlogo 100 %s' % head(u))
        # 带 r 参数（部分实现要）
        u = 'https://p.qlogo.cn/gh/%s/%s/100?r=1' % (gid, owner)
        print('   p.qlogo 100?r=1 %s' % head(u))
        print('   现用个人接口 %s'
              % head('https://q1.qlogo.cn/g?b=qq&nk=%s&s=100' % gid))


if __name__ == '__main__':
    main()
