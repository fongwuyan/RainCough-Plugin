#!/bin/bash
# 生产机 NapCat 实例重建 —— 第 4 步
#
# 全新安装 NapCat+QQ 后，登录态没了，需要重建实例并等扫码。
# 这里按插件的 napcat@<uin> 模板重建 1132096843 实例：
#   /opt/napcat/instances/1132096843/{home,work,logs}
#   work/config/{webui.json,onebot11_1132096843.json}
#   systemd: napcat@.service + xvfb-rcbot-<显示号>.service
set -u

UIN="${1:-1132096843}"
BASE=/opt/napcat
INST="$BASE/instances/$UIN"
WEBUI_PORT=6099
ONEBOT_PORT=6700
DISPLAY_NUM=1
TOKEN=rcnapcat

echo "=== 1. 建目录 ==="
mkdir -p "$INST/home" "$INST/work/config" "$INST/logs"
chmod 700 "$INST/home"

echo
echo "=== 2. 写实例 env ==="
cat > "$INST/env" <<EOF
# 由重建脚本生成
WEBUI_PORT=$WEBUI_PORT
ONEBOT_PORT=$ONEBOT_PORT
DISPLAY=:$DISPLAY_NUM
INDEX=0
EOF
cat "$INST/env"

echo
echo "=== 3. 写 webui.json ==="
cat > "$INST/work/config/webui.json" <<EOF
{"host":"0.0.0.0","port":$WEBUI_PORT,"token":"$TOKEN","loginRate":100}
EOF
cat "$INST/work/config/webui.json"

echo
echo "=== 4. 写 onebot11 配置（提前写，避免登录时抢 6700） ==="
cat > "$INST/work/config/onebot11_$UIN.json" <<EOF
{
  "network": {
    "httpServers": [],
    "httpSseServers": [],
    "httpClients": [],
    "websocketServers": [
      {
        "debug": false,
        "enable": true,
        "heartInterval": 30000,
        "host": "127.0.0.1",
        "messagePostFormat": "array",
        "name": "rc-core",
        "port": $ONEBOT_PORT,
        "reportSelfMessage": false,
        "token": "",
        "enableForcePushEvent": true
      }
    ],
    "websocketClients": [],
    "plugins": []
  },
  "musicSignUrl": "",
  "enableLocalFile2Url": false,
  "parseMultMsg": false,
  "imageDownloadProxy": "",
  "timeout": {
    "baseTimeout": 10000,
    "uploadSpeedKBps": 256,
    "downloadSpeedKBps": 256,
    "maxTimeout": 1800000
  }
}
EOF
echo "  已写 onebot11_$UIN.json (WS $ONEBOT_PORT)"

echo
echo "=== 5. 写 systemd 单元 ==="
cat > /etc/systemd/system/xvfb-rcbot-$DISPLAY_NUM.service <<EOF
[Unit]
Description=Xvfb display :$DISPLAY_NUM (for 雨咯Bot 实例)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :$DISPLAY_NUM -screen 0 1080x760x16 +extension GLX +render
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/napcat@.service <<'EOF'
[Unit]
Description=NapCat instance %i (QQ %i)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=HOME=/opt/napcat/instances/%i/home
Environment=NAPCAT_WORKDIR=/opt/napcat/instances/%i/work
EnvironmentFile=/opt/napcat/instances/%i/env
WorkingDirectory=/opt/napcat/napcat
ExecStart=/opt/napcat/QQ/qq --no-sandbox
Restart=always
RestartSec=5
LimitNOFILE=65535
TimeoutStopSec=15
KillMode=control-group

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
echo "  单元已写: napcat@.service, xvfb-rcbot-$DISPLAY_NUM.service"

echo
echo "=== 6. 启动 Xvfb 与 NapCat 实例 ==="
systemctl enable --now xvfb-rcbot-$DISPLAY_NUM.service
sleep 2
systemctl enable --now napcat@$UIN.service
sleep 8
echo "  xvfb-rcbot-$DISPLAY_NUM: $(systemctl is-active xvfb-rcbot-$DISPLAY_NUM.service 2>&1)"
echo "  napcat@$UIN: $(systemctl is-active napcat@$UIN.service 2>&1)"

echo
echo "=== 7. 等 WebUI 端口 ==="
for i in $(seq 1 30); do
  if ss -ltn 2>/dev/null | grep -q ":$WEBUI_PORT "; then
    echo "  WebUI $WEBUI_PORT 已监听（第 $i 次探测）"
    break
  fi
  sleep 2
done
ss -ltn 2>/dev/null | grep -E ':6099|:6700' || echo "  (端口尚未监听)"

echo
echo "=== 8. 日志尾部 ==="
journalctl -u napcat@$UIN.service --no-pager -n 25 2>/dev/null | tail -25

echo
echo "INSTANCE_READY $UIN"
echo "EXIT_CODE=0"
