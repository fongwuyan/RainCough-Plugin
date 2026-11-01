# -*- coding: utf-8 -*-
"""配置：JSON 文件 + 默认值深合并 + 原子写。"""
import copy
import json
import os
import threading

_lock = threading.RLock()

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
CFG_FILE = os.path.join(ROOT, 'data', 'config.json')

DEFAULT = {
    'onebot': {
        'ws_url': 'ws://127.0.0.1:6700',
        'access_token': '',
        'self_id': '',
    },
    'http': {
        'host': '127.0.0.1',
        'port': 6710,
    },
    'bot': {
        'enabled': True,
        'group_need_at': True,        # 群里必须 @ 才回
        'private_always_reply': True,  # 私聊全部回复
        'reply_with_mention': False,   # 回复时 @ 对方
        'wake_prefix': ['/'],          # 群里的唤醒前缀（发了就回，不用 @）
        'rate_limit': {'window': 60, 'max': 30},
        'allowed_groups': [],          # 空 = 不限
        'blocked_groups': [],
    },
    'context': {
        'max_tokens': 128000,
        'keep_recent_ratio': 0.15,
        'compress_enabled': True,
        'compress_provider': '',       # 空 = 用默认提供商
        'max_history_messages': 200,
        'max_output_tokens': 4096,
    },
    'session_mode': {
        'group': 'public',             # public=群共享 / private=群内每人独立
        'private': 'private',
    },
    'features': {
        'web_search': {'enabled': False, 'max_results': 5},
        'vision': {'enabled': False, 'max_images': 3},
    },
    'providers': [],
    'default_provider': '',
    'personas': [],
    'default_persona': '',
}


def _merge(base, patch):
    if not isinstance(base, dict) or not isinstance(patch, dict):
        return patch
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load():
    with _lock:
        try:
            with open(CFG_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f) or {}
        except Exception:
            raw = {}
        return _merge(copy.deepcopy(DEFAULT), raw)


def save(cfg):
    with _lock:
        os.makedirs(os.path.dirname(CFG_FILE), exist_ok=True)
        tmp = CFG_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CFG_FILE)
    return cfg


def patch(part):
    """局部更新（深合并），返回新配置。"""
    with _lock:
        cfg = load()
        cfg = _merge(cfg, part)
        return save(cfg)


def get_provider(cfg, pid=None):
    pid = pid or cfg.get('default_provider') or ''
    for p in cfg.get('providers') or []:
        if p.get('id') == pid:
            return p
    provs = [p for p in (cfg.get('providers') or []) if p.get('enable', True)]
    return provs[0] if provs else None


def get_persona(cfg, pid=None):
    pid = pid or cfg.get('default_persona') or ''
    for p in cfg.get('personas') or []:
        if p.get('id') == pid:
            return p
    return (cfg.get('personas') or [None])[0]
