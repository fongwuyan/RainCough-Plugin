# -*- coding: utf-8 -*-
"""rcbot 存储/聊天记录层冒烟测试（本地，不连 QQ）。

覆盖：
  · 会话 id 带账号前缀，多号不串
  · 迁移：老会话补前缀，幂等
  · chat_logs 全量写入 + 撤回打标 + 墓碑
  · 导出 JSON 字段完整
  · 清理媒体只删文件不删消息
"""
import asyncio
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TMP = tempfile.mkdtemp(prefix='rcbot-smoke-')
os.environ['RCBOT_DATA_DIR'] = TMP

from rcbot import chats, config, media, store  # noqa: E402

FAILED = []


def check(name, cond, extra=''):
    if cond:
        print('  ok   %s' % name)
    else:
        print('  FAIL %s %s' % (name, extra))
        FAILED.append(name)


async def main():
    # 用临时库
    store.DB_FILE = os.path.join(TMP, 'test.db')
    await store.init()
    await store.ensure_columns()

    print('== 会话 id 与账号隔离 ==')
    s1 = await store.ensure_session('group', '555', title='群A', account_id='a111')
    s2 = await store.ensure_session('group', '555', title='群A', account_id='a222')
    check('同群不同号 → 不同会话', s1 != s2, '%s vs %s' % (s1, s2))
    check('会话 id 带账号前缀', s1 == 'a111:group:555', s1)
    p1 = await store.ensure_session('private', '999', account_id='a111')
    check('私聊 id 格式', p1 == 'a111:private:999', p1)

    print('== 迁移：老会话补前缀 ==')
    await store._db.execute(
        'INSERT INTO sessions(id,kind,target_id,enabled,mode,created_at,updated_at)'
        ' VALUES(?,?,?,1,?,?,?)', ('group:777', 'group', '777', 'public', 1, 1))
    await store._db.execute(
        'INSERT INTO messages(session_id,role,content,created_at) VALUES(?,?,?,?)',
        ('group:777', 'user', '老消息', 1))
    await store._db.commit()
    await store.migrate_account_prefix('a111')
    await store.migrate_account_prefix('a111')   # 再跑一次，必须幂等
    cur = await store._db.execute('SELECT id FROM sessions WHERE id LIKE ?', ('%777%',))
    rows = [r['id'] for r in await cur.fetchall()]
    check('老会话补上前缀', rows == ['a111:group:777'], rows)
    cur = await store._db.execute('SELECT session_id FROM messages WHERE content=?', ('老消息',))
    mrows = [r['session_id'] for r in await cur.fetchall()]
    check('老消息同步补前缀（幂等）', mrows == ['a111:group:777'], mrows)

    print('== chat_logs 写入与撤回 ==')
    segs = [
        {'type': 'text', 'data': {'text': '今天天气不错'}},
        {'type': 'at', 'data': {'qq': '10001'}},
        {'type': 'image', 'data': {'file': 'a.image', 'url': 'http://x/a.jpg'}},
        {'type': 'face', 'data': {'id': '14'}},
        {'type': 'record', 'data': {'file': 'b.silk', 'url': 'http://x/b.silk'}},
        {'type': 'video', 'data': {'file': 'c.mp4', 'url': 'http://x/c.mp4'}},
        {'type': 'file', 'data': {'name': 'doc.pdf', 'size': 100, 'url': 'http://x/d.pdf'}},
    ]
    rid = await chats.record('a111', 'group', '555', 'user', segs,
                             sender_id='10001', sender_name='张三',
                             msg_id='90001', created_at=1762000000)
    check('写入返回行 id', bool(rid), rid)
    txt = chats.seg_text(segs)
    check('纯文本提取正确', '今天天气不错' in txt and '[图片]' in txt
          and '[语音]' in txt and '[视频]' in txt, txt)
    check('文件段带文件名', 'doc.pdf' in txt, txt)

    n = await chats.mark_recalled('a111', '90001', by='10002')
    check('撤回命中 1 条', n == 1, n)
    cur = await store._db.execute('SELECT recalled, recalled_by, text FROM chat_logs WHERE id=?', (rid,))
    row = await cur.fetchone()
    check('撤回标记已置', row['recalled'] == 1, row['recalled'])
    check('撤回后原文保留', '今天天气不错' in (row['text'] or ''), row['text'])
    check('撤回人已记录', row['recalled_by'] == '10002', row['recalled_by'])

    # 撤回一条没记录过的 → 墓碑
    n2 = await chats.mark_recalled('a111', '99999', by='10002')
    check('未命中时写墓碑', n2 == 0, n2)
    cur = await store._db.execute('SELECT role, recalled FROM chat_logs WHERE msg_id=?', ('99999',))
    rows = await cur.fetchall()
    check('墓碑已写入且标记撤回', len(rows) == 1 and rows[0]['recalled'] == 1
          and rows[0]['role'] == 'system', [dict(r) for r in rows])

    print('== 会话列表与消息分页 ==')
    sess = await chats.list_sessions(account_id='a111')
    check('按账号列出会话', len(sess) >= 1, len(sess))
    check('会话带 msg_count', all('msg_count' in s for s in sess))
    msgs = await chats.list_messages('a111:group:555', limit=10)
    check('消息倒序取回', len(msgs) >= 1 and msgs[0]['segs'][0]['type'] == 'text', len(msgs))
    check('媒体清单可解析', isinstance(msgs[0]['media'], list))

    print('== 导出 ==')
    doc, name = await chats.export(account_id='a111')
    check('导出有文件名', name.endswith('.json'), name)
    check('导出含 accounts', isinstance(doc.get('accounts'), list) and doc['accounts'])
    check('导出含 sessions', len(doc.get('sessions') or []) >= 1)
    m0 = doc['sessions'][0]['messages'][0]
    for k in ('msg_id', 'sender', 'role', 'created_at', 'text', 'segs', 'media',
              'recalled', 'recalled_by'):
        check('导出字段 %s' % k, k in m0)
    js = json.dumps(doc, ensure_ascii=False)
    check('导出是合法 JSON', len(js) > 100)

    print('== 媒体清理（只删文件，留消息） ==')
    root = os.path.join(TMP, 'media')
    chats.set_media_root(root)
    os.makedirs(os.path.join(root, '111', '2026-11-01'), exist_ok=True)
    fp = os.path.join(root, '111', '2026-11-01', 'x.jpg')
    with open(fp, 'wb') as f:
        f.write(b'x' * 1024)
    await chats.record('a111', 'group', '555', 'user',
                       [{'type': 'image', 'data': {}}], sender_id='1',
                       msg_id='90002', created_at=1762000001,
                       media=[{'kind': 'image', 'seg': 0,
                               'rel': '111/2026-11-01/x.jpg', 'bytes': 1024,
                               'mime': 'image/jpeg', 'local': 1}])
    r = await chats.purge_media_only(account_id='a111')
    check('删掉 1 个媒体文件', r['files'] == 1, r)
    check('文件已不存在', not os.path.exists(fp))
    cur = await store._db.execute('SELECT COUNT(*) AS c FROM chat_logs WHERE msg_id=?', ('90002',))
    row = await cur.fetchone()
    check('消息文本仍保留', row['c'] == 1, row['c'])
    cur = await store._db.execute('SELECT media FROM chat_logs WHERE msg_id=?', ('90002',))
    row = await cur.fetchone()
    check('媒体标记置为不可用', '"local":0' in (row['media'] or '').replace(' ', ''),
          row['media'])

    print('== 一致性巡检 ==')
    c = await chats.check_media_consistency()
    check('巡检能跑', 'total' in c, c)

    print('== 配置兼容 ==')
    cfg = config.load()
    check('旧配置包装成单账号', len(cfg['onebot']['accounts']) == 1,
          cfg['onebot']['accounts'])
    check('账号 id 规则', cfg['onebot']['accounts'][0]['id'].startswith('a'), cfg['onebot']['accounts'][0])

    await store.close()
    shutil.rmtree(TMP, ignore_errors=True)
    print()
    if FAILED:
        print('FAILED: %d 项 → %s' % (len(FAILED), FAILED))
        return 1
    print('ALL PASS')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
