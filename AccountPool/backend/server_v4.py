"""号池管理台 · RainCough 控制面.

Go Gateway 负责协议/转发/账号池；这里只负责启动、配置和转发管理 API。
"""
import atexit
import json
import os
import platform
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PLUGIN_DIR)

import rcplugin as rc

DATA_DIR = os.path.join(PLUGIN_DIR, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
TOKEN_FILE = os.path.join(DATA_DIR, "admin.token")
PID_FILE = os.path.join(DATA_DIR, "gateway.pid")
LOG_FILE = os.path.join(DATA_DIR, "gateway.log")

ADMIN_ADDR = "127.0.0.1:18901"
DEFAULT_LAN_ADDR = "127.0.0.1:18900"
VERSION = "0.2.0"

_lock = threading.RLock()
_proc = None

_META = {
    "name": "AccountPool",
    "label": "号池管理台",
    "version": VERSION,
    "description": "自研 Go Gateway：账号池、OpenAI/Anthropic/Gemini 兼容、LAN API",
}


def _settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = {}
    d.setdefault("lan_addr", DEFAULT_LAN_ADDR)
    d.setdefault("lan_enabled", False)
    return d


def _save_settings(d):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def _binary():
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = "amd64" if machine in ("x86_64", "amd64") else ("arm64" if machine in ("aarch64", "arm64") else machine)
    if system == "windows":
        p = os.path.join(PLUGIN_DIR, "bin", "windows-%s" % arch, "accountpool-gateway.exe")
    else:
        p = os.path.join(PLUGIN_DIR, "bin", "linux-%s" % arch, "accountpool-gateway")
    return p


def _admin_token():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            t = f.read().strip()
            if t:
                return t
    import secrets
    token = "adm_" + secrets.token_hex(24)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)
    try:
        os.chmod(TOKEN_FILE, 0o600)
    except Exception:
        pass
    return token


def _health(timeout=1.0):
    token = _admin_token()
    req = urllib.request.Request("http://%s/admin/v1/status" % ADMIN_ADDR,
                                 headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _alive():
    global _proc
    if _proc is not None and _proc.poll() is None:
        return True
    if _health():
        return True
    return False


def _start_locked():
    global _proc
    if _health():
        return
    binary = _binary()
    if not os.path.exists(binary):
        raise rc.RCError(5001, "Gateway 未编译：缺少 %s" % binary)
    os.makedirs(DATA_DIR, exist_ok=True)
    token = _admin_token()
    settings = _settings()
    args = [binary, "-data", DATA_DIR, "-admin-addr", ADMIN_ADDR,
            "-lan-addr", settings.get("lan_addr", DEFAULT_LAN_ADDR),
            "-admin-token", token]
    log = open(LOG_FILE, "ab", buffering=0)
    _proc = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT,
                             cwd=PLUGIN_DIR, env=dict(os.environ, ACCOUNT_POOL_ADMIN_TOKEN=token))
    for _ in range(50):
        if _health(0.5):
            return
        if _proc.poll() is not None:
            raise rc.RCError(5002, "Gateway 启动失败，查看 data/gateway.log")
        time.sleep(0.1)
    raise rc.RCError(5003, "Gateway 启动超时")


def ensure_gateway():
    with _lock:
        _start_locked()


def _admin(method, path, body=None, timeout=10):
    ensure_gateway()
    token = _admin_token()
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request("http://%s%s" % (ADMIN_ADDR, path), data=data, method=method,
                                 headers={"Authorization": "Bearer " + token,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(raw).get("error") or raw
        except Exception:
            msg = raw
        raise rc.RCError(e.code, str(msg)[:300])
    except Exception as e:
        raise rc.RCError(502, str(e)[:300])


@rc.interface("accountpool.status")
def status(params):
    ensure_gateway()
    d = _admin("GET", "/admin/v1/status")
    d["lan_addr"] = _settings().get("lan_addr", DEFAULT_LAN_ADDR)
    d["lan_enabled"] = _settings().get("lan_enabled", False)
    d["binary"] = _binary()
    return d


@rc.interface("accountpool.request")
def request(params):
    method = str((params or {}).get("method") or "GET").upper()
    path = str((params or {}).get("path") or "")
    if not path.startswith("/admin/v1/"):
        raise rc.RCError(400, "非法管理路径")
    if method not in ("GET", "POST", "DELETE"):
        raise rc.RCError(400, "非法方法")
    return _admin(method, path, (params or {}).get("body"))


@rc.interface("accountpool.settings.save")
def settings_save(params):
    d = _settings()
    lan = str((params or {}).get("lan_addr") or "").strip()
    enabled = bool((params or {}).get("lan_enabled"))
    if enabled:
        if not lan:
            lan = "0.0.0.0:18900"
        host, _, port = lan.rpartition(":")
        if not host or not port.isdigit():
            raise rc.RCError(400, "LAN 地址格式应为 host:port")
        d["lan_enabled"] = True
        d["lan_addr"] = lan
    else:
        d["lan_enabled"] = False
        d["lan_addr"] = DEFAULT_LAN_ADDR
    _save_settings(d)
    return {"ok": True, "settings": d}


@rc.interface("accountpool.gateway.restart")
def gateway_restart(params):
    global _proc
    with _lock:
        if _proc is not None and _proc.poll() is None:
            try:
                _proc.terminate()
                _proc.wait(timeout=5)
            except Exception:
                _proc.kill()
        _proc = None
        _start_locked()
    return {"ok": True, "status": _health() or {}}


@rc.interface("accountpool.gateway.log")
def gateway_log(params):
    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-200:]
        return {"log": "".join(lines)}
    except Exception:
        return {"log": ""}


def _shutdown():
    global _proc
    if _proc is not None and _proc.poll() is None:
        try:
            _proc.terminate()
        except Exception:
            pass


atexit.register(_shutdown)


if __name__ == "__main__":
    rc.serve(
        endpoint=os.environ.get("RC_ENDPOINT", ""),
        name="AccountPool",
        version=VERSION,
        manifest={"label": "号池管理台", "description": _META["description"]},
        frontend={"pages": [{"path": "", "title": "号池管理台"}]},
        iface_ids=None,
        plugin_dir=PLUGIN_DIR,
    )
