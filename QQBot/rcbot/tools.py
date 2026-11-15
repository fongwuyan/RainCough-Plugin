# -*- coding: utf-8 -*-
"""工具链：系统内置工具 + 受限工作区。

设计约束（按需求）：
  · 只做系统内置工具，不开放自定义 HTTP / shell
  · 工作区初始为空，AI 只能在这个目录里读写，不能碰面板其它路径
  · 另外一类是只读辅助工具（联网搜索、当前时间）
"""
import ast
import base64
import hashlib
import json
import math
import operator
import os
import random as _random
import re
import time
from collections import deque
from datetime import date, timedelta
import threading

from . import config, logbuf, search

MAX_FILE = 256 * 1024          # 单个文件 256KB
DEFAULT_QUOTA_MB = 20


def cfg_dir():
    return os.path.dirname(os.path.abspath(config.CFG_FILE))


def ws_root():
    d = os.path.join(cfg_dir(), 'workspace')
    os.makedirs(d, exist_ok=True)
    return os.path.realpath(d)


def _safe(rel=''):
    root = ws_root()
    rel = str(rel or '').strip().replace('\\', '/')
    rel = rel.lstrip('/')
    p = os.path.realpath(os.path.join(root, rel))
    if p != root and not p.startswith(root + os.sep):
        raise RuntimeError('路径超出工作区')
    return p


def rel_of(p):
    root = ws_root()
    if p == root:
        return ''
    return os.path.relpath(p, root).replace('\\', '/')


def _quota_bytes(cfg=None):
    t = (cfg or config.load()).get('tools') or {}
    mb = int((t.get('workspace') or {}).get('max_mb') or DEFAULT_QUOTA_MB)
    return max(1, mb) * 1024 * 1024


def usage():
    root = ws_root()
    files = 0
    total = 0
    for dirpath, _dirs, names in os.walk(root):
        for n in names:
            try:
                st = os.stat(os.path.join(dirpath, n))
                files += 1
                total += st.st_size
            except Exception:
                pass
    return {'root': root, 'files': files, 'bytes': total}


def list_dir(rel=''):
    p = _safe(rel)
    if not os.path.isdir(p):
        raise RuntimeError('不是目录')
    items = []
    for n in sorted(os.listdir(p)):
        fp = os.path.join(p, n)
        try:
            st = os.stat(fp)
            items.append({'name': n, 'is_dir': os.path.isdir(fp), 'size': st.st_size,
                          'mtime': int(st.st_mtime)})
        except Exception:
            continue
    return {'path': rel_of(p), 'items': items}


def read_text(rel, limit=MAX_FILE):
    p = _safe(rel)
    if not os.path.isfile(p):
        raise RuntimeError('文件不存在')
    size = os.path.getsize(p)
    if size > limit:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            data = f.read(limit)
        return {'path': rel_of(p), 'content': data, 'truncated': True, 'size': size}
    with open(p, 'r', encoding='utf-8', errors='replace') as f:
        return {'path': rel_of(p), 'content': f.read(), 'truncated': False, 'size': size}


