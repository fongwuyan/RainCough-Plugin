# -*- coding: utf-8 -*-
"""单账户：NapCat 实例的管理（只管 systemd/目录/端口，登录一律走 NapCat 接口）。

★ 设计原则（2026-11-02 从多账户回退到单账户）：
  **登录相关的事全部交给 NapCat 的接口**，插件不自己造状态机。
  NapCat 4.18.42 实际提供的接口（实测探测结果）：

    POST /api/QQLogin/CheckLoginStatus
      → {isLogin, isOffline, loginPhase, qrLoginAccepted, coreReady,
         qrcodeurl, loginError}
      登录状态三层：qrLoginAccepted(手机已确认) / isLogin(QQ已登录)
                  / coreReady(核心就绪，OneBot 开始监听)
    POST /api/QQLogin/GetQQLoginQrcode   → {qrcode: "https://txz.qq.com/..."}
    POST /api/QQLogin/RefreshQRcode      → {qrcodeurl: "..."}
    POST /api/QQLogin/GetQQLoginInfo     → {uid, uin, nick}
                                          ★ 未登录时返回空串，不是报错
    POST /api/QQLogin/GetQuickLoginListNew → []   本机历史登录过的号
    POST /api/QQLogin/SetQuickLogin      {uin}  设快登号
    POST /api/QQLogin/RestartNapCat      重启 NapCat 进程

  不存在的（别调）：Reboot / LogoutQQ / GetQQLoginList / base/GetLoginInfo

  ★ 本模块只负责"把 NapCat 跑起来"（目录、systemd、端口、显示号），
    以及在它没起来时把它拉起来 —— 登录/出码/取号一律由调用方调上面的接口。
"""
import json
import os
import shutil
import subprocess
import time

BASE = "/opt/napcat"
INST_BASE = os.path.join(BASE, "instances")
# ★ 单账户下实例目录固定用一个名字，不跟 QQ 号走 ——
#   换号时不用改名、不用搬目录，登录态由 NapCat 自己管。
SLOT = "main"

WEBUI_PORT = 6099
ONEBOT_PORT = 6700
DISPLAY_NUM = 1
TOKEN = "rcnapcat"

UNIT_DIR = "/etc/systemd/system"
NAPCAT_UNIT = "napcat@%s.service"
XVFB_UNIT_NAME = "xvfb-rcbot-%d.service"

NAPCAT_UNIT_BODY = """[Unit]
Description=NapCat (雨咯Bot)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Environment=HOME=/opt/napcat/instances/main/home
Environment=NAPCAT_WORKDIR=/opt/napcat/instances/main/work
EnvironmentFile=/opt/napcat/instances/main/env
WorkingDirectory=/opt/napcat/napcat
ExecStart=/opt/napcat/QQ/qq --no-sandbox
Restart=always
RestartSec=5
LimitNOFILE=65535
TimeoutStopSec=15
KillMode=control-group

[Install]
WantedBy=multi-user.target
"""

