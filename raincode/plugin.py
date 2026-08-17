# -*- coding: utf-8 -*-
"""RainCough raincode — 精简版 opencode: AI 编程助手插件。

架构: 前端 Vue 组件 -> 本插件(薄壳) -> Node/TS 零依赖 agent(dist/index.js, SSE)。
功能: 流式对话 / 工具调用(shell+文件, 工作区沙箱) / 会话历史 / 任务清单 / 技能 /
      审批(auto/confirm/whitelist) / 在线模型列表(OpenCode Zen 免费模型)。
默认 LLM: OpenCode Zen https://opencode.ai/zen/v1 + deepseek-v4-flash-free(免费, 支持工具调用)。
"""
import os
import re
import json
import time
import signal
import shutil
import subprocess
import urllib.request

from flask import request, jsonify, Response
from plugins.base import Plugin

PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(PLUGIN_ROOT, 'agent')
AGENT_DIST = os.path.join(AGENT_DIR, 'dist', 'index.js')
DATA_DIR = os.path.join(PLUGIN_ROOT, 'data')
SESS_DIR = os.path.join(DATA_DIR, 'sessions')
SKILL_DIR = os.path.join(DATA_DIR, 'skills')
WORKSPACE = os.path.join(DATA_DIR, 'workspace')
CONF_PATH = os.path.join(DATA_DIR, 'config.json')
SECRET_PATH = os.path.join(DATA_DIR, 'agent_secret')
PID_PATH = os.path.join(DATA_DIR, 'agent.pid')
LOG_PATH = os.path.join(DATA_DIR, 'agent.log')
UNIT = 'rcvpn-raincode-agent.service'
SYSTEMD_DIR = '/etc/systemd/system'

for _d in (DATA_DIR, SESS_DIR, SKILL_DIR, WORKSPACE):
    try:
        os.makedirs(_d, exist_ok=True)
    except Exception:
        pass

DEFAULT_CONF = {
    'api_base': 'https://opencode.ai/zen/v1',
    'api_key': '',
    'model': 'deepseek-v4-flash-free',
    'workspace': WORKSPACE,
    'agent_port': 8765,
    'approve_mode': 'confirm',
    'whitelist': ['ls', 'pwd', 'cat ', 'git status', 'git log', 'git diff',
                  'npm run build', 'npm test', 'node --version', 'npm --version',
                  'python3 --version', 'python3 -c', 'python3 -m pip list'],
    'shell_timeout': 30,
    'output_cap': 20000,
    'max_tool_steps': 40,
    'sudo_pw': '',
}

# 离线兜底: opencode 免费模型(运行时拉取 /models 失败时使用)
FALLBACK_FREE = [
    {'id': 'deepseek-v4-flash-free', 'name': 'DeepSeek V4 Flash Free',
     'context': 200000, 'max_tokens': 128000, 'reasoning': True},
    {'id': 'mimo-v2.5-free', 'name': 'MiMo-V2.5 Free',
     'context': 262144, 'max_tokens': 65536, 'reasoning': True},
    {'id': 'north-mini-code-free', 'name': 'North Mini Code Free',
     'context': 0, 'max_tokens': 0, 'reasoning': True},
    {'id': 'nemotron-3-ultra-free', 'name': 'Nemotron 3 Ultra Free',
     'context': 0, 'max_tokens': 0, 'reasoning': True},
    {'id': 'nemotron-3.5-lightning-free', 'name': 'Nemotron 3.5 Lightning Free',
     'context': 0, 'max_tokens': 0, 'reasoning': True},
    {'id': 'big-pickle', 'name': 'Big Pickle',
     'context': 0, 'max_tokens': 0, 'reasoning': True},
    {'id': 'hy3-free', 'name': 'Hy3 Free',
     'context': 0, 'max_tokens': 0, 'reasoning': True},
    {'id': 'laguna-s-2.1-free', 'name': 'Laguna S 2.1 Free',
     'context': 0, 'max_tokens': 0, 'reasoning': True},
]


