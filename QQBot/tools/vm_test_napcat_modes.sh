#!/bin/bash
# 在虚拟机上按宿主的方式复现, 找出差异
echo "=== A. 完全照宿主: cd /opt/napcat/napcat + 设 NAPCAT_WORKDIR ==="
mkdir -p /tmp/q1/config /tmp/q1/cache /tmp/q1/logs
cd /opt/napcat/napcat
HOME=/tmp/q1 NAPCAT_WORKDIR=/tmp/q1 DISPLAY=:1 timeout 15 /opt/napcat/QQ/qq --no-sandbox 2>&1 | grep -vE '[▄▀█]' | head -8
echo
echo "=== B. 加上 NAPCAT_MAIN_PATH ==="
cd /opt/napcat/napcat
HOME=/tmp/q1 NAPCAT_WORKDIR=/tmp/q1 NAPCAT_MAIN_PATH=/opt/napcat/napcat/napcat.mjs DISPLAY=:1 timeout 15 /opt/napcat/QQ/qq --no-sandbox 2>&1 | grep -vE '[▄▀█]' | head -8
echo
echo "=== C. 端口是否起来了 ==="
ss -ltn | grep -E ':(6099|6700) ' || echo '(无)'
echo
echo "=== D. 宿主上的 3975339260 实例目录都放了什么 ==="
echo '  (在宿主上查, 见下一步)'
echo
echo "=== E. 虚拟机 /opt/napcat/napcat/loadNapCat.js 内容 ==="
cat /opt/napcat/napcat/loadNapCat.js
