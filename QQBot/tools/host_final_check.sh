#!/bin/bash
# 宿主：最终验收 —— 生产与开发完全分离
echo "════════════════ 最终验收 ════════════════"
echo
echo "【1】对外访问"
curl -s -o /dev/null -w '  生产 http://192.168.2.200:3900/  -> %{http_code}\n' -m 8 http://192.168.2.200:3900/
curl -s -o /dev/null -w '  开发 http://192.168.2.200:3910/  -> %{http_code}\n' -m 10 http://192.168.2.200:3910/
echo
echo "【2】生产侧（宿主）"
echo "  面板进程: $(pgrep -fc 'raincough -port 3900') 个"
echo "  插件进程: $(pgrep -fc 'QQBot/server_v4.py') 个"
echo "  rcbot:    $(systemctl is-active rcbot 2>&1)"
echo "  数据目录: /opt/rcbot/data ($(du -sh /opt/rcbot/data 2>/dev/null | cut -f1))"
echo
echo "【3】开发侧（虚拟机）"
ssh -p 2223 -i /root/.ssh/rcbot-vm -o StrictHostKeyChecking=no -o BatchMode=yes rcbot@127.0.0.1 '
  echo "  主机名:   $(hostname)"
  echo "  地址:     $(ip -4 addr show ens3 | grep -oP "inet \K[0-9.]+")"
  echo "  面板:     $(systemctl is-active rcbot-dev-panel)"
  echo "  rcbot:    $(systemctl is-active rcbot-dev-bot)"
  echo "  插件进程: $(pgrep -cf server_v4.py) 个"
  echo "  NapCat:   $(du -sh /opt/napcat 2>/dev/null | cut -f1)"
  echo "  磁盘:     $(df -h / | tail -1 | awk "{print \$3\" / \"\$2\" (\"\$5\")\"}")"
' 2>&1
echo
echo "【4】转发规则（已持久化）"
iptables -t nat -S PREROUTING | grep -E '3910|2223|6711' | sed 's/^/  /'
echo "  rules.v4: $(ls -la --time-style=+%m-%d\ %H:%M /etc/iptables/rules.v4 | awk '{print $6" "$7}')"
echo
echo "【5】开机自启"
echo "  rcbot-dev.service: $(systemctl is-enabled rcbot-dev 2>&1)"
echo "════════════════════════════════════════"
