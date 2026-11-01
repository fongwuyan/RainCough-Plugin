#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""雨咯Bot 插件 —— 统一控制台网关。

三块后端：
  · NapCat（协议端）—— 概览 / QQ 账户 / 运行日志，走它自己的 WebUI API
  · rcbot（机器人）—— 模型提供商 / 人格 / 会话 / 上下文 / 聊天记录，走 127.0.0.1:6710
  · NapCat 实例管理 —— systemd 模板多实例（tools/napcat_inst.py）

插件本身不持有业务状态，只做转发与聚合；NapCat 的 Credential 与日志环形缓冲
是唯一的进程内缓存，重启即失效、可自愈。
"""

import collections
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcplugin as rc  # noqa: E402

NAME = "QQBot"          # ★ 必须与插件目录名一致（目录名即插件身份，不改）
VERSION = "1.3.0"
LABEL = "雨咯Bot"

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, "data")
os.makedirs(DATA, exist_ok=True)
CFG_FILE = os.path.join(DATA, "config.json")

DEFAULT_CFG = {
    "api": "http://127.0.0.1:6710",          # rcbot
    "timeout": 90,
    "napcat": {
        "base": "http://127.0.0.1:6099",     # NapCat WebUI（默认实例）
        "token": "rcnapcat",
        "unit": "napcat",                    # systemd 单元名（读历史日志用）
    },
    # ★ 多实例：NapCat 实例的 systemd 管理
    "instances": {
        "base_dir": "/opt/napcat/instances",
        "webui_base": 6099,      # WebUI = base + index
        "onebot_base": 6700,     # OneBot = base + 2*index（避开 rcbot 的 6710）
        "manage_enabled": True,  # 是否允许面板增删实例（需要 root）
    },
}


def _cfg():
    try:
        with open(CFG_FILE, "r", encoding="utf-8") as f:
            d = json.load(f) or {}
    except Exception:
        d = {}
    out = json.loads(json.dumps(DEFAULT_CFG))
    for k, v in d.items():
        if k == "napcat" and isinstance(v, dict):
            out["napcat"].update({kk: vv for kk, vv in v.items() if kk in out["napcat"]})
        elif k in out:
            out[k] = v
    return out


def _save_cfg(d):
    tmp = CFG_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CFG_FILE)


def _q(s):
    return urllib.parse.quote(str(s), safe="")


# ---------------------------------------------------------------- rcbot 转发

def _req(path, method="GET", body=None, timeout=None):
    cfg = _cfg()
    url = cfg["api"].rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout or cfg["timeout"]) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return {"ok": False, "error": "rcbot 返回 HTTP %s" % e.code}
    except Exception as e:
        return {"ok": False,
                "error": "连不上 rcbot（%s）。在服务器上跑 systemctl status rcbot 看看"
                         % str(e)[:120]}


def _data(path, method="GET", body=None, timeout=None):
    r = _req(path, method, body, timeout)
    if not r.get("ok"):
        raise RuntimeError(r.get("error") or "rcbot 返回失败")
    return r.get("data")


# ---------------------------------------------------------------- NapCat 客户端

_CRED = {"val": "", "exp": 0}
_CRED_LOCK = threading.RLock()


def _nc_login(force=False):
    """NapCat WebUI 的登录口令是 sha256(token + '.napcat')，返回 Credential。"""
    with _CRED_LOCK:
        if not force and _CRED["val"] and _CRED["exp"] > time.time():
            return _CRED["val"]
        cfg = _cfg()["napcat"]
        token = (cfg.get("token") or "").strip()
        if not token:
            raise RuntimeError("没有配置 NapCat WebUI token（设置页可改）")
        h = hashlib.sha256((token + ".napcat").encode("utf-8")).hexdigest()
        url = cfg["base"].rstrip("/") + "/api/auth/login"
        req = urllib.request.Request(
            url, json.dumps({"hash": h}).encode("utf-8"),
            {"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            raise RuntimeError("连不上 NapCat WebUI（%s）：%s"
                               % (cfg.get("base"), str(e)[:120]))
        cred = (d.get("data") or {}).get("Credential") or ""
        if not cred:
            raise RuntimeError("NapCat 登录失败：token 不对？（返回 %s）"
                               % json.dumps(d, ensure_ascii=False)[:160])
        _CRED["val"] = cred
        _CRED["exp"] = time.time() + 50 * 60
        return cred


def _nc(path, body=None, method="POST", timeout=15, retry=True):
    cfg = _cfg()["napcat"]
    url = cfg["base"].rstrip("/") + "/api" + path
    data = json.dumps(body if body is not None else {}).encode("utf-8") if method == "POST" else None
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + _nc_login()}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        if retry and e.code in (401, 403):
            _nc_login(force=True)
            return _nc(path, body, method, timeout, retry=False)
        raise RuntimeError("NapCat %s 返回 HTTP %s" % (path, e.code))
    except Exception as e:
        raise RuntimeError("NapCat 请求失败（%s）：%s" % (path, str(e)[:120]))


def _nc_data(path, body=None, method="POST", timeout=15):
    r = _nc(path, body, method, timeout)
    if r.get("code") not in (0, None):
        raise RuntimeError("NapCat %s 失败：%s" % (path, r.get("message") or r.get("code")))
    return r.get("data")


# ---- 指定实例的 NapCat 调用（多账号时每个实例有自己的 WebUI 端口与 token）
#
# Credential 是 per-instance 的（登录的是那个实例的 WebUI），
# 所以要单独缓存，不能共用 _CRED。

_CRED_AT = {}
_CRED_AT_LOCK = threading.RLock()


def _nc_login_at(base, token, force=False):
    """对指定 WebUI 登录，返回 Credential。"""
    with _CRED_AT_LOCK:
        key = base + "|" + token
        c = _CRED_AT.get(key)
        if not force and c and c["exp"] > time.time():
            return c["val"]
        digest = hashlib.sha256((token + ".napcat").encode("utf-8")).hexdigest()
        url = base.rstrip("/") + "/api/auth/login"
        data = json.dumps({"token": digest}).encode("utf-8")
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            raise RuntimeError("连不上 NapCat WebUI（%s）：%s" % (base, str(e)[:120]))
        cred = (d.get("data") or {}).get("Credential") or ""
        if not cred:
            raise RuntimeError("NapCat 登录失败：token 不对？")
        _CRED_AT[key] = {"val": cred, "exp": time.time() + 50 * 60}
        return cred


def _nc_at(base, token, path, body=None, method="POST", timeout=15, retry=True):
    url = base.rstrip("/") + "/api" + path
    data = json.dumps(body if body is not None else {}).encode("utf-8") if method == "POST" else None
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + _nc_login_at(base, token)}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        if retry and e.code in (401, 403):
            _nc_login_at(base, token, force=True)
            return _nc_at(base, token, path, body, method, timeout, retry=False)
        raise RuntimeError("NapCat %s 返回 HTTP %s" % (path, e.code))
    except Exception as e:
        raise RuntimeError("NapCat 请求失败（%s）：%s" % (path, str(e)[:120]))


def _nc_data_at(base, token, path, body=None, method="POST", timeout=15):
    r = _nc_at(base, token, path, body, method, timeout)
    if r.get("code") not in (0, None):
        raise RuntimeError("NapCat %s 失败：%s" % (path, r.get("message") or r.get("code")))
    return r.get("data")


# ---------------------------------------------------------------- NapCat 实时日志缓冲

_LOG_BUF = collections.deque(maxlen=4000)
_LOG_LOCK = threading.Lock()
_LOG_THREAD = None
_LOG_STATE = {"connected": False, "err": "", "ts": 0}


def _log_push(level, msg):
    if not msg:
        return
    with _LOG_LOCK:
        _LOG_BUF.append({"level": (level or "info").lower(), "text": msg,
                         "ts": int(time.time())})


def _log_worker():
    """常驻订阅 NapCat 的 SSE 实时日志，写进环形缓冲。"""
    while True:
        try:
            cfg = _cfg()["napcat"]
            url = cfg["base"].rstrip("/") + "/api/Log/GetLogRealTime"
            req = urllib.request.Request(url, headers={
                "Authorization": "Bearer " + _nc_login(),
                "Accept": "text/event-stream"})
            with urllib.request.urlopen(req, timeout=90) as r:
                _LOG_STATE.update(connected=True, err="", ts=int(time.time()))
                for raw in r:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if not payload:
                        continue
                    try:
                        obj = json.loads(payload)
                    except Exception:
                        _log_push("info", payload)
                        continue
                    if isinstance(obj, dict):
                        _log_push(obj.get("level"), obj.get("message") or obj.get("msg") or "")
                    else:
                        _log_push("info", str(obj))
                _LOG_STATE.update(connected=False, err="SSE 结束")
        except Exception as e:
            _LOG_STATE.update(connected=False, err=str(e)[:160])
            time.sleep(4)


def _log_ensure():
    global _LOG_THREAD
    if _LOG_THREAD and _LOG_THREAD.is_alive():
        return
    _LOG_THREAD = threading.Thread(target=_log_worker, name="nc-log", daemon=True)
    _LOG_THREAD.start()


def _journal(unit, lines=400):
    if not unit:
        return []
    try:
        p = subprocess.run(
            ["journalctl", "-u", unit, "-n", str(int(lines)),
             "--no-pager", "-o", "cat"],
            capture_output=True, timeout=12)
        txt = (p.stdout or b"").decode("utf-8", "replace")
        if p.returncode != 0 and not txt.strip():
            return []
        return [ln for ln in txt.splitlines() if ln.strip()]
    except Exception:
        return []


_LV = re.compile(r"\[(INFO|WARN|WARNING|ERROR|DEBUG|FATAL|TRACE)\]", re.I)


def _guess_level(line):
    m = _LV.search(line)
    if m:
        lv = m.group(1).lower()
        return "warn" if lv == "warning" else lv
    low = line.lower()
    if "error" in low or "失败" in line:
        return "error"
    if "warn" in low:
        return "warn"
    if "debug" in low:
        return "debug"
    return "info"


# ---------------------------------------------------------------- 连接设置

@rc.interface("qqbot.health")
def health(params):
    return {"ok": True, "ts": int(time.time()), "version": VERSION}


@rc.interface("qqbot.conn.get")
def conn_get(params):
    cfg = _cfg()
    nc_ok, nc_err = False, ""
    try:
        _nc_login()
        nc_ok = True
    except Exception as e:
        nc_err = str(e)[:160]
    rb_ok, rb_err = False, ""
    try:
        _data("/api/status", timeout=8)
        rb_ok = True
    except Exception as e:
        rb_err = str(e)[:160]
    return {"ok": True, "config": cfg, "version": VERSION,
            "napcat": {"ok": nc_ok, "error": nc_err},
            "rcbot": {"ok": rb_ok, "error": rb_err}}


@rc.interface("qqbot.conn.save")
def conn_save(params):
    p = (params or {}).get("config") or {}
    d = _cfg()
    if "api" in p:
        d["api"] = str(p.get("api") or "").strip().rstrip("/") or DEFAULT_CFG["api"]
    if "timeout" in p:
        try:
            d["timeout"] = max(10, min(300, int(p["timeout"])))
        except Exception:
            pass
    nc = p.get("napcat") or {}
    if isinstance(nc, dict):
        if "base" in nc:
            d["napcat"]["base"] = str(nc.get("base") or "").strip().rstrip("/") or DEFAULT_CFG["napcat"]["base"]
        if "token" in nc:
            d["napcat"]["token"] = str(nc.get("token") or "").strip()
        if "unit" in nc:
            d["napcat"]["unit"] = str(nc.get("unit") or "").strip() or "napcat"
        _CRED.update(val="", exp=0)
    _save_cfg(d)
    return {"ok": True, "config": d}


# ---------------------------------------------------------------- 概览（NapCat 基础信息）

def _sysinfo_sse(timeout=7):
    """NapCat 的 /base/GetSysStatusRealTime 是 SSE，取第一帧就够。"""
    cfg = _cfg()["napcat"]
    url = cfg["base"].rstrip("/") + "/api/base/GetSysStatusRealTime"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + _nc_login(), "Accept": "text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            deadline = time.time() + timeout
            while time.time() < deadline:
                line = r.readline()
                if not line:
                    break
                s = line.decode("utf-8", "replace").strip()
                if s.startswith("data:"):
                    return json.loads(s[5:].strip())
    except Exception:
        return None
    return None


def _qq_process():
    """找到 QQ 主进程，返回 (pid, rss_mb, cpu_pct 采样)。"""
    try:
        p = subprocess.run(["pgrep", "-af", "qq --no-sandbox"],
                           capture_output=True, timeout=6)
        txt = (p.stdout or b"").decode("utf-8", "replace").strip().splitlines()
        if not txt:
            return None
        pid = int(txt[0].split()[0])
        with open("/proc/%d/status" % pid, "r", encoding="utf-8") as f:
            st = f.read()
        rss = 0
        for ln in st.splitlines():
            if ln.startswith("VmRSS:"):
                rss = int(ln.split()[1]) / 1024.0
                break
        return {"pid": pid, "rss_mb": round(rss, 1)}
    except Exception:
        return None


@rc.interface("qqbot.nc.overview")
def nc_overview(params):
    out = {"ok": True, "account": {}, "versions": {}, "sys": None,
           "counters": {}, "proc": None, "errors": []}

    # 账号
    try:
        st = _nc_data("/QQLogin/CheckLoginStatus") or {}
        out["account"].update({
            "login": bool(st.get("isLogin")),
            "offline": bool(st.get("isOffline")),
            "phase": st.get("loginPhase") or "",
            "qrcode": st.get("qrcodeurl") or "",
        })
    except Exception as e:
        out["errors"].append("账号状态：%s" % str(e)[:120])

    try:
        ql = _nc_data("/QQLogin/GetQuickLoginListNew") or []
        if isinstance(ql, dict):
            ql = ql.get("list") or []
        if ql:
            cur = ql[0]
            out["account"].update({
                "uin": str(cur.get("uin") or ""),
                "nick": cur.get("nickName") or "",
                "avatar": cur.get("faceUrl") or "",
            })
        out["quick"] = [{"uin": str(x.get("uin") or ""), "nick": x.get("nickName") or "",
                         "avatar": x.get("faceUrl") or ""} for x in ql]
    except Exception as e:
        out["errors"].append("快速登录：%s" % str(e)[:120])

    # 版本
    try:
        v = _nc_data("/base/GetNapCatVersion", method="GET")
        out["versions"]["napcat"] = (v or {}).get("version") if isinstance(v, dict) else str(v)
    except Exception as e:
        out["errors"].append("NapCat 版本：%s" % str(e)[:120])
    try:
        qv = _nc_data("/base/QQVersion", method="GET")
        out["versions"]["qq"] = qv if isinstance(qv, str) else (qv or {}).get("version")
    except Exception as e:
        out["errors"].append("QQ 版本：%s" % str(e)[:120])
    out["versions"]["webui"] = "Next"

    # 系统
    out["sys"] = _sysinfo_sse()
    out["proc"] = _qq_process()

    # 网络计数
    try:
        ob = _nc_data("/OB11Config/GetConfig") or {}
        net = ob.get("network") or {}
        out["counters"] = {
            "configs": len([1 for k in ("httpServers", "httpClients", "websocketServers",
                                        "websocketClients", "httpSseServers")
                            if net.get(k)]),
            "httpServers": len(net.get("httpServers") or []),
            "httpClients": len(net.get("httpClients") or []),
            "wsServers": len(net.get("websocketServers") or []),
            "wsClients": len(net.get("websocketClients") or []),
            "sseServers": len(net.get("httpSseServers") or []),
        }
    except Exception as e:
        out["errors"].append("网络配置：%s" % str(e)[:120])

    # rcbot 侧状态（顺带带上，前端概览底部展示）
    try:
        out["bot"] = _data("/api/status", timeout=8)
    except Exception as e:
        out["bot"] = None
        out["errors"].append("rcbot：%s" % str(e)[:120])
    return out


# ---------------------------------------------------------------- QQ 账户

@rc.interface("qqbot.nc.account")
def nc_account(params):
    out = {"ok": True, "status": {}, "quick": [], "qrcode": "", "errors": []}
    try:
        st = _nc_data("/QQLogin/CheckLoginStatus") or {}
        out["status"] = {
            "login": bool(st.get("isLogin")),
            "offline": bool(st.get("isOffline")),
            "phase": st.get("loginPhase") or "",
            "coreReady": bool(st.get("coreReady")),
            "err": st.get("loginError") or st.get("loginErrMsg") or "",
        }
        out["qrcode"] = st.get("qrcodeurl") or ""
    except Exception as e:
        out["errors"].append("账号状态：%s" % str(e)[:140])

    try:
        ql = _nc_data("/QQLogin/GetQuickLoginListNew") or []
        if isinstance(ql, dict):
            ql = ql.get("list") or []
        out["quick"] = [{"uin": str(x.get("uin") or ""), "nick": x.get("nickName") or "",
                         "avatar": x.get("faceUrl") or "",
                         "online": bool(x.get("isQuickLogin"))} for x in ql]
        if out["quick"] and not out["status"].get("login") is None:
            out["status"]["uin"] = out["quick"][0]["uin"]
            out["status"]["nick"] = out["quick"][0]["nick"]
            out["status"]["avatar"] = out["quick"][0]["avatar"]
    except Exception as e:
        out["errors"].append("快速登录：%s" % str(e)[:140])

    # 没登录时拿一张新二维码
    if not out["status"].get("login"):
        try:
            q = _nc_data("/QQLogin/GetQQLoginQrcode") or {}
            out["qrcode"] = q.get("qrcode") or out["qrcode"]
        except Exception as e:
            out["errors"].append("二维码：%s" % str(e)[:140])
    return out


@rc.interface("qqbot.nc.action")
def nc_action(params):
    act = (params or {}).get("action") or ""
    if act == "qrcode":
        return {"ok": True, "data": _nc_data("/QQLogin/GetQQLoginQrcode")}
    if act == "refresh":
        return {"ok": True, "data": _nc_data("/QQLogin/RefreshQRcode")}
    if act == "quick_login":
        uin = str((params or {}).get("uin") or "")
        if not uin:
            raise RuntimeError("缺少 uin")
        return {"ok": True, "data": _nc_data("/QQLogin/SetQuickLogin", {"uin": uin})}
    if act == "restart":
        return {"ok": True, "data": _nc_data("/QQLogin/RestartNapCat")}
    if act == "restart_process":
        return {"ok": True, "data": _nc_data("/Process/Restart")}
    raise RuntimeError("不认识的动作：%s" % act)


# ---------------------------------------------------------------- 运行日志（NapCat）

@rc.interface("qqbot.nc.logs")
def nc_logs(params):
    p = params or {}
    n = max(50, min(2000, int(p.get("lines") or 400)))
    mode = p.get("mode") or "live"
    level = (p.get("level") or "").lower()
    _log_ensure()

    if mode == "history":
        unit = (_cfg()["napcat"].get("unit") or "napcat").strip()
        raw = _journal(unit, n)
        source = "journal"
        items = [{"level": _guess_level(x), "text": x, "ts": 0} for x in raw]
        if not items:
            with _LOG_LOCK:
                items = list(_LOG_BUF)[-n:]
            source = "webui"
    else:
        with _LOG_LOCK:
            items = list(_LOG_BUF)[-n:]
        source = "webui"

    if level:
        items = [x for x in items if x["level"] == level]

    with _LOG_LOCK:
        total = len(_LOG_BUF)
    return {"ok": True, "items": items, "source": source, "total": total,
            "connected": _LOG_STATE["connected"], "err": _LOG_STATE["err"],
            "hint": "" if items else (
                "还没有日志。NapCat 的实时日志走 SSE，连上后新产生的日志会出现在这里"
                if source == "webui" else
                "读不到 systemd 日志（可能不是 systemd 起的，或当前用户没权限）")}


@rc.interface("qqbot.nc.logs.clear")
def nc_logs_clear(params):
    with _LOG_LOCK:
        _LOG_BUF.clear()
    return {"ok": True}


# ---------------------------------------------------------------- NapCat 实例管理
#
# 一个 QQ 号 = 一个 NapCat 实例 = 一套 systemd 单元（napcat@<uin> + xvfb@<n>）。
# 端口：WebUI = 6099+index，OneBot = 6700+2*index（避开 rcbot 的 6710）。


def _inst_cfg():
    return _cfg().get("instances") or {}


def _run(cmd, timeout=60):
    """跑一条命令，返回 (rc, 输出)。"""
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
        return p.returncode, ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
    except Exception as e:
        return 1, str(e)


def _inst_dir(uin):
    base = (_inst_cfg().get("base_dir") or "/opt/napcat/instances").rstrip("/")
    return os.path.join(base, str(uin))


def _inst_env(uin):
    """读实例的 env 文件（端口/display）。"""
    out = {}
    try:
        with open(os.path.join(_inst_dir(uin), "env"), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    out[k.strip()] = v.strip()
    except Exception:
        pass
    return out


def _inst_list():
    """列出所有实例目录。"""
    base = (_inst_cfg().get("base_dir") or "/opt/napcat/instances").rstrip("/")
    out = []
    try:
        for n in sorted(os.listdir(base)):
            d = os.path.join(base, n)
            if os.path.isdir(d):
                out.append(n)
    except Exception:
        pass
    return out


def _unit_state(unit):
    rc_, o = _run("systemctl is-active %s 2>/dev/null" % unit, timeout=15)
    return (o or "").strip() or "unknown"


def _unit_enabled(unit):
    rc_, o = _run("systemctl is-enabled %s 2>/dev/null" % unit, timeout=15)
    return (o or "").strip() or "unknown"


@rc.interface("qqbot.inst.list")
def inst_list(params):
    """实例列表：每个 QQ 号一个 NapCat 实例。"""
    cfg = _cfg()
    icfg = _inst_cfg()
    base = (icfg.get("base_dir") or "/opt/napcat/instances").rstrip("/")
    items = []
    for uin in _inst_list():
        env = _inst_env(uin)
        webui_port = env.get("WEBUI_PORT") or ""
        ob_port = env.get("ONEBOT_PORT") or ""
        disp = env.get("DISPLAY") or ""
        items.append({
            "uin": uin,
            "unit": "napcat@%s" % uin,
            "xvfb_unit": "xvfb@%s" % (disp.lstrip(":") or "1"),
            "state": _unit_state("napcat@%s" % uin),
            "enabled": _unit_enabled("napcat@%s" % uin),
            "webui_port": int(webui_port) if webui_port.isdigit() else 0,
            "onebot_port": int(ob_port) if ob_port.isdigit() else 0,
            "display": disp,
            "dir": _inst_dir(uin),
            "webui": ("http://127.0.0.1:%s" % webui_port) if webui_port else "",
        })
    # rcbot 侧的实际连接状态（哪些号真的连上了）
    try:
        st = _data("/api/accounts", timeout=15) or {}
        live = {str(a.get("uin") or ""): a for a in (st.get("items") or [])}
    except Exception:
        live = {}
    for it in items:
        a = live.get(str(it["uin"]))
        if a:
            it["online"] = bool(a.get("online"))
            it["nick"] = a.get("nick") or ""
            it["avatar"] = a.get("avatar") or ""
            it["account_id"] = a.get("id") or ""
            it["connected"] = bool(a.get("connected"))
        else:
            it["online"] = False
            it["nick"] = ""
            it["avatar"] = ""
    return {"ok": True, "data": {"items": items, "base_dir": base,
                                 "count": len(items)}}


@rc.interface("qqbot.inst.add")
def inst_add(params):
    """新增实例：建目录 + 写 env + 写 systemd 模板 + 启动 + 取二维码。

    需要 root（非 root 面板会明确拒绝，不 sudo）。
    """
    p = params or {}
    uin = str(p.get("uin") or "").strip()
    if not uin.isdigit():
        raise RuntimeError("uin 必须是数字")
    if os.geteuid() != 0:
        raise RuntimeError("新增实例需要 root 权限（当前面板不是 root 运行）")
    if os.path.isdir(_inst_dir(uin)):
        raise RuntimeError("这个 QQ 号的实例已经存在了")

    icfg = _inst_cfg()
    base = (icfg.get("base_dir") or "/opt/napcat/instances").rstrip("/")
    d = os.path.join(base, uin)
    for sub in ("home", "work", "logs"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    os.makedirs(os.path.join(d, "work", "config"), exist_ok=True)

    # 分配端口：实测空闲，且 OneBot 避开 rcbot 的 6710
    _, used_out = _run("ss -ltn 2>/dev/null | awk 'NR>1{print $4}'", timeout=15)
    used = set()
    for line in (used_out or "").splitlines():
        m = re.search(r":(\d+)\s*$", line.strip())
        if m:
            used.add(int(m.group(1)))
    wb = int(icfg.get("webui_base") or 6099)
    ob = int(icfg.get("onebot_base") or 6700)
    idx = 0
    while True:
        wp = wb + idx
        op = ob + 2 * idx
        if op != 6710 and wp not in used and op not in used:
            break
        idx += 1
    disp = 1
    _, disp_out = _run("ps aux 2>/dev/null | grep -o 'Xvfb :[0-9]*'", timeout=15)
    used_d = set(int(x) for x in re.findall(r":(\d+)", disp_out or ""))
    while disp in used_d:
        disp += 1

    with open(os.path.join(d, "env"), "w", encoding="utf-8") as f:
        f.write("# 由雨咯Bot 面板生成 —— 每个实例一份\n")
        f.write("WEBUI_PORT=%d\n" % wp)
        f.write("ONEBOT_PORT=%d\n" % op)
        f.write("DISPLAY=:%d\n" % disp)
        f.write("INDEX=%d\n" % idx)

    token = (cfg_napcat_token())
    wcfg = os.path.join(d, "work", "config", "webui.json")
    if not os.path.exists(wcfg):
        with open(wcfg, "w", encoding="utf-8") as f:
            json.dump({"host": "0.0.0.0", "port": wp, "token": token,
                       "loginRate": 100}, f, ensure_ascii=False)

    # systemd 模板
    _write_units()
    _run("systemctl daemon-reload", timeout=30)

    # 启动
    _run("systemctl enable napcat@%s" % uin, timeout=30)
    _run("systemctl start napcat@%s" % uin, timeout=60)

    # 把账号加进 rcbot 配置（这样 rcbot 会连它）
    try:
        _data("/api/accounts", "POST", {
            "action": "add", "uin": uin,
            "ws_url": "ws://127.0.0.1:%d" % op,
            "webui": "http://127.0.0.1:%d" % wp,
            "unit": "napcat@%s" % uin,
            "instance_dir": d,
        }, timeout=25)
    except Exception as e:
        return {"ok": False, "error": "实例已建好，但加进 rcbot 失败：%s" % str(e)[:200],
                "data": {"uin": uin, "webui_port": wp, "onebot_port": op}}

    return {"ok": True, "data": {"uin": uin, "webui_port": wp,
                                 "onebot_port": op, "display": ":%d" % disp,
                                 "dir": d, "unit": "napcat@%s" % uin}}


def cfg_napcat_token():
    return (_cfg().get("napcat") or {}).get("token") or "rcnapcat"


_XVFB_UNIT = """[Unit]
Description=Xvfb display :%i (for napcat@%i)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :%i -screen 0 1080x760x16 +extension GLX +render
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

