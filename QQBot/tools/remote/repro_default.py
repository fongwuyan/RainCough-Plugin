# -*- coding: utf-8 -*-
"""复现：保存一张卡片会不会把 default_card 改掉。"""
import json
import sys

sys.path.insert(0, '/opt/rcbot')
from rcbot import cards, config  # noqa: E402

cfg = config.load()
print('load 后 default_card  =', repr(cfg.get('default_card')))
print('load 后 default_persona=', repr(cfg.get('default_persona')))
print('cards 数量 =', len(cards.list_cards(cfg)))
print('default_id(cfg) =', repr(cards.default_id(cfg)))
print('cfg[\'default_card\'] 真值?', bool(cfg.get('default_card')))

# 只读试算：不落盘
c = cards.find(cfg, 'card_xizhiqing')
if c:
    before = cfg.get('default_card')
    cards.save(cfg, c, set_default=False)
    print('save(set_default=False) 后 default_card =', repr(cfg.get('default_card')),
          '（原来是 %r）' % before)
    print('save 后 default_persona =', repr(cfg.get('default_persona')))
else:
    print('找不到汐之青卡片')
