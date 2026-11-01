#!/bin/bash
# 开发虚拟机：后台装依赖 + 写日志（供宿主轮询）
set -u
export DEBIAN_FRONTEND=noninteractive
LOG=/var/log/vm-deps.log

exec > >(tee -a "$LOG") 2>&1
echo "=== 开始 $(date) ==="

cat > /etc/apt/sources.list << 'EOF'
deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security/ bookworm-security main contrib non-free non-free-firmware
EOF
rm -f /etc/apt/sources.list.d/*.list 2>/dev/null || true

apt-get update -qq
echo "--- apt update 完成 ---"

apt-get install -y -qq --no-install-recommends \
  ca-certificates curl wget git unzip xz-utils \
  python3 python3-venv python3-pip \
  xvfb x11-utils libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 \
  fonts-noto-cjk
echo "--- 依赖安装完成 ---"

mkdir -p /opt/raincough/plugins /opt/rcbot /opt/napcat /opt/raincough/data
echo "=== 版本 ==="
python3 -V
git --version
cmake --version | head -1
Xvfb -help 2>&1 | head -1 || true
echo "DEPS_DONE"
