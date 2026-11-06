# -*- coding: utf-8 -*-
"""SnowLuma 后端：用 Docker 容器跑 QQ（替代 NapCat 的原生安装）。

SnowLuma 与 NapCat 的形态差异（决定了这里的实现方式）：

| 维度 | NapCat（原生） | SnowLuma（Docker） |
|---|---|---|
| QQ 进程 | 宿主机上的 /opt/napcat/QQ/qq + Xvfb | **容器内**（镜像自带 QQ + Xvfb + VNC） |
| 控制 | systemctl start/stop/restart | docker start/stop/restart |
| 日志 | journalctl -u napcat.service | docker logs |
| 扫码 | WebUI API 给二维码 URL，面板里画出来 | **只能通过 noVNC 远程桌面**扫（没有二维码 API） |
| 账号信息 | /api/QQLogin/CheckLoginStatus + GetQQLoginInfo | OneBot `get_login_info`（HTTP 3000） |
| OneBot | WebSocket 6700 | WebSocket 3001（HTTP 3000） |

所以这里做三件事：
  1. 容器的生命周期（起/停/重启/日志）
  2. 从容器日志里取 noVNC 的远程桌面密码，拼出可直接扫码的 URL
  3. 用 OneBot 的 get_login_info 判断登录态与账号信息

★ SnowLuma 的 OneBot 实例是"QQ 登录后才起来"的（hook 注入成功才拉 OneBotInstance），
  所以 **3000 端口能正常回 get_login_info = 已登录**，不用再猜状态机。
"""
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

CONTAINER = "snowluma"
IMAGE = "motricseven7/snowluma:latest"

# 端口（与 compose 模板一致）
WEBUI_PORT = 5099
NOVNC_PORT = 6081
ONEBOT_HTTP_PORT = 3000
ONEBOT_WS_PORT = 3001

# OneBot 的固定令牌 —— 部署时写进 onebot.json，rcbot 用它连 WS
ONEBOT_TOKEN = "rcsnow"

VOLUMES = {
    "qq-gateway-data": "/app/data",
    "qq-client-config": "/app/.config",
    "qq-client-data": "/app/.local/share",
}

# VNC 密码在容器日志里打印（首次启动时随机生成）
_VNC_RE = re.compile(r"(?:远程桌面密码|remote desktop password)[:：]\s*(\S+)")


def sh(cmd, timeout=60):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
        return p.returncode, ((p.stdout or b"") + (p.stderr or b"")).decode("utf-8", "replace")
    except Exception as e:
        return 1, str(e)


def docker_ok():
    rc, o = sh("docker version --format '{{.Server.Version}}' 2>/dev/null", timeout=20)
    return rc == 0 and (o or "").strip() != ""


def exists():
    rc, o = sh("docker inspect -f '{{.State.Status}}' %s 2>/dev/null" % CONTAINER, timeout=20)
    return rc == 0 and (o or "").strip() in ("running", "exited", "created", "paused", "restarting")


def state():
    """容器状态：running / exited / absent / unknown。"""
    rc, o = sh("docker inspect -f '{{.State.Status}}' %s 2>/dev/null" % CONTAINER, timeout=20)
    if rc != 0:
        return "absent"
    return (o or "").strip() or "unknown"


def image_present():
    rc, o = sh("docker images -q %s 2>/dev/null" % IMAGE, timeout=20)
    return rc == 0 and bool((o or "").strip())


def _volume_args():
    args = []
    for vol in VOLUMES:
        args.append("-v %s" % vol)
    return " ".join(args)


