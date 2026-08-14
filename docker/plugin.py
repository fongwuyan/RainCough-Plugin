import json
import shutil
import subprocess
import threading
from flask import request, jsonify
from plugins.base import Plugin

DOCKER = shutil.which('docker') or '/usr/bin/docker'


def _run(args, timeout=60):
    try:
        r = subprocess.run([DOCKER] + args, capture_output=True, text=True, timeout=timeout)
        return r
    except subprocess.TimeoutExpired:
        return None


def _ok(args, timeout=60):
    r = _run(args, timeout)
    if r is None:
        return {'ok': False, 'error': 'docker 命令超时'}
    if r.returncode != 0:
        return {'ok': False, 'error': (r.stderr or r.stdout or '').strip()[-500:]}
    return {'ok': True, 'out': r.stdout.strip()}


def _err(msg):
    return jsonify({'error': msg}), 500


def _parse_json_lines(text):
    result = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            result.append(json.loads(line))
        except Exception:
            pass
    return result


def _ctr_summary(c):
    ports = []
    for p in (c.get('Ports') or '').split(','):
        p = p.strip()
        if p and p != 'Ports':
            ports.append(p)
    names = (c.get('Names') or '').replace('/', '').split(',')
    return {
        'id': (c.get('ID') or '')[:12],
        'name': names[0] if names else '',
        'image': c.get('Image') or '',
        'status': c.get('Status') or '',
        'state': c.get('State') or '',
        'ports': ports,
        'created': c.get('CreatedAt') or '',
        'command': c.get('Command') or '',
    }


def _img_summary(i):
    size = i.get('Size') or ''
    tags = i.get('RepoTags') or []
    repo = i.get('Repository') or ''
    tag = i.get('Tag') or ''
    if tags:
        labels = tags
    elif repo:
        labels = ['%s:%s' % (repo, tag) if tag else repo]
    else:
        labels = ['<none>:%s' % tag] if tag else ['<none>']
    return {
        'id': (i.get('ID') or '').replace('sha256:', '')[:12],
        'tags': labels,
        'repo': repo,
        'tag': tag,
        'size': size,
        'created': i.get('CreatedSince') or '',
    }