XVFB_UNIT_BODY = """[Unit]
Description=Xvfb display :%d (for 雨咯Bot)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :%d -screen 0 1080x760x16 +extension GLX +render
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

UNIT = "napcat.service"


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
        return p.returncode, ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
    except Exception as e:
        return 1, str(e)


def inst_dir():
    return os.path.join(INST_BASE, SLOT)


def env_path():
    return os.path.join(inst_dir(), "env")


def read_env():
    out = {}
    try:
        with open(env_path(), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    out[k.strip()] = v.strip()
    except Exception:
        pass
    return out


def webui_port():
    v = read_env().get("WEBUI_PORT") or ""
    return int(v) if v.isdigit() else WEBUI_PORT


def onebot_port():
    v = read_env().get("ONEBOT_PORT") or ""
    return int(v) if v.isdigit() else ONEBOT_PORT


def current_uin():
    """问 NapCat 当前登录的是哪个 QQ 号（没登录返回空串）。

    ★ 走 NapCat 官方接口 /api/QQLogin/GetQQLoginInfo，
      不自己维护"哪个实例对应哪个号"的状态。
    """
    try:
        import hashlib
        import json as _json
        import urllib.request
        base = "http://127.0.0.1:%d" % webui_port()
        h = hashlib.sha256((TOKEN + ".napcat").encode("utf-8")).hexdigest()
        req = urllib.request.Request(
            base + "/api/auth/login", data=_json.dumps({"hash": h}).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            cred = (_json.loads(r.read().decode("utf-8", "replace")).get("data")
                    or {}).get("Credential") or ""
        if not cred:
            return ""
        req2 = urllib.request.Request(
            base + "/api/QQLogin/GetQQLoginInfo", data=b"{}",
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + cred}, method="POST")
        with urllib.request.urlopen(req2, timeout=10) as r:
            info = (_json.loads(r.read().decode("utf-8", "replace")).get("data") or {})
        return str(info.get("uin") or "")
    except Exception:
        return ""


def pick_instance():
    """当前账号的 QQ 号。

    ★ 单账户下实例目录固定叫 main，目录名**不是** QQ 号
      （换号时不用改名、不用搬目录，登录态由 NapCat 自己管）。
      所以 QQ 号要问 NapCat —— 没登录时返回空串。
    """
    return current_uin()


def unit_state(unit=UNIT):
    rc, o = sh("systemctl is-active %s 2>/dev/null" % unit, timeout=15)
    return (o or "").strip() or "unknown"


def unit_enabled(unit=UNIT):
    rc, o = sh("systemctl is-enabled %s 2>/dev/null" % unit, timeout=15)
    return (o or "").strip() or "unknown"


def _write(path, content):
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


def ensure_dirs():
    d = inst_dir()
    for sub in ("home", "work", "logs"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    os.makedirs(os.path.join(d, "work", "config"), exist_ok=True)
    return d


def write_env(quick_account=""):
    d = ensure_dirs()
    lines = [
        "# 由雨咯Bot 面板生成 —— 单账户",
        "DISPLAY=:%d" % DISPLAY_NUM,
        "WEBUI_PORT=%d" % WEBUI_PORT,
        "ONEBOT_PORT=%d" % ONEBOT_PORT,
        "INDEX=0",
    ]
    if quick_account:
        lines.append("NAPCAT_QUICK_ACCOUNT=%s" % quick_account)
    with open(env_path(), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return env_path()


def write_webui_config():
    cfg_dir = os.path.join(inst_dir(), "work", "config")
    os.makedirs(cfg_dir, exist_ok=True)
    path = os.path.join(cfg_dir, "webui.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"host": "0.0.0.0", "port": WEBUI_PORT,
                   "token": TOKEN, "loginRate": 100}, f, ensure_ascii=False)
    return path


def write_onebot_config():
    cfg_dir = os.path.join(inst_dir(), "work", "config")
    os.makedirs(cfg_dir, exist_ok=True)
    path = os.path.join(cfg_dir, "onebot11.json")
    cfg = {
        "network": {
            "httpServers": [],
            "httpSseServers": [],
            "httpClients": [],
            "websocketServers": [{
                "debug": False,
                "enable": True,
                "heartInterval": 30000,
                "host": "127.0.0.1",
                "messagePostFormat": "array",
                "name": "rc-core",
                "port": ONEBOT_PORT,
                "reportSelfMessage": False,
                "token": "",
                "enableForcePushEvent": True,
            }],
            "websocketClients": [],
            "plugins": [],
        },
        "musicSignUrl": "",
        "enableLocalFile2Url": False,
        "parseMultMsg": False,
        "imageDownloadProxy": "",
        "timeout": {
            "baseTimeout": 10000,
            "uploadSpeedKBps": 256,
            "downloadSpeedKBps": 256,
            "maxTimeout": 1800000,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    return path


def write_units():
    _write(os.path.join(UNIT_DIR, UNIT), NAPCAT_UNIT_BODY)
    _write(os.path.join(UNIT_DIR, XVFB_UNIT_NAME % DISPLAY_NUM),
           XVFB_UNIT_BODY % (DISPLAY_NUM, DISPLAY_NUM))


def ensure_running():
    """确保 NapCat 在跑。返回 (ok, state)。"""
    ensure_dirs()
    if not os.path.exists(env_path()):
        write_env()
    if not os.path.exists(os.path.join(inst_dir(), "work", "config", "webui.json")):
        write_webui_config()
    if not os.path.exists(os.path.join(inst_dir(), "work", "config", "onebot11.json")):
        write_onebot_config()
    write_units()
    sh("systemctl daemon-reload", timeout=30)

    xvfb = XVFB_UNIT_NAME % DISPLAY_NUM
    sh("systemctl enable %s" % xvfb, timeout=30)
    if unit_state(xvfb) != "active":
        sh("systemctl start %s" % xvfb, timeout=30)

    sh("systemctl enable %s" % UNIT, timeout=30)
    if unit_state(UNIT) != "active":
        sh("systemctl reset-failed %s 2>/dev/null" % UNIT, timeout=15)
        sh("systemctl start %s" % UNIT, timeout=90)
    return unit_state(UNIT) == "active", unit_state(UNIT)


def port_listening(port):
    rc, o = sh("ss -ltn 2>/dev/null | grep -c ':%s '" % port, timeout=10)
    return "1" in (o or "")


def wait_port(port, tries=25):
    for _ in range(tries):
        if port_listening(port):
            return True
        time.sleep(1)
    return False


def stop():
    sh("systemctl disable --now %s 2>/dev/null" % UNIT, timeout=60)
    xvfb = XVFB_UNIT_NAME % DISPLAY_NUM
    sh("systemctl disable --now %s 2>/dev/null" % xvfb, timeout=30)


def restart():
    sh("systemctl restart %s" % UNIT, timeout=90)
    xvfb = XVFB_UNIT_NAME % DISPLAY_NUM
    sh("systemctl start %s" % xvfb, timeout=30)


def logout():
    """换号：清掉登录态（NapCat 的接口没有 LogoutQQ，所以自己清目录）。

    ★ 只删登录态相关的数据，保留目录与配置 ——
      下次扫码仍然是同一个实例，不用重建。
    """
    home = os.path.join(inst_dir(), "home", ".config", "QQ")
    for sub in ("nt_qq_*", "global", "NapCat"):
        p = os.path.join(home, sub)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
    # 清掉快登号，免得它拿失效的登录态反复快登
    write_env()
    try:
        os.remove(env_path() + ".bak")
    except Exception:
        pass
    return True


def cleanup_legacy_instances():
    """清理多账户时代留下的旧实例目录与单元（单账户只保留 main）。

    只删"看起来像旧实例"的：目录名不是 main 且不是纯数字/占位名之外的东西…
    实际上单账户下 main 之外的都该清，但要先保证 main 存在。
    """
    try:
        names = os.listdir(INST_BASE)
    except Exception:
        return []
    removed = []
    for n in names:
        if n == SLOT:
            continue
        d = os.path.join(INST_BASE, n)
        if not os.path.isdir(d):
            continue
        # 旧单元（napcat@<uin>.service / napcat@_pending_*.service）
        for u in ("napcat@%s.service" % n,):
            up = os.path.join(UNIT_DIR, u)
            if os.path.exists(up):
                sh("systemctl disable --now %s 2>/dev/null" % u, timeout=45)
                try:
                    os.remove(up)
                except Exception:
                    pass
        shutil.rmtree(d, ignore_errors=True)
        removed.append(n)
    if removed:
        sh("systemctl daemon-reload", timeout=30)
    return removed
