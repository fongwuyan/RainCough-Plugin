# -*- coding: utf-8 -*-
"""QQ 框架后端的统一接口：NapCat（原生 systemd）与 SnowLuma（Docker）。

为什么要这一层：
  两个框架的形态差得很远 ——
    NapCat：宿主机原生装 QQ + Xvfb + systemd，WebUI 有「取二维码」的 API
    SnowLuma：整包跑在 Docker 里（镜像自带 QQ + Xvfb + noVNC），
              **没有二维码 API**，只能在远程桌面里扫码
  面板的「QQ 账户」页只想问「现在什么状态、怎么登录、能不能重启」，
  不该关心底下是哪个框架。所以这里做一层适配。

对外只暴露这些函数（返回结构两者一致）：
    kind()           当前用的是哪个框架
    account_info()   账号信息（uin/nick/avatar/login/state/端口…）
    scan()           登录入口（NapCat 给二维码文本；SnowLuma 给 noVNC 地址）
    refresh_scan()   刷新二维码（SnowLuma 是重开远程桌面，无意义就返回同样的）
    status()         扫码进度
    action(act)      start / stop / restart / quick_login / logout
    logs(n)          运行日志
    logs_clear()     清空日志缓冲（仅 NapCat 有内存缓冲）
"""
import hashlib
import json
import os
import urllib.error
import urllib.request

from . import single, snowluma

# ---------------------------------------------------------------- 配置

_DEF = {
    "kind": "napcat",              # napcat | snowluma
    "snowluma_public_host": "",    # noVNC 对外主机名（空=由前端用当前页面 host 拼）
}


# ★ 后端的开关存在**插件自己的配置**里（<插件目录>/data/config.json），
#   不能存 rcbot 的配置 —— rcbot 进程把配置读进内存后，
#   任何一次 config.save 都会把内存里的旧值写回去，插件的修改就丢了。
#   （这是实测踩到的：切到 snowluma 后重启 rcbot，backend.kind 又变回 napcat）
_PLUGIN_CFG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "config.json")


def _read_plugin_cfg():
    try:
        with open(_PLUGIN_CFG, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def _write_plugin_cfg(d):
    try:
        os.makedirs(os.path.dirname(_PLUGIN_CFG), exist_ok=True)
        tmp = _PLUGIN_CFG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _PLUGIN_CFG)
        return True
    except Exception:
        return False


def cfg():
    """读插件配置里的 backend 段。"""
    c = _read_plugin_cfg().get("backend") or {}
    out = dict(_DEF)
    out.update({k: v for k, v in (c or {}).items() if k in out})
    return out


def kind():
    k = str(cfg().get("kind") or "napcat").strip().lower()
    return k if k in ("napcat", "snowluma") else "napcat"


def set_kind(k):
    """切换后端（写插件配置）。仅切开关，不动底层服务。"""
    d = _read_plugin_cfg()
    b = d.get("backend") or {}
    b["kind"] = str(k).strip().lower()
    d["backend"] = b
    if not _write_plugin_cfg(d):
        raise RuntimeError("写插件配置失败：%s" % _PLUGIN_CFG)
    return b["kind"]


# ---------------------------------------------------------------- NapCat 客户端
#
# 这里的实现刻意**不依赖 server_v4.py** —— 那个模块里的 _nc_* 是给概览页用的，
# 从那边 import 会形成循环依赖（server_v4 → backend → server_v4）。
# 账户页只需要 4 个接口，在这里直接实现更清楚。