_NAPCAT_UNIT = """[Unit]
Description=NapCat instance %i (QQ %i)
After=network-online.target xvfb@%i.service
Wants=network-online.target
Requires=xvfb@%i.service

[Service]
Type=simple
User=root
Environment=HOME=/opt/napcat/instances/%i/home
Environment=NAPCAT_WORKDIR=/opt/napcat/instances/%i/work
Environment=NAPCAT_QUICK_ACCOUNT=%i
Environment=DISPLAY=:%i
EnvironmentFile=-/opt/napcat/instances/%i/env
WorkingDirectory=/opt/napcat/napcat
ExecStart=/opt/napcat/QQ/qq --no-sandbox
Restart=always
RestartSec=5
LimitNOFILE=65535
TimeoutStopSec=30
KillMode=mixed

[Install]
WantedBy=multi-user.target
"""


def _write_units():
    """写 systemd 模板单元。"""
    for name, content in (("xvfb@.service", _XVFB_UNIT),
                           ("napcat@.service", _NAPCAT_UNIT)):
        path = os.path.join("/etc/systemd/system", name)
        try:
            old = ""
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    old = f.read()
            if old != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception:
            pass


@rc.interface("qqbot.inst.action")
def inst_action(params):
    """实例操作：start / stop / restart / qrcode / quick_login / remove。"""
    p = params or {}
    uin = str(p.get("uin") or "").strip()
    act = (p.get("action") or "").lower()
    if not uin:
        raise RuntimeError("缺少 uin")
    env = _inst_env(uin)
    wp = env.get("WEBUI_PORT") or ""
    unit = "napcat@%s" % uin
    token = cfg_napcat_token()

    if act in ("start", "stop", "restart"):
        _run("systemctl %s %s" % (act, unit), timeout=90)
        return {"ok": True, "data": {"uin": uin, "action": act,
                                     "state": _unit_state(unit)}}

    if act == "remove":
        if os.geteuid() != 0:
            raise RuntimeError("删除实例需要 root 权限")
        _run("systemctl disable --now %s" % unit, timeout=60)
        disp = env.get("DISPLAY", ":1").lstrip(":")
        _run("systemctl stop xvfb@%s" % disp, timeout=30)
        try:
            _data("/api/accounts", "POST", {"action": "remove", "id": "a%s" % uin},
                  timeout=25)
        except Exception:
            pass
        import shutil
        d = _inst_dir(uin)
        if os.path.isdir(d) and not p.get("keep_data"):
            shutil.rmtree(d, ignore_errors=True)
        return {"ok": True, "data": {"uin": uin, "removed": True}}

    # 下面的都要连 WebUI，先确认端口
    if not wp:
        raise RuntimeError("这个实例没有 env 文件，端口未知")
    base = "http://127.0.0.1:%s" % wp
    if act == "qrcode":
        st = _nc_data_at(base, token, "/QQLogin/CheckLoginStatus") or {}
        q = _nc_data_at(base, token, "/QQLogin/GetQQLoginQrcode") or {}
        return {"ok": True, "data": {"qrcode": q.get("qrcode") or st.get("qrcodeurl") or "",
                                     "login": bool(st.get("isLogin")),
                                     "phase": st.get("loginPhase") or "",
                                     "webui": base}}

    if act == "quick_login":
        r = _nc_data_at(base, token, "/QQLogin/SetQuickLogin", {"uin": uin})
        return {"ok": True, "data": r}

    if act == "status":
        st = _nc_data_at(base, token, "/QQLogin/CheckLoginStatus") or {}
        return {"ok": True, "data": {"login": bool(st.get("isLogin")),
                                     "phase": st.get("loginPhase") or "",
                                     "coreReady": bool(st.get("coreReady"))}}

    raise RuntimeError("不认识的动作：%s" % act)


