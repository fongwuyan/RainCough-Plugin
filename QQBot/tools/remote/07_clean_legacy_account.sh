#!/bin/bash
# 清理 rcbot 配置里遗留的旧单值字段（ws_url/access_token/self_id）
#
# ★ 为什么必须清：
#   rcbot/config.py 的 _normalize_accounts 看到 onebot.ws_url 有值、
#   但 accounts[] 为空时，会自动包装出一个 id=a_default 的空账号。
#   多实例下这个空账号是纯干扰：它在界面上显示一个没有 QQ 号的条目，
#   还持续去连 6700 刷"连接失败"警告。
#   删掉账号（POST /api/accounts remove）没用 —— 加载配置时又会被包出来。
set -u

P=/opt/rcbot/data/config.json
echo "=== 清理前 ==="
python3 - <<'PY'
import json
d = json.load(open('/opt/rcbot/data/config.json', encoding='utf-8'))
ob = d.get('onebot') or {}
print('  旧单值字段:', {k: ob.get(k) for k in ('ws_url', 'access_token', 'self_id') if k in ob})
print('  accounts:', [a.get('id') for a in (ob.get('accounts') or [])])
PY

echo
echo "=== 清理 ==="
python3 - <<'PY'
import json
p = '/opt/rcbot/data/config.json'
d = json.load(open(p, encoding='utf-8'))
ob = d.setdefault('onebot', {})
removed = []
for k in ('ws_url', 'access_token', 'self_id'):
    if k in ob:
        ob.pop(k)
        removed.append(k)
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('  已删除:', removed)
PY

systemctl restart rcbot
sleep 6

echo
echo "=== 清理后 ==="
curl -s -m 8 http://127.0.0.1:6710/api/accounts | python3 -c "
import sys, json
d = json.load(sys.stdin).get('data') or {}
for a in d.get('items') or []:
    print('  id=%s uin=%r ws=%s unit=%s' % (a.get('id'), a.get('uin'), a.get('webui'), a.get('unit')))
print('  count=%s' % d.get('count'))
"
echo "CLEAN_DONE"
