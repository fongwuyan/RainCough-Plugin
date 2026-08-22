# -*- coding: utf-8 -*-
"""RainCough raincode — 精简版 opencode: 内置于面板的 AI 编程 Agent 插件。

架构: 前端 Vue 组件 -> 本插件(薄壳) -> Node/TS 零依赖 agent(dist/index.js, SSE)。
功能: 会话式编程(可切换工作目录/多会话) / 工具调用(shell+文件, 工作区沙箱) /
      会话历史 / 任务清单 / 技能注入 / 单配置(API Base + Key + 模型) /
      长期记忆(memory.md, 跨会话共享) / 子智能体(delegate) / 审批(auto/confirm/whitelist)。
"""
import os
import re
import json
import time
import signal
import shutil
import subprocess
import threading
import urllib.request

from flask import request, jsonify, Response
from plugins.base import Plugin

PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(PLUGIN_ROOT, 'agent')
AGENT_DIST = os.path.join(AGENT_DIR, 'dist', 'index.js')
DATA_DIR = os.path.join(PLUGIN_ROOT, 'data')
SESS_DIR = os.path.join(DATA_DIR, 'sessions')
SKILL_DIR = os.path.join(DATA_DIR, 'skills')
MEMORY_PATH = os.path.join(DATA_DIR, 'memory.md')
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
    'api_base': '',
    'api_key': '',
    'model': '',
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
    'providers': [],
    'default_provider': '',
    'principles': [],
}


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
                  'approve_mode', 'shell_timeout', 'output_cap', 'max_tool_steps',
                  'sudo_pw'):
            if k in saved and saved[k] not in (None, ''):
                cfg[k] = saved[k]
        if isinstance(saved.get('whitelist'), list):
            cfg['whitelist'] = [str(x) for x in saved['whitelist']]
        if isinstance(saved.get('providers'), list):
            cfg['providers'] = saved['providers']
        if saved.get('default_provider'):
            cfg['default_provider'] = str(saved['default_provider'])
        if isinstance(saved.get('principles'), list):
            cfg['principles'] = [str(x) for x in saved['principles'] if str(x).strip()]
    except Exception:
        pass
    # 迁移: 若仅有旧版单配置且无 providers, 则生成一个默认服务商
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        if not cfg.get('providers') and cfg.get('api_base') and cfg.get('api_key'):
            cfg['providers'] = [{
                'name': 'default',
                'api_base': str(cfg.get('api_base') or '').strip().rstrip('/'),
                'api_key': str(cfg.get('api_key') or ''),
                'default_model': str(cfg.get('model') or ''),
                'enabled': True,
            }]
            if not cfg.get('default_provider'):
                cfg['default_provider'] = 'default'
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
    out['principles'] = [str(x) for x in (cfg.get('principles') or []) if str(x).strip()]
    out['default_provider'] = str(cfg.get('default_provider') or '')
    out['providers'] = _providers_out(cfg.get('providers'))
    return out


def _providers_out(providers):
    """脱敏返回服务商列表: key 用 has_key + '****' 回显。"""
    out = []
    for p in providers or []:
        if not isinstance(p, dict):
            continue
        out.append({
            'name': str(p.get('name') or ''),
            'api_base': str(p.get('api_base') or ''),
            'api_key': '****' if p.get('api_key') else '',
            'has_key': bool(p.get('api_key')),
            'default_model': str(p.get('default_model') or ''),
            'enabled': bool(p.get('enabled', True)),
        })
    return out


def _resolve_provider(cfg, name):
    """按名称取服务商(仅启用的)。"""
    name = str(name or '').strip()
    if not name:
        return None
    for p in cfg.get('providers') or []:
        if isinstance(p, dict) and str(p.get('name') or '') == name \
                and p.get('enabled', True):
            return p
    return None


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
def _session_list(workspace=None):
    out = []
    try:
        for fn in os.listdir(SESS_DIR):
            if not fn.endswith('.json'):
                continue
            s = _load_json(os.path.join(SESS_DIR, fn), {})
            if not s:
                continue
            sw = s.get('workspace', '')
            if workspace is not None and sw != workspace:
                continue
            out.append({
                'id': s.get('id', fn[:-5]),
                'title': s.get('title', '未命名'),
                'created': s.get('created', 0),
                'updated': s.get('updated', 0),
                'messages': len(s.get('messages', [])),
                'pending': bool(s.get('pending')),
                'workspace': sw,
            })
    except Exception:
        pass
    out.sort(key=lambda x: x.get('updated', 0), reverse=True)
    return out


