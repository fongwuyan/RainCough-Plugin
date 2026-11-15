# -*- coding: utf-8 -*-
"""HTTP API：给 RainCough 插件做转发用，只监听 127.0.0.1。

2026-11-01 新增：
  /api/accounts*  多账号（连接状态、账号级配置）
  /api/chat/*     全量聊天记录（会话、消息、导出、统计、清理）
"""
import asyncio
import hashlib
import json
import os
import random as _random
import re
import time
import uuid
from collections import deque

from aiohttp import web

from . import cards, chats, compress, config, forward, group_avatar, llm, logbuf, media, memory, panel, profile, search, store, tools
from .bot import attach_images, strip_emoji, strip_meta_leak, truncate_chars

# ---------------- 媒体转码任务（异步）
# 一次转几十个大视频要几分钟，同步 HTTP 会超时、也不能取消。
# 这里用内存任务表：启动 → 逐条转 → 进度/取消可查（进程重启后任务丢失，前端会提示）。
_media_jobs = {}
_media_job_seq = 0


def _job_public(job):
    return {k: v for k, v in job.items() if k != 'cancel'}


async def _start_transcode_job(ids):
    global _media_job_seq
    _media_job_seq += 1
    jid = 'tr%d-%d' % (int(time.time()), _media_job_seq)
    _media_jobs[jid] = {
        'id': jid, 'state': 'running', 'total': len(ids), 'done': 0,
        'ok': 0, 'failed': 0, 'error': '', 'current': 0,
        'started_at': int(time.time()), 'cancel': False,
    }
    asyncio.create_task(_run_transcode_job(jid, list(ids)))
    return jid


async def _run_transcode_job(jid, ids):
    job = _media_jobs.get(jid)
    if not job:
        return
    for i, mid in enumerate(ids):
        if job.get('cancel'):
            job['state'] = 'cancelled'
            break
        job['current'] = mid
        try:
            r = await chats.transcode_media([mid])
            job['ok'] += int((r or {}).get('ok') or 0)
            job['failed'] += int((r or {}).get('failed') or 0)
        except Exception as e:
            job['failed'] += 1
            job['error'] = str(e)[:160]
            logbuf.debug('chat', '转码任务失败 %s：%s' % (mid, str(e)[:80]))
        job['done'] = i + 1
        await asyncio.sleep(0)
    if job.get('state') != 'cancelled':
        job['state'] = 'done'
    job['finished_at'] = int(time.time())
    # 只保留最近 20 个任务
    if len(_media_jobs) > 20:
        for k in sorted(_media_jobs, key=lambda x: _media_jobs[x].get('started_at', 0))[:len(_media_jobs) - 20]:
            if _media_jobs[k].get('state') != 'running':
                _media_jobs.pop(k, None)



# random_reply 生成后先存这儿，用户点「发送到 QQ」时凭 token 取回发送
# （不重新调模型 —— 页面看到什么，群里就是什么）。
_RND_CACHE = {}
_RND_TTL = 300      # 5 分钟过期
_RND_MAX = 50
# 最近抽过的消息，避免连续翻到同一条
_RND_RECENT = deque(maxlen=30)
# 抽过的文本指纹（同文反复出现的不再挑）
_RND_SEEN = deque(maxlen=200)
# 每个会话的抽取状态：{sid: {last, count}}
_RND_GROUP = {}


def _pick_weighted(rows):
    """从候选消息里按权重抽一条。

    权重 = 长度合适度 × 内容可接话度 × 新鲜度 × 群公平度
    目的：像人翻聊天记录，挑「有话可接」的，而不是纯随机翻到 `[图片]` 或一句"嗯"。
    """
    now = int(time.time())
    recent_ids = set(_RND_RECENT)
    seen_hashes = {h for h, _t in _RND_SEEN}
    scored = []
    for r in rows:
        if r.get('id') in recent_ids:
            continue
        text = str(r.get('text') or '').strip()
        n = len(text)
        if n < 4 or n > 500:
            continue
        if text.startswith('[引用]'):
            continue
        h = hashlib.sha1(text.encode('utf-8')).hexdigest()[:16]
        if h in seen_hashes:
            continue
        # 长度：8–60 字最像一句可接的话
        if 8 <= n <= 60:
            ls = 1.0
        elif n < 8:
            ls = 0.45
        elif n <= 120:
            ls = 0.85
        else:
            ls = max(0.2, 120.0 / n)
        # 内容信号：问句更好接；命令/@/链接/纯符号降权
        cs = 1.0
        if text.endswith(('?', '？')):
            cs += 0.45
        if any(c in text for c in '。！？!?…'):
            cs += 0.15
        if text.startswith(('@', '/', '#')):
            cs -= 0.35
        if text.startswith('['):
            cs -= 0.5
        if re.search(r'https?://', text) and n < 40:
            cs -= 0.4
        if not re.search(r'[\u4e00-\u9fffA-Za-z]', text):
            cs = 0.1
        cs = max(0.05, cs)
        # 新鲜度：半衰期 10 天，老消息保底 0.2
        age_days = max(0.0, (now - (r.get('created_at') or now)) / 86400.0)
        rs = max(0.2, 0.5 ** (age_days / 10.0))
        # 群公平：刚抽过的群暂时降权，抽得多的群也降权
        st = _RND_GROUP.get(r.get('session_id')) or {}
        last = int(st.get('last') or 0)
        cnt = int(st.get('count') or 0)
        if now - last > 3600:
            cnt = 0
        gs = 1.0 if now - last > 1800 else 0.35
        gf = 1.0 / (1.0 + cnt * 0.15)
        scored.append((max(0.001, ls * cs * rs * gs * gf), r, h))
    if not scored:
        return None
    total = sum(x[0] for x in scored)
    x = _random.random() * total
    for w, r, h in scored:
        x -= w
        if x <= 0:
            sid = r.get('session_id') or ''
            st = _RND_GROUP.setdefault(sid, {'last': 0, 'count': 0})
            st['last'] = now
            st['count'] = int(st.get('count') or 0) + 1
            _RND_RECENT.append(r.get('id'))
            _RND_SEEN.append((h, now))
            return r
    pick = scored[-1][1]
    _RND_RECENT.append(pick.get('id'))
    return pick


def _put_random(token, item):
    now = int(time.time())
    for k in [k for k, v in _RND_CACHE.items() if now - (v.get('at') or 0) > _RND_TTL]:
        _RND_CACHE.pop(k, None)
    if len(_RND_CACHE) >= _RND_MAX:
        for k in sorted(_RND_CACHE, key=lambda x: _RND_CACHE[x].get('at') or 0)[:10]:
            _RND_CACHE.pop(k, None)
    _RND_CACHE[token] = item


def _peek_random(token):
    """只看不消费：发送失败时还能重试。"""
    item = _RND_CACHE.get(token)
    if not item:
        return None
    if int(time.time()) - (item.get('at') or 0) > _RND_TTL:
        _RND_CACHE.pop(token, None)
        return None
    return item


def _consume_random(token):
    _RND_CACHE.pop(token, None)


