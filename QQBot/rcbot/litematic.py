# -*- coding: utf-8 -*-
"""Litematica 投影解析：gzip+NBT → 统计 + PNG 报告。

不依赖第三方 NBT 库；渲染用 Pillow（rcbot venv 里已有）。
解析是 CPU 密集的，调用方应放到 asyncio.to_thread。
"""
import gzip
import math
import os
import struct
import tempfile
import time

MASK64 = (1 << 64) - 1


class _Reader(object):
    def __init__(self, data):
        self.d = data
        self.p = 0

    def u1(self):
        v = self.d[self.p]
        self.p += 1
        return v

    def i1(self):
        v = struct.unpack_from('>b', self.d, self.p)[0]
        self.p += 1
        return v

    def i2(self):
        v = struct.unpack_from('>h', self.d, self.p)[0]
        self.p += 2
        return v

    def i4(self):
        v = struct.unpack_from('>i', self.d, self.p)[0]
        self.p += 4
        return v

    def i8(self):
        v = struct.unpack_from('>q', self.d, self.p)[0]
        self.p += 8
        return v

    def f4(self):
        v = struct.unpack_from('>f', self.d, self.p)[0]
        self.p += 4
        return v

    def f8(self):
        v = struct.unpack_from('>d', self.d, self.p)[0]
        self.p += 8
        return v

    def s(self):
        n = self.i2()
        v = self.d[self.p:self.p + n].decode('utf-8', 'replace')
        self.p += n
        return v

    def val(self, t):
        if t == 1: return self.i1()
        if t == 2: return self.i2()
        if t == 3: return self.i4()
        if t == 4: return self.i8()
        if t == 5: return self.f4()
        if t == 6: return self.f8()
        if t == 7:
            n = self.i4(); v = self.d[self.p:self.p + n]; self.p += n; return v
        if t == 8: return self.s()
        if t == 9:
            tt = self.u1(); n = self.i4()
            return [self.val(tt) for _ in range(n)]
        if t == 10:
            o = {}
            while True:
                tt = self.u1()
                if tt == 0:
                    return o
                k = self.s()
                o[k] = self.val(tt)
        if t == 11:
            n = self.i4()
            return [self.i4() for _ in range(n)]
        if t == 12:
            n = self.i4()
            return [self.i8() for _ in range(n)]
        raise ValueError('未知 NBT 标签 %s' % t)


def read_nbt(path):
    with gzip.open(path, 'rb') as f:
        data = f.read()
    r = _Reader(data)
    t = r.u1()
    if t != 10:
        raise ValueError('不是 NBT 文件')
    r.s()
    return r.val(10)


_NAMED = {
    'air': (11, 14, 20), 'red_wool': (161, 39, 34), 'gray_wool': (125, 125, 115),
    'acacia_planks': (186, 99, 55), 'bricks': (156, 91, 68), 'dirt': (139, 90, 43),
    'smooth_stone_slab': (160, 160, 160), 'grass_block': (106, 168, 79),
    'acacia_stairs': (167, 90, 47), 'acacia_slab': (173, 95, 51),
    'stone_bricks': (122, 122, 122), 'oak_leaves': (79, 127, 44),
    'nether_bricks': (59, 31, 43), 'nether_brick_stairs': (59, 31, 43),
    'stone_brick_stairs': (120, 120, 120), 'brick_stairs': (150, 84, 63),
    'cobblestone': (117, 117, 117), 'obsidian': (36, 26, 51),
    'rose_bush': (184, 67, 74), 'bookshelf': (154, 123, 79), 'oak_stairs': (176, 138, 84),
    'quartz_block': (232, 228, 222), 'quartz_stairs': (226, 222, 216),
    'cobblestone_wall': (111, 111, 111), 'polished_andesite': (157, 157, 157),
    'quartz_slab': (230, 226, 220), 'acacia_fence': (168, 97, 58), 'stone': (138, 138, 138),
    'quartz_pillar': (228, 224, 218), 'iron_bars': (107, 114, 120),
    'red_tulip': (192, 57, 43), 'oak_log': (123, 90, 52), 'stone_brick_slab': (118, 118, 118),
    'torch': (255, 207, 92), 'oak_slab': (176, 138, 84), 'poppy': (214, 69, 65),
    'glass': (184, 216, 223), 'black_stained_glass': (43, 47, 51),
    'water': (63, 118, 228), 'lava': (211, 84, 0),
}


