#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询功能组合筛选验证。

用户要求：「查询指定QQ用户的信息」+「筛选出已撤回/未撤回的消息」，
这两个可以同时使用。所以要验证：
  · 单独按发送者查
  · 单独按撤回状态查
  · 单独按消息类型查
  · ★ 三者同时用（叠加）
"""
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = 'http://127.0.0.1:6710'


def get(path, **q):
    url = BASE + path
    if q:
        url += '?' + urllib.parse.urlencode({k: v for k, v in q.items() if v})
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def brief(rows):
    out = []
    for m in rows:
        kinds = []
        for md in (m.get('media') or []):
            if md.get('kind') and md['kind'] not in kinds:
                kinds.append(md['kind'])
        out.append({
            'id': m.get('id'),
            'from': m.get('sender_id'),
            'name': m.get('sender_name'),
            'recalled': bool(m.get('recalled')),
            'kinds': kinds,
            'text': (m.get('text') or '')[:24],
        })
    return out


def show(title, **q):
    d = get('/api/chat/query', limit=100, **q)
    rows = d['data']['items']
    print('\n== %s ==' % title)
    print('   参数: %s' % {k: v for k, v in q.items() if v})
    print('   命中 %d 条' % len(rows))
    for r in brief(rows):
        print('     #%-3s %-11s %-6s 撤回=%-5s %-8s %s'
              % (r['id'], r['from'], (r['name'] or '')[:6], r['recalled'],
                 ','.join(r['kinds']) or '-', r['text']))


def main():
    # 先拿一个真实发送者
    sd = get('/api/chat/senders')['data']['items']
    if not sd:
        print('库里没有发送者，先随便造点数据')
        return 1
    uin = sd[0]['sender_id']
    print('样本发送者: %s (%s) 共 %s 条'
          % (uin, sd[0].get('sender_name'), sd[0].get('c')))

    show('全部消息')
    show('按发送者', sender=uin)
    show('已撤回', recalled='yes')
    show('未撤回', recalled='no')
    show('按类型=视频', kind='video')
    show('按类型=语音', kind='record')
    show('按类型=图片', kind='image')
    show('按类型=文本', kind='text')
    show('★ 发送者+已撤回', sender=uin, recalled='yes')
    show('★ 发送者+未撤回', sender=uin, recalled='no')
    show('★ 发送者+类型=文本', sender=uin, kind='text')
    show('★ 发送者+已撤回+类型=视频', sender=uin, recalled='yes', kind='video')
    show('★ 不存在的用户', sender='999999999999')

    # 一致性校验：撤回筛选的计数必须与总数吻合
    allr = get('/api/chat/query', limit=500)['data']['items']
    yes = get('/api/chat/query', recalled='yes', limit=500)['data']['items']
    no = get('/api/chat/query', recalled='no', limit=500)['data']['items']
    print('\n=== 一致性 ===')
    print('全部 %d = 已撤回 %d + 未撤回 %d ? %s'
          % (len(allr), len(yes), len(no),
             'OK' if len(allr) == len(yes) + len(no) else '不一致 !!'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
