#!/bin/bash
# 生产机 QQBot / NapCat / QQ 彻底卸载 —— 第 2 步：卸载
#
# 卸载范围：
#   1. 面板插件 QQBot（目录 + 面板注册记录）
#   2. rcbot 运行时（/opt/rcbot：源码/venv/数据/媒体/日志）
#   3. NapCat + QQ 本体（/opt/napcat：QQ 二进制/NapCat/登录态/配置）
#   4. systemd 单元（napcat.service / napcat@.service / xvfb@.service /
#      xvfb-rcbot-*.service / rcbot.service）
#   5. /app/napcat 软链（QQ 加载 NapCat 的硬编码路径）
#   6. 残留的 napcat docker 容器
#
# 备份在 /opt/_uninstall-backup-<时间戳>/，本脚本不碰它。
set -u

echo "=== 1. 停服务 ==="
for u in napcat.service rcbot.service; do
  systemctl stop "$u" 2>/dev/null
  systemctl disable "$u" 2>/dev/null
  echo "  stop+disable $u -> $(systemctl is-active "$u" 2>&1)"
done
# 实例单元（napcat@<uin>.service）
for u in $(systemctl list-unit-files --no-legend 2>/dev/null | awk '/^napcat@.*\.service/{print $1}'); do
  systemctl stop "$u" 2>/dev/null
  systemctl disable "$u" 2>/dev/null
  echo "  stop+disable $u"
done
# Xvfb 实例单元
for u in $(systemctl list-unit-files --no-legend 2>/dev/null | awk '/^xvfb-rcbot-.*\.service/{print $1}'); do
  systemctl stop "$u" 2>/dev/null
  systemctl disable "$u" 2>/dev/null
  echo "  stop+disable $u"
done
sleep 2
# 兜底：残留进程
pkill -f '/opt/napcat/QQ/qq' 2>/dev/null && echo "  pkill QQ" || true
pkill -f '/opt/rcbot/venv/bin/python' 2>/dev/null && echo "  pkill rcbot" || true
sleep 2

echo
echo "=== 2. 删 systemd 单元文件 ==="
for f in /etc/systemd/system/napcat.service \
         /etc/systemd/system/napcat@.service \
         /etc/systemd/system/xvfb@.service \
         /etc/systemd/system/rcbot.service \
         /etc/systemd/system/xvfb-rcbot-*.service; do
  [ -e "$f" ] && rm -f "$f" && echo "  rm $f"
done
systemctl daemon-reload
systemctl reset-failed 2>/dev/null
echo "  剩余 napcat/rcbot/xvfb 单元:"
systemctl list-unit-files --no-legend 2>/dev/null | grep -E 'napcat|rcbot|xvfb' || echo "    (无)"

echo
echo "=== 3. 删面板插件目录 ==="
if [ -d /opt/raincough/plugins/QQBot ]; then
  rm -rf /opt/raincough/plugins/QQBot
  echo "  rm -rf /opt/raincough/plugins/QQBot"
fi
[ -d /opt/raincough/plugins/QQBot ] && echo "  !! 仍存在" || echo "  已删除"

echo
echo "=== 4. 删 rcbot 运行时 ==="
if [ -d /opt/rcbot ]; then
  rm -rf /opt/rcbot
  echo "  rm -rf /opt/rcbot"
fi
[ -d /opt/rcbot ] && echo "  !! 仍存在" || echo "  已删除"

echo
echo "=== 5. 删 NapCat + QQ ==="
if [ -d /opt/napcat ]; then
  rm -rf /opt/napcat
  echo "  rm -rf /opt/napcat"
fi
[ -d /opt/napcat ] && echo "  !! 仍存在" || echo "  已删除"

echo
echo "=== 6. 删 /app/napcat 软链 ==="
if [ -L /app/napcat ] || [ -e /app/napcat ]; then
  rm -rf /app/napcat
  echo "  rm /app/napcat"
fi
# /app 空了就整个删掉
rmdir /app 2>/dev/null && echo "  rmdir /app" || true

echo
echo "=== 7. 清残留容器与 QQ 配置 ==="
docker rm -f rc-nap-src 2>/dev/null && echo "  docker rm rc-nap-src" || echo "  (无 rc-nap-src 容器)"
# QQ 在 root 家目录可能留的登录态/缓存
rm -rf /root/.config/QQ /root/.local/share/QQ /root/.cache/QQ 2>/dev/null
echo "  清 /root 下的 QQ 配置"

echo
echo "=== 8. 校验 ==="
echo "  /opt/napcat: $([ -e /opt/napcat ] && echo '!! 还在' || echo '已删')"
echo "  /opt/rcbot:  $([ -e /opt/rcbot ] && echo '!! 还在' || echo '已删')"
echo "  插件目录:    $([ -e /opt/raincough/plugins/QQBot ] && echo '!! 还在' || echo '已删')"
echo "  /app/napcat: $([ -e /app/napcat ] && echo '!! 还在' || echo '已删')"
echo "  端口占用:"
ss -ltnp 2>/dev/null | grep -E ':6099|:6700|:6710' || echo "    (6099/6700/6710 均已释放)"
echo
echo "  面板仍在跑（不卸载面板本身）: $(systemctl is-active raincough)"
echo "UNINSTALL_DONE"
