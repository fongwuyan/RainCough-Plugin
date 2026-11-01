#!/bin/bash
# 虚拟机：完整验证实例能真正起来并出二维码
set -u
API=http://127.0.0.1:3910
CJ=/tmp/c.txt
rm -f $CJ
curl -s -c $CJ -o /dev/null -X POST "$API/api/auth/login" \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'

echo "=== 1. 创建实例 7776665555 ==="
curl -s -b $CJ -m 30 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' \
  -d '{"iface":"qqbot.inst.add","params":{"uin":"7776665555"}}' | head -c 350
echo
echo
echo "=== 2. 等 40 秒, 观察单元与端口 ==="
for i in $(seq 1 8); do
  sleep 5
  st=$(systemctl is-active napcat@7776665555 2>&1)
  xv=$(systemctl is-active xvfb-rcbot-1 2>&1)
  port=$(ss -ltn 2>/dev/null | grep -c ':6099 ')
  echo "  t=$((i*5))s napcat=$st xvfb=$xv 6099监听=$port"
done
echo
echo "=== 3. 端口 ==="
ss -ltn | grep -E ':(6099|6700) ' || echo '(无监听)'
echo
echo "=== 4. 取二维码 ==="
curl -s -b $CJ -m 30 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' \
  -d '{"iface":"qqbot.inst.action","params":{"uin":"7776665555","action":"qrcode"}}' | head -c 400
echo
echo
echo "=== 5. NapCat 日志尾部 ==="
journalctl -u napcat@7776665555 --no-pager -n 25 2>&1 | grep -vE '[▄▀█]' | tail -10
echo
echo "=== 6. 实例列表 ==="
curl -s -b $CJ -m 15 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.inst.list","params":{}}' | head -c 350
echo
echo "REAL_DONE"