def create():
    """起容器（不存在则创建）。

    ★ 两个安全参数不能少：
        --cap-add=SYS_PTRACE      native addon 靠 ptrace 注入 QQ 进程
        --security-opt seccomp=unconfined  默认 seccomp 会拦截注入
      --shm-size=1g：QQ 基于 Chromium，共享内存太小会崩
    """
    if not docker_ok():
        return False, "Docker 不可用（docker version 失败）"
    if not image_present():
        return False, "镜像不存在：%s（先 docker pull）" % IMAGE

    if exists():
        if state() != "running":
            rc, o = sh("docker start %s" % CONTAINER, timeout=120)
            if rc == 0:
                _boot_fix()
            return rc == 0, o
        _boot_fix()
        return True, "already running"

    cmd = (
        "docker run -d --name %s --restart unless-stopped "
        "--shm-size=1g --ulimit nofile=65536:1048576 "
        "--cap-add=SYS_PTRACE --security-opt seccomp=unconfined "
        "-e SNOWLUMA_WEBUI_HOST=0.0.0.0 "
        "-e SNOWLUMA_WEBUI_PORT=%d "
        '-e SNOWLUMA_QQ_FLAGS="--disable-gpu --disable-software-rasterizer --disable-gpu-compositing" '
        "-p %d:%d -p %d:%d -p %d:%d -p %d:%d "
        "%s %s"
        % (CONTAINER,
           WEBUI_PORT,
           NOVNC_PORT, NOVNC_PORT,
           WEBUI_PORT, WEBUI_PORT,
           ONEBOT_HTTP_PORT, ONEBOT_HTTP_PORT,
           ONEBOT_WS_PORT, ONEBOT_WS_PORT,
           _volume_args(), IMAGE)
    )
    rc, o = sh(cmd, timeout=300)
    if rc == 0:
        _boot_fix()
    return rc == 0, o


# 令牌是否已经固化过（进程级缓存，避免每次调接口都 docker exec）
_TOKEN_FIXED = {"done": False}


def _boot_fix():
    """容器起来后做一次初始化：把 OneBot 的 accessToken 固定成 rcsnow。

    SnowLuma 首次启动会生成**随机** token 写进配置，rcbot 侧没法预先知道。
    改完必须重启容器才生效 —— 所以这一步只在真的改了的时候重启。
    """
    if _TOKEN_FIXED["done"]:
        return
    # 等容器里的 node 与配置文件就绪
    for _ in range(15):
        rc, o = sh("docker exec %s test -f /app/data/config/onebot.json" % CONTAINER,
                   timeout=15)
        if rc == 0:
            break
        time.sleep(2)
    ok, out = ensure_onebot_config()
    if ok and "TOKEN_SET" in (out or ""):
        sh("docker restart %s" % CONTAINER, timeout=180)
        time.sleep(8)
        _TOKEN_FIXED["done"] = True
        return
    # 已经是目标值 / 暂时改不了：标记完成，避免每次都重启
    if ok:
        _TOKEN_FIXED["done"] = True


def stop():
    if not exists():
        return True, "absent"
    rc, o = sh("docker stop %s" % CONTAINER, timeout=120)
    return rc == 0, o


def restart():
    if not exists():
        return create()
    rc, o = sh("docker restart %s" % CONTAINER, timeout=180)
    return rc == 0, o


def remove():
    """删容器（保留数据卷 —— 登录态在里面，删了要重新扫码）。"""
    if not exists():
        return True, "absent"
    sh("docker stop %s 2>/dev/null" % CONTAINER, timeout=120)
    rc, o = sh("docker rm %s" % CONTAINER, timeout=60)
    return rc == 0, o


def logs(lines=400):
    """容器日志（去掉 Qt/GLib 的噪音行）。"""
    n = max(50, min(5000, int(lines or 400)))
    rc, o = sh("docker logs --tail %d %s 2>&1" % (n, CONTAINER), timeout=60)
    if rc != 0:
        return ""
    keep = []
    for ln in (o or "").splitlines():
        if re.search(r"QtNetwork|GLib|libQt6|Fontconfig|dbus", ln):
            continue
        keep.append(ln)
    return "\n".join(keep)


def vnc_password():
    """从容器日志里取远程桌面密码。

    ★ 不设 VNC_PASSWD 时，官方镜像首次启动会**随机生成**并只在日志打印一次；
      容器重建只要数据卷还在，密码就不变（存在卷里）。
    """
    _, o = sh("docker logs %s 2>&1 | grep -Ei '远程桌面密码|remote desktop password' "
              "| tail -n 1" % CONTAINER, timeout=60)
    m = _VNC_RE.search(o or "")
    return m.group(1).strip() if m else ""


