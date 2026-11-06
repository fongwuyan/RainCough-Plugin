#!/bin/bash
# 构建插件前端并回填产物。
#
# ★ 为什么要这个脚本：构建工具只认 RainCough-Core/plugins/<名>/frontend/，
#   而源码在 RainCough-Plugin/<名>/frontend/。两边是**拷贝关系**，不会自动同步。
#   以前忘了同步，就会出现"前端改完、构建成功、面板还是老样子"的假象
#   （产物 mtime 变新但内容没变）。
#
# 用法：bash tools/build_frontend.sh [插件名]   # 默认 QQBot
set -e
PLUGIN="${1:-QQBot}"
SRC="$(cd "$(dirname "$0")/.." && pwd)"                 # RainCough-Plugin/QQBot
CORE="$(cd "$SRC/../../RainCough-Core" && pwd)"          # RainCough-Core
DST="$CORE/plugins/$PLUGIN"

echo "== 同步前端源码: $SRC/frontend → $DST/frontend"
mkdir -p "$DST/frontend" "$DST/assets"
cp -f "$SRC/frontend/"*.js "$SRC/frontend/"*.mjs "$DST/frontend/" 2>/dev/null || true

echo "== 构建"
node "$CORE/tools/build-plugin-frontend.js" "$PLUGIN"

echo "== 回填产物"
cp -f "$DST/assets/plugin.js" "$SRC/assets/plugin.js"
ls -la "$SRC/assets/plugin.js"
md5sum "$DST/assets/plugin.js" "$SRC/assets/plugin.js"
