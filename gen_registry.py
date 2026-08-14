#!/usr/bin/env python3
"""生成 RainCough-Plugin 仓库的 registry.json。

扫描各插件目录下的 plugin.py, 以正则提取插件元信息(name/label/description),
version 取自 VERSION 或 info.prop 文件。运行:
    python gen_registry.py
"""
import os
import re
import json
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'registry.json')

KNOWN = [
    ('aigen', 'AI 生图'),
    ('docker', 'Docker 管理'),
    ('JMComic', 'JMComic 搜索与阅读'),
    ('kvm', 'KVM 虚拟机'),
    ('laizhangsetu', '来张涩图'),
    ('mcserver', 'MC 服务器'),
    ('mcskin', 'MC 皮肤'),
    ('toolbox', '全能工具箱'),
    ('touchgal', 'TouchGal 游戏查找'),
    ('uptime', '站点监控'),
    ('yulotool', '工具箱'),
]


def parse_plugin_meta(plugin_dir):
    """从 plugin.py 提取 Plugin 子类的 name/label/description。"""
    pf = os.path.join(plugin_dir, 'plugin.py')
    if not os.path.isfile(pf):
        return {}
    with open(pf, encoding='utf-8', errors='replace') as f:
        text = f.read()
    # 找出继承 Plugin 的类
    classes = re.findall(r'^\s*class\s+(\w+)\s*\(\s*(?:plugins\.)?Plugin\s*\)', text, re.M)
    if not classes:
        return {}
    meta = {}
    # 取类体内顶层 name = / label = / description =
    for field in ('name', 'label', 'description'):
        m = re.search(r'^\s*%s\s*=\s*[\'"]([^\'"]*)[\'"]' % field, text, re.M)
        if m:
            meta[field] = m.group(1).strip()
    return meta


def read_version(plugin_dir):
    for fname in ('VERSION', 'info.prop'):
        p = os.path.join(plugin_dir, fname)
        if os.path.isfile(p):
            try:
                with open(p, encoding='utf-8', errors='replace') as f:
                    content = f.read()
                m = re.search(r'(?:version|ver)\s*=\s*([\w.]+)', content, re.I)
                if m:
                    return m.group(1)
                if fname == 'VERSION':
                    return content.strip()
            except Exception:
                pass
    return '0.1.0'


def main():
    plugins = []
    for name, fallback_label in KNOWN:
        d = os.path.join(ROOT, name)
        if not os.path.isdir(d):
            continue
        meta = parse_plugin_meta(d)
        entry = {
            'name': name,
            'label': meta.get('label') or fallback_label,
            'version': read_version(d),
            'path': name,
            'author': '',
            'description': meta.get('description') or fallback_label,
        }
        plugins.append(entry)
    registry = {
        'name': 'RainCough 插件集',
        'updated': time.strftime('%Y-%m-%d %H:%M:%S'),
        'plugins': plugins,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print('generated %s with %d plugins' % (OUT, len(plugins)))


if __name__ == '__main__':
    main()
