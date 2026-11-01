#!/bin/bash
# 清理生产实例的 BOT 插件数据（聊天记录 + 媒体 + 会话历史）
# 先全量备份, 确认备份 OK 再清。
set -u

TS=$(date +%Y%m%d-%H%M%S)
BK=/opt/rcbot/.backup-dataclean-$TS

echo "=== 1. 备份 ==="
mkdir -p "$BK"
cp -a /opt/rcbot/data/rcbot.db "$BK/rcbot.db"
cp -a /opt/rcbot/data/config.json "$BK/config.json"
cp -a /opt/rcbot/media "$BK/media"
cp -a /opt/raincough/plugins/QQBot/data/config.json "$BK/plugin-config.json"
echo "  备份到: $BK"
du -sh "$BK"
ls -la "$BK"

echo
echo "=== 2. 备份校验(行数对比) ==="
python3 - << PY
import sqlite3
a = sqlite3.connect('$BK/rcbot.db')
b = sqlite3.connect('/opt/rcbot/data/rcbot.db')
for t in ('chat_logs', 'messages', 'sessions', 'summaries', 'accounts'):
    na = a.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
    nb = b.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
    print('  %-12s 备份=%-6s 当前=%-6s %s' % (t, na, nb, 'OK' if na == nb else '!! 不一致'))
PY
echo "  媒体文件数: $(find $BK/media -type f 2>/dev/null | wc -l)"
echo "  当前媒体数: $(find /opt/rcbot/media -type f 2>/dev/null | wc -l)"

echo
echo "=== 3. 停 rcbot(避免它往里写) ==="
systemctl stop rcbot
sleep 3
echo "  rcbot: $(systemctl is-active rcbot 2>&1)"

echo
echo "=== 4. 清数据库 ==="
python3 - << 'PY'
import sqlite3
c = sqlite3.connect('/opt/rcbot/data/rcbot.db')
for t in ('chat_logs', 'messages', 'summaries', 'sessions'):
    try:
        n = c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
        c.execute('DELETE FROM ' + t)
        print('  %-12s 删了 %d 行' % (t, n))
    except Exception as e:
        print('  %-12s 跳过 (%s)' % (t, str(e)[:60]))
c.commit()
# accounts 保留(那是账号连接状态, 不是聊天数据), 但清掉旧的统计字段
c.execute("DELETE FROM sqlite_sequence WHERE name IN ('chat_logs','messages','summaries','sessions')")
c.commit()
for t in ('chat_logs', 'messages', 'sessions', 'summaries', 'accounts'):
    n = c.execute('SELECT COUNT(*) FROM ' + t).fetchone()[0]
    print('  现在 %-12s %d 行' % (t, n))
c.close()
PY

echo
echo "=== 5. 清媒体文件 ==="
n=$(find /opt/rcbot/media -type f 2>/dev/null | wc -l)
echo "  待删 $n 个文件"
find /opt/rcbot/media -type f -delete 2>/dev/null
# 清空的目录也清掉, 留根目录
find /opt/rcbot/media -mindepth 1 -type d -empty -delete 2>/dev/null || true
echo "  剩余: $(find /opt/rcbot/media -type f 2>/dev/null | wc -l) 个文件, 目录占用 $(du -sh /opt/rcbot/media 2>/dev/null | cut -f1)"

echo
echo "=== 6. 起 rcbot ==="
systemctl start rcbot
sleep 5
echo "  rcbot: $(systemctl is-active rcbot 2>&1)"

echo
echo "=== 7. 验证 ==="
tail -5 /opt/rcbot/logs/rcbot.log 2>/dev/null
echo
echo "  备份位置: $BK"
echo "CLEAN_DONE"
