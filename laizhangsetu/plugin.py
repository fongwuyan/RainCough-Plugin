import os
import re
import random
import json
import hashlib
import shutil
import requests as http_req
from datetime import datetime
from flask import request, jsonify, send_from_directory
from PIL import Image, ImageFilter
from io import BytesIO
from plugins.base import Plugin

LOLICON_API = 'https://api.lolicon.app/setu/v2'
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')
SEEN_FILE = os.path.join(os.path.dirname(__file__), 'seen.json')

DEFAULT_CONFIG = {
    'show_info': True,
    'exclude_ai': True,
    'flip_h': False,
    'flip_v': False,
    'auto_revoke': False,
    'revoke_time': 5000,
    'cool_down': 0,
    'blur_chance': 5,
    'r18': False,
    'img_size': 0,
    'proxy': 'i.pixiv.re',
    'exclude_seen': False,
    'storage_paths': [CACHE_DIR],
    'active_path': CACHE_DIR,
    'auto_switch_full': True,
    'full_threshold_mb': 1024,
}


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
    paths = merged.get('storage_paths') or []
    if CACHE_DIR not in paths:
        paths.insert(0, CACHE_DIR)
    merged['storage_paths'] = paths
    if merged.get('active_path') not in paths:
        merged['active_path'] = paths[0]
    return merged


def save_config(cfg):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def storage_paths():
    return load_config().get('storage_paths', [CACHE_DIR])


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


def load_seen():
    if os.path.isfile(SEEN_FILE):
        try:
            return set(json.load(open(SEEN_FILE, 'r', encoding='utf-8')))
        except:
            pass
    return set()


def save_seen(pids):
    with open(SEEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(pids), f)


