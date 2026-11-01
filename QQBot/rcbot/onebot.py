# -*- coding: utf-8 -*-
"""OneBot 11 正向 WS 客户端：连 NapCat、收事件、调 API。"""
import asyncio
import json

import aiohttp

from . import logbuf


class OneBot:
    def __init__(self, cfg_getter, on_event):
        self.cfg_getter = cfg_getter
        self.on_event = on_event          # async def (event) -> None
        self.ws = None
        self.connected = False
        self.self_id = ''
        self._pending = {}
        self._n = 0
        self._backoff = 1.0

    # ---------------- 连接

    async def run(self):
        while True:
            cfg = self.cfg_getter().get('onebot') or {}
            url = (cfg.get('ws_url') or '').strip()
            if not url:
                logbuf.warn('onebot', '没配 ws_url，5 秒后重试')
                await asyncio.sleep(5)
                continue
            headers = {}
            tok = (cfg.get('access_token') or '').strip()
            if tok:
                headers['Authorization'] = 'Bearer ' + tok
            try:
                await self._session(url, headers)
                self._backoff = 1.0
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logbuf.warn('onebot', '连接失败：%s（%.0fs 后重连）'
                            % (str(e)[:160], self._backoff))
            self.connected = False
            self.ws = None
            await asyncio.sleep(self._backoff)
            self._backoff = min(30.0, self._backoff * 1.8)

    async def _session(self, url, headers):
        async with aiohttp.ClientSession() as sess:
            async with sess.ws_connect(url, headers=headers, heartbeat=25,
                                       timeout=aiohttp.ClientWSTimeout(ws_close=5)) as ws:
                self.ws = ws
                self.connected = True
                self._backoff = 1.0
                logbuf.info('onebot', '已连上 %s' % url)
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            self._handle(json.loads(msg.data))
                        except Exception as e:
                            logbuf.warn('onebot', '解析消息失败：%s' % str(e)[:160])
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        break
        logbuf.warn('onebot', '连接断开')

    def _handle(self, data):
        echo = data.get('echo')
        if echo and echo in self._pending:
            fut = self._pending.pop(echo)
            if not fut.done():
                fut.set_result(data)
            return
        post = data.get('post_type')
        if post == 'meta_event':
            if data.get('meta_event_type') == 'lifecycle':
                sid = data.get('self_id')
                if sid:
                    self.self_id = str(sid)
                    logbuf.info('onebot', '账号 %s 已就绪' % sid)
            return
        if self.on_event:
            asyncio.create_task(self._safe_event(data))

    async def _safe_event(self, data):
        try:
            await self.on_event(data)
        except Exception as e:
            logbuf.error('bot', '处理事件出错：%s' % str(e)[:300])

    # ---------------- 调 API

    async def call(self, action, params=None, timeout=20):
        ws = self.ws
        if ws is None or ws.closed:
            raise RuntimeError('还没连上 NapCat')
        self._n += 1
        echo = 'rc-%d' % self._n
        fut = asyncio.get_event_loop().create_future()
        self._pending[echo] = fut
        try:
            await ws.send_json({'action': action, 'params': params or {}, 'echo': echo})
            return await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            raise RuntimeError('调用 %s 超时' % action)
        finally:
            self._pending.pop(echo, None)

    async def send_text(self, kind, target, text, mention=None):
        segs = []
        if mention:
            segs.append({'type': 'at', 'data': {'qq': str(mention)}})
            segs.append({'type': 'text', 'data': {'text': ' '}})
        segs.append({'type': 'text', 'data': {'text': text}})
        if kind == 'group':
            return await self.call('send_group_msg',
                                   {'group_id': int(target), 'message': segs})
        return await self.call('send_private_msg',
                               {'user_id': int(target), 'message': segs})

    async def status(self):
        out = {'connected': self.connected, 'self_id': self.self_id}
        try:
            r = await self.call('get_login_info', timeout=8)
            out['login'] = r.get('data') or {}
            out['online'] = r.get('status') == 'ok'
        except Exception as e:
            out['online'] = False
            out['error'] = str(e)[:160]
        return out
