import os
import io
import re
import json
import time
import shutil
import hashlib
import threading
from datetime import datetime
from flask import request, jsonify
from plugins.base import Plugin
from plugins.yulotool_common import (
    find_tool, run_cmd, save_uploads, new_session, work_dir,
    safe_join, fmt_size,
)

PLUGIN = 'toolbox'
PLUGIN_ROOT = os.path.join(os.path.dirname(__file__))
DATA_DIR = os.path.join(PLUGIN_ROOT, 'data')
FEEDS_FILE = os.path.join(DATA_DIR, 'feeds.json')

OCR_MODEL_DIR = '/opt/touchgal/models/rapidocr_models'

_ocr_engine = None
_ocr_lock = threading.Lock()

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


def _get_ocr():
    global _ocr_engine
    if _ocr_engine is None:
        with _ocr_lock:
            if _ocr_engine is None:
                from rapidocr import RapidOCR
                from rapidocr.utils.typings import OCRVersion, ModelType
                params = {
                    'Global.model_root_dir': OCR_MODEL_DIR,
                    'Det.ocr_version': OCRVersion.PPOCRV5,
                    'Det.model_type': ModelType.SERVER,
                    'Rec.ocr_version': OCRVersion.PPOCRV5,
                    'Rec.model_type': ModelType.SERVER,
                    'Cls.ocr_version': OCRVersion.PPOCRV5,
                    'Cls.model_type': ModelType.MOBILE,
                }
                _ocr_engine = RapidOCR(params=params)
    return _ocr_engine


def _dhash_from_bytes(data, size=16):
    from PIL import Image
    import numpy as np
    img = Image.open(io.BytesIO(data)).convert('L').resize((size + 1, size), Image.BILINEAR)
    arr = np.asarray(img, dtype=np.int16)
    diff = arr[:, 1:] > arr[:, :-1]
    bits = diff.flatten()
    h = 0
    for b in bits[:64]:
        h = (h << 1) | int(b)
    return h


def _hamming(a, b):
    return (a ^ b).bit_count()  # 内置 C 实现


