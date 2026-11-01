# -*- coding: utf-8 -*-
"""消息处理：过滤 → 定位会话 → 组上下文（含图片/联网/引用）→ 调模型 → 回消息。"""
import base64
import io
import os
import time

import aiohttp

from . import compress, config, llm, logbuf, store

MAX_REPLY_CHARS = 3000
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_IMAGE_SIDE = 1536   # 长边；文字截图要看清，太小会糊


def _seg_text(segs):
    """从 OneBot 消息段里取纯文本、at 列表、图片信息。

    图片给 dict（url + file）：先按 url 下载，失败再用 file 找本地缓存。
    """
    if isinstance(segs, str):
        return segs, [], []
    texts, ats, imgs = [], [], []
    for s in segs or []:
        if not isinstance(s, dict):
            continue
        t = s.get('type')
        d = s.get('data') or {}
        if t == 'text':
            texts.append(d.get('text') or '')
        elif t == 'at':
            qq = str(d.get('qq') or '')
            if qq and qq != 'all':
                ats.append(qq)
        elif t == 'image':
            imgs.append({'url': d.get('url') or '', 'file': d.get('file') or ''})
            texts.append('[图片]')
        elif t == 'face':
            texts.append('[表情]')
        elif t == 'record':
            texts.append('[语音]')
        elif t == 'video':
            texts.append('[视频]')
        elif t == 'file':
            texts.append('[文件]')
    return ''.join(texts).strip(), ats, imgs


# 模型侧只认这四种（实测 deepseek 报错信息里列的就是 webp/png/jpeg/gif）
_MAGIC = [
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
    (b'GIF87a', 'image/gif'),
    (b'GIF89a', 'image/gif'),
]


def _mime_of(b):
    """只按文件头判断；认不出来就返回 None —— 千万别默认成 jpeg。

    QQ 图片链接会过期/被风控，这时候拿回来的是 HTML 错误页，
    默认成 image/jpeg 硬发，模型会整条请求 400，回复直接没了。
    """
    for magic, mime in _MAGIC:
        if b.startswith(magic):
            return mime
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
        return 'image/webp'
    return None


def _normalize_image(raw):
    """统一转成干净的 JPEG。

    QQ 的图千奇百怪：CMYK JPEG、APNG、WebP、超大图、动图……
    模型偶尔以「unsupported image」整条拒掉，转一遍最省事。
    没有 Pillow 就原样返回，靠文件头判断。
    """
    try:
        from PIL import Image
    except Exception:
        return raw, _mime_of(raw)
    try:
        im = Image.open(io.BytesIO(raw))
        try:
            im.seek(0)          # 动图只取第一帧
        except Exception:
            pass
        if im.mode not in ('RGB', 'L'):
            im = im.convert('RGB')
        w, h = im.size
        longest = max(w, h)
        if longest > MAX_IMAGE_SIDE:
            s = float(MAX_IMAGE_SIDE) / longest
            im = im.resize((max(1, int(w * s)), max(1, int(h * s))))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=85, optimize=True)
        return buf.getvalue(), 'image/jpeg'
    except Exception as e:
        logbuf.debug('bot', '图片转码失败，按原样发：%s' % str(e)[:80])
        return raw, _mime_of(raw)


