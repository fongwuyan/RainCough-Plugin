# -*- coding: utf-8 -*-
"""会话与消息存储（SQLite / aiosqlite）。"""
import os
import time

import aiosqlite

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
DB_FILE = os.path.join(ROOT, 'data', 'rcbot.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
  id          TEXT PRIMARY KEY,
  kind        TEXT NOT NULL,
  target_id   TEXT NOT NULL,
  title       TEXT DEFAULT '',
  persona_id  TEXT DEFAULT '',
  provider_id TEXT DEFAULT '',
  enabled     INTEGER DEFAULT 1,
  mode        TEXT DEFAULT 'public',
  created_at  INTEGER DEFAULT 0,
  updated_at  INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS messages (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  role       TEXT NOT NULL,
  content    TEXT NOT NULL,
  name       TEXT DEFAULT '',
  created_at INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_msg_sess ON messages(session_id, id);
CREATE TABLE IF NOT EXISTS summaries (
  session_id  TEXT PRIMARY KEY,
  content     TEXT DEFAULT '',
  upto_msg_id INTEGER DEFAULT 0,
  updated_at  INTEGER DEFAULT 0
);
"""

_db = None


async def init():
    global _db
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    _db = await aiosqlite.connect(DB_FILE)
    _db.row_factory = aiosqlite.Row
    await _db.executescript(SCHEMA)
    await _db.commit()
    return _db


async def close():
    global _db
    if _db:
        await _db.close()
        _db = None


def _now():
    return int(time.time())


def session_key(kind, target_id, mode='public'):
    """会话 id 规则：
    私聊  private:<uid>
    群公共 group:<gid>
    群私有 group:<gid>:<uid>
    """
    if kind == 'private':
        return 'private:%s' % target_id
    if mode == 'private':
        return 'group:%s:%s' % target_id
    return 'group:%s' % target_id


async def ensure_session(kind, target_id, title='', mode='public'):
    sid = session_key(kind, target_id, mode)
    cur = await _db.execute('SELECT id FROM sessions WHERE id=?', (sid,))
    row = await cur.fetchone()
    now = _now()
    if row is None:
        await _db.execute(
            'INSERT INTO sessions(id,kind,target_id,title,enabled,mode,created_at,updated_at)'
            ' VALUES(?,?,?,?,1,?,?,?)',
            (sid, kind, str(target_id), title or '', mode, now, now))
        await _db.commit()
    elif title:
        await _db.execute('UPDATE sessions SET title=?, updated_at=? WHERE id=? AND title=""',
                          (title, now, sid))
        await _db.commit()
    return sid


async def get_session(sid):
    cur = await _db.execute('SELECT * FROM sessions WHERE id=?', (sid,))
    row = await cur.fetchone()
    return dict(row) if row else None


async def list_sessions():
    cur = await _db.execute(
        'SELECT s.*, (SELECT COUNT(*) FROM messages m WHERE m.session_id=s.id) AS msg_count,'
        ' (SELECT MAX(created_at) FROM messages m WHERE m.session_id=s.id) AS last_at'
        ' FROM sessions s ORDER BY s.updated_at DESC')
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def update_session(sid, fields):
    allow = ('title', 'persona_id', 'provider_id', 'enabled', 'mode')
    sets, vals = [], []
    for k in allow:
        if k in fields:
            sets.append('%s=?' % k)
            vals.append(fields[k])
    if not sets:
        return False
    sets.append('updated_at=?')
    vals.append(_now())
    vals.append(sid)
    await _db.execute('UPDATE sessions SET %s WHERE id=?' % ','.join(sets), vals)
    await _db.commit()
    return True


async def delete_session(sid):
    await _db.execute('DELETE FROM messages WHERE session_id=?', (sid,))
    await _db.execute('DELETE FROM summaries WHERE session_id=?', (sid,))
    await _db.execute('DELETE FROM sessions WHERE id=?', (sid,))
    await _db.commit()


async def clear_session(sid):
    await _db.execute('DELETE FROM messages WHERE session_id=?', (sid,))
    await _db.execute('DELETE FROM summaries WHERE session_id=?', (sid,))
    await _db.execute('UPDATE sessions SET updated_at=? WHERE id=?', (_now(), sid))
    await _db.commit()


async def add_message(sid, role, content, name=''):
    now = _now()
    cur = await _db.execute(
        'INSERT INTO messages(session_id,role,content,name,created_at) VALUES(?,?,?,?,?)',
        (sid, role, content, name, now))
    await _db.execute('UPDATE sessions SET updated_at=? WHERE id=?', (now, sid))
    await _db.commit()
    return cur.lastrowid


async def recent_messages(sid, limit=200, after_id=0):
    cur = await _db.execute(
        'SELECT * FROM messages WHERE session_id=? AND id>? ORDER BY id DESC LIMIT ?',
        (sid, after_id, int(limit)))
    rows = await cur.fetchall()
    return [dict(r) for r in reversed(rows)]


async def count_messages(sid):
    cur = await _db.execute('SELECT COUNT(*) AS c FROM messages WHERE session_id=?', (sid,))
    row = await cur.fetchone()
    return row['c'] if row else 0


async def get_summary(sid):
    cur = await _db.execute('SELECT * FROM summaries WHERE session_id=?', (sid,))
    row = await cur.fetchone()
    return dict(row) if row else None


async def set_summary(sid, content, upto_msg_id):
    await _db.execute(
        'INSERT INTO summaries(session_id,content,upto_msg_id,updated_at) VALUES(?,?,?,?)'
        ' ON CONFLICT(session_id) DO UPDATE SET content=excluded.content,'
        ' upto_msg_id=excluded.upto_msg_id, updated_at=excluded.updated_at',
        (sid, content, int(upto_msg_id), _now()))
    await _db.commit()


async def session_detail(sid, limit=50):
    s = await get_session(sid)
    if not s:
        return None
    msgs = await recent_messages(sid, limit)
    summ = await get_summary(sid)
    s['messages'] = msgs
    s['summary'] = (summ or {}).get('content') or ''
    s['msg_count'] = await count_messages(sid)
    return s


async def stats():
    cur = await _db.execute('SELECT COUNT(*) AS c FROM sessions')
    n_sess = (await cur.fetchone())['c']
    cur = await _db.execute('SELECT COUNT(*) AS c FROM messages')
    n_msg = (await cur.fetchone())['c']
    cur = await _db.execute('SELECT COUNT(*) AS c FROM sessions WHERE enabled=1')
    n_on = (await cur.fetchone())['c']
    return {'sessions': n_sess, 'enabled': n_on, 'messages': n_msg}
