import os
import re
import json
import time
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import request, jsonify, send_file
from plugins.base import Plugin, path_stats

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
LIBRARY_FILE = os.path.join(DOWNLOADS_DIR, 'library.json')
IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
METADATA_FILE = os.path.join(os.path.dirname(__file__), 'metadata.json')
ALBUM_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'album_cache.json')
PHOTO_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'photo_cache.json')

def _load_cache(path):
    try:
        if os.path.isfile(path):
            return json.load(open(path, 'r', encoding='utf-8'))
    except Exception:
        pass
    return {}

def _save_cache(path, cache):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False)
    except Exception:
        pass

DEFAULT_CONFIG = {'show_info': True, 'storage_paths': [DOWNLOADS_DIR],
                  'active_path': DOWNLOADS_DIR, 'auto_switch_full': True,
                  'full_threshold_mb': 1024}

def load_config():
    if os.path.isfile(DATA_FILE):
        try:
            cfg = json.load(open(DATA_FILE, 'r', encoding='utf-8'))
        except:
            cfg = {}
    else:
        cfg = {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    # ensure storage_paths always contains the default downloads dir
    paths = merged.get('storage_paths') or []
    if DOWNLOADS_DIR not in paths:
        paths.insert(0, DOWNLOADS_DIR)
    merged['storage_paths'] = paths
    if merged.get('active_path') not in paths:
        merged['active_path'] = paths[0]
    return merged

def save_config(cfg):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def storage_paths():
    """All configured download directories (ordered)."""
    return load_config().get('storage_paths', [DOWNLOADS_DIR])


def _dir_writable(path):
    """True if the dir exists and a probe file can be written.
    Uses a real write test because os.access() cannot detect a kernel
    read-only remount (e.g. after disk I/O errors)."""
    try:
        if not os.path.isdir(path):
            return False
        probe = os.path.join(path, '.wtest')
        with open(probe, 'w') as f:
            f.write('1')
        os.remove(probe)
        return True
    except Exception:
        return False


def active_dir():
    """Currently active write directory (falls back to a writable one)."""
    cfg = load_config()
    ap = cfg.get('active_path')
    if ap in storage_paths() and _dir_writable(ap):
        return ap
    for p in storage_paths():
        if _dir_writable(p):
            return p
    return storage_paths()[0]


def _dir_free_mb(path):
    try:
        return shutil.disk_usage(path).free // (1024 * 1024)
    except Exception:
        return 0


def pick_dir():
    """Pick the write dir. If auto-switch enabled and active dir is full,
    rotate to the next dir with enough free space (and update active_path)."""
    cfg = load_config()
    paths = storage_paths()
    if not cfg.get('auto_switch_full', True):
        return active_dir()
    threshold = int(cfg.get('full_threshold_mb') or 1024)
    active = active_dir()
    idx = paths.index(active) if active in paths else 0
    n = len(paths)
    for i in range(n):
        cand = paths[(idx + i) % n]
        if _dir_writable(cand) and _dir_free_mb(cand) >= threshold:
            if cand != active:
                cfg['active_path'] = cand
                save_config(cfg)
            return cand
    return active

def get_client():
    from jmcomic import JmOption
    opt = JmOption.default()
    opt.client.impl = 'api'
    return opt.new_jm_client()

_jm_client = None

def jm():
    global _jm_client
    if _jm_client is None:
        _jm_client = get_client()
    return _jm_client

def album_dir(aid):
    """Return the directory that already contains this aid, else the active dir."""
    for base in storage_paths():
        d = os.path.join(base, str(aid))
        if os.path.isdir(d):
            return d
    d = os.path.join(active_dir(), str(aid))
    os.makedirs(d, exist_ok=True)
    return d

def load_library():
    merged = {}
    for base in storage_paths():
        p = os.path.join(base, 'library.json')
        if os.path.isfile(p):
            try:
                data = json.load(open(p, 'r', encoding='utf-8'))
                if isinstance(data, dict):
                    merged.update(data)
            except:
                pass
    return merged

def save_library(lib):
    """Write library.json to the first writable storage dir.
    Never raises: if no writable dir exists the write is skipped so a
    read-only/missing disk cannot break library reads."""
    for base in storage_paths():
        if not _dir_writable(base):
            continue
        try:
            with open(os.path.join(base, 'library.json'), 'w', encoding='utf-8') as f:
                json.dump(lib, f, ensure_ascii=False, indent=2)
            return
        except Exception:
            continue

def rebuild_library():
    lib = load_library()
    for aid in list(lib.keys()):
        total = 0
        cached = 0
        for base in storage_paths():
            d = os.path.join(base, str(aid))
            if os.path.isdir(d):
                for root, dirs, files in os.walk(d):
                    for f in files:
                        if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png', '.gif')):
                            total += 1
                cached += total
                break
        if cached == 0:
            del lib[aid]
        else:
            lib[aid]['cached'] = cached
            lib[aid]['total'] = total
    save_library(lib)
    return lib

def find_local_image(aid, filename):
    """Search all download dirs for a local image file."""
    for base in storage_paths():
        # flat: downloads/{aid}/{filename}
        p = os.path.join(base, aid, filename)
        if os.path.isfile(p):
            return p
        # recursive under downloads/{aid}
        d = os.path.join(base, aid)
        if os.path.isdir(d):
            for root, dirs, files in os.walk(d):
                if filename in files:
                    return os.path.join(root, filename)
    return None


_library_cache = {'ts': 0, 'data': None}


def _sorted_library():
    """Build & cache the sorted library list for a few seconds (disk scan is slow)."""
    now = time.time()
    if _library_cache['data'] is not None and now - _library_cache['ts'] < 5:
        return _library_cache['data']
    lib = rebuild_library()
    items = sorted([{**v, 'aid': k} for k, v in lib.items()], key=lambda x: x.get('updated', 0), reverse=True)
    # add zip info (check every storage path)
    for item in items:
        for base in storage_paths():
            zp = os.path.join(base, f'{item["aid"]}.zip')
            if os.path.isfile(zp):
                item['zip_size'] = os.path.getsize(zp)
                item['zip_base'] = base
                break
    # attach cached tags only (no blocking album-detail fetch)
    cached_meta = load_metadata()
    for item in items:
        m = cached_meta.get(item['aid'])
        if m and m.get('tags'):
            item['tags'] = m.get('tags', [])
    _library_cache['data'] = items
    _library_cache['ts'] = now
    return items


def is_complete_download(aid):
    """True if the album was fully downloaded (marker or zip archive)."""
    aid = str(aid)
    for base in storage_paths():
        if os.path.isfile(os.path.join(base, aid, '.complete')):
            return True
        if os.path.isfile(os.path.join(base, f'{aid}.zip')):
            return True
    return False


def album_from_local(aid):
    """Build album payload purely from local files (no JM API)."""
    aid = str(aid)
    if not is_complete_download(aid):
        return None
    lib = load_library().get(aid, {})
    meta = load_metadata().get(aid, {})
    name = lib.get('name') or meta.get('name') or ''
    author = lib.get('author') or meta.get('author') or ''
    chapters = []
    base = album_dir(aid)
    if os.path.isdir(base):
        for d in sorted(os.listdir(base)):
            sub = os.path.join(base, d)
            if not os.path.isdir(sub) or d.startswith('.'):
                continue
            files = [f for f in os.listdir(sub)
                     if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png', '.gif'))]
            if files:
                chapters.append({'aid': aid, 'cid': d, 'name': name or f'章节 {d}'})
    if not chapters:
        return None
    if len(chapters) > 1:
        for i, ch in enumerate(chapters, 1):
            ch['name'] = f'第{i}话'
    return {
        'id': aid,
        'name': name,
        'author': author,
        'authors': [author] if author else [],
        'description': '',
        'tags': meta.get('tags', []),
        'likes': 0,
        'views': 0,
        'comment_count': 0,
        'page_count': 0,
        'chapters': chapters,
        'related': [],
    }


def scan_cached_files(aid):
    total = 0
    for base in storage_paths():
        d = os.path.join(base, aid)
        if os.path.isdir(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png', '.gif')):
                        total += 1
    return total


def fetch_total_pages(client, album):
    """Sum page counts across all chapters via check_photo."""
    total = 0
    try:
        for photo in album:
            client.check_photo(photo)
            total += len(photo.page_arr or [])
    except:
        pass
    return total


def load_metadata():
    if os.path.isfile(METADATA_FILE):
        try:
            return json.load(open(METADATA_FILE, 'r', encoding='utf-8'))
        except:
            pass
    return {}


def save_metadata(meta):
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


_meta_lock = threading.Lock()


def get_album_meta(client, aid):
    """Cached album metadata: name/author/tags (thread-safe)."""
    with _meta_lock:
        meta = load_metadata()
        if aid in meta:
            return meta[aid]
    try:
        album = client.get_album_detail(aid)
        entry = {
            'name': album.name,
            'author': album.author,
            'tags': list(album.tags) if album.tags else [],
            'updated': int(time.time()),
        }
    except Exception:
        entry = {'name': '', 'author': '', 'tags': []}
    with _meta_lock:
        meta = load_metadata()
        if aid not in meta:
            meta[aid] = entry
            save_metadata(meta)
    return entry


CDN_DOMAINS = [
    'cdn-msp.jmapiproxy2.cc',
    'cdn-msp.jmapiproxy1.cc',
    'www.cdnhjk.net',
]


def _download_image(aid, cid, filename, local_path):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    import requests
    for domain in CDN_DOMAINS:
        try:
            url = f'https://{domain}/media/photos/{cid}/{filename}'
            r = requests.get(url, timeout=30,
                             headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                      'Referer': 'https://18comic.vip/'})
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(r.content)
            return r.content
        except:
            continue
    return None


_scramble_cache = {}
_SCRAMBLE_FILE = os.path.join(IMG_DIR, 'scramble.json')

def _load_scramble_cache():
    try:
        if os.path.isfile(_SCRAMBLE_FILE):
            c = json.load(open(_SCRAMBLE_FILE, 'r', encoding='utf-8'))
            _scramble_cache.update({str(k): str(v) for k, v in c.items()})
    except Exception:
        pass
    try:
        pc = _load_cache(PHOTO_CACHE_FILE)
        for cid, v in pc.items():
            if v.get('scramble_id'):
                _scramble_cache.setdefault(str(cid), str(v['scramble_id']))
    except Exception:
        pass

_load_scramble_cache()

# Bound CDN image download concurrency (allow parallel, avoid CDN throttling)
_cdn_lock = threading.BoundedSemaphore(4)


def _persist_scramble():
    try:
        with open(_SCRAMBLE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_scramble_cache, f, ensure_ascii=False)
    except Exception:
        pass


def get_scramble_id(cid):
    """Cached scramble_id per chapter id (persisted to disk)."""
    if cid not in _scramble_cache:
        try:
            photo = jm().get_photo_detail(cid)
            _scramble_cache[cid] = str(photo.scramble_id)
            _persist_scramble()
        except:
            return None
    return _scramble_cache[cid]


def decode_jm_image(data, scramble_id, photo_id, filename, save_path):
    """Decode scrambled JM image and save. Gif saved raw."""
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    if ext == 'gif' or not scramble_id:
        with open(save_path, 'wb') as f:
            f.write(data)
        return
    from jmcomic import JmImageTool
    # get_num hashes f"{aid}{filename}" without the file extension
    num = JmImageTool.get_num(scramble_id, photo_id, os.path.splitext(filename)[0])
    img_src = JmImageTool.open_image(data)
    JmImageTool.decode_and_save(num, img_src, save_path)


def download_one(aid):
    """Download a single album to the selected storage dir (resumable). Returns bool."""
    aid = str(aid)
    base = pick_dir()
    os.makedirs(base, exist_ok=True)
    tmp = os.path.join(base, f'_tmp_{aid}')
    tmp_album = os.path.join(tmp, aid)
    dst = os.path.join(base, aid)
    ok = False
    # prefetch metadata + total page count so library shows name/author and
    # progress has an accurate total (page_count is cheap, no per-chapter fetch)
    try:
        detail = jm().get_album_detail(aid)
        lib = load_library()
        entry = lib.get(aid, {})
        if detail.page_count:
            entry['total'] = detail.page_count
        else:
            entry['total'] = fetch_total_pages(jm(), detail) or entry.get('total') or 0
        entry['name'] = entry.get('name') or detail.name
        entry['author'] = entry.get('author') or detail.author
        entry['updated'] = int(time.time())
        lib[aid] = entry
        save_library(lib)
    except Exception:
        pass
    try:
        import zipfile
        from jmcomic import JmOption
        from jmcomic.jm_option import DirRule
        opt = JmOption.default()
        opt.dir_rule = DirRule('Bd_Aid', tmp)
        opt.download_album(aid)
        if not os.path.isdir(tmp_album):
            return False
        # keep legacy layout downloads/{aid}/{aid}/xxx so existing
        # album_from_local / chapter_pages / find_local_image keep working
        dest = os.path.join(dst, aid)
        if os.path.isdir(dst) and not is_complete_download(aid):
            shutil.rmtree(dst, ignore_errors=True)
        os.makedirs(dst, exist_ok=True)
        shutil.move(tmp_album, dest)
        zip_path = os.path.join(base, f'{aid}.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(dst):
                for f in files:
                    fp = os.path.join(root, f)
                    arcname = os.path.relpath(fp, base)
                    zf.write(fp, arcname)
        try:
            open(os.path.join(dst, '.complete'), 'w').close()
        except Exception:
            pass
        total = scan_cached_files(aid)
        lib = load_library()
        entry = lib.get(aid, {})
        entry['total'] = total
        entry['cached'] = total
        entry['updated'] = int(time.time())
        lib[aid] = entry
        save_library(lib)
        ok = True
        return True
    except Exception:
        return False
    finally:
        if ok and os.path.isdir(tmp):
            shutil.rmtree(tmp, ignore_errors=True)


class DownloadManager:
    """Single worker queue for single/batch downloads, sequential, resumable."""

    def __init__(self):
        self._lock = threading.Lock()
        self._queue = []
        self._tasks = {}
        self._current = None
        self._worker = None
        self._batch = {
            'running': False, 'stop': False, 'mode': '', 'keyword': '',
            'status': 'idle', 'found': 0, 'current': None, 'results': {},
            'done': 0, 'fail': 0, 'skip': 0, 'error': '',
        }

    def _ensure_worker_locked(self):
        if self._worker is None or not self._worker.is_alive():
            self._worker = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker.start()

    def enqueue(self, aid):
        aid = str(aid)
        with self._lock:
            if is_complete_download(aid):
                return 'cached'
            t = self._tasks.get(aid)
            if t and t['status'] in ('queued', 'downloading'):
                return 'queued'
            self._tasks[aid] = {'status': 'queued', 'name': ''}
            self._queue.append(aid)
            self._ensure_worker_locked()
        return 'queued'

    def status(self, aid):
        with self._lock:
            t = self._tasks.get(str(aid))
            return dict(t) if t else None

    def start_batch(self, mode, keyword):
        with self._lock:
            if self._batch['running']:
                return False, '已有批量下载任务进行中'
            self._batch = {
                'running': True, 'stop': False, 'mode': mode, 'keyword': keyword,
                'status': 'collecting', 'found': 0, 'current': None, 'results': {},
                'done': 0, 'fail': 0, 'skip': 0, 'error': '',
            }
        threading.Thread(target=self._collect, args=(mode, keyword), daemon=True).start()
        return True, '开始批量下载'

    def stop_batch(self):
        with self._lock:
            if not self._batch['running']:
                return False
            self._batch['stop'] = True
            self._queue.clear()
            for r in self._batch['results'].values():
                if r['status'] == 'queued':
                    r['status'] = 'skipped'
                    self._batch['skip'] += 1
        return True

    def batch_status(self):
        with self._lock:
            b = dict(self._batch)
            b['results'] = dict(self._batch['results'])
            b['current'] = self._current
            return b

    def _collect(self, mode, keyword):
        try:
            client = jm()
            page = 1
            while True:
                with self._lock:
                    if self._batch['stop']:
                        break
                if mode == 'author':
                    result = client.search_author(search_query=keyword, page=page)
                elif mode == 'tag':
                    result = client.search_tag(search_query=keyword, page=page)
                else:
                    result = client.search_site(search_query=keyword, page=page)
                items = [(str(aid), name) for aid, name in result]
                if not items:
                    break
                page_count = getattr(result, 'page_count', 1) or 1
                with self._lock:
                    if self._batch['stop']:
                        break
                    for aid, name in items:
                        if aid in self._batch['results']:
                            continue
                        if is_complete_download(aid):
                            self._batch['results'][aid] = {'name': name, 'status': 'skipped'}
                            self._batch['skip'] += 1
                            continue
                        self._batch['results'][aid] = {'name': name, 'status': 'queued'}
                        self._batch['found'] += 1
                        self._tasks.setdefault(aid, {'status': 'queued', 'name': name})
                        self._queue.append(aid)
                    self._ensure_worker_locked()
                if page >= page_count:
                    break
                page += 1
        except Exception as e:
            with self._lock:
                self._batch['error'] = str(e)
        finally:
            with self._lock:
                if self._batch['running'] and self._batch['status'] == 'collecting':
                    self._batch['status'] = 'downloading'

    def _worker_loop(self):
        while True:
            with self._lock:
                if self._batch['stop']:
                    self._batch['stop'] = False
                    self._batch['running'] = False
                    self._batch['status'] = 'stopped'
                    self._queue.clear()
                if not self._queue:
                    if self._batch['running'] and self._batch['status'] == 'collecting':
                        time.sleep(0.3)
                        continue
                    if self._batch['running'] and self._batch['status'] == 'downloading':
                        self._batch['running'] = False
                        self._batch['status'] = 'done'
                    self._current = None
                    break
                aid = self._queue.pop(0)
                self._current = aid
                t = self._tasks.get(aid)
                if t:
                    t['status'] = 'downloading'
                if aid in self._batch['results']:
                    self._batch['results'][aid]['status'] = 'downloading'
            ok = download_one(aid)
            with self._lock:
                self._current = None
                t = self._tasks.get(aid)
                if t:
                    t['status'] = 'completed' if ok else 'failed'
                if aid in self._batch['results']:
                    self._batch['results'][aid]['status'] = 'completed' if ok else 'failed'
                    if ok:
                        self._batch['done'] += 1
                    else:
                        self._batch['fail'] += 1


_manager = DownloadManager()


class Jmcomic(Plugin):
    name = 'jmcomic'
    label = 'JMComic'
    icon = ''
    description = '禁漫天堂搜索与漫画阅读'

    def storage_provider(self):
        cfg = load_config()
        return {
            'name': 'jmcomic',
            'label': '本子库存储路径',
            'paths': cfg.get('storage_paths', [DOWNLOADS_DIR]),
            'active_path': cfg.get('active_path'),
            'auto_switch_full': cfg.get('auto_switch_full', True),
            'full_threshold_mb': cfg.get('full_threshold_mb', 1024),
        }

    # 可插拔设置: 注入「设置页 → 插件设置」
    def get_setting_schema(self):
        return [
            {'key': 'storage_paths', 'label': '本子库存储路径', 'type': 'paths'},
            {'key': 'auto_switch_full', 'label': '满盘自动切换', 'type': 'switch',
             'help': '剩余空间低于阈值时自动切换到下一存储路径'},
            {'key': 'full_threshold_mb', 'label': '切换阈值 (MB)', 'type': 'number',
             'help': '剩余空间低于该值时换盘'},
        ]

    def get_settings(self):
        cfg = load_config()
        paths = cfg.get('storage_paths', [DOWNLOADS_DIR])
        return {'storage_paths': path_stats(paths),
                'active_path': cfg.get('active_path'),
                'auto_switch_full': cfg.get('auto_switch_full', True),
                'full_threshold_mb': cfg.get('full_threshold_mb', 1024)}

    def save_settings(self, data):
        cfg = load_config()
        if 'storage_paths' in data:
            paths = [p for p in data['storage_paths'] if isinstance(p, str) and p.strip()]
            if DOWNLOADS_DIR not in paths:
                paths.insert(0, DOWNLOADS_DIR)
            cfg['storage_paths'] = paths
            if data.get('active_path') not in paths:
                cfg['active_path'] = paths[0]
            else:
                cfg['active_path'] = data['active_path']
        if 'auto_switch_full' in data:
            cfg['auto_switch_full'] = bool(data['auto_switch_full'])
        if 'full_threshold_mb' in data:
            try:
                cfg['full_threshold_mb'] = int(data['full_threshold_mb'])
            except (TypeError, ValueError):
                pass
        save_config(cfg)
        return True, 'ok'

    def _register_routes(self):

        def _search_tag_all(client, tag, max_pages=8):
            """Collect all aids matching a single tag (paginated), return {aid: name}."""
            aids = {}
            for pg in range(1, max_pages + 1):
                try:
                    result = client.search_tag(search_query=tag, page=pg)
                except Exception:
                    break
                if not result:
                    break
                for aid, name in result:
                    aids[str(aid)] = name
                if pg >= getattr(result, 'page_count', 1):
                    break
            return aids

        def _search_tags_intersection(client, tags, page, per=45):
            """AND search across multiple tags: collect each tag's aids, intersect."""
            from concurrent.futures import ThreadPoolExecutor
            results = [None] * len(tags)
            with ThreadPoolExecutor(max_workers=min(len(tags), 4)) as ex:
                futs = {ex.submit(_search_tag_all, client, t): i for i, t in enumerate(tags)}
                for f in futs:
                    results[futs[f]] = f.result()
            if any(not r for r in results):
                return [], 0, 1
            inter = set(results[0])
            for r in results[1:]:
                inter &= set(r)
            order = [aid for aid in results[0] if aid in inter]
            total = len(order)
            page_count = max(1, -(-total // per))
            start = (page - 1) * per
            ids = order[start:start + per]
            items = [{'id': aid, 'name': results[0].get(aid, '')} for aid in ids]
            return items, total, page_count

        @self.route('/search', methods=['GET'])
        def search():
            keyword = request.args.get('keyword', '').strip()
            page = request.args.get('page', 1, type=int)
            mode = request.args.get('mode', 'keyword')
            if not keyword:
                return jsonify({'error': '请输入搜索关键词'}), 400
            try:
                client = jm()
                if mode == 'tag' and re.split(r'[,，\s]+', keyword) and len(re.split(r'[,，\s]+', keyword)) > 1:
                    tags = [t for t in re.split(r'[,，\s]+', keyword) if t]
                    items, total, page_count = _search_tags_intersection(client, tags, page)
                    cached_meta = load_metadata()
                    for item in items:
                        m = cached_meta.get(item['id'])
                        if m:
                            item['author'] = m.get('author', '')
                            item['tags'] = m.get('tags', [])
                    return jsonify({'items': items, 'total': total, 'page_count': page_count})
                if mode == 'author':
                    result = client.search_author(search_query=keyword, page=page)
                elif mode == 'tag':
                    result = client.search_tag(search_query=keyword, page=page)
                elif mode == 'work':
                    result = client.search_work(search_query=keyword, page=page)
                else:
                    result = client.search_site(search_query=keyword, page=page)
                items = [{'id': str(aid), 'name': name} for aid, name in result]
                # attach cached metadata only (no blocking album-detail fetch per item)
                cached_meta = load_metadata()
                for item in items:
                    m = cached_meta.get(item['id'])
                    if m:
                        item['author'] = m.get('author', '')
                        item['tags'] = m.get('tags', [])
                total = getattr(result, 'total', 0)
                page_count = getattr(result, 'page_count', 1)
                return jsonify({'items': items, 'total': total, 'page_count': page_count})
            except Exception as e:
                return jsonify({'error': f'搜索失败: {str(e)}'}), 502

        @self.route('/meta/', methods=['GET'])
        def album_meta():
            aid = _tail('/meta/', request.path)
            if not aid or not aid.isdigit():
                return jsonify({'error': '缺少漫画ID'}), 400
            try:
                return jsonify(get_album_meta(jm(), aid))
            except Exception as e:
                return jsonify({'error': f'获取信息失败: {str(e)}'}), 502

        @self.route('/album/', methods=['GET'])
        def album_detail():
            aid = _tail('/album/', request.path)
            if not aid or not aid.isdigit():
                return jsonify({'error': '缺少漫画ID'}), 400
            cache = _load_cache(ALBUM_CACHE_FILE)
            entry = cache.get(aid)
            if entry and time.time() - entry.get('fetched', 0) < 6 * 3600:
                return jsonify(entry['data'])
            # fully-downloaded albums: serve from local files (instant, offline-safe)
            local = album_from_local(aid)
            if local:
                return jsonify(local)
            try:
                detail = jm().get_album_detail(aid)
                # cache name/author in library
                lib = load_library()
                if aid not in lib:
                    lib[aid] = {}
                lib[aid]['name'] = detail.name
                lib[aid]['author'] = detail.author
                lib[aid]['updated'] = int(time.time())
                save_library(lib)
                chapters = []
                for ep in detail.episode_list:
                    cid = str(ep[1])
                    if cid == '1' and len(detail.episode_list) == 1:
                        cid = str(detail.album_id)
                    chapters.append({
                        'aid': str(detail.album_id),
                        'cid': cid,
                        'name': ep[2],
                    })
                data = {
                    'id': str(detail.album_id),
                    'name': detail.name,
                    'author': detail.author,
                    'authors': list(detail.authors) if detail.authors else [],
                    'description': detail.description or '',
                    'tags': list(detail.tags) if detail.tags else [],
                    'likes': detail.likes,
                    'views': detail.views,
                    'comment_count': detail.comment_count,
                    'page_count': detail.page_count,
                    'chapters': chapters,
                    'related': [
                        {'id': str(r.get('id', '')), 'name': r.get('name', ''), 'author': r.get('author', '')}
                        for r in (detail.related_list or [])
                    ],
                }
                cache[aid] = {'data': data, 'fetched': int(time.time())}
                _save_cache(ALBUM_CACHE_FILE, cache)
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': f'获取漫画详情失败: {str(e)}'}), 502

        @self.route('/chapter/', methods=['GET'])
        def chapter_pages():
            rest = _tail('/chapter/', request.path)
            parts = rest.split('/')
            if len(parts) == 1:
                aid, cid = None, parts[0]
            elif len(parts) == 2:
                aid, cid = parts
            else:
                return jsonify({'error': '参数错误: /chapter/[aid/]cid'}), 400
            if not cid or not cid.isdigit():
                return jsonify({'error': '缺少章节ID'}), 400
            # build page list from local downloaded files (no JM API call) —
            # only when the album was fully downloaded, else reader partial
            # caches would be mistaken for the complete chapter
            if aid and aid.isdigit() and is_complete_download(aid):
                d = os.path.join(album_dir(aid), cid)
                if os.path.isdir(d):
                    files = sorted(f for f in os.listdir(d)
                                   if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png', '.gif')))
                    if files:
                        return jsonify({
                            'id': cid,
                            'name': '',
                            'page_arr': files,
                            'total': len(files),
                        })
            # disk photo cache
            pcache = _load_cache(PHOTO_CACHE_FILE)
            entry = pcache.get(cid)
            if entry:
                return jsonify(entry)
            try:
                photo = jm().get_photo_detail(cid)
                _scramble_cache[str(photo.photo_id)] = str(photo.scramble_id)
                _persist_scramble()
                data = {
                    'id': str(photo.photo_id),
                    'name': photo.name,
                    'author': photo.author,
                    'tags': list(photo.tags) if photo.tags else [],
                    'scramble_id': str(photo.scramble_id),
                    'page_arr': list(photo.page_arr),
                    'total': len(photo.page_arr),
                }
                pcache[cid] = data
                _save_cache(PHOTO_CACHE_FILE, pcache)
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': f'获取章节失败: {str(e)}'}), 502

        @self.route('/download/', methods=['POST'])
        def download_album():
            aid = _tail('/download/', request.path)
            if not aid or not aid.isdigit():
                return jsonify({'error': '缺少漫画ID'}), 400
            result = _manager.enqueue(aid)
            if result == 'cached':
                return jsonify({'message': f'本子 {aid} 已缓存', 'status': 'cached'})
            if result == 'queued':
                return jsonify({'message': f'本子 {aid} 已在下载队列中', 'status': 'queued'})
            return jsonify({'message': f'开始下载 {aid}', 'status': 'downloading'})

        @self.route('/download/', methods=['GET'])
        def download_status():
            aid = _tail('/download/', request.path)
            if not aid or not aid.isdigit():
                return jsonify({'error': '缺少漫画ID'}), 400
            cached = scan_cached_files(aid)
            tmp = None
            tmp_count = 0
            for base in storage_paths():
                p = os.path.join(base, f'_tmp_{aid}')
                if os.path.isdir(p):
                    tmp = p
                    break
            if tmp and os.path.isdir(tmp):
                for root, dirs, files in os.walk(tmp):
                    for f in files:
                        if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png', '.gif')):
                            tmp_count += 1
            downloaded = cached + tmp_count
            lib = load_library()
            entry = lib.get(aid, {})
            total = entry.get('total') or 0
            if total and downloaded > total:
                downloaded = total
            task = _manager.status(aid)
            if task and task['status'] in ('queued', 'downloading'):
                status = 'downloading'
            elif task and task['status'] == 'failed':
                status = 'failed'
            elif cached >= total and total > 0:
                status = 'completed'
            elif downloaded > 0:
                status = 'downloading'
            else:
                status = 'not_found'
            return jsonify({'aid': aid, 'total': total, 'downloaded': downloaded, 'cached': cached, 'status': status})

        @self.route('/download/batch', methods=['POST', 'GET'])
        def download_batch():
            if request.method == 'POST':
                body = request.json or {}
                mode = body.get('mode', 'keyword')
                keyword = (body.get('keyword') or '').strip()
                if mode not in ('keyword', 'author', 'tag'):
                    return jsonify({'error': '不支持的批量模式'}), 400
                if not keyword:
                    return jsonify({'error': '请输入批量搜索关键词'}), 400
                ok, msg = _manager.start_batch(mode, keyword)
                if not ok:
                    return jsonify({'error': msg}), 409
                return jsonify({'message': msg, 'mode': mode, 'keyword': keyword})
            return jsonify(_manager.batch_status())

        @self.route('/download/batch/stop', methods=['POST'])
        def download_batch_stop():
            ok = _manager.stop_batch()
            if not ok:
                return jsonify({'error': '当前没有批量下载任务'}), 409
            return jsonify({'message': '已停止批量下载'})

        @self.route('/download_zip/', methods=['GET'])
        def download_zip():
            aid = _tail('/download_zip/', request.path)
            if not aid or not aid.isdigit():
                return jsonify({'error': '缺少漫画ID'}), 400
            zip_path = None
            for base in storage_paths():
                p = os.path.join(base, f'{aid}.zip')
                if os.path.isfile(p):
                    zip_path = p
                    break
            if zip_path:
                return send_file(zip_path, mimetype='application/zip', as_attachment=True,
                                 download_name=f'{aid}.zip')
            return jsonify({'error': 'ZIP 文件不存在'}), 404

        @self.route('/image/', methods=['GET'])
        def image_proxy():
            rest = _tail('/image/', request.path)
            parts = rest.split('/')
            if len(parts) < 3:
                return jsonify({'error': '参数不足: aid/cid/filename'}), 400
            aid, cid, filename = parts[0], parts[1], '/'.join(parts[2:])
            # check local cache first (any directory structure)
            local_path = find_local_image(aid, filename)
            if local_path:
                return send_file(local_path, mimetype=_guess_mime(filename), max_age=0)
            # download and cache to {active_dir}/{aid}/{cid}/{filename} (serialized one at a time)
            local_path = os.path.join(active_dir(), aid, cid, filename)
            with _cdn_lock:
                # a queued request may have downloaded it while we waited
                p = find_local_image(aid, filename)
                if p:
                    return send_file(p, mimetype=_guess_mime(filename), max_age=0)
                data = _download_image(aid, cid, filename, local_path)
                if data:
                    decode_jm_image(data, get_scramble_id(cid), cid, filename, local_path)
                    return send_file(local_path, mimetype=_guess_mime(filename), max_age=0)
            return jsonify({'error': '图片加载失败'}), 502

        @self.route('/cover/', methods=['GET'])
        def cover():
            aid = _tail('/cover/', request.path)
            if not aid or not aid.isdigit():
                return jsonify({'error': '缺少漫画ID'}), 400

            def _find_cover():
                for ext in ('jpg', 'jpeg', 'webp', 'png', 'gif'):
                    p = os.path.join(IMG_DIR, f'{aid}.{ext}')
                    if os.path.isfile(p):
                        return p
                return None

            # serve cached cover (never deleted)
            p = _find_cover()
            if p:
                return send_file(p, mimetype=_guess_mime(f'x.{os.path.splitext(p)[1][1:]}'), max_age=0)
            # fetch first image and cache to img/ (serialized one at a time)
            try:
                client = jm()
                album = client.get_album_detail(aid)
                photo_id = str(album.episode_list[0][1])
                if photo_id == '1' and len(album.episode_list) == 1:
                    photo_id = str(album.album_id)
                photo = client.get_photo_detail(photo_id)
                if not photo.page_arr:
                    return jsonify({'error': '该漫画无图片'}), 404
                filename = photo.page_arr[0]
                ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else 'jpg'
                save_path = os.path.join(IMG_DIR, f'{aid}.{ext}')
                with _cdn_lock:
                    # a queued request may have downloaded it while we waited
                    p = _find_cover()
                    if p:
                        return send_file(p, mimetype=_guess_mime(f'x.{os.path.splitext(p)[1][1:]}'), max_age=0)
                    data = _download_image(aid, photo_id, filename, save_path)
                    if not data:
                        return jsonify({'error': '封面下载失败'}), 502
                    decode_jm_image(data, photo.scramble_id, photo_id, filename, save_path)
                return send_file(save_path, mimetype=_guess_mime(f'x.{ext}'), max_age=0)
            except Exception as e:
                return jsonify({'error': f'获取封面失败: {str(e)}'}), 502

        @self.route('/library', methods=['GET'])
        def list_library():
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 45, type=int)
            page = max(page, 1)
            page_size = max(page_size, 1)
            items = _sorted_library()
            total = len(items)
            start = (page - 1) * page_size
            paged = items[start:start + page_size]
            return jsonify({
                'items': paged,
                'total': total,
                'page': page,
                'page_size': page_size,
                'page_count': (total + page_size - 1) // page_size,
            })

        @self.route('/library/', methods=['DELETE'])
        def delete_library():
            aid = _tail('/library/', request.path)
            for base in storage_paths():
                d = os.path.join(base, aid)
                if os.path.isdir(d):
                    shutil.rmtree(d)
                zip_path = os.path.join(base, f'{aid}.zip')
                if os.path.isfile(zip_path):
                    os.remove(zip_path)
            lib = load_library()
            if aid in lib:
                del lib[aid]
                save_library(lib)
            return jsonify({'message': f'已删除 {aid}'})

        @self.route('/config', methods=['GET', 'POST'])
        def handle_config():
            if request.method == 'POST':
                new_cfg = request.json or {}
                cfg = load_config()
                if 'storage_paths' in new_cfg:
                    paths = [p for p in new_cfg['storage_paths'] if isinstance(p, str) and p.strip()]
                    if DOWNLOADS_DIR not in paths:
                        paths.insert(0, DOWNLOADS_DIR)
                    cfg['storage_paths'] = paths
                    if new_cfg.get('active_path') not in paths:
                        cfg['active_path'] = paths[0]
                    else:
                        cfg['active_path'] = new_cfg['active_path']
                    if 'auto_switch_full' in new_cfg:
                        cfg['auto_switch_full'] = bool(new_cfg['auto_switch_full'])
                    if 'full_threshold_mb' in new_cfg:
                        cfg['full_threshold_mb'] = max(0, int(new_cfg['full_threshold_mb'] or 0))
                else:
                    cfg.update(new_cfg)
                save_config(cfg)
                return jsonify({'message': '设置已保存', 'config': load_config()})
            return jsonify(load_config())

        @self.route('/info', methods=['GET'])
        def plugin_info():
            return jsonify(self.get_info())

def _tail(prefix, path):
    idx = path.find(prefix)
    if idx < 0:
        return ''
    return path[idx + len(prefix):].lstrip('/')

def _guess_mime(filename):
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    return {
        'webp': 'image/webp',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
    }.get(ext, 'image/webp')