def write_text(rel, content, cfg=None):
    p = _safe(rel)
    if os.path.isdir(p):
        raise RuntimeError('目标是目录')
    data = str(content or '').encode('utf-8')
    if len(data) > MAX_FILE:
        raise RuntimeError('单个文件不能超过 %dKB' % (MAX_FILE // 1024))
    used = usage()['bytes']
    old = os.path.getsize(p) if os.path.isfile(p) else 0
    if used - old + len(data) > _quota_bytes(cfg):
        raise RuntimeError('工作区已满（上限 %dMB）' % (int((cfg or config.load())
                                                    .get('tools', {}).get('workspace', {})
                                                    .get('max_mb') or DEFAULT_QUOTA_MB)))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(str(content or ''))
    return {'path': rel_of(p), 'size': len(data)}


def mkdir(rel):
    p = _safe(rel)
    os.makedirs(p, exist_ok=True)
    return {'path': rel_of(p)}


def delete(rel):
    p = _safe(rel)
    if p == ws_root():
        raise RuntimeError('不能删除工作区根目录')
    if os.path.isdir(p):
        import shutil
        shutil.rmtree(p)
    elif os.path.isfile(p):
        os.remove(p)
    else:
        raise RuntimeError('路径不存在')
    return {'path': rel_of(p)}


# ---------------------------------------------------------------- 工具定义

def _fn(name, desc, props=None, required=None):
    return {
        'type': 'function',
        'function': {
            'name': name,
            'description': desc,
            'parameters': {
                'type': 'object',
                'properties': props or {},
                'required': required or [],
            },
        },
    }


TOOLS = [
    {
        'id': 'web_search', 'name': '联网搜索', 'category': 'aux',
        'desc': '搜索互联网获取实时信息（新闻、价格、天气等）',
        'schema': _fn('web_search',
                      '搜索互联网获取实时信息。遇到新闻、价格、天气、赛事或不确定的事实时使用。',
                      {'query': {'type': 'string', 'description': '搜索关键词'}}, ['query']),
    },
    {
        'id': 'now', 'name': '当前时间', 'category': 'aux',
        'desc': '获取服务器当前日期与时间',
        'schema': _fn('now', '获取当前日期、时间与星期。涉及“今天/现在”的问题先调用它。'),
    },
    {
        'id': 'calc', 'name': '高级计算器', 'category': 'aux',
        'desc': '安全求值数学表达式（三角函数、对数、阶乘、取余、幂等）',
        'schema': _fn(
            'calc',
            '计算数学表达式并返回结果。支持 + - * / // % **、括号、sqrt/sin/cos/tan/'
            'asin/acos/atan/log/log10/log2/exp/abs/round/floor/ceil/factorial/min/max/gcd，'
            '常量 pi、e、tau。例如 "sqrt(2)*10"、"factorial(6)/2"、"log(1000,10)"。',
            {'expression': {'type': 'string', 'description': '数学表达式'},
             'precision': {'type': 'integer', 'description': '保留小数位，可省略'}},
            ['expression']),
    },
    {
        'id': 'convert', 'name': '单位换算', 'category': 'aux',
        'desc': '长度/重量/温度/存储/时间换算',
        'schema': _fn(
            'convert',
            '单位换算。category: length|mass|temperature|data|time。'
            '例如 length 的 m/km/cm/mm/mi/ft/in；mass 的 kg/g/mg/t/lb/oz；'
            'temperature 的 C/F/K；data 的 B/KB/MB/GB/TB；time 的 s/min/h/d/week。',
            {'value': {'type': 'number', 'description': '数值'},
             'from': {'type': 'string', 'description': '原单位'},
             'to': {'type': 'string', 'description': '目标单位'},
             'category': {'type': 'string', 'description': '类别，可省略自动判断'}},
            ['value', 'from', 'to']),
    },
    {
        'id': 'random', 'name': '随机/抽签', 'category': 'aux',
        'desc': '随机整数、随机小数、掷骰子、抛硬币、从列表抽一个',
        'schema': _fn(
            'random',
            '生成随机结果。kind: int|float|dice|coin|choice。'
            'int/float 用 min/max；dice 用 sides（默认 6）与 count（默认 1）；'
            'choice 用 items（字符串数组）。',
            {'kind': {'type': 'string', 'description': 'int|float|dice|coin|choice'},
             'min': {'type': 'number'}, 'max': {'type': 'number'},
             'sides': {'type': 'integer'}, 'count': {'type': 'integer'},
             'items': {'type': 'array', 'items': {'type': 'string'}}},
            ['kind']),
    },
    {
        'id': 'codec', 'name': '编码/摘要', 'category': 'aux',
        'desc': 'MD5/SHA1/SHA256、Base64 编解码',
        'schema': _fn(
            'codec',
            '对文本做摘要或 Base64 编解码。action: md5|sha1|sha256|b64e|b64d。',
            {'action': {'type': 'string', 'description': 'md5|sha1|sha256|b64e|b64d'},
             'text': {'type': 'string', 'description': '待处理文本'}},
            ['action', 'text']),
    },
    {
        'id': 'date_calc', 'name': '日期计算', 'category': 'aux',
        'desc': '两个日期相差天数、日期加减天数',
        'schema': _fn(
            'date_calc',
            '日期计算。action: diff（date1/date2 相差天数）| add（date1 加减 days）。'
            '日期格式 YYYY-MM-DD。',
            {'action': {'type': 'string', 'description': 'diff|add'},
             'date1': {'type': 'string'}, 'date2': {'type': 'string'},
             'days': {'type': 'integer'}},
            ['action', 'date1']),
    },
    {
        'id': 'ws_list', 'name': '工作区·列出', 'category': 'workspace',
        'desc': '列出工作区目录内容',
        'schema': _fn('ws_list', '列出工作区某个目录下的文件与文件夹。path 留空表示根目录。',
                      {'path': {'type': 'string', 'description': '相对路径，可留空'}}),
    },
    {
        'id': 'ws_read', 'name': '工作区·读取', 'category': 'workspace',
        'desc': '读取工作区里的文本文件',
        'schema': _fn('ws_read', '读取工作区内某个文本文件的内容。',
                      {'path': {'type': 'string', 'description': '相对路径'}}, ['path']),
    },
    {
        'id': 'ws_write', 'name': '工作区·写入', 'category': 'workspace',
        'desc': '写入/覆盖工作区里的文本文件',
        'schema': _fn('ws_write', '在工作区写入或覆盖一个文本文件（自动建目录）。',
                      {'path': {'type': 'string', 'description': '相对路径'},
                       'content': {'type': 'string', 'description': '文件内容'}},
                      ['path', 'content']),
    },
    {
        'id': 'ws_mkdir', 'name': '工作区·建目录', 'category': 'workspace',
        'desc': '在工作区创建目录',
        'schema': _fn('ws_mkdir', '在工作区创建目录（含多级）。',
                      {'path': {'type': 'string', 'description': '相对路径'}}, ['path']),
    },
    {
        'id': 'ws_delete', 'name': '工作区·删除', 'category': 'workspace',
        'desc': '删除工作区里的文件或目录',
        'schema': _fn('ws_delete', '删除工作区内的文件或目录（不可恢复）。',
                      {'path': {'type': 'string', 'description': '相对路径'}}, ['path']),
    },
]

_BY_ID = {t['id']: t for t in TOOLS}

# ---- 工具调用统计（内存，进程重启清零） ----
_STATS = {}
_RECENT = deque(maxlen=40)
_STATS_LOCK = threading.Lock()


def _record(name, ms, ok, args=None, err=''):
    info = _BY_ID.get(name) or {'name': name}
    with _STATS_LOCK:
        st = _STATS.setdefault(name, {'calls': 0, 'ok': 0, 'fail': 0, 'ms': 0.0,
                                      'last_ms': 0, 'last_ts': 0})
        st['calls'] += 1
        st['ok' if ok else 'fail'] += 1
        st['ms'] += ms
        st['last_ms'] = int(ms)
        st['last_ts'] = int(time.time())
        try:
            prev = json.dumps(args or {}, ensure_ascii=False)
        except Exception:
            prev = ''
        _RECENT.appendleft({
            'time': time.strftime('%H:%M:%S'),
            'tool': name, 'name': info.get('name') or name,
            'ok': bool(ok), 'ms': int(ms),
            'args': prev[:70], 'error': (err or '')[:80],
        })


def stats():
    with _STATS_LOCK:
        tools_out = []
        total = ok = fail = 0
        for t in TOOLS:
            st = _STATS.get(t['id'])
            if not st or not st['calls']:
                continue
            calls = st['calls']
            tools_out.append({
                'id': t['id'], 'name': t['name'], 'calls': calls,
                'ok': st['ok'], 'fail': st['fail'],
                'avg_ms': round(st['ms'] / calls, 1),
                'last_ms': st['last_ms'], 'last_ts': st['last_ts'],
            })
            total += calls
            ok += st['ok']
            fail += st['fail']
        recent = list(_RECENT)
    return {
        'total': total, 'ok': ok, 'fail': fail,
        'rate': round(ok * 100.0 / total, 1) if total else 0,
        'tools': tools_out, 'recent': recent,
    }


def enabled_map(cfg=None):
    cfg = cfg or config.load()
    t = cfg.get('tools') or {}
    en = t.get('enabled') or {}
    out = {}
    for tid in _BY_ID:
        if tid == 'web_search':
            feat = ((cfg.get('features') or {}).get('web_search') or {}).get('enabled')
            out[tid] = bool(en.get(tid, feat))
        else:
            out[tid] = bool(en.get(tid, True))
    return out


def public_list(cfg=None):
    en = enabled_map(cfg)
    return [{'id': t['id'], 'name': t['name'], 'desc': t['desc'],
             'category': t['category'], 'enabled': en.get(t['id'], False)}
            for t in TOOLS]


def _run_now():
    from . import panel
    n = panel.now()
    return {'date': n.strftime('%Y-%m-%d'), 'time': n.strftime('%H:%M:%S'),
            'weekday': '一二三四五六日'[n.weekday()]}


# ---------------------------------------------------------------- 辅助工具实现

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod, ast.Pow: operator.pow}
_FUNCS = {
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
    'log': lambda x, base=math.e: math.log(x, base), 'log10': math.log10,
    'log2': math.log2, 'exp': math.exp, 'abs': abs, 'round': round,
    'floor': math.floor, 'ceil': math.ceil, 'factorial': math.factorial,
    'min': min, 'max': max, 'gcd': math.gcd, 'degrees': math.degrees,
    'radians': math.radians, 'pow': pow,
}
_CONSTS = {'pi': math.pi, 'e': math.e, 'tau': math.tau}


def _fmt(v):
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    f = float(v)
    if f.is_integer() and abs(f) < 1e15:
        return str(int(f))
    return ('%.10g' % f)


def _eval_node(node):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        a = _eval_node(node.left)
        b = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(b) > 10000:
            raise RuntimeError('指数过大')
        return _OPS[type(node.op)](a, b)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        v = _eval_node(node.operand)
        return v if isinstance(node.op, ast.UAdd) else -v
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in _FUNCS and not node.keywords:
        args = [_eval_node(a) for a in node.args]
        if node.func.id == 'factorial' and (not args or int(args[0]) > 1000):
            raise RuntimeError('阶乘参数过大')
        return _FUNCS[node.func.id](*args)
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    raise RuntimeError('表达式包含不支持的运算')


def calc(expr, precision=None):
    expr = str(expr or '').strip()
    if not expr:
        raise RuntimeError('表达式为空')
    if len(expr) > 500:
        raise RuntimeError('表达式过长')
    # 计算器习惯用 ^ 表示幂，Python 里是异或，这里统一转换
    expr = expr.replace('^', '**')
    try:
        tree = ast.parse(expr, mode='eval')
        val = _eval_node(tree)
    except ZeroDivisionError:
        raise RuntimeError('除数不能为 0')
    except RuntimeError:
        raise
    except Exception:
        raise RuntimeError('无法解析表达式')
    if isinstance(val, complex) or not math.isfinite(float(val)):
        raise RuntimeError('结果不是有限数字')
    if precision is not None:
        val = round(float(val), max(0, min(15, int(precision))))
    return {'expression': expr, 'value': val, 'result': _fmt(val)}


_UNITS = {
    'length': {'m': 1.0, 'km': 1000.0, 'cm': 0.01, 'mm': 0.001,
               'mi': 1609.344, 'ft': 0.3048, 'in': 0.0254, 'yd': 0.9144},
    'mass': {'kg': 1.0, 'g': 0.001, 'mg': 1e-6, 't': 1000.0,
             'lb': 0.45359237, 'oz': 0.028349523125},
    'data': {'B': 1.0, 'KB': 1024.0, 'MB': 1048576.0,
             'GB': 1073741824.0, 'TB': 1099511627776.0},
    'time': {'s': 1.0, 'min': 60.0, 'h': 3600.0, 'd': 86400.0, 'week': 604800.0},
}
_TEMP = {'C', 'F', 'K'}


def convert(value, frm, to, category=''):
    v = float(value)
    frm = str(frm or '').strip()
    to = str(to or '').strip()
    cat = str(category or '').strip().lower()
    if not cat:
        if frm.upper() in _TEMP or to.upper() in _TEMP:
            cat = 'temperature'
        else:
            for k, table in _UNITS.items():
                if frm in table or to in table:
                    cat = k
                    break
    if cat == 'temperature':
        f, t = frm.upper(), to.upper()
        if f not in _TEMP or t not in _TEMP:
            raise RuntimeError('温度单位只支持 C/F/K')
        c = v if f == 'C' else ((v - 32) * 5 / 9 if f == 'F' else v - 273.15)
        out = c if t == 'C' else (c * 9 / 5 + 32 if t == 'F' else c + 273.15)
        return {'value': out, 'result': '%.4f' % out, 'from': frm, 'to': to}
    table = _UNITS.get(cat)
    if not table or frm not in table or to not in table:
        raise RuntimeError('不支持的单位：%s → %s' % (frm, to))
    out = v * table[frm] / table[to]
    return {'value': out, 'result': '%.6g' % out, 'category': cat,
            'from': frm, 'to': to}


def rand(kind='int', **kw):
    k = str(kind or 'int').lower()
    if k == 'int':
        a = int(kw.get('min') or 0)
        b = int(kw.get('max') or 100)
        if a > b:
            a, b = b, a
        n = _random.randint(a, b)
        return {'kind': k, 'result': str(n)}
    if k == 'float':
        a = float(kw.get('min') or 0)
        b = float(kw.get('max') or 1)
        if a > b:
            a, b = b, a
        n = round(_random.uniform(a, b), 6)
        return {'kind': k, 'result': str(n)}
    if k == 'dice':
        sides = max(2, int(kw.get('sides') or 6))
        cnt = max(1, min(20, int(kw.get('count') or 1)))
        rolls = [_random.randint(1, sides) for _ in range(cnt)]
        return {'kind': k, 'rolls': rolls, 'result': ' + '.join(map(str, rolls)),
                'total': sum(rolls)}
    if k == 'coin':
        return {'kind': k, 'result': _random.choice(['正面', '反面'])}
    if k == 'choice':
        items = [str(x) for x in (kw.get('items') or []) if str(x).strip()]
        if not items:
            raise RuntimeError('items 不能为空')
        return {'kind': k, 'result': _random.choice(items)}
    raise RuntimeError('未知随机类型：%s' % kind)


def codec(action, text):
    a = str(action or '').lower()
    raw = str(text or '').encode('utf-8')
    if a in ('md5', 'sha1', 'sha256'):
        h = hashlib.new(a)
        h.update(raw)
        return {'action': a, 'result': h.hexdigest()}
    if a == 'b64e':
        return {'action': a, 'result': base64.b64encode(raw).decode('ascii')}
    if a == 'b64d':
        try:
            return {'action': a, 'result': base64.b64decode(raw).decode('utf-8')}
        except Exception:
            raise RuntimeError('不是合法的 Base64 文本')
    raise RuntimeError('未知操作：%s' % action)


def date_calc(action, date1, date2='', days=0):
    a = str(action or '').lower()
    try:
        d1 = date.fromisoformat(str(date1))
    except Exception:
        raise RuntimeError('日期格式应为 YYYY-MM-DD')
    if a == 'diff':
        try:
            d2 = date.fromisoformat(str(date2))
        except Exception:
            raise RuntimeError('日期格式应为 YYYY-MM-DD')
        return {'days': (d2 - d1).days, 'result': '%d 天' % (d2 - d1).days}
    if a == 'add':
        d = d1 + timedelta(days=int(days or 0))
        return {'date': d.isoformat(), 'result': d.isoformat()}
    raise RuntimeError('未知操作：%s' % action)


async def run_manual(name, args):
    """手动测试也计入统计（面板「测试」按钮）。"""
    t0 = time.time()
    try:
        r = await _dispatch(name, args)
    except Exception as e:
        _record(name, (time.time() - t0) * 1000, False, args, str(e))
        raise
    _record(name, (time.time() - t0) * 1000, True, args)
    return r


async def _dispatch(name, args):
    args = args or {}
    if name == 'web_search':
        cfg = config.load()
        lim = int((((cfg.get('features') or {}).get('web_search') or {})
                   .get('max_results')) or 5)
        q = str(args.get('query') or args.get('q') or '')
        res = await search.query(q, limit=lim)
        return {'query': q, 'results': res}
    if name == 'now':
        return _run_now()
    if name == 'calc':
        return calc(args.get('expression') or '', args.get('precision'))
    if name == 'convert':
        return convert(args.get('value') or 0, args.get('from') or '',
                       args.get('to') or '', args.get('category') or '')
    if name == 'random':
        kw = {k: v for k, v in args.items() if k != 'kind'}
        return rand(args.get('kind') or 'int', **kw)
    if name == 'codec':
        return codec(args.get('action') or '', args.get('text') or '')
    if name == 'date_calc':
        return date_calc(args.get('action') or '', args.get('date1') or '',
                         args.get('date2') or '', args.get('days') or 0)
    if name == 'ws_list':
        return list_dir(args.get('path') or '')
    if name == 'ws_read':
        return read_text(args.get('path') or '')
    if name == 'ws_write':
        return write_text(args.get('path') or '', args.get('content') or '')
    if name == 'ws_mkdir':
        return mkdir(args.get('path') or '')
    if name == 'ws_delete':
        return delete(args.get('path') or '')
    raise RuntimeError('未知工具：%s' % name)


def build(cfg=None):
    """返回 (OpenAI tools, runner)；按开关过滤。"""
    cfg = cfg or config.load()
    en = enabled_map(cfg)
    tools = [t['schema'] for t in TOOLS if en.get(t['id'])]

    async def runner(name, args):
        if not en.get(name):
            raise RuntimeError('工具未启用：%s' % name)
        t0 = time.time()
        try:
            r = await _dispatch(name, args)
        except Exception as e:
            _record(name, (time.time() - t0) * 1000, False, args, str(e))
            raise
        ms = (time.time() - t0) * 1000
        _record(name, ms, True, args)
        logbuf.info('tool', '%s(%s) → ok %dms' % (name, json.dumps(args, ensure_ascii=False)[:120], ms))
        return r

    if not tools:
        return None, None
    return tools, runner