@rc.interface("qqbot.inst.logs")
def inst_logs(params):
    """实例日志（journalctl）。"""
    p = params or {}
    uin = str(p.get("uin") or "").strip()
    unit = "napcat@%s" % uin if uin else (p.get("unit") or "napcat")
    n = max(50, min(2000, int(p.get("lines") or 400)))
    _, out = _run("journalctl -u %s -n %d --no-pager 2>/dev/null" % (unit, n), timeout=30)
    items = [{"level": _guess_level(x), "text": x, "ts": 0}
             for x in (out or "").splitlines() if x.strip()]
    return {"ok": True, "items": items, "source": "journal", "total": len(items)}


# ---------------------------------------------------------------- 机器人状态

@rc.interface("rcbot.status")
def status(params):
    return {"ok": True, "data": _data("/api/status", timeout=25)}


# ---------------------------------------------------------------- 聊天记录

@rc.interface("qqbot.chat.sessions")
def chat_sessions(params):
    """聊天记录会话列表。"""
    p = params or {}
    q = {}
    for k in ("account_id", "kind", "kw", "limit"):
        if p.get(k) not in (None, ""):
            q[k] = p[k]
    qs = urllib.parse.urlencode(q)
    return {"ok": True, "data": _data("/api/chat/sessions" + ("?" + qs if qs else ""),
                                       timeout=30)}