def _nc_login(port, token, timeout=10):
    """NapCat WebUI 登录，换 Credential。"""
    url = "http://127.0.0.1:%d/api/auth/login" % int(port)
    h = hashlib.sha256((token + ".napcat").encode("utf-8")).hexdigest()
    req = urllib.request.Request(
        url, data=json.dumps({"hash": h}).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        return str(((d.get("data") or {}).get("Credential")) or "")
    except Exception:
        return ""


def _nc_post(port, token, path, body=None, timeout=10):
    """调 NapCat WebUI 的 /api/QQLogin/*。返回 data；失败抛异常。

    ★ NapCat 的 Unauthorized 有两种形态：HTTP 401/403，以及
      **HTTP 200 + body {code:-1,message:"Unauthorized"}**（新版常见）。
      两种都要重登一次再试。
    """
    cred = _nc_login(port, token, timeout)
    if not cred:
        raise RuntimeError("连不上 NapCat WebUI（127.0.0.1:%d）" % int(port))

    def _do(c):
        req = urllib.request.Request(
            "http://127.0.0.1:%d/api%s" % (int(port), path),
            data=json.dumps(body or {}).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + c},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return None
            raise RuntimeError("NapCat %s 返回 HTTP %s" % (path, e.code))

    r = _do(cred)
    if r is None or str(r.get("message") or "").lower() == "unauthorized":
        cred = _nc_login(port, token, timeout)      # 强制重登
        r = _do(cred)
    if r is None:
        raise RuntimeError("NapCat 鉴权失败（%s）" % path)
    if r.get("code") not in (0, None):
        raise RuntimeError("NapCat %s 失败：%s" % (path, r.get("message") or r.get("code")))
    return r.get("data")


# ---------------------------------------------------------------- NapCat 实现

def _napcat_info():
    out = {"backend": "napcat", "uin": "", "nick": "", "avatar": "",
           "login": False, "accepted": False, "core_ready": False,
           "phase": "", "state": "unknown", "webui_port": 0, "onebot_port": 0,
           "webui": "", "scan_mode": "qrcode", "error": ""}
    try:
        ok, st = single.ensure_running()
    except Exception as e:
        out["error"] = str(e)[:160]
        return out
    out["state"] = st
    wp, op = single.webui_port(), single.onebot_port()
    out["webui_port"], out["onebot_port"] = wp, op
    out["webui"] = "http://127.0.0.1:%d" % wp

    token = _nc_token()
    try:
        s = _nc_post(wp, token, "/QQLogin/CheckLoginStatus", timeout=8) or {}
        out["login"] = bool(s.get("isLogin"))
        out["accepted"] = bool(s.get("qrLoginAccepted"))
        out["core_ready"] = bool(s.get("coreReady"))
        out["phase"] = s.get("loginPhase") or ""
        out["qrcode"] = s.get("qrcodeurl") or ""
    except Exception as e:
        out["error"] = str(e)[:160]

    if out["login"]:
        try:
            info = _nc_post(wp, token, "/QQLogin/GetQQLoginInfo", timeout=8) or {}
            out["uin"] = str(info.get("uin") or "")
            out["nick"] = info.get("nick") or ""
            out["avatar"] = info.get("faceUrl") or info.get("avatar") or ""
        except Exception:
            pass
    return out


def _nc_token():
    try:
        from . import config as _c
        return ((_c.load() or {}).get("napcat") or {}).get("token") or "rcnapcat"
    except Exception:
        return "rcnapcat"


# ---------------------------------------------------------------- SnowLuma 实现

def _snowluma_info():
    out = {"backend": "snowluma", "uin": "", "nick": "", "avatar": "",
           "login": False, "accepted": False, "core_ready": False,
           "phase": "", "state": "absent", "webui_port": snowluma.WEBUI_PORT,
           "onebot_port": snowluma.ONEBOT_WS_PORT, "webui": "",
           "scan_mode": "novnc", "novnc_port": snowluma.NOVNC_PORT,
           "novnc_path": "", "novnc_password": "", "error": ""}
    if not snowluma.docker_ok():
        out["error"] = "Docker 不可用"
        return out

    st = snowluma.state()
    out["state"] = st
    if st == "running":
        info = snowluma.login_info()
        if info:
            out["uin"] = info.get("uin") or ""
            out["nick"] = info.get("nick") or ""
            out["login"] = True
            # SnowLuma 没有"手机已确认/核心就绪"这种中间态 ——
            # OneBot 能回 get_login_info 就说明 QQ 已登录、hook 已注入
            out["accepted"] = True
            out["core_ready"] = True
            out["phase"] = "ready"
        else:
            out["phase"] = "waiting_qrcode"
    else:
        out["phase"] = "stopped" if st != "absent" else "absent"

    pw = snowluma.vnc_password()
    out["novnc_password"] = pw
    host = str(cfg().get("snowluma_public_host") or "")
    q = "autoconnect=1&resize=scale"
    if pw:
        q += "&password=" + urllib.request.quote(pw)
    out["novnc_path"] = "/vnc.html?" + q
    out["novnc_url"] = ("http://%s:%d%s" % (host, snowluma.NOVNC_PORT, out["novnc_path"])
                        if host else "")
    return out


# ---------------------------------------------------------------- 统一接口

def account_info():
    if kind() == "snowluma":
        out = _snowluma_info()
    else:
        out = _napcat_info()
    # 头像：两边都可能拿不到，按 QQ 号现拼（QQ 头像是独立服务）
    if not out.get("avatar"):
        out["avatar"] = _avatar(out.get("uin") or "")
    # rcbot 侧的连接状态（谁连上谁没连上，只有 rcbot 自己知道）
    try:
        from . import config as _c
        api = ((_c.load() or {}).get("api") or "http://127.0.0.1:6710").rstrip("/")
        with urllib.request.urlopen(api + "/api/status", timeout=6) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        accs = ((d.get("data") or {}).get("accounts") or [])
        a = accs[0] if accs else None
        if a:
            out["online"] = bool(a.get("online"))
            out["connected"] = bool(a.get("connected"))
            if not out.get("uin"):
                out["uin"] = str(a.get("uin") or "")
            if not out.get("nick"):
                out["nick"] = a.get("nick") or ""
            if not out.get("avatar"):
                out["avatar"] = a.get("avatar") or _avatar(out.get("uin") or "")
    except Exception:
        pass
    return out


def _avatar(uin, size=100):
    u = str(uin or "").strip()
    if not u.isdigit() or len(u) < 5 or len(u) > 12:
        return ""
    return "https://q1.qlogo.cn/g?b=qq&nk=%s&s=%d" % (u, int(size))


def scan():
    """登录入口。

    NapCat  → {mode:'qrcode', qrcode:'https://txz.qq.com/...'}
    SnowLuma→ {mode:'novnc', novnc_port, novnc_path, novnc_password}
    """
    if kind() == "snowluma":
        ok, msg = snowluma.create()
        info = _snowluma_info()
        if not ok:
            raise RuntimeError("启动 SnowLuma 容器失败：%s" % str(msg)[:200])
        if info.get("login"):
            return {"mode": "novnc", "login": True, "uin": info.get("uin") or "",
                    "nick": info.get("nick") or "",
                    "novnc_port": info.get("novnc_port"),
                    "novnc_path": info.get("novnc_path") or "",
                    "novnc_password": info.get("novnc_password") or "",
                    "hint": "已经登录了"}
        return {"mode": "novnc", "login": False,
                "novnc_port": info.get("novnc_port"),
                "novnc_path": info.get("novnc_path") or "",
                "novnc_password": info.get("novnc_password") or "",
                "hint": "在下面的远程桌面里用手机 QQ 扫码登录"}

    # NapCat
    single.ensure_running()
    wp = single.webui_port()
    token = _nc_token()
    st = _nc_post(wp, token, "/QQLogin/CheckLoginStatus", timeout=10) or {}
    if st.get("isLogin"):
        info = _nc_post(wp, token, "/QQLogin/GetQQLoginInfo", timeout=8) or {}
        return {"mode": "qrcode", "login": True, "qrcode": "",
                "phase": st.get("loginPhase") or "",
                "uin": str(info.get("uin") or ""), "nick": info.get("nick") or "",
                "hint": "已经登录了"}
    qr = st.get("qrcodeurl") or ""
    if not qr:
        try:
            q = _nc_post(wp, token, "/QQLogin/GetQQLoginQrcode", timeout=10) or {}
            qr = q.get("qrcode") or ""
        except Exception:
            qr = ""
    return {"mode": "qrcode", "login": False, "qrcode": qr,
            "phase": st.get("loginPhase") or "",
            "hint": "用手机 QQ 扫描下面的二维码授权登录"}


def refresh_scan():
    if kind() == "snowluma":
        # 远程桌面没有"刷新二维码"的概念 —— QQ 自己会轮换
        return {"mode": "novnc", "hint": "远程桌面里 QQ 会自动刷新二维码"}
    wp = single.webui_port()
    r = _nc_post(wp, _nc_token(), "/QQLogin/RefreshQRcode", timeout=10) or {}
    return {"mode": "qrcode", "qrcode": r.get("qrcodeurl") or r.get("qrcode") or ""}


def status():
    """扫码进度。"""
    info = account_info()
    if kind() == "snowluma":
        return {"done": bool(info.get("login")), "uin": info.get("uin") or "",
                "nick": info.get("nick") or "", "avatar": info.get("avatar") or "",
                "phase": info.get("phase") or "",
                "accepted": bool(info.get("login")),
                "logged": bool(info.get("login")),
                "core_ready": bool(info.get("login")),
                "onebot_ready": bool(info.get("login")),
                "backend": "snowluma", "error": info.get("error") or ""}
    return {"done": bool(info.get("login")), "uin": info.get("uin") or "",
            "nick": info.get("nick") or "", "avatar": info.get("avatar") or "",
            "phase": info.get("phase") or "",
            "accepted": bool(info.get("accepted")),
            "logged": bool(info.get("login")),
            "core_ready": bool(info.get("core_ready")),
            "onebot_ready": bool(info.get("login")) and single.port_listening(
                single.onebot_port()),
            "backend": "napcat", "error": info.get("error") or ""}


def action(act):
    """账户操作。"""
    act = str(act or "").lower()
    if kind() == "snowluma":
        if act == "start":
            ok, msg = snowluma.create()
            if not ok:
                raise RuntimeError("启动失败：%s" % str(msg)[:200])
            return {"action": act, "state": snowluma.state()}
        if act == "stop":
            snowluma.stop()
            return {"action": act, "state": snowluma.state()}
        if act == "restart":
            ok, msg = snowluma.restart()
            if not ok:
                raise RuntimeError("重启失败：%s" % str(msg)[:200])
            return {"action": act, "state": snowluma.state()}
        if act == "logout":
            # 换号：删容器（数据卷保留则登录态还在，所以要连卷一起清）
            snowluma.remove()
            snowluma.sh("docker volume rm qq-client-config qq-client-data 2>/dev/null",
                        timeout=60)
            return {"action": act, "removed": True,
                    "hint": "已清登录态，重新扫码即可换号"}
        if act == "quick_login":
            raise RuntimeError("SnowLuma 没有快登概念 —— QQ 客户端自己会记住上次的号")
        raise RuntimeError("不认识的动作：%s" % act)

    # NapCat
    if act == "logout":
        single.logout()
        single.restart()
        return {"action": act, "removed": True}
    if act in ("start", "stop", "restart"):
        if act == "start":
            single.ensure_running()
        elif act == "stop":
            single.stop()
        else:
            single.ensure_running()
            single.restart()
        return {"action": act, "state": single.unit_state()}
    if act == "quick_login":
        wp = single.webui_port()
        info = _nc_post(wp, _nc_token(), "/QQLogin/GetQQLoginInfo", timeout=8) or {}
        uin = str(info.get("uin") or "")
        if not uin:
            raise RuntimeError("还没登录，没有可快登的号")
        return _nc_post(wp, _nc_token(), "/QQLogin/SetQuickLogin", {"uin": uin})
    raise RuntimeError("不认识的动作：%s" % act)


def logs(lines=400):
    n = max(50, min(2000, int(lines or 400)))
    if kind() == "snowluma":
        txt = snowluma.logs(n)
        items = [{"level": _guess_level(x), "text": x, "ts": 0}
                 for x in (txt or "").splitlines()]
        return {"items": items, "source": "docker", "total": len(items),
                "connected": snowluma.state() == "running",
                "err": "" if items else "",
                "unit": snowluma.CONTAINER,
                "hint": "" if items else (
                    "没有日志。容器可能还没启动（点「启动」或「扫码登录」拉起它）")}
    txt = single.sh("journalctl -u %s --no-pager -n %d 2>/dev/null"
                    % (single.UNIT, n), timeout=30)[1]
    items = [{"level": _guess_level(x), "text": x, "ts": 0}
             for x in (txt or "").splitlines()]
    return {"items": items, "source": "journal", "total": len(items),
            "connected": single.unit_state() == "active",
            "err": "", "unit": single.UNIT,
            "hint": "" if items else "读不到 systemd 日志"}


def _guess_level(line):
    s = (line or "").lower()
    if "[error]" in s or " error" in s or "失败" in s or "failed" in s:
        return "error"
    if "[warn]" in s or " warning" in s or "警告" in s:
        return "warn"
    if "[debug]" in s:
        return "debug"
    return "info"


def onebot_call(action, body=None, timeout=10):
    """调 OneBot 的一个 action（只对 SnowLuma 有意义；NapCat 走 WS 不提供 HTTP）。"""
    if kind() != "snowluma":
        return None
    return snowluma._onebot("/" + action, body, timeout)


def onebot_port():
    """OneBot 端口 —— rcbot 连这个。"""
    if kind() == "snowluma":
        return snowluma.ONEBOT_WS_PORT
    return single.onebot_port()


def onebot_url():
    """OneBot WebSocket 的完整地址（含 token 查询参数）。"""
    if kind() == "snowluma":
        return "ws://127.0.0.1:%d/?access_token=%s" % (
            snowluma.ONEBOT_WS_PORT, snowluma.ONEBOT_TOKEN)
    return "ws://127.0.0.1:%d" % single.onebot_port()
