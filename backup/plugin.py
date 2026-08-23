# -*- coding: utf-8 -*-
"""系统备份: 目录打包(tar.gz/tar), 保留轮换, 可定时, 接入统一任务队列。

架构: 前端 Vue 组件 -> plugins/backup/plugin.py
      -> subprocess tar 打包(无第三方依赖) + threading 定时调度
功能: 备份任务(多来源路径/目标目录/压缩方式/保留份数/间隔小时/排除规则) /
      立即备份 / 运行历史(时长/大小/状态/删除归档) / 任务队列可见进度 /
      开机中断任务标记 / 可选 tar 读校验。
"""
import os
import re
import json
import time
import shutil
import threading
import subprocess
from datetime import datetime

from flask import jsonify, request
from plugins.base import Plugin

PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PLUGIN_ROOT, 'data')
JOBS_FILE = os.path.join(DATA_DIR, 'backup.json')
CFG_FILE = os.path.join(DATA_DIR, 'config.json')
MAX_RUNS_PER_JOB = 20
WORKER_INTERVAL = 30  # 秒

_LOCK = threading.RLock()
_running = set()  # 正在执行的 job 名


def _load_json(path, default):
    if os.path.isfile(path):
        try:
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            if isinstance(d, type(default)):
                return d
        except Exception:
            pass
    return default


def _save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        pass


def _load_jobs():
    with _LOCK:
        return _load_json(JOBS_FILE, {})


def _save_jobs(jobs):
    with _LOCK:
        _save_json(JOBS_FILE, jobs)


def _load_conf():
    with _LOCK:
        return _load_json(CFG_FILE, {})


def _save_conf(cfg):
    with _LOCK:
        _save_json(CFG_FILE, cfg)


DEFAULT_CONF = {'default_target': '/opt/touchgal/backups', 'default_keep': 5,
                'verify_archive': True}


def _conf():
    cfg = dict(DEFAULT_CONF)
    cfg.update(_load_conf())
    return cfg


def _slug(name):
    return re.sub(r'[^\w.\-\u4e00-\u9fff]+', '_', name).strip('_') or 'backup'


def _valid_name(name):
    return bool(re.match(r'^[A-Za-z0-9_\-\u4e00-\u9fff]{1,40}$', str(name or '')))


def _validate_sources(sources):
    out = []
    for s in (sources or []):
        p = str(s).strip()
        if not p or not os.path.isabs(p):
            continue
        out.append(os.path.normpath(p.rstrip(os.sep)))
    return out


def _timestamp():
    return datetime.now().strftime('%Y%m%d-%H%M%S')


def _fmt_size(b):
    b = float(b or 0)
    for u in ('B', 'KB', 'MB', 'GB', 'TB'):
        if b < 1024 or u == 'TB':
            return ('%d %s' % (int(b), u)) if u == 'B' else ('%.1f %s' % (b, u))
        b /= 1024
    return '0 B'


