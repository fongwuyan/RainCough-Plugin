#!/bin/bash
echo "=== QQ 需要的动态库(缺失的) ==="
ldd /opt/napcat/QQ/qq 2>&1 | grep 'not found' | sort -u
echo
echo "=== 装缺失的库 ==="
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq \
  libgtk-3-0 libgdk-pixbuf-2.0-0 libx11-xcb1 libxcursor1 libxi6 \
  libxrandr2 libxdamage1 libxfixes3 libxcomposite1 libxinerama1 libxkbfile1 \
  libglib2.0-0 libdbus-1-3 libexpat1 libfontconfig1 libfreetype6 \
  libgssapi-krb5-2 libnspr4 libnss3 libxss1 libxtst6 libsecret-1-0 \
  libatk-bridge2.0-0 libatspi2.0-0 libcups2 libdrm2 libpango-1.0-0 \
  libcairo2 libasound2 libgbm1 2>&1 | tail -4
echo
echo "=== 装完再查 ==="
ldd /opt/napcat/QQ/qq 2>&1 | grep 'not found' | sort -u || echo "  全部齐了"
echo
echo "=== 实测启动 ==="
mkdir -p /tmp/qtest
cd /opt/napcat/napcat
HOME=/tmp/qtest DISPLAY=:1 timeout 12 /opt/napcat/QQ/qq --no-sandbox 2>&1 | grep -vE '[▄▀█]' | head -10
echo
echo "=== 端口有没有起来 ==="
ss -ltn | grep -E ':(6099|6700) ' || echo '(还没起, 正常 —— 要等 NapCat 加载)'
echo "DEPS2_DONE"
