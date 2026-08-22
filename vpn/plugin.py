# -*- coding: utf-8 -*-
"""RainCough VPN
WireGuard / OpenVPN / v2ray(代理) 三技术, 客户端 + 服务端双模式, 含节点订阅。
命令编排走 sudo -S(sudo_pw 存 vpn.conf), 服务统一用 systemd unit(开机自启/崩溃自愈)。
"""
import os
import re
import sys
import json
import time
import base64
import socket
import shutil
import subprocess
import urllib.parse
import urllib.request

from flask import request, jsonify, Response
from plugins.base import Plugin

# v2ray 实时流量统计 (gRPC StatsService); 无 grpcio 时流量返 0,不影响其它功能
_VDIR = os.path.dirname(os.path.abspath(__file__))
if _VDIR not in sys.path:
    sys.path.insert(0, _VDIR)
try:
    import stats_pb2 as _spb
    import stats_pb2_grpc as _spbgrpc
    import grpc as _grpc
    _GRPC_OK = True
except Exception:
    _spb = _spbgrpc = _grpc = None
    _GRPC_OK = False

PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PLUGIN_ROOT, 'data')
CONF_PATH = os.path.join(PLUGIN_ROOT, 'vpn.conf')
WG_ETC = '/etc/wireguard'
OVPN_CLIENT_DIR = '/etc/openvpn/client'
OVPN_SERVER_DIR = '/etc/openvpn/server'
EASY_RSA_DIR = '/etc/openvpn/easy-rsa'
SYSTEMD_DIR = '/etc/systemd/system'
FWD_TARGET = 'https://api.ipify.org'
LATENCY_TARGET = 'https://github.com'
SPEED_URL = 'https://speed.cloudflare.com/__down?bytes=10000000'

_SUB_STORE = os.path.join(DATA_DIR, 'subs.json')
_NODE_STORE = os.path.join(DATA_DIR, 'nodes.json')
_WG_STORE = os.path.join(DATA_DIR, 'wg_server.json')
_OVPN_STORE = os.path.join(DATA_DIR, 'ovpn_server.json')
_V2_STORE = os.path.join(DATA_DIR, 'v2ray.json')

WIREGUARD_BOUND = ('wg', 'wg-quick')
SECRET_HINTS = ('privatekey', 'presharedkey', 'privat_endpoint', 'password', 'secret')


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------
def _read_conf():
    cfg = {}
    try:
        with open(CONF_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                cfg[k.strip()] = v.strip()
    except Exception:
        pass
    return cfg


def _write_conf(cfg):
    try:
        with open(CONF_PATH, 'w', encoding='utf-8') as f:
            for k, v in cfg.items():
                f.write('%s=%s\n' % (k, v))
        os.chmod(CONF_PATH, 0o600)
    except Exception:
        pass


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


def _sudo(args, timeout=60):
    try:
        pw = _read_conf().get('sudo_pw', '')
        r = subprocess.run(['sudo', '-S'] + list(args), capture_output=True,
                           text=True, timeout=timeout, input=pw + '\n')
        return {'ok': r.returncode == 0, 'rc': r.returncode,
                'out': r.stdout, 'err': r.stderr}
    except subprocess.TimeoutExpired:
        return {'ok': False, 'rc': None, 'out': '', 'err': '命令超时'}
    except Exception as e:
        return {'ok': False, 'rc': None, 'out': '', 'err': str(e)}


def _sh(args, timeout=60):
    try:
        r = subprocess.run(list(args), capture_output=True, text=True, timeout=timeout)
        return {'ok': r.returncode == 0, 'rc': r.returncode,
                'out': r.stdout, 'err': r.stderr}
    except subprocess.TimeoutExpired:
        return {'ok': False, 'rc': None, 'out': '', 'err': '命令超时'}
    except Exception as e:
        return {'ok': False, 'rc': None, 'out': '', 'err': str(e)}


def _bin(name):
    return shutil.which(name)


def _redact(text):
    """把输出里的密钥/密码行打码, 避免前端泄漏私钥。"""
    if not text:
        return text
    out = []
    for line in text.splitlines():
        low = line.lower()
        if any(h in low for h in SECRET_HINTS) and '=' in line:
            k, _ = line.split('=', 1)
            out.append('%s=***' % k.strip())
        else:
            out.append(line)
    return '\n'.join(out)


def _endpoint_host():
    try:
        h = request.host.split(':')[0]
        if h and h not in ('localhost', '127.0.0.1'):
            return h
    except Exception:
        pass
    return _host_ip() or '192.168.2.200'


def _host_ip():
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=6) as r:
            return r.read().decode('utf-8', 'replace').strip()
    except Exception:
        return None


def _lan_ip():
    """返回宿主一个私有 IPv4 地址(链接模式供 LAN 客户端使用); 无则 None。"""
    import ipaddress
    try:
        r = _sh(['sh', '-c', "ip -4 route get 1.1.1.1 2>/dev/null | sed -n 's/.*src \\([0-9.]*\\).*/\\1/p'"])
        if r['out'] and r['out'].strip():
            cand = r['out'].strip().split()[0]
            ip = ipaddress.ip_address(cand)
            if ip.is_private and not ip.is_loopback:
                return cand
    except Exception:
        pass
    try:
        r = _sh(['sh', '-c', "hostname -I 2>/dev/null"])
        for cand in (r['out'] or '').split():
            try:
                ip = ipaddress.ip_address(cand)
                if ip.is_private and not ip.is_loopback:
                    return cand
            except Exception:
                continue
    except Exception:
        pass
    return None


def _wan_if():
    r = _sh(['sh', '-c', "ip route show default 2>/dev/null | awk '{print $5}' | head -1"])
    return r['out'].strip() or None


def _dns_ok():
    return bool(shutil.which('resolvconf') or os.path.isfile('/sbin/resolvconf'))


def _tcp_latency(host, port, timeout=4):
    host = host.split(',')[0].strip()
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        return None, 'dns解析失败'
    s = time.time()
    try:
        sk = socket.create_connection((ip, port), timeout=timeout)
        sk.settimeout(2)
        try:
            sk.recv(1)
        except Exception:
            pass
        sk.close()
        return int((time.time() - s) * 1000), None
    except Exception as e:
        return None, '连接失败 %s' % str(e).split(':')[-1].strip()


def _unit_action(unit, action, timeout=90):
    if action == 'autostart':
        on = bool(request.json.get('on')) if request.json else True
        return _sudo(['systemctl', 'enable' if on else 'disable', unit], timeout=30)
    return _sudo(['systemctl', '--no-pager', action, unit], timeout=timeout)


def _unit_running(unit):
    r = _sudo(['systemctl', '--no-pager', 'is-active', unit], timeout=30)
    return (r['out'] or '').strip()


def _write_unit(unit, lines):
    path = os.path.join(SYSTEMD_DIR, unit)
    r = _sudo(['bash', '-c',
               "cat > '%s' <<'EOF'\n%s\nEOF\nchmod 644 '%s'\n" % (path, ''.join(lines), path)],
              timeout=30)
    _sudo(['systemctl', 'daemon-reload'], timeout=30)
    return r


def _read_unit(unit):
    path = os.path.join(SYSTEMD_DIR, unit)
    r = _sudo(['cat', path], timeout=30)
    return r['out'] if r['ok'] else ''


def _rm_unit(unit):
    _sudo(['rm', '-f', os.path.join(SYSTEMD_DIR, unit)], timeout=30)
    _sudo(['systemctl', 'daemon-reload'], timeout=30)


# ---------------------------------------------------------------------------
# 前端便捷工具
# ---------------------------------------------------------------------------
def _log_tail(pattern, n=200):
    r = _sudo(['bash', '-c', "journalctl _PID=$(pgrep -f '%s' | head -1) -n %d --no-pager 2>/dev/null" % (pattern, n)], timeout=40)
    body = r['out'] or ''
    if not body:
        r = _sudo(['bash', '-c', "journalctl -n %d --no-pager | grep -iE '%s' | tail -%d" % (n * 3, pattern, n)], timeout=40)
        body = r['out'] or ''
    return body[-4000:]


