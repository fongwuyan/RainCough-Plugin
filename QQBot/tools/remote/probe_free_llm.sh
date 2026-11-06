#!/bin/sh
# 探测生产机到各家「免费/低价 LLM」的连通性与可用性。
# 只读探测，不改任何配置。
set +e

echo "### 0. 基础网络"
curl -s -o /dev/null -w "baidu  %{http_code} %{time_total}s\n" --max-time 8 https://www.baidu.com
echo "proxy env: [${HTTP_PROXY}][${http_proxy}][${HTTPS_PROXY}]"

probe() {
  # $1=名字 $2=host
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 "https://$2" 2>/dev/null)
  echo "net  $1  $2 -> ${code:-FAIL}"
}

echo
echo "### 1. 候选域名连通性"
probe "dashscope(阿里百炼)"   dashscope.aliyuncs.com
probe "siliconflow(硅基)"    api.siliconflow.cn
probe "bigmodel(智谱)"       open.bigmodel.cn
probe "moonshot(Kimi)"       api.moonshot.cn
probe "deepseek"             api.deepseek.com
probe "qianfan(百度千帆)"    qianfan.baidubce.com
probe "xunfei(讯飞)"         spark-api-open.xf-yun.com
probe "pollinations(免key)"  text.pollinations.ai
probe "groq(免费额度)"       api.groq.com
probe "openrouter(免费)"     openrouter.ai
probe "gemini(免费额度)"     generativelanguage.googleapis.com
probe "hunyuan(腾讯混元)"     api.hunyuan.cloud.tencent.com
probe "volcengine(火山)"      ark.cn-beijing.volces.com

echo
echo "### 2. 免 key 的 OpenAI 兼容端点实测（pollinations）"
curl -s --max-time 25 -X POST https://text.pollinations.ai/openai/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"openai","messages":[{"role":"user","content":"只回复两个字：可用"}],"max_tokens":50}' \
  | head -c 600
echo

echo
echo "### 3. 免 key 的 GET 形式（pollinations 兜底）"
curl -s --max-time 25 "https://text.pollinations.ai/%E5%8F%AA%E5%9B%9E%E5%A4%8D%E4%B8%A4%E4%B8%AA%E5%AD%97%EF%BC%9A%E5%8F%AF%E7%94%A8" | head -c 300
echo

echo
echo "### 4. 智谱 GLM-4-Flash（免费模型，401 = 域名通、只是没 key）"
curl -s --max-time 20 -o /dev/null -w "models -> %{http_code}\n" \
  https://open.bigmodel.cn/api/paas/v4/models -H 'Authorization: Bearer none'

echo "### 5. 硅基流动（401 = 通）"
curl -s --max-time 20 -o /dev/null -w "models -> %{http_code}\n" \
  https://api.siliconflow.cn/v1/models -H 'Authorization: Bearer none'

echo "### 6. 百炼 compatible-mode（401 = 通）"
curl -s --max-time 20 -o /dev/null -w "models -> %{http_code}\n" \
  https://dashscope.aliyuncs.com/compatible-mode/v1/models -H 'Authorization: Bearer none'

echo "### done"
