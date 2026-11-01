#!/bin/bash
# 装插件依赖（系统 python3）
set -u
echo "=== 装 aiohttp 等 ==="
apt-get install -y -qq python3-aiohttp python3-requests 2>&1 | tail -3
python3 -c "import aiohttp; print('aiohttp', aiohttp.__version__)" 2>&1
echo
echo "=== 重启面板 ==="
systemctl restart rcbot-dev-panel
sleep 10
echo "面板: $(systemctl is-active rcbot-dev-panel)"
echo
echo "=== 插件进程 ==="
ps -eo pid,args | grep '[s]erver_v4.py' | head -3 || echo '(无)'
echo
echo "=== 插件列表 ==="
rm -f /tmp/c.txt
curl -s -c /tmp/c.txt -o /dev/null -X POST http://127.0.0.1:3910/api/auth/login \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'
curl -s -b /tmp/c.txt -m 10 http://127.0.0.1:3910/api/plugins | head -c 300
echo
echo
echo "=== QQBot 接口 ==="
for iface in 'rcbot.accounts' 'qqbot.inst.list' 'qqbot.chat.stats'; do
  r=$(curl -s -b /tmp/c.txt -m 25 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
      -H 'Content-Type: application/json' -d "{\"iface\":\"$iface\",\"params\":{}}")
  echo "  $iface -> $(echo "$r" | head -c 240)"
  echo
done
