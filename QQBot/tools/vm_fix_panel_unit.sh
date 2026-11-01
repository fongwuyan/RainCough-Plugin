#!/bin/bash
# 开发虚拟机：修正面板的 systemd 单元（环境变量名要与生产一致）
set -u
echo "=== 生产 vs 虚拟机的环境变量差异 ==="
echo "  生产: RC_PLUGINS_DIR=/opt/raincough/plugins  RC_UDS_DIR=/run/raincough  RuntimeDirectory=raincough"
echo "  修正后用同样的三项"
echo

cat > /etc/systemd/system/rcbot-dev-panel.service << 'EOF'
[Unit]
Description=RainCough 开发面板 (rcbot-dev, port 3910)
After=network-online.target
Wants=network-online.target

[Service]
Environment=RC_STORE_GATE=off
Type=simple
User=root
Group=root
WorkingDirectory=/opt/raincough
Environment=RC_DATA_DIR=/opt/raincough/data
Environment=RC_PLUGINS_DIR=/opt/raincough/plugins
Environment=RC_UDS_DIR=/run/raincough
ExecStart=/opt/raincough/raincough -port 3910
Restart=always
RestartSec=3
RuntimeDirectory=raincough
RuntimeDirectoryPreserve=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart rcbot-dev-panel
sleep 8
echo "面板: $(systemctl is-active rcbot-dev-panel)"
echo
echo "=== 插件进程 ==="
ps -eo pid,args | grep '[s]erver_v4.py' | head -3 || echo '(无)'
echo
echo "=== run 目录 ==="
ls -la /run/raincough/ /run/raincough/plugins/ 2>&1 | head -10
echo
echo "=== 插件 .rc.endpoint ==="
cat /opt/raincough/plugins/QQBot/.rc.endpoint 2>&1 | head -2
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
  echo "  $iface -> $(echo "$r" | head -c 230)"
done
