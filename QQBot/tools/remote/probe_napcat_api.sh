#!/bin/bash
# 探查 NapCat 可用的账号资料接口（昵称/头像/QQ号）
set -u

H=$(python3 -c "import hashlib;print(hashlib.sha256(b'rcnapcat.napcat').hexdigest())")
R=$(curl -s -m 10 -X POST -H 'Content-Type: application/json' \
      -d "{\"hash\":\"$H\"}" http://127.0.0.1:6099/api/auth/login)
C=$(echo "$R" | python3 -c 'import sys,json;print((json.load(sys.stdin).get("data") or {}).get("Credential",""))')
echo "credential 长度: ${#C}"

probe() {
  local path="$1" method="${2:-POST}"
  echo
  echo "--- $method $path ---"
  if [ "$method" = "GET" ]; then
    curl -s -m 8 -H "Authorization: Bearer $C" "http://127.0.0.1:6099/api$path" | head -c 400
  else
    curl -s -m 8 -X POST -H "Authorization: Bearer $C" -H 'Content-Type: application/json' \
         -d '{}' "http://127.0.0.1:6099/api$path" | head -c 400
  fi
  echo
}

probe /QQLogin/GetQuickLoginListNew
probe /QQLogin/CheckLoginStatus
probe /OB11Config/GetConfig
probe /QQLogin/GetQQLoginInfo
probe /base/GetLoginInfo
probe /OB11Config/GetConfig
probe /QQLogin/GetQuickLoginList

echo
echo "=== 探测 OneBot 标准动作（需要已登录） ==="
probe /get_login_info
probe /get_status

echo "PROBE_DONE"