# ---------------------------------------------------------------------------
# 配置 / 工具
# ---------------------------------------------------------------------------
def _load_conf():
    cfg = dict(DEFAULT_CONF)
    cfg['whitelist'] = list(DEFAULT_CONF['whitelist'])
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        for k in ('api_base', 'api_key', 'model', 'workspace', 'agent_port',
                  'approve_mode', 'shell_timeout', 'output_cap', 'max_tool_steps', 'sudo_pw'):
            if k in saved and saved[k] not in (None, ''):
                cfg[k] = saved[k]
        if isinstance(saved.get('whitelist'), list):
            cfg['whitelist'] = [str(x) for x in saved['whitelist']]
    except Exception:
        pass
    if not cfg.get('workspace'):
        cfg['workspace'] = WORKSPACE
    try:
        os.makedirs(cfg['workspace'], exist_ok=True)
    except Exception:
        pass
    return cfg


def _save_conf(cfg):
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CONF_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _config_out(cfg):
    out = dict(cfg)
    out['api_key'] = '****' if cfg.get('api_key') else ''
    out['has_key'] = bool(cfg.get('api_key'))
    out['sudo_pw'] = '****' if cfg.get('sudo_pw') else ''
    return out


def _secret():
    if not os.path.isfile(SECRET_PATH):
        try:
            with open(SECRET_PATH, 'w') as f:
                f.write(os.urandom(24).hex())
            os.chmod(SECRET_PATH, 0o600)
        except Exception:
            pass
    try:
        with open(SECRET_PATH) as f:
            return f.read().strip()
    except Exception:
        return ''


def _node_bin():
    n = shutil.which('node')
    if n:
        return n
    for cand in ('/usr/local/bin/node', '/usr/bin/node', '/opt/node/bin/node'):
        if os.path.isfile(cand):
            return cand
    return None


def _node_ok():
    ver = _node_version()
    if not ver:
        return False
    try:
        return int(ver.lstrip('v').split('.')[0]) >= 18
    except Exception:
        return False


def _node_version():
    n = _node_bin()
    if not n:
        return ''
    try:
        r = subprocess.run([n, '--version'], capture_output=True, text=True, timeout=10)
        return (r.stdout or '').strip()
    except Exception:
        return ''


def _agent_url(path):
    return 'http://127.0.0.1:%d%s' % (_load_conf().get('agent_port', 8765), path)


