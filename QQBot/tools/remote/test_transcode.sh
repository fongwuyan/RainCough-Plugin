#!/usr/bin/env bash
# 验证转码的原子性：
#  1. 造一个真正的 AMR 文件（内容是 #!AMR 头），后缀故意用 .mp3
#     —— 这正是生产机历史数据的形态
#  2. 调用 convert_atomic 转 mp3，验证：成功、结果是真 mp3、原件不丢
#  3. 造一个无法转换的垃圾文件，验证：失败时**原件还在**（这是曾经的 bug）
set -u
cd /opt/rcbot
PY=/opt/rcbot/venv/bin/python
T=/tmp/transcode_test
rm -rf "$T"; mkdir -p "$T"

echo "=== 1. 造 AMR 文件（后缀伪装成 .mp3）==="
# ffmpeg 只有 amrnb 解码器没有编码器，所以手工造 AMR-NB 帧
python3 - "$T" <<'MKEOF'
import sys, os
T = sys.argv[1]
# AMR-NB：文件头 "#!AMR\n"，之后每帧 32 字节（首字节=帧类型）
data = b'#!AMR\n'
for _ in range(40):          # 40 帧 ≈ 2 秒
    data += b'\x00' + b'\x00' * 31
with open(os.path.join(T, 'fake.mp3'), 'wb') as f:
    f.write(data)
print('已生成', len(data), '字节')
MKEOF
ls -la "$T/fake.mp3" 2>&1
head -c 8 "$T/fake.mp3" | od -An -c | head -1
echo "-- ffmpeg 能否识别 --"
ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "$T/fake.mp3" 2>&1 | head -1

echo
echo "=== 2. 原子转码（成功路径）==="
$PY - "$T" <<'PYEOF'
import asyncio, os, sys
sys.path.insert(0, '/opt/rcbot')
from rcbot import ffmpeg

T = sys.argv[1]
src = os.path.join(T, 'fake.mp3')

async def main():
    before = os.path.getsize(src)
    out, mime = await ffmpeg.convert_atomic(src, 'audio', timeout=120)
    print('转换结果:', out, mime)
    print('原文件仍在:', os.path.exists(src), '大小', os.path.getsize(src) if os.path.exists(src) else '-')
    if out:
        with open(out, 'rb') as f:
            head = f.read(4)
        print('产物是 mp3:', head[:3] == b'ID3' or head[:2] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'),
              '大小', os.path.getsize(out))
    # 失败路径：垃圾内容
    bad = os.path.join(T, 'garbage.mp3')
    with open(bad, 'wb') as f:
        f.write(b'not a real audio at all' * 10)
    out2, mime2 = await ffmpeg.convert_atomic(bad, 'audio', timeout=60)
    print('垃圾文件转换:', out2, mime2)
    print('★ 失败后原件还在:', os.path.exists(bad), '大小',
          os.path.getsize(bad) if os.path.exists(bad) else '-')

asyncio.run(main())
PYEOF

echo
echo "=== 3. 用 ffprobe 验证产物 ==="
for f in "$T"/*.mp3; do
  echo -n "$(basename $f): "
  ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "$f" 2>&1 | head -1
done

rm -rf "$T"
echo "=== 测试结束 ==="