def _tz_ts(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return '-'


def _job_out(job, runs):
    running = job['name'] in _running
    last = runs[0] if runs else None
    next_run = None
    if job.get('interval_hours') and not running:
        base = (last or {}).get('end') or (last or {}).get('start') or job.get('created') or time.time()
        next_run = base + int(job['interval_hours']) * 3600
    return {
        'name': job['name'],
        'sources': list(job.get('sources', [])),
        'target': job.get('target', ''),
        'compress': job.get('compress', 'gz'),
        'keep': int(job.get('keep', 5)),
        'interval_hours': int(job.get('interval_hours', 0)),
        'excludes': list(job.get('excludes', [])),
        'paused': bool(job.get('paused', False)),
        'created': job.get('created'),
        'running': running,
        'last_run': last,
        'next_run': int(next_run) if next_run else None,
    }


def _build_tar(job, out):
    """构造 tar 子进程参数; 返回 (cmd, cwd)。"""
    cmd = ['tar', '-c']
    if job.get('compress') == 'gz':
        cmd.append('-z')
    cmd += ['-f', out]
    for ex in job.get('excludes') or []:
        if str(ex).strip():
            cmd.append('--exclude=' + str(ex).strip())
    for src in job.get('sources') or []:
        src = src.rstrip(os.sep) or '/'
        cmd += ['-C', os.path.dirname(src), os.path.basename(src)]
    return cmd


def _rotate_keep(job, out_file):
    """按保留份数清理该任务旧归档。"""
    keep = max(1, int(job.get('keep', 5)))
    target = job.get('target', '')
    prefix = _slug(job['name']) + '-'
    try:
        files = []
        for f in os.listdir(target):
            if f.startswith(prefix) and re.match(r'^' + re.escape(prefix) + r'\d{8}-\d{6}\.tar(\.gz)?$', f):
                fp = os.path.join(target, f)
                if os.path.isfile(fp) and fp != out_file:
                    files.append((os.path.getmtime(fp), fp))
        files.sort(reverse=True)
        for _, fp in files[keep - 1:]:
            try:
                os.remove(fp)
            except OSError:
                pass
    except Exception:
        pass


def _run_backup(job, manual=False):
    name = job['name']
    if name in _running:
        return {'ok': False, 'error': '任务正在执行中: ' + name}
    with _LOCK:
        _running.add(name)
    tid = None
    try:
        from tasks import begin, update, finish
        tid = begin('backup', '备份 %s' % name, kind='backup')
        update(tid, phase='prepare', progress=5, message='准备打包…')

        target = job.get('target', '')
        if not target or not os.path.isdir(target):
            raise RuntimeError('目标目录不存在或不可写: ' + (target or '(空)'))
        start = time.time()
        os.makedirs(target, exist_ok=True)
        out = os.path.join(target, '%s-%s.tar%s' % (_slug(name), _timestamp(), '.gz' if job.get('compress') == 'gz' else ''))

        update(tid, phase='packing', progress=30, message='tar 打包中…')
        cmd = _build_tar(job, out)
        rc = subprocess.run(cmd, capture_output=True, timeout=7200)
        if rc.returncode != 0:
            err = (rc.stderr or b'').decode('utf-8', 'replace').strip()
            raise RuntimeError('打包失败: %s' % (err[:300] or 'tar 退出码 %d' % rc.returncode))

        update(tid, phase='verify', progress=85, message='校验归档…')
        if _conf().get('verify_archive', True):
            vrc = subprocess.run(['tar', '-tf', out], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, timeout=180)
            if vrc.returncode != 0:
                try:
                    os.remove(out)
                except OSError:
                    pass
                raise RuntimeError('归档校验失败(损坏?): ' + os.path.basename(out))

        size = os.path.getsize(out)
        _rotate_keep(job, out)
        end = time.time()
        _record(job, out, start, end, size, 'done', '')
        finish(tid, True, message='备份完成 %s (%s)' % (os.path.basename(out), _fmt_size(size)))
        return {'ok': True, 'file': out, 'size': size}
    except subprocess.TimeoutExpired:
        _record(job, '', start if 'start' in dir() else time.time(), time.time(), 0, 'error', '执行超时')
        if tid:
            from tasks import finish as tf
            tf(tid, False, error='执行超时')
        return {'ok': False, 'error': '执行超时'}
    except Exception as e:
        msg = str(e)
        _record(job, '', 0, 0, 0, 'error', msg)
        if tid:
            from tasks import finish as tf
            tf(tid, False, error=msg)
        return {'ok': False, 'error': msg}
    finally:
        with _LOCK:
            _running.discard(name)


def _record(job, out_file, start, end, size, status, error):
    with _LOCK:
        jobs = _load_jobs()
        j = jobs.get(job['name'])
        if not j:
            return
        runs = j.setdefault('runs', [])
        runs.insert(0, {
            'file': out_file, 'start': int(start), 'end': int(end or time.time()),
            'duration': round((end or time.time()) - start, 1),
            'size': size, 'status': status, 'error': str(error or ''),
        })
        del runs[MAX_RUNS_PER_JOB:]
        j['last_run'] = int(start or time.time())
        j['last_status'] = status
        _save_jobs(jobs)


def _stale_mark():
    """服务重启后, 把未完成任务标记为 interrupted。"""
    with _LOCK:
        jobs = _load_jobs()
        for j in jobs.values():
            runs = j.setdefault('runs', [])
            if runs and runs[0].get('status') in ('running',):
                runs[0]['status'] = 'interrupted'
                runs[0]['error'] = '备份被中断(服务重启)'
        _save_jobs(jobs)


_stale_mark()


def _worker_loop():
    while True:
        try:
            with _LOCK:
                jobs = _load_jobs()
            now = time.time()
            for job in jobs.values():
                if job.get('paused') or job['name'] in _running:
                    continue
                iv = int(job.get('interval_hours', 0) or 0)
                if iv <= 0:
                    continue
                last = (job.get('runs') or [{}])[0].get('end') or job.get('created') or now
                if now - last >= iv * 3600:
                    t = threading.Thread(target=_run_backup, args=(job,), daemon=True)
                    t.start()
        except Exception:
            pass
        time.sleep(WORKER_INTERVAL)


class BackupPlugin(Plugin):
    name = 'backup'
    label = '系统备份'
    icon = ''
    description = '目录打包备份与保留轮换: 多来源路径/tar.gz 定时打包, 保留 N 份, 运行历史, 接入任务队列'

    def __init__(self):
        super().__init__()
        try:
            threading.Thread(target=_worker_loop, daemon=True).start()
        except Exception:
            pass

    def get_setting_schema(self):
        cfg = _conf()
        return [
            {'key': 'default_target', 'label': '默认备份目录', 'type': 'text',
             'value': cfg.get('default_target', ''),
             'help': '新建任务时的默认目标目录(建议放外置盘/挂载点)'},
            {'key': 'default_keep', 'label': '默认保留份数', 'type': 'number',
             'value': cfg.get('default_keep', 5)},
            {'key': 'verify_archive', 'label': '打包后校验归档', 'type': 'switch',
             'value': bool(cfg.get('verify_archive', True))},
        ]

    def get_settings(self):
        cfg = _conf()
        return {'default_target': cfg.get('default_target', ''),
                'default_keep': cfg.get('default_keep', 5),
                'verify_archive': bool(cfg.get('verify_archive', True))}

    def save_settings(self, data):
        cfg = _load_conf()
        if 'default_target' in data:
            cfg['default_target'] = str(data['default_target'] or '').strip()
        if 'default_keep' in data:
            try:
                cfg['default_keep'] = max(1, int(data['default_keep']))
            except Exception:
                pass
        if 'verify_archive' in data:
            cfg['verify_archive'] = bool(data['verify_archive'])
        _save_conf(cfg)
        return True, '已保存'

    def _register_routes(self):
        @self.route('/jobs', methods=['GET'])
        def jobs_list():
            jobs = _load_jobs()
            return jsonify({'jobs': [_job_out(j, j.get('runs', []))
                                     for j in jobs.values()]})

        @self.route('/jobs', methods=['POST'])
        def jobs_create():
            data = request.get_json(silent=True) or {}
            name = str(data.get('name', '')).strip()
            if not _valid_name(name):
                return jsonify({'error': '任务名仅允许字母/数字/下划线/中文, 最长40'}), 400
            jobs = _load_jobs()
            if name in jobs:
                return jsonify({'error': '任务已存在'}), 409
            sources = _validate_sources(data.get('sources'))
            if not sources:
                return jsonify({'error': '至少需要一个存在的来源路径'}), 400
            target = str(data.get('target') or _conf().get('default_target', '') or '').strip()
            if not target or not os.path.isabs(target):
                return jsonify({'error': '目标目录必须是绝对路径'}), 400
            for s in sources:
                t = os.path.normpath(target)
                if t == s or t.startswith(s.rstrip(os.sep) + os.sep):
                    return jsonify({'error': '目标目录不能位于备份来源内(防止套娃)'}), 400
            try:
                os.makedirs(target, exist_ok=True)
            except Exception as e:
                return jsonify({'error': '目标目录不可用: %s' % e}), 400
            compress = str(data.get('compress') or 'gz')
            if compress not in ('gz', 'none'):
                compress = 'gz'
            try:
                keep = max(1, int(data.get('keep', _conf().get('default_keep', 5))))
            except Exception:
                keep = 5
            try:
                interval = max(0, int(data.get('interval_hours', 0)))
            except Exception:
                interval = 0
            job = {
                'name': name, 'sources': sources, 'target': os.path.normpath(target),
                'compress': compress, 'keep': keep, 'interval_hours': interval,
                'excludes': [str(x).strip() for x in (data.get('excludes') or []) if str(x).strip()],
                'paused': False, 'created': int(time.time()), 'runs': [],
            }
            jobs[name] = job
            _save_jobs(jobs)
            return jsonify({'status': True, 'job': _job_out(job, [])})

        @self.route('/jobs/update', methods=['POST'])
        def jobs_update():
            data = request.get_json(silent=True) or {}
            old = str(data.get('old_name') or '').strip()
            name = str(data.get('name') or old).strip()
            jobs = _load_jobs()
            job = jobs.get(old) if old else jobs.get(name)
            if not job:
                return jsonify({'error': '任务不存在'}), 404
            if old and name != old:
                if not _valid_name(name):
                    return jsonify({'error': '任务名仅允许字母/数字/下划线/中文, 最长40'}), 400
                if name in jobs:
                    return jsonify({'error': '新名称已存在'}), 409
                job['name'] = name
                jobs.pop(old, None)
                jobs[name] = job
            if 'sources' in data:
                sources = _validate_sources(data.get('sources'))
                if sources:
                    job['sources'] = sources
            if 'target' in data:
                t = str(data.get('target') or '').strip()
                if t and os.path.isabs(t):
                    try:
                        os.makedirs(t, exist_ok=True)
                    except Exception:
                        pass
                    job['target'] = os.path.normpath(t)
            if 'compress' in data and data['compress'] in ('gz', 'none'):
                job['compress'] = data['compress']
            if 'keep' in data:
                try:
                    job['keep'] = max(1, int(data['keep']))
                except Exception:
                    pass
            if 'interval_hours' in data:
                try:
                    job['interval_hours'] = max(0, int(data['interval_hours']))
                except Exception:
                    pass
            if 'excludes' in data:
                job['excludes'] = [str(x).strip() for x in data['excludes'] if str(x).strip()]
            if 'paused' in data:
                job['paused'] = bool(data['paused'])
            _save_jobs(jobs)
            return jsonify({'status': True, 'job': _job_out(job, job.get('runs', []))})

        @self.route('/jobs/delete', methods=['POST'])
        def jobs_delete():
            data = request.get_json(silent=True) or {}
            name = str(data.get('name') or '').strip()
            jobs = _load_jobs()
            if name not in jobs:
                return jsonify({'error': '任务不存在'}), 404
            if name in _running:
                return jsonify({'error': '任务正在执行中, 无法删除'}), 400
            jobs.pop(name, None)
            _save_jobs(jobs)
            return jsonify({'ok': True, 'message': '已删除任务 %s' % name})

        @self.route('/jobs/run', methods=['POST'])
        def jobs_run():
            data = request.get_json(silent=True) or {}
            name = str(data.get('name') or '').strip()
            jobs = _load_jobs()
            job = jobs.get(name)
            if not job:
                return jsonify({'error': '任务不存在'}), 404
            if job.get('paused'):
                return jsonify({'error': '任务已暂停'}), 400
            t = threading.Thread(target=_run_backup, args=(job, True), daemon=True)
            t.start()
            return jsonify({'status': True, 'message': '已开始备份 %s, 可在任务队列查看进度' % name})

        @self.route('/runs', methods=['GET'])
        def runs_list():
            jobs = _load_jobs()
            rows = []
            for j in jobs.values():
                for r in j.get('runs', []):
                    rows.append({
                        'job': j['name'], 'file': r.get('file', ''),
                        'start': r.get('start'), 'end': r.get('end'),
                        'duration': r.get('duration'), 'size': r.get('size'),
                        'status': r.get('status'), 'error': r.get('error'),
                    })
            rows.sort(key=lambda x: -(x.get('start') or 0))
            return jsonify({'runs': rows[:200]})

        @self.route('/runs/delete', methods=['POST'])
        def runs_delete():
            data = request.get_json(silent=True) or {}
            filename = str(data.get('file') or '').strip()
            # 仅允许删除本插件记录的归档文件(防御路径穿越)
            jobs = _load_jobs()
            target = None
            for j in jobs.values():
                if os.path.abspath(os.path.join(j.get('target', '/'), os.path.basename(filename))) == \
                        os.path.abspath(filename) and filename.startswith(j.get('target', '')):
                    target = filename
                    break
            if not target or not os.path.isfile(target):
                return jsonify({'error': '归档不存在'}), 404
            try:
                os.remove(target)
                for j in jobs.values():
                    j['runs'] = [r for r in j.get('runs', []) if r.get('file') != target]
                _save_jobs(jobs)
                return jsonify({'ok': True, 'message': '已删除归档 ' + os.path.basename(target)})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.route('/status', methods=['GET'])
        def status():
            jobs = _load_jobs()
            total = 0
            latest = None
            for j in jobs.values():
                runs = j.get('runs', [])
                if runs:
                    r = runs[0]
                    total += r.get('size', 0)
                    if latest is None or (r.get('start') or 0) > (latest[0].get('start') or 0):
                        latest = (r, j['name'])
            return jsonify({
                'jobs': len(jobs),
                'running': sorted(_running),
                'total_backup_size': total,
                'latest': {'job': latest[1], 'run': latest[0]} if latest else None,
            })
