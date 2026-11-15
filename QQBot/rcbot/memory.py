# -*- coding: utf-8 -*-
"""角色记忆库：把卡片字段迁进 memory_items，按类型注入，供星空视图读坐标。"""
import asyncio
import difflib
import hashlib
import json
import math
import os
import random
import re
import time
import uuid

from . import config, logbuf, store

_GOLDEN = math.pi * (3 - math.sqrt(5))
_TYPE_POS = {'fact': (0, 470), 'event': (300, 400), 'relationship': (-320, 400)}
# 抽取写入串行化：避免同一条消息并发时重复入库
_EXTRACT_LOCK = asyncio.Lock()


def _now():
    return int(time.time())


def new_id():
    return 'mem_' + uuid.uuid4().hex[:12]


def _hash(seed, text):
    h = hashlib.sha1((str(seed) + '|' + str(text)).encode('utf-8')).hexdigest()
    return int(h[:12], 16) / float(0xFFFFFFFFFFFF)


def _json(v, default):
    try:
        return json.loads(v) if isinstance(v, str) else (v if v is not None else default)
    except Exception:
        return default


# ---------------------------------------------------------------- 迁移

def _split_sections(prompt):
    """把「【外貌】…【日常】…」拆成 dict；没有标题就整段当 persona。"""
    text = str(prompt or '').strip()
    if not text:
        return {}
    parts = re.split(r'\n(?=【[^】]{1,20}】)', text)
    out = {}
    for p in parts:
        m = re.match(r'^【([^】]+)】\s*', p)
        if not m:
            out.setdefault('_head', '')
            out['_head'] = (out['_head'] + '\n' + p).strip()
            continue
        key = m.group(1).strip()
        body = p[m.end():].strip()
        out[key] = body
    return out


_APPEARANCE_KEYS = ('外貌', '形象', '外观')
_PERSONA_KEYS = ('两种状态', '怎么说话', '说话方式', '性格')
_TABOO_KEYS = ('边界', '禁则', '不要做')


def _layout(clusters):
    """按类型分星座：主星按黄金角排布，卫星绕主星螺旋散开。返回 {cluster: (x,y)}。"""
    centers = {}
    n = max(1, len(clusters))
    for i, cl in enumerate(clusters):
        r = 0 if n == 1 else 240 + 260 * math.sqrt(i / n)
        a = i * _GOLDEN
        centers[cl] = (round(math.cos(a) * r, 1), round(math.sin(a) * r, 1))
    return centers


def _sat_pos(center, idx, seed):
    jitter = _hash(seed, idx)
    ang = idx * _GOLDEN + (jitter - 0.5) * 0.8
    rad = 26 + 15 * math.sqrt(idx) + jitter * 6
    return (round(center[0] + math.cos(ang) * rad, 1),
            round(center[1] + math.sin(ang) * rad, 1))


