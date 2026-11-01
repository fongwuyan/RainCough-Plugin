#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用插件的正规接口重建 NapCat 实例（走 qqbot.inst.add / qqbot.inst.action）。

★ 为什么不用手写脚本建实例：
   插件的 inst_add 除了建目录/写 env/写 systemd/启动，还会把实例
   **注册进 rcbot 的账号表**（POST /api/accounts），并分配不冲突的端口与显示号。
   手写脚本做不了这步 → rcbot 里会留一个空的 a_default，机器人连不上。

用法:
    MSYS_NO_PATHCONV=1 python tools/rebuild_inst.py --target prod --uin 1132096843
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
        raise RuntimeError('%s 失败: %s' % (iface, json.dumps(r, ensure_ascii=False)[:300]))
    res = r.get('result') or {}
    if res.get('ok') is False:
        raise RuntimeError('%s 内部错误: %s' % (iface, json.dumps(res, ensure_ascii=False)[:300]))
    return res.get('data')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--uin', required=True, help='要添加的 QQ 号')
    ap.add_argument('--keep', action='store_true', help='保留已有实例（不删重建）')
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)

    # 1. 看现状
    lst = data(api, 'qqbot.inst.list', {}) or {}
    items = lst.get('items') or []
    print('== 当前实例 ==')
    for it in items:
        print('  %s webui=%s onebot=%s display=%s state=%s'
              % (it.get('uin'), it.get('webui'), it.get('onebot_port'),
                 it.get('display'), it.get('state')))

    exists = [it for it in items if str(it.get('uin')) == args.uin]
    if exists and args.keep:
        print('\n== 实例已存在，跳过 add ==')
    else:
        if exists:
            print('\n== 移除手工搭建的旧实例（走插件 remove 接口）==')
            d = data(api, 'qqbot.inst.action', {'uin': args.uin, 'action': 'remove'})
            print('  %s' % json.dumps(d, ensure_ascii=False)[:300])
            time.sleep(3)

        print('\n== qqbot.inst.add ==')
        d = data(api, 'qqbot.inst.add', {'uin': args.uin}, timeout=60)
        print('  %s' % json.dumps(d, ensure_ascii=False)[:400])

    # 3. 轮询就绪
    print('\n== 等待 WebUI 就绪 ==')
    for i in range(40):
        time.sleep(3)
        lst = data(api, 'qqbot.inst.list', {}) or {}
        it = [x for x in (lst.get('items') or []) if str(x.get('uin')) == args.uin]
        if it and it[0].get('state') == 'active':
            print('  第 %d 次: state=%s webui=%s' % (i + 1, it[0].get('state'), it[0].get('webui')))
            break
    else:
        print('  未在 120s 内就绪')

    # 4. rcbot 账号是否已注册
    print('\n== rcbot 账号表 ==')
    st = data(api, 'rcbot.status', {}) or {}
    for a in (st.get('accounts') or []):
        print('  id=%s uin=%s ws=%s unit=%s connected=%s'
              % (a.get('id'), a.get('uin'), a.get('webui'), a.get('unit'), a.get('connected')))

    # 5. 取二维码
    print('\n== 扫码 ==')
    q = data(api, 'qqbot.inst.action', {'uin': args.uin, 'action': 'qrcode'}, timeout=40)
    print('  phase=%s login=%s' % (q.get('phase'), q.get('login')))
    print('  qrcode=%s' % (q.get('qrcode') or '(空)'))
    if q.get('qrcode'):
        with open('qrcode_url.txt', 'w', encoding='utf-8') as f:
            f.write(q['qrcode'])
        print('  已写入 qrcode_url.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
