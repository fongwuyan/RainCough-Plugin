"""Render a 64x64 Minecraft skin from a structured LLM spec (JSON).

Spec schema (as produced by the local LLM):

{
  "palette": {
    "skin": "#E8B98A", "hair": "#4A3620", "shirt": "#3366CC",
    "pants": "#223366", "shoes": "#222222", "sleeve": "#2A4FA0",
    "accent": "#FFFFFF", "eye": "#1A1A1A"
  },
  "head":   {"hair_style": "full|fringe|spiky|bald", "face": "default|happy|serious", "hair_parts": ["top","back","sides"]},
  "torso":  {"pattern": "solid|stripe_v|stripe_h|grid|jacket|collar", "accent": "#FFFFFF", "belt": false},
  "arms":   {"pattern": "solid|stripe_v|grid", "sleeve": true},
  "legs":   {"pattern": "solid|stripe_v|grid", "shoes": true}
}
"""

from PIL import Image
import numpy as np

TEX = 64

HEX_RE = None


def _hex(c):
    if not isinstance(c, str):
        c = '#888888'
    c = c.strip().lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    if len(c) != 6:
        c = '888888'
    try:
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    except Exception:
        return (136, 136, 136, 255)


def _shade(rgb, f):
    return tuple(max(0, min(255, int(v * f))) for v in rgb[:3]) + (255,)


def _box_uvs(u, v, w, h, d):
    """Same UV layout as mcskin plugin: standard 64x64 (legacy + overlay rows)."""
    return {
        'top': (u + d, v, w, d),
        'bottom': (u + w + d, v, w, d),
        'left': (u, v + d, d, h),
        'front': (u + d, v + d, w, h),
        'right': (u + w + d, v + d, d, h),
        'back': (u + w + d * 2, v + d, w, h),
    }