@rc.interface("qqbot.chat.messages")
def chat_messages(params):
    """聊天记录消息分页。"""
    p = params or {}
    q = {}
    for k in ("session_id", "before_id", "limit", "kw"):
        if p.get(k) not in (None, ""):
            q[k] = p[k]
    if not q.get("session_id"):
        raise RuntimeError("缺少 session_id")
    qs = urllib.parse.urlencode(q)
    return {"ok": True, "data": _data("/api/chat/messages?" + qs, timeout=30)}


@rc.interface("qqbot.chat.stats")
def chat_stats(params):
    """聊天记录统计 + 媒体占用 + 磁盘水位。"""
    p = params or {}
    q = {}
    if p.get("account_id"):
        q["account_id"] = p["account_id"]
    qs = urllib.parse.urlencode(q)
    return {"ok": True, "data": _data("/api/chat/stats" + ("?" + qs if qs else ""),
                                       timeout=30)}


@rc.interface("qqbot.chat.export")
def chat_export(params):
    """导出 JSON。

    rcbot 的 /api/chat/export 返回的是**文件下载**（带 Content-Disposition），
    不是 JSON-RPC 那样的 {ok,data}，所以这里不能用 _data() —— 要直接取字节再解析。
    """
    p = params or {}
    q = {}
    for k in ("account_id", "session_id", "from", "to"):
        if p.get(k) not in (None, ""):
            q[k] = p[k]
    qs = urllib.parse.urlencode(q)
    url = _cfg()["api"].rstrip("/") + "/api/chat/export" + ("?" + qs if qs else "")
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:
        raise RuntimeError("导出失败：%s" % str(e)[:200])
    try:
        doc = json.loads(raw)
    except Exception as e:
        raise RuntimeError("导出结果不是合法 JSON：%s" % str(e)[:120])
    return {"ok": True, "data": doc}


