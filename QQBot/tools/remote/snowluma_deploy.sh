#!/usr/bin/env bash
# 部署 SnowLuma 容器（与 NapCat 并存，端口不冲突）
#
# 端口规划：
#   NapCat  : WebUI 6099 / OneBot 6700
#   SnowLuma: WebUI 5099 / noVNC 6081 / OneBot HTTP 3000 / OneBot WS 3001
#
# ★ 两个安全参数不能少（缺了 hook 注入不进去）：
#     --cap-add=SYS_PTRACE            native addon 靠 ptrace 注入 QQ 进程
#     --security-opt seccomp=unconfined  默认 seccomp 会拦截注入
set -u

NAME=snowluma
IMAGE=motricseven7/snowluma:latest

echo "=== 0. 前置检查 ==="
docker version --format 'docker {{.Server.Version}}' 2>/dev/null || { echo "  Docker 不可用"; exit 1; }
docker images -q "$IMAGE" | grep -q . || { echo "  镜像不存在，先 docker pull $IMAGE"; exit 1; }
echo "  镜像: $(docker images "$IMAGE" --format '{{.Size}}')"

echo
echo "=== 1. 清理同名容器（数据卷保留 = 登录态保留）==="
if docker inspect "$NAME" >/dev/null 2>&1; then
  echo "  已存在，先删容器（不动 volume）"
  docker rm -f "$NAME" >/dev/null 2>&1
fi

echo
echo "=== 2. 启动 ==="
docker run -d \
  --name "$NAME" \
  --restart unless-stopped \
  --shm-size=1g \
  --ulimit nofile=65536:1048576 \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -e SNOWLUMA_WEBUI_HOST=0.0.0.0 \
  -e SNOWLUMA_WEBUI_PORT=5099 \
  -e SNOWLUMA_SCREEN=1280x800x24 \
  -e SNOWLUMA_QQ_FLAGS="--disable-gpu --disable-software-rasterizer --disable-gpu-compositing" \
  -p 6081:6081 -p 5099:5099 -p 3000:3000 -p 3001:3001 \
  -v qq-gateway-data -v qq-client-config -v qq-client-data \
  "$IMAGE" >/dev/null

echo "  等待容器起来…"
for i in $(seq 1 30); do
  st=$(docker inspect -f '{{.State.Status}}' "$NAME" 2>/dev/null)
  [ "$st" = "running" ] && break
  sleep 2
done
echo "  状态: $(docker inspect -f '{{.State.Status}}' "$NAME" 2>/dev/null)"

echo
echo "=== 3. 端口 ==="
for p in 6081 5099 3000 3001; do
  echo "  $p: $(ss -ltn 2>/dev/null | grep -c ":$p ") 个监听"
done

echo
echo "=== 4. 远程桌面密码（noVNC 登录用）==="
docker logs "$NAME" 2>&1 | grep -Ei '远程桌面密码|remote desktop password' | tail -1

echo
echo "=== 5. WebUI 临时密码（admin 用）==="
docker logs "$NAME" 2>&1 | grep -Ei '临时密码|initial credentials' | tail -1

echo
echo "=== 6. 固定 OneBot 令牌 ==="
# SnowLuma 首次启动会生成随机 accessToken，rcbot 侧没法预先知道 ——
# 这里改成固定值；同时打开 reportSelfMessage，否则机器人自己发的消息
# 不进事件流，消息页就看不到自己说过的话。
# ★ 容器里不只有 onebot.json：QQ 登录后 SnowLuma 会另存 onebot_<uin>.json 并优先用它。
#   只改 onebot.json 实测完全不生效，必须逐份改。同时关掉框架自带的 #sl
#   （statusCommand），否则和 rcbot 侧的状态指令会一条触发回两条。
docker exec snowluma node -e "
const fs=require('fs');const dir='/app/data/config';
const files=fs.readdirSync(dir).filter(f=>/^onebot.*\.json$/.test(f));
let n=0;
for (const f of files) {
  const p=dir+'/'+f;
  let d; try{d=JSON.parse(fs.readFileSync(p,'utf8'))}catch(e){continue}
  d.networks=d.networks||{};
  let ch=false;
  for (const k of ['httpServers','wsServers']) {
    for (const x of (d.networks[k]||[])) {
      if (x.accessToken!=='rcsnow'){x.accessToken='rcsnow';ch=true;n++}
      if (x.reportSelfMessage!==true){x.reportSelfMessage=true;ch=true;n++}
    }
  }
  if (d.statusCommand && d.statusCommand.enabled!==false){d.statusCommand.enabled=false;ch=true;n++}
  if (ch) fs.writeFileSync(p,JSON.stringify(d,null,2));
}
console.log(n?'CONFIG_SET':'CONFIG_OK');
" 2>&1 | tail -2
echo "  校验: $(docker exec snowluma node -e "
const fs=require('fs');const dir='/app/data/config';
process.stdout.write(fs.readdirSync(dir).filter(f=>/^onebot.*\.json$/.test(f)).map(f=>{
  const d=JSON.parse(fs.readFileSync(dir+'/'+f,'utf8'));
  const w=(d.networks.wsServers||[]).map(x=>x.port+':'+x.accessToken+':self='+x.reportSelfMessage).join(',');
  return f+'['+w+',statusCommand='+((d.statusCommand||{}).enabled)+']';
}).join(' | '));
")"
echo "  重启容器让配置生效…"
docker restart snowluma >/dev/null 2>&1
sleep 6
echo "  状态: $(docker inspect -f '{{.State.Status}}' snowluma 2>/dev/null)"

echo
echo "=== 7. 首次启动日志（尾 15 行）==="
docker logs --tail 15 "$NAME" 2>&1 | grep -v -E 'QtNetwork|GLib|libQt6' | tail -15
echo "=== 完成 ==="