def _take_random(token):
    """取回并作废（一条结果只发一次，避免重复点击发两遍）。"""
    item = _RND_CACHE.pop(token, None)
    if not item:
        return None
    if int(time.time()) - (item.get('at') or 0) > _RND_TTL:
        return None
    return item


def ok(data=None):
    return web.json_response({'ok': True, 'data': data})


def bad(msg, code=400):
    return web.json_response({'ok': False, 'error': str(msg)[:500]}, status=code)


async def _body(request):
    try:
        return await request.json()
    except Exception:
        return {}


def make_app(mgr, bot):
    app = web.Application(client_max_size=8 * 1024 * 1024)

    # ---------------- 状态

    async def status(request):
        cfg = config.load()
        accounts = await mgr.status_all()
        stats_ = await store.stats()
        prov = config.get_provider(cfg)
        persona = config.get_persona(cfg)
        # 单账号时保留旧的 onebot 字段，前端老代码不用改
        onebot = accounts[0] if len(accounts) == 1 else {
            'connected': any(a.get('online') for a in accounts),
            'self_id': accounts[0].get('self_id', '') if accounts else '',
            'accounts': accounts,
        }
        return ok({
            'onebot': onebot,
            'accounts': accounts,
            'stats': stats_,
            'bot': cfg.get('bot'),
            'provider': (prov or {}).get('id'),
            'provider_model': (prov or {}).get('model'),
            'persona': (persona or {}).get('id'),
            'context': cfg.get('context'),
            'features': cfg.get('features'),
            'last_error': bot.last_error,
            'ts': int(time.time()),
        })

    # ---------------- 账号

    async def get_accounts(request):
        cfg = config.load()
        items = await mgr.status_all()
        # 配置里有但还没连上的（刚加的号），也要显示出来
        live = {a.get('id') for a in items}
        for a in config.get_accounts(cfg):
            if a['id'] not in live:
                items.append({'id': a['id'], 'uin': a.get('uin') or '', 'online': False,
                              'connected': False, 'nick': a.get('nick') or '',
                              'avatar': a.get('avatar') or '', 'ws_url': a.get('ws_url') or '',
                              'webui': a.get('webui') or '', 'unit': a.get('unit') or '',
                              'enabled': bool(a.get('enabled', True)),
                              'persona_id': a.get('persona_id') or '',
                              'provider_id': a.get('provider_id') or '',
                              'instance_dir': a.get('instance_dir') or '',
                              'pending': True})
        return ok({'items': items, 'count': len(items)})

    async def post_accounts(request):
        """新增/修改/删除账号。action = add | update | remove | toggle"""
        b = await _body(request)
        action = (b.get('action') or 'update').lower()
        cfg = config.load()
        obcfg = cfg.setdefault('onebot', {})
        accs = obcfg.setdefault('accounts', [])
        aid = (b.get('id') or '').strip()

        def find(it):
            for i, a in enumerate(accs):
                if a.get('id') == aid:
                    return i, a
            return -1, None

        if action == 'add':
            uin = str(b.get('uin') or '').strip()
            if not uin:
                return bad('缺少 uin')
            new_id = config.account_id(uin)
            # 已存在就更新（幂等）—— 实例修复/重建时会重复调这里，
            # 直接报错会导致账号配置同步不上
            exist = None
            for i, a in enumerate(accs):
                if a.get('id') == new_id or str(a.get('uin') or '') == uin:
                    exist = i
                    break
            if exist is not None:
                accs[exist].update({
                    'ws_url': (b.get('ws_url') or accs[exist].get('ws_url') or '').strip(),
                    'webui': b.get('webui') or accs[exist].get('webui') or '',
                    'unit': b.get('unit') or accs[exist].get('unit') or '',
                    'instance_dir': b.get('instance_dir') or accs[exist].get('instance_dir') or '',
                    'enabled': True,
                })
                config.save(cfg)
                await store.upsert_account(new_id, uin=uin)
                return ok({'id': new_id, 'updated': True})
            acc = {
                'id': new_id,
                'uin': uin,
                'ws_url': (b.get('ws_url') or '').strip(),
                'access_token': b.get('access_token') or '',
                'enabled': True,
                'nick': b.get('nick') or '',
                'avatar': b.get('avatar') or '',
                'webui': b.get('webui') or '',
                'unit': b.get('unit') or '',
                'instance_dir': b.get('instance_dir') or '',
            }
            # ★ 单账户（2026-11-02 从多账户回退）：只保留一条。
            #   换号时新账号进来，旧的直接清掉 —— 否则机器人会同时挂着
            #   两条 OneBot 连接，事件归属和聊天记录都会串。
            if len(accs) > 0:
                for old in list(accs):
                    if old.get('id') != new_id:
                        try:
                            await store.upsert_account(old['id'], enabled=0)
                        except Exception:
                            pass
                        accs.remove(old)
            accs.append(acc)
            await store.upsert_account(new_id, uin=uin, nick=acc['nick'])
            config.save(cfg)
            return ok({'id': new_id})

        if action == 'remove':
            i, a = find(aid)
            if i < 0:
                return bad('没有这个账号', 404)
            accs.pop(i)
            config.save(cfg)
            return ok({'id': aid})

        i, a = find(aid)
        if i < 0:
            return bad('没有这个账号', 404)
        for k in ('ws_url', 'access_token', 'nick', 'avatar', 'webui', 'unit',
                  'instance_dir', 'persona_id', 'provider_id'):
            if k in b:
                a[k] = b[k]
        if 'enabled' in b:
            a['enabled'] = bool(b['enabled'])
        if isinstance(b.get('bot'), dict):
            a['bot'] = b['bot']
        config.save(cfg)
        db_fields = {k: a[k] for k in ('nick', 'avatar', 'persona_id', 'provider_id')
                     if k in a}
        db_fields['enabled'] = 1 if a.get('enabled', True) else 0
        if 'bot' in a:
            db_fields['bot_cfg'] = a['bot']
        await store.upsert_account(aid, **db_fields)
        return ok({'id': aid})

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
        # 兼容层：人格的本体已经是「角色卡片」，这里返回兼容形状
        cfg = config.load()
        items = [cards.to_persona(c) for c in cards.list_cards(cfg)]
        return ok({'items': items, 'default': cards.default_id(cfg)})

    async def post_personas(request):
        b = await _body(request)
        pid = (b.get('id') or '').strip()
        if not pid:
            return bad('缺少 id')
        cfg = config.load()
        cur = cards.find(cfg, pid) or cards.normalize({'id': pid, 'name': pid})
        for k in ('name', 'prompt'):
            if k in b:
                cur[k] = b[k]
        if b.get('make_default'):
            cur['status'] = 'published'
        cards.save(cfg, cur, set_default=bool(b.get('make_default')))
        config.save(cfg)
        return ok({'id': cur['id']})

    async def del_persona(request):
        b = await _body(request)
        pid = (b.get('id') or '').strip()
        cfg = config.load()
        cards.delete(cfg, pid)
        config.save(cfg)
        return ok()

    # ---------------- 角色卡片
    async def get_cards(request):
        cfg = config.load()
        items = [cards.with_assets(cfg, c) for c in cards.list_cards(cfg)]
        return ok({'items': items, 'default': cards.default_id(cfg),
                   'schema': cards.SCHEMA})

    async def post_cards(request):
        """保存角色卡片。传 id 就是更新，不传就是新建。"""
        b = await _body(request)
        card = b.get('card') if isinstance(b.get('card'), dict) else b
        if not str(card.get('name') or '').strip():
            return bad('角色名字不能为空')
        cfg = config.load()
        saved = cards.save(cfg, card, set_default=bool(b.get('set_default')))
        config.save(cfg)
        return ok(cards.with_assets(cfg, saved))

    async def del_card(request):
        b = await _body(request)
        cid = (b.get('id') or '').strip()
        if not cid:
            return bad('缺少 id')
        cfg = config.load()
        n = cards.delete(cfg, cid)
        config.save(cfg)
        return ok({'left': n})

    async def clone_card(request):
        b = await _body(request)
        cid = (b.get('id') or '').strip()
        cfg = config.load()
        c = cards.clone(cfg, cid, (b.get('name') or '').strip())
        if not c:
            return bad('找不到这张卡片')
        config.save(cfg)
        return ok(cards.with_assets(cfg, c))

    async def import_card(request):
        b = await _body(request)
        try:
            c = cards.import_card(b.get('json') or b.get('card') or '')
        except Exception as e:
            return bad(str(e)[:200])
        cfg = config.load()
        saved = cards.save(cfg, c)
        config.save(cfg)
        return ok(cards.with_assets(cfg, saved))

    async def export_card(request):
        q = request.query
        cid = (q.get('id') or '').strip()
        cfg = config.load()
        c = cards.find(cfg, cid) if cid else None
        if not c:
            c = cards.find(cfg, cards.default_id(cfg))
        if not c:
            return bad('没有可导出的卡片')
        return ok({'json': cards.export_card(c), 'card': c})

    # ---------------- 会话

    async def get_sessions(request):
        account_id = request.query.get('account_id') or ''
        rows = await store.list_sessions(account_id)
        cfg = config.load()
        gnames = getattr(bot, '_group_names', {}) or {}
        fnames = getattr(bot, '_friend_names', {}) or {}
        for r in rows:
            tid = str(r.get('target_id') or '')
            if r.get('kind') == 'group':
                r['display'] = r.get('title') or gnames.get(tid, '')
            else:
                r['display'] = r.get('title') or fnames.get(tid, '')
            r['mode_label'] = '公共' if (r.get('kind') == 'group' and r.get('mode') != 'private') else '私有'
            # 聊过没有 —— 目录行（只是登记了，没消息）
            r['talked'] = 1 if (r.get('msg_count') or r.get('last_at')) else 0
        return ok({'items': rows, 'stats': await store.stats(),
                   'default_persona': cfg.get('default_persona'),
                   'default_provider': cfg.get('default_provider')})

    async def sync_catalog(request):
        """拉取账号的**全部**群聊与好友，登记成会话目录行（默认不启用）。

        为什么要这个：
          原来 sessions 表里只有「收到过消息」的会话，
          于是使用者没法提前配置某个群的称呼/人格/是否启用。
        目录行的 enabled 默认 0 —— 机器人不会在没说过话的群里主动开口，
        要开自己在「会话管理」里点开关。
        """
        b = await _body(request)
        only = (b.get('account_id') or '').strip()
        accounts = list(getattr(mgr, 'accounts', {}).values())
        if only:
            accounts = [a for a in accounts if a.id == only]
        if not accounts:
            return bad('没有已连接的账号')
        stat = {'groups': 0, 'friends': 0, 'new': 0, 'titled': 0,
                'exists': 0, 'accounts': []}
        for acc in accounts:
            ob = getattr(acc, 'ob', None)
            if ob is None or not getattr(ob, 'connected', False):
                stat['accounts'].append({'id': acc.id, 'ok': False, 'why': '未连接'})
                continue
            one = {'id': acc.id, 'ok': True}
            # 群
            try:
                r = await ob.call('get_group_list', timeout=25)
                items = r.get('data') or []
                for g in items:
                    gid = str(g.get('group_id') or '')
                    name = profile.clean_name(g.get('group_name'))
                    if not gid:
                        continue
                    stat['groups'] += 1
                    res = await store.sync_catalog('group', gid, name, acc.id)
                    stat[res] = stat.get(res, 0) + 1
                one['groups'] = len(items)
            except Exception as e:
                one['group_error'] = str(e)[:160]
            # 好友
            try:
                r = await ob.call('get_friend_list', timeout=25)
                items = r.get('data') or []
                for f in items:
                    fid = str(f.get('user_id') or '')
                    name = profile.clean_name(f.get('remark') or f.get('nickname') or '')
                    if not fid:
                        continue
                    stat['friends'] += 1
                    res = await store.sync_catalog('private', fid, name, acc.id)
                    stat[res] = stat.get(res, 0) + 1
                one['friends'] = len(items)
            except Exception as e:
                one['friend_error'] = str(e)[:160]
            stat['accounts'].append(one)
        logbuf.info('api', '会话目录同步：群 %d / 好友 %d，新增 %d'
                    % (stat['groups'], stat['friends'], stat.get('new', 0)))
        return ok(stat)

    async def bulk_sessions(request):
        """批量启用/停用会话。"""
        b = await _body(request)
        enabled = 1 if b.get('enabled') else 0
        ids = b.get('ids')
        if isinstance(ids, str):
            ids = [x for x in ids.split(',') if x]
        ids = [str(x) for x in (ids or [])]
        n = await store.bulk_set_enabled(enabled, ids=ids,
                                         kind=str(b.get('kind') or ''),
                                         account_id=str(b.get('account_id') or ''))
        logbuf.info('api', '批量%s会话 %d 个' % ('启用' if enabled else '停用', n))
        return ok({'changed': n})

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

    # ---------------- 随机挑消息回

    async def random_reply(request):
        """从**已启用的群聊**里随机挑一条消息，让机器人对它回一句。

        「随机挑消息回」跟普通回复不一样：不是回当前这条，
        而是从历史里随机翻一条出来回应 —— 有点「翻牌」的意思。

        范围由设置页决定（features.random_pick.scope）：
          enabled_groups —— 只在「会话管理」里启用了的群聊里挑（默认）
          all_groups     —— 所有群聊
          session        —— 只在指定会话里挑（前端临时切换）

        返回里带 token —— 用户点「发送到 QQ」时凭它把这条回复发出去
        （不重新调模型，页面看到的就是群里会出现的）。
        """
        b = await _body(request)
        sid = (b.get('sid') or '').strip()
        cfg = config.load()
        rp = (cfg.get('features') or {}).get('random_pick') or {}
        if not rp.get('enabled', True):
            return bad('随机挑消息回已关闭（设置 → 能力 → 允许随机挑消息回）')
        scope = (b.get('scope') or rp.get('scope') or 'enabled_groups').strip()
        acct = config.default_account(cfg) or {}

        sql = ("SELECT id, account_id, session_id, kind, target_id, sender_id,"
               " sender_name, text, created_at, msg_id FROM chat_logs"
               " WHERE role='user' AND text<>'' AND recalled=0"
               # 纯媒体占位符没法接话，排除
               " AND text NOT IN ('[图片]','[语音]','[视频]','[表情]','[文件]')"
               " AND text NOT LIKE '[文件:%'"
               " AND text NOT LIKE '%一条消息被撤回%'"
               " AND length(trim(text))>=2")
        args = []
        if scope == 'session' and sid:
            sql += ' AND session_id=?'
            args.append(sid)
        elif scope in ('enabled_groups', 'all_groups'):
            # ★ 用子查询而不是 IN (?,?,…) —— 群多了参数会超 SQLite 上限
            if scope == 'enabled_groups':
                sql += (" AND session_id IN"
                        " (SELECT id FROM sessions WHERE enabled=1 AND kind='group')")
            else:
                sql += " AND session_id IN (SELECT id FROM sessions WHERE kind='group')"
        if rp.get('respect_need_at'):
            bot_cfg = config.resolve_bot_cfg(cfg, {})
            if bot_cfg.get('group_need_at', True):
                prefixes = [p for p in (bot_cfg.get('wake_prefix') or []) if p]
                cond = ("segs LIKE '%\"type\": \"at\"%'"
                        " OR segs LIKE '%\"type\":\"at\"%'")
                if prefixes:
                    cond += ' OR text LIKE ?'
                    args.append(prefixes[0] + '%')
                sql += ' AND (' + cond + ')'
        # 取最近 2000 条做候选池，真正抽哪条交给加权算法
        sql += ' ORDER BY created_at DESC LIMIT 2000'
        cur = await store._db.execute(sql, args)
        rows = [dict(r) for r in await cur.fetchall()]
        picked = _pick_weighted(rows)
        if not picked:
            if scope == 'enabled_groups':
                return bad('没有已启用的群聊可挑 —— 先去「会话管理」把要用的群启用')
            return bad('没有可挑的消息')

        sess = await store.get_session(picked['session_id']) or {}
        # 角色卡片：提供商 / 模型 / 温度 / 输出长度
        card = cards.find(cfg, sess.get('persona_id') or cfg.get('default_card')
                          or cfg.get('default_persona') or '')
        style = (card or {}).get('style') or {}
        cmodel = (card or {}).get('model') or {}
        pid = (sess.get('provider_id') or acct.get('provider_id')
               or cmodel.get('provider_id') or '')
        chain = config.provider_chain(cfg, pid, acct)
        if cmodel.get('model') and chain:
            _pid = cmodel.get('provider_id') or pid
            chain = [dict(p, model=cmodel['model']) if str(p.get('id')) == str(_pid) else p
                     for p in chain]
        if not chain:
            return bad('没有可用的模型提供商')
        persona = config.get_persona(cfg, sess.get('persona_id'), acct, picked['text'])
        system = (persona or {}).get('prompt') or ''
        try:
            ms = await memory.build_prompt(card, picked['text'])
            if ms:
                system = ms
        except Exception:
            pass
        ctx = cfg.get('context') or {}
        try:
            mt = int(style.get('max_tokens') or 0) or int(ctx.get('max_output_tokens') or 4096)
        except Exception:
            mt = 4096
        try:
            temp = float(style.get('temperature')) if style.get('temperature') is not None else 0.8
        except Exception:
            temp = 0.8
        # 被挑中的那条当作用户输入
        msgs = [{'role': 'user', 'content': picked['text']}]
        try:
            reply, used = await llm.chat_chain(
                chain, msgs, system=system, max_tokens=mt, temperature=temp)
        except Exception as e:
            return bad(e)
        try:
            mc = int(style.get('max_chars') or 0)
        except Exception:
            mc = 0
        reply = strip_meta_leak(reply)
        if mc:
            reply = truncate_chars(reply, mc)
        if not ((card or {}).get('style') or {}).get('allow_emoji'):
            reply = strip_emoji(reply)
        # 附上这条消息来自哪个会话，页面上好显示
        title = sess.get('title') or picked.get('target_id') or ''
        # 暂存这次结果：用户点「发送到 QQ」时凭 token 发出去
        token = uuid.uuid4().hex[:16]
        _put_random(token, {
            'account_id': picked.get('account_id') or '',
            'session_id': picked.get('session_id') or '',
            'kind': picked.get('kind') or 'group',
            'target_id': picked.get('target_id') or '',
            'sender_id': picked.get('sender_id') or '',
            'sender_name': picked.get('sender_name') or '',
            'msg_id': picked.get('msg_id') or '',
            'reply': reply,
            'at': int(time.time()),
        })
        return ok({
            'reply': reply,
            'provider': (used or {}).get('id'),
            'token': token,
            'picked': {
                'id': picked['id'],
                'session_id': picked['session_id'],
                'kind': picked['kind'],
                'target_id': picked['target_id'],
                'title': title,
                'sender_id': picked['sender_id'],
                'sender_name': picked['sender_name'],
                'text': picked['text'],
                'created_at': picked['created_at'],
            },
        })

    async def send_random_reply(request):
        """把刚才随机挑出来的那条回复**真的发到 QQ**。

        凭 random_reply 返回的 token 发送（不重新调模型），
        页面看到什么，群里就出现什么。
        """
        b = await _body(request)
        token = str(b.get('token') or '').strip()
        item = _peek_random(token)
        if not item:
            return bad('这次的结果已过期，请重新挑一条')
        kind = item.get('kind') or 'group'
        target = str(item.get('target_id') or '')
        if not target:
            return bad('没有目标会话')
        acc_id = item.get('account_id') or ''
        acc = getattr(mgr, 'accounts', {}).get(acc_id)
        ob = getattr(acc, 'ob', None) if acc else None
        if ob is None or not getattr(ob, 'connected', False):
            return bad('账号没连上，稍后再试')
        text = item.get('reply') or ''
        if not text:
            return bad('没有可发送的内容')
        # 群里 @ 一下被挑中消息的说话人，让对方知道在回他
        mention = item.get('sender_id') if kind == 'group' else None
        try:
            r = await ob.send_text(kind, target, text, mention=mention or None,
                                   quote=item.get('msg_id') or None)
        except Exception as e:
            return bad('发送失败：%s' % str(e)[:200])
        _consume_random(token)
        # 机器人自己的发言进聊天档案 + 喂模型的上下文
        data = (r or {}).get('data') or {}
        msg_id = str(data.get('message_id') or '')
        cfg = config.load()
        acct_cfg = config.find_account(cfg, acc_id) or {}
        nick = acct_cfg.get('nick') or '机器人'
        sid = str((data.get('sender') or {}).get('user_id')
                  or getattr(ob, 'self_id', '') or acct_cfg.get('uin') or '')
        try:
            segs = [{'type': 'text', 'data': {'text': text}}]
            await chats.record(acc_id, kind, target, 'assistant', segs,
                               sender_id=sid, sender_name=nick, msg_id=msg_id,
                               created_at=int(time.time()), media=[],
                               sender_avatar=profile.avatar_url(sid))
            if item.get('session_id'):
                await store.add_message(item['session_id'], 'assistant', text)
        except Exception as e:
            logbuf.warn('api', '记录随机回复的自身消息失败：%s' % str(e)[:120])
        logbuf.info('api', '随机挑回复已发到 %s/%s（msg_id=%s）' % (kind, target, msg_id))
        return ok({'sent': True, 'message_id': msg_id, 'target_id': target,
                   'kind': kind, 'at': mention or ''})

    # ---------------- 上下文预览

    async def preview_context(request):
        """给前端看某个会话现在会怎么拼上下文（不调模型）。"""
        sid = request.query.get('sid') or ''
        cfg = config.load()
        sess = await store.get_session(sid) if sid else None
        acct = config.find_account(cfg, (sess or {}).get('account_id')) or {}
        persona = config.get_persona(cfg, (sess or {}).get('persona_id'), acct)
        provider = config.get_provider(cfg, (sess or {}).get('provider_id'), acct)
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
            dacc = config.default_account(cfg) or {}
            sid = store.session_key('private', '__test__', 'private',
                                    dacc.get('id') or '')
            await store.ensure_session('private', '__test__', title='试聊', mode='private',
                                       account_id=dacc.get('id') or '')
        sess = await store.get_session(sid)
        if not sess:
            return bad('会话不存在', 404)
        acct = config.find_account(cfg, (sess or {}).get('account_id')) or {}
        persona = config.get_persona(cfg, (sess or {}).get('persona_id'), acct, text)
        provider = config.get_provider(cfg, (sess or {}).get('provider_id'), acct)
        chain = config.provider_chain(cfg, (sess or {}).get('provider_id'), acct)
        if not provider or not chain:
            return bad('没有可用的模型提供商')
        system = (persona or {}).get('prompt') or ''
        card = cards.find(cfg, (sess or {}).get('persona_id') or cfg.get('default_card')
                          or cfg.get('default_persona') or '')
        try:
            ms = await memory.build_prompt(card, text)
            if ms:
                system = ms
        except Exception:
            pass
        await store.add_message(sid, 'user', text, name='测试')
        tools, runner = llm.web_tools(cfg)
        try:
            sys2, messages, meta = await compress.build_context(cfg, sid, system, provider)
            try:
                exs = await memory.pick_examples(card, text, 2)
                if exs:
                    few = []
                    for e in reversed(exs):
                        few = [{'role': 'user', 'content': e['user']},
                               {'role': 'assistant', 'content': e['assistant']}] + few
                    messages = few + messages
            except Exception:
                pass
            vis = (cfg.get('features') or {}).get('vision') or {}
            if b.get('images') and vis.get('enabled'):
                n = await attach_images(messages, b.get('images'),
                                        int(vis.get('max_images') or 3))
                if n:
                    meta['images'] = n
            reply, used = await llm.chat_chain(
                chain, messages, system=sys2,
                max_tokens=int((cfg.get('context') or {}).get('max_output_tokens') or 4096),
                tools=tools, tool_runner=runner)
            # 卡片的字数上限（和真实回复同一套逻辑）
            card = cards.find(cfg, (sess or {}).get('persona_id')
                              or cfg.get('default_card') or cfg.get('default_persona') or '')
            try:
                mc = int(((card or {}).get('style') or {}).get('max_chars') or 0)
            except Exception:
                mc = 0
            reply = strip_meta_leak(reply)
            if mc:
                reply = truncate_chars(reply, mc)
            if not ((card or {}).get('style') or {}).get('allow_emoji'):
                reply = strip_emoji(reply)
        except Exception as e:
            return bad(e)
        await store.add_message(sid, 'assistant', reply)
        meta['provider'] = (used or {}).get('id')
        return ok({'reply': reply, 'sid': sid, 'meta': meta,
                   'messages': len(messages)})

    # ---------------- 聊天记录（全量档案）

    async def chat_sessions(request):
        q = request.query
        rows = await chats.list_sessions(
            account_id=q.get('account_id') or '',
            kind=q.get('kind') or '',
            keyword=q.get('kw') or '',
            limit=int(q.get('limit') or 200))
        # 会话标题：群名/对方昵称 + 头像
        #
        # ★ 之前这里只读 bot._group_names，而那个缓存**从来没有被填过**
        #   （fill_group_names 没有调用点）→ 群名一直是裸群号。
        #   现在名字由 Bot.group_display / friend_display 提供，
        #   拿不到时退回 QQ 号，头像按 QQ 号从 qlogo 取。
        # 本机托管的真实群头像（从 QQ 客户端缓存捞出来的）优先
        local = await group_avatar.local_map()
        for r in rows:
            kind = str(r.get('kind') or '')
            tid = str(r.get('target_id') or '')
            if kind == 'group':
                name, av = bot.group_display(tid)
                p = local.get(tid)
                if p and os.path.isfile(p):
                    # 绝对路径交给插件层转成预览 URL
                    r['avatar_path'] = p
                    av = ''
            else:
                name, av = bot.friend_display(tid)
            r['display'] = name or tid
            r['avatar'] = av
        return ok({'items': rows})

    async def chat_messages(request):
        q = request.query
        sid = q.get('session_id') or ''
        if not sid:
            return bad('缺少 session_id')
        rows = await chats.list_messages(
            sid,
            before_id=int(q.get('before_id') or 0),
            limit=int(q.get('limit') or 50),
            keyword=q.get('kw') or '')
        return ok({'items': rows, 'count': len(rows)})

    async def chat_forward(request):
        """合并转发展开：按 forward id 取节点内容。

        节点里的图片会落盘到媒体目录（QQ 的 rkey 会过期），
        结果按 forward_id 缓存，第二次展开直接命中缓存。
        """
        q = request.query
        fid = str(q.get('id') or '')
        if not fid:
            return bad('缺少 id')
        acct = str(q.get('account_id') or '')
        try:
            data = await forward.expand(bot, fid, account_id=acct)
        except Exception as e:
            return bad(str(e)[:200])
        return ok(data)

    async def chat_session_ui(request):
        """会话 UI 状态：置顶 / 免打扰 / 已读位置 / 草稿。"""
        b = await _body(request)
        sid = str(b.get('session_id') or '')
        if not sid:
            return bad('缺少 session_id')
        try:
            data = await chats.save_session_ui(
                sid,
                pinned=b.get('pinned'),
                muted=b.get('muted'),
                last_read_id=b.get('last_read_id'),
                draft=b.get('draft'))
        except Exception as e:
            return bad(str(e)[:200])
        return ok(data)

    async def chat_recall(request):
        """撤回消息：调 OneBot delete_msg，成功后在库里打撤回标记。"""
        b = await _body(request)
        mid = str(b.get('msg_id') or '')
        if not mid:
            return bad('缺少 msg_id')
        try:
            r = await bot.recall(mid)
        except Exception as e:
            return bad(str(e)[:200])
        return ok(r)

    async def chat_stats(request):
        account_id = request.query.get('account_id') or ''
        cfg = config.load()
        root = chats.media_root(cfg)
        usage = media.dir_usage(root)
        disk = media.disk_free(root)
        st = await chats.stats(account_id)
        used_pct = 0
        if disk.get('total'):
            used_pct = int(disk['used'] * 100 / disk['total'])
        return ok({
            'chat': st,
            'media': usage,
            'disk': dict(disk, used_pct=used_pct),
            'media_dir': root,
        })

    async def chat_export(request):
        q = request.query
        doc, name = await chats.export(
            account_id=q.get('account_id') or '',
            session_id=q.get('session_id') or '',
            date_from=int(q.get('from') or 0),
            date_to=int(q.get('to') or 0))
        body = json.dumps(doc, ensure_ascii=False, indent=2).encode('utf-8')
        # 文件名只有 ASCII，去掉引号 —— Content-Disposition 里的引号没转义会让
        # aiohttp 抛 ValueError（500）
        safe = ''.join(ch for ch in name if ch.isalnum() or ch in '-_.').strip() or 'chat-export.json'
        # ★ content_type 里不能带 charset —— aiohttp 会抛
        #   "charset must not be in content_type argument"（这是 500 的真正原因）
        return web.Response(
            body=body,
            content_type='application/json',
            charset='utf-8',
            headers={'Content-Disposition': 'attachment; filename="%s"' % safe})

    async def chat_purge_media(request):
        """只清媒体文件，保留消息文本（永久保留是明确要求）。"""
        b = await _body(request)
        if b.get('confirm') is not True:
            return bad('需要 confirm=true')
        r = await chats.purge_media_only(
            account_id=b.get('account_id') or '',
            session_id=b.get('session_id') or '',
            date_from=int(b.get('from') or 0),
            date_to=int(b.get('to') or 0))
        return ok(r)

    async def chat_media_check(request):
        return ok(await chats.check_media_consistency())

    # ---------------- 查询（按用户 / 撤回状态 / 消息类型，可叠加）

    async def chat_query(request):
        q = request.query
        r = await chats.query_messages(
            sender=q.get('sender') or '',
            recalled=q.get('recalled') or '',
            kind=q.get('kind') or '',
            keyword=q.get('kw') or '',
            session_id=q.get('session_id') or '',
            account_id=q.get('account_id') or '',
            date_from=int(q.get('from') or 0),
            date_to=int(q.get('to') or 0),
            limit=int(q.get('limit') or 50),
            before_id=int(q.get('before_id') or 0))
        r['count'] = len(r.get('items') or [])
        return ok(r)

    async def chat_senders(request):
        try:
            lim = int(request.query.get('limit') or 200)
        except Exception:
            lim = 200
        return ok({'items': await chats.query_senders(
            keyword=request.query.get('kw') or '', limit=lim)})

    # ---------------- 一键清空会话

    async def chat_clear_session(request):
        b = await _body(request)
        if b.get('confirm') is not True:
            return bad('需要 confirm=true')
        sid = str(b.get('session_id') or '').strip()
        if not sid:
            return bad('缺少 session_id')
        try:
            r = await chats.clear_session(
                sid,
                with_media=bool(b.get('with_media')),
                account_id=str(b.get('account_id') or ''))
        except ValueError as e:
            return bad(str(e))
        return ok(r)

    # ---------------- 媒体库

    async def chat_media_list(request):
        q = request.query
        r = await chats.list_media(
            kind=q.get('kind') or '',
            sender=q.get('sender') or '',
            keyword=q.get('kw') or '',
            session_id=q.get('session_id') or '',
            account_id=q.get('account_id') or '',
            limit=int(q.get('limit') or 100),
            offset=int(q.get('offset') or 0),
            sort=q.get('sort') or 'time')
        # 统计只在首屏/显式要求时算：翻页时不必每次 GROUP BY 全表
        want_stats = (q.get('with_stats') or '') not in ('0', 'false')
        if want_stats and int(q.get('offset') or 0) == 0:
            r['stats'] = await chats.media_stats(q.get('account_id') or '')
        return ok(r)

    async def chat_media_stats(request):
        return ok(await chats.media_stats(request.query.get('account_id') or ''))

    async def chat_thumb(request):
        """按需生成缩略图，返回缓存文件的绝对路径。

        图片解码是同步 CPU 活，丢线程池，别卡住收消息的循环。
        """
        rel = request.query.get('rel') or ''
        try:
            size = int(request.query.get('size') or 320)
        except Exception:
            size = 320
        try:
            path = await asyncio.to_thread(chats.ensure_thumb, rel, size)
        except Exception as e:
            logbuf.debug('chat', '缩略图接口失败：%s' % str(e)[:80])
            path = ''
        return ok({'path': path or ''})

    async def chat_media_delete(request):
        b = await _body(request)
        if b.get('confirm') is not True:
            return bad('需要 confirm=true')
        ids = b.get('ids') or []
        rels = b.get('rels') or []
        r = await chats.delete_media(
            ids=ids if isinstance(ids, list) else [],
            rels=rels if isinstance(rels, list) else [],
            kind=str(b.get('kind') or ''),
            session_id=str(b.get('session_id') or ''))
        return ok(r)

    async def chat_media_transcode(request):
        """把 HEVC / AMR 之类转成浏览器能播的格式。

        默认同步（兼容旧前端）；async=true 时起后台任务，立即返回 job id，
        前端轮询 /api/chat/media/task 看进度并可取消 —— 大视频不会撞 15s 超时。
        """
        b = await _body(request)
        ids = b.get('ids') or []
        if not isinstance(ids, list):
            ids = []
        if not ids:
            ids = [x['id'] for x in await chats.media_need_transcode()]
        if b.get('async'):
            jid = await _start_transcode_job(ids)
            return ok({'job': jid, 'total': len(ids)})
        r = await chats.transcode_media(ids)
        return ok(r)

    async def chat_media_task(request):
        """转码任务进度 / 取消。"""
        if request.method == 'POST':
            b = await _body(request)
            jid = str(b.get('id') or '')
            job = _media_jobs.get(jid)
            if not job:
                return bad('任务不存在')
            if b.get('cancel'):
                job['cancel'] = True
            return ok(_job_public(job))
        jid = request.query.get('id') or ''
        job = _media_jobs.get(jid)
        if not job:
            return bad('任务不存在')
        return ok(_job_public(job))

    async def chat_media_reindex(request):
        return ok(await chats.rebuild_media_index())

    async def chat_media_repair(request):
        """修复媒体引用（转码后消息里还指向旧文件名）。"""
        return ok(await chats.repair_media_refs())

    # ---------------- 工具链

    async def tools_get(request):
        cfg = config.load()
        t = cfg.get('tools') or {}
        ws = tools.usage()
        ws['max_mb'] = int((t.get('workspace') or {}).get('max_mb') or 20)
        return ok({'tools': tools.public_list(cfg), 'workspace': ws,
                   'enabled': tools.enabled_map(cfg)})

    async def tools_save(request):
        b = await _body(request)
        cfg = config.load()
        t = cfg.get('tools') or {}
        if isinstance(b.get('enabled'), dict):
            t['enabled'] = {k: bool(v) for k, v in b['enabled'].items()}
        if isinstance(b.get('workspace'), dict) and 'max_mb' in b['workspace']:
            ws = t.get('workspace') or {}
            try:
                ws['max_mb'] = max(1, min(1024, int(b['workspace']['max_mb'] or 20)))
            except Exception:
                ws['max_mb'] = 20
            t['workspace'] = ws
        cfg['tools'] = t
        config.save(cfg)
        return ok({'status': True})

    async def tools_stats(request):
        return ok(tools.stats())

    async def tools_test(request):
        b = await _body(request)
        tid = str(b.get('id') or '')
        if not tid:
            return bad('缺少工具 id')
        try:
            res = await tools.run_manual(tid, b.get('args') or {})
        except Exception as e:
            return bad(str(e)[:240])
        return ok({'result': res})

    async def tools_fs(request):
        if request.method == 'GET':
            try:
                return ok(tools.list_dir(request.query.get('path') or ''))
            except Exception as e:
                return bad(str(e)[:200])
        b = await _body(request)
        act = str(b.get('action') or '')
        path = str(b.get('path') or '')
        try:
            if act == 'list':
                r = tools.list_dir(path)
            elif act == 'read':
                r = tools.read_text(path)
            elif act == 'write':
                r = tools.write_text(path, b.get('content') or '')
            elif act == 'mkdir':
                r = tools.mkdir(path)
            elif act == 'delete':
                r = tools.delete(path)
            else:
                return bad('未知操作')
        except Exception as e:
            return bad(str(e)[:240])
        return ok(r)

    # ---------------- 用户面板（菜单 / 文本库 / 图片库）

    async def panel_get(request):
        cfg = config.load()
        sec = cfg.get('panel') or {}
        # 老配置补齐「运势等级」字段并落盘，前端与 bot 读到的是同一份
        if panel.ensure_defaults(sec):
            panel.save_section(sec)
        images = {}
        for p in (sec.get('image_pools') or []):
            pid = str(p.get('id') or '')
            d = panel.images_dir(pid)
            try:
                names = sorted(os.listdir(d))
            except Exception:
                names = []
            out = []
            for n in names:
                fp = os.path.join(d, n)
                if os.path.isfile(fp):
                    out.append({'name': n, 'abs': fp,
                                'size': os.path.getsize(fp)})
            images[pid] = out
        bt = (cfg.get('features') or {}).get('web_search') or {}
        tools = [{'id': 'web_search', 'name': '联网搜索', 'builtin': True,
                  'desc': '按关键词搜索网页（AI 调用）',
                  'enabled': bool(bt.get('enabled'))}]
        return ok({'panel': sec, 'images': images, 'builtin_tools': tools,
                   'workspace': ''})

    async def panel_save(request):
        b = await _body(request)
        sec = b.get('panel') if isinstance(b.get('panel'), dict) else b
        if not isinstance(sec, dict) or not sec:
            return bad('缺少面板配置')
        panel.ensure_defaults(sec)
        panel.save_section(sec)
        return ok({'status': True})

    async def panel_preview(request):
        b = await _body(request)
        sec = config.load().get('panel') or {}
        mode = str(b.get('mode') or 'menu')
        if mode == 'menu':
            return ok({'text': panel.render_menu(sec, int(b.get('page') or 0))})
        name = str(b.get('id') or b.get('name') or '')
        item = next((x for x in panel._items(sec) if x.get('id') == name), None) \
            or panel.match_item(sec, name)
        if not item:
            return bad('功能项不存在')
        image = ''
        text, image_path = await panel.build_reply(
            sec, item, str(b.get('uid') or '10000'),
            str(b.get('nick') or '测试用户'), b.get('date') or None)
        if image_path and os.path.isfile(image_path):
            image = image_path
        return ok({'text': text, 'image': image})

    async def panel_generate(request):
        b = await _body(request)
        pid = str(b.get('pool_id') or '')
        if not pid:
            return bad('缺少 pool_id')
        try:
            n = await panel.generate_into_pool(pid, b.get('count'))
        except Exception as e:
            return bad(str(e)[:240])
        return ok({'added': n})

    async def panel_image_upload(request):
        b = await _body(request)
        pid = str(b.get('pool_id') or '')
        raw = str(b.get('data') or '')
        if not pid or not raw:
            return bad('缺少参数')
        if raw.startswith('data:') and ',' in raw:
            raw = raw.split(',', 1)[1]
        try:
            data = base64.b64decode(raw)
        except Exception:
            return bad('图片数据不合法')
        if len(data) > 12 * 1024 * 1024:
            return bad('图片超过 12MB')
        name = panel.append_image(pid, b.get('name') or 'image.jpg', data)
        cfg = config.load()
        sec = cfg.get('panel') or {}
        for p in (sec.get('image_pools') or []):
            if p.get('id') == pid:
                p.setdefault('items', []).append(name)
                break
        panel.save_section(sec)
        return ok({'name': name,
                   'path': os.path.join(panel.images_dir(pid), name)})

    # ---------------- 记忆库
    async def memory_map(request):
        q = request.query
        cid = (q.get('card_id') or '').strip()
        cfg = config.load()
        if not cid:
            cid = cfg.get('default_card') or cfg.get('default_persona') or ''
        card = cards.find(cfg, cid)
        if not card:
            return bad('卡片不存在', 404)
        acct = config.default_account(cfg) or {}
        await memory.ensure_seeded(card, acct.get('id') or '')
        return ok(await memory.map_data(cid, q.get('scope_type') or '',
                                        q.get('scope_id') or ''))

    async def memory_item(request):
        it = await memory.get_item((request.query.get('id') or '').strip())
        if not it:
            return bad('记忆不存在', 404)
        return ok(it)

    async def memory_save(request):
        b = await _body(request)
        item = b.get('item') or b
        if not item.get('content'):
            return bad('缺少内容')
        iid = await memory.save_item(item)
        return ok({'id': iid})

    async def memory_delete(request):
        b = await _body(request)
        iid = str(b.get('id') or '').strip()
        if not iid:
            return bad('缺少 id')
        await memory.delete_item(iid, hard=bool(b.get('hard')))
        return ok({'deleted': iid})

    async def memory_pin(request):
        b = await _body(request)
        iid = str(b.get('id') or '').strip()
        if not iid:
            return bad('缺少 id')
        cur = await store._db.execute('UPDATE memory_items SET pinned=? WHERE id=?',
                                      (1 if b.get('pinned') else 0, iid))
        await store._db.commit()
        return ok({'id': iid, 'pinned': bool(b.get('pinned')), 'updated': cur.rowcount})

    async def memory_seed(request):
        b = await _body(request)
        cfg = config.load()
        cid = str(b.get('card_id') or cfg.get('default_card') or '')
        card = cards.find(cfg, cid)
        if not card:
            return bad('卡片不存在', 404)
        acct = config.default_account(cfg) or {}
        n = await memory.ensure_seeded(card, acct.get('id') or '')
        return ok({'card_id': cid, 'seeded': n})

    async def memory_tile(request):
        q = request.query
        cid = (q.get('card_id') or '').strip()
        if not cid:
            return bad('缺少 card_id')
        try:
            tx, ty = int(q.get('tx') or 0), int(q.get('ty') or 0)
        except Exception:
            tx, ty = 0, 0
        return ok({'items': await memory.tile(cid, tx, ty,
                                              scope_type=q.get('scope_type') or '',
                                              scope_id=q.get('scope_id') or '')})

    async def memory_search(request):
        q = request.query
        cid = (q.get('card_id') or '').strip()
        if not cid:
            return bad('缺少 card_id')
        return ok({'items': await memory.search(cid, q.get('q') or '',
                                                scope_type=q.get('scope_type') or '',
                                                scope_id=q.get('scope_id') or '')})

    async def memory_triggers(request):
        cid = (request.query.get('card_id') or '').strip()
        if not cid:
            return bad('缺少 card_id')
        return ok({'items': await memory.list_trigger_items(cid)})

    async def memory_bulk(request):
        b = await _body(request)
        cid = str(b.get('card_id') or '').strip()
        items = b.get('items') or []
        if not cid or not isinstance(items, list):
            return bad('缺少 card_id 或 items')
        replace_type = str(b.get('replace_type') or '').strip()
        if replace_type:
            await store._db.execute(
                'UPDATE memory_items SET archived=1,updated_at=? WHERE card_id=? AND type=? AND archived=0',
                (int(time.time()), cid, replace_type))
            await store._db.commit()
        n = 0
        for it in items:
            if not isinstance(it, dict):
                continue
            it = dict(it)
            it['card_id'] = cid
            await memory.save_item(it)
            n += 1
        return ok({'saved': n})

    async def memory_consolidate(request):
        b = await _body(request)
        cid = str(b.get('card_id') or '').strip()
        if not cid:
            return bad('缺少 card_id')
        return ok(await memory.consolidate(cid))

    async def memory_stats(request):
        cid = (request.query.get('card_id') or '').strip()
        return ok(await memory.stats(cid))

    app.router.add_get('/api/memory/map', memory_map)
    app.router.add_get('/api/memory/item', memory_item)
    app.router.add_post('/api/memory/save', memory_save)
    app.router.add_post('/api/memory/delete', memory_delete)
    app.router.add_post('/api/memory/pin', memory_pin)
    app.router.add_post('/api/memory/seed', memory_seed)
    app.router.add_get('/api/memory/stats', memory_stats)
    app.router.add_get('/api/memory/search', memory_search)
    app.router.add_get('/api/memory/tile', memory_tile)
    app.router.add_post('/api/memory/consolidate', memory_consolidate)
    app.router.add_post('/api/memory/bulk', memory_bulk)
    app.router.add_get('/api/memory/triggers', memory_triggers)

    app.router.add_get('/api/status', status)
    app.router.add_get('/api/config', get_config)
    app.router.add_post('/api/config', post_config)

    app.router.add_get('/api/accounts', get_accounts)
    app.router.add_post('/api/accounts', post_accounts)

    app.router.add_get('/api/providers', get_providers)
    app.router.add_post('/api/providers', post_providers)
    app.router.add_post('/api/providers/delete', del_provider)
    app.router.add_post('/api/providers/test', test_provider)
    app.router.add_get('/api/providers/models', provider_models)

    app.router.add_get('/api/personas', get_personas)
    app.router.add_post('/api/personas', post_personas)
    app.router.add_post('/api/personas/delete', del_persona)

    app.router.add_get('/api/cards', get_cards)
    app.router.add_post('/api/cards', post_cards)
    app.router.add_post('/api/cards/delete', del_card)
    app.router.add_post('/api/cards/clone', clone_card)
    app.router.add_post('/api/cards/import', import_card)
    app.router.add_get('/api/cards/export', export_card)

    # ★ catalog / bulk 必须注册在 /api/sessions/{sid} 前面，
    #   否则 {sid} 会把 /api/sessions/catalog 当成会话 id 吃掉。
    app.router.add_post('/api/sessions/catalog', sync_catalog)
    app.router.add_post('/api/sessions/bulk', bulk_sessions)
    app.router.add_get('/api/sessions', get_sessions)
    app.router.add_get('/api/sessions/{sid}', get_session)
    app.router.add_post('/api/sessions/{sid}', post_session)
    app.router.add_post('/api/sessions/{sid}/clear', clear_session)
    app.router.add_post('/api/sessions/delete', del_session)

    app.router.add_get('/api/chat/sessions', chat_sessions)
    app.router.add_get('/api/chat/messages', chat_messages)
    app.router.add_get('/api/chat/stats', chat_stats)
    app.router.add_get('/api/chat/export', chat_export)
    app.router.add_post('/api/chat/recall', chat_recall)
    app.router.add_post('/api/chat/session-ui', chat_session_ui)
    app.router.add_get('/api/chat/forward', chat_forward)
    app.router.add_post('/api/chat/purge-media', chat_purge_media)
    app.router.add_get('/api/chat/media-check', chat_media_check)

    app.router.add_get('/api/chat/query', chat_query)
    app.router.add_get('/api/chat/senders', chat_senders)
    app.router.add_post('/api/chat/session-clear', chat_clear_session)
    app.router.add_get('/api/chat/media', chat_media_list)
    app.router.add_get('/api/chat/media/stats', chat_media_stats)
    app.router.add_get('/api/chat/thumb', chat_thumb)
    app.router.add_route('*', '/api/chat/media/task', chat_media_task)
    # 用户面板
    app.router.add_route('*', '/api/panel', lambda r: panel_get(r) if r.method == 'GET' else panel_save(r))
    app.router.add_post('/api/panel/preview', panel_preview)
    app.router.add_post('/api/panel/generate', panel_generate)
    app.router.add_post('/api/panel/image', panel_image_upload)
    # 工具链
    app.router.add_route('*', '/api/tools', lambda r: tools_get(r) if r.method == 'GET' else tools_save(r))
    app.router.add_post('/api/tools/test', tools_test)
    app.router.add_get('/api/tools/stats', tools_stats)
    app.router.add_route('*', '/api/tools/fs', tools_fs)
    app.router.add_post('/api/chat/media/delete', chat_media_delete)
    app.router.add_post('/api/chat/media/transcode', chat_media_transcode)
    app.router.add_post('/api/chat/media/reindex', chat_media_reindex)
    app.router.add_post('/api/chat/media/repair', chat_media_repair)

    app.router.add_get('/api/logs', get_logs)
    app.router.add_get('/api/stats', get_stats)
    app.router.add_post('/api/chat/random_reply', random_reply)
    app.router.add_post('/api/chat/random_reply/send', send_random_reply)
    app.router.add_get('/api/context', preview_context)
    app.router.add_get('/api/tools/search', tools_search)
    app.router.add_post('/api/test/chat', test_chat)

    return app