def _workspace_list():
    cfg = _load_conf()
    ws = [cfg.get('workspace') or WORKSPACE]
    for w in cfg.get('workspaces', []) or []:
        if w and w not in ws:
            ws.append(w)
    try:
        for fn in os.listdir(SESS_DIR):
            if fn.endswith('.json'):
                s = _load_json(os.path.join(SESS_DIR, fn), {})
                sw = s.get('workspace', '')
                if sw and sw not in ws:
                    ws.append(sw)
    except Exception:
        pass
    return ws


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
            if not s.get('execution'):
                continue
            payload.append({
                'name': s.get('name'),
                'title': s.get('title') or s.get('name'),
                'description': s.get('description', ''),
                'params': s.get('params') or [],
                'execution': s.get('execution'),
                'enabled': True,
            })
    except Exception:
        pass
    return payload


def _skill_struct_ok(skill):
    """校验新结构 skill: 有 name + execution(kind=shell/tool/http) 及必要字段。"""
    if not isinstance(skill, dict) or not isinstance(skill.get('execution'), dict):
        return False
    kind = skill['execution'].get('kind')
    if kind == 'shell':
        return bool(str(skill['execution'].get('command') or '').strip())
    if kind == 'tool':
        return bool(str(skill['execution'].get('tool') or '').strip())
    if kind == 'http':
        return bool(str(skill['execution'].get('url') or '').strip())
    return False


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
                'params': s.get('params') or [],
                'execution': s.get('execution'),
                'enabled': s.get('enabled', True),
                'updated': s.get('updated', 0),
            })
    except Exception:
        pass
    out.sort(key=lambda x: x.get('updated', 0), reverse=True)
    return out


