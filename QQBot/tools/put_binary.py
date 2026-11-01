# -*- coding: utf-8 -*-
"""上传二进制文件到生产机（走面板的 /api/fm/upload，multipart）。

put_file.py 走的是 /api/fm/save（文本接口），二进制会被 UTF-8 编解码毁掉。
这个用 multipart 传原始字节。

用法:
    MSYS_NO_PATHCONV=1 python tools/put_binary.py --target prod \
        --path /root/qqbot-reinstall --file raincough-new /tmp/raincough-linux-amd64
"""
import argparse
import hashlib
import http.cookiejar
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid

PRESETS = {
    'prod': ('http://192.168.2.200:3900', '1'),
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


def multipart(fields, fname, data, ctype='application/octet-stream', field='file'):
    """自己拼 multipart/form-data（不引第三方依赖）。

    field —— 文件字段名：/api/fm/upload 用 'file'，/api/fm/upload/chunk 用 'chunk'
    """
    boundary = '----rcbnd' + uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
                    % (boundary, k, v)).encode('utf-8'))
    ctype2 = ctype or mimetypes.guess_type(fname)[0] or 'application/octet-stream'
    out.append(('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
                'Content-Type: %s\r\n\r\n' % (boundary, field, fname, ctype2)).encode('utf-8'))
    out.append(data)
    out.append(('\r\n--%s--\r\n' % boundary).encode('utf-8'))
    return b''.join(out), 'multipart/form-data; boundary=%s' % boundary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', default='prod')
    ap.add_argument('--path', required=True, help='远端目标目录')
    ap.add_argument('--file', required=True, help='远端文件名')
    ap.add_argument('--src', required=True, help='本地文件')
    ap.add_argument('--timeout', type=int, default=600)
    args = ap.parse_args()

    base, pw = PRESETS[args.target]
    op = login(base, pw)

    with open(args.src, 'rb') as f:
        data = f.read()
    md5 = hashlib.md5(data).hexdigest()
    print('本地: %s  %d 字节  md5=%s' % (args.src, len(data), md5))

    # 用 chunk 接口：它尊重 path 字段（单请求 upload 会忽略 path，存到 /）
    body, ctype = multipart({
        'path': args.path,
        'filename': args.file,
        'file_id': 'rc' + uuid.uuid4().hex[:16],
        'chunk_index': '0',
        'total_chunks': '1',
        'conflict': 'overwrite',
    }, args.file, data, field='chunk')
    req = urllib.request.Request(base + '/api/fm/upload/chunk', body,
                                 {'Content-Type': ctype})
    try:
        r = op.open(req, timeout=args.timeout)
        d = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print('上传失败 HTTP %s: %s' % (e.code, e.read()[:400]))
        return 1
    except Exception as e:
        print('上传失败：%s' % str(e)[:300])
        return 1
    print('上传结果: %s' % json.dumps(d, ensure_ascii=False)[:300])
    if not d.get('status'):
        return 1

    # 校验 md5
    remote = '%s/%s' % (args.path.rstrip('/'), args.file)
    r = op.open(base + '/api/fm/hash?path=' + urllib.request.quote(remote), timeout=120)
    h = json.loads(r.read().decode())
    print('远端 md5=%s  %s' % (h.get('md5'), '一致 OK' if h.get('md5') == md5 else '不一致 !!'))
    return 0 if h.get('md5') == md5 else 1


if __name__ == '__main__':
    sys.exit(main())