@rc.interface("qqbot.chat.purge_media")
def chat_purge_media(params):
    """清理媒体文件（保留消息文本）。"""
    p = params or {}
    if p.get("confirm") is not True:
        raise RuntimeError("需要 confirm=true")
    return {"ok": True, "data": _data("/api/chat/purge-media", "POST", {
        "account_id": p.get("account_id") or "",
        "session_id": p.get("session_id") or "",
        "from": int(p.get("from") or 0),
        "to": int(p.get("to") or 0),
        "confirm": True,
    }, timeout=300)}


@rc.interface("rcbot.accounts")
def rcbot_accounts(params):
    """rcbot 侧的账号列表（连接状态）。"""
    return {"ok": True, "data": _data("/api/accounts", timeout=25)}


@rc.interface("rcbot.account.save")
def rcbot_account_save(params):
    """新增/修改/删除账号（rcbot 侧配置）。"""
    p = params or {}
    return {"ok": True, "data": _data("/api/accounts", "POST", p, timeout=25)}


# ---------------------------------------------------------------- 设置（触发 / 上下文 / 能力）

@rc.interface("rcbot.config.get")
def config_get(params):
    return {"ok": True, "data": _data("/api/config")}


@rc.interface("rcbot.config.save")
def config_save(params):
    body = (params or {}).get("config") or {}
    return {"ok": True, "data": _data("/api/config", "POST", body)}


