#!/bin/bash
# 虚拟机：验证创建新实例（之前报 name 'unit' is not defined）
set -u
API=http://127.0.0.1:3910
CJ=/tmp/c.txt
rm -f $CJ
curl -s -c $CJ -o /dev/null -X POST "$API/api/auth/login" \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'

echo "=== 创建一个测试实例 (9998887777) ==="
r=$(curl -s -b $CJ -m 180 -X POST "$API/api/plugins/QQBot/invoke" \
    -H 'Content-Type: application/json' \
    -d '{"iface":"qqbot.inst.add","params":{"uin":"9998887777"}}')
echo "$r" | head -c 800
echo
echo
echo "=== 实例列表 ==="
curl -s -b $CJ -m 15 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.inst.list","params":{}}' | head -c 700
echo
echo
echo "=== 单元状态 ==="
systemctl list-units --type=service --all --no-legend --no-pager | grep -iE 'napcat|xvfb' || echo '(无)'
echo
echo "=== 端口 ==="
ss -ltn | grep -E ':(6099|6100|6700|6702) ' || echo '(无监听)'
echo
echo "=== 清理测试实例 ==="
curl -s -b $CJ -m 60 -X POST "$API/api/plugins/QQBot/invoke" \
  -H 'Content-Type: application/json' \
  -d '{"iface":"qqbot.inst.action","params":{"uin":"9998887777","action":"remove"}}' | head -c 300
echo
echo "TEST_DONE"
