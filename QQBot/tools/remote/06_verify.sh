#!/bin/bash
# 生产机重装后总验收
set -u

echo "=== 1. 服务状态 ==="
for u in raincough rcbot napcat@1132096843 xvfb-rcbot-1; do
  echo "  $u: $(systemctl is-active $u 2>&1)"
done
echo "  面板插件 QQBot: 见下方接口检查"

echo
echo "=== 2. 端口 ==="
ss -ltn 2>/dev/null | grep -E ':3900|:6099|:6700|:6710' || true

echo
echo "=== 3. 安装产物 ==="
echo "  /opt/napcat:      $(du -sh /opt/napcat 2>/dev/null | cut -f1)"
echo "  /opt/rcbot:       $(du -sh /opt/rcbot 2>/dev/null | cut -f1)"
echo "  插件目录:          $(du -sh /opt/raincough/plugins/QQBot 2>/dev/null | cut -f1)"
echo "  QQ 版本:          $(python3 -c "import json;print(json.load(open('/opt/napcat/QQ/resources/app/package.json'))['version'])" 2>/dev/null)"
echo "  NapCat package.json main: $(python3 -c "import json;print(json.load(open('/opt/napcat/QQ/resources/app/package.json')).get('main'))" 2>/dev/null)"
echo "  /app/napcat ->    $(readlink /app/napcat 2>/dev/null)"
echo "  NapCat 注入目录:   $(ls /opt/napcat/QQ/resources/app/app_launcher/napcat/napcat.mjs 2>/dev/null && echo 'napcat.mjs ✓')"
echo "  rcbot 依赖:        $(/opt/rcbot/venv/bin/python -c 'import aiohttp,aiosqlite,PIL;print("aiohttp",aiohttp.__version__,"| aiosqlite",aiosqlite.__version__,"| pillow",PIL.__version__)' 2>/dev/null)"
echo "  silk_v3_decoder:   $([ -x /opt/rcbot/bin/silk_v3_decoder ] && echo '已编译' || echo '未编译(可选)')"

echo
echo "=== 4. 单元文件 ==="
systemctl list-unit-files --no-legend 2>/dev/null | grep -E 'napcat|rcbot|xvfb' | sed 's/^/  /'

echo
echo "=== 5. 旧残留检查（应为空） ==="
echo "  旧 legacy napcat.service: $([ -f /etc/systemd/system/napcat.service ] && echo '!! 还在' || echo '已清')"
echo "  旧 /opt/napcat/home 登录态: $([ -d /opt/napcat/home ] && echo '存在(新装的空目录)' || echo '无')"
echo "  docker 容器 rc-nap-src: $(docker ps -a 2>/dev/null | grep -c rc-nap-src) 个"

echo
echo "=== 6. 备份位置（可回滚） ==="
ls -d /opt/_uninstall-backup-* 2>/dev/null | sed 's/^/  /'
du -sh /opt/_uninstall-backup-* 2>/dev/null | sed 's/^/  /'

echo
echo "=== 7. 磁盘 ==="
df -h / | tail -1

echo "VERIFY_DONE"
echo "EXIT_CODE=0"