def novnc_url(host=""):
    """可直接扫码的 noVNC 地址（带密码，打开就自动连）。

    autoconnect=1 + password 省掉用户手动输密码那一步。
    """
    pw = vnc_password()
    q = "autoconnect=1&resize=scale"
    if pw:
        q += "&password=" + urllib.request.quote(pw)
    return "http://%s:%d/vnc.html?%s" % (host or "127.0.0.1", NOVNC_PORT, q)


# ---------------------------------------------------------------- OneBot

def _onebot(path, body=None, timeout=8):
    """调 OneBot HTTP API（3000）。返回 data；失败返回 None。"""
    url = "http://127.0.0.1:%d%s" % (ONEBOT_HTTP_PORT, path)
    data = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + ONEBOT_TOKEN},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        if d.get("retcode") not in (0, None):
            return None
        return d.get("data")
    except Exception:
        return None


def login_info():
    """当前登录的账号信息；没登录返回 {}。

    ★ SnowLuma 的 OneBot 实例要等 QQ 登录后才起来 ——
      所以这个接口能返回数据就说明已经登录了。
    """
    d = _onebot("/get_login_info")
    if not isinstance(d, dict):
        return {}
    uin = d.get("user_id") or d.get("uin")
    if not uin:
        return {}
    return {"uin": str(uin), "nick": d.get("nickname") or d.get("nick") or ""}


def onebot_alive():
    """OneBot HTTP 是否可用（= 已登录且 hook 成功）。"""
    return bool(login_info())


def ensure_onebot_config():
    """把 OneBot 的 accessToken 固定成 ONEBOT_TOKEN。

    ★ 不用 sed —— JSON 里带引号，经 shell → docker exec → sh 三层转义后
      正则几乎必然被吃掉（实测 grep 得到 0）。改成把 python 脚本 base64 传进去，
      容器里解码后执行，绕开所有转义问题。
    """
    if not exists():
        return False, "容器不存在"

    # 先看当前值
    rc, cur = sh("docker exec %s cat /app/data/config/onebot.json 2>/dev/null" % CONTAINER,
                 timeout=30)
    if rc != 0 or not (cur or "").strip():
        return False, "读不到配置"
    if (cur or "").count(ONEBOT_TOKEN) >= 2:
        return True, "TOKEN_ALREADY"

    script = (
        "import json,sys\n"
        "p='/app/data/config/onebot.json'\n"
        "d=json.load(open(p,encoding='utf-8'))\n"
        "n=0\n"
        "for k in ('httpServers','wsServers'):\n"
        "    for x in (d.get('networks') or {}).get(k) or []:\n"
        "        if x.get('accessToken')!='%s':\n"
        "            x['accessToken']='%s';n+=1\n"
        "json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)\n"
        "print('CHANGED' if n else 'NOCHANGE')\n"
    ) % (ONEBOT_TOKEN, ONEBOT_TOKEN)
    import base64
    b64 = base64.b64encode(script.encode("utf-8")).decode("ascii")
    # 容器里用 python3（镜像是 debian，带 python3）；没有就退回 node
    cmd = ("docker exec %s sh -c \"echo %s | base64 -d | python3 -\"" % (CONTAINER, b64))
    rc, o = sh(cmd, timeout=60)
    if "CHANGED" in (o or ""):
        return True, "TOKEN_SET"
    if "NOCHANGE" in (o or ""):
        return True, "TOKEN_ALREADY"
    return False, (o or "")[:200]


def _sq(s):
    """给 shell 用的单引号包裹（内部单引号转义）。"""
    return "'" + s.replace("'", "'\\''") + "'"


def wait_onebot(tries=30):
    """等 OneBot 起来（登录后才有）。"""
    for _ in range(tries):
        if onebot_alive():
            return True
        time.sleep(2)
    return False
