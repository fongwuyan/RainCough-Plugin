#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从生产机下载二进制文件（base64 走面板终端通道，注意逐块取避免被截断）。

用法:
    MSYS_NO_PATHCONV=1 python tools/pull_file.py --target prod \
        /root/qqbot-reinstall/qrcode.png ./qq-qrcode.png
"""
import argparse
import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from deploy import Api, PRESETS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('remote')
    ap.add_argument('local')
    ap.add_argument('--target', choices=list(PRESETS), default='prod')
    ap.add_argument('--password', default='1')
    ap.add_argument('--chunk', type=int, default=3800)
    args = ap.parse_args()

    api = Api(PRESETS[args.target]['base'], args.password)

    # 取总大小与校验和
    info = api.run("stat -c '%%s' %s; md5sum %s | cut -d' ' -f1" % (args.remote, args.remote), timeout=60)
    lines = [l.strip() for l in (info or '').splitlines() if l.strip().isdigit() or len(l.strip()) == 32]
    size = int(lines[0]) if lines else 0
    md5 = lines[1] if len(lines) > 1 else ''
    print('远端大小=%s md5=%s' % (size, md5))

    buf = bytearray()
    off = 0
    while off < size:
        n = min(args.chunk, size - off)
        # 用 hex 而不是 base64: 终端回显会掺进提示符/换行，
        # hex 字符集小且每字节固定两字符，好过滤也好校验。
        cmd = ("dd if=%s bs=1 skip=%d count=%d 2>/dev/null | od -An -tx1 -v | tr -d ' \\n'"
               % (args.remote, off, n))
        out = api.run(cmd, timeout=90) or ''
        # 终端回显会把一行 hex 拆成多行，且可能混入提示符。
        # 策略：扫描全文，收集所有连续的 hex 片段（允许跨行拼接），
        # 取最长的一段 —— 那就是真正的数据行。
        best = ''
        cur = ''
        for ch in out.replace('\r', ''):
            if ch in '0123456789abcdef':
                cur += ch
            else:
                if len(cur) > len(best):
                    best = cur
                cur = ''
        if len(cur) > len(best):
            best = cur
        # 回显里往往还有更长的 hex 串（元数据），取长度最接近期望的那段
        want = n * 2
        cands = []
        cur = ''
        for ch in out.replace('\r', ''):
            if ch in '0123456789abcdef':
                cur += ch
            else:
                if cur:
                    cands.append(cur)
                cur = ''
        if cur:
            cands.append(cur)
        if cands:
            close = sorted(cands, key=lambda s: abs(len(s) - want))
            best = close[0]
        hexs = best if len(best) % 2 == 0 else best[:-1]
        if len(hexs) < 32:
            print('第 %d 块取数失败' % off)
            break
        try:
            buf.extend(bytes.fromhex(hexs))
        except Exception as e:
            print('第 %d 块解码失败: %s' % (off, e))
            break
        off += n
        print('  已取 %d/%d 字节' % (off, size))

    with open(args.local, 'wb') as f:
        f.write(buf)
    print('已写入 %s (%d 字节)' % (args.local, len(buf)))
    if md5:
        import hashlib
        got = hashlib.md5(bytes(buf)).hexdigest()
        print('校验: 远端=%s 本地=%s %s' % (md5, got, '一致 ✓' if md5 == got else '不一致 ✗'))


if __name__ == '__main__':
    sys.exit(main())
