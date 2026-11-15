# -*- coding: utf-8 -*-
"""用户面板：固定菜单 + 功能项 + 文本库/图片库 + 每日 AI 文案。

设计要点（与前端「面板」页签对应）：
  · 群聊必须 @ 才响应；私聊直接发「菜单」即可
  · 菜单是纯文本，不走模型、不进上下文
  · 功能项 content = 文本库 + 图片库；同人同日固定（seed = uid+date+feature）
  · 图片库支持本地图片与外部 API；API 图按天缓存，302 最多跟 3 跳
  · 文本库可开「每日 AI 生成 N 条」，到点自动追加
"""
import asyncio
import hashlib
import json
import os
import re
import time
from datetime import datetime

from . import config, logbuf, llm

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

# 每个会话最近一次菜单的编号映射：key -> (expire_ts, [item_id...])
_MENU = {}
_MENU_TTL = 600
_COOLDOWN = {}
_GEN_TRY = {}


def _cfg_dir():
    return os.path.dirname(os.path.abspath(config.CFG_FILE))


def cache_dir(*parts):
    d = os.path.join(_cfg_dir(), 'panel_cache', *[str(p) for p in parts])
    os.makedirs(d, exist_ok=True)
    return d


def images_dir(pool_id=''):
    d = os.path.join(_cfg_dir(), 'panel_images', str(pool_id or ''))
    os.makedirs(d, exist_ok=True)
    return d


LEVEL_DEFAULTS = ['大吉', '中吉', '小吉', '平']


def ensure_defaults(sec):
    """给老配置补默认功能项与「运势等级」字段。"""
    changed = False
    items = _items(sec)
    if not any(x.get('id') == 'litematic' or '投影解析' in (x.get('aliases') or [])
               for x in items):
        sec.setdefault('items', []).append({
            'id': 'litematic', 'name': '投影解析', 'aliases': ['投影解析', '投影'],
            'desc': '开启后自动解析群里的 .litematic 投影文件', 'type': 'text',
            'text': '@我 投影解析开启功能\n@我 投影解析关闭功能',
            'cooldown': 3, 'show_in_menu': True, 'enabled': True,
        })
        changed = True
    for it in _items(sec):
        if it.get('type') != 'content':
            continue
        if 'levels' in it:
            continue
        if it.get('id') == 'fortune' or it.get('with_level'):
            it['levels'] = list(LEVEL_DEFAULTS)
            it.setdefault('level_prefix', '运势')
            changed = True
    return changed


def section(cfg=None):
    cfg = cfg or config.load()
    sec = cfg.get('panel') or {}
    ensure_defaults(sec)
    return sec


def save_section(sec):
    cfg = config.load()
    cfg['panel'] = sec
    config.save(cfg)
    logbuf.info('panel', '面板配置已保存（%d 个功能项）' % len(sec.get('items') or []))
    return sec


def _items(sec):
    return [x for x in (sec.get('items') or []) if isinstance(x, dict)]


def visible_items(sec):
    return [x for x in _items(sec) if x.get('enabled', True) and x.get('show_in_menu', True)]


def _pool(sec, pid):
    for p in (sec.get('text_pools') or []):
        if p.get('id') == pid:
            return p
    return None


def _image_pool(sec, pid):
    for p in (sec.get('image_pools') or []):
        if p.get('id') == pid:
            return p
    return None


# ---------------------------------------------------------------- 时间 / seed

def now():
    tz = (section().get('timezone') or 'Asia/Shanghai')
    try:
        if ZoneInfo:
            return datetime.now(ZoneInfo(tz))
    except Exception:
        pass
    return datetime.now()


def day_key():
    return now().strftime('%Y-%m-%d')


def seed_of(*parts):
    raw = '|'.join(str(p) for p in parts).encode('utf-8')
    return int(hashlib.sha256(raw).hexdigest()[:12], 16)


# ---------------------------------------------------------------- 菜单

