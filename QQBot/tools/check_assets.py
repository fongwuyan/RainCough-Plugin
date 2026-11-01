# -*- coding: utf-8 -*-
"""检查前端产物里是否含新功能（esbuild 会把中文转成 \\uXXXX，要先反转义）。"""
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'assets/plugin.js'
d = open(path, encoding='utf-8').read()
t = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), d)

kws = ['媒体库', '查询', '清空会话', '转成可播放格式', '撤回状态',
       'qqbot.chat.media_list', 'qqbot.chat.query', 'qqbot.chat.clear_session',
       'qqbot.chat.media_transcode', 'qqbot.chat.senders',
       'qqbot.inst.list', '全部账号']
bad = 0
for kw in kws:
    hit = kw in t
    if kw.startswith('qqbot.inst') or kw == '全部账号':
        # 这些是「应该消失的旧东西」
        print('%-28s %s %s' % (kw, hit, '(应消失)' if not hit else '!! 还在'))
        if hit:
            bad += 1
    else:
        print('%-28s %s' % (kw, hit))
        if not hit:
            bad += 1
print('=== 缺失/残留:', bad, '===')
sys.exit(1 if bad else 0)