@rc.interface("rcbot.tools.search")
def tools_search(params):
    q = (params or {}).get("q") or ""
    if not q.strip():
        raise RuntimeError("缺少关键词")
    return {"ok": True, "data": _data("/api/tools/search?q=" + _q(q), timeout=40)}


# ---------------------------------------------------------------- 模型提供商

@rc.interface("rcbot.providers")
def providers(params):
    return {"ok": True, "data": _data("/api/providers")}


@rc.interface("rcbot.provider.save")
def provider_save(params):
    return {"ok": True, "data": _data("/api/providers", "POST", params or {})}


@rc.interface("rcbot.provider.delete")
def provider_delete(params):
    return {"ok": True, "data": _data("/api/providers/delete", "POST", params or {})}


@rc.interface("rcbot.provider.test")
def provider_test(params):
    return {"ok": True, "data": _data("/api/providers/test", "POST", params or {}, timeout=150)}


@rc.interface("rcbot.provider.models")
def provider_models(params):
    pid = (params or {}).get("id") or ""
    return {"ok": True, "data": _data("/api/providers/models?id=" + _q(pid), timeout=40)}


# ---------------------------------------------------------------- 人格

@rc.interface("rcbot.personas")
def personas(params):
    return {"ok": True, "data": _data("/api/personas")}


