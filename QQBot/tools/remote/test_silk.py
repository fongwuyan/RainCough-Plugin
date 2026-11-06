# -*- coding: utf-8 -*-
"""验证 pilk 把 QQ 的 SILK_V3 解成 wav，再转 mp3。"""
import os
import subprocess

SRC = "/opt/rcbot/media/3975339260/2026-11-06/1013617447_0.amr"
WAV = "/tmp/rec.wav"
MP3 = "/tmp/rec.mp3"

from pilk import silk_to_wav  # noqa: E402

print("输入 magic:", open(SRC, "rb").read(10))
silk_to_wav(SRC, WAV, rate=24000)
print("wav:", os.path.getsize(WAV))

r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", WAV, "-c:a", "libmp3lame", "-b:a", "64k", MP3],
                   capture_output=True, text=True)
print("ffmpeg rc=%d %s" % (r.returncode, (r.stderr or "")[:200]))
p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration,size", "-show_entries", "stream=sample_rate,channels",
                    "-of", "default=nw=1", MP3], capture_output=True, text=True)
print((p.stdout or "").strip())
