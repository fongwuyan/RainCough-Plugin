# -*- coding: utf-8 -*-
"""Docker 管理插件 v2 (重写)

容器/镜像/卷/网络/日志/启停/创建/Compose/资源清理。
命令统一走 subprocess(list), 不做 shell 拼接; 输出统一 JSON。
daemon 未启动时 /info 等返回明确的 503 状态与提示, 前端可一键启动。
"""
import json
import os
import shutil
import subprocess
import threading

from flask import request, jsonify
from plugins.base import Plugin

DOCKER = shutil.which('docker') or '/usr/bin/docker'
COMPOSE = shutil.which('docker-compose') or shutil.which('compose') or None


def _run(args, timeout=120):
    try:
        r = subprocess.run([DOCKER] + args, capture_output=True, text=True, timeout=timeout)
        return r
    except subprocess.TimeoutExpired:
        return None


def _ok(args, timeout=120):
    r = _run(args, timeout)
    if r is None:
        return {'ok': False, 'error': 'docker 命令超时'}
    if r.returncode != 0:
        return {'ok': False, 'error': (r.stderr or r.stdout or '').strip()[-500:]}
    return {'ok': True, 'out': r.stdout.strip()}


def _j(args, timeout=120):
    r = _ok(args, timeout)
    if not r['ok']:
        return None, r['error']
    try:
        return json.loads(r['out'] or 'null'), None
    except Exception:
        return None, 'docker 输出非 JSON'


def _err(msg, code=500):
    return jsonify({'error': msg}), code


def _many(args, timeout=120):
    r = _ok(args, timeout)
    if not r['ok']:
        return None, r['error']
    return _lines(r['out']), None


def _lines(text):
    out = []
    for line in (text or '').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def _ctr_summary(c):
    names = (c.get('Names') or '').replace('/', '')
    ports = [p.strip() for p in (c.get('Ports') or '').split(',') if p.strip() and p.strip() != 'Ports']
    return {
        'id': (c.get('ID') or '')[:12],
        'name': (names.split(',')[0] if names else ''),
        'image': c.get('Image') or '',
        'status': c.get('Status') or '',
        'state': c.get('State') or '',
        'ports': ports,
        'command': c.get('Command') or '',
        'created': c.get('CreatedAt') or '',
    }


def _img_summary(i):
    tags = (i.get('RepoTags') or [])
    if tags == ['<none>:<none>']:
        tags = []
    return {
        'id': (i.get('ID') or '').replace('sha256:', '')[:12],
        'tags': tags,
        'size': i.get('Size') or 0,
        'created': i.get('CreatedSince') or i.get('CreatedAt') or '',
    }