def _two_cols(entries, columns=2):
    """把 [(序号, 名称)] 排成两列，中英文混排按显示宽度补空格。"""
    def w(s):
        return sum(2 if ord(c) > 127 else 1 for c in s)
    cols = max(1, min(4, int(columns or 2)))
    per = (len(entries) + cols - 1) // cols
    blocks = [entries[i:i + per] for i in range(0, len(entries), per)]
    widths = []
    for b in blocks:
        widths.append(max([w('%d. %s' % e) for e in b] or [0]))
    lines = []
    for i in range(per):
        cells = []
        for bi, b in enumerate(blocks):
            if i < len(b):
                s = '%d. %s' % b[i]
                cells.append(s + ' ' * (widths[bi] - w(s) + 4))
        lines.append(''.join(cells).rstrip())
    return lines


def render_menu(sec=None, page=0, columns=None):
    sec = sec or section()
    vis = visible_items(sec)
    if not vis:
        return (sec.get('title') or '雨咯Bot') + '\n\n暂时还没有可用的功能'
    size = max(1, int(sec.get('page_size') or 8))
    pages = [vis[i:i + size] for i in range(0, len(vis), size)]
    page = max(0, min(int(page or 0), len(pages) - 1))
    cur = pages[page]
    start = page * size
    entries = [(start + i + 1, x.get('name') or x.get('id') or '未命名')
               for i, x in enumerate(cur)]
    if page < len(pages) - 1:
        entries.append((start + len(cur) + 1, '更多'))
    lines = [sec.get('title') or '雨咯Bot', '']
    lines.extend(_two_cols(entries, columns or sec.get('columns') or 2))
    hint = sec.get('hint') or '回复数字或功能名即可'
    footer = ('第 %d/%d 页 · ' % (page + 1, len(pages))) if len(pages) > 1 else ''
    lines += ['', footer + hint]
    return '\n'.join(lines)


def remember_menu(key, sec=None, page=0):
    sec = sec or section()
    vis = visible_items(sec)
    size = max(1, int(sec.get('page_size') or 8))
    page = int(page or 0)
    ids = [x.get('id') for x in vis[page * size:(page + 1) * size]]
    _MENU[key] = (time.time() + _MENU_TTL, ids, page)


def resolve_number(key, n):
    hit = _MENU.get(key)
    if not hit:
        return None, 0
    exp, ids, page = hit
    if time.time() > exp:
        _MENU.pop(key, None)
        return None, 0
    idx = int(n) - 1
    if idx < 0 or idx >= len(ids):
        return None, 0
    return ids[idx], page


def match_item(sec, text):
    t = str(text or '').strip().lower()
    if not t:
        return None
    for x in _items(sec):
        if not x.get('enabled', True):
            continue
        names = [x.get('name') or ''] + list(x.get('aliases') or [])
        for nm in names:
            if nm and t == str(nm).strip().lower():
                return x
    return None


def cooldown_ok(key, seconds):
    try:
        seconds = int(seconds or 0)
    except Exception:
        seconds = 0
    if seconds <= 0:
        return True
    now_ts = time.time()
    last = _COOLDOWN.get(key) or 0
    if now_ts - last < seconds:
        return False
    _COOLDOWN[key] = now_ts
    return True


# ---------------------------------------------------------------- 文本库

def _text_of(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get('text') or '')
    return ''


def text_items(pool):
    out = []
    for it in (pool.get('items') or []):
        s = _text_of(it).strip()
        if s:
            out.append(s)
    return out


def snapshot_texts(sec, pool_id, day=None):
    """当天首次使用时冻结文案池，之后编辑/生成都不影响当天结果。"""
    pool = _pool(sec, pool_id)
    if not pool:
        return []
    day = day or day_key()
    p = os.path.join(cache_dir(day), 'pool_%s.json' % re.sub(r'[^A-Za-z0-9_.-]', '_', str(pool_id)))
    try:
        if os.path.isfile(p):
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return [str(x) for x in data]
    except Exception:
        pass
    items = text_items(pool)
    try:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False)
    except Exception as e:
        logbuf.debug('panel', '写文案快照失败：%s' % str(e)[:100])
    return items


# ---------------------------------------------------------------- 图片库

def image_cache_path(day, feature, uid):
    return os.path.join(cache_dir(day), 'img_%s_%s.jpg' % (feature, uid))


