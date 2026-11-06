# -*- coding: utf-8 -*-
"""生成「双人格」风格的角色卡配图。

产出（<媒体根>/cards/<card_id>/）：
    avatar.jpg     512×512  圆形头像（QQ 头像下载后本机托管）
    cover.jpg     1280×720  封面：左冷(理智) / 右暖(疯狂)，中间一道裂缝
    portrait.jpg   720×1080 竖版海报

跑在装了 Pillow 的机器上（生产机：/opt/rcbot/venv/bin/python）。

用法:
    /opt/rcbot/venv/bin/python make_dual_cover.py \
        --card-id card_xizhiqing \
        --avatar-url "https://q1.qlogo.cn/g?b=qq&nk=3975339260&s=200"
"""
import argparse
import io
import json
import math
import os
import random
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFilter

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'}

# 理智（冷）/ 疯狂（暖）
C_L1 = (18, 42, 74)
C_L2 = (86, 148, 214)
C_R1 = (78, 26, 40)
C_R2 = (222, 140, 72)
C_LINE = (240, 226, 210)


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def media_root():
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


def vgrad(w, h, c1, c2):
    """竖向渐变（按行算，比逐像素快很多）。"""
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)],
               fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return img


def hgrad(w, h, c1, c2):
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(1, w - 1)
        d.line([(x, 0), (x, h)],
               fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return img


def circle_avatar(src, size):
    """把正方形头像裁成圆形（透明底）。"""
    im = Image.open(src).convert('RGBA')
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    im = im.resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def jagged_split(w, h, x_mid, seed=7):
    """中间那道裂缝：一条上下抖动的折线。"""
    rnd = random.Random(seed)
    pts = []
    y = -10
    x = x_mid
    while y < h + 10:
        pts.append((x, y))
        y += 14
        x = x_mid + rnd.randint(-16, 16)
    return pts


def make_cover(avatar_png, out_path, w=1280, h=720, seed=7):
    """左冷右暖 + 中间裂缝 + 中间圆形头像。"""
    left = hgrad(w // 2 + 8, h, C_L1, C_L2)
    right = hgrad(w - w // 2 + 8, h, C_R2, C_R1)
    canvas = Image.new('RGB', (w, h))
    canvas.paste(left, (0, 0))
    canvas.paste(right, (w // 2, 0))

    # 中间的光晕
    glow = Image.new('RGB', (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(jagged_split(w, h, w // 2, seed), fill=(255, 245, 235), width=5)
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    canvas = Image.blend(canvas, Image.blend(canvas, glow, 0.55), 0.9)

    # 裂缝本体（细白线 + 一点暗边）
    d = ImageDraw.Draw(canvas)
    pts = jagged_split(w, h, w // 2, seed)
    d.line(pts, fill=(20, 16, 24), width=7)
    d.line(pts, fill=C_LINE, width=2)

    # 中间的圆形头像（白边 + 投影）
    av = Image.open(avatar_png).convert('RGBA')
    size = 236
    av = av.resize((size, size), Image.LANCZOS)
    ring = Image.new('RGBA', (size + 16, size + 16), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, size + 15, size + 15), fill=(255, 255, 255, 235))
    shadow = Image.new('RGBA', (size + 16, size + 16), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((6, 10, size + 21, size + 25), fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    cx, cy = w // 2, h // 2
    canvas.paste(shadow, (cx - (size + 16) // 2, cy - (size + 16) // 2), shadow)
    canvas.paste(ring, (cx - (size + 16) // 2, cy - (size + 16) // 2), ring)
    canvas.paste(av, (cx - size // 2, cy - size // 2), av)

    # 噪点质感
    noise = Image.effect_noise((w, h), 12).convert('L')
    canvas = Image.blend(canvas, Image.merge('RGB', (noise, noise, noise)), 0.045)
    canvas.save(out_path, 'JPEG', quality=90, optimize=True, progressive=True)
    return canvas.size


def make_portrait(avatar_png, out_path, w=720, h=1080):
    """竖版海报：冷底 + 头像 + 两道色调。"""
    bg = vgrad(w, h, C_L1, (32, 58, 92))
    d = ImageDraw.Draw(bg, 'RGBA')
    # 右侧暖光
    for i in range(160):
        t = i / 159
        x0 = int(w * 0.52 + t * w * 0.55)
        d.ellipse((x0 - 120, int(h * 0.18), x0 + 120, int(h * 0.82)),
                  fill=(222, 140, 72, int(46 * (1 - t))))
    bg = bg.filter(ImageFilter.GaussianBlur(24))
    av = Image.open(avatar_png).convert('RGBA')
    size = 420
    av = av.resize((size, size), Image.LANCZOS)
    ring = Image.new('RGBA', (size + 18, size + 18), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, size + 17, size + 17), fill=(255, 255, 255, 232))
    bg.paste(ring, (w // 2 - (size + 18) // 2, int(h * 0.22)), ring)
    bg.paste(av, (w // 2 - size // 2, int(h * 0.22) + 9), av)
    bg.save(out_path, 'JPEG', quality=90, optimize=True, progressive=True)
    return bg.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--card-id', required=True)
    ap.add_argument('--avatar-url', required=True)
    ap.add_argument('--out-root', default='')
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()

    root = args.out_root or media_root()
    d = os.path.join(root, 'cards', args.card_id)
    src = os.path.join(d, 'src')
    os.makedirs(src, exist_ok=True)

    raw = os.path.join(src, 'avatar_raw.jpg')
    data = fetch(args.avatar_url)
    open(raw, 'wb').write(data)

    # 先存一份方形头像（前端头像用圆形裁切，但方形的也能用）
    im = Image.open(io.BytesIO(data)).convert('RGB')
    side = min(im.size)
    im = im.crop(((im.width - side) // 2, (im.height - side) // 2,
                  (im.width - side) // 2 + side, (im.height - side) // 2 + side))
    av_square = os.path.join(d, 'avatar.jpg')
    im.resize((512, 512), Image.LANCZOS).save(av_square, 'JPEG', quality=92)

    circle = circle_avatar(raw, 512)
    av_circle = os.path.join(d, 'avatar_circle.png')
    circle.save(av_circle, 'PNG')

    cover = os.path.join(d, 'cover.jpg')
    portrait = os.path.join(d, 'portrait.jpg')
    cs = make_cover(av_circle, cover, seed=args.seed)
    ps = make_portrait(av_circle, portrait)

    print(json.dumps({
        'card_id': args.card_id, 'dir': d,
        'avatar': os.path.relpath(av_square, root),
        'cover': os.path.relpath(cover, root),
        'portrait': os.path.relpath(portrait, root),
        'cover_size': cs, 'portrait_size': ps,
        'src_bytes': len(data),
    }, ensure_ascii=False))


if __name__ == '__main__':
    sys.exit(main())
