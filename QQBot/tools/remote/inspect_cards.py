# -*- coding: utf-8 -*-
"""打印生产机上的卡片配置现状（排查默认卡片被谁改掉）。"""
import json
import sys

P = '/opt/rcbot/data/config.json'
cfg = json.load(open(P, encoding='utf-8'))
print('default_card   =', repr(cfg.get('default_card')))
print('default_persona=', repr(cfg.get('default_persona')))
print('default_provider=', repr(cfg.get('default_provider')))
print('cards 顺序:')
for i, c in enumerate(cfg.get('cards') or []):
    print('  %d. id=%-22s name=%-8s version=%s status=%s'
          % (i, c.get('id'), c.get('name'), c.get('version'), c.get('status')))
print('personas 段:')
for p in cfg.get('personas') or []:
    print('  id=%-22s name=%-8s' % (p.get('id'), p.get('name')))
print('accounts:')
for a in ((cfg.get('onebot') or {}).get('accounts') or []):
    print('  id=%s persona_id=%r provider_id=%r' % (a.get('id'), a.get('persona_id'), a.get('provider_id')))