_CN = {
    'red_wool': '红色羊毛', 'gray_wool': '灰色羊毛', 'acacia_planks': '金合欢木板',
    'bricks': '红砖', 'dirt': '泥土', 'smooth_stone_slab': '平滑石台阶',
    'grass_block': '草方块', 'acacia_stairs': '金合欢楼梯', 'acacia_slab': '金合欢台阶',
    'stone_bricks': '石砖', 'oak_leaves': '橡木树叶', 'nether_bricks': '下界砖',
    'nether_brick_stairs': '下界砖楼梯', 'stone_brick_stairs': '石砖楼梯',
    'brick_stairs': '红砖楼梯', 'cobblestone': '圆石', 'obsidian': '黑曜石',
    'rose_bush': '玫瑰丛', 'bookshelf': '书架', 'oak_stairs': '橡木楼梯',
    'quartz_block': '石英块', 'quartz_stairs': '石英楼梯', 'cobblestone_wall': '圆石墙',
    'polished_andesite': '磨制安山岩', 'quartz_slab': '石英台阶', 'acacia_fence': '金合欢栅栏',
    'stone': '石头', 'quartz_pillar': '石英柱', 'iron_bars': '铁栏杆',
    'red_tulip': '红色郁金香', 'oak_log': '橡木原木', 'stone_brick_slab': '石砖台阶',
    'torch': '火把', 'oak_slab': '橡木台阶', 'poppy': '虞美人', 'glass': '玻璃',
    'black_stained_glass': '黑色染色玻璃', 'water': '水', 'lava': '岩浆',
}
_VER = {2975: '1.18.2', 3120: '1.19.2', 3337: '1.19.4', 3463: '1.20',
        3578: '1.20.1', 3700: '1.20.4', 3837: '1.20.6', 3953: '1.21', 4082: '1.21.4'}


def _label(name):
    k = name.replace('minecraft:', '')
    return _CN.get(k, k)


def _color(name):
    k = name.replace('minecraft:', '')
    if k in _NAMED:
        return _NAMED[k]
    if 'red_' in k: return (176, 58, 46)
    if any(x in k for x in ('stone', 'andesite', 'deepslate', 'cobble', 'tuff', 'basalt', 'bedrock')):
        return (138, 138, 134)
    if 'acacia' in k: return (181, 101, 58)
    if any(x in k for x in ('oak', 'wood', 'planks', 'log', 'fence', 'sign')):
        return (156, 118, 72)
    if 'brick' in k: return (148, 80, 62)
    if any(x in k for x in ('quartz', 'calcite', 'diorite')): return (222, 217, 210)
    if 'glass' in k: return (185, 215, 222)
    if any(x in k for x in ('leaves', 'grass', 'flower', 'tulip', 'poppy', 'bush', 'fern',
                            'vine', 'moss', 'azalea', 'roots', 'lily')):
        return (79, 127, 58)
    if 'water' in k: return (63, 118, 228)
    if 'lava' in k: return (211, 84, 0)
    if any(x in k for x in ('torch', 'lantern', 'candle', 'glow', 'light')):
        return (232, 195, 90)
    if any(x in k for x in ('wool', 'carpet', 'banner', 'bed', 'painting')):
        return (168, 111, 102)
    h = 0
    for ch in k:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    hue = h % 360
    return _hsl(hue, 0.45, 0.55)


def _hsl(h, s, l):
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = l - c / 2
    if h < 60: rgb = (c, x, 0)
    elif h < 120: rgb = (x, c, 0)
    elif h < 180: rgb = (0, c, x)
    elif h < 240: rgb = (0, x, c)
    elif h < 300: rgb = (x, 0, c)
    else: rgb = (c, 0, x)
    return tuple(int((v + m) * 255) for v in rgb)