async def _fetch_image(src, ob=None, timeout=15):
    """拿到图片原始字节：先 url，再本地缓存，最后让 OneBot 落一份。"""
    url = (src.get('url') if isinstance(src, dict) else src) or ''
    path = (src.get('file') if isinstance(src, dict) else '') or ''
    errs = []

    if url.startswith('http'):
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, timeout=aiohttp.ClientTimeout(total=timeout),
                                    headers={'User-Agent': 'Mozilla/5.0'}) as r:
                    if r.status >= 400:
                        raise RuntimeError('HTTP %s' % r.status)
                    # ⚠️ 必须循环读到底：StreamReader.read(n) 只返回「当前缓冲区里的
                    # 最多 n 字节」，不是读满 n。之前直接 read(MAX+1) 只拿到 32KB，
                    # 图被截断，模型一律回 "unsupported image"。
                    chunks, total = [], 0
                    while True:
                        chunk = await r.content.read(65536)
                        if not chunk:
                            break
                        chunks.append(chunk)
                        total += len(chunk)
                        if total > MAX_IMAGE_BYTES:
                            raise RuntimeError('图片超过 %dMB'
                                               % (MAX_IMAGE_BYTES // 1024 // 1024))
                    data = b''.join(chunks)
            if data:
                return data
        except Exception as e:
            errs.append('url %s' % str(e)[:60])

    if path and os.path.exists(path):
        with open(path, 'rb') as f:
            return f.read(MAX_IMAGE_BYTES + 1)

    # url 过期时，让 NapCat 把图落到本地缓存再读
    if ob is not None and path:
        try:
            r = await ob.call('get_image', {'file': path}, timeout=timeout)
            p2 = ((r.get('data') or {}).get('file')) or ''
            if p2 and os.path.exists(p2):
                with open(p2, 'rb') as f:
                    return f.read(MAX_IMAGE_BYTES + 1)
        except Exception as e:
            errs.append('get_image %s' % str(e)[:60])

    raise RuntimeError('取不到图片' + ('（%s）' % '；'.join(errs) if errs else ''))


async def _image_data_url(src, ob=None, timeout=15):
    """把图片读成 data URL —— 模型服务端拉不到墙外的图，只能我们代传。"""
    data = await _fetch_image(src, ob, timeout)
    if not data:
        raise RuntimeError('图片为空')
    if len(data) > MAX_IMAGE_BYTES:
        raise RuntimeError('图片超过 %dMB' % (MAX_IMAGE_BYTES // 1024 // 1024))
    raw_len = len(data)
    data, mime = _normalize_image(data)
    if not mime:
        raise RuntimeError('不是可识别的图片（头部 %s）' % data[:8].hex())
    logbuf.debug('bot', '图片 %d → %d 字节 / %s' % (raw_len, len(data), mime))
    return 'data:%s;base64,%s' % (mime, base64.b64encode(data).decode())


async def attach_images(messages, imgs, limit=3, ob=None):
    """把图片作为 content 分段挂到最后一条 user 消息上，返回成功张数。

    只挂当前这轮，历史里仍然只留 [图片] 文本 —— 否则每轮都要重传图片，
    token 会爆。
    """
    if not messages or not imgs:
        return 0
    idx = len(messages) - 1
    while idx >= 0 and messages[idx].get('role') != 'user':
        idx -= 1
    if idx < 0:
        return 0
    cur = messages[idx].get('content') or ''
    if not isinstance(cur, str):
        return 0
    parts = [{'type': 'text', 'text': cur or '看看这张图'}]
    n = 0
    for src in imgs[:max(1, limit)]:
        try:
            parts.append({'type': 'image_url',
                          'image_url': {'url': await _image_data_url(src, ob)}})
            n += 1
        except Exception as e:
            tag = (src.get('file') if isinstance(src, dict) else src) or ''
            logbuf.warn('bot', '图片加载失败（%s）：%s' % (str(tag)[:50], str(e)[:120]))
    if not n:
        return 0
    messages[idx]['content'] = parts
    return n



class RateLimiter:
    def __init__(self):
        self.hits = {}

    def allow(self, key, window, limit):
        if limit <= 0:
            return True
        now = time.time()
        arr = self.hits.get(key) or []
        arr = [t for t in arr if now - t < window]
        if len(arr) >= limit:
            self.hits[key] = arr
            return False
        arr.append(now)
        self.hits[key] = arr
        return True


class Bot:
    def __init__(self, ob):
        self.ob = ob
        self.rl = RateLimiter()
        self._group_names = {}
        self.last_error = ''

    # ---------------- 引用消息：reply 段只给 id，得再查一次

    async def _resolve_quote(self, segs):
        """取出被引用消息的文本、发送者、图片。

        用户「引用一张图再问这是什么」时，图片不在当前消息段里，
        只有一个 reply(id)，不查就永远看不到图。
        """
        rid = ''
        for s in segs or []:
            if isinstance(s, dict) and s.get('type') == 'reply':
                rid = str((s.get('data') or {}).get('id') or '')
                break
        if not rid:
            return '', '', []
        try:
            mid = int(rid) if rid.isdigit() else rid
            r = await self.ob.call('get_msg', {'message_id': mid}, timeout=12)
            d = r.get('data') or {}
            qtext, _, qimgs = _seg_text(d.get('message'))
            sender = d.get('sender') or {}
            who = (sender.get('card') or sender.get('nickname')
                   or str(sender.get('user_id') or ''))
            return qtext, who, qimgs
        except Exception as e:
            logbuf.debug('bot', '取引用消息失败（%s）：%s' % (rid, str(e)[:100]))
            return '', '', []

    # ---------------- 入口

    async def on_event(self, ev):
        if ev.get('post_type') != 'message':
            return
        cfg = config.load()
        if not (cfg.get('bot') or {}).get('enabled', True):
            return

        mtype = ev.get('message_type')          # private | group
        self_id = str(ev.get('self_id') or self.ob.self_id or '')
        uid = str(ev.get('user_id') or '')
        gid = str(ev.get('group_id') or '')
        if not uid or uid == self_id:
            return

        text, ats, imgs = _seg_text(ev.get('message'))
        quote_text, quote_who, quote_imgs = await self._resolve_quote(ev.get('message'))
        if not text and not imgs and not quote_imgs:
            return

        bot = cfg.get('bot') or {}
        if mtype == 'group':
            if gid in [str(x) for x in (bot.get('blocked_groups') or [])]:
                return
            allow = [str(x) for x in (bot.get('allowed_groups') or [])]
            if allow and gid not in allow:
                return
            need_at = bool(bot.get('group_need_at', True))
            prefixes = bot.get('wake_prefix') or []
            hit_prefix = None
            for p in prefixes:
                if p and text.startswith(p):
                    hit_prefix = p
                    break
            if need_at and self_id not in ats and hit_prefix is None:
                return
            if hit_prefix:
                text = text[len(hit_prefix):].strip()
            # 只发图 / 只引用不说话也要回，别被空文本拦掉
            if not text and not imgs and not quote_imgs:
                return
        else:
            if not bot.get('private_always_reply', True):
                return

        # 限流
        rl = bot.get('rate_limit') or {}
        if not self.rl.allow('%s:%s' % (mtype, gid or uid),
                             int(rl.get('window') or 60), int(rl.get('max') or 30)):
            logbuf.debug('bot', '触发限流：%s/%s' % (mtype, gid or uid))
            return

        # 会话
        mode = (cfg.get('session_mode') or {}).get(
            'group' if mtype == 'group' else 'private', 'public')
        sender = ev.get('sender') or {}
        nick = sender.get('card') or sender.get('nickname') or uid
        title = ''
        if mtype == 'group':
            title = self._group_names.get(gid, '')
        sid = await store.ensure_session(mtype, gid or uid, title=title, mode=mode)
        sess = await store.get_session(sid)
        if sess and not sess.get('enabled', 1):
            logbuf.debug('bot', '会话 %s 已停用，跳过' % sid)
            return

        prompt_text = text or ('[图片]' if imgs else '')
        if quote_text or quote_imgs:
            q = quote_text or '[图片]'
            head = '（引用 %s：%s）' % (quote_who or '上一条消息', q)
            prompt_text = (head + ('\n' + prompt_text if prompt_text else '')).strip()
        prompt_text = prompt_text or '[图片]'
        # 当前消息的图优先，其次才是被引用的图
        all_imgs = list(imgs) + list(quote_imgs)
        await store.add_message(sid, 'user', prompt_text, name=nick)

        # 人格 / 提供商
        persona = config.get_persona(cfg, (sess or {}).get('persona_id'))
        provider = config.get_provider(cfg, (sess or {}).get('provider_id'))
        system = (persona or {}).get('prompt') or ''
        if not provider:
            self.last_error = '没有可用的模型提供商'
            logbuf.error('bot', self.last_error)
            return

        ctx = cfg.get('context') or {}
        vis = (cfg.get('features') or {}).get('vision') or {}
        tools, runner = llm.web_tools(cfg)
        try:
            system, messages, meta = await compress.build_context(cfg, sid, system, provider)
            plain = None          # 去掉图片后的版本，带图失败时兜底重试
            if vis.get('enabled') and all_imgs:
                n = await attach_images(messages, all_imgs,
                                        int(vis.get('max_images') or 3), ob=self.ob)
                if n:
                    meta['images'] = n
                    plain = [dict(m) for m in messages[:-1]]
                    plain.append({'role': 'user', 'content': prompt_text})
            logbuf.info('bot', '%s ← %s（%s）上下文 %d 条 / ~%s tokens%s%s%s'
                        % (sid, nick, text[:40], len(messages), meta.get('tokens'),
                           '，已压缩' if meta.get('compressed') else '',
                           '，图 %d 张' % meta['images'] if meta.get('images') else '',
                           '，联网开' if tools else ''))
            try:
                reply = await llm.chat(provider, messages, system=system,
                                       max_tokens=int(ctx.get('max_output_tokens') or 2048),
                                       tools=tools, tool_runner=runner)
            except Exception as e:
                if plain and ('image' in str(e).lower() or '图片' in str(e)):
                    logbuf.warn('bot', '带图请求被拒，去掉图片重试：%s' % str(e)[:150])
                    meta.pop('images', None)
                    reply = await llm.chat(provider, plain, system=system,
                                           max_tokens=int(ctx.get('max_output_tokens') or 2048),
                                           tools=tools, tool_runner=runner)
                else:
                    raise
        except Exception as e:
            self.last_error = str(e)[:300]
            logbuf.error('bot', '生成失败：%s' % self.last_error)
            return

        reply = (reply or '').strip()
        if not reply:
            return
        await store.add_message(sid, 'assistant', reply)

        mention = None
        if mtype == 'group' and bot.get('reply_with_mention'):
            mention = uid
        for i in range(0, len(reply), MAX_REPLY_CHARS):
            chunk = reply[i:i + MAX_REPLY_CHARS]
            try:
                await self.ob.send_text(mtype, gid or uid, chunk, mention=mention if i == 0 else None)
            except Exception as e:
                logbuf.error('bot', '发送失败：%s' % str(e)[:200])
                break

    # ---------------- 群名缓存（异步补，不阻塞）

    async def fill_group_names(self):
        try:
            r = await self.ob.call('get_group_list', timeout=15)
            for g in (r.get('data') or []):
                gid = str(g.get('group_id') or '')
                name = g.get('group_name') or ''
                if gid and name:
                    self._group_names[gid] = name
            if self._group_names:
                logbuf.info('bot', '群列表已缓存 %d 个' % len(self._group_names))
        except Exception as e:
            logbuf.debug('bot', '拉群列表失败：%s' % str(e)[:120])
