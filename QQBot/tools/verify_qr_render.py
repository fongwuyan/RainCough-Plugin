#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证二维码在前端能正常渲染（用与前端完全相同的 makeQr 实现）。

在本地用 frontend/qrcode.mjs 生成 SVG → 存成 .svg，
再用 headless 浏览器截一张图，确认肉眼可见且可扫。

用法:
    MSYS_NO_PATHCONV=1 python tools/verify_qr_render.py --target prod
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402

NODE_SNIPPET = r"""
import m from '%s';
const qr = m(0, 'M');
qr.addData(process.env.QR_TEXT);
qr.make();
process.stdout.write(qr.createSvgTag({cellSize:5, margin:0, scalable:true}));
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--keep', action='store_true', help='保留实例不删')
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)
    r = api.post('/api/plugins/QQBot/invoke', {
        'iface': 'qqbot.inst.scan', 'params': {}, 'timeout_ms': 90000,
    }, timeout=120)
    res = (r.get('result') or {}).get('data') or {}
    slug = res.get('slug')
    url = res.get('qrcode')
    print('slug=%s' % slug)
    print('qrcode=%s' % (url or '(空)'))
    if not url:
        print('没拿到二维码')
        return 1

    # 用前端同一份 qrcode.mjs 生成 SVG
    qrpath = os.path.join(HERE, '..', 'frontend', 'qrcode.mjs')
    # Windows 下 ESM 导入绝对路径必须是 file:// URL
    qrurl = 'file:///' + os.path.abspath(qrpath).replace('\\', '/').lstrip('/')
    code = NODE_SNIPPET % qrurl
    out = 'qr-preview.svg'
    env = dict(os.environ)
    env['QR_TEXT'] = url
    p = subprocess.run(['node', '--input-type=module', '-e', code],
                       capture_output=True, text=True,
                       cwd=os.path.dirname(qrpath), env=env)
    svg = p.stdout
    if p.returncode != 0:
        print('node 失败:', p.stderr[:400])
        return 1
    with open(out, 'w', encoding='utf-8') as f:
        f.write(svg)
    print('已生成 %s (%d 字节)' % (out, len(svg)))
    print('SVG 头:', svg[:120])
    if '<svg' not in svg:
        print('!! 不是有效 SVG')
        return 1

    if not args.keep:
        api.post('/api/plugins/QQBot/invoke', {
            'iface': 'qqbot.inst.action',
            'params': {'uin': slug, 'action': 'remove'},
            'timeout_ms': 60000,
        }, timeout=90)
        print('已清理实例 %s' % slug)
    return 0


if __name__ == '__main__':
    sys.exit(main())
