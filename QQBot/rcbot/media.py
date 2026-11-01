# -*- coding: utf-8 -*-
"""媒体副本：下载、落盘、语音转码。

为什么必须**同步**下载（不能等用户点开才取）：
  · NapCat 给的 url 是 QQ CDN 临时地址，会过期
  · file 是 NapCat 本地缓存路径，会被它自己清掉
  → 消息到达那一刻不下手，事后就永远拿不到了

落盘路径：<media_dir>/<账号uin>/<日期>/<msg_id>_<段序号>.<ext>
  日期用**消息事件时间**而不是落盘时间，否则补录历史消息时目录会很怪。

语音：QQ 语音是 SILK，浏览器放不了。
  实测 ffmpeg 5.1.9 有，但**没有 silk 解码器**，apt 也没有 silk 包
  → 需要外部的 silk_v3_decoder 转成 mp3（转码器路径在 config.media.silk_decoder）。
  转码器不在就退化：保留原始 .silk，UI 显示下载按钮而不是播放器。
"""
import asyncio
import os
import shutil
import subprocess
import time

import aiohttp

from . import logbuf

MAX_BYTES = 200 * 1024 * 1024

# OneBot 媒体段类型 → (落盘扩展名, 是否需要转码)
_MEDIA_TYPES = {
    'image': ('.jpg', False),
    'record': ('.mp3', True),     # SILK → mp3
    'video': ('.mp4', False),
    'face': ('.gif', False),
    'file': ('.bin', False),
}


class Downloader:
    """带并发上限与超时的下载器。"""

    def __init__(self, concurrency=4, timeout=20):
        self.sem = asyncio.Semaphore(max(1, int(concurrency)))
        self.timeout = int(timeout)

    async def fetch(self, url, headers=None):
        """拿 url 的字节。失败返回 None。"""
        if not url or not url.startswith('http'):
            return None
        async with self.sem:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            try:
                async with aiohttp.ClientSession() as sess:
                    async with sess.get(url, timeout=timeout,
                                        headers=headers or {'User-Agent': 'Mozilla/5.0'}) as r:
                        if r.status >= 400:
                            return None
                        chunks, total = [], 0
                        while True:
                            chunk = await r.content.read(65536)
                            if not chunk:
                                break
                            chunks.append(chunk)
                            total += len(chunk)
                            if total > MAX_BYTES:
                                return None
                        return b''.join(chunks)
            except Exception as e:
                logbuf.debug('media', '下载失败 %s：%s' % (url[:80], str(e)[:100]))
                return None


_DOWNLOADER = None


def downloader(concurrency=4, timeout=20):
    global _DOWNLOADER
    if _DOWNLOADER is None:
        _DOWNLOADER = Downloader(concurrency, timeout)
    return _DOWNLOADER


def _date_dir(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts or time.time()))


def _safe_name(s):
    keep = []
    for ch in str(s or ''):
        if ch.isalnum() or ch in '-_.':
            keep.append(ch)
        else:
            keep.append('_')
    return ''.join(keep)[:80] or 'x'


