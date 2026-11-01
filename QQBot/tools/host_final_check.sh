#!/bin/bash
# 宿主：最终验收 —— 生产与开发完全分离
#
# ★ 关键：必须从**局域网外部客户端**验证，
#   只在宿主本机测会漏掉 DNAT/route_localnet 这类问题
#   （本机走 OUTPUT 链，外部走 PREROUTING 链，行为不一样）。
echo "════════════════ 最终验收 ════════════════"
echo
echo "【1】宿主侧监听"
ss -ltnp | grep -E ':(3900|3910|2223|6710|6711) ' | awk '{print "  "$4"  "$6}'
echo
echo "【2】宿主本机访问"
for u in "http://127.0.0.1:3900/" "http://127.0.0.1:3910/" "http://192.168.2.200:3910/"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 8 "$u")
  echo "  $u  -> $code"
done
echo
echo "【3】生产侧状态（宿主）"
echo "  面板进程: $(pgrep -fc 'raincough -port 3900') 个"
echo "  插件进程: $(pgrep -fc 'QQBot/server_v4.py') 个"
echo "  rcbot:    $(systemctl is-active rcbot 2>&1)"
echo
echo "【4】开发侧状态（虚拟机）"
ssh -p 2223 -i /root/.ssh/rcbot-vm -o StrictHostKeyChecking=no -o BatchMode=yes rcbot@127.0.0.1 '
  echo "  主机名:   $(hostname)"
  echo "  地址:     $(ip -4 addr show ens3 | grep -oP "inet \K[0-9.]+")"
  echo "  面板:     $(systemctl is-active rcbot-dev-panel)"
  echo "  rcbot:    $(systemctl is-active rcbot-dev-bot)"
  echo "  插件进程: $(pgrep -cf server_v4.py) 个"
  echo "  NapCat:   $(du -sh /opt/napcat 2>/dev/null | cut -f1)"
' 2>&1
echo
echo "【5】转发规则（应该为空 —— 多余的 DNAT 会挡住外部访问）"
rules=$(iptables -t nat -S PREROUTING | grep -cE '3910|2223|6711')
echo "  PREROUTING 中相关 DNAT 规则数: $rules"
[ "$rules" = "0" ] && echo "  ✓ 无多余规则（外部访问靠 qemu 的 0.0.0.0 监听）" \
                  || echo "  ✗ 有多余规则，会挡住外部访问"
echo
echo "【6】开机自启"
echo "  rcbot-dev.service: $(systemctl is-enabled rcbot-dev 2>&1)"
echo "════════════════════════════════════════"
echo
echo "★ 请在浏览器/其它机器上打开下面两个地址实测（宿自查不出 PREROUTING 链的问题）:"
echo "    生产 http://192.168.2.200:3900"
echo "    开发 http://192.168.2.200:3910"
