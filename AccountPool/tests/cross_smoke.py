import json, os, subprocess, tempfile, threading, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MOCK = 18920
ADMIN = "http://127.0.0.1:18930"
LAN = "http://127.0.0.1:18931"
TOKEN = "cross-admin"

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        body = json.dumps({"data": [{"id": "mock-1"}], "models": [{"name": "models/gemini-mock"}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0")); req = json.loads(self.rfile.read(n) or b"{}")
        if self.path.startswith("/v1/messages"):
            out = {"id":"msg_mock","type":"message","role":"assistant","model":"claude-mock",
                   "content":[{"type":"text","text":"anthropic-pong"}],"stop_reason":"end_turn",
                   "usage":{"input_tokens":3,"output_tokens":2}}
        elif self.path.startswith("/v1beta/"):
            out = {"candidates":[{"content":{"role":"model","parts":[{"text":"gemini-pong"}]},"finishReason":"STOP"}],
                   "usageMetadata":{"promptTokenCount":3,"candidatesTokenCount":2,"totalTokenCount":5}}
        else:
            out = {"id":"chatcmpl-mock","object":"chat.completion","model":req.get("model","mock-1"),
                   "choices":[{"index":0,"message":{"role":"assistant","content":"openai-pong"},"finish_reason":"stop"}],
                   "usage":{"prompt_tokens":3,"completion_tokens":2,"total_tokens":5}}
        body = json.dumps(out).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

def req(url, method="GET", body=None, token=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token: r.add_header("Authorization", "Bearer " + token)
    for k, v in (headers or {}).items():
        r.add_header(k, v)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

mock = ThreadingHTTPServer(("127.0.0.1", MOCK), H)
threading.Thread(target=mock.serve_forever, daemon=True).start()
data = tempfile.mkdtemp(prefix="accountpool-cross-")
bin_path = os.path.join(os.path.dirname(__file__), "..", "bin", "windows-amd64", "accountpool-gateway.exe")
proc = subprocess.Popen([bin_path, "-data", data, "-admin-addr", "127.0.0.1:18930", "-lan-addr", "127.0.0.1:18931", "-admin-token", TOKEN],
                        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
try:
    for _ in range(50):
        s, d = req(ADMIN + "/admin/v1/status", token=TOKEN)
        if s == 200: break
        time.sleep(0.1)
    def admin(method, path, body=None):
        s, d = req(ADMIN + path, method, body, TOKEN)
        if s >= 400: raise SystemExit((path, s, d))
        return d
    for name, typ, model in [("openai-mock", "openai", "mock-1"), ("anthropic-mock", "anthropic", "claude-mock"), ("gemini-mock", "gemini", "gemini-mock")]:
        p = admin("POST", "/admin/v1/providers", {"name": name, "type": typ, "base_url": "http://127.0.0.1:%d" % MOCK, "api_key": "sk", "models": [model]})["provider"]
        admin("POST", "/admin/v1/accounts", {"provider_id": p["id"], "label": name, "api_key": "sk"})
    token = admin("POST", "/admin/v1/tokens", {"name": "cross"})["token"]

    s, d = req(LAN + "/v1/messages", "POST", {"model": "mock-1", "max_tokens": 32, "messages": [{"role": "user", "content": "ping"}]},
               headers={"x-api-key": token})
    print("anthropic-down/openai-up:", s, d.get("content")[0]["text"] if isinstance(d, dict) and d.get("content") else d)
    s, d = req(LAN + "/v1beta/models/mock-1:generateContent?key=" + token, "POST", {"contents": [{"parts": [{"text": "ping"}]}]})
    print("gemini-down/openai-up:", s, d.get("candidates")[0]["content"]["parts"][0]["text"] if isinstance(d, dict) else d)
    s, d = req(LAN + "/v1/chat/completions", "POST", {"model": "claude-mock", "messages": [{"role": "user", "content": "ping"}]}, token)
    print("openai-down/anthropic-up:", s, d.get("choices")[0]["message"]["content"] if isinstance(d, dict) and d.get("choices") else d)
    s, d = req(LAN + "/v1/chat/completions", "POST", {"model": "gemini-mock", "messages": [{"role": "user", "content": "ping"}]}, token)
    print("openai-down/gemini-up:", s, d.get("choices")[0]["message"]["content"] if isinstance(d, dict) and d.get("choices") else d)
    s, d = req(LAN + "/v1/messages", "POST", {"model": "gemini-mock", "max_tokens": 32, "messages": [{"role": "user", "content": "ping"}]},
               headers={"x-api-key": token})
    print("anthropic-down/gemini-up:", s, d.get("content")[0]["text"] if isinstance(d, dict) and d.get("content") else d)
    s, d = req(LAN + "/v1beta/models/claude-mock:generateContent?key=" + token, "POST", {"contents": [{"parts": [{"text": "ping"}]}]})
    print("gemini-down/anthropic-up:", s, d.get("candidates")[0]["content"]["parts"][0]["text"] if isinstance(d, dict) and d.get("candidates") else d)
finally:
    proc.terminate()
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
    mock.shutdown()
