#!/bin/bash
# 部署新插件代码到虚拟机并清理脏数据
set -u
echo "=== 1. 停插件 ==="
pkill -f 'plugins/QQBot/server_v4.py' 2>/dev/null
sleep 2
echo
echo "=== 2. 清掉迁移过来的脏实例目录 ==="
echo "  (这些是宿主上建过的实例, 迁到虚拟机后目录跟着过来了, 但登录态/配置全是宿主路径)"
for uin in 1132096843 11320968432; do
  if [ -d "/opt/napcat/instances/$uin" ]; then
    echo "  删除 $uin"
    systemctl disable --now "napcat@$uin" 2>/dev/null
    rm -rf "/opt/napcat/instances/$uin"
  fi
done
# 顺便清掉对应的 xvfb 单元
for d in 1 2 3 4 5; do
  if systemctl is-active "xvfb-rcbot-$d" >/dev/null 2>&1; then
    echo "  停 xvfb-rcbot-$d"
    systemctl disable --now "xvfb-rcbot-$d" 2>/dev/null
  fi
  rm -f "/etc/systemd/system/xvfb-rcbot-$d.service"
done
systemctl daemon-reload
systemctl reset-failed 2>/dev/null
echo "  实例目录现在: $(ls /opt/napcat/instances/ 2>/dev/null || echo '(空)')"
echo
echo "=== 3. 修正插件配置(napcat.base 指向本机, 不要指宿主) ==="
cat > /opt/raincough/plugins/QQBot/data/config.json << 'EOF'
{
  "default": "astrbot",
  "napcat": {
    "base": "http://127.0.0.1:6099",
    "path": "/webui",
    "token": "rcnapcat"
  },
  "instances": {
    "base_dir": "/opt/napcat/instances",
    "webui_base": 6099,
    "onebot_base": 6700
  },
  "astrbot": {
    "base": "http://192.168.2.200:6185",
    "path": "/_rc_autologin.html?u=astrbot&p=CkAdPZCRKnIkpN1zOM8Uv8Nj",
    "token": ""
  }
}
EOF
cat /opt/raincough/plugins/QQBot/data/config.json
echo
echo "=== 4. 重启面板(插件会重新注册) ==="
systemctl restart rcbot-dev-panel
sleep 10
systemctl is-active rcbot-dev-panel
echo
echo "=== 5. 验证 ==="
rm -f /tmp/c.txt
curl -s -c /tmp/c.txt -o /dev/null -X POST http://127.0.0.1:3910/api/auth/login \
  -H 'Content-Type: application/json' -d '{"password":"qtyataa1313"}'
echo "  插件列表:"
curl -s -b /tmp/c.txt -m 10 http://127.0.0.1:3910/api/plugins | head -c 250
echo
echo
echo "  实例列表:"
curl -s -b /tmp/c.txt -m 15 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.inst.list","params":{}}' | head -c 600
echo
echo
echo "  概览:"
curl -s -b /tmp/c.txt -m 15 -X POST http://127.0.0.1:3910/api/plugins/QQBot/invoke \
  -H 'Content-Type: application/json' -d '{"iface":"qqbot.nc.overview","params":{}}' | head -c 500
echo
echo "DEPLOY_DONE"
