#!/bin/bash
# 宿主：持久化转发规则
echo "=== 写 iptables-persistent ==="
apt-get install -y -qq iptables-persistent 2>&1 | tail -2
# netfilter-persistent 会被 dialog 打扰
echo 'iptables-persistent iptables-persistent/autosave_v4 true' | debconf-set-selections 2>/dev/null
DEBIAN_FRONTEND=noninteractive dpkg-reconfigure iptables-persistent 2>&1 | tail -3
echo
echo "=== 落盘规则 ==="
netfilter-persistent save 2>&1 | tail -2
ls -la /etc/iptables/ 2>&1 | head -6
echo
echo "=== 规则确认 ==="
iptables -t nat -S PREROUTING | grep -E '3910|2223|6711'
iptables -t nat -S OUTPUT | grep -E '3910'
echo
echo "=== 同时补一条: 2223(SSH) 和 6711(rcbot) 也走 192.168.2.200 ==="
iptables -t nat -D PREROUTING -d 192.168.2.200/32 -p tcp --dport 2223 -j DNAT --to-destination 127.0.0.1:2223 2>/dev/null
iptables -t nat -A PREROUTING -d 192.168.2.200/32 -p tcp --dport 2223 -j DNAT --to-destination 127.0.0.1:2223
iptables -t nat -D OUTPUT -d 192.168.2.200/32 -p tcp --dport 2223 -j DNAT --to-destination 127.0.0.1:2223 2>/dev/null
iptables -t nat -A OUTPUT -d 192.168.2.200/32 -p tcp --dport 2223 -j DNAT --to-destination 127.0.0.1:2223
netfilter-persistent save 2>&1 | tail -1
iptables -t nat -S PREROUTING | grep -E '3910|2223'
