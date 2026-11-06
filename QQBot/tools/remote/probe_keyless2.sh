#!/bin/sh
# 第二轮：看哪些免 key 端点能真的出一句话。
set +e

echo "### 1. GitHub Models：免 key 列模型"
curl -s --max-time 20 https://models.github.ai/inference/models | head -c 600
echo
echo "### 2. GitHub Models：免 key 直接对话（401 = 需要 PAT）"
curl -s --max-time 25 -X POST https://models.github.ai/inference/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 300
echo

echo "### 3. ModelScope（魔搭，国内直连）：免 key 对话"
curl -s --max-time 30 -X POST https://api-inference.modelscope.cn/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 400
echo
echo "### 3b. ModelScope：带任意 token"
curl -s --max-time 30 -X POST https://api-inference.modelscope.cn/v1/chat/completions \
  -H 'Content-Type: application/json' -H 'Authorization: Bearer ms-free' \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 400
echo

echo "### 4. OVH 免费推理：先列模型"
curl -s --max-time 20 https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models | head -c 700
echo

echo "### 5. LLM7：列模型"
curl -s --max-time 20 https://api.llm7.io/v1/models | head -c 700
echo

echo "### 6. Kilo Gateway：OpenAI 兼容路径"
curl -s --max-time 25 -X POST https://api.kilo.ai/api/openai/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 300
echo

echo "### 7. NVIDIA NIM：列模型（401 = 通）"
curl -s --max-time 20 -o /dev/null -w "models -> %{http_code}\n" \
  https://integrate.api.nvidia.com/v1/models
echo "### done"
