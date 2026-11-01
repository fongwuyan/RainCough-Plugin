#!/bin/bash
# NapCat 注入 Linux QQ（官方 install.sh 的 install_napcat + modify_qq_config 等价实现）
#
# ★ 为什么必须做这一步：
#   Linux QQ 的 Electron 入口是 resources/app/package.json 里的 "main" 字段。
#   NapCat 官方脚本的做法是把 main 改成 "./loadNapCat.js"，
#   并把 NapCat 整个包拷到 resources/app/app_launcher/napcat/，
#   让 loadNapCat.js 去 import app_launcher/napcat/napcat.mjs。
#   不做这步 → QQ 正常启动但 NapCat 根本没被加载 → WebUI 端口永远不监听。
#
#   ★ 注意：之前那份 66 字节的 loadNapCat.js（import 'file:///app/napcat/napcat.mjs'）
#     是 Docker 镜像的约定路径，对原生安装是错的 —— 这里按官方脚本改成相对路径。
set -u

BASE=/opt/napcat
QQ_APP="$BASE/QQ/resources/app"
NAPCAT_SRC="$BASE/napcat"
TARGET="$QQ_APP/app_launcher/napcat"

echo "=== 1. 拷 NapCat 到 app_launcher/napcat ==="
mkdir -p "$TARGET"
# config / plugins 保留已有内容（不覆盖），其余整体覆盖
for item in "$NAPCAT_SRC"/*; do
  b=$(basename "$item")
  case "$b" in
    config|plugins)
      mkdir -p "$TARGET/$b"
      cp -rn "$item/." "$TARGET/$b/" 2>/dev/null
      ;;
    *)
      cp -rf "$item" "$TARGET/"
      ;;
  esac
done
echo "  目标: $TARGET"
ls "$TARGET" | head -20
[ -f "$TARGET/napcat.mjs" ] && echo "  napcat.mjs 已就位 ✓" || { echo "  !! 缺 napcat.mjs"; exit 1; }

echo
echo "=== 2. 写 loadNapCat.js（官方内容，相对路径） ==="
cat > "$QQ_APP/loadNapCat.js" <<'EOF'
const path = require('node:path');
const { pathToFileURL } = require('node:url');
import(pathToFileURL(path.join(__dirname, 'app_launcher/napcat/napcat.mjs')).href);
EOF
cat "$QQ_APP/loadNapCat.js"

echo
echo "=== 3. 改 QQ package.json 的 main 字段 ==="
python3 - "$QQ_APP/package.json" <<'PY'
import json, sys, shutil
p = sys.argv[1]
shutil.copy2(p, p + '.bak')
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
old = d.get('main')
d['main'] = './loadNapCat.js'
with open(p, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('  main: %r -> %r' % (old, d['main']))
PY
python3 -c "import json;print('  校验 main =', json.load(open('$QQ_APP/package.json'))['main'])"

echo
echo "=== 4. 重启实例 ==="
systemctl restart napcat@1132096843 2>/dev/null || true
sleep 15
echo "  napcat@1132096843: $(systemctl is-active napcat@1132096843 2>&1)"
echo "  端口:"
ss -ltn 2>/dev/null | grep -E ':6099|:6700' || echo "    (尚未监听)"

echo
echo "=== 5. 日志（去掉哈希噪声） ==="
journalctl -u napcat@1132096843 --since '-40s' --no-pager 2>/dev/null \
  | grep -v -E '[0-9a-f]{64}$' | tail -30

echo "INJECT_DONE"
echo "EXIT_CODE=0"
