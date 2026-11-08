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
# ★ 递归复制：frontend/ 下已有子目录（im/），只 cp *.js 会漏掉它们，
#   构建时报 "Could not resolve ./im/shell.js"。
cp -rf "$SRC/frontend/." "$DST/frontend/"

echo "== 模板体检"
# ★ esbuild 看不见模板字符串里的 Vue 语法（模板是运行时才编译的），
#   所以模板写错照样能构建成功 —— 面板里却是白屏。构建前先跑一遍编译器。
if [ -f "$SRC/tools/check_templates.js" ]; then
  node "$SRC/tools/check_templates.js" "$SRC"
fi

echo "== 构建"
# ★ 构建工具即使失败也退出 0（只是打印 [fail]），所以必须自己检查输出，
#   否则会出现"构建失败但看起来成功、回填的还是旧产物"的假象。
BUILD_OUT="$(node "$CORE/tools/build-plugin-frontend.js" "$PLUGIN" 2>&1)" || true
echo "$BUILD_OUT"
if echo "$BUILD_OUT" | grep -qE '\[fail\]|ERROR'; then
  echo "!! 构建失败，未回填产物" >&2
  exit 1
fi

echo "== 回填产物"
cp -f "$DST/assets/plugin.js" "$SRC/assets/plugin.js"
ls -la "$SRC/assets/plugin.js"
md5sum "$DST/assets/plugin.js" "$SRC/assets/plugin.js"
