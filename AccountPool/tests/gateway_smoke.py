import json, os, subprocess, tempfile, threading, time, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MOCK_PORT = 18912
ADMIN = "http://127.0.0.1:18911"
LAN = "http://127.0.0.1:18910"
TOKEN = "test-admin"

class Mock(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.endswith("/models"):
            body = json.dumps({"data": [{"id": "mock-1"}]}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0")); raw = self.rfile.read(n)
        req = json.loads(raw or b"{}")
        body = json.dumps({"id": "chatcmpl-mock", "object": "chat.completion",
                           "model": req.get("model", "mock-1"),
                           "choices": [{"index": 0, "message": {"role": "assistant", "content": "pong"}, "finish_reason": "stop"}],
                           "usage": {"prompt_tokens": 3, "completion_tokens": 1, "total_tokens": 4}}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

def req(url, method="GET", body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token: r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

mock = ThreadingHTTPServer(("127.0.0.1", MOCK_PORT), Mock)
threading.Thread(target=mock.serve_forever, daemon=True).start()

data = tempfile.mkdtemp(prefix="accountpool-test-")
bin_path = os.path.join(os.path.dirname(__file__), "..", "bin", "windows-amd64", "accountpool-gateway.exe")
proc = subprocess.Popen([bin_path, "-data", data, "-admin-addr", "127.0.0.1:18911", "-lan-addr", "127.0.0.1:18910", "-admin-token", TOKEN],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    for _ in range(50):
        s, d = req(ADMIN + "/admin/v1/status", token=TOKEN)
        if s == 200: break
        time.sleep(0.1)
    print("status", s, d)
    s, d = req(ADMIN + "/admin/v1/providers", "POST", {"name": "mock", "type": "openai", "base_url": "http://127.0.0.1:%d/v1" % MOCK_PORT, "api_key": "sk-test", "models": ["mock-1"]}, TOKEN)
    print("provider", s, d)
    pid = d["provider"]["id"]
    s, d = req(ADMIN + "/admin/v1/accounts", "POST", {"provider_id": pid, "label": "mock-account", "api_key": "sk-test"}, TOKEN)
    print("account", s, d)
    s, d = req(ADMIN + "/admin/v1/tokens", "POST", {"name": "lan", "rpm": 0, "daily_quota": 0}, TOKEN)
    print("token", s, d)
    lan_token = d["token"]
    s, d = req(LAN + "/v1/models", token=lan_token)
    print("models", s, d)
    s, d = req(LAN + "/v1/chat/completions", "POST", {"model": "mock-1", "messages": [{"role": "user", "content": "ping"}]}, lan_token)
    print("chat", s, d)
    s, d = req(ADMIN + "/admin/v1/usage", token=TOKEN)
    print("usage", s, len(d.get("usage", [])))
finally:
    proc.terminate()
    try: proc.wait(timeout=5)
    except Exception: proc.kill()
    mock.shutdown()
