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

echo "--- NapCat 运行时依赖(QQ 是 Electron, 缺库直接起不来) ---"
apt-get install -y -qq --no-install-recommends \
  libgtk-3-0 libgdk-pixbuf-2.0-0 libx11-xcb1 libxcursor1 libxi6 \
  libxinerama1 libxkbfile1 libglib2.0-0 libdbus-1-3 libexpat1 \
  libfontconfig1 libfreetype6 libgssapi-krb5-2 libnspr4 libxss1 \
  libxtst6 libsecret-1-0 libatspi2.0-0 2>&1 | tail -2

echo "--- ★ 建 /app/napcat 软链接 ---"
# QQ 内置的加载器 QQ/resources/app/loadNapCat.js 是硬编码的:
#     (async () => {await import('file:///app/napcat/napcat.mjs');})();
# 这是 NapCat 官方 Docker 镜像的约定路径, 宿主上靠
#     /app/napcat -> /opt/napcat/napcat
# 这个软链接接上。没有它 QQ 启动就报
#     Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/app/napcat/napcat.mjs'
# 然后 systemd 一直重启("activating auto-restart"), WebUI 永远不监听。
# (napcat/loadNapCat.js 那个支持 NAPCAT_MAIN_PATH 的版本用不上 ——
#  QQ 只加载自己 resources/app 里的那个。)
mkdir -p /app
if [ ! -e /app/napcat ] && [ ! -L /app/napcat ]; then
  ln -s /opt/napcat/napcat /app/napcat
fi
ls -la /app/napcat

echo "--- 建目录 ---"
mkdir -p /opt/rcbot/data /opt/rcbot/logs /opt/rcbot/media /opt/raincough/data /opt/raincough/logs
mkdir -p /opt/napcat/instances

echo "--- 清理临时包 ---"
rm -f /tmp/mig-*.tar.gz
df -h / | tail -1
echo "MIGRATE_DONE"
