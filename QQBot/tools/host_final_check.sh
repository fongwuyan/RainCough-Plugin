#!/bin/bash
# 宿主：最终验收 —— 生产与开发完全分离
echo "════════ 开发生产分离验收 ════════"
echo
echo "=== 1. 端口占用 ==="
ss -ltn | grep -E ':(3900|3910|6710|6711|2223) ' | awk '{print "  "$4}'
echo
echo "=== 2. 生产面板(宿主, 3900) ==="
curl -s -o /dev/null -w '  http://127.0.0.1:3900/  → %{http_code}\n' -m 8 http://127.0.0.1:3900/
echo "  插件:"
for p in QQBot; do
  curl -s -m 8 http://127.0.0.1:3900/api/plugins | python3 -c "
import json,sys
d=json.load(sys.stdin)
for x in (d if isinstance(d,list) else []):
    print('    %-10s v%-8s alive=%s' % (x.get('name'), x.get('version'), x.get('alive')))
" 2>/dev/null
done
echo
echo "=== 3. 开发面板(虚拟机, 3910 经转发) ==="
curl -s -o /dev/null -w '  http://192.168.2.200:3910/  → %{http_code}\n' -m 10 http://192.168.2.200:3910/
curl -s -m 10 http://192.168.2.200:3910/ | grep -oE '<title>[^<]*</title>' | sed 's/^/  /'
echo
echo "=== 4. 两边数据目录(应完全独立) ==="
echo "  生产 rcbot 数据: /opt/rcbot/data        ($(du -sh /opt/rcbot/data 2>/dev/null | cut -f1))"
echo "  生产 插件数据:   /opt/raincough/data     ($(du -sh /opt/raincough/data 2>/dev/null | cut -f1))"
echo "  开发 rcbot 数据: 机内 /opt/rcbot/data"
echo
echo "=== 5. 虚拟机状态 ==="
ssh -p 2223 -i /root/.ssh/rcbot-vm -o StrictHostKeyChecking=no -o BatchMode=yes rcbot@127.0.0.1 \
  'echo "  主机名: $(hostname)"; echo "  地址: $(ip -4 addr show ens3 | grep -oP "inet \K[0-9.]+")"; \
   echo "  面板: $(systemctl is-active rcbot-dev-panel)"; echo "  rcbot: $(systemctl is-active rcbot-dev-bot)"; \
   echo "  插件进程: $(pgrep -cf server_v4.py)"; echo "  磁盘: $(df -h / | tail -1 | awk "{print \$3\" / \"\$2\" (\"\$5\")\"}")"' 2>&1
echo
echo "=== 6. 持久化 ==="
echo "  iptables 规则:"
iptables -t nat -S PREROUTING | grep -E '3910|2223|6711' | sed 's/^/    /'
echo "  rules.v4 时间: $(ls -la --time-style=+%H:%M /etc/iptables/rules.v4 | awk '{print $6}')"
echo "  rcbot-dev.service: $(systemctl is-enabled rcbot-dev 2>&1)"
echo
echo "═══════════════════════════════════"