class LaisetPlugin(Plugin):
    name = 'laizhangsetu'
    label = '来张涩图'
    icon = ''
    description = '调用 Lolicon API 获取随机 Pixiv 涩图，支持标签搜索、R18、图片处理'

    def storage_provider(self):
        cfg = load_config()
        return {
            'name': 'laizhangsetu',
            'label': '图片库存储路径',
            'paths': cfg.get('storage_paths', [CACHE_DIR]),
            'active_path': cfg.get('active_path'),
            'auto_switch_full': cfg.get('auto_switch_full', True),
            'full_threshold_mb': cfg.get('full_threshold_mb', 1024),
        }

    def _register_routes(self):
        config = load_config()

        @self.route('/fetch', methods=['POST'])
        def fetch():
            try:
                data = request.json or {}
                cfg = dict(load_config())

                # Accept both 'tags' array and 'tag' string
                tags = data.get('tags') or []
                if not tags:
                    tag_str = data.get('tag', '').strip()
                    if tag_str:
                        tags = [t.strip() for t in tag_str.split('&') if t.strip()]

                params = {
                    'proxy': cfg.get('proxy', 'i.pixiv.re'),
                    'excludeAI': 'true' if cfg.get('exclude_ai', True) else '',
                    'r18': 2 if cfg.get('r18', False) else 0,
                    'size': ['original', 'regular', 'small'][cfg.get('img_size', 0)],
                }

                # Multiple tag params for AND logic; | inside a tag for OR
                if tags:
                    params['tag'] = tags if len(tags) > 1 else tags[0]

                params = {k: v for k, v in params.items() if v not in (None, '', 0, False)}

                # Exclude seen PIDs
                seen_pids = load_seen() if cfg.get('exclude_seen', False) else set()
                max_attempts = 10
                attempt = 0
                item = None
                while attempt < max_attempts:
                    attempt += 1
                    r = http_req.get(LOLICON_API, params=params, timeout=15)
                    result = r.json()
                    if result.get('error'):
                        return jsonify({'error': f'API 错误: {result["error"]}'}), 502
                    items = result.get('data', [])
                    if not items:
                        q = '|'.join(tags) if tags else ''
                        return jsonify({'error': f'没有找到关于 "{q}" 的涩图喵!'}), 404
                    item = items[0]
                    pid = item.get('pid')
                    if not cfg.get('exclude_seen', False) or pid not in seen_pids:
                        break

                if item is None:
                    return jsonify({'error': '没有找到新的涩图了喵！'}), 404

                # Mark PID as seen
                if cfg.get('exclude_seen', False):
                    seen_pids.add(item.get('pid'))
                    if len(seen_pids) > 10000:
                        seen_pids = set(list(seen_pids)[-5000:])
                    save_seen(seen_pids)

                urls = item.get('urls', {})
                img_url = urls.get(params.get('size', 'original'), urls.get('original', ''))

                # Download image for processing
                img_resp = http_req.get(img_url, timeout=30)
                img_resp.raise_for_status()
                content_type = img_resp.headers.get('Content-Type', '')
                img_data = BytesIO(img_resp.content)

                try:
                    pil_img = Image.open(img_data)
                    pil_img.verify()
                except Exception as e:
                    err_msg = f'图片解析失败 (PID: {item.get("pid")}, 大小: {len(img_resp.content)} bytes, Content-Type: {content_type}): {e}'
                    return jsonify({'error': err_msg}), 502

                img_data.seek(0)
                pil_img = Image.open(img_data)

                if cfg.get('flip_h', False):
                    pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)

                if cfg.get('flip_v', False):
                    pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)

                blur_chance = cfg.get('blur_chance', 5)
                is_blurred = False
                if blur_chance > 0 and random.randint(0, 99) < blur_chance:
                    pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=20))
                    is_blurred = True

                cache_base = pick_dir()
                os.makedirs(cache_base, exist_ok=True)
                safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff_-]', '_', item.get('title', 'untitled'))[:50]
                cache_path = os.path.join(cache_base, f'{safe_name}.jpg')
                if pil_img.mode == 'RGBA':
                    pil_img = pil_img.convert('RGB')
                pil_img.save(cache_path, 'JPEG', quality=92)

                result_data = {
                    'pid': item.get('pid'),
                    'uid': item.get('uid'),
                    'title': item.get('title'),
                    'author': item.get('author'),
                    'width': item.get('width'),
                    'height': item.get('height'),
                    'tags': item.get('tags', []),
                    'r18': item.get('r18', False),
                    'url': f'/api/plugins/laizhangsetu/cache/{safe_name}.jpg',
                    'original_url': img_url,
                    'is_blurred': is_blurred,
                    'show_info': cfg.get('show_info', True),
                }

                # Save to history
                history_file = os.path.join(os.path.dirname(__file__), 'history.json')
                history = []
                if os.path.isfile(history_file):
                    try:
                        history = json.load(open(history_file, 'r', encoding='utf-8'))
                    except:
                        pass
                history.insert(0, {
                    'pid': result_data['pid'],
                    'title': result_data['title'],
                    'author': result_data['author'],
                    'url': result_data['url'],
                    'tags': result_data['tags'],
                    'r18': result_data['r18'],
                    'width': result_data['width'],
                    'height': result_data['height'],
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                if len(history) > 100:
                    history = history[:100]
                json.dump(history, open(history_file, 'w', encoding='utf-8'), ensure_ascii=False)

                return jsonify(result_data)

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.route('/cache/<path:filename>', methods=['GET'])
        def serve_cache(filename):
            import os as _os
            for base in storage_paths():
                p = _os.path.join(base, filename)
                if _os.path.isfile(p):
                    return send_from_directory(base, filename)
            return jsonify({'error': '图片不存在'}), 404

        @self.route('/config', methods=['GET', 'POST'])
        def handle_config():
            if request.method == 'POST':
                new_cfg = request.json or {}
                cfg = load_config()
                if 'storage_paths' in new_cfg:
                    paths = [p for p in new_cfg['storage_paths'] if isinstance(p, str) and p.strip()]
                    if CACHE_DIR not in paths:
                        paths.insert(0, CACHE_DIR)
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

        @self.route('/cooldown', methods=['GET'])
        def cooldown_status():
            cool_secs = config.get('cool_down', 0)
            return jsonify({'cool_down': cool_secs})

        @self.route('/history', methods=['GET', 'DELETE'])
        def history():
            history_file = os.path.join(os.path.dirname(__file__), 'history.json')
            if request.method == 'DELETE':
                if os.path.isfile(history_file):
                    os.remove(history_file)
                seen_file = SEEN_FILE
                if os.path.isfile(seen_file):
                    os.remove(seen_file)
                return jsonify({'message': '历史已清空'})

            records = []
            if os.path.isfile(history_file):
                try:
                    records = json.load(open(history_file, 'r', encoding='utf-8'))
                except:
                    pass
            return jsonify(records)