# ---------------------------------------------------------------------------
# 插件
# ---------------------------------------------------------------------------
class VpnPlugin(Plugin):
    name = 'vpn'
    label = 'VPN 网络'
    icon = ''
    description = 'WireGuard / OpenVPN / v2ray 代理: 客户端+服务端连接管理, 节点订阅, 出网检测'

    # ---- 可插拔设置: 设置页「插件设置」 ----
    def get_setting_schema(self):
        sch = [
            {'key': 'sudo_pw', 'label': 'sudo 密码(用于提权管理 VPN)', 'type': 'text',
             'value': '', 'help': '留空则不修改已保存的密码'},
            {'key': 'fwd_target', 'label': '出网检测目标', 'type': 'text',
             'value': _read_conf().get('fwd_target', FWD_TARGET),
             'help': '经代理测试时请求的目标(返回本机出口 IP 的接口)'},
        ]
        return sch

    def get_settings(self):
        cfg = _read_conf()
        return {'sudo_pw': '', 'fwd_target': cfg.get('fwd_target', FWD_TARGET)}

    def save_settings(self, data):
        cfg = _read_conf()
        skip = not data.get('sudo_pw')
        changed = False
        if not skip:
            cfg['sudo_pw'] = str(data['sudo_pw'])
            cfg.pop('_masked', None)
            changed = True
        if data.get('fwd_target'):
            cfg['fwd_target'] = str(data['fwd_target']).strip()
            changed = True
        _write_conf(cfg)
        return True, '已保存'

    def _register_routes(self):
        self._routes_env()
        self._routes_wg()
        self._routes_ovpn()
        self._routes_v2()
        self._routes_overview()

    # ---- 环境 ----
    def _routes_env(self):
        @self.route('/env', methods=['GET'])
        def env():
            wg_t = shutil.which('wg')
            wgq = shutil.which('wg-quick')
            wg_mod = os.path.isdir('/sys/module/wireguard')
            ovpn = shutil.which('openvpn')
            easy = shutil.which('easyrsa') or os.path.isfile('/usr/share/easy-rsa/easyrsa')
            v2b = shutil.which('v2ray') or shutil.which('xray')
            apt = _bin('apt-get')
            sudo_r = _sudo(['true'], timeout=20)
            return jsonify({
                'wireguard': {'installed': bool(wg_t and wgq),
                              'module': wg_mod, 'tool': wg_t,
                              'ograde': '内核模块已加载' if wg_mod else '内核模块未加载/未装'},
                'openvpn': {'installed': bool(ovpn), 'tool': ovpn},
                'easyrsa': {'installed': bool(easy),
                            'tool': shutil.which('easyrsa') or '/usr/share/easy-rsa/easyrsa'},
                'v2ray': {'installed': bool(v2b),
                          'tool': v2b, 'version': self._v2_ver(v2b)},
                'apt': bool(apt),
                'sudo': sudo_r.get('ok'),
                'sudo_note': '' if sudo_r.get('ok') else (sudo_r.get('err') or 'sudo 需密码, 请在设置页填写'),
            })

        @self.route('/install', methods=['POST'])
        def install():
            data = request.json or {}
            pkgs = data.get('packages') or []
            if not pkgs:
                return jsonify({'error': '未指定安装包'}), 400
            r = _sudo(['apt-get', 'install', '-y'] + list(pkgs), timeout=600)
            return jsonify({'ok': r['ok'], 'out': _redact(r['out'][-3000:]),
                            'err': _redact(r['err'][-1000:])})

    def _v2_ver(self, path):
        if not path:
            return ''
        try:
            return (_sh([path, 'version'], timeout=15)['out'] or '').strip()[:120]
        except Exception:
            return ''

    # ---- WireGuard ----
    def _wg_profiles(self):
        r = _sudo(['ls', '-1', WG_ETC], timeout=20)
        names = []
        if r['ok']:
            for n in (r['out'] or '').splitlines():
                if n.endswith('.conf'):
                    names.append(n[:-5])
        names.sort()
        return names

    def _wg_running(self):
        r = _sudo(['wg', 'show', 'interfaces'], timeout=20)
        return (r['out'] or '').split() if r['ok'] else []

    def _wg_status(self):
        r = _sudo(['wg', 'show'], timeout=20)
        interfaces = []
        cur_if = None
        cur_peer = None
        if r['ok']:
            for raw in (r['out'] or '').splitlines():
                s = raw.rstrip()
                m = re.match(r'^interface:\s*(\S+)', s)
                if m:
                    cur_if = {'iface': m.group(1), 'public_key': '', 'port': None,
                              'own_address': '', 'peers': []}
                    interfaces.append(cur_if)
                    cur_peer = None
                    continue
                m = re.match(r'^\s+public key:\s*(\S+)', s)
                if m and cur_if:
                    cur_if['public_key'] = m.group(1)
                    continue
                m = re.match(r'^\s+listening port:\s*(\d+)', s)
                if m and cur_if:
                    cur_if['port'] = int(m.group(1))
                    cur_if['own_address'] = self._wg_iface_addr(cur_if['iface'])
                    continue
                m = re.match(r'^peer:\s*(\S+)', s)
                if m and cur_if:
                    cur_peer = {'pubkey': m.group(1), 'endpoint': None,
                                'allowed_ips': [], 'handshake': None,
                                'transfer_rx': None, 'transfer_tx': None,
                                'keepalive': None}
                    cur_if['peers'].append(cur_peer)
                    continue
                if cur_peer is None:
                    continue
                m = re.match(r'^\s+endpoint:\s*(\S+)', s)
                if m:
                    cur_peer['endpoint'] = m.group(1); continue
                m = re.match(r'^\s+allowed ips:\s*(.+)', s)
                if m:
                    cur_peer['allowed_ips'] = m.group(1).split(','); continue
                m = re.match(r'^\s+latest handshake:\s*(.+)', s)
                if m:
                    cur_peer['handshake'] = m.group(1).strip(); continue
                m = re.match(r'^\s+transfer:\s*([\d.]+ \S+) received,\s*([\d.]+ \S+) sent', s)
                if m:
                    cur_peer['transfer_rx'] = m.group(1)
                    cur_peer['transfer_tx'] = m.group(2)
                    continue
                m = re.match(r'^\s+persistent keepalive:\s*(\S+)', s)
                if m:
                    cur_peer['keepalive'] = m.group(1)
        return {'interfaces': interfaces, 'running': [i['iface'] for i in interfaces]}

    def _wg_iface_addr(self, iface):
        r = _sudo(['bash', '-c', "ip -4 addr show %s 2>/dev/null | awk '/inet /{print $2}' | head -1" % iface], timeout=20)
        return (r['out'] or '').strip()

    def _routes_wg(self):
        @self.route('/wg/env', methods=['GET'])
        def wg_env():
            return jsonify({'profiles': self._wg_profiles(),
                            'running': self._wg_running()})

        @self.route('/wg/status', methods=['GET'])
        def wg_status():
            return jsonify(self._wg_status())

        @self.route('/wg/import', methods=['POST'])
        def wg_import():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            content = data.get('content', '')
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '名称需为字母数字_-'}), 400
            if not content or '[Interface]' not in content:
                return jsonify({'error': '配置内容需包含 [Interface]'}), 400
            path = os.path.join(WG_ETC, name + '.conf')
            r = _sudo(['bash', '-c',
                       "cat > '%s' <<'EOF'\n%s\nEOF\nchmod 600 '%s'\n" % (path, content, path)],
                      timeout=30)
            if not r['ok']:
                return jsonify({'error': r['err'][-300:]}), 500
            return jsonify({'ok': True, 'name': name})

        @self.route('/wg/action', methods=['POST'])
        def wg_action():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            action = data.get('action', '')
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '非法名称'}), 400
            if action == 'delete':
                r = _sudo(['systemctl', '--no-pager', 'stop',
                           'rcvpn-wg-%s.service' % name], timeout=30)
                _rm_unit('rcvpn-wg-%s.service' % name)
                _sudo(['rm', '-f', os.path.join(WG_ETC, name + '.conf')], timeout=20)
                return jsonify({'ok': True})
            if action == 'up':
                r = _sudo(['wg-quick', 'up', name], timeout=40)
                if not r['ok']:
                    return jsonify({'error': (r['err'] or r['out'])[-400:]}), 500
                self._ensure_wg_unit(name)
                return jsonify({'ok': True})
            if action == 'down':
                r = _sudo(['wg-quick', 'down', name], timeout=40)
                _rm_unit('rcvpn-wg-%s.service' % name)
                return jsonify({'ok': True, 'note': (r['err'] or '').strip()[-200:] or None})
            if action == 'autostart':
                self._ensure_wg_unit(name)
                return jsonify(_unit_action('rcvpn-wg-%s.service' % name, 'autostart'))
            if action == 'unitstate':
                return jsonify({'active': _unit_running('rcvpn-wg-%s.service' % name),
                                'unit': _read_unit('rcvpn-wg-%s.service' % name)})
            return jsonify({'error': '未知操作'}), 400

        @self.route('/wg/config', methods=['GET'])
        def wg_config():
            name = request.args.get('name', '')
            if not name:
                return jsonify({'error': '缺少 name'}), 400
            path = os.path.join(WG_ETC, name + '.conf')
            r = _sudo(['cat', path], timeout=20)
            return jsonify({'name': name, 'content': _redact(r['out'] if r['ok'] else '')})

        @self.route('/wg/server', methods=['GET'])
        def wg_server_get():
            store = _load_json(_WG_STORE, {})
            running = self._wg_running()
            fwd = _sh(['sh', '-c', 'sysctl -n net.ipv4.ip_forward'] )['out'].strip()
            safe = dict(store)
            safe.pop('server_privkey', None)
            safe.pop('server_psk', None)
            for p in safe.get('peers', []):
                p.pop('privkey', None)
            return jsonify({
                'store': safe,
                'running': store.get('iface') in running,
                'normalized': self._server_conf(store, plain=False),
                'binds': self._norm_ip(), 'wan_if': _wan_if(),
                'ip_forward': fwd == '1',
            })

        @self.route('/wg/server/save', methods=['POST'])
        def wg_server_save():
            data = request.json or {}
            store = _load_json(_WG_STORE, {})
            for k in ('iface', 'address', 'port', 'mtu', 'dns', 'wan_if'):
                if data.get(k) is not None:
                    store[k] = str(data[k]).strip()
            old = store.get('server_privkey')
            if data.get('genkeys') or not old:
                self._gen_wg_keys(store, data.get('peer_count', 0))
            store['peers'] = data.get('peers', store.get('peers', []))
            _save_json(_WG_STORE, store)
            return jsonify({'ok': True})

        @self.route('/wg/server/up', methods=['POST'])
        def wg_server_up():
            store = _load_json(_WG_STORE, {})
            if not store.get('server_privkey'):
                self._gen_wg_keys(store)
            self._wg_enable_nat(store)
            r = _sudo(['wg-quick', 'up', store.get('iface', 'wg0')], timeout=60)
            if not r['ok']:
                return jsonify({'error': (r['err'] or r['out'])[-400:]}), 500
            self._ensure_wg_unit(store.get('iface', 'wg0'))
            return jsonify({'ok': True})

        @self.route('/wg/server/down', methods=['POST'])
        def wg_server_down():
            store = _load_json(_WG_STORE, {})
            _sudo(['wg-quick', 'down', store.get('iface', 'wg0')], timeout=40)
            _rm_unit('rcvpn-wg-%s.service' % store.get('iface', 'wg0'))
            return jsonify({'ok': True})

        @self.route('/wg/peers/add', methods=['POST'])
        def wg_peer_add():
            data = request.json or {}
            store = _load_json(_WG_STORE, {})
            if not store.get('server_privkey'):
                self._gen_wg_keys(store)
            name = str(data.get('name', '')).strip()
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '非法名称'}), 400
            self._gen_wg_keys(store, data.get('peer_count', 0))
            peers = store.setdefault('peers', [])
            if any(p.get('name') == name for p in peers):
                return jsonify({'error': 'peer 已存在'}), 400
            client_pub, client_priv = self._wg_keypair()
            base = store.get('address', '10.8.0.1/24').split('/')[0]
            cid = len(peers) + 1
            client_addr = '%s.%d' % ('.'.join(base.split('.')[:3]), cid + 1)
            peers.append({'name': name, 'pubkey': client_pub, 'privkey': client_priv,
                          'address': client_addr + '/32', 'created': int(time.time())})
            _save_json(_WG_STORE, store)
            return jsonify({'ok': True, 'name': name, 'address': client_addr})

        @self.route('/wg/peers/delete', methods=['POST'])
        def wg_peer_del():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            store = _load_json(_WG_STORE, {})
            before = store.get('peers', [])
            store['peers'] = [p for p in before if p.get('name') != name]
            _save_json(_WG_STORE, store)
            return jsonify({'ok': True, 'removed': len(before) - len(store['peers'])})

        @self.route('/wg/export', methods=['POST'])
        def wg_export():
            name = str((request.json or {}).get('name', '')).strip()
            store = _load_json(_WG_STORE, {})
            peer = next((p for p in store.get('peers', []) if p.get('name') == name), None)
            if not peer:
                return jsonify({'error': 'peer 不存在'}), 404
            server_priv = store.get('server_privkey')
            server_pub = self._wg_pubkey(server_priv) if server_priv else ''
            dns_line = ('DNS = %s\n' % store.get('dns', '1.1.1.1')) if _dns_ok() else ''
            endpoint = _endpoint_host()
            port = store.get('port', '51820')
            conf = ('[Interface]\n'
                    'PrivateKey = %s\n'
                    'Address = %s\n'
                    '%s'
                    '\n[Peer]\n'
                    'PublicKey = %s\n'
                    'PresharedKey = %s\n'
                    'AllowedIPs = %s\n'
                    'Endpoint = %s:%s\n'
                    'PersistentKeepalive = 25\n') % (
                        peer.get('privkey', ''), peer.get('address', ''),
                        dns_line, server_pub, store.get('server_psk', ''),
                        store.get('allow_ips', '0.0.0.0/0'), endpoint, port)
            return jsonify({'ok': True, 'content': conf, 'filename': '%s.conf' % name})

        @self.route('/wg/peer', methods=['GET'])
        def wg_peer():
            name = request.args.get('name', '')
            store = _load_json(_WG_STORE, {})
            peer = next((p for p in store.get('peers', []) if p.get('name') == name), None)
            if not peer:
                return jsonify({'error': 'peer 不存在'}), 404
            return jsonify({'name': peer['name'], 'address': peer['address'],
                            'pubkey': peer['pubkey'],
                            'client_conf': self._client_conf(store, peer)})

    def _gen_wg_keys(self, store, peer_count=0):
        if not store.get('server_privkey'):
            store['server_privkey'] = self._wg_genkey()
        if not store.get('server_psk'):
            store['server_psk'] = self._wg_genkey()
        for _ in range(peer_count):
            pass
        return store

    def _wg_genkey(self):
        r = _sh(['wg', 'genkey'], timeout=15)
        return (r['out'] or '').strip()

    def _wg_pubkey(self, priv):
        r = _sh(['bash', '-c', "echo '%s' | wg pubkey" % priv], timeout=15)
        return (r['out'] or '').strip()

    def _wg_keypair(self):
        priv = self._wg_genkey()
        return self._wg_pubkey(priv), priv

    def _server_conf(self, store, plain=False):
        if not store.get('server_privkey'):
            store['server_privkey'] = self._wg_genkey()
            store['server_psk'] = store.get('server_psk') or self._wg_genkey()
        iface = store.get('iface', 'wg0')
        lines = []
        conf_lines = ['[Interface]\n',
                      'Address = %s\n' % store.get('address', '10.8.0.1/24'),
                      'ListenPort = %s\n' % store.get('port', '51820'),
                      ]
        if store.get('mtu'):
            conf_lines.append('MTU = %s\n' % store['mtu'])
        if store.get('dns') and _dns_ok():
            conf_lines.append('DNS = %s\n' % store['dns'])
        shadow = 'PrivateKey = %s\n' % (store.get('server_privkey', ''))
        psk = store.get('server_psk', '')
        conf_lines.append(shadow if plain else 'PrivateKey = ***\n')
        for p in store.get('peers', []):
            conf_lines.append('\n[Peer]\n')
            conf_lines.append('PublicKey = %s\n' % p.get('pubkey', ''))
            conf_lines.append('PresharedKey = %s\n' % (psk if plain else '***'))
            conf_lines.append('AllowedIPs = %s\n' % p.get('address', ''))
        return ''.join(conf_lines), shadow

    def _wg_enable_nat(self, store):
        subnet = store.get('address', '10.8.0.1/24').split('/')[0]
        wan = store.get('wan_if') or _wan_if()
        conf, _ = self._server_conf(store, plain=True)
        self._write_wg_conf(store.get('iface', 'wg0'), conf)
        _sudo(['sh', '-c', 'sysctl -w net.ipv4.ip_forward=1'], timeout=20)
        if wan:
            ipt = _bin('iptables')
            if ipt:
                _sudo([ipt, '-t', 'nat', '-C',
                       'POSTROUTING', '-s', subnet, '-o', wan, '-j', 'MASQUERADE'],
                      timeout=20)
                _sudo([ipt, '-t', 'nat', '-I',
                       'POSTROUTING', '-s', subnet, '-o', wan, '-j', 'MASQUERADE'],
                      timeout=20)

    def _write_wg_conf(self, iface, conf):
        path = os.path.join(WG_ETC, iface + '.conf')
        _sudo(['bash', '-c', "cat > '%s' <<'EOF'\n%s\nEOF\nchmod 600 '%s'\n" % (path, conf, path)],
              timeout=30)

    def _ensure_wg_unit(self, name):
        unit = 'rcvpn-wg-%s.service' % name
        body = ['[Unit]\nDescription=RainCough WireGuard %s\nAfter=network-online.target\nWants=network-online.target\n'
                '\n[Service]\nType=oneshot\nRemainAfterExit=yes\n'
                'ExecStart=/usr/bin/wg-quick up %s\nExecStop=/usr/bin/wg-quick down %s\n'
                '\n[Install]\nWantedBy=multi-user.target\n' % (name, name, name)]
        _write_unit(unit, body)

    def _client_conf(self, store, peer):
        server_priv = store.get('server_privkey', '')
        server_pub = self._wg_pubkey(server_priv) if server_priv else ''
        dns_line = ('DNS = %s\n' % store.get('dns', '1.1.1.1')) if _dns_ok() else ''
        return ('[Interface]\nPrivateKey = %s\nAddress = %s\n%s\n'
                '[Peer]\nPublicKey = %s\nPresharedKey = %s\nAllowedIPs = %s\n'
                'Endpoint = %s:%s\nPersistentKeepalive = 25\n') % (
                    peer.get('privkey', ''), peer.get('address', ''),
                    dns_line, server_pub, store.get('server_psk', ''),
                    store.get('allow_ips', '0.0.0.0/0'),
                    _endpoint_host(), store.get('port', '51820'))

    def _norm_ip(self):
        r = _sudo(['ip', '-brief', 'addr'], timeout=20)
        return _redact(r['out'] if r['ok'] else '')

    # ---- OpenVPN ----
    def _ovpn_clients(self):
        r = _sudo(['ls', '-1', OVPN_CLIENT_DIR], timeout=20)
        names = []
        if r['ok']:
            for n in (r['out'] or '').splitlines():
                if n.endswith('.conf'):
                    names.append(n[:-5])
        names.sort()
        return names

    def _ovpn_running(self):
        r = _sudo(['bash', '-c', "pgrep -a openvpn 2>/dev/null || true"], timeout=20)
        return (r['out'] or '').strip()

    def _routes_ovpn(self):
        @self.route('/ovpn/env', methods=['GET'])
        def ovpn_env():
            return jsonify({'clients': self._ovpn_clients(),
                            'running': self._ovpn_running(),
                            'server_running': (_unit_running('rcvpn-ovpn-server.service') == 'active')})

        @self.route('/ovpn/import', methods=['POST'])
        def ovpn_import():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            content = data.get('content', '')
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '名称需为字母数字_-'}), 400
            if not content:
                return jsonify({'error': '配置内容为空'}), 400
            path = os.path.join(OVPN_CLIENT_DIR, name + '.conf')
            r = _sudo(['bash', '-c',
                       "cat > '%s' <<'EOF'\n%s\nEOF\nchmod 600 '%s'\n" % (path, content, path)],
                      timeout=30)
            if not r['ok']:
                return jsonify({'error': r['err'][-300:]}), 500
            return jsonify({'ok': True, 'name': name})

        @self.route('/ovpn/action', methods=['POST'])
        def ovpn_action():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            action = data.get('action', '')
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '非法名称'}), 400
            if action == 'delete':
                _sudo(['systemctl', '--no-pager', 'stop', 'rcvpn-ovpn-%s.service' % name], timeout=30)
                _rm_unit('rcvpn-ovpn-%s.service' % name)
                _sudo(['rm', '-f', os.path.join(OVPN_CLIENT_DIR, name + '.conf')], timeout=20)
                return jsonify({'ok': True})
            if action == 'up':
                self._write_ovpn_unit(name, 'client')
                return jsonify(_unit_action('rcvpn-ovpn-%s.service' % name, 'start'))
            if action == 'down':
                return jsonify(_unit_action('rcvpn-ovpn-%s.service' % name, 'stop'))
            if action == 'autostart':
                return jsonify(_unit_action('rcvpn-ovpn-%s.service' % name, 'autostart'))
            if action == 'unitstate':
                return jsonify({'active': _unit_running('rcvpn-ovpn-%s.service' % name),
                                'unit': _read_unit('rcvpn-ovpn-%s.service' % name)})
            return jsonify({'error': '未知操作'}), 400

        @self.route('/ovpn/config', methods=['GET'])
        def ovpn_config():
            name = request.args.get('name', '')
            path = os.path.join(OVPN_CLIENT_DIR, name + '.conf')
            r = _sudo(['cat', path], timeout=20)
            return jsonify({'name': name, 'content': _redact(r['out'] if r['ok'] else '')})

        @self.route('/ovpn/log', methods=['GET'])
        def ovpn_log():
            return jsonify({'log': _log_tail('openvpn')})

        @self.route('/ovpn/server', methods=['GET'])
        def ovpn_server_get():
            store = _load_json(_OVPN_STORE, {})
            pki = os.path.isdir(os.path.join(EASY_RSA_DIR, 'pki'))
            conf = os.path.isfile(os.path.join(OVPN_SERVER_DIR, store.get('iface', 'server') + '.conf'))
            return jsonify({'store': store, 'pki_ready': pki, 'conf_exists': conf,
                            'running': (_unit_running('rcvpn-ovpn-server.service') == 'active'),
                            'server_conf': self._read_ovpn_server_conf()})

        @self.route('/ovpn/server/save', methods=['POST'])
        def ovpn_server_save():
            data = request.json or {}
            store = _load_json(_OVPN_STORE, {})
            for k in ('iface', 'port', 'proto', 'subnet', 'server_address', 'dns', 'comp_lzo'):
                if data.get(k) is not None:
                    store[k] = str(data[k]).strip()
            _save_json(_OVPN_STORE, store)
            if data.get('write_conf'):
                r = self._write_ovpn_server_conf(store)
                if not r['ok']:
                    return jsonify({'error': r['err'][-400:]}), 500
            return jsonify({'ok': True})

        @self.route('/ovpn/server/init-pki', methods=['POST'])
        def ovpn_init_pki():
            r = self._init_easyrsa()
            if not r['ok']:
                return jsonify({'ok': False, 'error': r['err'][-500:], 'out': r['out'][-1500:]}), 500
            return jsonify({'ok': True, 'out': r['out'][-1500:]})

        @self.route('/ovpn/server/build', methods=['POST'])
        def ovpn_build():
            store = _load_json(_OVPN_STORE, {})
            out = []
            ok = True
            for step in ('server', 'dh'):
                name = store.get('server_name', 'server')
                r = self._easyrsa(step, name)
                out.append('[%s] rc=%s %s%s' % (step, r.get('rc'),
                                                r.get('out', '')[-300:], r.get('err', '')[-300:]))
                if not r.get('ok'):
                    ok = False
            _save_json(_OVPN_STORE, store)
            return jsonify({'ok': ok, 'out': '\n'.join(out)[-2000:]})

        @self.route('/ovpn/server/up', methods=['POST'])
        def ovpn_server_up():
            store = _load_json(_OVPN_STORE, {})
            self._write_ovpn_server_conf(store)
            self._write_ovpn_unit(store.get('iface', 'server'), 'server')
            return jsonify(_unit_action('rcvpn-ovpn-server.service', 'start'))

        @self.route('/ovpn/server/down', methods=['POST'])
        def ovpn_server_down():
            return jsonify(_unit_action('rcvpn-ovpn-server.service', 'stop'))

        @self.route('/ovpn/server/log', methods=['GET'])
        def ovpn_server_log():
            return jsonify({'log': _log_tail('openvpn')})

    def _init_easyrsa(self):
        easy = shutil.which('easyrsa') or '/usr/share/easy-rsa/easyrsa'
        _sudo(['mkdir', '-p', EASY_RSA_DIR], timeout=20)
        cmd = ['bash', '-c',
               'cd %s && ( [ -d pki ] || %s init-pki 2>&1 )' % (EASY_RSA_DIR, easy)]
        r1 = _sudo(cmd, timeout=120)
        if not r1['ok']:
            return r1
        if not os.path.isfile(os.path.join(EASY_RSA_DIR, 'pki', 'ca.crt')):
            cmd = ['bash', '-c',
                   'cd %s && EASYRSA_BATCH=1 EASYRSA_REQ_CN=RCVPN %s build-ca nopass 2>&1'
                   % (EASY_RSA_DIR, easy)]
            return _sudo(cmd, timeout=120)
        return r1

    def _easyrsa(self, task, name):
        easy = shutil.which('easyrsa') or '/usr/share/easy-rsa/easyrsa'
        if task == 'server':
            cmd = ['bash', '-c',
                   'cd %s && [ -f pki/issued/%s.crt ] || { '
                   'EASYRSA_BATCH=1 EASYRSA_REQ_CN=%s %s gen-req %s nopass 2>&1 && '
                   'EASYRSA_BATCH=1 %s sign-req server %s 2>&1 ; }'
                   % (EASY_RSA_DIR, name, name, easy, name, easy, name)]
            return _sudo(cmd, timeout=120)
        if task == 'dh':
            cmd = ['bash', '-c', 'cd %s && [ -f pki/dh.pem ] || %s gen-dh 2>&1' % (EASY_RSA_DIR, easy)]
            return _sudo(cmd, timeout=600)
        if task == 'build-ca':
            cmd = ['bash', '-c',
                   'cd %s && EASYRSA_BATCH=1 EASYRSA_REQ_CN=RCVPN %s build-ca nopass 2>&1'
                   % (EASY_RSA_DIR, easy)]
            return _sudo(cmd, timeout=120)
        return {'ok': False, 'err': '未知任务'}

    def _write_ovpn_server_conf(self, store):
        store.setdefault('iface', 'server')
        store.setdefault('port', '1194')
        store.setdefault('proto', 'udp')
        store.setdefault('server_address', '10.9.0.0 255.255.255.0')
        subnet = store.get('subnet', '10.9.0.0/24')
        dns = store.get('dns') or '1.1.1.1'
        # subnet "net mask" -> server_address net mask
        try:
            net, mask = subnet.split('/')
        except Exception:
            net, mask = '10.9.0.0', '24'
        prefix = int(mask)
        ones = prefix
        mask_bin = (0xffffffff << (32 - ones)) & 0xffffffff
        mask_str = '.'.join(str((mask_bin >> s) & 0xff) for s in (24, 16, 8, 0))
        wand = '.'.join(net.split('.')[:3])
        conf = ('port %s\nproto %s\ndev tun\ntopology subnet\n'
                'server %s %s\nifconfig-pool-persist ipp.txt\n'
                'push "redirect-gateway def1 bypass-dhcp"\n'
                'push "dhcp-option DNS %s"\n'
                'keepalive 10 120\n'
                'ca %s/pki/ca.crt\n'
                'cert %s/pki/issued/server.crt\n'
                'key %s/pki/private/server.key\n'
                'dh %s/pki/dh.pem\n'
                'user nobody\ngroup nogroup\npersist-key\npersist-tun\nstatus /var/log/openvpn-server.log\n'
                'verb 3\nexplicit-exit-notify 1\n') % (
                    store.get('port', '1194'), store.get('proto', 'udp'),
                    wand + '.0', mask_str, dns,
                    EASY_RSA_DIR, EASY_RSA_DIR, EASY_RSA_DIR, EASY_RSA_DIR)
        path = os.path.join(OVPN_SERVER_DIR, store.get('iface', 'server') + '.conf')
        return _sudo(['bash', '-c',
                      "mkdir -p %s && cat > '%s' <<'EOF'\n%s\nEOF\nchmod 600 '%s'\n" %
                      (OVPN_SERVER_DIR, path, conf, path)], timeout=30)

    def _read_ovpn_server_conf(self):
        store = _load_json(_OVPN_STORE, {})
        path = os.path.join(OVPN_SERVER_DIR, store.get('iface', 'server') + '.conf')
        r = _sudo(['cat', path], timeout=20)
        return _redact(r['out'] if r['ok'] else '')

    def _write_ovpn_unit(self, name, mode):
        unit = 'rcvpn-ovpn-%s.service' % name
        if mode == 'server':
            cfg = os.path.join(OVPN_SERVER_DIR, name + '.conf')
        else:
            cfg = os.path.join(OVPN_CLIENT_DIR, name + '.conf')
        body = ['[Unit]\nDescription=RainCough OpenVPN %s %s\nAfter=network-online.target\nWants=network-online.target\n'
                '\n[Service]\nType=simple\nRestart=on-failure\n'
                'ExecStart=/usr/sbin/openvpn --config %s\n'
                '\n[Install]\nWantedBy=multi-user.target\n' % (name, mode, cfg)]
        _write_unit(unit, body)

    # ---- v2ray 订阅 ----
    def _v2_conf_dir(self):
        d = os.path.join(PLUGIN_ROOT, 'v2ray')
        os.makedirs(d, exist_ok=True)
        return d

    def _v2_profiles(self):
        d = self._v2_conf_dir()
        names = []
        for f in sorted(os.listdir(d)):
            if f.endswith('.json'):
                names.append(f[:-5])
        return names

    def _v2_running(self):
        r = _sudo(['bash', '-c', "systemctl --no-pager list-units --type=service --all | grep rcvpn-v2ray || true"], timeout=30)
        return (r['out'] or '').strip()

    def _running_v2_names(self):
        r = _sudo(['bash', '-c', "systemctl --no-pager list-units --type=service --all "
                                 "| grep rcvpn-v2ray | grep ' active ' || true"], timeout=30)
        out = (r['out'] or '')
        names = []
        for line in out.splitlines():
            m = re.search(r'rcvpn-v2ray-([A-Za-z0-9_-]+)\.service', line)
            if m:
                names.append(m.group(1))
        return names

    def _ovpn_ifaces(self):
        try:
            ifaces = []
            with open('/proc/net/dev', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('tun'):
                        ifaces.append(line.split(':')[0])
            return ifaces
        except Exception:
            return []

    def _routes_v2(self):
        @self.route('/v2/env', methods=['GET'])
        def v2_env():
            return jsonify({'profiles': self._v2_profiles(),
                            'running': self._v2_running(),
                            'dir': self._v2_conf_dir(),
                            'engines': {'sing_box': bool(self._sb_bin()),
                                        'v2ray': bool(shutil.which('v2ray') or shutil.which('xray') or os.path.isfile('/usr/bin/v2ray'))}})

        @self.route('/v2/load', methods=['GET'])
        def v2_load():
            name = request.args.get('name', '')
            path = os.path.join(self._v2_conf_dir(), name + '.json')
            if not os.path.isfile(path):
                return jsonify({'error': '配置不存在'}), 404
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception as e:
                return jsonify({'error': str(e)}), 400
            return jsonify({'name': name, 'config': cfg})

        @self.route('/v2/save', methods=['POST'])
        def v2_save():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            cfg = data.get('config')
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '名称需为字母数字_-'}), 400
            if not isinstance(cfg, dict):
                return jsonify({'error': '配置需为 JSON 对象'}), 400
            inbounds = cfg.get('inbounds') or []
            if not inbounds:
                cfg.setdefault('inbounds', [{'tag': 'socks-in', 'listen': '127.0.0.1',
                                             'port': int(data.get('port', 1080)),
                                             'protocol': 'socks'}])
            cfg = self._ensure_v2_stats(cfg, name)
            path = os.path.join(self._v2_conf_dir(), name + '.json')
            self._save_json(path, cfg)
            return jsonify({'ok': True, 'name': name, 'inbound': inbounds[0] if inbounds else {}})

        @self.route('/v2/action', methods=['POST'])
        def v2_action():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            action = data.get('action', '')
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '非法名称'}), 400
            cfg_path = os.path.join(self._v2_conf_dir(), name + '.json')
            if action == 'delete':
                _sudo(['systemctl', '--no-pager', 'stop', 'rcvpn-v2ray-%s.service' % name], timeout=30)
                _rm_unit('rcvpn-v2ray-%s.service' % name)
                try:
                    os.remove(cfg_path)
                except Exception:
                    pass
                return jsonify({'ok': True})
            if not os.path.isfile(cfg_path):
                return jsonify({'error': '配置不存在'}), 404
            if action in ('up', 'start', 'restart', 'down', 'stop'):
                self._ensure_v2_unit(name)
                act = {'up': 'start', 'start': 'start', 'restart': 'restart',
                       'down': 'stop', 'stop': 'stop'}[action]
                return jsonify(_unit_action('rcvpn-v2ray-%s.service' % name, act))
            if action == 'autostart':
                self._ensure_v2_unit(name)
                return jsonify(_unit_action('rcvpn-v2ray-%s.service' % name, 'autostart'))
            if action == 'unitstate':
                return jsonify({'active': _unit_running('rcvpn-v2ray-%s.service' % name),
                                'unit': _read_unit('rcvpn-v2ray-%s.service' % name)})
            return jsonify({'error': '未知操作'}), 400

        @self.route('/v2/test', methods=['POST'])
        def v2_test():
            data = request.json or {}
            name = str(data.get('name', '')).strip()
            cfg_path = os.path.join(self._v2_conf_dir(), name + '.json')
            if not os.path.isfile(cfg_path):
                return jsonify({'error': '配置不存在'}), 404
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception:
                return jsonify({'error': '配置损坏'}), 400
            target = _read_conf().get('fwd_target', FWD_TARGET)
            return jsonify(self._run_v2_probe(cfg, target))

        @self.route('/v2/log', methods=['GET'])
        def v2_log():
            return jsonify({'log': _log_tail('rcvpn-v2ray')})

        @self.route('/v2/wizard', methods=['POST'])
        def v2_wizard():
            data = request.json or {}
            proto = str(data.get('protocol', '')).lower()
            name = str(data.get('name', '')).strip()
            port = int(data.get('port', 1080))
            addr = str(data.get('address', '')).strip()
            if not re.match(r'^[A-Za-z0-9_-]{1,32}$', name):
                return jsonify({'error': '名称非法'}), 400
            out = self._wizard_outbound(proto, data)
            if not out:
                return jsonify({'error': '不支持的协议'}), 400
            out = dict(out)
            if not out.get('tag') or out['tag'] in ('proxy', 'v2ray-out'):
                out['tag'] = '%s:%s' % (proto, addr or name)
            cfg = {'log': {'loglevel': 'warning'},
                   'inbounds': [{'tag': 'socks-in', 'listen': '127.0.0.1',
                                 'port': port, 'protocol': 'socks'}],
                   'outbounds': [out]}
            cfg = self._ensure_v2_stats(cfg, name)
            path = os.path.join(self._v2_conf_dir(), name + '.json')
            self._save_json(path, cfg)
            return jsonify({'ok': True, 'name': name, 'summary': self._outbound_summary(out),
                            'config': cfg})

        # ---- 订阅 ----
        @self.route('/v2/subs', methods=['GET', 'POST', 'DELETE'])
        def subs():
            store = _load_json(_SUB_STORE, [])
            if request.method == 'GET':
                return jsonify(store)
            if request.method == 'DELETE':
                data = request.json or {}
                url = data.get('url')
                store = [s for s in store if s.get('url') != url]
                _save_json(_SUB_STORE, store)
                return jsonify({'ok': True})
            data = request.json or {}
            url = str(data.get('url', '')).strip()
            name = str(data.get('name', '')).strip()
            if not url.startswith(('http://', 'https://')):
                return jsonify({'error': '订阅链接需 http(s)://'}), 400
            store = [s for s in store if s.get('url') != url]
            store.append({'url': url, 'name': name, 'added': int(time.time()),
                          'last_ok': None, 'count': 0, 'error': None})
            _save_json(_SUB_STORE, store)
            return jsonify({'ok': True})

        @self.route('/v2/subs/refresh', methods=['POST'])
        def subs_refresh():
            data = request.json or {}
            url = data.get('url')
            store = _load_json(_SUB_STORE, [])
            nodes = _load_json(_NODE_STORE, [])
            if url:
                store = [s for s in store if s.get('url') == url]
            results = []
            for sub in store:
                n, err, ok = self._fetch_sub(sub['url'])
                sub['last_ok'] = ok
                sub['count'] = len(n)
                sub['error'] = err
                group = (sub.get('name') or 'default').strip() or 'default'
                for node in n:
                    node['group'] = group
                    idx = next((i for i, nn in enumerate(nodes) if nn.get('_id') == node['_id']), None)
                    if idx is None:
                        nodes.append(node)
                    else:
                        old_lat = nodes[idx].get('latency')
                        old_err = nodes[idx].get('latency_err')
                        old_spd = nodes[idx].get('speed_mbps')
                        kept = {k: nodes[idx].get(k) for k in ('latency', 'latency_err', 'speed_mbps')
                                if nodes[idx].get(k) is not None}
                        nodes[idx] = dict(node)
                        nodes[idx].update(kept)
                results.append({'url': sub['url'], 'nodes': len(n),
                                'error': err, 'ok': ok})
            _save_json(_SUB_STORE, store)
            _save_json(_NODE_STORE, nodes)
            return jsonify({'ok': True, 'results': results, 'total': len(nodes)})

        @self.route('/v2/nodes', methods=['GET'])
        def nodes():
            query = request.args.get('q', '')
            group = request.args.get('group', '')
            store = _load_json(_NODE_STORE, [])
            if query:
                store = [n for n in store if query.lower() in str(n.get('name', '')).lower()
                         or query.lower() in str(n.get('addr', '')).lower()]
            if group and group != 'all':
                store = [n for n in store if n.get('group') == group]
            for n in store:
                n['engine'] = self._engine_for(n.get('protocol') or '')
            return jsonify(store)

        @self.route('/v2/nodes/groups', methods=['GET'])
        def nodes_groups():
            store = _load_json(_NODE_STORE, [])
            groups = []
            for n in store:
                g = n.get('group') or 'default'
                if g not in groups:
                    groups.append(g)
            return jsonify(groups)

        @self.route('/v2/nodes/delete', methods=['POST'])
        def nodes_del():
            data = request.json or {}
            ids = data.get('ids') if isinstance(data.get('ids'), list) else [data.get('id')]
            store = _load_json(_NODE_STORE, [])
            store = [n for n in store if n.get('_id') not in ids]
            _save_json(_NODE_STORE, store)
            return jsonify({'ok': True, 'left': len(store)})

        @self.route('/v2/nodes/test', methods=['POST'])
        def nodes_test():
            data = request.json or {}
            ids = data.get('ids') if isinstance(data.get('ids'), list) else [data.get('id')]
            store = _load_json(_NODE_STORE, [])
            target = 'ping'  # 节点延迟: 直接 ping 节点地址
            results = []
            for n in store:
                if n.get('_id') not in ids:
                    continue
                res = self._ping_host(n.get('addr') or n.get('address') or '')
                if res.get('ok'):
                    n['latency'] = res.get('ms')
                    n['latency_err'] = None
                    results.append({'_id': n['_id'], 'latency': n['latency'], 'error': None})
                else:
                    n['latency'] = None
                    n['latency_err'] = res.get('error', '测试失败')
                    results.append({'_id': n['_id'], 'latency': None, 'error': n['latency_err']})
            _save_json(_NODE_STORE, store)
            return jsonify({'ok': True, 'results': results, 'target': target})

        @self.route('/v2/nodes/speedtest', methods=['POST'])
        def nodes_speedtest():
            data = request.json or {}
            _id = data.get('id')
            store = _load_json(_NODE_STORE, [])
            node = next((n for n in store if n.get('_id') == _id), None)
            if not node:
                return jsonify({'error': '节点不存在'}), 404
            eng = self._engine_for(node.get('protocol'))
            if eng == 'sing-box-missing':
                return jsonify({'ok': False, 'error': '该协议需 sing-box 内核, 但 sing-box 未安装'})
            if eng == 'sing-box':
                res = self._run_singbox_probe(node, SPEED_URL, duration=5)
            else:
                out = self._wizard_outbound(node['protocol'], node)
                if not out:
                    return jsonify({'ok': False, 'error': '无法为该节点构建代理配置'})
                cfg = {'log': {'loglevel': 'warning'}, 'outbounds': [out]}
                res = self._run_v2_speedtest(cfg)
            if res.get('ok') and res.get('mbs'):
                node['speed_mbps'] = res.get('mbs')
                _save_json(_NODE_STORE, store)
            return jsonify(res)

        @self.route('/v2/nodes/select', methods=['POST'])
        def nodes_select():
            data = request.json or {}
            _id = data.get('id')
            name = str(data.get('name', 'v2play')).strip()
            port = int(data.get('port', 1080))
            store = _load_json(_NODE_STORE, [])
            node = next((n for n in store if n.get('_id') == _id), None)
            if not node:
                return jsonify({'error': '节点不存在'}), 404
            eng = self._engine_for(node.get('protocol'))
            if eng == 'sing-box-missing':
                return jsonify({'error': '该协议需 sing-box 内核, 但 sing-box 未安装'}), 400
            if eng == 'sing-box':
                return jsonify(self._connect_singbox(name, node, port))
            out = self._wizard_outbound(node['protocol'], node)
            if not out:
                return jsonify({'error': '该节点协议当前引擎不支持连接'}), 400
            out = dict(out)
            out['tag'] = '%s:%s' % (node['protocol'], node.get('name') or node.get('addr') or 'node')
            cfg = {'log': {'loglevel': 'warning'},
                   'inbounds': [{'tag': 'socks-in', 'listen': self._proxy_bind(),
                                 'port': port, 'protocol': 'socks'}],
                   'outbounds': [out, {'protocol': 'freedom', 'tag': 'direct'}]}
            cfg = self._ensure_v2_stats(cfg, name)
            path = os.path.join(self._v2_conf_dir(), name + '.json')
            self._save_json(path, cfg)
            self._ensure_v2_unit(name)
            _unit_action('rcvpn-singbox-%s.service' % name, 'stop', timeout=15)
            _unit_action('rcvpn-v2ray-%s.service' % name, 'restart')
            self._set_active(name, self._node_label(node))
            return jsonify({'ok': True, 'name': name, 'summary': self._outbound_summary(out),
                            'mode': self._mode_status()})

        @self.route('/v2/mode', methods=['GET', 'POST'])
        def v2_mode():
            if request.method == 'GET':
                return jsonify(self._mode_status())
            data = request.json or {}
            mode = self._set_mode(data.get('mode'))
            # 重启当前活动通道使 bind 生效
            name = 'v2play'
            if _unit_running('rcvpn-v2ray-%s.service' % name) == 'active':
                cfg_path = os.path.join(self._v2_conf_dir(), name + '.json')
                if os.path.isfile(cfg_path):
                    try:
                        with open(cfg_path, 'r', encoding='utf-8') as f:
                            cfg = json.load(f)
                        for i in (cfg.get('inbounds') or []):
                            if i.get('tag') == 'socks-in':
                                i['listen'] = self._proxy_bind()
                        with open(cfg_path, 'w', encoding='utf-8') as f:
                            json.dump(cfg, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                _unit_action('rcvpn-v2ray-%s.service' % name, 'restart')
            elif _unit_running('rcvpn-singbox-%s.service' % name) == 'active':
                cfg_path = os.path.join(self._sb_conf_dir(), name + '.json')
                if os.path.isfile(cfg_path):
                    try:
                        with open(cfg_path, 'r', encoding='utf-8') as f:
                            cfg = json.load(f)
                        for i in (cfg.get('inbounds') or []):
                            if i.get('tag') == 'socks-in':
                                i['listen'] = self._proxy_bind()
                        with open(cfg_path, 'w', encoding='utf-8') as f:
                            json.dump(cfg, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                _unit_action('rcvpn-singbox-%s.service' % name, 'restart')
            return jsonify({'ok': True, **self._mode_status()})

    # ---- v2ray 工具 ----
    def _save_json(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _ensure_v2_unit(self, name):
        unit = 'rcvpn-v2ray-%s.service' % name
        binp = shutil.which('v2ray') or shutil.which('xray') or '/usr/bin/v2ray'
        cfg_path = os.path.join(self._v2_conf_dir(), name + '.json')
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                cfg = self._ensure_v2_stats(cfg, name)
                with open(cfg_path, 'w', encoding='utf-8') as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        body = ['[Unit]\nDescription=RainCough v2ray %s\nAfter=network-online.target\nWants=network-online.target\n'
                '\n[Service]\nType=simple\nRestart=always\nRestartSec=3\n'
                'ExecStart=%s -config %s\n'
                '\n[Install]\nWantedBy=multi-user.target\n' % (name, binp, cfg_path)]
        _write_unit(unit, body)

    def _v2_api_port(self, name):
        n = 0
        for ch_ in name:
            n = (n * 31 + ord(ch_)) & 0xFFFF
        return 10085 + (n % 100)

    # ---- 代理模式: 本地/链接 ----
    def _get_mode(self):
        return _read_conf().get('proxy_mode', 'local')

    def _proxy_bind(self):
        return '0.0.0.0' if self._get_mode() == 'link' else '127.0.0.1'

    def _set_mode(self, mode):
        mode = 'link' if mode == 'link' else 'local'
        cfg = _read_conf()
        cfg['proxy_mode'] = mode
        _write_conf(cfg)
        return mode

    def _mode_status(self):
        return {'mode': self._get_mode(), 'bind': self._proxy_bind(),
                'lan_ip': _lan_ip(), 'local_ip': '127.0.0.1', 'port': 1080}

    def _ensure_v2_stats(self, cfg, name):
        """为 v2ray 配置注入流量统计(api+stats+policy.system+routing), 幂等。"""
        cfg = dict(cfg)
        cfg['stats'] = {}
        cfg['policy'] = {'system': {
            'statsInboundUplink': True, 'statsInboundDownlink': True,
            'statsOutboundUplink': True, 'statsOutboundDownlink': True}}
        cfg['api'] = {'tag': 'api', 'services': ['StatsService']}
        inbounds = list(cfg.get('inbounds') or [])
        if not any(str(i.get('tag')) == 'api' for i in inbounds):
            inbounds.append({'tag': 'api', 'listen': '127.0.0.1',
                             'port': self._v2_api_port(name),
                             'protocol': 'dokodemo-door',
                             'settings': {'address': '127.0.0.1'}})
        cfg['inbounds'] = inbounds
        rules = list((cfg.get('routing') or {}).get('rules') or [])
        if not any(r.get('type') == 'field' and 'api' in (r.get('inboundTag') or []) for r in rules):
            rules.append({'type': 'field', 'inboundTag': ['api'], 'outboundTag': 'api'})
        cfg['routing'] = {'rules': rules}
        return cfg

    def _query_v2_stats(self, name):
        """gRPC 查询运行中 v2ray 的累计上行/下行字节 (排除 api 自身统计)。"""
        if not _GRPC_OK:
            return None
        port = self._v2_api_port(name)
        try:
            ch_ = _grpc.insecure_channel('127.0.0.1:%d' % port,
                                         options=[('grpc.enable_http_proxy', 0)])
            stub = _spbgrpc.StatsServiceStub(ch_)
            r = stub.QueryStats(_spb.QueryStatsRequest(pattern='', reset=False), timeout=4)
            up = down = 0
            for s in r.stat:
                if s.name.startswith('inbound>>>api>>>'):
                    continue
                if s.name.endswith('>>>traffic>>>uplink'):
                    up += s.value
                elif s.name.endswith('>>>traffic>>>downlink'):
                    down += s.value
            return {'up': up, 'down': down}
        except Exception:
            return None

    def _query_singbox_stats(self, name):
        """经 ss 采样 sing-box 出站 TCP 连接的累计 rx/tx 字节 (无需 v2ray_api 编译tag)。"""
        try:
            r = _sudo(['bash', '-c', "systemctl show rcvpn-singbox-%s.service -p MainPID --value" % name],
                      timeout=20)
            pid = (r['out'] or '').strip()
            if not pid or pid == '0':
                r = _sudo(['bash', '-c', "pgrep -f 'sing-box run -c.*%s' | head -1" % name], timeout=20)
                pid = (r['out'] or '').strip()
            if not pid:
                return None
            script = (
                "import re,subprocess,sys\n"
                "pid='%s'\n"
                "out=subprocess.run(['ss','-tinp'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout.decode('utf-8','replace')\n"
                "lines=out.splitlines()\n"
                "rx=tx=0\n"
                "for i,l in enumerate(lines):\n"
                "  if not l.startswith('ESTAB'):\n"
                "    continue\n"
                "  if ('pid='+pid) not in l:\n"
                "    continue\n"
                "  toks=l.split()\n"
                "  if len(toks)<5:\n"
                "    continue\n"
                "  try:\n"
                "    lport=int(toks[3].rsplit(':',1)[1])\n"
                "  except Exception:\n"
                "    continue\n"
                "  if lport==1080:\n"
                "    continue\n"
                "  for j in range(i+1,min(i+3,len(lines))):\n"
                "    info=lines[j]\n"
                "    m=re.search(r'bytes_received:(\\d+)',info)\n"
                "    a=re.search(r'bytes_acked:(\\d+)',info)\n"
                "    if m: rx+=int(m.group(1))\n"
                "    if a: tx+=int(a.group(1))\n"
                "    if lines[j].startswith('ESTAB') and j>i: break\n"
                "sys.stdout.write('%%d %%d' %% (rx,tx))\n"
            ) % pid
            r = _sudo(['bash', '-c', "echo 1 | sudo -S python3 -c \"%s\"" % script.replace('"', '\\"')],
                      timeout=40)
            parts = (r['out'] or '').strip().split()
            if len(parts) == 2:
                return {'down': int(parts[0]), 'up': int(parts[1])}
            return None
        except Exception:
            return None

    def _active_path(self, name):
        return os.path.join(DATA_DIR, 'active_%s.json' % name)

    def _set_active(self, name, label):
        try:
            with open(self._active_path(name), 'w', encoding='utf-8') as f:
                json.dump({'node': label}, f, ensure_ascii=False)
        except Exception:
            pass

    def _get_active(self, name):
        try:
            with open(self._active_path(name), 'r', encoding='utf-8') as f:
                return (json.load(f) or {}).get('node')
        except Exception:
            return None

    def _node_label(self, node):
        return '%s:%s' % (node.get('protocol'), node.get('name') or node.get('addr') or 'node')

    @staticmethod
    def _proc_net_rx_tx(iface):
        """返回指定接口累计 rx/tx 字节; 接口不存在返回 None。"""
        try:
            with open('/proc/net/dev', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(iface + ':'):
                        parts = line.split()
                        return int(parts[1]), int(parts[9])  # rx, tx
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # sing-box 引擎 (anytls / hysteria2 / tuic / ssr)
    # ------------------------------------------------------------------
    _SINGBOX_PROTOS = ('anytls', 'hysteria2', 'tuic', 'ssr')

    def _sb_bin(self):
        return shutil.which('sing-box') or ('/usr/local/bin/sing-box'
                                            if os.path.isfile('/usr/local/bin/sing-box') else None)

    def _sb_conf_dir(self):
        d = os.path.join(DATA_DIR, 'singbox')
        os.makedirs(d, exist_ok=True)
        return d

    def _engine_for(self, proto):
        if proto in self._SINGBOX_PROTOS:
            return 'sing-box' if self._sb_bin() else 'sing-box-missing'
        return 'v2ray'

    def _singbox_outbound(self, proto, d):
        addr = str(d.get('addr') or '').strip() or str(d.get('address') or '').strip()
        port = int(d.get('port') or 0)
        if not addr or not port:
            return None
        sni = d.get('sni') or d.get('host') or addr
        insecure = bool(d.get('allowInsecure'))
        if proto == 'hysteria2':
            out = {'type': 'hysteria2', 'tag': 'out', 'server': addr, 'server_port': port,
                   'password': d.get('password', ''),
                   'tls': {'enabled': True, 'server_name': sni, 'insecure': insecure}}
            obfs_type = (d.get('obfs') or '').strip()
            if obfs_type and obfs_type.lower() != 'none' and d.get('obfs_password'):
                out['obfs'] = {'type': obfs_type, 'password': d.get('obfs_password', '')}
            return out
        if proto == 'anytls':
            return {'type': 'anytls', 'tag': 'out', 'server': addr, 'server_port': port,
                    'password': d.get('uuid') or d.get('password', ''),
                    'tls': {'enabled': True, 'server_name': sni, 'insecure': insecure}}
        if proto == 'tuic':
            return {'type': 'tuic', 'tag': 'out', 'server': addr, 'server_port': port,
                    'uuid': d.get('uuid', ''), 'password': d.get('password', ''),
                    'congestion_control': d.get('congestion') or 'cubic',
                    'tls': {'enabled': True, 'server_name': sni, 'insecure': insecure,
                            'alpn': ['h3']}}
        if proto == 'ssr':
            return {'type': 'shadowsocksr', 'tag': 'out', 'server': addr, 'server_port': port,
                    'method': d.get('cipher', 'aes-256-cfb'), 'password': d.get('password', ''), }
        return None

    def _singbox_config(self, out, port, bind=None, stats=False, name=None):
        cfg = {'log': {'level': 'warn'},
               'inbounds': [{'type': 'socks', 'tag': 'socks-in',
                             'listen': bind if bind is not None else self._proxy_bind(),
                             'listen_port': int(port)}],
               'outbounds': [out, {'type': 'direct', 'tag': 'direct'}],
               'route': {'final': 'out'}}
        if stats and name:
            cfg['experimental'] = {'v2ray_api': {
                'listen': '127.0.0.1:%d' % self._v2_api_port(name),
                'stats': {'enabled': True,
                          'inbounds': ['socks-in'],
                          'outbounds': ['out', 'direct']}}}
        return cfg

    def _ensure_singbox_unit(self, name, port):
        unit = 'rcvpn-singbox-%s.service' % name
        binp = self._sb_bin()
        cfg_path = os.path.join(self._sb_conf_dir(), name + '.json')
        body = ['[Unit]\nDescription=RainCough sing-box %s\nAfter=network-online.target\nWants=network-online.target\n'
                '\n[Service]\nType=simple\nRestart=always\nRestartSec=3\n'
                'ExecStart=%s run -c %s\n'
                '\n[Install]\nWantedBy=multi-user.target\n' % (name, binp, cfg_path)]
        _write_unit(unit, body)

    def _connect_singbox(self, name, node, port):
        out = self._singbox_outbound(node.get('protocol'), node)
        if not out:
            return {'error': '无法为该节点构建 sing-box 配置'}
        if not self._sb_bin():
            return {'error': 'sing-box 未安装'}
        cfg = self._singbox_config(out, port, stats=False, name=name)
        cfg_path = os.path.join(self._sb_conf_dir(), name + '.json')
        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        self._ensure_singbox_unit(name, port)
        _unit_action('rcvpn-v2ray-%s.service' % name, 'stop', timeout=15)
        r = _unit_action('rcvpn-singbox-%s.service' % name, 'restart')
        self._set_active(name, self._node_label(node))
        return {'name': name, 'summary': {'protocol': node.get('protocol'),
                                          'address': node.get('addr'), 'port': node.get('port'),
                                          'engine': 'sing-box'}, 'mode': self._mode_status(), **r}

    def _singbox_running_names(self):
        r = _sudo(['bash', '-c', "systemctl --no-pager list-units --type=service --all "
                                 "| grep rcvpn-singbox | grep ' active ' || true"], timeout=30)
        names = []
        for line in (r['out'] or '').splitlines():
            m = re.search(r'rcvpn-singbox-([A-Za-z0-9_-]+)\.service', line)
            if m:
                names.append(m.group(1))
        return names

    def _run_singbox_probe(self, node, target, port=10809, duration=0):
        """临时起 sing-box 测延迟/带宽; duration>0 用 speedtest 逻辑, 否则延迟。"""
        out = self._singbox_outbound(node.get('protocol'), node)
        if not out:
            return {'ok': False, 'error': '无法构建 sing-box 配置'}
        if not self._sb_bin():
            return {'ok': False, 'error': 'sing-box 未安装'}
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(self._singbox_config(out, port, bind='127.0.0.1'), f, ensure_ascii=False, default=str)
            path = f.name
        proc = subprocess.Popen([self._sb_bin(), 'run', '-c', path],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = {'ok': False, 'error': '启动失败'}
        try:
            time.sleep(2.0)
            if duration:
                r = subprocess.run(['curl', '-s', '--max-time', str(duration + 8), '-x',
                                    'socks5h://127.0.0.1:%d' % port, '-o', '/dev/null',
                                    '-w', '%{size_download} %{time_starttransfer} %{time_total}',
                                    SPEED_URL], capture_output=True, timeout=duration + 15)
                parts = r.stdout.decode('utf-8', 'replace').split()
                if len(parts) == 3 and int(parts[0]) > 0:
                    size, startt, totalt = int(parts[0]), float(parts[1]), float(parts[2])
                    mb = size / 1048576.0
                    result = {'ok': True, 'ms': int(startt * 1000),
                              'mbps': round(mb / totalt * 8, 2), 'mbs': round(mb / totalt, 2),
                              'bytes': size}
                else:
                    result = {'ok': False, 'error': '代理不可用, 无数据返回'}
            else:
                s = time.time()
                r = subprocess.run(['curl', '-s', '-m', '12', '-x',
                                    'socks5h://127.0.0.1:%d' % port, '-o', '/dev/null',
                                    '-w', '%{time_starttransfer}', target],
                                   capture_output=True, timeout=15)
                raw = r.stdout.decode('utf-8', 'replace').strip()
                if r.returncode == 0 and raw and raw != '0.000000':
                    result = {'ok': True, 'ms': int(float(raw) * 1000), 'latency': int(float(raw) * 1000)}
                else:
                    result = {'ok': False, 'error': (r.stderr.decode('utf-8', 'replace') or '代理不可用')[:200]}
        except Exception as e:
            result = {'ok': False, 'error': str(e)[:200]}
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                os.remove(path)
            except Exception:
                pass
        return result

    def _run_v2_speedtest(self, cfg, duration=5):
        """临时起该节点 v2ray,经 curl 代理下载固定大文件,测真实下行带宽(MB/s)。"""
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            dur = dict(cfg)
            dur['inbounds'] = [{'tag': 'probe-in', 'listen': '127.0.0.1',
                                'port': 10809, 'protocol': 'socks'}]
            json.dump(dur, f, ensure_ascii=False, default=str)
            path = f.name
        binp = shutil.which('v2ray') or shutil.which('xray') or '/usr/bin/v2ray'
        proc = subprocess.Popen([binp, '-config', path],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = {'ok': False, 'error': '启动失败'}
        try:
            time.sleep(2.5)
            r = subprocess.run(
                ['curl', '-s', '--max-time', str(duration + 8), '-x',
                 'socks5h://127.0.0.1:10809', '-o', '/dev/null',
                 '-w', '%{size_download} %{time_starttransfer} %{time_total}', SPEED_URL],
                capture_output=True, timeout=duration + 15)
            parts = r.stdout.decode('utf-8', 'replace').split()
            if len(parts) == 3:
                size, startt, totalt = int(parts[0]), float(parts[1]), float(parts[2])
                if size > 0 and totalt > 0:
                    mb = size / 1048576.0
                    result = {'ok': True, 'ms': int(startt * 1000),
                              'mbps': round(mb / totalt * 8, 2),
                              'mbs': round(mb / totalt, 2),
                              'bytes': size}
                else:
                    result = {'ok': False, 'error': '代理不可用, 无数据返回'}
            else:
                result = {'ok': False, 'error': (r.stderr.decode('utf-8', 'replace') or '下载失败')[:200]}
        except Exception as e:
            result = {'ok': False, 'error': str(e)[:200]}
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                os.remove(path)
            except Exception:
                pass
        return result

    def _ping_host(self, host, count=4):
        """直接 ping 节点地址, 返回 {ok, ms(平均RTT)}。"""
        host = (str(host or '')).strip()
        if not host:
            return {'ok': False, 'error': '无节点地址'}
        r = _sudo(['ping', '-c', str(count), '-W', '1', host], timeout=20)
        out = (r['out'] or '') + (r['err'] or '')
        # iputils: rtt min/avg/max/mdev = x/y/z/w ms
        m = re.search(r'= \d+\.?\d*/(\d+\.?\d*)/\d+\.?\d*/\d+\.?\d*\s+ms', out)
        if m:
            return {'ok': True, 'ms': int(round(float(m.group(1))))}
        # 老版本: round-trip min/avg/max = x/y/z ms
        m2 = re.search(r'= (\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)\s+ms', out)
        if m2:
            return {'ok': True, 'ms': int(round(float(m2.group(2))))}
        return {'ok': False, 'error': 'ping 失败 (节点不可达)'}

    def _run_v2_probe(self, cfg, target):
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            dur = dict(cfg)
            dur['inbounds'] = [{'tag': 'probe-in', 'listen': '127.0.0.1',
                                'port': 10809, 'protocol': 'socks'}]
            json.dump(dur, f, ensure_ascii=False)
            path = f.name
        binp = shutil.which('v2ray') or shutil.which('xray') or '/usr/bin/v2ray'
        proc = subprocess.Popen([binp, '-config', path],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = {}
        try:
            time.sleep(2.0)
            s = time.time()
            try:
                r = subprocess.run(['curl', '-s', '-m', '12', '-x',
                                    'socks5h://127.0.0.1:10809', '-o', '/dev/null',
                                    '-w', '%{time_starttransfer}', target],
                                   capture_output=True, timeout=15)
                raw = r.stdout.decode('utf-8', 'replace').strip()
                ok = r.returncode == 0 and raw and raw != '0.000000'
                if not ok:
                    # 目标可能返回 JSON/IP 文本时也用 -w 仍为 xx; 尝试读 body
                    r2 = subprocess.run(['curl', '-s', '-m', '12', '-x',
                                         'socks5h://127.0.0.1:10809', target],
                                        capture_output=True, timeout=15)
                    raw2 = r2.stdout.decode('utf-8', 'replace').strip()
                    if raw2 and ('://' in raw2 or '.' in raw2):
                        body = raw2
                        ok = True
                if ok:
                    try:
                        latency_ms = int(float(raw) * 1000)
                    except Exception:
                        latency_ms = int((time.time() - s) * 1000)
                    result = {'ok': True, 'ms': latency_ms, 'latency': latency_ms,
                              'exit_ip': ''}
                else:
                    err = (r.stderr.decode('utf-8', 'replace') or '代理不可用').strip()
                    result = {'ok': False, 'error': err[:200]}
            except Exception as e:
                result = {'ok': False, 'error': str(e)[:200]}
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                os.remove(path)
            except Exception:
                pass
        return result

    def _wizard_outbound(self, proto, d):
        addr = str(d.get('address', '')).strip() or str(d.get('addr', '')).strip()
        port = int(d.get('port', 0))
        if not addr or not port:
            return None
        if proto == 'vmess':
            out = {'protocol': 'vmess', 'tag': 'out', 'settings': {'vnext': [{
                'address': addr, 'port': port,
                'users': [{'id': d.get('uuid', ''), 'alterId': int(d.get('alterId', 0)),
                           'security': d.get('security', 'auto')}]}]}}
            self._tag_net(out, d)
            return out
        if proto == 'vless':
            out = {'protocol': 'vless', 'tag': 'out', 'settings': {'vnext': [{
                'address': addr, 'port': port,
                'users': [{'id': d.get('uuid', ''), 'encryption': 'none',
                           'flow': d.get('flow', '')}]}]}}
            self._tag_net(out, d)
            return out
        if proto == 'trojan':
            out = {'protocol': 'trojan', 'tag': 'out', 'settings': {'servers': [{
                'address': addr, 'port': port, 'password': d.get('password', ''),
                'flow': d.get('flow', '')}]}}
            self._tag_net(out, d)
            return out
        if proto == 'ss':
            out = {'protocol': 'shadowsocks', 'tag': 'out',
                   'settings': {'servers': [{'address': addr, 'port': port,
                                             'method': d.get('cipher', 'aes-256-gcm'),
                                             'password': d.get('password', '')}]}}
            return out
        return None

    def _tag_net(self, out, d):
        net = d.get('network', '').lower()
        tls = d.get('tls')
        sock = {'network': net}
        if net == 'ws':
            sock['settings'] = {'path': d.get('path', '/'), 'headers': {
                'Host': d.get('host', d.get('sni', ''))}}
        elif net == 'grpc':
            sock['settings'] = {'serviceName': d.get('path', '')}
        elif net == 'httpupgrade':
            sock['settings'] = {'path': d.get('path', '/'), 'host': d.get('host', '')}
        if tls:
            stream = {'network': net, 'security': 'tls', 'tlsSettings': {
                'serverName': d.get('sni') or d.get('host', ''),
                'allowInsecure': bool(d.get('allowInsecure'))}}
            stream.update(sock)
        else:
            stream = {'network': net}
            stream.update(sock)
        if 'reality' in (d.get('security') or '').lower() or d.get('reality'):
            stream['security'] = 'reality'
            stream['realitySettings'] = {
                'serverName': d.get('sni', ''), 'fingerprint': d.get('fp', 'chrome'),
                'show': False, 'publicKey': d.get('pbk', ''),
                'shortId': d.get('sidx', ''), 'spiderX': d.get('spx', '/'),
            }
        out['streamSettings'] = stream

    def _outbound_summary(self, out):
        p = out.get('protocol')
        base = out.get('settings', {})
        srv = {}
        if p in ('vmess', 'vless'):
            srv = (base.get('vnext') or [{}])[0]
        elif p == 'trojan':
            srv = (base.get('servers') or [{}])[0]
        elif p == 'shadowsocks':
            srv = (base.get('servers') or [{}])[0]
        net = (out.get('streamSettings') or {}).get('network', 'tcp')
        sec = (out.get('streamSettings') or {}).get('security', 'none')
        return {'protocol': p, 'address': srv.get('address'), 'port': srv.get('port'),
                'network': net, 'security': sec,
                'sni': ((out.get('streamSettings') or {}).get('tlsSettings') or {}).get('serverName')}

    def _fetch_sub(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (RainCough) /1.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as r2:
                raw = r2.read().decode('utf-8', 'replace')
        except Exception as e:
            return [], '拉取失败: %s' % str(e)[:150], False
        text = raw
        stripped = re.sub(r'\s+', '', text)
        if not stripped:
            return [], '内容为空', False
        if '://' not in text:
            try:
                dec = base64.b64decode(re.sub(r'[^0-9A-Za-z+/=]', '', text) + '==').decode('utf-8', 'replace')
                if '://' in dec:
                    text = dec
            except Exception:
                pass
        nodes = []
        for line in text.splitlines():
            line = line.strip()
            if not line or '://' not in line:
                continue
            node = self._parse_link(line)
            if node:
                nodes.append(node)
        return nodes, None, True

    def _parse_link(self, link):
        try:
            scheme = link.split('://', 1)[0].lower()
            if scheme == 'vmess':
                node = self._parse_vmess(link)
            elif scheme in ('vless', 'trojan', 'ss', 'ssr',
                            'anytls', 'hysteria2', 'tuic', 'hysteria', 'wireguard'):
                node = self._parse_url(link)
            else:
                return None
            if not node or not node.get('addr'):
                return None
            addr = str(node['addr'])
            if addr in ('127.0.0.1', '0.0.0.0', '::1', 'localhost') or addr.startswith('127.'):
                return None
            node['_id'] = '%s-%s-%d' % (node['protocol'], node['addr'], int(node.get('port', 0)))
            return node
        except Exception:
            return None

    def _b64(self, s):
        try:
            s2 = re.sub(r'\s+', '', s)
            s2 = s2.replace('-', '+').replace('_', '/')
            return base64.b64decode(s2 + '=' * (-len(s2) % 4)).decode('utf-8', 'replace')
        except Exception:
            return None

    def _parse_vmess(self, link):
        payload = link.split('://', 1)[1]
        if '@' in payload and len(payload.split('@')[0]) > 40:
            cfg = self._b64(payload.split('@')[0])
            host = payload.split('@')[1]
        else:
            cfg = self._b64(payload)
            host = None
        data = {}
        if cfg:
            try:
                data = json.loads(cfg)
            except Exception:
                data = {}
        if not data:
            # 旧格式 vmess:// base64(host:port/...)? 尝试 "add:port"
            return {'protocol': 'vmess', 'name': link[:40], 'addr': host or '',
                    'port': 0, 'engine': 'v2ray', 'engine_support': True}
        if data.get('add'):
            data['addr'] = data['add']
            data['port'] = data['port']
        name = data.get('ps') or ('%s:%s' % (data.get('addr', ''), data.get('port', '')))
        return {'protocol': 'vmess', 'name': name, 'addr': data.get('addr', ''),
                'port': int(data.get('port', 0) or 0), 'uuid': data.get('id', ''),
                'alterId': int(data.get('aid', 0) or 0),
                'security': data.get('scy', 'auto'),
                'network': data.get('net', 'tcp'), 'path': data.get('path', ''),
                'host': data.get('host', ''), 'tls': data.get('tls', ''),
                'sni': data.get('sni', '') or data.get('host', ''),
                'allowInsecure': bool(str(data.get('n', '')).lower() == '1'),
                'engine': 'v2ray', 'engine_support': True}

    def _parse_url(self, link):
        scheme, rest = link.split('://', 1)
        frag = rest.split('#', 1)
        body = frag[0]
        name = urllib.parse.unquote(frag[1]) if len(frag) > 1 else ''
        if scheme == 'ssr':
            try:
                dec = self._b64(body.split('#')[0].split('/?')[0])
            except Exception:
                dec = self._b64(body)
            return {'protocol': 'ssr', 'name': name or (dec or body)[:40],
                    'addr': '', 'port': 0, 'engine': 'v2ray', 'engine_support': False,
                    'raw': dec or body}
        if scheme == 'ss':
            # ss://method:pass@host:port#name
            m = re.match(r'^(?:[A-Za-z0-9_+\-/=]+)@([^:]+):(\d+)$', body)
            if m:
                addr, port = m.group(1), m.group(2)
                cred = self._b64(body.split('@')[0]) or body.split('@')[0]
                return {'protocol': 'ss', 'name': name or ('%s:%s' % (addr, port)),
                        'addr': addr, 'port': int(port), 'engine': 'v2ray', 'engine_support': True,
                        'password': cred.split(':')[1], 'cipher': cred.split(':')[0]}
            # ss://base64(method:pass@host:port)#name  (带 插件 plugin)
            try:
                dec = self._b64(body.split('/?')[0])
            except Exception:
                dec = self._b64(body)
            if dec and '@' in dec:
                hostpart = dec.split('@')[1]
                addr = hostpart.split(':')[0]
                port = hostpart.split(':')[1].split()[0]
                cred = dec.split('@')[0].split(':')
                return {'protocol': 'ss', 'name': name or ('%s:%s' % (addr, port)),
                        'addr': addr, 'port': int(port or 0), 'engine': 'v2ray', 'engine_support': True,
                        'cipher': cred[0], 'password': cred[1],
                        'plugin': body.split('/?')[1] if '/?' in body else None}
            return None
        # vless / trojan 统一 URL 解析 (userinfo@host:port?params#name)
        hostpart = body.split('#', 1)[0].split('?', 1)[0]
        ident = ''
        if '@' in hostpart:
            ident, hostpart = hostpart.split('@', 1)
        if ':' not in hostpart:
            return None
        addr, port_s = hostpart.rsplit(':', 1)
        addr = addr.strip('[]')
        try:
            port = int(port_s)
        except (TypeError, ValueError):
            return None
        qs = {}
        if '?' in body:
            qs = dict(urllib.parse.parse_qsl(body.split('?', 1)[1].split('#', 1)[0]))
        node = {'protocol': scheme, 'name': name or ('%s:%s' % (addr, port)),
                'addr': addr, 'port': port, 'engine': 'v2ray',
                'engine_support': scheme in ('vless', 'trojan')}
        if scheme == 'vless':
            node['uuid'] = ident
            node['flow'] = qs.get('flow', '')
        elif scheme == 'trojan':
            node['password'] = ident
            node['flow'] = qs.get('flow', '')
        elif scheme == 'anytls':
            node['uuid'] = ident
            node['password'] = qs.get('password', '')
            node['flow'] = qs.get('flow', '')
        elif scheme == 'hysteria2':
            node['password'] = ident
            node['obfs'] = qs.get('obfs', '')
            node['obfs_password'] = qs.get('obfs-password', '')
        elif scheme == 'tuic':
            ident = ident.split(':', 1)
            if len(ident) == 2:
                node['uuid'], node['password'] = ident[0], ident[1]
            else:
                node['uuid'] = ident[0]
                node['password'] = ''
            node['congestion'] = qs.get('congestion', '')
        elif scheme == 'wireguard':
            node['password'] = ''
        node['security'] = qs.get('security', 'none')
        node['tls'] = qs.get('security', '')
        node['sni'] = qs.get('sni', '') or qs.get('host', '')
        node['fp'] = qs.get('fp', '')
        node['pbk'] = qs.get('pbk', '')
        node['sidx'] = qs.get('sid', '')
        node['spx'] = qs.get('spx', '/')
        node['network'] = qs.get('type', qs.get('network', 'tcp'))
        node['path'] = qs.get('path', '')
        node['host'] = qs.get('host', '')
        node['allowInsecure'] = qs.get('allowInsecure', '').lower() == '1'
        return node

    # ---- 总览 ----
    def _routes_overview(self):
        @self.route('/overview', methods=['GET'])
        def overview():
            try:
                direct_ip = _host_ip()
            except Exception:
                direct_ip = None
            wg = self._wg_status()
            ovpn = self._ovpn_running()
            v2r = self._v2_running() or 'none'
            # 出网检测: 尝试经任意已运行 v2ray socks 端口 (1080)
            proxied = None
            try:
                import urllib.request
                proxy = urllib.request.ProxyHandler({'http': 'socks5h://127.0.0.1:1080',
                                                     'https': 'socks5h://127.0.0.1:1080'})
                op = urllib.request.build_opener(proxy)
                with op.open('https://api.ipify.org', timeout=8) as rp:
                    proxied = rp.read().decode('utf-8', 'replace').strip()
            except Exception:
                pass
            return jsonify({
                'direct_ip': direct_ip,
                'proxy_ip': proxied,
                'wireguard': {'running': wg.get('running', []),
                              'interfaces': len(wg.get('interfaces', []))},
                'openvpn': {'running': bool(ovpn), 'detail': ovpn[:300]},
                'v2ray': {'detail': (v2r or 'none')[:300]},
                'channels_active': {
                    'wireguard': len(wg.get('running', [])) > 0,
                    'openvpn': bool(ovpn),
                    'v2ray': 'rcvpn-v2ray' in v2r or bool(self._singbox_running_names()),
                },
            })

        @self.route('/logs', methods=['GET'])
        def logs():
            tech = request.args.get('tech', '')
            pat = {'wg': 'wg-quick', 'ovpn': 'openvpn', 'v2': 'rcvpn-v2ray',
                   'v2ray': 'rcvpn-v2ray'}.get(tech, '')
            return jsonify({'log': _log_tail(pat) if pat else ''})

        @self.route('/overview/live', methods=['GET'])
        def overview_live():
            now = time.time()
            cache = getattr(self, '_traffic_cache', None)
            if cache is None:
                cache = self._traffic_cache = {}

            def rate(k, up, down, ts=None):
                ts = ts if ts is not None else now
                prev = cache.get(k)
                cache[k] = {'up': up, 'down': down, 'ts': ts}
                if not prev or ts <= prev['ts']:
                    return 0, 0
                dt = ts - prev['ts']
                return (int((down - prev['down']) / dt) if down >= prev['down'] else 0,
                        int((up - prev['up']) / dt) if up >= prev['up'] else 0)

            v2 = {'running': False, 'node': None, 'total_up': 0, 'total_down': 0,
                  'down_bps': 0, 'up_bps': 0, 'active': False}
            for name in self._running_v2_names():
                stats = self._query_v2_stats(name)
                if stats is None:
                    continue
                try:
                    with open(os.path.join(self._v2_conf_dir(), name + '.json'), 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                except Exception:
                    cfg = {}
                ob = (cfg.get('outbounds') or [{}])[0]
                tag = ob.get('tag') or ''
                if tag in ('out', 'proxy', 'direct', 'freedom', ''):
                    node = name
                else:
                    node = tag
                db, ub = rate('v2:' + name, stats['up'], stats['down'])
                v2 = {'running': True, 'node': node,
                      'total_up': stats['up'], 'total_down': stats['down'],
                      'down_bps': db, 'up_bps': ub, 'active': True, 'engine': 'v2ray'}
                break

            if not v2['running']:
                for _sb in self._singbox_running_names():
                    stats = self._query_singbox_stats(_sb)  # ss 采样出站连接字节
                    label = self._get_active(_sb) or 'sing-box: %s' % _sb
                    if stats:
                        db, ub = rate('sb:' + _sb, stats['up'], stats['down'])
                        v2 = {'running': True, 'node': label,
                              'total_up': stats['up'], 'total_down': stats['down'],
                              'down_bps': db, 'up_bps': ub, 'active': True, 'engine': 'sing-box'}
                    else:
                        v2 = {'running': True, 'node': label, 'total_up': 0,
                              'total_down': 0, 'down_bps': 0, 'up_bps': 0, 'active': True,
                              'engine': 'sing-box'}
                    break

            wg = {'running': [], 'total_up': 0, 'total_down': 0, 'down_bps': 0, 'up_bps': 0}
            for iface in self._wg_running():
                r = self._proc_net_rx_tx(iface)
                wg['running'].append(iface)
                if r is None:
                    continue
                rx, tx = r
                wg['total_down'] += rx
                wg['total_up'] += tx
                db, ub = rate('wg:' + iface, tx, rx)
                wg['down_bps'] += db
                wg['up_bps'] += ub

            ovpn = {'running': False, 'iface': None, 'total_up': 0, 'total_down': 0,
                    'down_bps': 0, 'up_bps': 0}
            if self._ovpn_running():
                ovpn['running'] = True
                for line in self._ovpn_ifaces():
                    r = self._proc_net_rx_tx(line)
                    if r is None:
                        continue
                    rx, tx = r
                    ovpn['iface'] = line
                    ovpn['total_down'] += rx
                    ovpn['total_up'] += tx
                    db, ub = rate('ovpn:' + line, tx, rx)
                    ovpn['down_bps'] += db
                    ovpn['up_bps'] += ub

            def nf(v):
                return int(max(v, 0))

            return jsonify({
                'ts': int(now),
                'v2ray': {**v2, 'total_up': nf(v2['total_up']), 'total_down': nf(v2['total_down'])},
                'wireguard': {**wg, 'total_up': nf(wg['total_up']), 'total_down': nf(wg['total_down'])},
                'openvpn': {**ovpn, 'total_up': nf(ovpn['total_up']), 'total_down': nf(ovpn['total_down'])},
            })

        @self.route('/stop-all', methods=['POST'])
        def stop_all():
            out = {}
            r1 = _sudo(['bash', '-c', "for f in /etc/systemd/system/rcvpn-*.service; do "
                                      "systemctl --no-pager stop $(basename $f) 2>/dev/null; done"], timeout=60)
            out['systemd'] = r1.get('ok')
            for iface in self._wg_running():
                _sudo(['wg-quick', 'down', iface], timeout=40)
            out['stopped_wg'] = self._wg_running()
            return jsonify({'ok': True, 'stopped': out})


_plugin = VpnPlugin()