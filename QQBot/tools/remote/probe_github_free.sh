#!/bin/sh
# 探测 GitHub 系 / 聚合路由类免费 LLM 在生产机的连通性。
set +e

p() {
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 "https://$2" 2>/dev/null)
  echo "net  $1  $2 -> ${code:-FAIL}"
}

echo "### GitHub 系"
p "github-models"      models.github.ai
p "github-api"         api.github.com
p "github-raw"         raw.githubusercontent.com
p "ghcr"               ghcr.io
p "hf-router"          router.huggingface.co
p "cerebras"           api.cerebras.ai
p "mistral"            api.mistral.ai
p "cloudflare"         api.cloudflare.com
p "nvidia-nim"         api.nvcf.nvidia.com
p "kilo"               api.kilo.ai
p "llm7"               api.llm7.io
p "ovh-endpoint"       oai.endpoints.kepler.ai.cloud.ovh.net
p "deepseek-web"       chat.deepseek.com
p "deepseek-api"       api.deepseek.com
p "pypi"               pypi.org
p "npm"                registry.npmjs.org
p "modelscope"         api-inference.modelscope.cn
p "opencode-zen"       opencode.ai

echo
echo "### GitHub Models 免 key 请求（应 401 = 域名通）"
curl -s --max-time 20 -o /dev/null -w "catalog -> %{http_code}\n" \
  https://models.github.ai/inference/models

echo "### DeepSeek 网页端（应 200/403 = 通）"
curl -s --max-time 15 -o /dev/null -w "chat.deepseek -> %{http_code}\n" https://chat.deepseek.com/

echo "### OVH 免费推理端点（pollinations 背后那个）"
curl -s --max-time 20 -X POST https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Meta-Llama-3.1-8B-Instruct","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 300
echo

echo "### LLM7（号称免 key）"
curl -s --max-time 20 -X POST https://api.llm7.io/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 300
echo

echo "### Kilo Gateway（免 key 路由）"
curl -s --max-time 20 -X POST https://api.kilo.ai/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":32}' \
  | head -c 300
echo
echo "### done"
