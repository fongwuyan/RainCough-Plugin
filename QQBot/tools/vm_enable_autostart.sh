#!/bin/bash
# 虚拟机：开启插件 autostart + 启动 + 全面验证
set -u
API=http://127.0.0.1:3910
CJ=/tmp/c.txt

echo "=== 登录 ==="
rm -f $CJ
curl -s -c $CJ -o /dev/null -X POST "$API/api/auth/login" \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'
echo
echo "=== 开启 autostart（★ 字段是 autostart，不是 on）==="
curl -s -b $CJ -m 15 -X POST "$API/api/services/autostart" \
  -H 'Content-Type: application/json' \
  -d '{"name":"QQBot","autostart":true}'
echo
echo
echo "=== 启动插件 ==="
curl -s -b $CJ -m 20 -X POST "$API/api/services/action" \
  -H 'Content-Type: application/json' -d '{"name":"QQBot","action":"start"}'
echo
sleep 6
echo
echo "=== 插件列表 ==="
curl -s -b $CJ -m 10 "$API/api/plugins" | head -c 250
echo
echo
echo "=== 确认 autostart 已生效 ==="
curl -s -b $CJ -m 10 "$API/api/services/list" | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    print('  (解析失败)'); raise SystemExit
items = d if isinstance(d, list) else (d.get('items') or d.get('services') or [])
for s in items:
    if 'QQ' in str(s.get('name','')):
        print('  %-10s autostart=%s state=%s' % (s.get('name'), s.get('autostart'), s.get('state')))
" 2>/dev/null
echo
echo "=== 实例列表 ==="
curl -s -b $CJ -m 15 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.inst.list","params":{}}' | head -c 500
echo
echo
echo "=== 概览 ==="
curl -s -b $CJ -m 15 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.nc.overview","params":{}}' | head -c 600
echo
echo
echo "=== rcbot 账号 ==="
curl -s -b $CJ -m 15 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' -d '{"iface":"rcbot.accounts","params":{}}' | head -c 300
echo
echo "VERIFY_DONE"
