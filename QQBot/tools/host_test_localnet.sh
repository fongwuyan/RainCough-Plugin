#!/bin/bash
# 验证：外部来源的包是否被 DNAT 到 127.0.0.1 后丢弃
echo "=== 内核当前对 route_localnet 的设置 ==="
sysctl net.ipv4.conf.all.route_localnet net.ipv4.conf.enp1s0.route_localnet 2>&1
echo
echo "=== 外部来源模拟 A: 带 DNAT(当前状态) ==="
timeout 8 curl -s -o /dev/null -w '  http_code=%{http_code} exit=%{exitcode}\n' \
  --interface enp1s0 --local-port 40001 -m 5 http://192.168.2.200:3910/ 2>&1
echo
echo "=== 临时删掉 PREROUTING 的 3910 DNAT ==="
iptables -t nat -D PREROUTING -d 192.168.2.200/32 -p tcp --dport 3910 -j DNAT --to-destination 127.0.0.1:3910 2>/dev/null
echo "  已删"
echo
echo "=== 外部来源模拟 B: 无 DNAT ==="
timeout 8 curl -s -o /dev/null -w '  http_code=%{http_code} exit=%{exitcode}\n' \
  --interface enp1s0 --local-port 40002 -m 5 http://192.168.2.200:3910/ 2>&1
echo
echo "=== 恢复原规则 ==="
iptables -t nat -A PREROUTING -d 192.168.2.200/32 -p tcp --dport 3910 -j DNAT --to-destination 127.0.0.1:3910
echo "  已恢复"
echo
echo "=== 打开 route_localnet 后再测 A ==="
sysctl -w net.ipv4.conf.all.route_localnet=1 >/dev/null
sysctl -w net.ipv4.conf.enp1s0.route_localnet=1 >/dev/null
timeout 8 curl -s -o /dev/null -w '  http_code=%{http_code}\n' \
  --interface enp1s0 --local-port 40003 -m 5 http://192.168.2.200:3910/ 2>&1
echo
echo "=== 恢复 route_localnet=0 ==="
sysctl -w net.ipv4.conf.all.route_localnet=0 >/dev/null
sysctl -w net.ipv4.conf.enp1s0.route_localnet=0 >/dev/null
echo "  已恢复"