async def save_media(segs, ob, root, account_uin, msg_id, ts, dl=None, silk_bin='', keep_silk=True):
    """把消息里的媒体段下载落盘，返回媒体清单 list[dict]。

    清单项：{kind, seg, rel, bytes, mime, local}
      rel   —— 相对 root 的路径
      local —— 1=文件在本机，0=只留了元数据（下载失败或被跳过）
    """
    out = []
    if not segs or isinstance(segs, str):
        return out
    dl = dl or downloader()
    day = _date_dir(ts)
    base = os.path.join(root, str(account_uin or 'unknown'), day)

    for i, s in enumerate(segs):
        if not isinstance(s, dict):
            continue
        t = s.get('type')
        if t not in _MEDIA_TYPES:
            continue
        d = s.get('data') or {}
        ext, need_conv = _MEDIA_TYPES[t]
        url = d.get('url') or ''
        path = d.get('file') or ''
        name = d.get('name') or ''

        # 表情包：只有 id 没有 url 时，用 QQ 官方表情接口补一个
        if t == 'face' and not url:
            fid = str(d.get('id') or '')
            if fid.isdigit():
                url = 'https://qzonestyle.gtimg.cn/qzone/em/e%s.gif' % fid

        data = None
        if url:
            data = await dl.fetch(url)
        if data is None and path and os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    data = f.read(MAX_BYTES + 1)
            except Exception:
                data = None
        if data is None and path and ob is not None:
            # 让 NapCat 落一份到本地再读
            data = await _via_onebot(ob, t, path)

        if not data:
            out.append({'kind': t, 'seg': i, 'rel': '', 'bytes': 0,
                        'mime': '', 'local': 0, 'name': name})
            continue

        fname = '%s_%d%s' % (_safe_name(msg_id or str(int(ts))), i, ext)
        rel = os.path.join(str(account_uin or 'unknown'), day, fname)
        full = os.path.join(root, rel)
        try:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'wb') as f:
                f.write(data)
        except Exception as e:
            logbuf.warn('media', '落盘失败 %s：%s' % (rel, str(e)[:120]))
            out.append({'kind': t, 'seg': i, 'rel': '', 'bytes': len(data),
                        'mime': '', 'local': 0, 'name': name})
            continue

        size = len(data)
        mime = _guess_mime(t)

        # 语音转码：silk → mp3
        if need_conv and silk_bin and os.path.isfile(silk_bin):
            ok = await _silk_to_mp3(full, silk_bin, root, rel)
            if ok:
                mp3_rel = rel[:-len(ext)] + '.mp3'
                mp3_full = os.path.join(root, mp3_rel)
                try:
                    size = os.path.getsize(mp3_full)
                except Exception:
                    size = 0
                mime = 'audio/mpeg'
                rel = mp3_rel
                if not keep_silk:
                    try:
                        os.remove(full)
                    except Exception:
                        pass
            else:
                # 转码失败：保留原始 silk，标出来让 UI 走下载
                mime = 'audio/silk'
        elif need_conv:
            mime = 'audio/silk'

        out.append({'kind': t, 'seg': i, 'rel': rel, 'bytes': size,
                    'mime': mime, 'local': 1, 'name': name})
    return out


async def _via_onebot(ob, t, path):
    """让 NapCat 把媒体落到本地缓存再读。"""
    action = {'image': 'get_image', 'record': 'get_record', 'video': 'get_video'}.get(t)
    if not action or ob is None:
        return None
    try:
        r = await ob.call(action, {'file': path}, timeout=20)
        p = ((r.get('data') or {}).get('file')) or ''
        if p and os.path.exists(p):
            with open(p, 'rb') as f:
                return f.read(MAX_BYTES + 1)
    except Exception as e:
        logbuf.debug('media', 'OneBot 取媒体失败：%s' % str(e)[:100])
    return None


def _guess_mime(t):
    return {'image': 'image/jpeg', 'record': 'audio/mpeg', 'video': 'video/mp4',
            'face': 'image/gif', 'file': 'application/octet-stream'}.get(t, '')


async def _silk_to_mp3(silk_path, silk_bin, root, rel):
    """silk → mp3。失败返回 False（调用方保留原文件）。"""
    base = silk_path[:-len('.mp3')] if silk_path.endswith('.mp3') else os.path.splitext(silk_path)[0]
    wav = base + '.wav'
    mp3 = base + '.mp3'
    try:
        p = subprocess.run([silk_bin, silk_path, wav],
                           capture_output=True, timeout=30)
        if p.returncode != 0 or not os.path.exists(wav):
            return False
        p2 = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav,
                             '-b:a', '64k', mp3],
                            capture_output=True, timeout=60)
        if p2.returncode != 0 or not os.path.exists(mp3):
            return False
        try:
            os.remove(wav)
        except Exception:
            pass
        return True
    except FileNotFoundError:
        logbuf.warn('media', 'ffmpeg 不存在，语音无法转码')
        return False
    except Exception as e:
        logbuf.warn('media', '语音转码失败：%s' % str(e)[:150])
        return False


def dir_usage(root):
    """媒体目录占用统计（字节 + 文件数）。"""
    total = 0
    n = 0
    per = {}
    if not root or not os.path.isdir(root):
        return {'bytes': 0, 'files': 0, 'per_account': {}}
    try:
        for name in os.listdir(root):
            sub = os.path.join(root, name)
            if not os.path.isdir(sub):
                continue
            s = 0
            c = 0
            for dirpath, _, files in os.walk(sub):
                for fn in files:
                    try:
                        s += os.path.getsize(os.path.join(dirpath, fn))
                        c += 1
                    except Exception:
                        pass
            per[name] = {'bytes': s, 'files': c}
            total += s
            n += c
    except Exception:
        pass
    return {'bytes': total, 'files': n, 'per_account': per}


def disk_free(path):
    """目标目录所在磁盘的剩余空间。"""
    try:
        st = shutil.disk_usage(path if os.path.exists(path) else '/')
        return {'total': st.total, 'used': st.used, 'free': st.free}
    except Exception:
        return {'total': 0, 'used': 0, 'free': 0}
