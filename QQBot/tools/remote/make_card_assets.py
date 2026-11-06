# -*- coding: utf-8 -*-
"""角色卡片图片资产：下载 → 裁剪 → 落到本机媒体目录（不外链，永久有效）。

跑在装了 Pillow 的那台机器上（生产机是 /opt/rcbot/venv/bin/python）。

产物（都在 <媒体根>/cards/<card_id>/ 下）：
    cover.jpg     1280×720  卡片封面（16:9）
    avatar.jpg    512×512  正方形头像
    portrait.png  竖版立绘（保留透明通道）

卡片里存的路径是**相对媒体根目录**的（cards/<card_id>/cover.jpg），
后端渲染时再拼成 /api/fm/preview?path=... —— 换机器不用改卡片。

用法:
    /opt/rcbot/venv/bin/python make_card_assets.py \
        --card-id card_xxx \
        --portrait-url https://.../HoshinoPortrait.png \
        --cover-url    https://.../HoshinoLobby.png
"""
import argparse
import io
import json
import os
import sys
import urllib.request

from PIL import Image

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'}


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def media_root():
    """媒体根目录：与 rcbot.chats.media_root() 保持一致。"""
    for p in ('/opt/rcbot/data/config.json', '/opt/rcbot/config.json'):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            d = ((cfg.get('chat') or {}).get('media_dir') or '')
            if d:
                return d
        except Exception:
            pass
    return '/opt/rcbot/media'


def save_cover(src, out, w=1280, h=720, top=0):
    """封面：从回忆大厅图裁 16:9。

    人物在画面右侧，左边留白给标题 —— 这是有意的构图，不要居中裁。
    """
    im = Image.open(src).convert('RGB')
    W, H = im.size
    if W < w or H < h:
        im = im.resize((max(W, w), max(H, h)), Image.LANCZOS)
        W, H = im.size
    top = max(0, min(H - h, int(top)))
    im = im.crop((0, top, W, top + h)).resize((w, h), Image.LANCZOS)
    im.save(out, 'JPEG', quality=88, optimize=True, progressive=True)
    return im.size


def save_avatar(src, out, size=512, box=None):
    """头像：从立绘的头部裁正方形。

    box 是源图上的 (left, top, right, bottom)；不给就按比例找脸的位置
    （立绘通常脸在上部 1/5 ~ 1/3 高度、水平居中偏右）。
    """
    im = Image.open(src).convert('RGBA')
    W, H = im.size
    if not box:
        side = int(W * 0.30)
        cx = int(W * 0.55)
        cy = int(H * 0.17)
        box = (cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)
    l, t, r, b = [int(x) for x in box]
    l = max(0, min(W - 1, l)); t = max(0, min(H - 1, t))
    r = max(l + 1, min(W, r)); b = max(t + 1, min(H, b))
    im = im.crop((l, t, r, b)).resize((size, size), Image.LANCZOS)
    # 圆角外的透明：前端已经用 border-radius 裁，这里保持矩形即可
    im.save(out, 'PNG', optimize=True)
    return (l, t, r, b)


def save_portrait(src, out, max_w=900):
    im = Image.open(src).convert('RGBA')
    if im.width > max_w:
        h = int(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.LANCZOS)
    im.save(out, 'PNG', optimize=True)
    return im.size


def make_preview(cover, avatar, out, width=760):
    """核验用拼图：左边封面、右上头像、右下立绘缩略。"""
    c = Image.open(cover).convert('RGB')
    a = Image.open(avatar).convert('RGBA')
    c = c.resize((width, int(c.height * width / c.width)), Image.LANCZOS)
    ch = c.height
    side = min(ch, a.width)
    a2 = a.resize((side, side), Image.LANCZOS)
    sheet = Image.new('RGB', (width, ch), (24, 26, 32))
    sheet.paste(c, (0, 0))
    sheet.paste(a2, (width - side - 12, 12), a2)
    sheet.save(out, 'JPEG', quality=86)
    return sheet.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--card-id', required=True)
    ap.add_argument('--portrait-url', default='')
    ap.add_argument('--cover-url', default='')
    ap.add_argument('--cover-top', type=int, default=0)
    ap.add_argument('--avatar-from', default='portrait', choices=['portrait', 'cover'])
    ap.add_argument('--avatar-box', default='', help='l,t,r,b 源图坐标')
    ap.add_argument('--out-root', default='')
    args = ap.parse_args()

    root = args.out_root or media_root()
    d = os.path.join(root, 'cards', args.card_id)
    os.makedirs(d, exist_ok=True)
    src_dir = os.path.join(d, 'src')
    os.makedirs(src_dir, exist_ok=True)

    out = {'card_id': args.card_id, 'dir': d}

    portrait_src = os.path.join(src_dir, 'portrait.png')
    if args.portrait_url:
        data = fetch(args.portrait_url)
        open(portrait_src, 'wb').write(data)
        out['portrait_bytes'] = len(data)

    cover_src = os.path.join(src_dir, 'cover_src.png')
    if args.cover_url:
        data = fetch(args.cover_url)
        open(cover_src, 'wb').write(data)
        out['cover_bytes'] = len(data)

    cover_out = os.path.join(d, 'cover.jpg')
    if os.path.isfile(cover_src):
        out['cover_size'] = save_cover(cover_src, cover_out, top=args.cover_top)
        out['cover'] = os.path.relpath(cover_out, root)

    avatar_out = os.path.join(d, 'avatar.png')
    avatar_src = portrait_src if args.avatar_from == 'portrait' else cover_src
    if os.path.isfile(avatar_src):
        box = None
        if args.avatar_box:
            box = [float(x) for x in args.avatar_box.split(',')]
        out['avatar_box'] = save_avatar(avatar_src, avatar_out, box=box)
        out['avatar'] = os.path.relpath(avatar_out, root)

    portrait_out = os.path.join(d, 'portrait.png')
    if os.path.isfile(portrait_src):
        out['portrait_size'] = save_portrait(portrait_src, portrait_out)
        out['portrait'] = os.path.relpath(portrait_out, root)

    prev = os.path.join(d, '_preview.jpg')
    if os.path.isfile(cover_out) and os.path.isfile(avatar_out):
        make_preview(cover_out, avatar_out, prev)
        out['preview'] = prev

    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())
