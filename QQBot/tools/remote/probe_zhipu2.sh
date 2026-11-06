#!/bin/sh
# 智谱各模型的人设实测（星野）
#
# ★ 密钥从环境变量传，别写进脚本：ZHIPU_KEY='xxx.yyy' sh probe_zhipu2.sh
set +e
KEY="${ZHIPU_KEY:-}"
if [ -z "$KEY" ]; then
  echo "缺少 ZHIPU_KEY 环境变量"
  exit 1
fi
B=https://open.bigmodel.cn/api/paas/v4

for M in "${@:-glm-4-flash glm-4.5-flash}"; do
  echo "--- $M"
  curl -s --max-time 60 -X POST "$B/chat/completions" \
    -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$M\",\"messages\":[{\"role\":\"system\",\"content\":\"你是星野，阿拜多斯高中的懒散学生会长兼对策委员会长，说话像大叔，懒洋洋，口头禅「唔嘿~」。只用中文，1~3句。\"},{\"role\":\"user\",\"content\":\"在吗\"}],\"max_tokens\":512}" \
    | python3 -c "import sys,json;
d=sys.stdin.read()
try:
    j=json.loads(d)
    if 'error' in j: print('ERR', str(j['error'])[:100])
    else:
        m=(j.get('choices') or [{}])[0].get('message') or {}
        u=j.get('usage') or {}
        print('content=', repr((m.get('content') or '')[:200]))
        print('tokens=', u.get('total_tokens'))
except Exception:
    print('RAW:', d[:200])"
done
echo "### done"
