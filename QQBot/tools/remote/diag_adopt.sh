#!/bin/bash
# 诊断扫码后为什么没认领出QQ 号
set -u

# 找最新的占位实例
SLUG=$(ls -1 /opt/napcat/instances/ 2>/dev/null | grep '^_pending_' | sort | tail -1)
echo "占位实例: $SLUG"
[ -z "$SLUG" ] && { echo "没有占位实例"; exit 0; }

WP=$(grep WEBUI_PORT /opt/napcat/instances/$SLUG/env 2>/dev/null | cut -d= -f2)
OP=$(grep ONEBOT_PORT /opt/napcat/instances/$SLUG/env 2>/dev/null | cut -d= -f2)
echo "WebUI=$WP OneBot=$OP"

H=$(python3 -c "import hashlib;print(hashlib.sha256(b'rcnapcat.napcat').hexdigest())")
R=$(curl -s -m 10 -X POST -H 'Content-Type: application/json' \
      -d "{\"hash\":\"$H\"}" "http://127.0.0.1:$WP/api/auth/login")
C=$(echo "$R" | python3 -c 'import sys,json;print((json.load(sys.stdin).get("data") or {}).get("Credential",""))' 2>/dev/null)
echo "credential 长度: ${#C}"

echo
echo "=== CheckLoginStatus ==="
curl -s -m 10 -X POST -H "Authorization: Bearer $C" -H 'Content-Type: application/json' \
     -d '{}' "http://127.0.0.1:$WP/api/QQLogin/CheckLoginStatus" | head -c 500
echo

echo
echo "=== GetQuickLoginListNew（认领靠它拿 uin） ==="
curl -s -m 10 -X POST -H "Authorization: Bearer $C" -H 'Content-Type: application/json' \
     -d '{}' "http://127.0.0.1:$WP/api/QQLogin/GetQuickLoginListNew" | head -c 500
echo

echo
echo "=== GetQQLoginInfo（备选：可能直接给 uin） ==="
curl -s -m 10 -X POST -H "Authorization: Bearer $C" -H 'Content-Type: application/json' \
     -d '{}' "http://127.0.0.1:$WP/api/QQLogin/GetQQLoginInfo" | head -c 500
echo

echo
echo "=== OneBot get_login_info（6700 端口） ==="
curl -s -m 8 -X POST -H 'Content-Type: application/json' -d '{}' \
     "http://127.0.0.1:$OP/get_login_info" | head -c 300
echo

echo
echo "=== 端口监听 ==="
ss -ltn 2>/dev/null | grep -E ":$WP|:$OP" || echo "  (未监听)"

echo "DIAG_DONE"
