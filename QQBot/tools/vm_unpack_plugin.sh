#!/bin/bash
# 机内：从 base64 还原插件文件
set -eu
D=/opt/raincough/plugins/QQBot

echo "=== 解 base64 ==="
base64 -d /tmp/qqbot.b64 > /tmp/qqbot-all.bin
wc -c /tmp/qqbot-all.bin

echo "=== 拆文件 ==="
cd /tmp
rm -rf qqbot-new && mkdir qqbot-new && cd qqbot-new
python3 - << 'PY'
data = open('/tmp/qqbot-all.bin','rb').read()
SEP = b'\n===FILE_SPLIT===\n'
parts = data.split(SEP)
order = ['server_v4.py', 'assets/plugin.js', 'frontend/plugin.js',
         'plugin.json', 'VERSION', 'rcplugin.py']
for name, content in zip(order, parts):
    name = name.strip()
    if not content:
        continue
    import os
    d = os.path.dirname(name)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(name, 'wb') as f:
        f.write(content)
    print('  %-22s %d bytes' % (name, len(content)))
PY

echo "=== 覆盖到插件目录 ==="
cp -f server_v4.py "$D/server_v4.py"
cp -f rcplugin.py "$D/rcplugin.py"
cp -f plugin.json "$D/plugin.json"
cp -f VERSION "$D/VERSION"
mkdir -p "$D/assets" "$D/frontend"
cp -f assets/plugin.js "$D/assets/plugin.js"
cp -f frontend/plugin.js "$D/frontend/plugin.js"
chmod 644 "$D/server_v4.py" "$D/rcplugin.py" "$D/plugin.json" "$D/VERSION"
chmod 644 "$D/assets/plugin.js" "$D/frontend/plugin.js"
rm -rf "$D/__pycache__"

echo "=== 校验 ==="
python3 -c "import ast,sys; ast.parse(open('$D/server_v4.py',encoding='utf-8').read()); print('  server_v4.py 语法 OK')"
python3 -c "import json; d=json.load(open('$D/plugin.json',encoding='utf-8')); print('  plugin.json OK, 接口', len(d['interfaces']))"
ls -la "$D/server_v4.py" "$D/assets/plugin.js"
echo "UNPACK_DONE"
