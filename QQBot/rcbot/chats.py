# -*- coding: utf-8 -*-
"""全量聊天档案：写入、查询、撤回打标、导出。

与 store.messages 的区别（别搞混）：
  messages   喂给 LLM 的上下文，过滤后才写，图片压成 [图片]，可清空
  chat_logs  这里管 —— 全量、原始段 JSON、撤回标记、永久保留

为什么撤回只能靠"先存内容再打标"：
  OneBot 的 group_recall / friend_recall 事件只带 message_id，不带原文
  （实测 napcat.mjs:85979-85988 反编译出的类定义）。
  所以消息到达那一刻必须把内容存下来，撤回事件只负责按 msg_id 打标。
"""
import json
import os
import time

from . import logbuf, store

MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')

# 媒体根目录覆盖（测试用；正常走 config.chat.media_dir）
_media_root_override = None


def set_media_root(path):
    """强制指定媒体根目录（测试与特殊部署用）。传 None 恢复默认。"""
    global _media_root_override
    _media_root_override = path

# 媒体段类型 → 落盘扩展名
_EXT_BY_TYPE = {
    'image': '.jpg',
    'record': '.mp3',
    'video': '.mp4',
    'file': '.bin',
    'face': '.gif',
}


def media_root(cfg=None):
    """媒体根目录：config.chat.media_dir > 默认 <包目录>/media。

    传入 cfg 时直接用它（不重读文件）—— 消息处理路径上会频繁调用。
    """
    if _media_root_override:
        return _media_root_override
    d = ''
    if cfg is not None:
        d = ((cfg.get('chat') or {}).get('media_dir') or '')
    else:
        try:
            from . import config as _cfg
            d = ((_cfg.load().get('chat') or {}).get('media_dir') or '')
        except Exception:
            pass
    return d or MEDIA_DIR


def _now():
    return int(time.time())


def _json(v, default=''):
    if isinstance(v, str):
        return v
    try:
        return json.dumps(v, ensure_ascii=False)
    except Exception:
        return default


# ---------------------------------------------------------------- 写入

async def record(account_id, kind, target_id, role, segs, sender_id='', sender_name='',
                  msg_id='', created_at=0, session_id=None, media=None):
    """写一条聊天档案。返回新行 id。

    segs  —— OneBot 原始消息段数组（list[dict]）
    media —— 媒体副本清单（list[dict]），由 media.py 填好后传进来
    """
    if session_id is None:
        session_id = store.session_key(kind, target_id, 'public', account_id)
    text = seg_text(segs)
    cur = await store._db.execute(
        'INSERT INTO chat_logs(account_id,session_id,kind,target_id,msg_id,sender_id,sender_name,'
        'role,segs,text,media,recalled,recalled_by,recalled_at,created_at)'
        ' VALUES(?,?,?,?,?,?,?,?,?,?,?,0,\'\',0,?)',
        (account_id or '', session_id, kind or '', str(target_id or ''), str(msg_id or ''),
         str(sender_id or ''), str(sender_name or ''), role or 'user',
         _json(segs, '[]'), text, _json(media or [], '[]'),
         int(created_at or _now())))
    await store._db.commit()
    return cur.lastrowid


def seg_text(segs):
    """从消息段里抽纯文本（图片/语音等转成占位，供搜索与降级渲染）。"""
    if isinstance(segs, str):
        return segs
    out = []
    for s in segs or []:
        if not isinstance(s, dict):
            continue
        t = s.get('type')
        d = s.get('data') or {}
        if t == 'text':
            out.append(d.get('text') or '')
        elif t == 'at':
            out.append('@%s' % (d.get('qq') or ''))
        elif t == 'image':
            out.append('[图片]')
        elif t == 'face':
            out.append('[表情]')
        elif t == 'record':
            out.append('[语音]')
        elif t == 'video':
            out.append('[视频]')
        elif t == 'file':
            out.append('[文件:%s]' % (d.get('name') or ''))
        elif t == 'reply':
            out.append('[引用]')
        elif t == 'json':
            out.append('[卡片]')
        elif t == 'xml':
            out.append('[XML]')
    return ''.join(out).strip()


# ---------------------------------------------------------------- 撤回

async def mark_recalled(account_id, msg_id, by='', kind=''):
    """按 message_id 给已记录的消息打撤回标记。返回命中的行数。

    撤回事件只有 message_id，没有原文 —— 原文在消息到达时就存好了。
    """
    if not msg_id:
        return 0
    cur = await store._db.execute(
        'UPDATE chat_logs SET recalled=1, recalled_by=?, recalled_at=?'
        ' WHERE account_id=? AND msg_id=?',
        (str(by or ''), _now(), account_id or '', str(msg_id)))
    await store._db.commit()
    n = cur.rowcount or 0
    if n:
        logbuf.info('chat', '撤回 %s 条消息（msg_id=%s，账号 %s）' % (n, msg_id, account_id))
    else:
        # 没命中：这条消息我们没记录到（机器人离线期间撤的，或 msg_id 对不上）。
        # 补一条墓碑，让聊天记录里能看出"这里原本有东西被撤了"。
        await _tombstone(account_id, msg_id, by, kind)
    return n


