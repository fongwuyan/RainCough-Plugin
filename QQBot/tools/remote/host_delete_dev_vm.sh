#!/usr/bin/env bash
# 删除开发虚拟机（rcbot-dev）。
#
# 开发机是 systemd 直接拉起的 QEMU（不是 libvirt 域）：
#   单元      /etc/systemd/system/rcbot-dev.service
#   磁盘      /var/lib/libvirt/images/rcbot-dev.qcow2  (30G)
#   seed      /var/lib/libvirt/seed/rcbot-dev-seed.img
#   端口转发  3910(面板) / 2223(SSH) / 6711(rcbot)
#
# 保留：debian12.qcow2（基础镜像，重建时要用）、其它 libvirt 镜像
set -u

echo "=== 1. 停机并禁用服务 ==="
systemctl disable --now rcbot-dev.service 2>&1 | tail -2
sleep 3
echo "  rcbot-dev.service = $(systemctl is-active rcbot-dev.service 2>&1)"
echo "  残留 qemu 进程: $(pgrep -fc 'qemu-system-x86_64.*rcbot-dev' 2>/dev/null || echo 0)"

echo
echo "=== 2. 删 systemd 单元 ==="
rm -f /etc/systemd/system/rcbot-dev.service
systemctl daemon-reload
systemctl reset-failed 2>/dev/null
echo "  单元文件: $([ -f /etc/systemd/system/rcbot-dev.service ] && echo 还在 || echo 已删)"

echo
echo "=== 3. 删磁盘与 seed ==="
for f in \
  /var/lib/libvirt/images/rcbot-dev.qcow2 \
  /var/lib/libvirt/seed/rcbot-dev-seed.img \
  /var/lib/libvirt/seed/rcbot-dev.xml \
  /var/lib/libvirt/seed/meta-data \
  /var/lib/libvirt/seed/network-config \
  /var/lib/libvirt/seed/user-data
do
  if [ -e "$f" ]; then
    sz=$(du -h "$f" 2>/dev/null | cut -f1)
    rm -f "$f"
    echo "  已删 $f ($sz)"
  else
    echo "  跳过 $f（不存在）"
  fi
done

echo
echo "=== 4. 删日志与辅助脚本 ==="
rm -f /var/log/rcbot-dev-serial.log
rm -rf /root/dev-migrate
rm -f /root/create_dev_vm.py
echo "  完成"

echo
echo "=== 5. 保留的基础镜像（重建时要用）==="
ls -la /var/lib/libvirt/images/debian12.qcow2 2>&1 | head -2
ls /var/lib/libvirt/images/ 2>/dev/null | head -10

echo
echo "=== 6. 验证 ==="
echo "  端口 3910: $(ss -ltn 2>/dev/null | grep -c ':3910 ')"
echo "  端口 2223: $(ss -ltn 2>/dev/null | grep -c ':2223 ')"
echo "  端口 6711: $(ss -ltn 2>/dev/null | grep -c ':6711 ')"
echo "  服务状态: $(systemctl is-active rcbot-dev.service 2>&1)"
echo "  磁盘: $([ -f /var/lib/libvirt/images/rcbot-dev.qcow2 ] && echo 还在 || echo 已删)"
echo "  磁盘占用:"; df -h / | tail -1
echo "=== 删除完成 ==="
