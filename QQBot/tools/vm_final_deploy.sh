#!/bin/bash
# 虚拟机：最终部署 + 完整验证
set -eu
D=/opt/raincough/plugins/QQBot

echo "=== 1. 还原文件 ==="
base64 -d /tmp/s4.b64 > "$D/server_v4.py"
base64 -d /tmp/aj.b64 > "$D/assets/plugin.js"
base64 -d /tmp/fj.b64 > "$D/frontend/plugin.js"
chmod 644 "$D/server_v4.py" "$D/assets/plugin.js" "$D/frontend/plugin.js"
python3 -c "import ast; ast.parse(open('$D/server_v4.py',encoding='utf-8').read()); print('  语法 OK')"
rm -rf "$D/__pycache__"

echo "=== 2. 清残留单元 ==="
for u in $(systemctl list-units --all --no-legend --no-pager 2>/dev/null | grep -oE 'napcat@[0-9]+' | sort -u); do
  echo "  删 $u"
  systemctl disable --now "$u" 2>/dev/null || true
  rm -f "/etc/systemd/system/$u.service"
done
for u in $(systemctl list-units --all --no-legend --no-pager 2>/dev/null | grep -oE 'xvfb-rcbot-[0-9]+' | sort -u); do
  echo "  删 $u"
  systemctl disable --now "$u" 2>/dev/null || true
  rm -f "/etc/systemd/system/$u.service"
done
systemctl daemon-reload
systemctl reset-failed 2>/dev/null || true

echo "=== 3. 重启面板 ==="
pkill -f 'plugins/QQBot/server_v4.py' 2>/dev/null || true
sleep 3
systemctl restart rcbot-dev-panel
sleep 10
echo "  面板: $(systemctl is-active rcbot-dev-panel)"

echo "=== 4. 登录 + 插件状态 ==="
rm -f /tmp/c.txt
curl -s -c /tmp/c.txt -o /dev/null -X POST http://127.0.0.1:3910/api/auth/login \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'
echo "  插件: $(curl -s -b /tmp/c.txt -m 10 http://127.0.0.1:3910/api/plugins | head -c 110)"
echo
echo "  autostart: $(curl -s -b /tmp/c.txt -m 10 http://127.0.0.1:3910/api/services/list | python3 -c "
import json,sys
d=json.load(sys.stdin)
items = d if isinstance(d,list) else (d.get('items') or [])
for s in items:
    if 'QQ' in str(s.get('name','')): print(s.get('name'), 'autostart=', s.get('autostart'), 'state=', s.get('state'))
" 2>/dev/null)"

echo
echo "=== 5. 实例列表 ==="
curl -s -b /tmp/c.txt -m 15 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.inst.list","params":{}}' | head -c 300
echo
echo
echo "=== 6. 概览(不应显示生产的账号) ==="
curl -s -b /tmp/c.txt -m 15 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.nc.overview","params":{}}' | head -c 300
echo
echo
echo "=== 7. 聊天记录 ==="
curl -s -b /tmp/c.txt -m 15 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.chat.stats","params":{}}' | head -c 250
echo
echo "FINAL_DONE"
