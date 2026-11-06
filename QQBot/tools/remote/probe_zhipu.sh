#!/bin/sh
# 验证智谱 API key：列模型 + 各免费模型对话
#
# ★ 密钥不要写进脚本（会进 git）—— 用环境变量传：
#   ZHIPU_KEY='xxx.yyy' sh /root/probe_zhipu.sh
#   或从生产机配置里读：
#   ZHIPU_KEY=$(/opt/rcbot/venv/bin/python -c "import json;print([p['api_key'] for p in json.load(open('/opt/rcbot/data/config.json'))['providers'] if p['id']=='zhipu'][0])") sh /root/probe_zhipu.sh
set +e
KEY="${ZHIPU_KEY:-}"
if [ -z "$KEY" ]; then
  echo "缺少 ZHIPU_KEY 环境变量"
  exit 1
fi
B=https://open.bigmodel.cn/api/paas/v4

echo "### 1. 列出可用模型"
curl -s --max-time 25 "$B/models" -H "Authorization: Bearer $KEY" \
  | python3 -c "import sys,json;
d=sys.stdin.read()
try:
    j=json.loads(d)
    if 'data' in j:
        ids=[m.get('id') for m in j['data']]
        print('共 %d 个模型' % len(ids))
        for i in ids: print('  ', i)
    else:
        print('ERR:', d[:300])
except Exception:
    print('RAW:', d[:300])"

echo
echo "### 2. 逐个模型对话测试（1113=要充值 → 不免费）"
for M in glm-4-flash glm-4-flash-250414 glm-4.5-flash glm-5.3-flash glm-5-turbo glm-4-air; do
  printf "  %-22s " "$M"
  curl -s --max-time 40 -X POST "$B/chat/completions" \
    -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$M\",\"messages\":[{\"role\":\"user\",\"content\":\"只回复两个字：可用\"}],\"max_tokens\":256}" \
    | python3 -c "import sys,json;
d=sys.stdin.read()
try:
    j=json.loads(d)
    if 'error' in j: print('ERR:', str(j['error'])[:110])
    else:
        m=(j.get('choices') or [{}])[0].get('message') or {}
        u=j.get('usage') or {}
        print('OK', repr((m.get('content') or '')[:30]), '| tokens', u.get('total_tokens'))
except Exception:
    print('RAW:', d[:160])"
done
echo "### done"
