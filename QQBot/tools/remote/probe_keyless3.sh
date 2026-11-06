#!/bin/sh
# 第三轮：确认哪些免 key 端点真的能出字。
set +e

echo "### A. GitHub Models 完整响应头（刚才只回了 OK）"
curl -s -i --max-time 25 -X POST https://models.github.ai/inference/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"openai/gpt-4o-mini","messages":[{"role":"user","content":"hi"}],"max_tokens":16}' \
  | head -c 700
echo

echo "### B. OVH 免费推理：只列 chat 类模型"
curl -s --max-time 20 https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/models \
  | tr ',' '\n' | grep '"id"' | head -40
echo

echo "### C. OVH 免费推理：真对话（免 key）"
for M in "Meta-Llama-3.3-70B-Instruct" "Qwen2.5-72B-Instruct" "Qwen3-32B" "gpt-oss-20b" "Mistral-Nemo-Instruct-2407"; do
  echo "--- $M"
  curl -s --max-time 30 -X POST https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$M\",\"messages\":[{\"role\":\"user\",\"content\":\"只回复两个字：可用\"}],\"max_tokens\":48}" \
    | head -c 300
  echo
done

echo "### D. LLM7 真对话（免 key，DeepSeek-V4-Flash-0731）"
curl -s --max-time 30 -X POST https://api.llm7.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"DeepSeek-V4-Flash-0731","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":48}' \
  | head -c 400
echo

echo "### E. NVIDIA integrate 免 key 对话"
curl -s --max-time 30 -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"meta/llama-3.3-70b-instruct","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":48}' \
  | head -c 300
echo
echo "### done"
