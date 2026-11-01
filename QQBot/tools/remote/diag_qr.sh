#!/bin/bash
# 诊断插件取二维码 Unauthorized 的原因
set -u

echo "=== 1. 插件配置的 napcat token ==="
python3 - <<'PY'
import json
p = '/opt/raincough/plugins/QQBot/data/config.json'
try:
    d = json.load(open(p))
    print(json.dumps(d.get('napcat'), ensure_ascii=False))
except Exception as e:
    print('  读不到:', e)
PY

echo
echo "=== 2. 实例的 webui.json ==="
cat /opt/napcat/instances/1132096843/work/config/webui.json 2>/dev/null; echo

echo
echo "=== 3. 实例 env ==="
cat /opt/napcat/instances/1132096843/env 2>/dev/null

echo
echo "=== 4. NapCat 实际加载的 webui 配置在哪 ==="
find /opt/napcat/instances/1132096843 -name 'webui.json' 2>/dev/null | sed 's/^/  /'
echo "  --- app_launcher/napcat 里的（注入时拷过去的旧配置） ---"
cat /opt/napcat/QQ/resources/app/app_launcher/napcat/config/webui.json 2>/dev/null; echo

echo
echo "=== 5. 用实例 token 登录 NapCat WebUI ==="
H=$(python3 -c "import hashlib;print(hashlib.sha256(b'rcnapcat.napcat').hexdigest())")
R=$(curl -s -m 10 -X POST -H 'Content-Type: application/json' \
      -d "{\"hash\":\"$H\"}" http://127.0.0.1:6099/api/auth/login)
echo "  登录响应: $(echo "$R" | head -c 150)"
C=$(echo "$R" | python3 -c 'import sys,json;print((json.load(sys.stdin).get("data") or {}).get("Credential",""))' 2>/dev/null)
echo "  credential 长度: ${#C}"
echo "  --- 带 credential 调 CheckLoginStatus ---"
curl -s -m 10 -X POST -H "Authorization: Bearer $C" -H 'Content-Type: application/json' \
     -d '{}' http://127.0.0.1:6099/api/QQLogin/CheckLoginStatus | head -c 250
echo
echo "  --- 不带 credential 直接调（复现插件的 401） ---"
curl -s -m 10 -X POST -H 'Content-Type: application/json' -d '{}' \
     http://127.0.0.1:6099/api/QQLogin/CheckLoginStatus | head -c 150
echo

echo "DIAG_DONE"
