#!/bin/bash
# 生产机：清掉多账户时代留下的实例目录与单元，只留单账户的 main
set -u

BASE=/opt/napcat/instances

echo "=== 清理前 ==="
ls -la "$BASE" 2>/dev/null
echo "--- 旧单元 ---"
systemctl list-unit-files --no-legend 2>/dev/null | grep -E 'napcat@|xvfb-rcbot' || echo "(无)"

echo
echo "=== 停掉旧单元 ==="
for u in $(systemctl list-unit-files --no-legend 2>/dev/null | awk '/^napcat@/{print $1}'); do
  echo "  stop $u"
  systemctl disable --now "$u" 2>/dev/null
done
# 只保留 xvfb-rcbot-1（单账户用），其余停掉
for u in $(systemctl list-unit-files --no-legend 2>/dev/null | awk '/^xvfb-rcbot-/{print $1}'); do
  case "$u" in
    xvfb-rcbot-1.service) echo "  保留 $u" ;;
    *) echo "  stop $u"; systemctl disable --now "$u" 2>/dev/null ;;
  esac
done

echo
echo "=== 删旧单元文件与实例目录 ==="
for f in /etc/systemd/system/napcat@*.service; do
  [ -e "$f" ] || continue
  echo "  rm $f"
  rm -f "$f"
done
for d in "$BASE"/*; do
  [ -d "$d" ] || continue
  b=$(basename "$d")
  [ "$b" = "main" ] && { echo "  保留 $b"; continue; }
  echo "  rm -rf $d"
  rm -rf "$d"
done
# xvfb 单元只留 1 号
for f in /etc/systemd/system/xvfb-rcbot-*.service; do
  [ -e "$f" ] || continue
  case "$f" in
    *xvfb-rcbot-1.service) ;;
    *) echo "  rm $f"; rm -f "$f" ;;
  esac
done

systemctl daemon-reload
systemctl reset-failed 2>/dev/null

echo
echo "=== 清理后 ==="
ls -la "$BASE" 2>/dev/null
echo "--- 单元 ---"
systemctl list-unit-files --no-legend 2>/dev/null | grep -E 'napcat|xvfb' || echo "(无)"

echo "CLEAN_DONE"
