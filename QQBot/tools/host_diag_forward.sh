#!/bin/bash
echo "=== 1. 当前 nat 规则(3910 相关) ==="
iptables -t nat -S PREROUTING | grep -E '3910|2223|6711' || echo '(无)'
iptables -t nat -S OUTPUT | grep -E '3910|2223|6711' || echo '(output 无)'
echo
echo "=== 2. qemu 的监听 ==="
ss -ltnp | grep -E ':(3910|2223|6711) ' || echo '(无)'
echo
echo "=== 3. route_localnet(外部访问 127.0.0.1 的关键开关) ==="
sysctl net.ipv4.conf.all.route_localnet net.ipv4.conf.default.route_localnet 2>&1
echo
echo "=== 4. INPUT 链策略 ==="
iptables -S INPUT | head -5
echo
echo "=== 5. 宿主本机各地址访问测试 ==="
for addr in 127.0.0.1 192.168.2.200; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 6 "http://$addr:3910/" 2>&1)
  echo "  http://$addr:3910/  -> $code"
done
echo
echo "=== 6. 模拟外部来源访问(走 enp1s0 出去再回来) ==="
echo "  路由判定:" $(ip route get 192.168.2.200 2>&1 | head -1)
echo
echo "=== 7. 从局域网另一地址模拟(加源地址) ==="
curl -s -o /dev/null -w '  src=192.168.2.200 -> %{http_code}\n' -m 6 \
  --interface 192.168.2.200 http://192.168.2.200:3910/ 2>&1
echo
echo "=== 8. 规则文件里存了什么 ==="
grep -E '3910' /etc/iptables/rules.v4 2>/dev/null | sed 's/^/  /'
