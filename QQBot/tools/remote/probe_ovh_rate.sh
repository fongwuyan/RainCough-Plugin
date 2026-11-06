#!/bin/sh
# 第四轮：OVH 免费推理端点限流测试 + 中文模型对比。
set +e
U=https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions

ask() {
  M="$1"
  curl -s --max-time 40 -X POST "$U" -H 'Content-Type: application/json' \
    -d "{\"model\":\"$M\",\"messages\":[{\"role\":\"user\",\"content\":\"只回复两个字：可用\"}],\"max_tokens\":48}" \
    | python3 -c "import sys,json;
d=sys.stdin.read()
try:
    j=json.loads(d)
    if 'error' in j: print('ERR:', str(j['error'])[:120])
    else:
        ch=(j.get('choices') or [{}])[0].get('message') or {}
        print('OK content=', repr((ch.get('content') or '')[:40]))
except Exception as e:
    print('RAW:', d[:160])"
}

echo "### 连发 6 次 gpt-oss-20b（间隔 2s，看限流）"
for i in 1 2 3 4 5 6; do
  printf "  #%d " "$i"
  ask gpt-oss-20b
  sleep 2
done

echo
echo "### 换中文/通用模型各测一次"
for M in Qwen3.8-27B Qwen3.5-9B Meta-Llama-3_3-70B-Instruct Mistral-Small-3.2-24B-Instruct-2506 gpt-oss-120b; do
  printf "  %-40s " "$M"
  ask "$M"
  sleep 1
done

echo
echo "### 真实中文对话（星野人设，测中文质量）"
curl -s --max-time 60 -X POST "$U" -H 'Content-Type: application/json' \
  -d '{"model":"Qwen3.8-27B","messages":[{"role":"system","content":"你是星野，阿拜多斯高中的懒散学生会长，说话像大叔，懒洋洋，口头禅「唔嘿~」。只用中文，1~3句。"},{"role":"user","content":"在吗"}],"max_tokens":200}' \
  | head -c 600
echo
echo "### done"