class DockerPlugin(Plugin):
    name = 'docker'
    label = 'Docker 管理'
    icon = ''
    description = 'Docker 容器与镜像管理：列表、启停、删除、日志、拉取/删除镜像'

    def _register_routes(self):
        @self.route('/info', methods=['GET'])
        def dk_info():
            r = _run(['version', '--format', '{{.Server.Version}}'], timeout=20)
            version = r.stdout.strip() if r and r.returncode == 0 else None
            rc = _run(['container', 'ls', '-a', '--format', '{{.ID}}'], timeout=20)
            ri = _run(['image', 'ls', '-q'], timeout=20)
            rn = _run(['network', 'ls', '-q'], timeout=20)
            rv = _run(['volume', 'ls', '-q'], timeout=20)
            def count(res):
                if res and res.returncode == 0:
                    return len([l for l in res.stdout.splitlines() if l.strip()])
                return 0
            running = _run(['container', 'ls', '-q'], timeout=20)
            return jsonify({
                'version': version,
                'containers_total': count(rc),
                'containers_running': count(running),
                'images': count(ri),
                'networks': count(rn),
                'volumes': count(rv),
            })

        @self.route('/containers', methods=['GET'])
        def dk_containers():
            r = _run(['container', 'ls', '-a', '--format', '{{json .}}'], timeout=30)
            if r is None:
                return _err('docker 命令超时')
            if r.returncode != 0:
                return _err((r.stderr or r.stdout or '').strip()[-300:])
            items = _parse_json_lines(r.stdout)
            return jsonify([_ctr_summary(c) for c in items])

        @self.route('/containers/start', methods=['POST'])
        def dk_start():
            cid = (request.json or {}).get('id', '')
            if not cid:
                return _err('缺少 id')
            res = _ok(['container', 'start', cid], timeout=30)
            if not res['ok']:
                return _err(res['error'])
            return jsonify({'ok': True})

        @self.route('/containers/stop', methods=['POST'])
        def dk_stop():
            cid = (request.json or {}).get('id', '')
            if not cid:
                return _err('缺少 id')
            res = _ok(['container', 'stop', cid], timeout=60)
            if not res['ok']:
                return _err(res['error'])
            return jsonify({'ok': True})

        @self.route('/containers/restart', methods=['POST'])
        def dk_restart():
            cid = (request.json or {}).get('id', '')
            if not cid:
                return _err('缺少 id')
            res = _ok(['container', 'restart', cid], timeout=60)
            if not res['ok']:
                return _err(res['error'])
            return jsonify({'ok': True})

        @self.route('/containers/remove', methods=['POST'])
        def dk_remove():
            data = request.json or {}
            cid = data.get('id', '')
            if not cid:
                return _err('缺少 id')
            force = bool(data.get('force', True))
            args = ['container', 'rm']
            if force:
                args.append('-f')
            args.append(cid)
            res = _ok(args, timeout=60)
            if not res['ok']:
                return _err(res['error'])
            return jsonify({'ok': True})

        @self.route('/containers/logs', methods=['GET'])
        def dk_logs():
            cid = request.args.get('id', '')
            tail = request.args.get('tail', '200')
            if not cid:
                return _err('缺少 id')
            r = _run(['container', 'logs', '--tail', str(tail), cid], timeout=30)
            if r is None:
                return _err('docker 命令超时')
            if r.returncode != 0:
                return _err((r.stderr or '').strip()[-300:])
            return jsonify({'logs': (r.stdout + r.stderr).rstrip()})

        @self.route('/containers/stats', methods=['GET'])
        def dk_stats():
            cid = request.args.get('id', '')
            if not cid:
                return _err('缺少 id')
            r = _run(['container', 'stats', '--no-stream', '--format', '{{json .}}', cid], timeout=30)
            if r is None:
                return _err('docker 命令超时')
            if r.returncode != 0:
                return _err((r.stderr or r.stdout or '').strip()[-300:])
            items = _parse_json_lines(r.stdout)
            if not items:
                return jsonify({})
            s = items[0]
            return jsonify({
                'cpu': s.get('CPUPerc', ''),
                'mem_usage': s.get('MemUsage', ''),
                'mem_perc': s.get('MemPerc', ''),
                'net_io': s.get('NetIO', ''),
                'block_io': s.get('BlockIO', ''),
                'pids': s.get('PIDs', ''),
            })

        @self.route('/images', methods=['GET'])
        def dk_images():
            r = _run(['image', 'ls', '--format', '{{json .}}'], timeout=30)
            if r is None:
                return _err('docker 命令超时')
            if r.returncode != 0:
                return _err((r.stderr or r.stdout or '').strip()[-300:])
            items = _parse_json_lines(r.stdout)
            result = []
            for i in items:
                result.append(_img_summary(i))
            return jsonify(result)

        @self.route('/images/pull', methods=['POST'])
        def dk_pull():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            if not name:
                return _err('缺少镜像名')
            try:
                from tasks import begin, update, finish
            except Exception:
                begin = update = finish = None

            def _work():
                if begin:
                    tid = begin('docker', '拉取镜像 %s' % name, kind='download')
                else:
                    tid = None
                try:
                    res = _ok(['image', 'pull', name], timeout=900)
                    if tid:
                        if res['ok']:
                            finish(tid, True, message=res['out'])
                        else:
                            finish(tid, False, error=res['error'])
                except Exception as e:
                    if tid:
                        finish(tid, False, error=str(e))

            threading.Thread(target=_work, daemon=True).start()
            return jsonify({'ok': True, 'message': '已开始拉取镜像: ' + name})

        @self.route('/images/remove', methods=['POST'])
        def dk_remove_image():
            data = request.json or {}
            iid = data.get('id', '')
            if not iid:
                return _err('缺少 id')
            force = bool(data.get('force', True))
            args = ['image', 'rm']
            if force:
                args.append('-f')
            args.append(iid)
            res = _ok(args, timeout=60)
            if not res['ok']:
                return _err(res['error'])
            return jsonify({'ok': True, 'message': res['out']})

        @self.route('/networks', methods=['GET'])
        def dk_networks():
            r = _run(['network', 'ls', '--format', '{{json .}}'], timeout=20)
            if r is None:
                return _err('docker 命令超时')
            if r.returncode != 0:
                return _err((r.stderr or r.stdout or '').strip()[-300:])
            items = _parse_json_lines(r.stdout)
            return jsonify([{
                'id': (n.get('ID') or '')[:12],
                'name': n.get('Name') or '',
                'driver': n.get('Driver') or '',
                'scope': n.get('Scope') or '',
            } for n in items])

        @self.route('/volumes', methods=['GET'])
        def dk_volumes():
            r = _run(['volume', 'ls', '--format', '{{json .}}'], timeout=20)
            if r is None:
                return _err('docker 命令超时')
            if r.returncode != 0:
                return _err((r.stderr or r.stdout or '').strip()[-300:])
            items = _parse_json_lines(r.stdout)
            return jsonify([{
                'name': v.get('Name') or '',
                'driver': v.get('Driver') or '',
                'mountpoint': v.get('Mountpoint') or '',
            } for v in items])