def _category(name):
    s = name.replace('minecraft:', '')
    if name.endswith('air'): return '空气'
    if any(k in s for k in ('stone', 'brick', 'deepslate', 'cobble', 'concrete', 'terracotta',
                            'quartz', 'sandstone', 'andesite', 'diorite', 'granite', 'blackstone',
                            'tuff', 'copper', 'calcite', 'basalt')):
        return '石/砖/混凝土'
    if any(k in s for k in ('planks', 'log', 'wood', 'fence', 'door', 'stairs', 'slab',
                            'trapdoor', 'stripped')):
        return '木/楼梯'
    if 'glass' in s: return '玻璃'
    if any(k in s for k in ('light', 'lantern', 'torch', 'candle', 'glowstone',
                            'sea_lantern', 'shroomlight', 'froglight')):
        return '光源'
    if any(k in s for k in ('leaves', 'grass', 'flower', 'vine', 'moss', 'azalea',
                            'fern', 'roots', 'lily')):
        return '植物'
    if any(k in s for k in ('water', 'lava')): return '液体'
    if any(k in s for k in ('wool', 'carpet', 'banner', 'bed', 'painting', 'sign')):
        return '装饰'
    return '其他'


def analyze(path):
    root = read_nbt(path)
    md = root.get('Metadata') or {}
    regions = root.get('Regions') or {}
    rn = list(regions.keys())[0]
    r = regions[rn]
    size = r.get('Size') or {}
    X = abs(int(size.get('x') or 0))
    Y = abs(int(size.get('y') or 0))
    Z = abs(int(size.get('z') or 0))
    pal = [(p.get('Name') if isinstance(p, dict) else '') or ''
           for p in (r.get('BlockStatePalette') or [])]
    longs = [int(v) & MASK64 for v in (r.get('BlockStates') or [])]
    bits = max(1, int(math.ceil(math.log(max(2, len(pal)), 2))))
    mask = (1 << bits) - 1
    vol = X * Y * Z
    counts = [0] * len(pal)
    layers = [0] * Y
    sy = [-1] * (X * Z)
    sp = [0] * (X * Z)
    bp = 0
    step = bits
    t0 = time.time()
    for y in range(Y):
        for z in range(Z):
            row = z * X
            for x in range(X):
                li = bp >> 6
                off = bp & 63
                bp += step
                v = (longs[li] >> off) & mask
                if off + step > 64:
                    v |= (longs[li + 1] << (64 - off)) & mask
                name = pal[v] if v < len(pal) else ''
                counts[v] += 1
                if name.endswith('air'):
                    continue
                layers[y] += 1
                col = row + x
                if y > sy[col]:
                    sy[col] = y
                    sp[col] = v
    elapsed = time.time() - t0
    total = sum(counts)
    used = [(pal[i], counts[i], _category(pal[i])) for i in range(len(pal)) if counts[i]]
    used.sort(key=lambda t: -t[1])
    solid = [(n, c, cat) for n, c, cat in used if not n.endswith('air')]
    nonair = sum(c for _, c, _ in solid)
    cats = {}
    for n, c, cat in solid:
        cats[cat] = cats.get(cat, 0) + c
    return {
        'meta': {
            'name': md.get('Name') or 'Unnamed',
            'author': md.get('Author') or '',
            'created': md.get('TimeCreated') or 0,
            'region': rn,
            'pos': r.get('Position') or {},
        },
        'dims': (X, Y, Z), 'volume': vol, 'total': total, 'nonair': nonair,
        'blocks': len(solid), 'elapsed': elapsed,
        'top': solid[:12], 'cats': cats,
        'tiles': len(r.get('TileEntities') or []), 'entities': len(r.get('Entities') or []),
        'pal': pal, 'colors': [_color(n) for n in pal],
        'sy': sy, 'sp': sp, 'layers': layers,
        'dataVersion': root.get('MinecraftDataVersion'),
    }


_FONT_CANDS = [
    '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
]


def _font(size):
    from PIL import ImageFont
    for p in _FONT_CANDS:
        try:
            if os.path.isfile(p):
                return ImageFont.truetype(p, size, index=0)
        except Exception:
            continue
    return ImageFont.load_default()


