#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测 NapCat WebUI 实际提供的接口（直接问服务器，返回结构化结果）。"""
import hashlib
import json
import sys
import urllib.error
import urllib.request

WP = int(sys.argv[1] if len(sys.argv) > 1 else 6099)
BASE = "http://127.0.0.1:%d" % WP

h = hashlib.sha256(b"rcnapcat.napcat").hexdigest()
req = urllib.request.Request(
    BASE + "/api/auth/login", data=json.dumps({"hash": h}).encode(),
    headers={"Content-Type": "application/json"}, method="POST")
cred = ""
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read().decode())
    cred = (d.get("data") or {}).get("Credential") or ""
except Exception as e:
    print("登录失败:", e)
    sys.exit(1)
print("credential 长度:", len(cred))


def probe(path, method="POST", body=None):
    url = BASE + "/api" + path
    data = json.dumps(body if body is not None else {}).encode() if method == "POST" else None
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + cred}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = "HTTP %s" % e.code
    except Exception as e:
        raw = "ERR %s" % str(e)[:60]
    try:
        j = json.loads(raw)
        if isinstance(j, dict) and "code" in j:
            summary = "code=%s data=%s" % (j.get("code"),
                                           json.dumps(j.get("data"), ensure_ascii=False)[:140])
            if j.get("message"):
                summary += " msg=%s" % j.get("message")
        else:
            summary = raw[:140].replace("\n", " ")
    except Exception:
        summary = raw[:140].replace("\n", " ")
    print("  %-40s %s" % (method + " " + path, summary))


print("\n=== QQLogin ===")
for p in ("/QQLogin/CheckLoginStatus", "/QQLogin/GetQQLoginInfo",
          "/QQLogin/GetQQLoginQrcode", "/QQLogin/RefreshQRcode",
          "/QQLogin/GetQuickLoginListNew", "/QQLogin/SetQuickLogin",
          "/QQLogin/Reboot", "/QQLogin/RestartNapCat",
          "/QQLogin/LogoutQQ", "/QQLogin/GetQQLoginList",
          "/QQLogin/GetQuickLoginList"):
    probe(p)

print("\n=== base (GET) ===")
for p in ("/base/GetNapCatVersion", "/base/QQVersion", "/base/GetLoginInfo"):
    probe(p, "GET")

print("\n=== OB11Config ===")
for p in ("/OB11Config/GetConfig", "/OB11Config/GetConfigByType"):
    probe(p)
