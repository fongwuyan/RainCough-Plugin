#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LaiZhangTu 插件后端（接口库 v4）。

由 E:/jiaob/来张图 的 QQ 脚本插件（main.java + settings.html + ImageUtil.java）
移植到 RainCough 面板：保留 Lolicon API 标签检索、尺寸选择、图片代理、翻转、
随机模糊、冷却与本地缓存；QQ 消息相关的 @ / 撤回 / 卡片发送改为面板内的
配置页、历史记录与缓存管理。

图片由主系统代发：/api/plugins/laizhangtu/cache/<file>
对应本插件目录下的 cache/（见 internal/pluginx/rest.go:serveFromPanelURL）。

内容安全：本插件不接受任何涉及未成年人的性化标签，也会丢弃 API 返回结果中
命中同一规则的作品；不随插件分发任何图片素材。详见 README.md。
"""
import hashlib
import json
import os
import random
import re
import secrets
import sys
import threading
import time
from datetime import datetime
from io import BytesIO

import requests as http_req
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcplugin as rc

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(PLUGIN_DIR, 'cache')
CONFIG_FILE = os.path.join(PLUGIN_DIR, 'config.json')
HISTORY_FILE = os.path.join(PLUGIN_DIR, 'history.json')
SEEN_FILE = os.path.join(PLUGIN_DIR, 'seen.json')
LOLICON_API = 'https://api.lolicon.app/setu/v2'
PANEL_CACHE_PREFIX = '/api/plugins/laizhangtu/cache/'
SIZE_KEYS = ('original', 'regular', 'small')
# 实测 2026-11-07：num>20 时 API 静默返回 0 条（HTTP 200、error=''），所以必须自己夹住。
SEARCH_MAX_NUM = 20
SEARCH_DEFAULT_NUM = 8
SEARCH_TTL = 1800            # 搜索结果会话有效期（秒）；插件重启后需要重新搜索

NAME = 'laizhangtu'
LABEL = '来张图'
VERSION = '1.1.0'

DEFAULT_CONFIG = {
    'show_info': True,          # 显示标题/作者/pid/uid/尺寸/标签
    'exclude_ai': True,         # 排除 AI 生成作品
    'flip_h': True,             # 水平翻转（与原脚本默认值一致）
    'flip_v': False,            # 垂直翻转
    'blur_chance': 5,           # 「冲多了」随机模糊概率 0-100
    'img_size': 2,              # 0 原图 / 1 regular / 2 small（默认小图：实测代理下原图 1.5MB 要 70s+）
    'proxy': 'i.pixiv.re',      # 图片代理域名（实测唯一稳定可用；pixiv.re 会 404）
    'r18': False,               # 默认关闭；开启后 r18=2（混合）
    'exclude_seen': False,      # 排除已获取过的 pid
    'cool_down': 0,             # 两次获取之间的最小间隔（秒）
    'max_cache_mb': 256,        # 缓存上限，超出按时间删最旧
    'fetch_timeout': 20,        # 整次取图的总预算（秒），前端按同一数值放宽面板 invoke 超时
}

# 面板 invoke 默认 15s（RainCough-Core/internal/pluginx/http.go:277）。
# 实测：搜索接口 1.3~1.9s，图片代理 TTFB 2~7s，原图 1.5~2MB 全量下载可达 70s+；
# requests 的 read timeout 只管「两次读之间」，慢速滴流不会触发，所以必须
# 自己用单调时钟卡总预算，并在下载过程中逐块检查，否则面板必然先超时。
FETCH_HINT = '建议到「设置」把图片规格改成「小图 small」、调大「取图超时」，或更换图片代理域名。'
MAX_IMAGE_BYTES = 20 * 1024 * 1024

# ---- 内容安全 ---------------------------------------------------------------
# 下列词指向未成年人的性化内容，输入标签与 API 返回的作品标签/标题都要过滤。
# 后端是唯一权威校验点：前端也做提示，但绕过前端直接调接口同样拦得住。
_BLOCKED = re.compile(
    r'幼女|幼児|幼小|幼龄|稚女|稚児|萝莉|罗莉|正太|未成年|小学生|中学生|女童|男童|儿童|孩童'
    r'|ロリ|ショタ|児童|女子高生'
    r'|\bchild(?:ren)?\b|\bkids?\b|\bunderage\b|\bminors?\b|\bpreteen\b'
    r'|\btoddler\b|\bjailbait\b|\bloli(?:con|s)?\b|\bshotacon\b|\bshota\b',
    re.IGNORECASE,
)
BLOCK_MESSAGE = '请求包含不允许的内容（涉及未成年人的性化内容），已拒绝。'


def is_blocked(text):
    return bool(_BLOCKED.search(str(text or '')))


def _check_request_tags(groups):
    for g in groups:
        if is_blocked(g):
            raise rc.RCError(3000, BLOCK_MESSAGE)


def _check_result_item(item):
    if is_blocked(item.get('title')):
        return False
    for t in item.get('tags') or []:
        if is_blocked(t):
            return False
    return True


# ---- 配置 / 数据文件 ---------------------------------------------------------

def load_config():
    cfg = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg if isinstance(cfg, dict) else {})
    return normalize_config(merged)


def normalize_config(cfg):
    """把任意输入收敛到合法范围，避免前端传脏值把插件搞崩。"""
    out = dict(DEFAULT_CONFIG)
    out.update(cfg)
    for k in ('show_info', 'exclude_ai', 'flip_h', 'flip_v', 'r18', 'exclude_seen'):
        out[k] = bool(out.get(k))
    for k, lo, hi in (('blur_chance', 0, 100), ('img_size', 0, 2),
                      ('cool_down', 0, 3600), ('max_cache_mb', 16, 4096),
                      ('fetch_timeout', 5, 180)):
        try:
            out[k] = max(lo, min(hi, int(out.get(k))))
        except (TypeError, ValueError):
            out[k] = DEFAULT_CONFIG[k]
    proxy = str(out.get('proxy') or '').strip().lower()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.\-]*', proxy):
        proxy = DEFAULT_CONFIG['proxy']
    out['proxy'] = proxy
    return out


def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _read_json_list(path):
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def _write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---- 缓存 -------------------------------------------------------------------

def _cache_files():
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        return [os.path.join(CACHE_DIR, f) for f in os.listdir(CACHE_DIR)
                if os.path.isfile(os.path.join(CACHE_DIR, f))]
    except Exception:
        return []


def cache_stats(cfg=None):
    cfg = cfg or load_config()
    files = _cache_files()
    total = 0
    for p in files:
        try:
            total += os.path.getsize(p)
        except OSError:
            pass
    limit = int(cfg.get('max_cache_mb', 256)) * 1024 * 1024
    return {'count': len(files), 'bytes': total, 'mb': round(total / 1048576, 2),
            'limit_mb': int(cfg.get('max_cache_mb', 256)), 'dir': CACHE_DIR,
            'percent': round(total / limit * 100, 1) if limit else 0}


def trim_cache(cfg):
    """超过上限就按修改时间删最旧的文件（原脚本是每次启动全清）。"""
    limit = int(cfg.get('max_cache_mb', 256)) * 1024 * 1024
    files = []
    for p in _cache_files():
        try:
            files.append((os.path.getmtime(p), os.path.getsize(p), p))
        except OSError:
            pass
    files.sort()
    total = sum(s for _, s, _ in files)
    removed = 0
    for _, size, p in files:
        if total <= limit:
            break
        try:
            os.remove(p)
            total -= size
            removed += 1
        except OSError:
            pass
    return removed


# ---- 网络：整次取图共用一个时间预算 -----------------------------------------

class _Budget:
    """单调时钟预算：所有网络请求都只能花「剩余时间」，超时就说人话。"""

    def __init__(self, seconds):
        self.total = float(seconds)
        self.start = time.monotonic()

    def elapsed(self):
        return time.monotonic() - self.start

    def left(self):
        return self.total - self.elapsed()

    def require(self, stage, min_left=1.0):
        left = self.left()
        if left < min_left:
            raise rc.RCError(3000, '%s超时（本次取图已等待 %.0f 秒，预算 %.0f 秒）：%s'
                             % (stage, self.elapsed(), self.total, FETCH_HINT))
        return left

    def req_timeout(self, stage, cap=None):
        left = self.require(stage)
        read = left if cap is None else min(left, float(cap))
        return (min(3.0, max(1.0, read)), max(1.0, read))


def _brief(e):
    return re.sub(r'\s+', ' ', str(e))[:110]


def _api_error(err):
    """API 的 error 字段也可能携带限流文案（HTTP 200 或 429 都见过）。"""
    text = re.sub(r'\s+', ' ', str(err or ''))[:120]
    if re.search(r'429|限流|频繁|太快|太多|稍后|slow down|rate limit', text, re.I):
        return 'API 触发限流，请稍等 20~30 秒再试，避免连续高频搜索（%s）' % text
    return 'API 错误: %s' % text


def _net_error(stage, e, waited=None):
    """把 requests 的异常统一翻译成中文 RCError，避免面板回一串英文堆栈。"""
    if isinstance(e, rc.RCError):
        return e
    if isinstance(e, http_req.exceptions.Timeout):
        msg = ('%s超时（等待 %.1f 秒）：%s' % (stage, waited, FETCH_HINT)) if waited \
            else ('%s超时：%s' % (stage, FETCH_HINT))
    elif isinstance(e, http_req.exceptions.HTTPError):
        resp = getattr(e, 'response', None)
        code = getattr(resp, 'status_code', None) if resp is not None else None
        if code == 429:
            msg = '%s触发 API 限流（HTTP 429），请稍等 20~30 秒再试，避免连续高频搜索。' % stage
        else:
            msg = '%s返回 HTTP %s，请稍后重试或更换代理域名。' % (stage, code or '?')
    elif isinstance(e, http_req.exceptions.RequestException):
        msg = '%s失败：%s %s' % (stage, _brief(e), FETCH_HINT)
    else:
        msg = '%s异常：%s %s' % (stage, _brief(e), FETCH_HINT)
    return rc.RCError(3000, msg)


def _http_get(budget, url, params, stage, cap=None):
    budget.require(stage)
    to = budget.req_timeout(stage, cap)
    try:
        resp = http_req.get(url, params=params, timeout=to)
        resp.raise_for_status()
        return resp
    except Exception as e:
        raise _net_error(stage, e, to[1])


def _download_bytes(budget, url, stage='图片下载'):
    """流式下载，逐块检查总预算——慢速滴流也能在预算内被掐断。"""
    budget.require(stage)
    to = budget.req_timeout(stage)
    chunks, size = [], 0
    try:
        resp = http_req.get(url, timeout=to, stream=True)
        try:
            resp.raise_for_status()
            for chunk in resp.iter_content(65536):
                if not chunk:
                    continue
                size += len(chunk)
                if size > MAX_IMAGE_BYTES:
                    raise rc.RCError(3000, '图片超过 %d MB，已放弃：%s'
                                     % (MAX_IMAGE_BYTES // 1048576, FETCH_HINT))
                # 每块都问一次预算，避免「每秒来几个字节」把 read timeout 骗过去
                budget.require(stage, 0.2)
                chunks.append(chunk)
        finally:
            close = getattr(resp, 'close', None)
            if close:
                close()
    except Exception as e:
        raise _net_error(stage, e, to[1])
    if not chunks:
        raise rc.RCError(3000, '%s未返回数据（0 字节），请更换代理域名后重试。' % stage)
    return b''.join(chunks)


# ---- 核心逻辑 ---------------------------------------------------------------

_last_fetch = {'ts': 0.0}
_fetch_lock = threading.Lock()

# ---- 搜索结果会话 ------------------------------------------------------------
# 实测 API 会忽略 pid 参数（按 pid 请求仍返回另一张随机作品），所以「在结果列表里
# 选中第 N 条再取图」不能靠 pid 复现。这里用不透明 id 在服务端暂存该次结果的
# 图片地址，前端只回传 id：既保证选中的就是看到的那张，也避免调用方传入任意
# URL 造成 SSRF。会话仅存内存，插件重启或超过 SEARCH_TTL 后需重新搜索。
_search_lock = threading.Lock()
_search_sessions = {}    # id -> {item, size_key, groups, r18, ts}


def _prune_sessions_locked():
    now = time.time()
    for k in [k for k, v in _search_sessions.items() if now - v['ts'] > SEARCH_TTL]:
        del _search_sessions[k]
    if len(_search_sessions) > 200:
        oldest = sorted(_search_sessions, key=lambda k: _search_sessions[k]['ts'])
        for k in oldest[:len(oldest) - 200]:
            del _search_sessions[k]


def _session_put(item, size_key, groups, r18):
    sid = secrets.token_hex(10)
    with _search_lock:
        _prune_sessions_locked()
        _search_sessions[sid] = {'item': item, 'size_key': size_key,
                                 'groups': groups, 'r18': r18, 'ts': time.time()}
    return sid


def _session_get(sid):
    with _search_lock:
        entry = _search_sessions.get(sid)
        if entry and time.time() - entry['ts'] > SEARCH_TTL:
            del _search_sessions[sid]
            entry = None
        return dict(entry) if entry else None


# ---- API 搜索 ---------------------------------------------------------------

def _api_search(budget, cfg, groups, r18, size_key, num, stage='搜索接口'):
    """发一次搜索请求，返回 API 的 data 列表（尚未做内容过滤）。"""
    budget.require('搜索', 2.0)
    resp = _http_get(budget, LOLICON_API,
                     _api_params(cfg, groups, r18, size_key, num), stage, cap=8)
    try:
        result = resp.json()
    except Exception:
        raise rc.RCError(3000, '搜索接口返回的不是合法 JSON，请稍后重试或更换代理域名。')
    if not isinstance(result, dict):
        raise rc.RCError(3000, '搜索接口返回格式异常，请稍后重试。')
    if result.get('error'):
        raise rc.RCError(3000, _api_error(result['error']))
    return [x for x in (result.get('data') or []) if isinstance(x, dict)]


def parse_tag_expr(expr):
    """把「A|B&C」拆成 Lolicon 的多个 tag 参数：& 为与，| 留在组内表示或。

    同时也接受逗号/空格/中文逗号作为「与」的分隔，方便面板里输入。
    """
    parts = re.split(r'[&＋,，、\s]+', str(expr or '').strip())
    return [p.strip() for p in parts if p.strip()][:5]


def _parse_groups(data):
    """fetch / search 共用：解析 tag 表达式或 tags 数组，并做硬性内容校验。"""
    groups = data.get('tags') or []
    if isinstance(groups, list):
        groups = [str(g).strip() for g in groups if str(g).strip()][:5]
    else:
        groups = []
    if not groups:
        groups = parse_tag_expr(data.get('tag', ''))
    _check_request_tags(groups)
    return groups


def _clamp_num(value, default=SEARCH_DEFAULT_NUM):
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = default
    return max(1, min(SEARCH_MAX_NUM, n))


def _api_params(cfg, groups, r18, size_key=None, num=1):
    key = size_key or SIZE_KEYS[int(cfg.get('img_size', 2))]
    params = [
        ('proxy', cfg.get('proxy', 'i.pixiv.re')),
        ('r18', 2 if r18 else 0),
        ('size', key),
        ('num', num),
    ]
    if cfg.get('exclude_ai', True):
        params.append(('excludeAI', 'true'))
    for g in groups:
        params.append(('tag', g))
    return params


def _search_item(budget, cfg, groups, r18, size_key, seen):
    """在预算内搜索（必要时重试），返回合规且未见过的作品。"""
    for _ in range(8):
        items = _api_search(budget, cfg, groups, r18, size_key, 1)
        if not items:
            raise rc.RCError(3000, '没有找到关于「%s」的插画喵！' % (' & '.join(groups) if groups else '随机'))
        candidate = items[0]
        if not _check_result_item(candidate):
            continue
        if cfg.get('exclude_seen') and str(candidate.get('pid')) in seen:
            continue
        return candidate
    raise rc.RCError(3000, '连续取到的作品都不符合内容规则或已看过，请换个标签再试。')


def _pick_url(item, size_key):
    urls = item.get('urls') or {}
    # API 只返回所请求规格的那一个 key，所以要能兜到任意一个可用地址
    return urls.get(size_key) or urls.get('original') or next(iter(urls.values()), None)


def _public_item(item, sid, size_key):
    """搜索结果只给元数据 + 不透明 id；thumb 由前端按需加载，默认不展示。"""
    return {
        'id': sid, 'pid': item.get('pid'), 'uid': item.get('uid'),
        'title': item.get('title'), 'author': item.get('author'),
        'width': item.get('width'), 'height': item.get('height'),
        'tags': item.get('tags') or [], 'r18': bool(item.get('r18')),
        'size': size_key, 'thumb': _pick_url(item, size_key),
    }


def _materialize(cfg, item, size_key, budget, groups, r18, allow_fallback, source):
    """把「已选定的作品」下载、处理、落盘并记入历史。fetch 与 pick 共用。"""
    img_url = _pick_url(item, size_key)
    if not img_url:
        raise rc.RCError(3000, 'API 未返回图片地址')

    raw, final_url, degraded = None, img_url, False
    try:
        raw = _download_bytes(budget, img_url)
    except rc.RCError as first_err:
        # 原图/中等在这条代理链上实测要几十秒。预算还够时自动降级到 small
        # （实测约 30KB），并把代理换回唯一实测可用的默认值，兼顾代理填错。
        # pick 是「选中指定作品」，重新搜索会换成别的作品，所以不允许降级。
        if allow_fallback and size_key != 'small' and budget.left() > 5:
            fb = dict(cfg)
            fb['proxy'] = DEFAULT_CONFIG['proxy']
            try:
                fb_item = _search_item(budget, fb, groups, r18, 'small', set())
                fb_url = _pick_url(fb_item, 'small')
                if fb_url:
                    raw = _download_bytes(budget, fb_url, stage='小图降级下载')
                    item, size_key, final_url, degraded = fb_item, 'small', fb_url, True
            except rc.RCError:
                pass
        if raw is None:
            if not allow_fallback and size_key != 'small':
                raise rc.RCError(3000, '%s 该作品当前规格下载失败，请把图片规格改成「小图 small」后重新搜索。'
                                 % first_err.message)
            raise first_err

    if cfg.get('exclude_seen'):
        seen = set(str(x) for x in _read_json_list(SEEN_FILE))
        seen.add(str(item.get('pid')))
        _write_json(SEEN_FILE, sorted(seen)[-10000:])

    try:
        probe = Image.open(BytesIO(raw))
        probe.verify()
    except Exception as e:
        raise rc.RCError(3000, '图片解析失败 (PID %s, %d bytes): %s' % (item.get('pid'), len(raw), e))
    img = Image.open(BytesIO(raw))

    if cfg.get('flip_h'):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if cfg.get('flip_v'):
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    blurred = False
    if int(cfg.get('blur_chance', 5)) > 0 and random.randint(0, 99) < int(cfg['blur_chance']):
        img = img.filter(ImageFilter.GaussianBlur(radius=20))
        blurred = True
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    os.makedirs(CACHE_DIR, exist_ok=True)
    digest = hashlib.md5(raw).hexdigest()[:10]
    filename = 'pid_%s_%s.jpg' % (item.get('pid'), digest)
    img.save(os.path.join(CACHE_DIR, filename), 'JPEG', quality=92)
    removed = trim_cache(cfg)

    record = {
        'pid': item.get('pid'), 'uid': item.get('uid'),
        'title': item.get('title'), 'author': item.get('author'),
        'width': item.get('width'), 'height': item.get('height'),
        'tags': item.get('tags') or [], 'r18': bool(item.get('r18')),
        'url': PANEL_CACHE_PREFIX + filename, 'file': filename,
        'original_url': final_url, 'size': size_key,
        'is_blurred': blurred, 'show_info': bool(cfg.get('show_info')),
        'degraded': degraded, 'source': source,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cache_evicted': removed,
    }
    history = _read_json_list(HISTORY_FILE)
    history.insert(0, record)
    _write_json(HISTORY_FILE, history[:100])
    return record


def fetch_one(cfg, groups, r18, budget):
    """随机取一张：先搜索，再物化。全程受 budget 约束。"""
    seen = set(str(x) for x in _read_json_list(SEEN_FILE)) if cfg.get('exclude_seen') else set()
    size_key = SIZE_KEYS[int(cfg.get('img_size', 2))]
    item = _search_item(budget, cfg, groups, r18, size_key, seen)
    return _materialize(cfg, item, size_key, budget, groups, r18, True, 'fetch')


# ---- 接口实现（与 plugin.json 一一对应） -------------------------------------

@rc.interface('laizhangtu.info')
def ls_info(params):
    return {'name': NAME, 'label': LABEL, 'version': VERSION, 'lang': 'python',
            'description': 'Lolicon 插画：标签搜索结果列表、随机取图、图片处理与本地缓存',
            'source': '由 QQ 脚本插件「来张涩图」(main.java) 迁移',
            'safety': '拒绝涉及未成年人的性化标签与作品；不分发任何图片素材'}


@rc.interface('laizhangtu.config.get')
def ls_config_get(params):
    return load_config()


@rc.interface('laizhangtu.config.save')
def ls_config_save(params):
    data = params if isinstance(params, dict) else {}
    cfg = normalize_config({**load_config(), **data})
    save_config(cfg)
    return {'message': '设置已保存', 'config': cfg}


@rc.interface('laizhangtu.fetch')
def ls_fetch(params):
    data = params if isinstance(params, dict) else {}
    cfg = load_config()
    groups = _parse_groups(data)
    r18 = bool(data['r18']) if 'r18' in data else bool(cfg.get('r18'))
    budget = _Budget(float(cfg.get('fetch_timeout', DEFAULT_CONFIG['fetch_timeout'])))
    # 并发时别在锁上干等（SDK 是每请求一个线程），否则后到的请求会白等满面板超时
    if not _fetch_lock.acquire(timeout=min(2.0, max(0.1, budget.left() - 1))):
        raise rc.RCError(3000, '上一次取图还在进行，请稍后再试。')
    try:
        cd = int(cfg.get('cool_down', 0))
        wait = cd - (time.time() - _last_fetch['ts'])
        if cd > 0 and _last_fetch['ts'] > 0 and wait > 0:
            raise rc.RCError(3000, '正在冷却喵，还有 %d 秒才能再取一张！' % int(wait + 0.999))
        record = fetch_one(cfg, groups, r18, budget)
        _last_fetch['ts'] = time.time()   # 失败不消耗冷却
    finally:
        _fetch_lock.release()
    return {'items': [record]}


@rc.interface('laizhangtu.search')
def ls_search(params):
    """按标签搜索，返回 ≤20 条元数据（不下载图片、不落盘、不写历史）。"""
    data = params if isinstance(params, dict) else {}
    cfg = load_config()
    groups = _parse_groups(data)
    num = _clamp_num(data.get('num'))
    r18 = bool(data['r18']) if 'r18' in data else bool(cfg.get('r18'))
    size_key = SIZE_KEYS[int(cfg.get('img_size', 2))]
    # 搜索只发一次 API（实测 1.3~1.9s），不下载图片，预算封顶 20s 即可。
    budget = _Budget(min(float(cfg.get('fetch_timeout', 20)), 20.0))
    started = time.monotonic()
    items = _api_search(budget, cfg, groups, r18, size_key, num)

    seen = set(str(x) for x in _read_json_list(SEEN_FILE)) if cfg.get('exclude_seen') else set()
    out, filtered, skipped = [], 0, 0
    for it in items:
        if not _check_result_item(it):
            filtered += 1
            continue
        if cfg.get('exclude_seen') and str(it.get('pid')) in seen:
            skipped += 1
            continue
        out.append(_public_item(it, _session_put(it, size_key, groups, r18), size_key))
    label = ' & '.join(groups) if groups else '随机'
    return {
        'items': out, 'num': num, 'total': len(items), 'returned': len(out),
        'filtered': filtered, 'skipped_seen': skipped,
        'tag': label, 'size': size_key, 'r18': r18,
        'elapsed_ms': int((time.monotonic() - started) * 1000),
        'max_num': SEARCH_MAX_NUM, 'expires_in': SEARCH_TTL,
        'message': ('没有找到关于「%s」的插画喵！' % label) if not items else '',
    }


@rc.interface('laizhangtu.pick')
def ls_pick(params):
    """选中搜索结果里的某一条：按会话 id 取回该作品并下载、处理、落盘。"""
    data = params if isinstance(params, dict) else {}
    entry = _session_get(str(data.get('id') or ''))
    if not entry:
        raise rc.RCError(3000, '搜索结果已失效或不存在（有效期 %d 分钟），请重新搜索后再选择。'
                         % (SEARCH_TTL // 60))
    item = entry['item']
    if not _check_result_item(item):
        raise rc.RCError(3000, BLOCK_MESSAGE)

    cfg = load_config()
    budget = _Budget(float(cfg.get('fetch_timeout', DEFAULT_CONFIG['fetch_timeout'])))
    if not _fetch_lock.acquire(timeout=min(2.0, max(0.1, budget.left() - 1))):
        raise rc.RCError(3000, '上一次取图还在进行，请稍后再试。')
    try:
        cd = int(cfg.get('cool_down', 0))
        wait = cd - (time.time() - _last_fetch['ts'])
        if cd > 0 and _last_fetch['ts'] > 0 and wait > 0:
            raise rc.RCError(3000, '正在冷却喵，还有 %d 秒才能再取一张！' % int(wait + 0.999))
        record = _materialize(cfg, item, entry['size_key'], budget,
                              entry['groups'], entry['r18'], False, 'pick')
        _last_fetch['ts'] = time.time()
    finally:
        _fetch_lock.release()
    return {'items': [record]}


@rc.interface('laizhangtu.history.list')
def ls_history_list(params):
    return {'history': _read_json_list(HISTORY_FILE)}


@rc.interface('laizhangtu.history.clear')
def ls_history_clear(params):
    for f in (HISTORY_FILE, SEEN_FILE):
        try:
            if os.path.isfile(f):
                os.remove(f)
        except OSError:
            pass
    return {'message': '历史与已见记录已清空（缓存图片保留）'}


@rc.interface('laizhangtu.cache.stats')
def ls_cache_stats(params):
    return cache_stats()


@rc.interface('laizhangtu.cache.clear')
def ls_cache_clear(params):
    removed = 0
    for p in _cache_files():
        try:
            os.remove(p)
            removed += 1
        except OSError:
            pass
    # 历史里存的是缓存 URL，留着会全是破图，所以一起清掉
    for f in (HISTORY_FILE, SEEN_FILE):
        try:
            if os.path.isfile(f):
                os.remove(f)
        except OSError:
            pass
    return {'message': '已清空缓存与历史', 'removed': removed}


IFACE_IDS = [
    'laizhangtu.info', 'laizhangtu.config.get', 'laizhangtu.config.save',
    'laizhangtu.fetch', 'laizhangtu.search', 'laizhangtu.pick',
    'laizhangtu.history.list', 'laizhangtu.history.clear',
    'laizhangtu.cache.stats', 'laizhangtu.cache.clear',
]


if __name__ == '__main__':
    os.makedirs(CACHE_DIR, exist_ok=True)
    rc.serve(
        endpoint=os.environ.get('RC_ENDPOINT', ''),
        name=NAME,
        version=VERSION,
        manifest={'label': LABEL, 'description': 'Lolicon 插画搜索与取图（面板 v4 移植版）'},
        frontend={'pages': [{'path': '', 'title': LABEL}]},
        iface_ids=IFACE_IDS,
        plugin_dir=PLUGIN_DIR,
    )