def _agent_health():
    try:
        with urllib.request.urlopen(_agent_url('/health'), timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def _wait_health(seconds):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if _agent_health():
            return True
        time.sleep(0.4)
    return False


def _sudo(args, timeout=60):
    pw = _load_conf().get('sudo_pw', '')
    try:
        if pw:
            return subprocess.run(['sudo', '-S'] + list(args), capture_output=True,
                                  text=True, timeout=timeout, input=pw + '\n')
        return subprocess.run(['sudo', '-n'] + list(args), capture_output=True,
                              text=True, timeout=timeout)
    except Exception:
        return None


def _has_systemd():
    return shutil.which('systemctl') is not None and os.path.isdir(SYSTEMD_DIR)


def _unit_path():
    return os.path.join(SYSTEMD_DIR, UNIT)


def _ensure_unit():
    node = _node_bin() or '/usr/local/bin/node'
    port = int(_load_conf().get('agent_port', 8765))
    body = ('[Unit]\nDescription=RainCough raincode agent\n'
            'After=network-online.target\nWants=network-online.target\n\n'
            '[Service]\nType=simple\nRestart=always\nRestartSec=3\n'
            'ExecStart=%s %s --port %d --data %s --secret %s\n'
            'WorkingDirectory=%s\nEnvironment=NODE_ENV=production\n'
            '\n[Install]\nWantedBy=multi-user.target\n'
            % (node, AGENT_DIST, port, DATA_DIR, _secret(), AGENT_DIR))
    r = _sudo(['bash', '-c',
               "cat > '%s' <<'EOF'\n%s\nEOF\nchmod 644 '%s'\n"
               % (_unit_path(), body, _unit_path())], timeout=30)
    _sudo(['systemctl', 'daemon-reload'], timeout=30)
    return r


def _start_agent():
    if _agent_health():
        return {'ok': True, 'running': True}
    if not _node_bin():
        return {'ok': False, 'error': '未检测到 Node.js(需 >=18), 请先在服务器安装 Node.js'}
    if not _node_ok():
        return {'ok': False, 'error': 'Node.js 版本过低(%s), 需 >=18' % _node_version()}
    if not os.path.isfile(AGENT_DIST):
        return {'ok': False, 'error': '缺少 agent/dist/index.js(插件包不完整)'}
    port = int(_load_conf().get('agent_port', 8765))
    if _has_systemd():
        _ensure_unit()
        r = _sudo(['systemctl', 'enable', '--now', UNIT], timeout=60)
        if r and r.returncode == 0:
            if _wait_health(6):
                return {'ok': True, 'running': True, 'svc': 'systemd'}
    args = [_node_bin(), AGENT_DIST, '--port', str(port), '--data', DATA_DIR,
            '--secret', _secret()]
    try:
        with open(LOG_PATH, 'ab') as logf:
            p = subprocess.Popen(args, cwd=AGENT_DIR, stdout=logf, stderr=logf,
                                 start_new_session=True)
        with open(PID_PATH, 'w') as f:
            f.write(str(p.pid))
    except Exception as e:
        return {'ok': False, 'error': '启动失败: %s' % e}
    if _wait_health(6):
        return {'ok': True, 'running': True, 'svc': 'spawn'}
    return {'ok': False, 'error': 'agent 启动失败, 请查看日志 data/agent.log'}


def _stop_agent():
    if _has_systemd() and os.path.isfile(_unit_path()):
        _sudo(['systemctl', 'disable', '--now', UNIT], timeout=60)
    try:
        with open(PID_PATH) as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
    except Exception:
        pass
    return {'ok': True}


def _load_json(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d if isinstance(d, type(default)) else default
    except Exception:
        return default


def _save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 会话 / 技能 / 模型
# ---------------------------------------------------------------------------
def _session_list():
    out = []
    try:
        for fn in os.listdir(SESS_DIR):
            if not fn.endswith('.json'):
                continue
            s = _load_json(os.path.join(SESS_DIR, fn), {})
            if not s:
                continue
            out.append({
                'id': s.get('id', fn[:-5]),
                'title': s.get('title', '未命名'),
                'created': s.get('created', 0),
                'updated': s.get('updated', 0),
                'messages': len(s.get('messages', [])),
                'pending': bool(s.get('pending')),
            })
    except Exception:
        pass
    out.sort(key=lambda x: x.get('updated', 0), reverse=True)
    return out


def _session_path(sid):
    return os.path.join(SESS_DIR, sid + '.json')


def _skill_payload(names):
    names = names or []
    payload = []
    try:
        for fn in os.listdir(SKILL_DIR):
            if not fn.endswith('.json'):
                continue
            s = _load_json(os.path.join(SKILL_DIR, fn), {})
            if not s or s.get('name') not in names:
                continue
            if not s.get('instructions'):
                continue
            payload.append({
                'name': s.get('name'),
                'title': s.get('title') or s.get('name'),
                'description': s.get('description', ''),
                'instructions': s.get('instructions'),
                'enabled': True,
            })
    except Exception:
        pass
    return payload


def _skill_list():
    out = []
    try:
        for fn in sorted(os.listdir(SKILL_DIR)):
            if not fn.endswith('.json'):
                continue
            s = _load_json(os.path.join(SKILL_DIR, fn), {})
            if not s:
                continue
            out.append({
                'name': s.get('name', fn[:-5]),
                'title': s.get('title') or s.get('name') or fn[:-5],
                'description': s.get('description', ''),
                'enabled': s.get('enabled', True),
                'updated': s.get('updated', 0),
            })
    except Exception:
        pass
    out.sort(key=lambda x: x.get('updated', 0), reverse=True)
    return out


def _agent_config_for(data):
    cfg = _load_conf()
    return {
        'api_base': cfg.get('api_base', DEFAULT_CONF['api_base']),
        'api_key': cfg.get('api_key', ''),
        'model': str(data.get('model') or cfg.get('model') or DEFAULT_CONF['model']),
        'workspace': cfg.get('workspace') or WORKSPACE,
        'approve_mode': str(data.get('mode') or cfg.get('approve_mode') or 'confirm'),
        'whitelist': cfg.get('whitelist', []),
        'shell_timeout': int(cfg.get('shell_timeout', 30)),
        'output_cap': int(cfg.get('output_cap', 20000)),
        'max_tool_steps': int(cfg.get('max_tool_steps', 40)),
    }


def _proxy_sse(method, path, body):
    """把请求转发给本地 agent 服务并透传 SSE 流回浏览器。"""
    url = _agent_url(path)
    payload = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=payload, method=method,
                                 headers={'Content-Type': 'application/json',
                                          'X-Rc-Secret': _secret()})

    def gen():
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                while True:
                    chunk = r.read(4096)
                    if not chunk:
                        break
                    yield chunk
        except Exception as e:
            yield ('data: %s\n\n' % json.dumps({'type': 'error',
                                                'error': 'agent 通信失败: %s' % e},
                                               ensure_ascii=False)).encode('utf-8')

    return Response(gen(), content_type='text/event-stream; charset=utf-8',
                    direct_passthrough=True,
                    headers={'Cache-Control': 'no-cache',
                             'X-Accel-Buffering': 'no'})


# ---------------------------------------------------------------------------
# 插件
# ---------------------------------------------------------------------------
class RcPlugin(Plugin):
    name = 'raincode'
    label = 'AI 编程助手'
    icon = ''
    description = '精简版 opencode: 流式对话 + 工具调用(shell/文件) + 会话历史 + 任务清单 + 技能, 默认接入 opencode 免费模型'

    def get_setting_schema(self):
        cfg = _load_conf()
        return [
            {'key': 'api_base', 'label': 'API Base(OpenAI 兼容)', 'type': 'text',
             'value': cfg.get('api_base', DEFAULT_CONF['api_base']),
             'help': '默认 OpenCode Zen: https://opencode.ai/zen/v1'},
            {'key': 'api_key', 'label': 'API Key', 'type': 'text', 'value': '',
             'help': 'opencode 免费模型需首充激活后可用; 留空则保留已保存的 Key'},
            {'key': 'model', 'label': '默认模型', 'type': 'text',
             'value': cfg.get('model', DEFAULT_CONF['model'])},
            {'key': 'workspace', 'label': '工作区目录(agent 可读写范围)', 'type': 'text',
             'value': cfg.get('workspace', WORKSPACE)},
            {'key': 'agent_port', 'label': 'Agent 服务端口', 'type': 'number',
             'value': cfg.get('agent_port', 8765)},
            {'key': 'approve_mode', 'label': '默认审批方式', 'type': 'select',
             'value': cfg.get('approve_mode', 'confirm'),
             'options': [{'label': '自动执行', 'value': 'auto'},
                         {'label': '手动确认', 'value': 'confirm'},
                         {'label': '白名单', 'value': 'whitelist'}]},
        ]

    def get_settings(self):
        cfg = _load_conf()
        return {
            'api_base': cfg.get('api_base', DEFAULT_CONF['api_base']),
            'api_key': '',
            'model': cfg.get('model', DEFAULT_CONF['model']),
            'workspace': cfg.get('workspace', WORKSPACE),
            'agent_port': cfg.get('agent_port', 8765),
            'approve_mode': cfg.get('approve_mode', 'confirm'),
        }

    def save_settings(self, data):
        cfg = _load_conf()
        for k, v in data.items():
            if k == 'api_key':
                if v:
                    cfg['api_key'] = str(v).strip()
                continue
            if k == 'agent_port':
                try:
                    cfg['agent_port'] = int(v)
                except Exception:
                    pass
                continue
            if k in cfg and v not in (None, ''):
                cfg[k] = str(v).strip()
        _save_conf(cfg)
        return True, '已保存'

    def _register_routes(self):
        @self.route('/env', methods=['GET'])
        def env():
            cfg = _load_conf()
            node = _node_bin()
            return jsonify({
                'node': {'installed': bool(node), 'bin': node,
                         'version': _node_version(), 'ok': _node_ok()},
                'agent': {'running': _agent_health(),
                          'port': cfg.get('agent_port', 8765),
                          'svc': 'systemd' if os.path.isfile(_unit_path()) else 'spawn'},
                'workspace': cfg.get('workspace', WORKSPACE),
                'config': _config_out(cfg),
            })

        @self.route('/config', methods=['GET', 'POST'])
        def config_routes():
            if request.method == 'GET':
                return jsonify({'status': True, 'config': _config_out(_load_conf())})
            data = request.get_json(silent=True) or {}
            cfg = _load_conf()
            for k in ('api_base', 'model', 'workspace', 'approve_mode',
                      'shell_timeout', 'output_cap', 'max_tool_steps', 'sudo_pw'):
                if data.get(k) is None:
                    continue
                if k in ('shell_timeout', 'output_cap', 'max_tool_steps'):
                    try:
                        cfg[k] = int(data[k])
                    except Exception:
                        pass
                else:
                    cfg[k] = str(data[k]).strip()
            if data.get('agent_port') is not None:
                try:
                    cfg['agent_port'] = int(data['agent_port'])
                except Exception:
                    pass
            if data.get('api_key'):
                cfg['api_key'] = str(data['api_key']).strip()
            if isinstance(data.get('whitelist'), list):
                cfg['whitelist'] = [str(x).strip() for x in data['whitelist'] if str(x).strip()]
            _save_conf(cfg)
            return jsonify({'status': True, 'config': _config_out(cfg)})

        @self.route('/models', methods=['GET'])
        def models():
            cfg = _load_conf()
            key = cfg.get('api_key', '')
            live = None
            if key:
                try:
                    base = cfg.get('api_base', DEFAULT_CONF['api_base']).rstrip('/')
                    req = urllib.request.Request(base + '/models',
                                                 headers={'Authorization': 'Bearer ' + key})
                    with urllib.request.urlopen(req, timeout=12) as r:
                        data = json.loads(r.read().decode('utf-8'))
                    items = data.get('data') if isinstance(data, dict) else data
                    arr = []
                    for m in (items or []):
                        if not isinstance(m, dict):
                            continue
                        mid = m.get('id') or ''
                        cost = m.get('cost') or {}
                        try:
                            inp = cost.get('input', 0)
                            out = cost.get('output', 0)
                        except Exception:
                            inp = out = None
                        if not mid:
                            continue
                        if inp == 0 and out == 0:
                            arr.append({
                                'id': mid,
                                'name': m.get('name') or mid,
                                'context': m.get('context_window') or m.get('contextWindow') or 0,
                                'max_tokens': m.get('max_tokens') or m.get('maxTokens') or 0,
                                'reasoning': bool(m.get('reasoning')),
                            })
                    if arr:
                        live = arr
                except Exception:
                    pass
            if live:
                return jsonify({'status': True, 'models': live, 'source': 'live',
                                'suggested': 'deepseek-v4-flash-free'})
            return jsonify({'status': True, 'models': FALLBACK_FREE, 'source': 'fallback',
                            'suggested': 'deepseek-v4-flash-free',
                            'note': '在线模型列表获取失败(未配置 Key 或网络不可达), 显示内置默认列表'})

        @self.route('/start', methods=['POST'])
        def start():
            return jsonify(_start_agent())

        @self.route('/stop', methods=['POST'])
        def stop():
            return jsonify(_stop_agent())

        @self.route('/sessions', methods=['GET'])
        def sessions():
            return jsonify({'status': True, 'sessions': _session_list()})

        @self.route('/sessions/', methods=['GET', 'DELETE'])
        def sessions_crud():
            parts = request.path.split('/api/plugins/raincode/', 1)
            sub = parts[1] if len(parts) == 2 else ''
            sid = sub.split('/')[1] if len(sub.split('/')) > 1 and sub.split('/')[1] else ''
            if not sid:
                return jsonify({'error': '缺少 session id'}), 400
            p = _session_path(sid)
            if request.method == 'DELETE':
                try:
                    os.remove(p)
                except Exception:
                    pass
                try:
                    req = urllib.request.Request(_agent_url('/cancel'), data=b'{}',
                                                 method='POST',
                                                 headers={'Content-Type': 'application/json',
                                                          'X-Rc-Secret': _secret()})
                    urllib.request.urlopen(req, timeout=3)
                except Exception:
                    pass
                return jsonify({'ok': True})
            if not os.path.isfile(p):
                return jsonify({'error': '会话不存在'}), 404
            s = _load_json(p, {})
            return jsonify({'status': True, 'session': s})

        @self.route('/skills', methods=['GET', 'POST'])
        def skills():
            if request.method == 'GET':
                return jsonify({'status': True, 'skills': _skill_list()})
            data = request.get_json(silent=True) or {}
            name = str(data.get('name') or '').strip()
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '技能名需为字母数字_-'}), 400
            title = str(data.get('title') or name).strip()
            instructions = str(data.get('instructions') or '').strip()
            if not instructions:
                return jsonify({'error': '技能内容(instructions)不能为空'}), 400
            s = {
                'name': name, 'title': title,
                'description': str(data.get('description') or '').strip(),
                'instructions': instructions,
                'enabled': bool(data.get('enabled', True)),
                'updated': int(time.time()),
            }
            _save_json(os.path.join(SKILL_DIR, name + '.json'), s)
            return jsonify({'ok': True, 'skill': {
                'name': name, 'title': title,
                'description': s['description'], 'enabled': s['enabled'],
                'updated': s['updated']}})

        @self.route('/skills/toggle', methods=['POST'])
        def skill_toggle():
            data = request.get_json(silent=True) or {}
            name = str(data.get('name') or '').strip()
            s = _load_json(os.path.join(SKILL_DIR, name + '.json'), {})
            if not s:
                return jsonify({'error': '技能不存在'}), 404
            s['enabled'] = bool(data.get('enabled', not s.get('enabled', True)))
            s['updated'] = int(time.time())
            _save_json(os.path.join(SKILL_DIR, name + '.json'), s)
            return jsonify({'ok': True, 'enabled': s['enabled']})

        @self.route('/skills/', methods=['DELETE'])
        def skill_del():
            parts = request.path.split('/api/plugins/raincode/', 1)
            sub = parts[1] if len(parts) == 2 else ''
            name = sub.split('/')[1] if len(sub.split('/')) > 1 and sub.split('/')[1] else ''
            if not name:
                return jsonify({'error': '缺少技能名'}), 400
            try:
                os.remove(os.path.join(SKILL_DIR, name + '.json'))
            except Exception:
                return jsonify({'error': '技能不存在'}), 404
            return jsonify({'ok': True})

        @self.route('/chat', methods=['POST'])
        def chat():
            data = request.get_json(silent=True) or {}
            message = str(data.get('message') or '').strip()
            if not message:
                return jsonify({'error': '消息为空'}), 400
            cfg = _load_conf()
            if not cfg.get('api_key'):
                return jsonify({'error': '未配置 API Key, 请到设置页填写'}), 400
            if not _agent_health():
                r = _start_agent()
                if not r.get('ok'):
                    return jsonify({'error': r.get('error', 'agent 未运行')}), 500
            body = {
                'session_id': str(data.get('session_id') or ''),
                'message': message,
                'config': _agent_config_for(data),
                'skills': _skill_payload(data.get('active_skills')),
            }
            if data.get('model'):
                body['model'] = str(data['model'])
            return _proxy_sse('POST', '/chat', body)

        @self.route('/approve', methods=['POST'])
        def approve():
            data = request.get_json(silent=True) or {}
            session_id = str(data.get('session_id') or '')
            if not session_id:
                return jsonify({'error': '缺少 session_id'}), 400
            if not _agent_health():
                return jsonify({'error': 'agent 未运行'}), 500
            approved = bool(data.get('approved', True))
            # 白名单模式: 批准时可选加入白名单
            if approved and data.get('add_whitelist'):
                cfg = _load_conf()
                cmd = str(data.get('command') or '').strip()
                if cmd:
                    wl = cfg.get('whitelist', [])
                    if cmd not in wl:
                        wl.append(cmd)
                        cfg['whitelist'] = wl
                        _save_conf(cfg)
            body = {
                'session_id': session_id,
                'config': _agent_config_for(data),
                'skills': _skill_payload(data.get('active_skills')),
                'approved': approved,
                'reason': str(data.get('reason') or ''),
            }
            return _proxy_sse('POST', '/approve', body)

        @self.route('/cancel', methods=['POST'])
        def cancel():
            data = request.get_json(silent=True) or {}
            session_id = str(data.get('session_id') or '')
            if not _agent_health():
                return jsonify({'ok': True})
            try:
                req = urllib.request.Request(_agent_url('/cancel'),
                                             data=json.dumps({'session_id': session_id}).encode(),
                                             method='POST',
                                             headers={'Content-Type': 'application/json',
                                                      'X-Rc-Secret': _secret()})
                urllib.request.urlopen(req, timeout=3)
            except Exception:
                pass
            return jsonify({'ok': True})
