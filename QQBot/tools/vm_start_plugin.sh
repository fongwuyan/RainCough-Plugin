#!/bin/bash
# 开启 QQBot 插件的 autostart 并启动
set -u
CJ=/tmp/c.txt
rm -f $CJ
curl -s -c $CJ -o /dev/null -X POST http://127.0.0.1:3910/api/auth/login \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'

echo "=== 找插件启停接口 ==="
for p in /api/plugins/QQBot/start /api/plugins/QQBot/restart /api/services/action /api/plugins/autostart; do
  echo "--- POST $p ---"
  curl -s -b $CJ -m 15 -X POST "http://127.0.0.1:3910$p" \
    -H 'Content-Type: application/json' -d '{"name":"QQBot","action":"start","on":true}' | head -c 200
  echo
done
echo
echo "=== 观察插件进程 ==="
for i in 1 2 3 4 5 6; do
  sleep 4
  n=$(pgrep -cf 'server_v4.py')
  echo "  t=$((i*4))s 插件进程数=$n"
done
echo
echo "=== 插件列表 ==="
curl -s -b $CJ -m 10 http://127.0.0.1:3910/api/plugins | head -c 300
echo
echo
echo "=== 插件接口 ==="
for iface in 'rcbot.accounts' 'qqbot.inst.list' 'qqbot.chat.stats'; do
  r=$(curl -s -b $CJ -m 25 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
      -H 'Content-Type: application/json' -d "{\"iface\":\"$iface\",\"params\":{}}")
  echo "  $iface -> $(echo "$r" | head -c 230)"
done
