#!/bin/bash
# 探测 NapCat WebUI 实际提供的接口（逐个试，看返回什么）
set -u

WP="${1:-6099}"
H=$(python3 -c "import hashlib;print(hashlib.sha256(b'rcnapcat.napcat').hexdigest())")
R=$(curl -s -m 10 -X POST -H 'Content-Type: application/json' \
      -d "{\"hash\":\"$H\"}" "http://127.0.0.1:$WP/api/auth/login")
C=$(echo "$R" | python3 -c 'import sys,json;print((json.load(sys.stdin).get("data") or {}).get("Credential",""))' 2>/dev/null)
echo "credential 长度: ${#C}"
[ -z "$C" ] && { echo "登录失败：$R"; exit 1; }

probe() {
  local path="$1" method="${2:-POST}"
  local r
  if [ "$method" = "GET" ]; then
    r=$(curl -s -m 8 -H "Authorization: Bearer $C" "http://127.0.0.1:$WP/api$path")
  else
    r=$(curl -s -m 8 -X POST -H "Authorization: Bearer $C" -H 'Content-Type: application/json' \
         -d '{}' "http://127.0.0.1:$WP/api$path")
  fi
  # 只显示前 200 字符
  printf '  %-42s %s\n' "$method $path" "$(echo "$r" | head -c 200)"
}

echo
echo "=== QQLogin 相关 ==="
for p in \
  /QQLogin/CheckLoginStatus \
  /QQLogin/GetQQLoginInfo \
  /QQLogin/GetQQLoginQrcode \
  /QQLogin/RefreshQRcode \
  /QQLogin/GetQuickLoginListNew \
  /QQLogin/SetQuickLogin \
  /QQLogin/Reboot \
  /QQLogin/RestartNapCat \
  /QQLogin/LogoutQQ \
  /QQLogin/GetQQLoginList
do
  probe "$p"
done

echo
echo "=== base 相关 ==="
for p in \
  /base/GetNapCatVersion \
  /base/GetLoginInfo \
  /base/QQVersion \
  /base/GetQQVersion
do
  probe "$p" GET
done

echo
echo "=== OB11Config 相关 ==="
for p in /OB11Config/GetConfig; do probe "$p"; done

echo
echo "PROBE_DONE"
