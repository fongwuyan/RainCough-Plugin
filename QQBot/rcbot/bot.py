# -*- coding: utf-8 -*-
"""消息处理。

★ 2026-11-01 改造：事件处理拆成三条互相独立的路径（这是最容易做错的地方）

  路径 A 记录 —— 无条件全量落 chat_logs。
          不过滤黑白名单 / @ / 前缀 / 限流，群里别人聊天也记。
          用户要求"别只记机器人回话的那些"，这条路径是唯一保障。
  路径 B 应答 —— 沿用改造前的全部触发过滤，行为不变。
  路径 C 撤回 —— notice 事件按 msg_id 给已存的记录打标，原文保留。

  三者互不阻塞：记录功能坏了不能让机器人哑掉，应答策略调整不影响已存档内容。
"""
import base64
import io
import os
import time

import aiohttp

from . import chats, compress, config, llm, logbuf, media, profile, store

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
    """一个 Bot 服务所有账号。

    ob 由调用方按账号传入（每个账号一条连接），所以同一套代码能同时服务多个号。
    """

    def __init__(self, ob=None):
        self.ob = ob
        self.rl = RateLimiter()
        self._group_names = {}
        # 好友昵称 + 群头像。群名/好友名要调 OneBot 接口才能拿到，
        # 但那些接口要 QQ 已登录才有数据，所以在线程外异步拉，
        # 拉不到就退回"裸 QQ 号"显示（见 profile.display_name）。
        self._friend_names = {}
        self._group_avatars = {}
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

    # ---------------- 入口：按账号分发

    async def on_account_event(self, account, ev):
        """账号管理器把事件送进来。account 带 id / uin / cfg。"""
        self.ob = account.ob
        acct_cfg = account.cfg or {}
        acct_id = account.id or ''
        await self.on_event(ev, account_id=acct_id, acct_cfg=acct_cfg)

    # ---------------- 路径 C：撤回

    async def _handle_recall(self, ev, account_id):
        """notice 事件里的撤回：按 msg_id 打标，原文保留。

        OneBot 的撤回事件只带 message_id 不带原文
        （实测 napcat.mjs:85979-85988 反编译的类定义），
        所以内容必须在消息到达时就存下来 —— 这是路径 A 的存在理由之一。
        """
        nt = ev.get('notice_type') or ''
        if nt not in ('group_recall', 'friend_recall'):
            return
        msg_id = str(ev.get('message_id') or '')
        by = str(ev.get('operator_id') or ev.get('user_id') or '')
        kind = 'group' if nt == 'group_recall' else 'private'
        # 群号/对方号：给"没记到原文"的墓碑定位会话用
        target = str(ev.get('group_id') or ev.get('user_id') or '')
        try:
            await chats.mark_recalled(account_id, msg_id, by, kind, target)
        except Exception as e:
            logbuf.warn('chat', '撤回处理失败：%s' % str(e)[:200])

    # ---------------- 路径 A：记录（全量）

    async def _record(self, ev, account_id, acct_cfg):
        """无条件记录一条消息。不抛异常 —— 记录失败不该影响机器人应答。"""
        try:
            cfg = config.load()
            ccfg = cfg.get('chat') or {}
            if not ccfg.get('enabled', True):
                return
            mtype = ev.get('message_type') or ''
            if mtype not in ('group', 'private'):
                return
            self_id = str(ev.get('self_id') or '')
            uid = str(ev.get('user_id') or '')
            gid = str(ev.get('group_id') or '')
            if not uid:
                return
            # 机器人自己发的消息不在事件流里（reportSelfMessage=false），
            # 那边由发送路径自记。这里跳过自己发的，避免重复。
            if uid == self_id:
                return

            segs = ev.get('message')
            sender = ev.get('sender') or {}
            # 名字：群名片 > 昵称 > QQ 号；头像按 QQ 号从 qlogo 取
            uid, nick, avatar = profile.sender_profile(sender)
            target = gid if mtype == 'group' else uid
            ts = int(ev.get('time') or time.time())
            msg_id = str(ev.get('message_id') or '')

            # 媒体副本：必须同步下载（临时 URL 会过期）
            media_list = []
            if ccfg.get('media_enabled', True):
                mcfg = cfg.get('media') or {}
                dl = media.downloader(int(ccfg.get('download_concurrency') or 4),
                                      int(ccfg.get('download_timeout') or 20))
                media_list = await media.save_media(
                    segs, self.ob, chats.media_root(cfg),
                    acct_cfg.get('uin') or account_id, msg_id, ts, dl=dl,
                    silk_bin=mcfg.get('silk_decoder') or '',
                    keep_silk=bool(mcfg.get('keep_silk_source', True)),
                    account_id=account_id)

            await chats.record(account_id, mtype, target, 'user', segs,
                               sender_id=uid, sender_name=nick, msg_id=msg_id,
                               created_at=ts, media=media_list,
                               sender_avatar=avatar)
        except Exception as e:
            logbuf.warn('chat', '记录消息失败（不影响应答）：%s' % str(e)[:200])

    # ---------------- 主入口

    async def on_event(self, ev, account_id='', acct_cfg=None):
        acct_cfg = acct_cfg or {}
        post = ev.get('post_type')

        # 路径 C：撤回（notice）
        if post == 'notice':
            await self._handle_recall(ev, account_id)
            return
        if post != 'message':
            return

        # 路径 A：先无条件记录，再考虑要不要应答。
        # 顺序很重要 —— 记录要早于任何过滤，否则又变成"只记要回复的"。
        await self._record(ev, account_id, acct_cfg)

        # 路径 B：应答（原有逻辑）
        await self._maybe_reply(ev, account_id, acct_cfg)

    async def on_connected(self, ob=None, account_id=''):
        """OneBot 连上后回调：拉一次群列表/好友列表缓存名字。

        ★ 没有这一步，聊天记录里的群名/私聊名就一直是裸 QQ 号 ——
          因为名字只能从 OneBot 接口拿，而这些接口要登录后才有数据。
        """
        try:
            await self.fill_group_names(ob)
        except Exception as e:
            logbuf.debug('bot', '拉名字缓存失败：%s' % str(e)[:120])

    async def _maybe_reply(self, ev, account_id, acct_cfg):
        cfg = config.load()
        bot = config.resolve_bot_cfg(cfg, acct_cfg)
        if not bot.get('enabled', True):
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

        # 限流（按账号+会话，号之间互不影响）
        rl = bot.get('rate_limit') or {}
        rk = '%s:%s:%s' % (account_id, mtype, gid or uid)
        if not self.rl.allow(rk, int(rl.get('window') or 60), int(rl.get('max') or 30)):
            logbuf.debug('bot', '触发限流：%s' % rk)
            return

        # 会话（id 带账号前缀，多号不串）
        mode = (cfg.get('session_mode') or {}).get(
            'group' if mtype == 'group' else 'private', 'public')
        sender = ev.get('sender') or {}
        nick = sender.get('card') or sender.get('nickname') or uid
        title = ''
        if mtype == 'group':
            title = self._group_names.get(gid, '')
        sid = await store.ensure_session(mtype, gid or uid, title=title, mode=mode,
                                         account_id=account_id, uid=uid)
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

        # 人格 / 提供商（会话级 > 账号级 > 全局）
        persona = config.get_persona(cfg, (sess or {}).get('persona_id'), acct_cfg)
        provider = config.get_provider(cfg, (sess or {}).get('provider_id'), acct_cfg)
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
                r = await self.ob.send_text(mtype, gid or uid, chunk,
                                            mention=mention if i == 0 else None)
                # 机器人自己的发言也进聊天档案。
                # reportSelfMessage=false → 事件流里没有自己的消息，只能发送时自记。
                # 长回复分片，每片一个 message_id → 逐片记，否则撤回匹配不上。
                await self._record_own(account_id, acct_cfg, mtype, gid or uid,
                                        chunk, r, nick)
            except Exception as e:
                logbuf.error('bot', '发送失败：%s' % str(e)[:200])
                break

    async def send_manual(self, kind, target, text, reply_id=''):
        """面板「消息」页手动发一条文本。返回入库后的记录（前端直接替换乐观消息）。

        ★ 与机器人自动回复共用同一条发送路径（ob.send_text），
          所以 http/ws、token、群/私聊差异都不用再处理一遍。
        """
        text = str(text or '')
        if not text.strip():
            raise RuntimeError('消息内容为空')
        if self.ob is None:
            raise RuntimeError('QQ 还没连上')
        # 带引用发送：reply 段要放在最前，QQ 才会渲染成"引用回复"
        if reply_id:
            segs0 = [{'type': 'reply', 'data': {'id': str(reply_id)}},
                     {'type': 'text', 'data': {'text': text}}]
            if kind == 'group':
                r = await self.ob.call('send_group_msg',
                                       {'group_id': int(target), 'message': segs0})
            else:
                r = await self.ob.call('send_private_msg',
                                       {'user_id': int(target), 'message': segs0})
        else:
            r = await self.ob.send_text(kind, target, text)
        if not isinstance(r, dict) or r.get('status') != 'ok':
            raise RuntimeError('发送失败：%s' % str((r or {}).get('wording') or (r or {}).get('retcode') or r)[:160])
        data = (r or {}).get('data') or {}
        msg_id = str(data.get('message_id') or '')
        uin = str((data.get('sender') or {}).get('user_id') or '')
        if not uin.strip():
            uin = str(getattr(self.ob, 'self_id', '') or '')
        nick = ''
        try:
            info = await self.ob.call('get_login_info', timeout=8)
            nick = str(((info or {}).get('data') or {}).get('nickname') or '')
        except Exception:
            pass
        segs = [{'type': 'text', 'data': {'text': text}}]
        if reply_id:
            segs = [{'type': 'reply', 'data': {'id': str(reply_id)}}] + segs
        cfg = config.load()
        account_id = config.account_id(uin)
        created = int(time.time())
        row_id = await chats.record(account_id, kind, target, 'assistant', segs,
                                    sender_id=uin, sender_name=nick or '我',
                                    msg_id=msg_id, created_at=created, media=[])
        return {'id': row_id, 'msg_id': msg_id, 'created_at': created,
                'sender_id': uin, 'sender_name': nick or '我', 'role': 'assistant',
                'segs': segs, 'text': text, 'media': [], 'recalled': 0}

    async def recall(self, msg_id):
        """撤回一条消息（只能撤回自己有权限的，QQ 通常限 2 分钟内）。"""
        mid = str(msg_id or '')
        if not mid:
            raise RuntimeError('缺少 msg_id')
        if self.ob is None:
            raise RuntimeError('QQ 还没连上，稍后再试')
        if not (mid.lstrip('-').isdigit()):
            raise RuntimeError('msg_id 不合法：%s' % mid)
        await self.ob.call('delete_msg', {'message_id': int(mid)}, timeout=15)
        n = await chats.mark_recalled('', mid, by='self', kind='', target='')
        return {'recalled': True, 'updated': n}

    async def _record_own(self, account_id, acct_cfg, mtype, target, text, resp, nick):
        """记录机器人自己发出的消息。"""
        try:
            cfg = config.load()
            ccfg = cfg.get('chat') or {}
            if not ccfg.get('enabled', True):
                return
            data = (resp or {}).get('data') or {}
            msg_id = str(data.get('message_id') or '')
            segs = [{'type': 'text', 'data': {'text': text}}]
            await chats.record(account_id, mtype, target, 'assistant', segs,
                               sender_id=str((data.get('sender') or {}).get('user_id') or ''),
                               sender_name=nick or '机器人', msg_id=msg_id,
                               created_at=int(time.time()), media=[])
        except Exception as e:
            logbuf.debug('chat', '记录自身消息失败：%s' % str(e)[:120])

    # ---------------- 群名/好友名缓存（异步补，不阻塞）

    async def fill_group_names(self, ob=None):
        """拉一次群列表与好友列表，缓存群名/群头像/好友昵称。

        ★ 这个方法以前**从来没被调用过** —— 群名缓存永远是空的，
          于是聊天记录左侧列表里群名显示成裸群号。
          现在在 OneBot 连接就绪时自动调用。

        群名按账号缓存（不同号的群列表不同），键是 "账号id:群号"。
        """
        ob = ob or self.ob
        if ob is None:
            return
        try:
            r = await ob.call('get_group_list', timeout=15)
            for g in (r.get('data') or []):
                gid = str(g.get('group_id') or '')
                # 群名里可能带 QQ 的表情占位符（<$ÿĀ">…），必须清洗后再入缓存
                name = profile.clean_name(g.get('group_name'))
                if gid and name:
                    self._group_names[gid] = name
            if self._group_names:
                logbuf.info('bot', '群列表已缓存 %d 个' % len(self._group_names))
        except Exception as e:
            logbuf.debug('bot', '拉群列表失败：%s' % str(e)[:120])

        # 好友昵称：私聊会话显示名字靠它
        try:
            r = await ob.call('get_friend_list', timeout=15)
            for f in (r.get('data') or []):
                fid = str(f.get('user_id') or '')
                name = profile.clean_name(f.get('remark') or f.get('nickname') or '')
                if fid and name:
                    self._friend_names[fid] = name
            if self._friend_names:
                logbuf.info('bot', '好友列表已缓存 %d 个' % len(self._friend_names))
        except Exception as e:
            logbuf.debug('bot', '拉好友列表失败：%s' % str(e)[:120])

    def group_display(self, gid):
        """群会话的显示名 + 头像。

        群头像 QQ 没有公开直链（不像个人头像是 qlogo），
        所以头像用"群号当 QQ 号"去 qlogo 取 —— 取不到时前端显示占位圆。
        """
        gid = str(gid or '')
        name = profile.clean_name(self._group_names.get(gid, ''))
        return name or gid, profile.avatar_url(gid)

    def friend_display(self, uid):
        """私聊会话的显示名 + 头像。"""
        uid = str(uid or '')
        name = profile.clean_name(self._friend_names.get(uid, ''))
        return name or uid, profile.avatar_url(uid)