async def fetch_image(url, dest, timeout=10, max_bytes=8 * 1024 * 1024, max_redirects=3):
    import aiohttp
    timeout = max(3, min(30, int(timeout or 10)))
    max_bytes = max(64 * 1024, min(32 * 1024 * 1024, int(max_bytes or 8 * 1024 * 1024)))
    try:
        to = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=to) as sess:
            async with sess.get(url, allow_redirects=True, max_redirects=max_redirects) as r:
                if r.status >= 400:
                    raise RuntimeError('HTTP %s' % r.status)
                ctype = (r.headers.get('Content-Type') or '').lower()
                if ctype and not ctype.startswith('image/'):
                    raise RuntimeError('不是图片：%s' % ctype)
                data = bytearray()
                async for chunk in r.content.iter_chunked(64 * 1024):
                    data.extend(chunk)
                    if len(data) > max_bytes:
                        raise RuntimeError('图片超过 %dMB' % (max_bytes // 1024 // 1024))
                if not data:
                    raise RuntimeError('图片为空')
                tmp = dest + '.tmp'
                with open(tmp, 'wb') as f:
                    f.write(data)
                os.replace(tmp, dest)
                return True
    except Exception as e:
        logbuf.warn('panel', '拉取图片失败 %s：%s' % (str(url)[:80], str(e)[:120]))
        try:
            if os.path.isfile(dest):
                os.remove(dest)
        except Exception:
            pass
        return False


async def image_for(sec, item, uid, day=None):
    """返回本地图片绝对路径；没有/失败返回空串。"""
    pid = item.get('image_pool') or ''
    pool = _image_pool(sec, pid)
    if not pool or not pool.get('enabled', True):
        return ''
    day = day or day_key()
    feat = item.get('id') or 'item'
    if pool.get('source') == 'api':
        api = pool.get('api') or {}
        url = str(api.get('url') or '').strip()
        if not url:
            return ''
        dest = image_cache_path(day, feat, uid)
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            return dest
        ok = await fetch_image(url, dest, api.get('timeout') or 10,
                               api.get('max_bytes') or 8 * 1024 * 1024,
                               api.get('max_redirects') or 3)
        if not ok:
            # 外部图站偶尔超时/302 抖动：隔 1 秒再试一次
            await asyncio.sleep(1)
            ok = await fetch_image(url, dest, api.get('timeout') or 10,
                                   api.get('max_bytes') or 8 * 1024 * 1024,
                                   api.get('max_redirects') or 3)
        return dest if ok else ''
    files = [x for x in (pool.get('items') or []) if x]
    if not files:
        return ''
    idx = seed_of(feat, uid, day) % len(files)
    name = files[idx]
    if os.path.isabs(name):
        return name if os.path.isfile(name) else ''
    p = os.path.join(images_dir(pool.get('id')), name)
    return p if os.path.isfile(p) else ''


# ---------------------------------------------------------------- 功能项

async def build_reply(sec, item, uid, nick='', day=None):
    """执行一个 content/text 功能项，返回 (文本, 图片路径)。"""
    day = day or day_key()
    ensure_defaults(sec)
    text = ''
    image = ''
    typ = item.get('type') or 'content'
    if typ == 'content':
        pool = _pool(sec, item.get('text_pool') or '')
        texts = snapshot_texts(sec, item.get('text_pool') or '', day)
        if texts:
            idx = seed_of(item.get('id'), uid, day) % len(texts)
            text = texts[idx]
        if item.get('image_pool'):
            image = await image_for(sec, item, uid, day)
    elif typ == 'text':
        text = str(item.get('text') or '')
    if text:
        text = text.replace('{nick}', nick or str(uid)).replace('{uid}', str(uid))
        text = text.replace('{date}', day).replace('{group}', '')
        # 运势等级：单独一次种子，和文案/图片互不影响
        levels = [str(x).strip() for x in (item.get('levels') or []) if str(x).strip()]
        if levels:
            lv = levels[seed_of('level', item.get('id'), uid, day) % len(levels)]
            prefix = str(item.get('level_prefix') or '运势')
            text = '%s:%s\n%s' % (prefix, lv, text)
    return text, image


# ---------------------------------------------------------------- 每日 AI 文案

def _default_gen_prompt(count):
    return ('你是文案作者。写一条「今日运势」，150 字左右（必须 100–200 字），'
            '分别写早上、工作/学习、人际、晚上各一句，包含一句总评和宜 / 忌。'
            '直接输出正文，不要编号、不要解释。')


def _parse_texts(raw):
    s = str(raw or '').strip()
    s = re.sub(r'^```(?:json)?', '', s).strip()
    s = re.sub(r'```$', '', s).strip()
    m = re.search(r'\[[\s\S]*\]', s)
    if m:
        s = m.group(0)
    try:
        data = json.loads(s)
        if isinstance(data, list):
            out = []
            for x in data:
                if isinstance(x, str):
                    out.append(x.strip())
                elif isinstance(x, dict):
                    t = (x.get('text') or x.get('content') or x.get('运势')
                         or x.get('文案') or '')
                    if not t:
                        vals = [str(v) for v in x.values()
                                if isinstance(v, (str, int, float))]
                        t = ' '.join(vals)
                    out.append(str(t).strip())
            return [x for x in out if x]
    except Exception:
        pass
    # 再兜底：按行拆，去掉编号/项目符号
    out = []
    for line in s.splitlines():
        line = re.sub(r'^\s*(?:[-*•·]|\d+[.、)）])\s*', '', line).strip()
        line = line.strip('"“”\' ')
        if line:
            out.append(line)
    return out


def _usable_text(t):
    """校验并清洗一条文案：100–200 字、不是 JSON/代码块、去掉换行。"""
    t = (t or '').strip()
    if len(t) < 100 or len(t) > 200:
        return ''
    if t.startswith(('[', '{', '```')) or '```' in t or '"总评"' in t:
        return ''
    return re.sub(r'[ \t]*\n+[ \t]*', '', t)


async def generate_into_pool(pool_id, count=None, cfg=None):
    """调模型生成 N 条文案并追加到文本池，返回新增条数。"""
    cfg = cfg or config.load()
    sec = section(cfg)
    pool = _pool(sec, pool_id)
    if not pool:
        raise RuntimeError('文本组不存在：%s' % pool_id)
    ai = pool.get('ai_daily') or {}
    n = max(1, min(50, int(count or ai.get('count') or 10)))
    pid = str(ai.get('provider_id') or '')
    provider = config.get_provider(cfg, pid, {}) if pid else config.get_provider(cfg, '', {})
    if not provider:
        raise RuntimeError('没有可用的模型提供商')
    base_prompt = str(ai.get('prompt') or _default_gen_prompt(1)).replace('{count}', '1')
    enforce = '\n\n只输出一条正文，不要 JSON、不要编号。'
    sem = asyncio.Semaphore(3)

    async def _one():
        async with sem:
            for _try in range(2):
                try:
                    t = await llm.chat(provider,
                                       [{'role': 'user', 'content': base_prompt + enforce}],
                                       system='只输出正文，不要编号、不要解释。',
                                       max_tokens=1024, temperature=0.9)
                    t = _usable_text(t)
                    if t:
                        return t
                except Exception as e:
                    logbuf.warn('panel', '单条生成失败：%s' % str(e)[:100])
                await asyncio.sleep(0.2)
            return ''

    results = await asyncio.gather(*[_one() for _ in range(n)])
    cand = [t for t in results if t]
    logbuf.info('panel', '生成可用：%d/%d（长度 %s）' % (
        len(cand), n, ','.join(str(len(t)) for t in cand[:10])))
    if not cand:
        logbuf.warn('panel', '本批没有 100–200 字的可用文案（%d 条候选）' % n)
        raise RuntimeError('模型没有返回可用文案（100–200 字）')
    existing = set(text_items(pool))
    today = day_key()
    added = []
    short = 0
    for t in cand[:n]:
        t = _usable_text(t)
        if not t or t in existing:
            continue
        # 长度硬约束：100–200 字（超短的模型废话不要）
        if len(t) < 100 or len(t) > 200:
            short += 1
            continue
        existing.add(t)
        # 只记生成日期，不做其它分类
        added.append({'text': t, 'source': 'ai', 'gen_date': today})
    if short:
        logbuf.info('panel', '丢弃 %d 条长度不在 100–200 字的文案' % short)
    if not added:
        return 0
    pool.setdefault('items', []).extend(added)
    # 超上限：只裁掉最旧的 AI 条目，手动条目不动
    keep_max = int(ai.get('keep_max') or 300)
    items = pool['items']
    if keep_max > 0 and len(items) > keep_max:
        overflow = len(items) - keep_max
        kept = []
        for it in items:
            if overflow > 0 and isinstance(it, dict) and it.get('source') == 'ai':
                overflow -= 1
                continue
            kept.append(it)
        pool['items'] = kept
    ai['last_run_date'] = today
    ai['last_run_count'] = len(added)
    ai['last_run_at'] = int(time.time())
    pool['ai_daily'] = ai
    save_section(sec)
    logbuf.info('panel', '每日文案生成：%s +%d 条（共 %d）' % (pool.get('name') or pool_id,
                                                             len(added), len(pool['items'])))
    return len(added)


async def _tick(cfg):
    sec = section(cfg)
    if not sec.get('enabled', True):
        return
    cur = now()
    day = cur.strftime('%Y-%m-%d')
    hhmm = cur.strftime('%H:%M')
    for pool in (sec.get('text_pools') or []):
        ai = pool.get('ai_daily') or {}
        if not ai.get('enabled'):
            continue
        if ai.get('last_run_date') == day:
            continue
        target = str(ai.get('time') or '00:10')
        if hhmm < target:
            continue
        pid = str(pool.get('id') or '')
        # 失败退避：同一天最多试 3 次，两次之间至少隔 10 分钟，避免每分钟打模型
        st = _GEN_TRY.get(pid) or {}
        if st.get('day') == day:
            if int(st.get('n') or 0) >= 3:
                continue
            if time.time() - float(st.get('ts') or 0) < 600:
                continue
        _GEN_TRY[pid] = {'day': day, 'n': int(st.get('n') or 0) + 1, 'ts': time.time()}
        try:
            await generate_into_pool(pool.get('id'), ai.get('count'), cfg)
            _GEN_TRY.pop(pid, None)
        except Exception as e:
            logbuf.warn('panel', '每日文案生成失败（%s）：%s' % (pid, str(e)[:160]))


async def scheduler(load_cfg=None):
    """每分钟检查一次是否有到点的文案生成任务。"""
    load_cfg = load_cfg or config.load
    # 启动时补一次：进程刚好在生成时间之后重启也不会漏
    while True:
        try:
            await _tick(load_cfg())
        except Exception as e:
            logbuf.warn('panel', '文案调度异常：%s' % str(e)[:160])
        await asyncio.sleep(60)


def cleanup_cache(days=7):
    """清理超过 N 天的图片缓存与文案快照。"""
    root = os.path.join(_cfg_dir(), 'panel_cache')
    if not os.path.isdir(root):
        return 0
    cutoff = time.time() - days * 86400
    n = 0
    for name in os.listdir(root):
        p = os.path.join(root, name)
        try:
            if os.path.isdir(p) and os.path.getmtime(p) < cutoff:
                for f in os.listdir(p):
                    try:
                        os.remove(os.path.join(p, f))
                    except Exception:
                        pass
                os.rmdir(p)
                n += 1
        except Exception:
            continue
    return n


def append_image(pool_id, filename, data):
    """保存本地上传的图片，返回文件名。"""
    d = images_dir(pool_id)
    fn = re.sub(r'[^A-Za-z0-9_.-]', '_', filename or 'image.jpg')
    if not os.path.splitext(fn)[1]:
        fn += '.jpg'
    p = os.path.join(d, fn)
    i = 1
    base, ext = os.path.splitext(fn)
    while os.path.exists(p):
        p = os.path.join(d, '%s_%d%s' % (base, i, ext))
        i += 1
    with open(p, 'wb') as f:
        f.write(data)
    return os.path.basename(p)
