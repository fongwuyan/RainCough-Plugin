# -*- coding: utf-8 -*-
"""验证媒体能通过面板通道正确提供（这决定视频/语音能不能播）。

要验证三件事：
  1. Content-Type 对（mp4 → video/mp4，mp3 → audio/mpeg）
  2. 支持 Range 请求（206 Partial Content）—— 不支持的话视频不能拖进度条、
     而且浏览器常常直接判为"播不了"
  3. 文件真的能取到内容（不是 404/空）
"""
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

PRESETS = {
    # 在生产机上跑（用 127.0.0.1）：rcbot 的 6710 只监听回环
    'prod': ('http://127.0.0.1:3900', '1'),
    'prod-ext': ('http://192.168.2.200:3900', '1'),
}


def login(base, password):
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    r = op.open(urllib.request.Request(
        base + '/api/auth/login', json.dumps({'password': password}).encode(),
        {'Content-Type': 'application/json'}), timeout=60)
    d = json.loads(r.read().decode())
    if not d.get('ok'):
        raise SystemExit('登录失败：%s' % d)
    return op


def head_info(op, url, rng=None):
    req = urllib.request.Request(url)
    if rng:
        req.add_header('Range', rng)
    try:
        r = op.open(req, timeout=60)
        body = r.read(4096)
        return r.status, dict(r.headers), len(body), body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), 0, b''


def main():
    base, pw = PRESETS[sys.argv[1] if len(sys.argv) > 1 else 'prod']
    op = login(base, pw)

    # 找媒体文件（通过 rcbot 接口拿绝对路径）
    import subprocess
    out = subprocess.run(
        ['curl', '-s', '-m', '30', 'http://127.0.0.1:6710/api/chat/media?limit=20'],
        capture_output=True, text=True).stdout
    items = json.loads(out)['data']['items']
    if not items:
        print('媒体库是空的，没有可测的文件')
        return 1

    ok = True
    for it in items:
        if not it.get('exists'):
            continue
        url = base + '/api/fm/preview?path=' + urllib.parse.quote(it['abs'])
        st, hd, n, body = head_info(op, url)
        ct = hd.get('Content-Type', '?')
        ar = hd.get('Accept-Ranges', '?')
        st2, hd2, n2, b2 = head_info(op, url, 'bytes=0-1023')
        print('%-28s %-8s' % (it['rel'].split('/')[-1], it['kind']))
        print('   全量: %s  Content-Type=%s  Accept-Ranges=%s  取到 %d 字节'
              % (st, ct, ar, n))
        print('   Range: %s  Content-Range=%s  取到 %d 字节'
              % (st2, hd2.get('Content-Range', '?'), n2))
        if st != 200 or n <= 0:
            ok = False
            print('   !! 状态异常')
        if st2 not in (200, 206):
            ok = False
            print('   !! 不支持 Range —— 浏览器可能判为播不了')
        if it['kind'] == 'video' and ct != 'video/mp4':
            ok = False
            print('   !! 视频的 Content-Type 不对')
        if it['kind'] == 'record' and ct not in ('audio/mpeg', 'audio/mp3'):
            ok = False
            print('   !! 音频的 Content-Type 不对')
        if it['kind'] == 'image' and not ct.startswith('image/'):
            ok = False
            print('   !! 图片的 Content-Type 不对')

    print('\n=== %s ===' % ('全部通过' if ok else '有问题'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
