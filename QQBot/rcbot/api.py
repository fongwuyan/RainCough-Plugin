# -*- coding: utf-8 -*-
"""HTTP API：给 RainCough 插件做转发用，只监听 127.0.0.1。"""
import json
import time

from aiohttp import web

from . import compress, config, llm, logbuf, search, store
from .bot import attach_images


def ok(data=None):
    return web.json_response({'ok': True, 'data': data})


def bad(msg, code=400):
    return web.json_response({'ok': False, 'error': str(msg)[:500]}, status=code)


async def _body(request):
    try:
        return await request.json()
    except Exception:
        return {}


def make_app(ob, bot):
    app = web.Application(client_max_size=8 * 1024 * 1024)

    # ---------------- 状态

    async def status(request):
        cfg = config.load()
        st = await ob.status()
        stats = await store.stats()
        prov = config.get_provider(cfg)
        persona = config.get_persona(cfg)
        return ok({
            'onebot': st,
            'stats': stats,
            'bot': cfg.get('bot'),
            'provider': (prov or {}).get('id'),
            'provider_model': (prov or {}).get('model'),
            'persona': (persona or {}).get('id'),
            'context': cfg.get('context'),
            'features': cfg.get('features'),
            'last_error': bot.last_error,
            'ts': int(time.time()),
        })

    # ---------------- 配置

    async def get_config(request):
        return ok(config.load())

    async def post_config(request):
        b = await _body(request)
        if not isinstance(b, dict):
            return bad('需要 JSON 对象')
        for k in ('providers', 'personas', 'default_provider', 'default_persona'):
            b.pop(k, None)     # 这两类走专用接口
        return ok(config.patch(b))

    # ---------------- 提供商

    async def get_providers(request):
        cfg = config.load()
        provs = cfg.get('providers') or []
        # 打码
        out = []
        for p in provs:
            q = dict(p)
            k = q.get('api_key') or ''
            q['key_hint'] = ('%s…%s' % (k[:6], k[-4:])) if len(k) > 12 else ('已设置' if k else '')
            q.pop('api_key', None)
            q['is_default'] = (p.get('id') == cfg.get('default_provider'))
            out.append(q)
        return ok({'items': out, 'default': cfg.get('default_provider')})

    async def post_providers(request):
        b = await _body(request)
        pid = (b.get('id') or '').strip()
        if not pid:
            return bad('缺少 id')
        cfg = config.load()
        arr = cfg.get('providers') or []
        cur = None
        for p in arr:
            if p.get('id') == pid:
                cur = p
                break
        if cur is None:
            cur = {'id': pid, 'enable': True, 'type': 'openai', 'timeout': 120}
            arr.append(cur)
        for k in ('label', 'type', 'api_base', 'model', 'timeout', 'enable'):
            if k in b:
                cur[k] = b[k]
        if b.get('api_key'):
            cur['api_key'] = b['api_key']
        if b.get('make_default'):
            cfg['default_provider'] = pid
        cfg['providers'] = arr
        if not cfg.get('default_provider'):
            cfg['default_provider'] = pid
        config.save(cfg)
        return ok({'id': pid})

    async def del_provider(request):
        b = await _body(request)
        pid = (b.get('id') or '').strip()
        cfg = config.load()
        cfg['providers'] = [p for p in (cfg.get('providers') or []) if p.get('id') != pid]
        if cfg.get('default_provider') == pid:
            cfg['default_provider'] = (cfg['providers'][0]['id'] if cfg['providers'] else '')
        config.save(cfg)
        return ok()

    async def test_provider(request):
        b = await _body(request)
        cfg = config.load()
        pid = (b.get('id') or '').strip()
        prov = None
        for p in cfg.get('providers') or []:
            if p.get('id') == pid:
                prov = dict(p)
                break
        if prov is None:
            prov = dict(b.get('provider') or {})
        if b.get('api_key'):
            prov['api_key'] = b['api_key']
        r = await llm.test(prov)
        return ok(r)

    async def provider_models(request):
        pid = request.query.get('id') or ''
        cfg = config.load()
        prov = None
        for p in cfg.get('providers') or []:
            if p.get('id') == pid:
                prov = p
                break
        if not prov:
            return bad('没有这个提供商')
        try:
            return ok(await llm.list_models(prov))
        except Exception as e:
            return bad(e)

    # ---------------- 人格

    async def get_personas(request):
        cfg = config.load()
        return ok({'items': cfg.get('personas') or [],
                   'default': cfg.get('default_persona')})

    async def post_personas(request):
        b = await _body(request)
        pid = (b.get('id') or '').strip()
        if not pid:
            return bad('缺少 id')
        cfg = config.load()
        arr = cfg.get('personas') or []
        cur = None
        for p in arr:
            if p.get('id') == pid:
                cur = p
                break
        if cur is None:
            cur = {'id': pid, 'name': pid, 'prompt': '', 'created_at': int(time.time())}
            arr.append(cur)
        for k in ('name', 'prompt'):
            if k in b:
                cur[k] = b[k]
        cur['updated_at'] = int(time.time())
        if b.get('make_default'):
            cfg['default_persona'] = pid
        cfg['personas'] = arr
        if not cfg.get('default_persona'):
            cfg['default_persona'] = pid
        config.save(cfg)
        return ok({'id': pid})

    async def del_persona(request):
        b = await _body(request)
        pid = (b.get('id') or '').strip()
        cfg = config.load()
        cfg['personas'] = [p for p in (cfg.get('personas') or []) if p.get('id') != pid]
        if cfg.get('default_persona') == pid:
            cfg['default_persona'] = (cfg['personas'][0]['id'] if cfg['personas'] else '')
        config.save(cfg)
        return ok()

    # ---------------- 会话

    async def get_sessions(request):
        rows = await store.list_sessions()
        cfg = config.load()
        gnames = getattr(bot, '_group_names', {}) or {}
        for r in rows:
            r['display'] = r.get('title') or (
                gnames.get(str(r.get('target_id')), '') if r.get('kind') == 'group' else '')
            r['mode_label'] = '公共' if (r.get('kind') == 'group' and r.get('mode') != 'private') else '私有'
        return ok({'items': rows, 'stats': await store.stats(),
                   'default_persona': cfg.get('default_persona'),
                   'default_provider': cfg.get('default_provider')})

    async def get_session(request):
        sid = request.match_info['sid']
        d = await store.session_detail(sid, int(request.query.get('limit') or 50))
        if not d:
            return bad('会话不存在', 404)
        summ = await store.get_summary(sid)
        d['summary_upto'] = (summ or {}).get('upto_msg_id')
        return ok(d)

    async def post_session(request):
        sid = request.match_info['sid']
        b = await _body(request)
        fields = {}
        for k in ('title', 'persona_id', 'provider_id', 'mode'):
            if k in b:
                fields[k] = b[k]
        if 'enabled' in b:
            fields['enabled'] = 1 if b['enabled'] else 0
        if not fields:
            return bad('没有要改的字段')
        await store.update_session(sid, fields)
        return ok(await store.get_session(sid))

    async def clear_session(request):
        sid = request.match_info['sid']
        await store.clear_session(sid)
        logbuf.info('api', '清空会话 %s' % sid)
        return ok()

    async def del_session(request):
        b = await _body(request)
        sid = (b.get('id') or '').strip()
        await store.delete_session(sid)
        logbuf.info('api', '删除会话 %s' % sid)
        return ok()

    # ---------------- 日志 / 统计

    async def get_logs(request):
        n = int(request.query.get('lines') or 300)
        kw = request.query.get('kw') or ''
        return ok({'lines': logbuf.tail(n, kw)})

    async def get_stats(request):
        return ok(await store.stats())

    # ---------------- 上下文预览

    async def preview_context(request):
        """给前端看某个会话现在会怎么拼上下文（不调模型）。"""
        sid = request.query.get('sid') or ''
        cfg = config.load()
        sess = await store.get_session(sid) if sid else None
        persona = config.get_persona(cfg, (sess or {}).get('persona_id'))
        provider = config.get_provider(cfg, (sess or {}).get('provider_id'))
        system = (persona or {}).get('prompt') or ''
        msgs = await store.recent_messages(sid, int((cfg.get('context') or {}).get('max_history_messages') or 200))
        summ = await store.get_summary(sid)
        summary = (summ or {}).get('content') or ''
        total = compress.est(system) + compress.est(summary) + compress.est_msgs(msgs)
        c = cfg.get('context') or {}
        budget = max(2000, int(c.get('max_tokens') or 128000)
                     - int(c.get('max_output_tokens') or 4096)
                     - compress.est(system) - compress.SAFE_MARGIN)
        return ok({
            'system': system,
            'summary': summary,
            'messages': msgs[-30:],
            'msg_count': len(msgs),
            'est_tokens': total,
            'budget': budget,
            'max_tokens': int(c.get('max_tokens') or 128000),
            'provider': (provider or {}).get('id'),
            'model': (provider or {}).get('model'),
        })

    # ---------------- 试聊（不经过 QQ，直接走完整链路）

    async def tools_search(request):
        q = (request.query.get('q') or '').strip()
        if not q:
            return bad('缺少 q')
        cfg = config.load()
        fs = (cfg.get('features') or {}).get('web_search') or {}
        try:
            res = await search.query(q, limit=int(fs.get('max_results') or 5))
        except Exception as e:
            return bad('搜索失败：%s' % str(e)[:300], 502)
        return ok({'query': q, 'results': res})

    async def test_chat(request):
        b = await _body(request)
        text = (b.get('text') or '').strip()
        if not text:
            return bad('缺少 text')
        cfg = config.load()
        sid = (b.get('sid') or '').strip()
        if not sid:
            sid = 'private:__test__'
            await store.ensure_session('private', '__test__', title='试聊', mode='private')
        sess = await store.get_session(sid)
        if not sess:
            return bad('会话不存在', 404)
        persona = config.get_persona(cfg, (sess or {}).get('persona_id'))
        provider = config.get_provider(cfg, (sess or {}).get('provider_id'))
        if not provider:
            return bad('没有可用的模型提供商')
        system = (persona or {}).get('prompt') or ''
        await store.add_message(sid, 'user', text, name='测试')
        tools, runner = llm.web_tools(cfg)
        try:
            sys2, messages, meta = await compress.build_context(cfg, sid, system, provider)
            vis = (cfg.get('features') or {}).get('vision') or {}
            if b.get('images') and vis.get('enabled'):
                n = await attach_images(messages, b.get('images'),
                                        int(vis.get('max_images') or 3))
                if n:
                    meta['images'] = n
            reply = await llm.chat(
                provider, messages, system=sys2,
                max_tokens=int((cfg.get('context') or {}).get('max_output_tokens') or 4096),
                tools=tools, tool_runner=runner)
        except Exception as e:
            return bad(e)
        await store.add_message(sid, 'assistant', reply)
        return ok({'reply': reply, 'sid': sid, 'meta': meta,
                   'messages': len(messages)})

    app.router.add_get('/api/status', status)
    app.router.add_get('/api/config', get_config)
    app.router.add_post('/api/config', post_config)

    app.router.add_get('/api/providers', get_providers)
    app.router.add_post('/api/providers', post_providers)
    app.router.add_post('/api/providers/delete', del_provider)
    app.router.add_post('/api/providers/test', test_provider)
    app.router.add_get('/api/providers/models', provider_models)

    app.router.add_get('/api/personas', get_personas)
    app.router.add_post('/api/personas', post_personas)
    app.router.add_post('/api/personas/delete', del_persona)

    app.router.add_get('/api/sessions', get_sessions)
    app.router.add_get('/api/sessions/{sid}', get_session)
    app.router.add_post('/api/sessions/{sid}', post_session)
    app.router.add_post('/api/sessions/{sid}/clear', clear_session)
    app.router.add_post('/api/sessions/delete', del_session)

    app.router.add_get('/api/logs', get_logs)
    app.router.add_get('/api/stats', get_stats)
    app.router.add_get('/api/context', preview_context)
    app.router.add_get('/api/tools/search', tools_search)
    app.router.add_post('/api/test/chat', test_chat)

    return app