async def _tombstone(account_id, msg_id, by, kind):
    """撤回但没记录到原文 → 写一条占位。"""
    sid = store.session_key(kind or 'private', '', 'public', account_id)
    try:
        await store._db.execute(
            'INSERT INTO chat_logs(account_id,session_id,kind,target_id,msg_id,sender_id,'
            'sender_name,role,segs,text,media,recalled,recalled_by,recalled_at,created_at)'
            ' VALUES(?,?,?,?,?,?,?,?,?,?,?,1,?,?,?)',
            (account_id or '', sid, kind or '', '', str(msg_id or ''), '', '',
             'system', '[]', '[一条消息被撤回]', '[]', str(by or ''), _now(), _now()))
        await store._db.commit()
    except Exception as e:
        logbuf.debug('chat', '墓碑写入失败：%s' % str(e)[:120])


# ---------------------------------------------------------------- 查询

async def list_sessions(account_id='', kind='', keyword='', limit=200):
    """会话列表（按最后一条消息时间倒序）。

    这是"聊天记录"页左侧的列表：按账号 → 群/私聊 → 会话。
    """
    sql = ('SELECT session_id, account_id, kind, target_id,'
           ' COUNT(*) AS msg_count, MAX(created_at) AS last_at,'
           ' SUM(recalled) AS recalled_count'
           ' FROM chat_logs WHERE 1=1')
    args = []
    if account_id:
        sql += ' AND account_id=?'
        args.append(account_id)
    if kind:
        sql += ' AND kind=?'
        args.append(kind)
    sql += ' GROUP BY session_id ORDER BY last_at DESC LIMIT ?'
    args.append(int(limit))
    if keyword:
        # 关键词过滤放在这层：先按关键词筛出命中的会话，再取列表
        pass
    cur = await store._db.execute(sql, args)
    rows = [dict(r) for r in await cur.fetchall()]
    if keyword:
        k = ('%' + keyword.lower() + '%')
        keep = []
        for r in rows:
            cur2 = await store._db.execute(
                'SELECT 1 FROM chat_logs WHERE session_id=? AND'
                ' (LOWER(text) LIKE ? OR LOWER(sender_name) LIKE ?) LIMIT 1',
                (r['session_id'], k, k))
            if await cur2.fetchone():
                keep.append(r)
        rows = keep
    return rows


async def list_messages(session_id, before_id=0, limit=50, keyword=''):
    """消息分页（倒序游标：给 before_id 取更早的）。

    前端向上滚动加载更多时用这个 —— 比 OFFSET 稳，插入新消息也不会错位。
    """
    sql = 'SELECT * FROM chat_logs WHERE session_id=?'
    args = [session_id]
    if before_id:
        sql += ' AND id<?'
        args.append(int(before_id))
    if keyword:
        sql += ' AND LOWER(text) LIKE ?'
        args.append('%' + keyword.lower() + '%')
    sql += ' ORDER BY id DESC LIMIT ?'
    args.append(int(limit))
    cur = await store._db.execute(sql, args)
    rows = [dict(r) for r in await cur.fetchall()]
    for r in rows:
        r['segs'] = _loads(r.get('segs'), [])
        r['media'] = _loads(r.get('media'), [])
    return list(reversed(rows))


def _loads(s, default):
    if isinstance(s, (list, dict)):
        return s
    try:
        return json.loads(s)
    except Exception:
        return default


async def stats(account_id=''):
    """统计：条数、撤回数、时间跨度。"""
    sql = 'SELECT COUNT(*) AS c, SUM(recalled) AS rc, MIN(created_at) AS t0, MAX(created_at) AS t1 FROM chat_logs'
    args = []
    if account_id:
        sql += ' WHERE account_id=?'
        args.append(account_id)
    cur = await store._db.execute(sql, args)
    row = await cur.fetchone()
    c = (row['c'] or 0) if row else 0
    return {
        'messages': c,
        'recalled': (row['rc'] or 0) if row else 0,
        'from': (row['t0'] or 0) if row else 0,
        'to': (row['t1'] or 0) if row else 0,
    }


# ---------------------------------------------------------------- 导出

