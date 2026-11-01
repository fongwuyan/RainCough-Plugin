#!/bin/bash
# 开发虚拟机：解压安装面板 / 插件 / rcbot / NapCat
set -u
LOG=/var/log/vm-migrate.log
exec > >(tee -a "$LOG") 2>&1
echo "=== 开始 $(date) ==="

echo "--- 解压面板 ---"
mkdir -p /opt/raincough
tar -xzf /tmp/mig-panel.tar.gz -C /opt/raincough
chmod 755 /opt/raincough/raincough
ls -la /opt/raincough/ | head -8

echo "--- 解压插件 ---"
mkdir -p /opt/raincough/plugins
tar -xzf /tmp/mig-plugins.tar.gz -C /opt/raincough/plugins
ls -la /opt/raincough/plugins/QQBot/ | head -8

echo "--- 解压 rcbot ---"
mkdir -p /opt/rcbot
tar -xzf /tmp/mig-rcbot.tar.gz -C /opt/rcbot
chmod 755 /opt/rcbot/rcbot.py
ls -la /opt/rcbot/ | head -8

echo "--- 解压 NapCat ---"
mkdir -p /opt/napcat
tar -xzf /tmp/mig-napcat.tar.gz -C /opt/napcat
ls -la /opt/napcat/ | head -8
echo "  QQ 体积: $(du -sh /opt/napcat/QQ 2>/dev/null | cut -f1)"
echo "  napcat 体积: $(du -sh /opt/napcat/napcat 2>/dev/null | cut -f1)"

echo "--- 建 rcbot venv ---"
python3 -m venv /opt/rcbot/venv
/opt/rcbot/venv/bin/pip install -q --upgrade pip 2>&1 | tail -2
/opt/rcbot/venv/bin/pip install -q aiohttp aiosqlite pillow 2>&1 | tail -3
/opt/rcbot/venv/bin/python -V
/opt/rcbot/venv/bin/pip list 2>/dev/null | head -8

echo "--- 建目录 ---"
mkdir -p /opt/rcbot/data /opt/rcbot/logs /opt/rcbot/media /opt/raincough/data /opt/raincough/logs
mkdir -p /opt/napcat/instances

echo "--- 清理临时包 ---"
rm -f /tmp/mig-*.tar.gz
df -h / | tail -1
echo "MIGRATE_DONE"