async def ensure_seeded(card, account_id=''):
    """卡片字段 → 记忆条目（只迁移一次）。"""
    card = card or {}
    cid = str(card.get('id') or '')
    if not cid:
        return 0
    cur = await store._db.execute('SELECT COUNT(*) AS c FROM memory_items WHERE card_id=?', (cid,))
    row = await cur.fetchone()
    if row and int(row['c']) > 0:
        return 0
    now = _now()
    items = []

    def add(type_, mode, content, meta=None, keys=None, importance=0.6,
            source='canon', scope_type='global', scope_id='', pinned=0,
            sort_order=0):
        content = str(content or '').strip()
        if not content:
            return
        items.append({
            'id': new_id(), 'card_id': cid, 'account_id': account_id,
            'scope_type': scope_type, 'scope_id': scope_id,
            'type': type_, 'mode': mode, 'content': content,
            'meta': json.dumps(meta or {}, ensure_ascii=False),
            'keys': json.dumps(list(keys or []), ensure_ascii=False),
            'importance': float(importance), 'confidence': 1.0,
            'source': source, 'sort_order': int(sort_order or 0),
            'created_at': now, 'updated_at': now,
            'pinned': int(pinned), 'state': 'active',
            'star_x': 0, 'star_y': 0, 'is_main': 0, 'parent_id': '',
            'cluster': type_, 'tile_x': 0, 'tile_y': 0,
        })

    name = card.get('name') or '角色'
    tagline = card.get('tagline') or ''
    add('profile', 'always', '%s。%s' % (name, tagline), importance=0.9, pinned=1)

    prompt = str(card.get('prompt') or '')
    secs = _split_sections(prompt)
    appearance = ''
    persona_parts = []
    for k, v in secs.items():
        if k in _APPEARANCE_KEYS:
            appearance = v
        elif k in _PERSONA_KEYS:
            persona_parts.append('【%s】%s' % (k, v))
        elif k.startswith('_'):
            continue
        else:
            add('canon', 'keyed', '【%s】%s' % (k, v), keys=[k], importance=0.55)
    if appearance:
        add('appearance', 'always', appearance,
            meta={'avatar': card.get('avatar') or '', 'cover': card.get('cover') or '',
                  'portrait': card.get('portrait') or '', 'theme': card.get('theme') or {}},
            importance=0.85)
    persona = '\n\n'.join(persona_parts) or prompt
    add('persona', 'always', persona, importance=0.9, pinned=1)

    for i, t in enumerate(card.get('taboos') or []):
        add('taboo', 'always', t, importance=0.7, sort_order=i)

    style = card.get('style') or {}
    add('style', 'config', json.dumps(style, ensure_ascii=False),
        meta={'kind': 'style'}, importance=0.3)
    model = card.get('model') or {}
    add('model', 'config', '%s / %s' % (model.get('provider_id') or '', model.get('model') or ''),
        meta={'kind': 'model', 'model': model}, importance=0.3)

    for i, g in enumerate(card.get('greetings') or []):
        add('greeting', 'session', g, importance=0.5, sort_order=i)
    for i, ex in enumerate(card.get('examples') or []):
        if not isinstance(ex, dict):
            continue
        u, a = str(ex.get('user') or ''), str(ex.get('assistant') or '')
        if u or a:
            add('example', 'fewshot', '%s\n%s' % (u, a),
                meta={'user': u, 'assistant': a}, keys=[u[:12]], importance=0.5, sort_order=i)
    for i, kw in enumerate(card.get('keywords') or []):
        if not isinstance(kw, dict):
            continue
        add('trigger', 'config', str(kw.get('reply') or ''),
            meta={'match': kw.get('match') or '', 'mode': kw.get('mode') or 'contains',
                  'require_at': kw.get('require_at') is not False,
                  'enabled': kw.get('enabled') is not False},
            importance=0.4, sort_order=i)
    for lb in card.get('lorebook') or []:
        if not isinstance(lb, dict):
            continue
        add('canon', 'keyed', lb.get('content') or '', keys=lb.get('keys') or [],
            importance=0.6, pinned=1 if lb.get('always') else 0)

    # 布局：主星 + 卫星
    clusters = []
    for it in items:
        cl = it['type']
        if cl not in clusters:
            clusters.append(cl)
    centers = _layout(clusters)
    per = {}
    main_by_cluster = {}
    for it in items:
        cl = it['type']
        # 每个星座第一颗（或 pinned）当主星
        if cl not in main_by_cluster:
            it['is_main'] = 1
            it['star_x'], it['star_y'] = centers[cl]
            it['cluster'] = cl
            main_by_cluster[cl] = it['id']
            per[cl] = 1
        else:
            idx = per.get(cl, 1)
            per[cl] = idx + 1
            x, y = _sat_pos(centers[cl], idx, it['id'])
            it['star_x'], it['star_y'] = x, y
            it['cluster'] = cl
            it['parent_id'] = main_by_cluster[cl]
        it['tile_x'] = int(it['star_x'] // 512)
        it['tile_y'] = int(it['star_y'] // 512)

    sql = ('INSERT INTO memory_items(id,card_id,account_id,scope_type,scope_id,subject_id,'
           'type,mode,content,meta,keys,importance,confidence,source,sort_order,created_at,'
           'updated_at,pinned,state,star_x,star_y,is_main,parent_id,cluster,tile_x,tile_y) '
           'VALUES(?,?,?,?,?,"",?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
    for it in items:
        await store._db.execute(sql, (
            it['id'], it['card_id'], it['account_id'], it['scope_type'], it['scope_id'],
            it['type'], it['mode'], it['content'], it['meta'], it['keys'],
            it['importance'], it['confidence'], it['source'], it.get('sort_order', 0),
            it['created_at'], it['updated_at'], it['pinned'], it['state'],
            it['star_x'], it['star_y'], it['is_main'], it['parent_id'], it['cluster'],
            it['tile_x'], it['tile_y']))
    await store._db.commit()
    logbuf.info('memory', '卡片 %s 已迁移 %d 条记忆' % (cid, len(items)))
    return len(items)


# ---------------------------------------------------------------- 读取

def _hit_score(text, keys):
    low = str(text or '').lower()
    hit = 0
    for k in keys or []:
        ks = str(k).strip().lower()
        if ks and ks in low:
            hit += len(ks)
    return hit


def _brightness(r, now):
    imp = float(r.get('importance') or 0.5)
    conf = float(r.get('confidence') or 1)
    last = r.get('last_used_at') or r.get('created_at') or now
    age = max(0, now - last) / 86400.0
    rec = 0.5 ** (age / 45.0)
    use = min(1.0, math.log1p(r.get('use_count') or 0) / math.log(20))
    pin = 1.0 if r.get('pinned') else 0.0
    return max(0.0, min(1.0, 0.45 * imp + 0.25 * rec + 0.15 * use + 0.10 * conf + 0.05 * pin))


async def refresh_states(card_id):
    """按亮度更新 正常/休眠/垃圾场；垃圾场移到边缘，不删除。"""
    now = _now()
    cur = await store._db.execute(
        'SELECT id,importance,confidence,pinned,use_count,last_used_at,created_at,state,'
        'star_x,star_y FROM memory_items WHERE card_id=? AND archived=0', (card_id,))
    rows = [dict(r) for r in await cur.fetchall()]
    changed = 0
    for r in rows:
        b = _brightness(r, now)
        if r.get('pinned'):
            st = 'active'
        elif b < 0.12:
            st = 'junk'
        elif b < 0.22:
            st = 'dormant'
        else:
            st = 'active'
        x, y = r['star_x'], r['star_y']
        if st == 'junk' and x > -650:
            x, y = round(-1200 + _hash(r['id'], 'junk') * 500, 1), \
                round(-450 + _hash(r['id'], 'jy') * 900, 1)
        if st != r.get('state') or x != r['star_x'] or y != r['star_y']:
            await store._db.execute(
                'UPDATE memory_items SET state=?,star_x=?,star_y=?,tile_x=?,tile_y=? WHERE id=?',
                (st, x, y, int(x // 512), int(y // 512), r['id']))
            changed += 1
    if changed:
        await store._db.commit()
    return changed


async def build_prompt(card, text='', scope_type='', scope_id=''):
    """从记忆库拼 system prompt；没有记忆则返回 None（调用方回退卡片）。"""
    cid = str((card or {}).get('id') or '')
    if not cid:
        return None
    try:
        cur = await store._db.execute(
            'SELECT * FROM memory_items WHERE card_id=? AND archived=0', (cid,))
        rows = [dict(r) for r in await cur.fetchall()]
    except Exception:
        return None
    if not rows:
        return None
    always = [r for r in rows if r['mode'] == 'always' and r['type'] != 'style']
    parts = [r['content'] for r in always if r['content']]
    # 0.3% 概率从垃圾场里「突然想起」一条
    if random.random() < 0.003:
        junk = [r for r in rows if r.get('state') == 'junk'
                and (r.get('scope_type') == 'global'
                     or (r.get('scope_type') == scope_type
                         and (not scope_id or r.get('scope_id') == scope_id)))]
        if junk:
            j = random.choice(junk)
            parts.append('【你突然想起】%s' % j['content'])
            await store._db.execute(
                'UPDATE memory_items SET state="dormant",awaken_count=awaken_count+1,'
                'last_awaken_at=?,last_used_at=? WHERE id=?',
                (_now(), _now(), j['id']))
            await store._db.commit()
            logbuf.info('memory', '垃圾场唤醒：%s' % str(j['content'])[:40])
    # 风格约束
    for r in rows:
        if r['type'] == 'style':
            try:
                st = json.loads(r['meta'] or '{}')
            except Exception:
                st = {}
            temp = st.get('temperature')
            if temp is not None:
                parts.append('回答风格：温度 %.1f，尽量短句。' % float(temp))
            break
    # canon / 示例 / 动态事实
    budget = 5000
    cand = []
    for r in rows:
        if r['mode'] not in ('keyed', 'retrieved', 'fewshot'):
            continue
        if r['scope_type'] != 'global':
            if r['scope_type'] != scope_type:
                continue
            if scope_id and r['scope_id'] != scope_id:
                continue
        keys = _json(r['keys'], [])
        sc = _hit_score(text, keys)
        if r['mode'] == 'fewshot' and not sc:
            continue
        if r['mode'] == 'keyed' and not sc:
            continue
        if r['type'] == 'canon' and not sc:
            continue
        cand.append((sc + r['importance'], r))
    cand.sort(key=lambda x: -x[0])
    used = 0
    for _, r in cand:
        if used >= 6:
            break
        c = r['content']
        if len(c) > budget:
            c = c[:budget]
        parts.append('【记忆·%s】%s' % (r['type'], c))
        budget -= len(c)
        used += 1
        if budget <= 0:
            break
    return '\n\n'.join(parts)


# ---------------------------------------------------------------- 自动抽取

_EXTRACT_SYSTEM = '''你是记忆抽取器。根据一轮对话，抽取最多 3 条值得长期记住的内容。
只输出 JSON 数组，不要解释，不要 markdown 代码块。
每个元素：
{"type":"fact|preference|event|relationship","content":"一句话，第三人称，不超过60字","keys":["2-4个词"],"importance":0.0到1.0,"confidence":0.0到1.0}
规则：
- 用户主动说出的姓名、城市、职业、喜好、计划、约定，必须记录；
- 只记稳定、以后有用的信息；不记寒暄、一次性琐事；
- 不记密码、证件、银行卡、精确住址、联系方式等敏感信息；
- 没有信息时输出 []，但用户透露个人信息时不要输出 []。
示例输入：用户：我叫阿岚，住在杭州，做设计
示例输出：[{"type":"fact","content":"用户叫阿岚，住在杭州，做设计","keys":["阿岚","杭州","设计"],"importance":0.7,"confidence":0.9}]'''

_SENSITIVE = re.compile(r'密码|身份证|银行卡|手机号|电话|住址|门牌|微信|支付宝|验证码')


def _norm(s):
    return re.sub(r'[\s\W_]+', '', str(s or '').lower())


async def _find_dupe_or_conflict(cid, scope_type, scope_id, typ, content, keys):
    """返回 ('dup', id) / ('supersede', old_id) / None。"""
    cur = await store._db.execute(
        'SELECT id,type,content,keys FROM memory_items WHERE card_id=? AND archived=0'
        ' AND scope_type=? AND scope_id=? AND type IN ("fact","preference","event","relationship")',
        (cid, scope_type, scope_id))
    rows = [dict(r) for r in await cur.fetchall()]
    norm_new = _norm(content)
    new_keys = {str(k).strip().lower() for k in (keys or []) if str(k).strip()}
    conflict = None
    for r in rows:
        if _norm(r['content']) == norm_new:
            return ('dup', r['id'])
        if r['type'] != typ:
            continue
        if typ not in ('fact', 'preference'):
            continue
        try:
            old_keys = {str(k).strip().lower() for k in json.loads(r['keys'] or '[]')}
        except Exception:
            old_keys = set()
        overlap = new_keys & old_keys
        if len(overlap) >= 2:
            conflict = r['id']
        elif len(overlap) >= 1:
            ratio = difflib.SequenceMatcher(None, norm_new, _norm(r['content'])).ratio()
            if ratio >= 0.7:
                conflict = r['id']
    if conflict:
        return ('supersede', conflict)
    return None


async def extract(cfg, card, text, reply, mtype, target, uid, account_id=''):
    """每条消息后异步抽取记忆。失败静默。"""
    try:
        if not text or not card:
            return 0
        cid = card.get('id') or ''
        chain = None
        try:
            from . import llm
            model = (card.get('model') or {})
            chain = config.provider_chain(cfg, model.get('provider_id') or '', {})
        except Exception:
            chain = None
        if not chain:
            return 0
        where = '群聊' if mtype == 'group' else '私聊'
        user_msg = '场景：%s\n用户：%s\n机器人：%s' % (where, str(text)[:800], str(reply)[:800])
        raw, _used = await asyncio.wait_for(
            llm.chat_chain(chain, [{'role': 'user', 'content': user_msg}],
                           system=_EXTRACT_SYSTEM, max_tokens=500, temperature=0.2),
            timeout=40)
        raw = str(raw or '').strip()
        if '```' in raw:
            raw = re.sub(r'```[a-z]*', '', raw).replace('```', '').strip()
        a, b = raw.find('['), raw.rfind(']')
        if a < 0 or b < a:
            return 0
        try:
            arr = json.loads(raw[a:b + 1])
        except Exception:
            return 0
        if not isinstance(arr, list):
            return 0
        scope_type = 'group' if mtype == 'group' else 'private'
        saved = 0
        for x in arr[:3]:
            try:
                if not isinstance(x, dict):
                    continue
                content = str(x.get('content') or '').strip()
                if len(content) < 4 or len(content) > 120 or _SENSITIVE.search(content):
                    continue
                try:
                    imp = float(x.get('importance') or 0.5)
                    conf = float(x.get('confidence') or 0.7)
                except Exception:
                    imp, conf = 0.5, 0.7
                if conf < 0.55 or imp < 0.35:
                    continue
                typ = x.get('type') or 'fact'
                keys = x.get('keys') or []
                async with _EXTRACT_LOCK:
                    found = await _find_dupe_or_conflict(cid, scope_type, target, typ, content, keys)
                    if found and found[0] == 'dup':
                        continue
                    iid = await save_item({
                        'card_id': cid, 'account_id': account_id, 'scope_type': scope_type,
                        'scope_id': target, 'subject_id': uid, 'type': typ,
                        'mode': 'retrieved', 'content': content,
                        'keys': keys, 'importance': imp, 'confidence': conf,
                        'source': 'auto',
                    })
                    if found and found[0] == 'supersede':
                        await store._db.execute(
                            'UPDATE memory_items SET archived=1,superseded_by=?,updated_at=? WHERE id=?',
                            (iid, _now(), found[1]))
                        await store._db.commit()
                saved += 1
            except Exception as e:
                logbuf.debug('memory', '单条抽取失败：%s' % str(e)[:100])
                continue
        if saved:
            logbuf.info('memory', '自动记住 %d 条（%s:%s）' % (saved, scope_type, target))
        return saved
    except Exception as e:
        logbuf.debug('memory', '抽取失败：%s' % str(e)[:120])
        return 0


async def list_trigger_items(card_id):
    """关键词管理页用：带 id 的完整规则。"""
    try:
        cur = await store._db.execute(
            'SELECT id,content,meta,updated_at FROM memory_items WHERE card_id=? AND type="trigger"'
            ' AND archived=0 ORDER BY updated_at DESC', (card_id,))
        rows = await cur.fetchall()
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            m = json.loads(r['meta'] or '{}')
        except Exception:
            m = {}
        out.append({'id': r['id'], 'match': m.get('match') or '',
                    'reply': m.get('reply') or r['content'] or '',
                    'mode': m.get('mode') or 'contains',
                    'require_at': m.get('require_at') is not False,
                    'enabled': m.get('enabled') is not False})
    out.sort(key=lambda x: x['match'])
    return out


async def list_triggers(card):
    """卡片的关键词必回规则（存在记忆里）。"""
    cid = str((card or {}).get('id') or '')
    if not cid:
        return []
    try:
        cur = await store._db.execute(
            'SELECT meta,content FROM memory_items WHERE card_id=? AND type="trigger"'
            ' AND archived=0', (cid,))
        rows = await cur.fetchall()
    except Exception:
        return []
    out = []
    for r in rows:
        try:
            m = json.loads(r['meta'] or '{}')
        except Exception:
            continue
        match = str(m.get('match') or '').strip()
        reply = str(m.get('reply') or r['content'] or '').strip()
        if not match or not reply:
            continue
        out.append({'match': match, 'reply': reply,
                    'mode': m.get('mode') or 'contains',
                    'require_at': m.get('require_at') is not False,
                    'enabled': m.get('enabled') is not False})
    return out


async def pick_examples(card, text='', limit=2):
    """挑 1-2 条示例对话，按当前消息关键词命中。返回 [{user, assistant}]。"""
    cid = str((card or {}).get('id') or '')
    if not cid:
        return []
    try:
        cur = await store._db.execute(
            'SELECT content,meta,keys FROM memory_items WHERE card_id=? AND type="example"'
            ' AND archived=0', (cid,))
        rows = [dict(r) for r in await cur.fetchall()]
    except Exception:
        return []
    scored = []
    for r in rows:
        try:
            meta = json.loads(r['meta'] or '{}')
            keys = json.loads(r['keys'] or '[]')
        except Exception:
            meta, keys = {}, []
        sc = _hit_score(text, keys)
        scored.append((sc, r.get('content') or '', meta))
    hit = [x for x in scored if x[0] > 0]
    hit.sort(key=lambda x: -x[0])
    out = []
    for _, content, meta in hit[:limit]:
        u = str(meta.get('user') or '')
        a = str(meta.get('assistant') or '')
        if not u or not a:
            parts = str(content).split('\n', 1)
            if len(parts) == 2:
                u, a = parts[0], parts[1]
        if u and a:
            out.append({'user': u, 'assistant': a})
    return out


async def direct_reply(card, text):
    """高频情景直接回示例台词（保证人设，不经过模型）。

    只在命中长度 >=2 的关键词、且消息较短时触发，避免误伤。
    """
    t = str(text or '').strip()
    if not t or len(t) > 24:
        return ''
    cid = str((card or {}).get('id') or '')
    try:
        cur = await store._db.execute(
            'SELECT content,meta,keys FROM memory_items WHERE card_id=? AND type="example"'
            ' AND archived=0', (cid,))
        rows = [dict(r) for r in await cur.fetchall()]
    except Exception:
        return ''
    best = None
    for r in rows:
        try:
            keys = [str(k) for k in json.loads(r['keys'] or '[]')]
            meta = json.loads(r['meta'] or '{}')
        except Exception:
            continue
        score = 0
        for k in keys:
            if len(k) >= 2 and k in t:
                score = max(score, len(k))
        if score >= 2 and (best is None or score > best[0]):
            best = (score, meta)
    if not best:
        return ''
    meta = best[1]
    return str(meta.get('assistant') or '')


async def pick_greeting(card):
    cid = str((card or {}).get('id') or '')
    try:
        cur = await store._db.execute(
            'SELECT content FROM memory_items WHERE card_id=? AND type="greeting"'
            ' AND archived=0', (cid,))
        rows = [r['content'] for r in await cur.fetchall()]
    except Exception:
        rows = []
    if not rows:
        return ''
    return random.choice(rows)


# ---------------------------------------------------------------- 星图

def _slim_star(r):
    return {'id': r['id'], 'type': r['type'], 'x': r['star_x'], 'y': r['star_y'],
            'main': bool(r['is_main']), 'parent': r['parent_id'],
            'state': r.get('state') or 'active',
            'b': round(min(1, (r['importance'] or 0.5) *
                           (0.5 ** (max(0, _now() - (r['last_used_at'] or 0)) / 86400 / 45))), 3),
            'label': (r['content'] or '')[:18]}


async def map_data(card_id, scope_type='', scope_id='', limit=400):
    import asyncio
    await asyncio.sleep(0)
    try:
        await refresh_states(card_id)
    except Exception:
        pass
    where = 'card_id=? AND archived=0'
    args = [card_id]
    if scope_type in ('group', 'private') and scope_id:
        where += ' AND (scope_type="global" OR (scope_type=? AND scope_id=?))'
        args += [scope_type, scope_id]
    elif scope_type == 'global':
        where += ' AND scope_type="global"'
    cur = await store._db.execute(
        'SELECT id,type,mode,content,keys,importance,pinned,state,star_x,star_y,is_main,'
        'parent_id,cluster,use_count,last_used_at,tile_x,tile_y '
        'FROM memory_items WHERE ' + where + ' ORDER BY is_main DESC, importance DESC', args)
    rows_all = [dict(r) for r in await cur.fetchall()]
    rows = [r for r in rows_all if r.get('state') != 'junk']
    junk_rows = [r for r in rows_all if r.get('state') == 'junk']
    total = len(rows)
    junk = len(junk_rows)
    main = [r for r in rows if r['is_main']]
    xs = [r['star_x'] for r in rows] or [0]
    ys = [r['star_y'] for r in rows] or [0]
    clusters = {}
    for r in rows:
        cl = r['cluster'] or r['type']
        c = clusters.setdefault(cl, {'name': cl, 'count': 0, 'x': 0, 'y': 0})
        c['count'] += 1
        if r['is_main']:
            c['x'], c['y'] = r['star_x'], r['star_y']
    return {'total': total, 'junk': junk, 'main': [_slim_star(r) for r in main],
            'stars': [],   # 卫星按视口分块由 /api/memory/tile 懒加载
            'bbox': {'minx': min(xs), 'maxx': max(xs), 'miny': min(ys), 'maxy': max(ys)},
            'junk_stars': [_slim_star(r) for r in junk_rows[:300]],
            'clusters': list(clusters.values())}


async def tile(card_id, tx, ty, limit=200, scope_type='', scope_id=''):
    where = 'card_id=? AND archived=0 AND state!="junk" AND is_main=0 AND tile_x=? AND tile_y=?'
    args = [card_id, int(tx), int(ty)]
    if scope_type in ('group', 'private') and scope_id:
        where += ' AND (scope_type="global" OR (scope_type=? AND scope_id=?))'
        args += [scope_type, scope_id]
    elif scope_type == 'global':
        where += ' AND scope_type="global"'
    args.append(int(limit))
    cur = await store._db.execute(
        'SELECT id,type,mode,content,keys,importance,pinned,state,star_x,star_y,is_main,'
        'parent_id,cluster,use_count,last_used_at,tile_x,tile_y '
        'FROM memory_items WHERE ' + where + ' LIMIT ?', args)
    rows = await cur.fetchall()
    return [_slim_star(dict(r)) for r in rows]


async def consolidate(card_id):
    """巩固：合并近似重复、归档陈旧事件。返回统计。"""
    now = _now()
    cur = await store._db.execute(
        'SELECT id,scope_type,scope_id,subject_id,type,content,keys,importance,pinned,'
        'created_at,state FROM memory_items WHERE card_id=? AND archived=0 AND state!="junk"'
        ' AND type IN ("fact","preference","event","relationship")', (card_id,))
    rows = [dict(r) for r in await cur.fetchall()]
    groups = {}
    for r in rows:
        groups.setdefault((r['scope_type'], r['scope_id'], r['subject_id'], r['type']), []).append(r)
    merged = 0
    for items in groups.values():
        for i in range(len(items)):
            a = items[i]
            if a.get('_gone'):
                continue
            for j in range(i + 1, len(items)):
                b = items[j]
                if b.get('_gone'):
                    continue
                if a['pinned'] or b['pinned']:
                    continue
                na, nb = _norm(a['content']), _norm(b['content'])
                if not na or not nb:
                    continue
                if difflib.SequenceMatcher(None, na, nb).ratio() < 0.9:
                    continue
                # 保留重要度高/更新的那条
                keep, drop = (a, b) if (a['importance'], a['created_at']) >= (b['importance'], b['created_at']) else (b, a)
                await store._db.execute(
                    'UPDATE memory_items SET archived=1,superseded_by=?,updated_at=? WHERE id=?',
                    (keep['id'], now, drop['id']))
                drop['_gone'] = True
                merged += 1
    stale = 0
    for r in rows:
        if r.get('_gone') or r['pinned']:
            continue
        if r['type'] == 'event' and r['created_at'] < now - 90 * 86400 and r['importance'] < 0.4:
            await store._db.execute('UPDATE memory_items SET archived=1,updated_at=? WHERE id=?',
                                    (now, r['id']))
            stale += 1
    if merged or stale:
        await store._db.commit()
    return {'merged': merged, 'stale': stale, 'scanned': len(rows)}


async def stats(card_id):
    cur = await store._db.execute(
        'SELECT type,COUNT(*) AS c,SUM(LENGTH(content)) AS chars FROM memory_items'
        ' WHERE card_id=? AND archived=0 GROUP BY type', (card_id,))
    types = {r['type']: int(r['c']) for r in await cur.fetchall()}
    total = sum(types.values())
    cur = await store._db.execute(
        'SELECT state,COUNT(*) AS c FROM memory_items WHERE card_id=? AND archived=0 GROUP BY state',
        (card_id,))
    states = {r['state']: int(r['c']) for r in await cur.fetchall()}
    cur = await store._db.execute(
        'SELECT scope_type,COUNT(*) AS c FROM memory_items WHERE card_id=? AND archived=0'
        ' GROUP BY scope_type', (card_id,))
    scopes = {r['scope_type']: int(r['c']) for r in await cur.fetchall()}
    cur = await store._db.execute(
        'SELECT COALESCE(SUM(LENGTH(content)),0) AS chars,'
        ' COALESCE(SUM(CASE WHEN created_at>=? THEN 1 ELSE 0 END),0) AS recent'
        ' FROM memory_items WHERE card_id=? AND archived=0', (_now() - 7 * 86400, card_id))
    r = await cur.fetchone()
    return {'total': total, 'types': types, 'states': states, 'scopes': scopes,
            'chars': int(r['chars'] or 0), 'recent7d': int(r['recent'] or 0)}


async def search(card_id, q, limit=80, scope_type='', scope_id=''):
    q = str(q or '').strip()
    if not q:
        return []
    like = '%' + q + '%'
    where = 'card_id=? AND archived=0 AND (content LIKE ? OR keys LIKE ?)'
    args = [card_id, like, like]
    if scope_type in ('group', 'private') and scope_id:
        where += ' AND (scope_type="global" OR (scope_type=? AND scope_id=?))'
        args += [scope_type, scope_id]
    elif scope_type == 'global':
        where += ' AND scope_type="global"'
    args.append(int(limit))
    cur = await store._db.execute(
        'SELECT id,type,content,keys,star_x,star_y,is_main,state,importance '
        'FROM memory_items WHERE ' + where + ' ORDER BY pinned DESC,importance DESC LIMIT ?', args)
    rows = await cur.fetchall()
    return [{'id': r['id'], 'type': r['type'], 'content': r['content'],
             'x': r['star_x'], 'y': r['star_y'], 'main': bool(r['is_main']),
             'state': r['state'] or 'active'} for r in rows]


async def get_item(mid):
    cur = await store._db.execute('SELECT * FROM memory_items WHERE id=?', (mid,))
    row = await cur.fetchone()
    return dict(row) if row else None


async def save_item(item):
    now = _now()
    iid = item.get('id') or new_id()
    cur = await store._db.execute('SELECT id FROM memory_items WHERE id=?', (iid,))
    exists = await cur.fetchone()
    meta = json.dumps(item.get('meta') or {}, ensure_ascii=False)
    keys = json.dumps(item.get('keys') or [], ensure_ascii=False)
    if exists:
        await store._db.execute(
            'UPDATE memory_items SET content=?,meta=?,keys=?,importance=?,confidence=?,'
            'pinned=?,type=?,mode=?,updated_at=? WHERE id=?',
            (item.get('content') or '', meta, keys, float(item.get('importance') or .5),
             float(item.get('confidence') or 1), int(bool(item.get('pinned'))),
             item.get('type') or 'fact', item.get('mode') or 'retrieved', now, iid))
    else:
        typ = item.get('type') or 'fact'
        cid = item.get('card_id') or ''
        cur = await store._db.execute(
            'SELECT id,star_x,star_y FROM memory_items WHERE card_id=? AND type=?'
            ' AND is_main=1 AND archived=0 LIMIT 1', (cid, typ))
        main = await cur.fetchone()
        if main:
            cur2 = await store._db.execute(
                'SELECT COUNT(*) AS c FROM memory_items WHERE card_id=? AND type=? AND archived=0',
                (cid, typ))
            cnt = int((await cur2.fetchone())['c'])
            x, y = _sat_pos((main['star_x'], main['star_y']), cnt, iid)
            parent, is_main = main['id'], 0
        else:
            if typ in _TYPE_POS:
                x, y = _TYPE_POS[typ]
            else:
                a = _hash(iid, typ) * math.pi * 2
                x, y = round(math.cos(a) * 420, 1), round(math.sin(a) * 420, 1)
            parent, is_main = '', 1
        await store._db.execute(
            'INSERT INTO memory_items(id,card_id,account_id,scope_type,scope_id,subject_id,'
            'type,mode,content,meta,keys,importance,confidence,source,created_at,updated_at,'
            'pinned,state,star_x,star_y,is_main,parent_id,cluster,tile_x,tile_y) '
            'VALUES(?,?,?,?,?,"",?,?,?,?,?,?,?,?,?,?,?,"active",?,?,?,?,?,?,?)',
            (iid, item.get('card_id') or '', item.get('account_id') or '',
             item.get('scope_type') or 'global', item.get('scope_id') or '',
             typ, item.get('mode') or 'retrieved',
             item.get('content') or '', meta, keys, float(item.get('importance') or .5),
             float(item.get('confidence') or 1), item.get('source') or 'manual', now, now,
             int(bool(item.get('pinned'))), x, y, is_main, parent, typ,
             int(x // 512), int(y // 512)))
    await store._db.commit()
    return iid


async def delete_item(iid, hard=False):
    if hard:
        await store._db.execute('DELETE FROM memory_items WHERE id=?', (iid,))
    else:
        await store._db.execute('UPDATE memory_items SET archived=1,updated_at=? WHERE id=?',
                                (_now(), iid))
    await store._db.commit()
