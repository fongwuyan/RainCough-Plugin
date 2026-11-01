#!/bin/bash
# 生产机 NapCat + QQ 全新安装 —— 第 3 步
#
# 部署布局（与雨咯Bot 插件代码里的硬编码路径一致，不改插件）：
#   /opt/napcat/napcat/   NapCat 代码（NapCat.Shell.zip 解包）
#   /opt/napcat/QQ/       QQ 本体（linuxqq deb 解包）
#   /opt/napcat/instances/<uin>/{home,work,logs}
#   /app/napcat -> /opt/napcat/napcat   ← QQ 内置加载器硬编码 file:///app/napcat/napcat.mjs
#
# 版本：
#   NapCat  v4.18.42（GitHub releases latest）
#   QQ      3.2.34-53644（官方 linuxqq_target_version）
set -u

NAPCAT_VER="v4.18.42"
QQ_VER="3.2.34-53644"
QQ_URL="https://qqdl.gtimg.cn/qqfile/QQNT/9.9.36/beta/9ee04bef/linuxqq_${QQ_VER}_amd64.deb"
NAPCAT_URL="https://github.com/NapNeko/NapCatQQ/releases/download/${NAPCAT_VER}/NapCat.Shell.zip"

BASE=/opt/napcat
TMP=$(mktemp -d)
echo "临时目录: $TMP"

echo
echo "=== 1. 系统依赖 ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq 2>/dev/null || true
apt-get install -y -qq unzip zip wget curl xvfb \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
  libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libasound2 libpango-1.0-0 libcairo2 libatspi2.0-0 \
  libgtk-3-0 fonts-wqy-microhei 2>&1 | tail -3
echo "  依赖安装完成"

echo
echo "=== 2. 下载 NapCat ($NAPCAT_VER) ==="
cd "$TMP"
# ★ 必须 --http1.1：GitHub Release 的 CDN 走 HTTP/2 时会随机
#   "PROTOCOL_ERROR (err 1)" 中断大文件下载（实测 34MB 传到 7MB 就断）。
#   配合 -C - 断点续传 + 多次重试，才能稳定拉完。
fetch() {
  local url="$1" out="$2" tries=6
  for i in $(seq 1 $tries); do
    echo "  尝试 $i/$tries: $out"
    if curl -fL --http1.1 -C - --connect-timeout 20 --max-time 900 \
            --retry 3 --retry-delay 3 -o "$out" "$url"; then
      echo "  下载完成 $(du -h "$out" | cut -f1)"
      return 0
    fi
    echo "  第 $i 次失败，3 秒后重试（断点续传）"
    sleep 3
  done
  return 1
}

echo
echo "=== 2. 下载 NapCat ($NAPCAT_VER) ==="
fetch "$NAPCAT_URL" NapCat.Shell.zip || {
  echo "  官方源下载失败，尝试用备份里的同名官方包兜底"
  BKZIP=$(ls -1 /opt/_uninstall-backup-*/napcat.tar.gz 2>/dev/null | head -1)
  if [ -n "$BKZIP" ]; then
    tar -xzf "$BKZIP" -C "$TMP" napcat/NapCat.Shell.zip 2>/dev/null \
      && cp "$TMP/napcat/NapCat.Shell.zip" "$TMP/NapCat.Shell.zip" \
      && echo "  已从备份取出 NapCat.Shell.zip" \
      || { echo "  !! 备份兜底也失败"; exit 1; }
  else
    echo "  !! NapCat 下载失败且无备份兜底"; exit 1
  fi
}

echo
echo "=== 3. 下载 QQ ($QQ_VER) ==="
fetch "$QQ_URL" QQ.deb || { echo "  !! QQ 下载失败"; exit 1; }

echo
echo "=== 4. 解包部署 ==="
mkdir -p "$BASE"
# NapCat
rm -rf "$BASE/napcat"
mkdir -p "$BASE/napcat"
unzip -q -o NapCat.Shell.zip -d "$BASE/napcat" && echo "  NapCat 解包 OK"
# QQ（dpkg -x 只解包不安装到系统，避免污染 dpkg 依赖链）
rm -rf "$BASE/QQ"
dpkg -x QQ.deb "$TMP/qqstage" && echo "  QQ 解包 OK"
mv "$TMP/qqstage/opt/QQ" "$BASE/QQ" && echo "  QQ 放到 $BASE/QQ"
# 版本校验
QV=$(python3 -c "import json;print(json.load(open('$BASE/QQ/resources/app/package.json'))['version'])" 2>/dev/null || echo '?')
echo "  QQ 实装版本: $QV"
[ "$QV" = "$QQ_VER" ] && echo "  版本匹配 ✓" || echo "  !! 版本与预期不符（预期 $QQ_VER）"
NV=$(python3 -c "import json;print(json.load(open('$BASE/napcat/package.json'))['version'])" 2>/dev/null || echo '?')
echo "  NapCat 版本: $NV"
[ -f "$BASE/napcat/napcat.mjs" ] && echo "  napcat.mjs 存在 ✓" || { echo "  !! 缺 napcat.mjs"; exit 1; }

echo
echo "=== 5. /app/napcat 软链（QQ 加载 NapCat 的硬编码路径）==="
mkdir -p /app
rm -rf /app/napcat
ln -s "$BASE/napcat" /app/napcat
ls -la /app/napcat

echo
echo "=== 6. 补上 QQ 内置 NapCat 加载器 ==="
# QQ 官方 deb 里的 resources/app/loadNapCat.js 是硬编码 /app/napcat/napcat.mjs 的版本；
# 如果解出来的包没有这个文件，就自己写一份（内容与官方一致）。
LOAD="$BASE/QQ/resources/app/loadNapCat.js"
if [ ! -f "$LOAD" ]; then
  printf "(async () => {await import('file:///app/napcat/napcat.mjs');})();\n" > "$LOAD"
  echo "  已写入 $LOAD"
else
  echo "  已存在: $(cat "$LOAD")"
fi

echo
echo "=== 7. 目录与权限 ==="
mkdir -p "$BASE/instances" "$BASE/home"
chmod 755 "$BASE/QQ/qq"
chmod 4755 "$BASE/QQ/chrome-sandbox" 2>/dev/null || true
ls -la "$BASE/"

echo
echo "=== 8. 清理临时文件 ==="
cd /
rm -rf "$TMP"
echo "  已清理 $TMP"

echo
echo "=== 安装完成 ==="
du -sh "$BASE" "$BASE/QQ" "$BASE/napcat"
echo "INSTALL_DONE"