def render(rep, out_path, title='投影解析'):
    from PIL import Image, ImageDraw
    X, Y, Z = rep['dims']
    W, H = 1080, 700
    img = Image.new('RGB', (W, H), (12, 16, 23))
    d = ImageDraw.Draw(img)
    f_title = _font(28)
    f_sub = _font(15)
    f_body = _font(17)
    f_small = _font(13)

    # 俯视图：按最高方块上色、高度加亮
    top = Image.new('RGB', (X, Z))
    maxh = max(1, max(rep['sy']))
    colors = rep['colors']
    fill = [0] * (X * Z)
    for i in range(X * Z):
        h = rep['sy'][i]
        c = colors[rep['sp'][i]] if 0 <= rep['sp'][i] < len(colors) else (40, 40, 40)
        f = 0.25 if h < 0 else 0.55 + 0.45 * (h / maxh)
        fill[i] = (min(255, int(c[0] * f)), min(255, int(c[1] * f)), min(255, int(c[2] * f)))
    top.putdata(fill)
    th = 520
    tw = max(1, int(X * th / Z))
    top = top.resize((tw, th), Image.NEAREST)
    ix, iy = 26, 92
    img.paste(top, (ix, iy))
    d.rectangle([ix - 2, iy - 2, ix + tw + 1, iy + th + 1], outline=(40, 52, 68))

    d.text((26, 20), title, font=f_title, fill=(238, 244, 255))
    ver = _VER.get(int(rep['dataVersion'] or 0), str(rep['dataVersion']))
    sub = '作者 %s     Minecraft %s' % (rep['meta']['author'] or '未知', ver)
    d.text((28, 58), sub, font=f_sub, fill=(126, 143, 163))

    x0 = ix + tw + 30
    y0 = 92
    lines = [
        ('尺寸', '%d × %d × %d' % (X, Y, Z)),
        ('体积', '{:,}'.format(rep['volume'])),
        ('非空气', '{:,}'.format(rep['nonair'])),
        ('方块种类', str(rep['blocks'])),
        ('方块实体', '{:,}'.format(rep['tiles'])),
        ('实体', '{:,}'.format(rep['entities'])),
    ]
    for i, (k, v) in enumerate(lines):
        yy = y0 + i * 30
        d.text((x0, yy), k, font=f_body, fill=(126, 143, 163))
        d.text((x0 + 130, yy), v, font=f_body, fill=(226, 234, 245))

    # 材料条（留出右侧数量空间）
    ybars = y0 + len(lines) * 30 + 16
    d.text((x0, ybars), '主要材料', font=f_body, fill=(180, 194, 212))
    maxc = max(1, rep['top'][0][1]) if rep['top'] else 1
    bar_x = x0 + 12
    bar_w = W - bar_x - 150
    for i, (name, cnt, _cat) in enumerate(rep['top'][:8]):
        yy = ybars + 32 + i * 34
        d.text((bar_x, yy), _label(name)[:16], font=f_small, fill=(180, 194, 212))
        d.rectangle([bar_x, yy + 17, bar_x + bar_w, yy + 28], fill=(28, 37, 50))
        w = max(2, int(bar_w * cnt / maxc))
        d.rectangle([bar_x, yy + 17, bar_x + w, yy + 28], fill=_color(name))
        d.text((bar_x + w + 6, yy + 13), '{:,}'.format(cnt), font=f_small, fill=(126, 143, 163))

    d.text((26, H - 26), '解析耗时 %.1fs · 生成时间 %s'
           % (rep['elapsed'], time.strftime('%Y-%m-%d %H:%M')), font=f_small, fill=(90, 104, 122))
    img.save(out_path, 'PNG')
    return out_path


def summary_text(rep, filename=''):
    X, Y, Z = rep['dims']
    parts = [
        '投影解析' + (' · ' + filename if filename else ''),
        '尺寸 %d×%d×%d · 体积 %s 格' % (X, Y, Z, '{:,}'.format(rep['volume'])),
        '非空气 %s · 方块种类 %d · 方块实体 %s · 实体 %d'
        % ('{:,}'.format(rep['nonair']), rep['blocks'],
           '{:,}'.format(rep['tiles']), rep['entities']),
    ]
    if rep['meta']['author']:
        parts.append('作者：%s' % rep['meta']['author'])
    top = [_label(n) + ' ' + '{:,}'.format(c) for n, c, _ in rep['top'][:3]]
    if top:
        parts.append('主材：' + ' / '.join(top))
    parts.append('耗时 %.1fs' % rep['elapsed'])
    return '\n'.join(parts)


def build_report(path, filename=''):
    rep = analyze(path)
    out = os.path.join(tempfile.gettempdir(), 'litematic-%d.png' % int(time.time() * 1000))
    try:
        render(rep, out, title='投影解析' + (' · ' + filename if filename else ''))
    except Exception:
        out = ''
    return summary_text(rep, filename), out
