#!/bin/bash
# 开发虚拟机：配置 systemd 服务并启动
set -u
LOG=/var/log/vm-setup.log
exec > >(tee -a "$LOG") 2>&1
echo "=== 开始 $(date) ==="

# ---------- 1. 面板 ----------
cat > /etc/systemd/system/rcbot-dev-panel.service << 'EOF'
[Unit]
Description=RainCough 开发面板 (rcbot-dev, port 3910)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/raincough
Environment=RC_STORE_GATE=off
Environment=RC_DATA_DIR=/opt/raincough/data
Environment=RC_UDS_DIR=/opt/raincough/run
Environment=RC_PLUGIN_DIR=/opt/raincough/plugins
ExecStart=/opt/raincough/raincough -port 3910
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# ---------- 2. rcbot ----------
cat > /etc/systemd/system/rcbot-dev-bot.service << 'EOF'
[Unit]
Description=RainCough 机器人内核 (rcbot-dev, port 6710)
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/rcbot
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/rcbot/venv/bin/python /opt/rcbot/rcbot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ---------- 3. NapCat 模板单元 ----------
cat > /etc/systemd/system/napcat@.service << 'EOF'
[Unit]
Description=NapCat instance %i (QQ %i)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=HOME=/opt/napcat/instances/%i/home
Environment=NAPCAT_WORKDIR=/opt/napcat/instances/%i/work
# 不设 NAPCAT_QUICK_ACCOUNT：对没登录过的号设了它，NapCat 会快登失败→
#   "登录态已失效" → 退出 → systemd 拉起 → 死循环。
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

cat > /etc/systemd/system/xvfb-rcbot-%i.service << 'EOF'
[Unit]
Description=Xvfb display :%i (for 雨咯Bot 实例)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :%i -screen 0 1080x760x16 +extension GLX +render
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /opt/raincough/run /opt/raincough/logs
systemctl daemon-reload
systemctl enable rcbot-dev-panel rcbot-dev-bot 2>&1 | tail -2

echo "--- 启动 rcbot ---"
systemctl restart rcbot-dev-bot
sleep 4
systemctl is-active rcbot-dev-bot

echo "--- 启动面板 ---"
systemctl restart rcbot-dev-panel
sleep 6
systemctl is-active rcbot-dev-panel

echo "--- 端口 ---"
ss -ltn | grep -E ':(3910|6710) ' || echo '(还没监听)'

echo "--- 日志 ---"
tail -8 /opt/raincough/logs/*.log 2>/dev/null | head -20
tail -8 /opt/rcbot/logs/rcbot.log 2>/dev/null
echo "SETUP_DONE"
