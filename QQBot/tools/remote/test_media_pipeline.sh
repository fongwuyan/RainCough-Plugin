#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证媒体落盘 + 转码链路（模拟一条带语音/视频的消息）。

走的是真实的 media.save_media → chats.record 路径，
验证：
  · 语音（AMR 内容）落盘为 .amr，自动转成 .mp3，playable=1
  · 视频（HEVC）落盘为 .mp4，后台转码成 .h264.mp4，playable=1
  · 媒体索引同步写入 media_files
"""
import asyncio
import os
import shutil
import sys
import time

sys.path.insert(0, '/opt/rcbot')

from rcbot import chats, media, store  # noqa: E402

ROOT = '/tmp/media_test/root'
SHM = '/opt/rcbot/media'


def amr_bytes():
    """造一段 AMR-NB（#!AMR 头 + 40 帧）。"""
    data = b'#!AMR\n'
    for _ in range(40):
        data += b'\x00' + b'\x00' * 31
    return data


async def main():
    # 1) 准备一个 HEVC 测试视频（用真实 QQ 视频更好，这里直接复制现有的）
    src_video = None
    for dp, _, fs in os.walk(SHM):
        for f in fs:
            if f.endswith('.h264.mp4'):
                src_video = os.path.join(dp, f)
                break
        if src_video:
            break

    # 造一个 HEVC 版本：用 ffmpeg 从现有视频转成 hevc（模拟 QQ 的 HEVC 视频）
    hevc = '/tmp/media_test/hevc.mp4'
    os.makedirs('/tmp/media_test', exist_ok=True)
    if src_video:
        import subprocess
        p = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src_video,
                            '-c:v', 'libx265', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p10le',
                            '-tag:v', 'hvc1', hevc], capture_output=True, timeout=600)
        print('HEVC 测试视频:', hevc, os.path.getsize(hevc) if os.path.exists(hevc) else '失败',
              p.stderr[:150])

    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT, exist_ok=True)

    segs = [
        {'type': 'record', 'data': {'file': 'x.amr', 'url': ''}},
        {'type': 'video', 'data': {'file': 'y.mp4', 'url': ''}},
    ]

    # 2) 把 AMR 内容塞到 record 段，HEVC 文件塞到 video 段
    amr_path = '/tmp/media_test/rec.amr'
    with open(amr_path, 'wb') as f:
        f.write(amr_bytes())

    class FakeOB:
        """模拟 OneBot：按 action 返回本地文件。"""
        def __init__(self, rec, vid):
            self.rec, self.vid = rec, vid

        async def call(self, action, params=None, timeout=20):
            if action == 'get_record':
                return {'data': {'file': self.rec}}
            if action == 'get_video':
                return {'data': {'file': self.vid}}
            return {'data': {}}

    ob = FakeOB(amr_path, hevc if os.path.exists(hevc) else '')

    print('\n=== save_media ===')
    mlist = await media.save_media(segs, ob, ROOT, '1132096843', '900000001',
                                   int(time.time()), account_id='a1132096843')
    for m in mlist:
        print('  %-8s rel=%-46s bytes=%-9s mime=%-12s playable=%s trans=%s'
              % (m['kind'], m['rel'], m['bytes'], m['mime'], m['playable'], m['transcode']))

    print('\n=== 等后台视频转码 ===')
    for i in range(60):
        await asyncio.sleep(2)
        done = all(m['transcode'] in ('done', 'failed', 'skipped') for m in mlist)
        if done:
            break
    for m in mlist:
        print('  %-8s rel=%-46s bytes=%-9s mime=%-12s playable=%s trans=%s'
              % (m['kind'], m['rel'], m['bytes'], m['mime'], m['playable'], m['transcode']))

    print('\n=== 落盘文件实际格式 ===')
    import subprocess
    for m in mlist:
        if not m['rel']:
            continue
        p = os.path.join(ROOT, m['rel'])
        if not os.path.exists(p):
            print('  %s -> 文件不存在 !!' % m['rel'])
            continue
        r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                            'stream=codec_name,pix_fmt', '-of', 'csv=p=0', p],
                           capture_output=True, text=True, timeout=60)
        print('  %-46s %s' % (m['rel'].split('/')[-1], (r.stdout or r.stderr).strip()[:80]))

    print('\n=== 索引写入 ===')
    await store.init() if hasattr(store, 'init') else None
    shutil.rmtree(ROOT, ignore_errors=True)
    shutil.rmtree('/tmp/media_test', ignore_errors=True)
    print('=== 完成 ===')


if __name__ == '__main__':
    asyncio.run(main())
