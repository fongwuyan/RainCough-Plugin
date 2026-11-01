#!/bin/bash
# 修复：外部客户端访问 192.168.2.200:3910 不通
#
# 根因：
#   qemu 的 hostfwd 监听在 0.0.0.0:3910 —— 外部机器访问 192.168.2.200:3910
#   时，目标 IP 就是宿主自己的地址，**本来就能直接命中 qemu 的监听**，
#   不需要任何 DNAT。
#   但我之前加了一条 PREROUTING 的 DNAT：
#       -d 192.168.2.200/32 --dport 3910 -j DNAT --to-destination 127.0.0.1:3910
#   外部来源的包目标被改成 127.0.0.1（loopback），而内核
#   net.ipv4.conf.all.route_localnet=0 → 拒绝路由 → 包被丢弃 → 连接超时。
#   （宿主本机访问走 OUTPUT 链，不受 route_localnet 限制，所以本机测是通的，
#     外部机器测就不通 —— 这就是"本机能开、别人开不了"的原因。）
#
# 修法：删掉 3910 的 DNAT，让外部包直接命中 qemu 的 0.0.0.0:3910。
#   2223/6711 只绑 127.0.0.1，外部访问本就不需要，同样清掉。

echo "=== 1. 删除 3910/2223/6711 的 DNAT 规则 ==="
for p in 3910 2223 6711; do
  for c in PREROUTING OUTPUT; do
    iptables -t nat -D $c -d 192.168.2.200/32 -p tcp --dport $p \
      -j DNAT --to-destination 127.0.0.1:$p 2>/dev/null
  done
done
iptables -t nat -S PREROUTING | grep -E '3910|2223|6711' && echo "  !! 还有残留" || echo "  已清理干净"
echo
echo "=== 2. 现在的监听 ==="
ss -ltnp | grep -E ':(3910|2223|6711) ' | sed 's/^/  /'
echo
echo "=== 3. 宿主本机测试 ==="
for addr in 127.0.0.1 192.168.2.200; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 6 "http://$addr:3910/" 2>&1)
  echo "  http://$addr:3910/  -> $code"
done
echo
echo "=== 4. 落盘 ==="
netfilter-persistent save >/dev/null 2>&1 && echo "  rules.v4 已更新"
grep -cE '3910|2223|6711' /etc/iptables/rules.v4 2>/dev/null | sed 's/^/  rules.v4 中相关规则数: /'
echo
echo "=== 5. 顺带确认 route_localnet 保持默认(不需要动) ==="
sysctl net.ipv4.conf.all.route_localnet