def _fill(img, uv, color, pattern=None, accent=None):
    x, y, w, h = uv
    if pattern is None:
        pattern = 'solid'
    base = _hex(color)
    acc = _hex(accent) if accent else _shade(base, 1.2)
    px = img.load()
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            c = base
            if pattern == 'stripe_v':
                c = acc if ((xx - x) % 2 == 0) else base
            elif pattern == 'stripe_h':
                c = acc if ((yy - y) % 2 == 0) else base
            elif pattern == 'grid':
                c = acc if (((xx - x) % 2 == 0) or ((yy - y) % 2 == 0)) else base
            elif pattern == 'jacket':
                c = acc if (yy - y) >= max(1, h - 2) else base
            elif pattern == 'collar':
                if (yy - y) < 2 and (xx - x) in (w // 2 - 1, w // 2):
                    c = _hex('#FFFFFF') if not accent else acc
            px[xx, yy] = c


def _draw_face(img, head_front_uv, eye_color='#1A1A1A', mouth=True):
    """Pixel eyes + optional mouth on the 8x8 head front face."""
    x, y, w, h = head_front_uv
    eye = _hex(eye_color)
    px = img.load()
    # classic 8x8 face: eyes at rows 3-4, cols 1 and 5
    for ex in (x + 1, x + 2):
        for ey in (y + 3, y + 4):
            px[ex, ey] = eye
    for ex in (x + 5, x + 6):
        for ey in (y + 3, y + 4):
            px[ex, ey] = eye
    if mouth:
        for mx in (x + 3, x + 4):
            px[mx, y + 6] = eye


def _hair_top(img, head_top_uv, hair_color):
    x, y, w, h = head_top_uv
    c = _hex(hair_color)
    px = img.load()
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px[xx, yy] = c


def render_skin(spec, model='wide'):
    """Render a 64x64 RGBA skin from an LLM spec dict."""
    if not isinstance(spec, dict):
        spec = {}
    pal = spec.get('palette') or {}
    head = spec.get('head') or {}
    torso = spec.get('torso') or {}
    arms = spec.get('arms') or {}
    legs = spec.get('legs') or {}

    img = Image.new('RGBA', (TEX, TEX), (0, 0, 0, 0))

    aw = 3 if model == 'slim' else 4

    head_uv = _box_uvs(0, 0, 8, 8, 8)
    head2_uv = _box_uvs(32, 0, 8, 8, 8)
    rleg_uv = _box_uvs(0, 16, 4, 12, 4)
    rleg2_uv = _box_uvs(0, 32, 4, 12, 4)
    body_uv = _box_uvs(16, 16, 8, 12, 4)
    body2_uv = _box_uvs(16, 32, 8, 12, 4)
    rarm_uv = _box_uvs(40, 16, aw, 12, 4)
    rarm2_uv = _box_uvs(40, 32, aw, 12, 4)
    larm_uv = _box_uvs(32, 48, aw, 12, 4)
    larm2_uv = _box_uvs(48, 48, aw, 12, 4)
    lleg_uv = _box_uvs(16, 48, 4, 12, 4)
    lleg2_uv = _box_uvs(0, 48, 4, 12, 4)

    skin_c = pal.get('skin', '#E8B98A')
    hair_c = pal.get('hair', '#4A3620')
    shirt_c = pal.get('shirt', '#3366CC')
    sleeve_c = pal.get('sleeve', shirt_c)
    pants_c = pal.get('pants', '#223366')
    shoes_c = pal.get('shoes', '#222222')
    accent_c = pal.get('accent', '#FFFFFF')
    eye_c = pal.get('eye', '#1A1A1A')

    # head base
    for face, uv in head_uv.items():
        _fill(img, uv, skin_c, 'solid')
    # hair style
    hstyle = (head.get('hair_style') or 'full').lower()
    if hstyle in ('full', 'fringe', 'spiky'):
        _hair_top(img, head_uv['top'], hair_c)
        if hstyle == 'full':
            for face in ('back', 'left', 'right'):
                _fill(img, head_uv[face], hair_c, 'solid')
        elif hstyle == 'fringe':
            x, y, w, h = head_uv['back']
            _fill(img, (x, y, w, 3), hair_c, 'solid')
        elif hstyle == 'spiky':
            _hair_top(img, head_uv['top'], hair_c)
            for face in ('back', 'left', 'right'):
                _fill(img, head_uv[face], hair_c, 'solid')
    if hstyle in ('fringe',):
        # fringe overlay on front top
        x, y, w, h = head_uv['front']
        _fill(img, (x, y, w, 2), hair_c, 'solid')
    # face
    fstyle = (head.get('face') or 'default').lower()
    _draw_face(img, head_uv['front'], eye_c, mouth=(fstyle != 'serious'))

    # torso
    tpat = (torso.get('pattern') or 'solid').lower()
    tacc = torso.get('accent') or accent_c
    for face, uv in body_uv.items():
        if face == 'front' and tpat == 'collar':
            _fill(img, uv, shirt_c, 'collar', tacc)
        else:
            _fill(img, uv, shirt_c, tpat, tacc)
    if torso.get('belt'):
        for uv in (body_uv['front'], body_uv['back']):
            x, y, w, h = uv
            _fill(img, (x, y + h - 2, w, 1), pal.get('belt', '#111111') or '#111111', 'solid')

    # arms
    apat = (arms.get('pattern') or 'solid').lower()
    arm_c = sleeve_c if arms.get('sleeve') else skin_c
    aacc = arms.get('accent') or accent_c
    for uv in (rarm_uv, rarm2_uv, larm_uv, larm2_uv):
        for face, fuv in uv.items():
            _fill(img, fuv, arm_c, apat, aacc)

    # legs
    lpat = (legs.get('pattern') or 'solid').lower()
    lacc = legs.get('accent') or accent_c
    for uv in (rleg_uv, rleg2_uv, lleg_uv, lleg2_uv):
        for face, fuv in uv.items():
            _fill(img, fuv, pants_c, lpat, lacc)
        if legs.get('shoes'):
            x, y, w, h = uv['front']
            _fill(img, (x, y + h - 2, w, 2), shoes_c, 'solid')
            x, y, w, h = uv['back']
            _fill(img, (x, y + h - 2, w, 2), shoes_c, 'solid')

    # simple ambient shading on sides/tops for depth
    img = _apply_shading(img, head_uv, body_uv, rarm_uv, rleg_uv)

    return img


def _apply_shading(img, head_uv, body_uv, rarm_uv, rleg_uv):
    """Light top, dark bottom/side for subtle depth (like legacy shading)."""
    arr = np.array(img).astype(np.float32)
    a = arr[..., 3]
    shade = np.ones_like(a)
    for uv in (head_uv, body_uv, rarm_uv, rleg_uv):
        x, y, w, h = uv['top']
        shade[y:y + h, x:x + w] *= 1.12
        x, y, w, h = uv['bottom']
        shade[y:y + h, x:x + w] *= 0.82
        x, y, w, h = uv['left']
        shade[y:y + h, x:x + w] *= 0.95
        x, y, w, h = uv['back']
        shade[y:y + h, x:x + w] *= 0.9
    mask = (a > 0)[..., None]
    arr[..., :3] = np.clip(arr[..., :3] * shade[..., None], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')