def _load_feeds():
    if not os.path.isfile(FEEDS_FILE):
        return []
    try:
        with open(FEEDS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def _save_feeds(feeds):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FEEDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(feeds, f, ensure_ascii=False, indent=2)


def _http_get(url, timeout=20):
    import requests
    resp = requests.get(url, headers={'User-Agent': USER_AGENT},
                        timeout=timeout, verify=False)
    resp.raise_for_status()
    return resp


def _parse_bing(q, limit=10):
    import requests
    from urllib.parse import quote
    url = f'https://www.bing.com/search?q={quote(q)}&count={limit}'
    try:
        resp = _http_get(url)
    except Exception as e:
        return {'ok': False, 'error': f'搜索失败: {e}'}
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for li in soup.select('li.b_algo'):
        a = li.select_one('h2 a')
        p = li.select_one('.b_caption p, p')
        if not a or not a.get('href'):
            continue
        results.append({
            'title': a.get_text(strip=True),
            'url': a['href'],
            'snippet': p.get_text(strip=True) if p else '',
        })
        if len(results) >= limit:
            break
    return {'ok': True, 'results': results}


class ToolboxPlugin(Plugin):
    name = 'toolbox'
    label = '全能工具箱'
    icon = ''
    description = 'OCR识别、二维码、图片/音视频处理、RSS聚合、网页搜索、文本工具'

    def _register_routes(self):
        # ==================== OCR ====================
        @self.route('/ocr', methods=['POST'])
        def tb_ocr():
            if not os.path.isdir(OCR_MODEL_DIR):
                return jsonify({'ok': False, 'error': 'OCR 模型未下载'}), 500
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            try:
                engine = _get_ocr()
                out = engine(saved[0]['path'])
                data = out.to_json() if hasattr(out, 'to_json') else []
                text = '\n'.join(item.get('txt', '') for item in data)
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': True, 'text': text, 'lines': data,
                                'elapse': getattr(out, 'elapse', None)})
            except Exception as e:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': str(e)}), 500

        @self.route('/ocr/check', methods=['GET'])
        def tb_ocr_check():
            models_ok = os.path.isdir(OCR_MODEL_DIR) and any(
                f.endswith('.onnx') for f in os.listdir(OCR_MODEL_DIR)
            )
            try:
                import rapidocr  # noqa
                pkg_ok = True
            except Exception:
                pkg_ok = False
            return jsonify({'ok': models_ok and pkg_ok, 'models': models_ok,
                            'package': pkg_ok, 'model_dir': OCR_MODEL_DIR})

        # ==================== 二维码 ====================
        @self.route('/qr/gen', methods=['GET'])
        def tb_qr_gen():
            text = (request.args.get('text') or '').strip()
            if not text:
                return jsonify({'ok': False, 'error': '内容不能为空'}), 400
            try:
                size = int(request.args.get('size') or 300)
            except ValueError:
                size = 300
            size = max(120, min(size, 1024))
            import qrcode
            from qrcode.constants import ERROR_CORRECT_M
            qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M,
                               box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            img = img.resize((size, size))
            os.makedirs(os.path.join(PLUGIN_ROOT, 'cache'), exist_ok=True)
            name = hashlib.md5(text.encode()).hexdigest() + '.png'
            path = os.path.join(PLUGIN_ROOT, 'cache', name)
            img.save(path)
            return jsonify({'ok': True,
                            'url': f'/api/plugins/toolbox/cache/{name}'})

        @self.route('/qr/decode', methods=['POST'])
        def tb_qr_decode():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            try:
                import cv2
                img = cv2.imread(saved[0]['path'])
                if img is None:
                    return jsonify({'ok': False, 'error': '无法读取图片'}), 400
                detector = cv2.QRCodeDetector()
                data, points, _ = detector.detectAndDecode(img)
                results = []
                if data:
                    results.append({'data': data, 'points': points.tolist() if points is not None else None})
                else:
                    decoder = cv2.QRCodeDetector()
                    ok, decoded, pts, _ = decoder.detectAndDecodeMulti(img)
                    if ok:
                        for d, p in zip(decoded, pts):
                            if d:
                                results.append({'data': d, 'points': p.tolist() if p is not None else None})
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': True, 'results': results})
            except Exception as e:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': str(e)}), 500

        # ==================== 图片 ====================
        @self.route('/image/similar', methods=['POST'])
        def tb_img_similar():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if len(saved) < 2:
                return jsonify({'ok': False, 'error': '请上传两张图片'}), 400
            a, b = saved[0], saved[1]
            try:
                ha = _dhash_from_bytes(open(a['path'], 'rb').read())
                hb = _dhash_from_bytes(open(b['path'], 'rb').read())
            except Exception as e:
                return jsonify({'ok': False, 'error': f'图片解析失败: {e}'}), 400
            dist = _hamming(ha, hb)
            shutil.rmtree(session, ignore_errors=True)
            pct = max(0, round((64 - dist) / 64 * 100, 1))
            return jsonify({'ok': True, 'a': a['filename'], 'b': b['filename'],
                            'hamming': dist, 'similarity': pct,
                            'verdict': '高度相似' if dist <= 4 else ('相似' if dist <= 10 else '不同')})

        @self.route('/image/process', methods=['POST'])
        def tb_img_process():
            magick = find_tool('convert')
            if not magick:
                return jsonify({'ok': False, 'error': '未安装 ImageMagick'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            fmt = (request.form.get('format') or '').lower()
            resize = (request.form.get('resize') or '').strip()
            quality = request.form.get('quality')
            rotate = request.form.get('rotate')
            results = []
            outputs = []
            for item in saved:
                src = item['path']
                base, ext = os.path.splitext(item['filename'])
                out_ext = fmt or ext.lstrip('.').lower() or 'png'
                out = os.path.join(session, f'{base}.{out_ext}')
                cmd = [magick, src]
                if resize:
                    cmd += ['-resize', resize]
                if quality:
                    try:
                        cmd += ['-quality', str(int(quality))]
                    except ValueError:
                        pass
                if rotate:
                    try:
                        cmd += ['-rotate', str(int(rotate))]
                    except ValueError:
                        pass
                cmd.append(out)
                r = run_cmd(cmd)
                ok = os.path.isfile(out)
                results.append({'name': item['filename'], 'ok': ok,
                                'error': '' if ok else (r['error'] or '处理失败').strip()[:200],
                                'output': os.path.basename(out) if ok else ''})
                if ok:
                    outputs.append(out)
            if len(outputs) == 1:
                return jsonify({'ok': True, 'results': results, 'single': True,
                                'download': f'/api/plugins/toolbox/file/{os.path.basename(session)}/{os.path.basename(outputs[0])}'})
            from plugins.yulotool.plugin import make_zip_from_files
            zip_path = os.path.join(session, 'images.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/toolbox/file/{os.path.basename(session)}/images.zip'})

        # ==================== 音视频 ====================
        @self.route('/media/info', methods=['POST'])
        def tb_media_info():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传媒体文件'}), 400
            ffprobe = find_tool('ffprobe')
            if not ffprobe:
                return jsonify({'ok': False, 'error': '未安装 ffprobe'}), 400
            path = saved[0]['path']
            r = run_cmd([ffprobe, '-v', 'error', '-show_format',
                         '-show_streams', '-of', 'json', path])
            try:
                data = json.loads(r['output'])
            except Exception:
                return jsonify({'ok': False, 'error': '解析失败'}), 400
            fmt = data.get('format', {})
            streams = data.get('streams', [])
            video = next((s for s in streams if s.get('codec_type') == 'video'), None)
            audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({
                'ok': True,
                'name': saved[0]['filename'],
                'size': int(fmt.get('size') or os.path.getsize(path)),
                'duration': float(fmt.get('duration') or 0),
                'bitrate': fmt.get('bit_rate'),
                'format': fmt.get('format_name'),
                'video': {
                    'codec': video.get('codec_name') if video else None,
                    'width': video.get('width') if video else None,
                    'height': video.get('height') if video else None,
                    'fps': video.get('avg_frame_rate') if video else None,
                } if video else None,
                'audio': {
                    'codec': audio.get('codec_name') if audio else None,
                    'sample_rate': audio.get('sample_rate') if audio else None,
                    'channels': audio.get('channels') if audio else None,
                } if audio else None,
            })

        @self.route('/media/process', methods=['POST'])
        def tb_media_process():
            ffmpeg = find_tool('ffmpeg')
            if not ffmpeg:
                return jsonify({'ok': False, 'error': '未安装 ffmpeg'}), 400
            action = request.form.get('action') or 'convert'
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传媒体文件'}), 400
            fmt = (request.form.get('format') or '').lower()
            try:
                crf = int(request.form.get('crf') or 28)
            except (TypeError, ValueError):
                crf = 28
            try:
                start = float(request.form.get('start') or 0)
            except (TypeError, ValueError):
                start = 0
            duration = request.form.get('duration')
            outputs = []
            results = []
            for item in saved:
                src = item['path']
                base, ext = os.path.splitext(item['filename'])
                if action == 'audio':
                    out_ext = fmt or 'mp3'
                    out = os.path.join(session, f'{base}.{out_ext}')
                    cmd = [ffmpeg, '-i', src, '-vn', '-y', out]
                elif action == 'clip':
                    out_ext = fmt or ext.lstrip('.').lower() or 'mp4'
                    out = os.path.join(session, f'{base}_clip.{out_ext}')
                    cmd = [ffmpeg, '-ss', str(start), '-i', src, '-c', 'copy']
                    if duration:
                        cmd += ['-t', str(duration)]
                    cmd += ['-y', out]
                elif action == 'compress':
                    out_ext = fmt or ext.lstrip('.').lower() or 'mp4'
                    out = os.path.join(session, f'{base}_compressed.{out_ext}')
                    cmd = [ffmpeg, '-i', src, '-c:v', 'libx264', '-crf', str(crf),
                           '-c:a', 'aac', '-b:a', '128k', '-y', out]
                else:
                    out_ext = fmt or ext.lstrip('.').lower() or 'mp4'
                    out = os.path.join(session, f'{base}.{out_ext}')
                    cmd = [ffmpeg, '-i', src, '-c:v', 'libx264', '-crf', str(crf), '-y', out]
                r = run_cmd(cmd, timeout=3600)
                ok = os.path.isfile(out) and os.path.getsize(out) > 0
                results.append({'name': item['filename'], 'ok': ok,
                                'error': '' if ok else (r['error'] or '处理失败').strip()[-300:],
                                'output': os.path.basename(out) if ok else ''})
                if ok:
                    outputs.append(out)
            if len(outputs) == 1:
                return jsonify({'ok': True, 'results': results, 'single': True,
                                'download': f'/api/plugins/toolbox/file/{os.path.basename(session)}/{os.path.basename(outputs[0])}'})
            from plugins.yulotool.plugin import make_zip_from_files
            zip_path = os.path.join(session, 'media.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/toolbox/file/{os.path.basename(session)}/media.zip'})

        @self.route('/media/merge', methods=['POST'])
        def tb_media_merge():
            ffmpeg = find_tool('ffmpeg')
            if not ffmpeg:
                return jsonify({'ok': False, 'error': '未安装 ffmpeg'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if len(saved) < 2:
                return jsonify({'ok': False, 'error': '请上传至少两个视频'}), 400
            list_path = os.path.join(session, 'list.txt')
            with open(list_path, 'w', encoding='utf-8') as f:
                for item in saved:
                    f.write(f"file '{item['path']}'\n")
            out = os.path.join(session, 'merged.mp4')
            r = run_cmd([ffmpeg, '-f', 'concat', '-safe', '0', '-i', list_path,
                         '-c', 'copy', '-y', out], timeout=3600)
            if not r['ok'] or not os.path.isfile(out):
                return jsonify({'ok': False, 'error': (r['error'] or '合并失败').strip()[-300:]}), 400
            return jsonify({'ok': True, 'files': len(saved),
                            'size': os.path.getsize(out),
                            'download': f'/api/plugins/toolbox/file/{os.path.basename(session)}/merged.mp4'})

        # ==================== 网络 ====================
        @self.route('/search', methods=['GET'])
        def tb_search():
            q = (request.args.get('q') or '').strip()
            if not q:
                return jsonify({'ok': False, 'error': '搜索关键词不能为空'}), 400
            try:
                limit = int(request.args.get('limit') or 10)
            except ValueError:
                limit = 10
            limit = max(1, min(limit, 20))
            return jsonify(_parse_bing(q, limit))

        @self.route('/urlcheck', methods=['POST'])
        def tb_urlcheck():
            data = request.json or {}
            urls = [u for u in (data.get('urls') or []) if isinstance(u, str) and u.strip()]
            if not urls:
                return jsonify({'ok': False, 'error': '请提供 URL 列表'}), 400
            import requests
            results = []
            for url in urls[:20]:
                started = time.time()
                entry = {'url': url}
                try:
                    r = requests.get(url, headers={'User-Agent': USER_AGENT},
                                     timeout=15, allow_redirects=True, verify=False)
                    entry['status'] = r.status_code
                    entry['ok'] = 200 <= r.status_code < 400
                    entry['ms'] = round((time.time() - started) * 1000)
                    entry['final_url'] = r.url
                    entry['size'] = len(r.content)
                except Exception as e:
                    entry['ok'] = False
                    entry['status'] = 0
                    entry['ms'] = round((time.time() - started) * 1000)
                    entry['error'] = str(e)[:150]
                results.append(entry)
            return jsonify({'ok': True, 'results': results})

        @self.route('/rss/feeds', methods=['GET'])
        def tb_rss_list():
            feeds = _load_feeds()
            for f in feeds:
                f['last_fetched'] = f.get('last_fetched')
            return jsonify({'ok': True, 'feeds': feeds})

        def _fetch_feed(url, timeout=20):
            import feedparser
            try:
                resp = _http_get(url, timeout=timeout)
                return feedparser.parse(resp.content)
            except Exception as e:
                return {'bozo': 1, 'bozo_exception': str(e), 'entries': [],
                        'feed': {'title': url}}

        @self.route('/rss/feeds', methods=['POST'])
        def tb_rss_add():
            data = request.json or {}
            url = str(data.get('url', '')).strip()
            name = str(data.get('name', '')).strip()
            if not url:
                return jsonify({'ok': False, 'error': 'RSS 地址不能为空'}), 400
            parsed = _fetch_feed(url)
            if parsed.bozo and not parsed.entries:
                return jsonify({'ok': False, 'error': '无法解析该 RSS 地址'}), 400
            title = (name or parsed.feed.get('title') or url)[:120]
            feeds = _load_feeds()
            for f in feeds:
                if f['url'] == url:
                    return jsonify({'ok': False, 'error': '该订阅源已存在'}), 400
            feeds.append({'url': url, 'name': title, 'added': int(time.time())})
            _save_feeds(feeds)
            return jsonify({'ok': True, 'feeds': feeds})

        @self.route('/rss/feeds/delete', methods=['POST'])
        def tb_rss_del():
            data = request.json or {}
            idx = data.get('idx')
            feeds = _load_feeds()
            if idx is None or not isinstance(idx, int) or idx < 0 or idx >= len(feeds):
                return jsonify({'ok': False, 'error': '订阅源不存在'}), 404
            feeds.pop(idx)
            _save_feeds(feeds)
            return jsonify({'ok': True, 'feeds': feeds})

        @self.route('/rss/fetch', methods=['POST'])
        def tb_rss_fetch():
            data = request.json or {}
            url = str(data.get('url', '')).strip()
            limit = 20
            if not url:
                return jsonify({'ok': False, 'error': 'RSS 地址不能为空'}), 400
            parsed = _fetch_feed(url)
            if parsed.bozo and not parsed.entries:
                return jsonify({'ok': False, 'error': '解析失败或源不可达'}), 400
            entries = []
            for e in parsed.entries[:limit]:
                entries.append({
                    'title': e.get('title', ''),
                    'link': e.get('link', ''),
                    'summary': (e.get('summary') or e.get('description') or '')[:500],
                    'published': e.get('published', ''),
                    'published_ts': time.mktime(e.get('published_parsed', time.localtime())),
                })
            feeds = _load_feeds()
            for f in feeds:
                if f['url'] == url:
                    f['last_fetched'] = int(time.time())
            _save_feeds(feeds)
            return jsonify({'ok': True, 'feed_title': parsed.feed.get('title', url),
                            'entries': entries})

        @self.route('/readability', methods=['POST'])
        def tb_readability():
            data = request.json or {}
            url = str(data.get('url', '')).strip()
            if not url:
                return jsonify({'ok': False, 'error': 'URL 不能为空'}), 400
            try:
                resp = _http_get(url)
            except Exception as e:
                return jsonify({'ok': False, 'error': f'抓取失败: {e}'}), 400
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                tag.decompose()
            title = soup.title.get_text(strip=True) if soup.title else url
            body = soup.body if soup.body else soup
            text = body.get_text(separator='\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
            return jsonify({'ok': True, 'url': url, 'title': title,
                            'length': len(text), 'text': text[:50000]})

        # ==================== 文本 ====================
        @self.route('/text/regex', methods=['POST'])
        def tb_text_regex():
            data = request.json or {}
            pattern = str(data.get('pattern', ''))
            text = str(data.get('text', ''))
            flags = int(data.get('flags') or 0)
            if not pattern:
                return jsonify({'ok': False, 'error': '正则表达式不能为空'}), 400
            try:
                rx = re.compile(pattern, flags)
            except re.error as e:
                return jsonify({'ok': False, 'error': f'正则错误: {e}'}), 400
            matches = []
            for m in rx.finditer(text):
                matches.append({
                    'start': m.start(),
                    'end': m.end(),
                    'match': m.group(0),
                    'groups': list(m.groups()),
                })
            return jsonify({'ok': True, 'pattern': pattern,
                            'count': len(matches), 'matches': matches[:200]})

        @self.route('/text/replace', methods=['POST'])
        def tb_text_replace():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文本文件'}), 400
            find = request.form.get('find') or ''
            replace = request.form.get('replace') or ''
            use_regex = request.form.get('regex') == '1'
            if not find:
                return jsonify({'ok': False, 'error': '查找内容不能为空'}), 400
            try:
                if use_regex:
                    rx = re.compile(find)
                else:
                    rx = None
            except re.error as e:
                return jsonify({'ok': False, 'error': f'正则错误: {e}'}), 400
            results = []
            outputs = []
            for item in saved:
                src = item['path']
                try:
                    content = open(src, 'r', encoding='utf-8', errors='replace').read()
                except Exception as e:
                    results.append({'name': item['filename'], 'ok': False, 'error': str(e)})
                    continue
                new = rx.sub(replace, content) if rx else content.replace(find, replace)
                out = os.path.join(session, item['filename'])
                with open(out, 'w', encoding='utf-8') as f:
                    f.write(new)
                results.append({'name': item['filename'], 'ok': True,
                                'replaced': content != new,
                                'output': os.path.basename(out)})
                outputs.append(out)
            from plugins.yulotool.plugin import make_zip_from_files
            zip_path = os.path.join(session, 'replaced.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/toolbox/file/{os.path.basename(session)}/replaced.zip'})

        @self.route('/text/convert', methods=['POST'])
        def tb_text_convert():
            data = request.json or {}
            content = str(data.get('content', ''))
            action = data.get('action') or 'json2yaml'
            if not content.strip():
                return jsonify({'ok': False, 'error': '内容不能为空'}), 400
            try:
                if action == 'json2yaml':
                    import yaml
                    obj = json.loads(content)
                    out = yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)
                elif action == 'yaml2json':
                    import yaml
                    obj = yaml.safe_load(content)
                    out = json.dumps(obj, ensure_ascii=False, indent=2)
                elif action == 'jsonfmt':
                    obj = json.loads(content)
                    out = json.dumps(obj, ensure_ascii=False, indent=2)
                elif action == 'jsonmin':
                    obj = json.loads(content)
                    out = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
                else:
                    return jsonify({'ok': False, 'error': '未知操作'}), 400
            except Exception as e:
                return jsonify({'ok': False, 'error': f'转换失败: {e}'}), 400
            return jsonify({'ok': True, 'output': out})

        @self.route('/text/stats', methods=['POST'])
        def tb_text_stats():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文本文件'}), 400
            content = open(saved[0]['path'], 'r', encoding='utf-8', errors='replace').read()
            shutil.rmtree(session, ignore_errors=True)
            chars = len(content)
            chars_no_space = len(re.sub(r'\s', '', content))
            words = re.findall(r'\w+', content, re.UNICODE)
            lines = content.splitlines()
            ch_freq = {}
            for ch in re.sub(r'\s', '', content):
                ch_freq[ch] = ch_freq.get(ch, 0) + 1
            top_chars = sorted(ch_freq.items(), key=lambda x: -x[1])[:20]
            return jsonify({
                'ok': True,
                'chars': chars,
                'chars_no_space': chars_no_space,
                'words': len(words),
                'lines': len(lines),
                'bytes': len(content.encode('utf-8')),
                'top_chars': [{'char': c, 'count': n} for c, n in top_chars],
            })
