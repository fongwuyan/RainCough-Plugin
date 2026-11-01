#!/bin/bash
# 生产机 QQBot / NapCat / QQ 彻底卸载 —— 第 1 步：全量备份
#
# 备份放在 /opt/_uninstall-backup-<时间戳>/（独立目录，不在 /opt/napcat、/opt/rcbot
# 之内，卸载时不会被一起删掉）。
set -u

TS=$(date +%Y%m%d-%H%M%S)
BK="/opt/_uninstall-backup-$TS"

echo "=== 备份目标: $BK ==="
mkdir -p "$BK"

echo
echo "--- 1. 备份 NapCat（含 QQ 本体与登录态） ---"
if [ -d /opt/napcat ]; then
  tar -C /opt -czf "$BK/napcat.tar.gz" napcat 2>/dev/null
  echo "  napcat.tar.gz  $(du -h "$BK/napcat.tar.gz" | cut -f1)"
else
  echo "  (无 /opt/napcat)"
fi

echo
echo "--- 2. 备份 rcbot（源码 + 数据 + 媒体 + venv） ---"
if [ -d /opt/rcbot ]; then
  tar -C /opt -czf "$BK/rcbot.tar.gz" rcbot 2>/dev/null
  echo "  rcbot.tar.gz  $(du -h "$BK/rcbot.tar.gz" | cut -f1)"
else
  echo "  (无 /opt/rcbot)"
fi

echo
echo "--- 3. 备份插件目录 ---"
if [ -d /opt/raincough/plugins/QQBot ]; then
  tar -C /opt/raincough/plugins -czf "$BK/QQBot-plugin.tar.gz" QQBot 2>/dev/null
  echo "  QQBot-plugin.tar.gz  $(du -h "$BK/QQBot-plugin.tar.gz" | cut -f1)"
fi

echo
echo "--- 4. 备份 systemd 单元 ---"
mkdir -p "$BK/systemd"
for u in napcat.service napcat@.service xvfb@.service xvfb-rcbot-*.service rcbot.service; do
  [ -f "/etc/systemd/system/$u" ] && cp -a "/etc/systemd/system/$u" "$BK/systemd/" && echo "  $u"
done

echo
echo "--- 5. 备份 /app/napcat 软链 ---"
readlink /app/napcat > "$BK/app-napcat-link.txt" 2>/dev/null || echo "(无)" > "$BK/app-napcat-link.txt"
cat "$BK/app-napcat-link.txt"

echo
echo "--- 6. 记录当前 QQ 账号与数据统计（供重装后对照） ---"
{
  echo "napcat 实例目录:"
  ls -la /opt/napcat/instances/ 2>/dev/null
  echo
  echo "各实例 env:"
  for f in /opt/napcat/instances/*/env; do
    [ -f "$f" ] && echo "--- $f" && cat "$f"
  done
  echo
  echo "NapCat onebot 配置:"
  ls /opt/napcat/napcat/config/ 2>/dev/null
  echo
  echo "rcbot 数据库表统计:"
  python3 - <<'PY'
import sqlite3, os
p = '/opt/rcbot/data/rcbot.db'
if os.path.exists(p):
    c = sqlite3.connect(p)
    for t in ('chat_logs', 'messages', 'sessions', 'summaries', 'accounts', 'providers', 'personas'):
        try:
            print('  %-12s %d' % (t, c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]))
        except Exception as e:
            print('  %-12s (无此表)' % t)
    c.close()
else:
    print('  (无 rcbot.db)')
PY
} > "$BK/state-before.txt" 2>&1
cat "$BK/state-before.txt"

echo
echo "=== 备份完成 ==="
du -sh "$BK"
echo "BACKUP_DIR=$BK"
echo "BACKUP_DONE"
