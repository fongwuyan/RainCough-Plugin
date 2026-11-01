#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在生产机后台跑一个脚本（nohup + 日志），再轮询结果。

面板终端通道有 ~15s 的 RPC 超时，长任务（装 QQ/NapCat/apt）必须走这条路。

用法:
    MSYS_NO_PATHCONV=1 python tools/prod_bg.py --target prod \
        --script /root/qqbot-reinstall/03_install_napcat_qq.sh --tag install
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description='后台执行长脚本并轮询日志')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--base', default='')
    ap.add_argument('--password', default='1')
    ap.add_argument('--script', required=True, help='远端脚本绝对路径')
    ap.add_argument('--tag', default='job', help='日志文件名前缀')
    ap.add_argument('--marker', default='', help='完成标记（默认取脚本名_DONE）')
    ap.add_argument('--wait', type=int, default=1800, help='最长等待秒')
    ap.add_argument('--poll', type=int, default=10, help='轮询间隔秒')
    args = ap.parse_args()

    preset = PRESETS[args.target]
    api = Api(args.base or preset['base'], args.password)
    log = '/root/qqbot-reinstall/%s.log' % args.tag
    marker = args.marker or (os.path.basename(args.script).replace('.sh', '') + '_DONE')

    api.run('rm -f %s; nohup bash %s > %s 2>&1 < /dev/null & echo started' % (log, args.script, log),
            timeout=30)
    print('== 后台启动 %s，日志 %s ==' % (args.script, log))

    t0 = time.time()
    shown = 0
    while time.time() - t0 < args.wait:
        time.sleep(args.poll)
        out = api.run('cat %s 2>/dev/null' % log, timeout=60)
        text = out or ''
        # 只打印新增部分
        lines = text.splitlines()
        if len(lines) > shown:
            for ln in lines[shown:]:
                print(ln)
            shown = len(lines)
        if marker in text:
            print('== 标记 %s 出现，执行完成 ==' % marker)
            return 0
        if 'EXIT_CODE=' in text:
            print('== 脚本已退出 ==')
            return 0

    print('== 超时(%ds)，最后日志末尾 ==' % args.wait)
    out = api.run('tail -30 %s' % log, timeout=60)
    print(out)
    return 1


if __name__ == '__main__':
    sys.exit(main())