@rc.interface("rcbot.persona.save")
def persona_save(params):
    return {"ok": True, "data": _data("/api/personas", "POST", params or {})}


@rc.interface("rcbot.persona.delete")
def persona_delete(params):
    return {"ok": True, "data": _data("/api/personas/delete", "POST", params or {})}


# ---------------------------------------------------------------- 会话

@rc.interface("rcbot.sessions")
def sessions(params):
    return {"ok": True, "data": _data("/api/sessions")}


@rc.interface("rcbot.session.get")
def session_get(params):
    p = params or {}
    sid = _q(p.get("id") or "")
    limit = int(p.get("limit") or 50)
    return {"ok": True, "data": _data("/api/sessions/%s?limit=%d" % (sid, limit))}


@rc.interface("rcbot.session.save")
def session_save(params):
    p = dict(params or {})
    sid = _q(p.pop("id", ""))
    return {"ok": True, "data": _data("/api/sessions/%s" % sid, "POST", p)}


@rc.interface("rcbot.session.clear")
def session_clear(params):
    sid = _q((params or {}).get("id") or "")
    return {"ok": True, "data": _data("/api/sessions/%s/clear" % sid, "POST", {})}


@rc.interface("rcbot.session.delete")
def session_delete(params):
    return {"ok": True, "data": _data("/api/sessions/delete", "POST", params or {})}