async def export(account_id='', session_id='', date_from=0, date_to=0):
    """导出 JSON（按账号 / 会话 / 日期范围）。

    返回 (dict, 文件名)。字段与前端展示一致，含撤回标记与媒体相对路径。
    """
    sql = 'SELECT * FROM chat_logs WHERE 1=1'
    args = []
    if account_id:
        sql += ' AND account_id=?'
        args.append(account_id)
    if session_id:
        sql += ' AND session_id=?'
        args.append(session_id)
    if date_from:
        sql += ' AND created_at>=?'
        args.append(int(date_from))
    if date_to:
        sql += ' AND created_at<=?'
        args.append(int(date_to))
    sql += ' ORDER BY id ASC'
    cur = await store._db.execute(sql, args)
    rows = [dict(r) for r in await cur.fetchall()]

    sess = {}
    order = []
    for r in rows:
        sid = r['session_id']
        if sid not in sess:
            sess[sid] = {
                'session_id': sid,
                'account_id': r.get('account_id') or '',
                'kind': r.get('kind') or '',
                'target_id': r.get('target_id') or '',
                'messages': [],
            }
            order.append(sid)
        sess[sid]['messages'].append({
            'msg_id': r.get('msg_id') or '',
            'sender': {'id': r.get('sender_id') or '', 'name': r.get('sender_name') or ''},
            'role': r.get('role') or 'user',
            'created_at': r.get('created_at') or 0,
            'text': r.get('text') or '',
            'segs': _loads(r.get('segs'), []),
            'media': _loads(r.get('media'), []),
            'recalled': bool(r.get('recalled')),
            'recalled_by': r.get('recalled_by') or '',
            'recalled_at': r.get('recalled_at') or 0,
        })

    accounts = []
    seen = set()
    for r in rows:
        aid = r.get('account_id') or ''
        if aid and aid not in seen:
            seen.add(aid)
            accounts.append({'id': aid, 'uin': aid[1:] if aid.startswith('a') else aid})

    doc = {
        'exported_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'version': 1,
        'accounts': accounts,
        'sessions': [sess[s] for s in order],
    }
    name = 'chat-export-%s.json' % time.strftime('%Y%m%d-%H%M%S')
    return doc, name


# ---------------------------------------------------------------- 清理

async def purge_media_only(account_id='', date_from=0, date_to=0, session_id=''):
    """只清媒体文件，保留消息文本（默认行为）。

    永久保留是明确要求，所以这里**只删媒体副本**：
    磁盘紧张时能腾出空间，但聊天记录本身一条不丢。
    """
    sql = 'SELECT id, media, session_id, created_at FROM chat_logs WHERE 1=1'
    args = []
    if account_id:
        sql += ' AND account_id=?'
        args.append(account_id)
    if session_id:
        sql += ' AND session_id=?'
        args.append(session_id)
    if date_from:
        sql += ' AND created_at>=?'
        args.append(int(date_from))
    if date_to:
        sql += ' AND created_at<=?'
        args.append(int(date_to))
    cur = await store._db.execute(sql, args)
    rows = await cur.fetchall()

    root = media_root()
    freed = 0
    nfile = 0
    touched = []
    for r in rows:
        media = _loads(r['media'], [])
        if not media:
            continue
        changed = False
        for m in media:
            if not m.get('local') or not m.get('rel'):
                continue
            p = os.path.join(root, m['rel'])
            try:
                if os.path.isfile(p):
                    freed += os.path.getsize(p)
                    os.remove(p)
                    nfile += 1
                m['local'] = 0
                changed = True
            except Exception as e:
                logbuf.debug('chat', '删媒体失败 %s：%s' % (m.get('rel'), str(e)[:80]))
        if changed:
            touched.append((r['id'], _json(media, '[]')))
    for mid, mj in touched:
        await store._db.execute('UPDATE chat_logs SET media=? WHERE id=?', (mj, mid))
    await store._db.commit()
    logbuf.info('chat', '清理媒体：%d 个文件，释放 %.1f MB（消息文本保留）'
                % (nfile, freed / 1048576.0))
    return {'files': nfile, 'bytes': freed, 'messages': len(touched)}


async def check_media_consistency():
    """巡检：库里标了有本地副本、但文件已不在的记录。

    磁盘被外部清理过（比如运维手动删了目录）时，靠这个找出来。
    """
    cur = await store._db.execute('SELECT id, media FROM chat_logs')
    root = media_root()
    missing = []
    total = 0
    for r in await cur.fetchall():
        media = _loads(r['media'], [])
        for m in media:
            if not m.get('local') or not m.get('rel'):
                continue
            total += 1
            if not os.path.isfile(os.path.join(root, m['rel'])):
                missing.append({'id': r['id'], 'rel': m['rel']})
    return {'total': total, 'missing': missing[:200], 'missing_count': len(missing)}