def _agent_config_for(data):
    cfg = _load_conf()
    prov = _resolve_provider(cfg, data.get('provider'))
    if prov:
        api_base = str(prov.get('api_base') or '').strip().rstrip('/')
        api_key = str(prov.get('api_key') or '')
        model = str(data.get('model') or prov.get('default_model') or '').strip()
        provider_name = str(prov.get('name') or '')
    else:
        api_base = (cfg.get('api_base') or '').strip().rstrip('/')
        api_key = cfg.get('api_key') or ''
        model = str(data.get('model') or cfg.get('model') or '').strip()
        provider_name = str(data.get('provider') or '').strip()
    return {
        'api_base': api_base,
        'api_key': api_key,
        'model': model,
        'provider': provider_name,
        'principles': [str(x) for x in (cfg.get('principles') or []) if str(x).strip()],
        'workspace': cfg.get('workspace') or WORKSPACE,
        'approve_mode': str(data.get('mode') or cfg.get('approve_mode') or 'confirm'),
        'agent_mode': str(data.get('agent_mode') or 'build'),
        'whitelist': cfg.get('whitelist', []),
        'shell_timeout': int(cfg.get('shell_timeout', 30)),
        'output_cap': int(cfg.get('output_cap', 20000)),
        'max_tool_steps': int(cfg.get('max_tool_steps', 40)),
        'memory_path': MEMORY_PATH,
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
    label = 'RainCode'
    icon = ''
    description = '内置于面板的 AI 编程 Agent(精简版 opencode): 会话式编程, OpenAI 兼容接口一键接入, 工具调用、长期记忆、子智能体、技能、任务清单与审批控制'

    def __init__(self):
        super().__init__()
        # 面板启动后自动拉起 agent(幂等: 已健康则跳过), 避免面板重启连带杀死 agent 后无人自愈
        try:
            threading.Thread(target=self._auto_start_agent, daemon=True).start()
        except Exception as e:
            print('[raincode] auto-start thread failed: %s' % e)

    def _auto_start_agent(self):
        try:
            time.sleep(2)
            r = _start_agent()
            if not (r or {}).get('ok'):
                print('[raincode] agent auto-start failed: %s' % (r or {}).get('error'))
            elif r.get('svc'):
                print('[raincode] agent auto-start ok (svc=%s)' % r.get('svc'))
        except Exception as e:
            print('[raincode] agent auto-start exception: %s' % e)

    def get_setting_schema(self):
        cfg = _load_conf()
        return [
            {'key': 'api_base', 'label': 'API Base(OpenAI 兼容)', 'type': 'text',
             'value': cfg.get('api_base', ''),
             'help': '如 https://api.deepseek.com/v1 或 https://api.openai.com/v1'},
            {'key': 'api_key', 'label': 'API Key', 'type': 'text', 'value': '',
             'help': '已配置时留空表示保留'},
            {'key': 'model', 'label': '模型', 'type': 'text',
             'value': cfg.get('model', ''),
             'help': '如 deepseek-chat / gpt-4o'},
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
            'api_base': cfg.get('api_base', ''),
            'api_key': '',
            'model': cfg.get('model', ''),
            'workspace': cfg.get('workspace', WORKSPACE),
            'agent_port': cfg.get('agent_port', 8765),
            'approve_mode': cfg.get('approve_mode', 'confirm'),
            'providers': _providers_out(cfg.get('providers')),
            'default_provider': str(cfg.get('default_provider') or ''),
            'principles': [str(x) for x in (cfg.get('principles') or []) if str(x).strip()],
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
                'workspaces': _workspace_list(),
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
            if isinstance(data.get('workspaces'), list):
                cfg['workspaces'] = [str(x).strip() for x in data['workspaces'] if str(x).strip()]
            cur = cfg.get('workspace') or WORKSPACE
            wslist = cfg.get('workspaces') or []
            if cur and cur not in wslist:
                wslist.append(cur)
                cfg['workspaces'] = wslist
            if data.get('api_key'):
                cfg['api_key'] = str(data['api_key']).strip()
            if data.get('default_provider') is not None:
                cfg['default_provider'] = str(data['default_provider']).strip()
            if isinstance(data.get('principles'), list):
                cfg['principles'] = [str(x).strip() for x in data['principles'] if str(x).strip()]
            if isinstance(data.get('providers'), list):
                # 整体替换服务商, '****' 表示保留旧 key
                old = {str(p.get('name') or ''): p for p in cfg.get('providers') or [] if isinstance(p, dict)}
                np_ = []
                for item in data['providers']:
                    if not isinstance(item, dict):
                        continue
                    r = dict(item)
                    if r.get('api_key') == '****':
                        prev = old.get(str(r.get('name') or '')) or {}
                        r['api_key'] = prev.get('api_key') or ''
                    np_.append(r)
                cfg['providers'] = np_
            if isinstance(data.get('whitelist'), list):
                cfg['whitelist'] = [str(x).strip() for x in data['whitelist'] if str(x).strip()]
            _save_conf(cfg)
            return jsonify({'status': True, 'config': _config_out(cfg)})

        @self.route('/providers', methods=['GET', 'POST'])
        def providers():
            if request.method == 'GET':
                return jsonify({'status': True, 'providers': _providers_out(_load_conf().get('providers'))})
            data = request.get_json(silent=True) or {}
            action = str(data.get('action') or 'save')
            cfg = _load_conf()
            providers = list(cfg.get('providers') or [])
            if action == 'save':
                # 保存全部服务商(整体替换)。key 为 '****' 时视为未改动保留旧值。
                new_providers = []
                old = {str(p.get('name') or ''): p for p in providers if isinstance(p, dict)}
                for item in data.get('providers') or []:
                    if not isinstance(item, dict):
                        continue
                    raw = dict(item)
                    name = str(raw.get('name') or '').strip()
                    if not name or not re.match(r'^[A-Za-z0-9_\- ]{1,40}$', name):
                        return jsonify({'error': '服务商名称非法'}), 400
                    if raw.get('api_key') == '****':
                        prev = old.get(name) or {}
                        raw['api_key'] = prev.get('api_key') or ''
                    new_providers.append(raw)
                cfg['providers'] = new_providers
                if data.get('default_provider') is not None:
                    cfg['default_provider'] = str(data['default_provider']).strip()
            elif action == 'delete':
                name = str(data.get('name') or '').strip()
                providers = [p for p in providers
                             if not (isinstance(p, dict) and str(p.get('name') or '') == name)]
                cfg['providers'] = providers
                if cfg.get('default_provider') == name:
                    cfg['default_provider'] = ''
            else:
                return jsonify({'error': '未知 action'}), 400
            _save_conf(cfg)
            return jsonify({'status': True, 'providers': _providers_out(cfg.get('providers')),
                            'default_provider': cfg.get('default_provider') or ''})

        @self.route('/models', methods=['GET'])
        def models():
            cfg = _load_conf()
            prov = _resolve_provider(cfg, request.args.get('provider'))
            agg = {'base': '', 'model': '', 'models': []}
            if prov:
                agg['base'] = str(prov.get('api_base') or '').strip().rstrip('/')
                agg['model'] = str(prov.get('default_model') or '')
            else:
                agg['base'] = (cfg.get('api_base') or '').strip().rstrip('/')
                agg['model'] = str(cfg.get('model') or '')
            base = agg['base']
            models_list = []
            if base:
                base_l = base.lower()
                if 'deepseek' in base_l:
                    models_list = ['deepseek-v4-flash', 'deepseek-chat', 'deepseek-reasoner']
                elif 'openai' in base_l or 'api.openai' in base_l:
                    models_list = ['gpt-4o', 'gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo']
                elif 'moonshot' in base_l or 'kimi' in base_l:
                    models_list = ['kimi-k2', 'moonshot-v1-8k']
                elif 'qwen' in base_l or 'dashscope' in base_l:
                    models_list = ['qwen-max', 'qwen-plus', 'qwen-turbo']
                elif 'zhipu' in base_l or 'bigmodel' in base_l:
                    models_list = ['glm-4', 'glm-4-plus', 'glm-4-flash']
                elif 'ollama' in base_l or 'localhost' in base_l or '127.0.0.1' in base_l:
                    models_list = ['llama3', 'qwen2.5', 'mistral']
                else:
                    models_list = ['']
            if agg['model'] not in models_list:
                models_list.insert(0, agg['model'])
            agg['models'] = [m for m in models_list if m]
            return jsonify({'status': True, 'models': agg['models'],
                            'current': agg['model'], 'base': agg['base']})

        @self.route('/principles', methods=['GET', 'POST'])
        def principles():
            cfg = _load_conf()
            if request.method == 'GET':
                return jsonify({'status': True, 'principles': cfg.get('principles') or []})
            data = request.get_json(silent=True) or {}
            if isinstance(data.get('principles'), list):
                cfg['principles'] = [str(x).strip() for x in data['principles'] if str(x).strip()]
                _save_conf(cfg)
            return jsonify({'status': True, 'principles': cfg.get('principles') or []})

        @self.route('/workspace/browse', methods=['GET'])
        def workspace_browse():
            """列出某目录下的子目录, 供前端选择工作目录。参数: path=绝对路径。"""
            p = request.args.get('path', '').strip() or WORKSPACE
            base = os.path.abspath(os.path.expanduser(p))
            out = {'path': base, 'name': os.path.basename(base) or base,
                   'parent': None, 'dirs': [], 'exists': os.path.isdir(base)}
            parent = os.path.dirname(base) or '/'
            if base != parent and os.path.isdir(parent):
                out['parent'] = parent
            if out['exists']:
                try:
                    for e in os.listdir(base):
                        if e.startswith('.'):
                            continue
                        fp = os.path.join(base, e)
                        if os.path.isdir(fp):
                            out['dirs'].append(e)
                except Exception:
                    pass
            return jsonify(out)

        @self.route('/start', methods=['POST'])
        def start():
            return jsonify(_start_agent())

        @self.route('/stop', methods=['POST'])
        def stop():
            return jsonify(_stop_agent())

        @self.route('/sessions', methods=['GET'])
        def sessions():
            ws = request.args.get('workspace') or None
            return jsonify({'status': True, 'workspaces': _workspace_list(),
                            'sessions': _session_list(ws)})

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
            execution = data.get('execution') or {}
            s = {
                'name': name, 'title': title,
                'description': str(data.get('description') or '').strip(),
                'params': data.get('params') or [],
                'execution': execution,
                'enabled': bool(data.get('enabled', True)),
                'updated': int(time.time()),
            }
            if not _skill_struct_ok(s):
                return jsonify({'error': '技能需配置 execution(shell/tool/http) 且字段完整'}), 400
            _save_json(os.path.join(SKILL_DIR, name + '.json'), s)
            return jsonify({'ok': True, 'skill': {
                'name': name, 'title': title,
                'description': s['description'], 'params': s['params'],
                'execution': s['execution'], 'enabled': s['enabled'],
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

        @self.route('/memory', methods=['GET', 'POST'])
        def memory():
            if request.method == 'GET':
                content = ''
                try:
                    if os.path.isfile(MEMORY_PATH):
                        with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
                            content = f.read()
                except Exception:
                    pass
                return jsonify({'status': True, 'content': content})
            data = request.get_json(silent=True) or {}
            if 'content' not in data:
                return jsonify({'error': '缺少 content'}), 400
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(MEMORY_PATH, 'w', encoding='utf-8') as f:
                    f.write(str(data['content']))
            except Exception as e:
                return jsonify({'error': '写入失败: %s' % e}), 500
            return jsonify({'ok': True})

        @self.route('/chat', methods=['POST'])
        def chat():
            data = request.get_json(silent=True) or {}
            message = str(data.get('message') or '').strip()
            if not message:
                return jsonify({'error': '消息为空'}), 400
            cfg = _load_conf()
            if not (cfg.get('api_base') and cfg.get('api_key')):
                return jsonify({'error': '尚未配置 API Base 与 Key, 请先到设置页填写'}), 400
            if not cfg.get('model'):
                return jsonify({'error': '尚未配置模型, 请先到设置页填写模型名称'}), 400
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
