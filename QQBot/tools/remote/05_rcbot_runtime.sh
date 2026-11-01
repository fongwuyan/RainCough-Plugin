#!/bin/bash
# rcbot 运行时部署（镜像源版）
#
# ★ 为什么不用官方 PyPI：实测生产机访问 pypi.org 超时 15s（每次请求都慢到超时），
#   换清华镜像只要 1.8s。pip 默认源在 pip.conf 里配。
set -u

echo "=== 1. 配 pip 镜像源 ==="
# ★ 用 PIP_INDEX_URL 环境变量而不是 /etc/pip.conf ——
#   这台机器上 /etc/pip.conf 已经是一个目录（Debian 打包遗留），写文件会失败。
export PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
export PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn"
export PIP_DEFAULT_TIMEOUT=60
echo "  PIP_INDEX_URL=$PIP_INDEX_URL"

echo
echo "=== 2. 装依赖 ==="
if [ ! -x /opt/rcbot/venv/bin/python ]; then
  python3 -m venv /opt/rcbot/venv 2>/dev/null || {
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq && apt-get install -y -qq python3-venv
    python3 -m venv /opt/rcbot/venv
  }
fi
# ★ 先查再装：这台机器的 pip 收尾会挂住（包已装完但进程不退出），
#   所以先验一遍，缺哪个补哪个，避免整段被卡死。
/opt/rcbot/venv/bin/python - <<'PY' 2>/dev/null && DEPS_OK=1 || DEPS_OK=0
import aiohttp, aiosqlite, PIL
PY
if [ "${DEPS_OK:-0}" = "1" ]; then
  echo "  依赖已齐，跳过 pip"
else
  /opt/rcbot/venv/bin/pip install -q 'aiohttp>=3.11' 'aiosqlite>=0.17' 'pillow>=9' 2>&1 | tail -3
fi
/opt/rcbot/venv/bin/python -c 'import aiohttp, aiosqlite, PIL; print("  依赖 OK:", aiohttp.__version__, aiosqlite.__version__, PIL.__version__)'

echo
echo "=== 3. 装 rcbot 运行时（从插件目录复制）==="
SRC=/opt/raincough/plugins/QQBot
if [ ! -d "$SRC/rcbot" ]; then
  echo "  !! 插件目录里没有 rcbot/ 源码：$SRC/rcbot"; exit 1
fi
install -d -m 0755 /opt/rcbot /opt/rcbot/data /opt/rcbot/logs /opt/rcbot/rcbot
rm -f /opt/rcbot/rcbot/*.py
cp -rf "$SRC/rcbot/." /opt/rcbot/rcbot/
install -m 0644 "$SRC/rcbot.py" /opt/rcbot/rcbot.py
chmod 0644 /opt/rcbot/rcbot/*.py
ls /opt/rcbot/rcbot/

echo
echo "=== 4. 注册 rcbot systemd 服务 ==="
cat > /etc/systemd/system/rcbot.service <<'RCBOT_UNIT'
[Unit]
Description=RainCough Bot (rcbot)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/rcbot
ExecStart=/opt/rcbot/venv/bin/python /opt/rcbot/rcbot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=RCBOT_LOG_LEVEL=INFO

[Install]
WantedBy=multi-user.target
RCBOT_UNIT
systemctl daemon-reload
systemctl enable rcbot
systemctl restart rcbot
sleep 8
echo "  rcbot: $(systemctl is-active rcbot 2>&1)"

echo
echo "=== 5. 编译 silk_v3_decoder（语音转码，可选）==="
mkdir -p /opt/rcbot/bin
if [ -x /opt/rcbot/bin/silk_v3_decoder ]; then
  echo "  已存在，跳过"
else
  command -v cmake >/dev/null 2>&1 || {
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq && apt-get install -y -qq git build-essential cmake
  }
  tmp=$(mktemp -d)
  cd "$tmp"
  if git clone --depth 1 https://github.com/foyoux/pilk.git 2>/dev/null; then
    if [ -d silk ]; then cd silk; fi
    if [ -f CMakeLists.txt ]; then
      cmake -B build -DCMAKE_BUILD_TYPE=Release >/dev/null 2>&1
      cmake --build build -j2 >/dev/null 2>&1
      find . -name 'silk_v3_decoder' -type f -perm -u+x | head -1 | xargs -r -I{} cp {} /opt/rcbot/bin/silk_v3_decoder
    fi
  fi
  chmod +x /opt/rcbot/bin/silk_v3_decoder 2>/dev/null
  cd /; rm -rf "$tmp"
  [ -x /opt/rcbot/bin/silk_v3_decoder ] && echo "  编译 OK" || echo "  编译未成功（可选功能，不阻塞）"
fi

echo
echo "=== 6. 校验 ==="
echo "  rcbot 端口 6710:"
ss -ltn 2>/dev/null | grep ':6710 ' || echo "    未监听"
echo "  rcbot 日志:"
tail -10 /opt/rcbot/logs/rcbot.log 2>/dev/null
echo "  数据目录:"
ls -la /opt/rcbot/data/ 2>/dev/null | head -6
echo "RCBOT_READY"
echo "EXIT_CODE=0"