@rc.interface("rcbot.context")
def context_preview(params):
    sid = (params or {}).get("id") or ""
    return {"ok": True, "data": _data("/api/context?sid=" + _q(sid))}


# ---------------------------------------------------------------- 试聊

@rc.interface("rcbot.test_chat")
def test_chat(params):
    return {"ok": True, "data": _data("/api/test/chat", "POST", params or {}, timeout=180)}


IFACES = [
    "qqbot.health", "qqbot.conn.get", "qqbot.conn.save",
    "qqbot.nc.overview", "qqbot.nc.account", "qqbot.nc.action",
    "qqbot.nc.logs", "qqbot.nc.logs.clear",
    "qqbot.inst.list", "qqbot.inst.add", "qqbot.inst.action", "qqbot.inst.logs",
    "qqbot.chat.sessions", "qqbot.chat.messages", "qqbot.chat.stats",
    "qqbot.chat.export", "qqbot.chat.purge_media",
    "rcbot.status", "rcbot.accounts", "rcbot.account.save",
    "rcbot.config.get", "rcbot.config.save", "rcbot.tools.search",
    "rcbot.providers", "rcbot.provider.save", "rcbot.provider.delete",
    "rcbot.provider.test", "rcbot.provider.models",
    "rcbot.personas", "rcbot.persona.save", "rcbot.persona.delete",
    "rcbot.sessions", "rcbot.session.get", "rcbot.session.save",
    "rcbot.session.clear", "rcbot.session.delete", "rcbot.context",
    "rcbot.test_chat",
]


if __name__ == "__main__":
    _log_ensure()
    rc.serve(
        endpoint=os.environ.get("RC_ENDPOINT", ""),
        name=NAME,
        version=VERSION,
        manifest={"label": LABEL, "description": "NapCat + RainCough Bot 统一控制台"},
        frontend={"pages": [{"path": "", "title": LABEL}]},
        iface_ids=IFACES,
        plugin_dir=DIR,
    )
