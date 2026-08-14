import os
import json
import time
import threading
import requests
from flask import request, jsonify
from plugins.base import Plugin

PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PLUGIN_ROOT, 'data')
STORE_FILE = os.path.join(DATA_DIR, 'uptime.json')

HISTORY_LIMIT = 2880
TICK_SECONDS = 2

_lock = threading.RLock()
_loaded = False
_targets = {}


def _load():
    global _targets, _loaded
    with _lock:
        if _loaded:
            return _targets
        _loaded = True
        if os.path.isfile(STORE_FILE):
            try:
                with open(STORE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                _targets = data if isinstance(data, dict) else {}
            except Exception:
                _targets = {}
        else:
            _targets = {}
        return _targets


def _save():
    with _lock:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(STORE_FILE, 'w', encoding='utf-8') as f:
                json.dump(_targets, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def _window_uptime(name):
    t = _targets.get(name)
    if not t:
        return None
    history = t.get('history', [])
    if not history:
        return None
    cutoff = time.time() - 86400
    recent = [h for h in history if h.get('ts', 0) >= cutoff]
    if not recent:
        return None
    ok = sum(1 for h in recent if h.get('ok'))
    return round(ok * 100.0 / len(recent), 1)


def _probe(name):
    t = _targets.get(name)
    if not t:
        return None
    method = t.get('method', 'GET')
    timeout = float(t.get('timeout', 10))
    expected = int(t.get('expected_status', 200))
    start = time.time()
    try:
        r = requests.request(method, t['url'], timeout=timeout,
                             allow_redirects=True,
                             headers={'User-Agent': 'uptime-monitor/1.0'})
        ok = r.status_code == expected
        ms = round((time.time() - start) * 1000)
    except Exception:
        ok = False
        ms = round((time.time() - start) * 1000)
    now = time.time()
    with _lock:
        t = _targets.get(name)
        if t:
            hist = t.setdefault('history', [])
            hist.append({'ts': int(now), 'ok': ok, 'ms': ms})
            if len(hist) > HISTORY_LIMIT:
                del hist[:len(hist) - HISTORY_LIMIT]
            t['last_check'] = int(now)
            t['last_ms'] = ms
            t['last_ok'] = ok
            if ok:
                t['last_up'] = int(now)
            else:
                t['last_down'] = int(now)
            t['uptime'] = _window_uptime(name)
        _save()
    return ok, ms


def _checker_loop():
    while True:
        time.sleep(TICK_SECONDS)
        now = time.time()
        targets = dict(_targets)
        for name, t in targets.items():
            interval = max(int(t.get('interval', 60)), 5)
            last = t.get('last_check', 0)
            if now - last >= interval:
                try:
                    _probe(name)
                except Exception:
                    pass


def _sanitize(name):
    t = _targets.get(name)
    if not t:
        return None
    return {
        'name': name,
        'url': t.get('url', ''),
        'method': t.get('method', 'GET'),
        'timeout': t.get('timeout', 10),
        'interval': t.get('interval', 60),
        'expected_status': t.get('expected_status', 200),
        'last_check': t.get('last_check'),
        'last_ms': t.get('last_ms'),
        'last_ok': t.get('last_ok'),
        'last_up': t.get('last_up'),
        'last_down': t.get('last_down'),
        'uptime': t.get('uptime'),
        'history_count': len(t.get('history', [])),
    }


class UptimePlugin(Plugin):
    name = 'uptime'
    label = 'Uptime 监控'
    icon = ''
    description = '站点探活监控：定时检测 HTTP 目标在线状态、响应时间与可用率'

    def __init__(self):
        super().__init__()
        _load()
        threading.Thread(target=_checker_loop, daemon=True).start()

    def _register_routes(self):
        @self.route('/targets', methods=['GET'])
        def up_targets():
            _load()
            result = [_sanitize(n) for n in _targets]
            result.sort(key=lambda x: x['name'])
            return jsonify(result)

        @self.route('/targets/create', methods=['POST'])
        def up_create():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            url = str(data.get('url', '')).strip()
            if not name or not url:
                return jsonify({'error': 'name 与 url 必填'}), 400
            _load()
            if name in _targets:
                return jsonify({'error': '目标已存在'}), 400
            if not url.startswith(('http://', 'https://')):
                return jsonify({'error': 'url 需以 http(s):// 开头'}), 400
            try:
                timeout = int(data.get('timeout', 10))
                interval = int(data.get('interval', 60))
                expected = int(data.get('expected_status', 200))
            except (TypeError, ValueError):
                return jsonify({'error': 'timeout/interval/expected_status 需为数字'}), 400
            if interval < 5:
                interval = 5
            method = str(data.get('method', 'GET')).upper()
            if method not in ('GET', 'HEAD'):
                method = 'GET'
            with _lock:
                _targets[name] = {
                    'url': url,
                    'method': method,
                    'timeout': timeout,
                    'interval': interval,
                    'expected_status': expected,
                    'history': [],
                    'created': int(time.time()),
                }
                _save()
            return jsonify(_sanitize(name))

        @self.route('/targets/update', methods=['POST'])
        def up_update():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            _load()
            if name not in _targets:
                return jsonify({'error': '目标不存在'}), 404
            t = _targets[name]
            url = str(data.get('url', '')).strip()
            if url:
                if not url.startswith(('http://', 'https://')):
                    return jsonify({'error': 'url 需以 http(s):// 开头'}), 400
                t['url'] = url
            if data.get('method'):
                method = str(data['method']).upper()
                if method in ('GET', 'HEAD'):
                    t['method'] = method
            for key in ('timeout', 'interval', 'expected_status'):
                if key in data and data[key] not in (None, ''):
                    try:
                        val = int(data[key])
                    except (TypeError, ValueError):
                        return jsonify({'error': '%s 需为数字' % key}), 400
                    if key == 'interval' and val < 5:
                        val = 5
                    t[key] = val
            with _lock:
                _save()
            return jsonify(_sanitize(name))

        @self.route('/targets/delete', methods=['POST'])
        def up_delete():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            _load()
            if name not in _targets:
                return jsonify({'error': '目标不存在'}), 404
            with _lock:
                del _targets[name]
                _save()
            return jsonify({'ok': True})

        @self.route('/targets/test', methods=['POST'])
        def up_test():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            _load()
            if name not in _targets:
                return jsonify({'error': '目标不存在'}), 404
            t = _targets[name]
            try:
                r = requests.request(t.get('method', 'GET'), t['url'],
                                     timeout=float(t.get('timeout', 10)),
                                     allow_redirects=True,
                                     headers={'User-Agent': 'uptime-monitor/1.0'})
                ok = r.status_code == int(t.get('expected_status', 200))
                ms = int(r.elapsed.total_seconds() * 1000)
                code = r.status_code
            except requests.exceptions.Timeout:
                return jsonify({'name': name, 'ok': False, 'ms': int(t.get('timeout', 10) * 1000), 'error': '连接超时'})
            except Exception as e:
                return jsonify({'name': name, 'ok': False, 'ms': 0, 'error': str(e)})
            return jsonify({'name': name, 'ok': ok, 'ms': ms, 'status_code': code,
                            'expected': int(t.get('expected_status', 200))})

        @self.route('/targets/history', methods=['GET'])
        def up_history():
            name = request.args.get('name', '')
            _load()
            t = _targets.get(name)
            if not t:
                return jsonify([])
            return jsonify(t.get('history', []))

        @self.route('/targets/status24', methods=['GET'])
        def up_status24():
            name = request.args.get('name', '')
            _load()
            t = _targets.get(name)
            if not t:
                return jsonify([])
            hist = t.get('history', [])
            bucket = 300
            buckets = 288
            now = int(time.time())
            start = now - buckets * bucket
            cells = [None] * buckets
            prev = None
            for h in hist:
                ts = h.get('ts', 0)
                if ts < start:
                    continue
                idx = (ts - start) // bucket
                if 0 <= idx < buckets:
                    ok = 1 if h.get('ok') else 0
                    cells[idx] = ok
                    prev = ok
            result = []
            for c in cells:
                if c is None:
                    c = prev
                result.append(c)
            return jsonify(result)

        @self.route('/status', methods=['GET'])
        def up_status():
            _load()
            total = len(_targets)
            online = sum(1 for n in _targets if _targets[n].get('last_ok'))
            offline = total - online
            u = [t.get('uptime') for t in _targets.values() if t.get('uptime') is not None]
            avg = round(sum(u) / len(u), 1) if u else None
            return jsonify({'total': total, 'online': online, 'offline': offline,
                            'avg_uptime': avg})
