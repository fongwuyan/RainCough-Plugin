#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""走新的扫码式流程建实例（qqbot.inst.scan），验证后端改造。

用法:
    MSYS_NO_PATHCONV=1 python tools/scan_add.py --target prod
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def call(api, iface, params, timeout=40):
    return api.post('/api/plugins/QQBot/invoke',
                    {'iface': iface, 'params': params, 'timeout_ms': timeout * 1000},
                    timeout=timeout + 15)


def data(api, iface, params, timeout=40):
    r = call(api, iface, params, timeout)
    if not (isinstance(r, dict) and r.get('ok')):
        raise RuntimeError('%s 失败: %s' % (iface, json.dumps(r, ensure_ascii=False)[:400]))
    res = r.get('result') or {}
    if res.get('ok') is False:
        raise RuntimeError('%s 内部错误: %s' % (iface, json.dumps(res, ensure_ascii=False)[:400]))
    return res.get('data')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--wait', type=int, default=0, help='等扫码完成的秒数，0=只建实例出码')
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)

    print('== 1. 扫码式建实例（不填 QQ 号）==')
    d = data(api, 'qqbot.inst.scan', {}, timeout=90)
    print('   slug=%s webui=%s onebot=%s display=%s' %
          (d.get('slug'), d.get('webui_port'), d.get('onebot_port'), d.get('display')))
    print('   qrcode=%s' % (d.get('qrcode') or '(空)'))
    print('   hint=%s' % (d.get('hint') or ''))
    if not d.get('qrcode'):
        print('   !! 没拿到二维码')
        return 1

    with open('qrcode_url.txt', 'w', encoding='utf-8') as f:
        f.write(d['qrcode'])
    print('   已写入 qrcode_url.txt')

    if not args.wait:
        print('\n== 只建实例完成（加 --wait N 可等扫码）==')
        return 0

    print('\n== 2. 等扫码 ==')
    slug = d.get('slug')
    t0 = time.time()
    while time.time() - t0 < args.wait:
        time.sleep(5)
        st = data(api, 'qqbot.inst.scan_status', {'slug': slug}, timeout=30)
        phase = st.get('phase') or '?'
        if st.get('done'):
            print('   登录成功: uin=%s nick=%s' % (st.get('uin'), st.get('nick')))
            break
        if st.get('error'):
            print('   %s (phase=%s)' % (st.get('error'), phase))
    else:
        print('   超时未登录 (phase=%s)' % phase)

    print('\n== 3. 实例列表 ==')
    lst = data(api, 'qqbot.inst.list', {}) or {}
    for it in (lst.get('items') or []):
        print('   %s nick=%r avatar=%s state=%s online=%s' %
              (it.get('uin'), it.get('nick'), (it.get('avatar') or '')[:50],
               it.get('state'), it.get('online')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
