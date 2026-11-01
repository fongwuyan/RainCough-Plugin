#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫码式新增的端到端验证：建实例 → 出码 → 关闭清理 → 占位过滤。

用法:
    MSYS_NO_PATHCONV=1 python tools/test_scan_flow.py --target prod
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
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)
    ok = True

    print('=== 1. 扫码式建实例 ===')
    d = data(api, 'qqbot.inst.scan', {}, timeout=90)
    slug = d.get('slug')
    print('   slug=%s webui=%s onebot=%s display=%s' %
          (slug, d.get('webui_port'), d.get('onebot_port'), d.get('display')))
    qr = d.get('qrcode') or ''
    print('   二维码: %s' % (qr[:60] + '...' if qr else '(空) ← 失败'))
    if not qr:
        print('   !! 没拿到二维码')
        ok = False

    print('\n=== 2. 占位实例不应出现在实例列表里 ===')
    lst = data(api, 'qqbot.inst.list', {}) or {}
    items = lst.get('items') or []
    names = [str(i.get('uin')) for i in items]
    print('   列表: %s' % names)
    if slug in names:
        print('   !! 占位实例出现在列表里了')
        ok = False
    else:
        print('   ✓ 已过滤')

    print('\n=== 3. 模拟"关闭弹窗"：删掉占位实例 ===')
    r = call(api, 'qqbot.inst.action', {'uin': slug, 'action': 'remove'}, timeout=60)
    print('   remove -> %s' % json.dumps(r, ensure_ascii=False)[:200])

    time.sleep(3)
    lst2 = data(api, 'qqbot.inst.list', {}) or {}
    names2 = [str(i.get('uin')) for i in (lst2.get('items') or [])]
    print('   删除后列表: %s' % names2)
    if slug in names2:
        print('   !! 占位实例还在')
        ok = False
    else:
        print('   ✓ 已清理')

    print('\n=== 4. 残留检查 ===')
    out = api.run('ls -d /opt/napcat/instances/* 2>/dev/null | wc -l; '
                  'systemctl list-units --all --no-legend 2>/dev/null | grep -c "_pending_" || true',
                  timeout=60)
    print('   %s' % (out or '').strip())

    print('\n=== 结论: %s ===' % ('全部通过' if ok else '有问题'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
