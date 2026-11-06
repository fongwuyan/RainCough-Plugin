# -*- coding: utf-8 -*-
"""排查语音：SnowLuma 到底给的是 SILK 还是 AMR，OneBot 能不能转。"""
import json
import os
import subprocess
import urllib.request

TOKEN = "rcsnow"
BASE = "http://127.0.0.1:3000"
FILE = "39bf1ce93063df67e06442cf099c565f.amr"


def call(path, body):
    req = urllib.request.Request(
        BASE + path, json.dumps(body).encode(),
        {"Content-Type": "application/json", "Authorization": "Bearer " + TOKEN},
        method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


for fmt in ("mp3", "amr", "wav", "silk"):
    try:
        d = call("/get_record", {"file": FILE, "out_format": fmt})
        data = d.get("data") or {}
        url = data.get("file") or ""
        print("out_format=%-5s keys=%s url_head=%s" % (fmt, list(data.keys()), url[:50]))
        if url.startswith("http"):
            raw = urllib.request.urlopen(url, timeout=30).read()
            p = "/tmp/rec_%s.bin" % fmt
            open(p, "wb").write(raw)
            print("   magic=%r size=%d" % (raw[:16], len(raw)))
            pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=format_name,duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True)
            print("   ffprobe: rc=%d %s %s" % (pr.returncode,
                                               (pr.stdout or "").strip(),
                                               (pr.stderr or "").strip()[:120]))
    except Exception as e:
        print("out_format=%-5s 失败: %s" % (fmt, str(e)[:120]))

# 本地能不能直接解 silk
p = "/opt/rcbot/media/3975339260/2026-11-06/1013617447_0.amr"
print("\n本地文件 magic:", open(p, "rb").read(16))
for tool in ("silk_v3_decoder", "ffmpeg"):
    r = subprocess.run(["which", tool], capture_output=True, text=True)
    print("%s -> %s" % (tool, (r.stdout or "").strip() or "缺失"))
r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-i", p, "/tmp/x.mp3"],
                   capture_output=True, text=True)
print("ffmpeg 直转 rc=%d\n%s" % (r.returncode, (r.stderr or "")[-300:]))
print("pip 可用:", subprocess.run(["python3", "-m", "pip", "--version"],
                                capture_output=True, text=True).stdout.strip()[:80])