class DockerPlugin(Plugin):
    name = 'docker'
    label = 'Docker 管理'
    icon = ''
    description = '容器/镜像/卷/网络/日志与 Compose 管理'

    def _register_routes(self):
        def _daemon_ok():
            data, err = _j(['info', '--format', '{{json .}}'])
            return data, err

        @self.route('/env', methods=['GET'])
        def env():
            return jsonify({
                'docker': bool(DOCKER), 'docker_tool': DOCKER,
                'compose': bool(COMPOSE), 'compose_tool': COMPOSE,
                'group': 'docker' in (os.getgroups() or []),
                'version': shutil.which('docker') and (os.popen('docker --version 2>/dev/null').read().strip() or ''),
            })

        @self.route('/info', methods=['GET'])
        def info():
            data, err = _daemon_ok()
            if data is None:
                return _err('docker daemon 未就绪: %s' % (err or 'unknown'), 503)
            return jsonify({
                'server_version': data.get('ServerVersion'),
                'os': data.get('OperatingSystem'),
                'arch': data.get('Architecture'),
                'kernel': data.get('KernelVersion'),
                'drivers': data.get('Driver'),
                'root_dir': data.get('DockerRootDir'),
                'cpus': data.get('NCPU'),
                'mem': data.get('MemTotal'),
                'images': data.get('Images'),
                'containers': data.get('Containers'),
                'containers_running': data.get('ContainersRunning'),
                'containers_paused': data.get('ContainersPaused'),
                'containers_stopped': data.get('ContainersStopped'),
            })

        @self.route('/status', methods=['GET'])
        def status():
            data, err = _daemon_ok()
            if data is None:
                return _err('docker daemon 未就绪', 503)
            df, derr = _j(['system', 'df', '--format', '{{json .}}'])
            disk = {}
            if derr is None and isinstance(df, list) and df:
                disk = {'total': df[0].get('TotalCount'), 'active': df[0].get('ActiveCount')}
            return jsonify({
                'version': data.get('ServerVersion'),
                'images': data.get('Images'),
                'running': data.get('ContainersRunning'),
                'paused': data.get('ContainersPaused'),
                'stopped': data.get('ContainersStopped'),
                'disk': disk,
            })

        @self.route('/containers', methods=['GET'])
        def containers():
            data, err = _many(['ps', '-a', '--format', '{{json .}}'])
            if data is None:
                return _err(str(err), 503)
            return jsonify([_ctr_summary(c) for c in data])

        def _by_id(kind):
            data = request.get_json(silent=True) or {}
            cid = str(data.get('id') or data.get('name') or '').strip()
            if not cid:
                return None, '缺少 id', None
            return cid, '', data

        @self.route('/containers/start', methods=['POST'])
        def c_start():
            cid, e, _ = _by_id(None)
            if e:
                return _err(e, 400)
            r = _ok(['start', cid])
            return jsonify({'ok': r['ok'], 'error': r.get('error', '')})

        @self.route('/containers/stop', methods=['POST'])
        def c_stop():
            cid, e, _ = _by_id(None)
            if e:
                return _err(e, 400)
            data = request.get_json(silent=True) or {}
            t = str(data.get('timeout', 10) or 10)
            r = _ok(['stop', '-t', t, cid])
            return jsonify({'ok': r['ok'], 'error': r.get('error', '')})

        @self.route('/containers/restart', methods=['POST'])
        def c_restart():
            cid, e, _ = _by_id(None)
            if e:
                return _err(e, 400)
            r = _ok(['restart', cid])
            return jsonify({'ok': r['ok'], 'error': r.get('error', '')})

        @self.route('/containers/remove', methods=['POST'])
        def c_remove():
            cid, e, data = _by_id(None)
            if e:
                return _err(e, 400)
            args = ['rm']
            if data.get('force'):
                args.append('-f')
            if data.get('volumes'):
                args.append('-v')
            args.append(cid)
            r = _ok(args)
            return jsonify({'ok': r['ok'], 'error': r.get('error', '')})

        @self.route('/containers/logs', methods=['GET'])
        def c_logs():
            cid = request.args.get('id', '').strip()
            if not cid:
                return _err('缺少 id', 400)
            tail = max(10, min(int(request.args.get('tail', 200) or 200), 5000))
            r = _ok(['logs', '--tail', str(tail), '-t', cid], timeout=60)
            return jsonify({'ok': r['ok'], 'log': r.get('out', ''), 'error': r.get('error', '')})

        @self.route('/containers/stats', methods=['GET'])
        def c_stats():
            cid = request.args.get('id', '').strip()
            if not cid:
                return _err('缺少 id', 400)
            r = _ok(['stats', '--no-stream', '--format', '{{json .}}', cid], timeout=60)
            if not r['ok']:
                return jsonify({'ok': False, 'error': r.get('error', '')})
            rows = _lines(r['out'])
            if not rows:
                return jsonify({'ok': False, 'error': '无统计'})
            d = rows[0]
            return jsonify({'ok': True, 'cpu': d.get('CPUPerc', ''), 'mem': d.get('MemUsage', ''),
                            'net': d.get('NetIO', ''), 'block': d.get('BlockIO', '')})

        @self.route('/containers/create', methods=['POST'])
        def c_create():
            data = request.get_json(silent=True) or {}
            image = str(data.get('image', '')).strip()
            if not image:
                return _err('缺少镜像', 400)
            args = ['run', '-d']
            name = str(data.get('name', '')).strip()
            if name:
                args += ['--name', name]
            if data.get('restart'):
                args += ['--restart', str(data['restart'])]
            if data.get('network'):
                args += ['--network', str(data['network'])]
            for p in (data.get('ports') or []):
                if str(p).strip():
                    args += ['-p', str(p).strip()]
            for e in (data.get('env') or []):
                if str(e).strip():
                    args += ['-e', str(e).strip()]
            for v in (data.get('volumes') or []):
                if str(v).strip():
                    args += ['-v', str(v).strip()]
            args.append(image)
            args += [str(x) for x in (data.get('cmd') or [])]
            r = _ok(args, timeout=300)
            return jsonify({'ok': r['ok'], 'id': r.get('out', '')[:24], 'error': r.get('error', '')})

        @self.route('/images', methods=['GET'])
        def images():
            data, err = _many(['images', '--format', '{{json .}}'])
            if data is None:
                return _err(str(err), 503)
            return jsonify([_img_summary(i) for i in data])

        @self.route('/images/pull', methods=['POST'])
        def pull():
            data = request.get_json(silent=True) or {}
            name = str(data.get('name', '')).strip()
            if not name:
                return _err('缺少镜像名', 400)

            def _work():
                r = _ok(['pull', name], timeout=1800)
                try:
                    task = None
                    if hasattr(self, '_tasks'):
                        pass
                    print('[docker] pull %s rc=%s %s' % (name, r['ok'], (r.get('error') or '')[:120]))
                except Exception:
                    pass

            threading.Thread(target=_work, daemon=True).start()
            return jsonify({'ok': True, 'message': '拉取中(后台), 稍后刷新镜像列表'})

        @self.route('/images/remove', methods=['POST'])
        def remove_image():
            data = request.get_json(silent=True) or {}
            iid = str(data.get('id', '')).strip()
            if not iid:
                return _err('缺少 id', 400)
            args = ['rmi']
            if data.get('force'):
                args.append('-f')
            args.append(iid)
            r = _ok(args)
            return jsonify({'ok': r['ok'], 'error': r.get('error', '')})

        @self.route('/networks', methods=['GET'])
        def networks():
            data, err = _many(['network', 'ls', '--format', '{{json .}}'])
            if data is None:
                return _err(str(err), 503)
            items = data
            return jsonify([{'id': (n.get('ID') or '')[:12], 'name': n.get('Name') or '',
                             'driver': n.get('Driver') or '', 'scope': n.get('Scope') or ''} for n in items])

        @self.route('/volumes', methods=['GET'])
        def volumes():
            data, err = _many(['volume', 'ls', '--format', '{{json .}}'])
            if data is None:
                return _err(str(err), 503)
            return jsonify([{'name': v.get('Name') or '', 'driver': v.get('Driver') or ''} for v in data])

        @self.route('/volume/remove', methods=['POST'])
        def volume_remove():
            data = request.get_json(silent=True) or {}
            vname = str(data.get('name', '')).strip()
            if not vname:
                return _err('缺少卷名', 400)
            r = _ok(['volume', 'rm', vname])
            return jsonify({'ok': r['ok'], 'error': r.get('error', '')})

        @self.route('/system/prune', methods=['POST'])
        def prune():
            data = request.get_json(silent=True) or {}
            args = ['system', 'prune', '-f']
            if data.get('all'):
                args.append('-a')
            if data.get('volumes'):
                args.append('--volumes')
            r = _ok(args, timeout=600)
            return jsonify({'ok': r['ok'], 'out': r.get('out', ''), 'error': r.get('error', '')})

        @self.route('/compose/up', methods=['POST'])
        def compose_up():
            if not COMPOSE:
                return _err('未安装 docker compose', 400)
            data = request.get_json(silent=True) or {}
            path = str(data.get('path', '')).strip()
            if not path or not os.path.isdir(path):
                return _err('需要有效项目目录 path', 400)
            try:
                r = subprocess.run([COMPOSE, '-f', os.path.join(path, 'docker-compose.yml'), 'up', '-d'],
                                   capture_output=True, text=True, timeout=600, cwd=path)
                ok = r.returncode == 0
                return jsonify({'ok': ok, 'out': (r.stdout or '')[-600:], 'error': (r.stderr or '')[-400:]})
            except Exception as ex:
                return _err(str(ex), 500)

        @self.route('/compose/down', methods=['POST'])
        def compose_down():
            if not COMPOSE:
                return _err('未安装 docker compose', 400)
            data = request.get_json(silent=True) or {}
            path = str(data.get('path', '')).strip()
            if not path or not os.path.isdir(path):
                return _err('需要有效项目目录 path', 400)
            try:
                r = subprocess.run([COMPOSE, '-f', os.path.join(path, 'docker-compose.yml'), 'down'],
                                   capture_output=True, text=True, timeout=600, cwd=path)
                return jsonify({'ok': r.returncode == 0, 'out': (r.stdout or '')[-600:], 'error': (r.stderr or '')[-400:]})
            except Exception as ex:
                return _err(str(ex), 500)

        @self.route('/compose/ps', methods=['POST'])
        def compose_ps():
            data = request.get_json(silent=True) or {}
            path = str(data.get('path', '')).strip()
            if not path or not os.path.isdir(path):
                return _err('需要有效项目目录 path', 400)
            r = _ok(['compose', '-f', os.path.join(path, 'docker-compose.yml'), 'ps'], timeout=120)
            if not r['ok']:
                r2 = subprocess.run([COMPOSE, '-f', os.path.join(path, 'docker-compose.yml'), 'ps'],
                                    capture_output=True, text=True, timeout=120, cwd=path)
                return jsonify({'ok': r2.returncode == 0, 'out': (r2.stdout or '')[-800:]})
            return jsonify({'ok': True, 'out': r['out'][-800:]})
