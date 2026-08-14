import os
import io
import json
import time
import random
import hashlib
import shutil
import base64
import numpy as np
from PIL import Image, ImageEnhance
from flask import request, jsonify
from plugins.base import Plugin
from plugins.yulotool_common import save_uploads, new_session
from plugins.sd_common import (
    get_pipe, get_img2img, resolve_model, list_models,
    new_job_id, JobManager, DEFAULT_MODEL_DIR,
)
from plugins.llm_common import (
    llm_generate, extract_json, enqueue_llm, get_llm_job,
    cancel_llm_job, new_llm_job_id, set_llm_runner,
    list_llm_models,
)
from plugins.mcskin.skin_render import render_skin

try:
    from torch import inference_mode as _no_grad_ctx
except Exception:
    _no_grad_ctx = None

try:
    import cv2
    HAVE_CV2 = True
except Exception:
    HAVE_CV2 = False

PLUGIN_ROOT = os.path.dirname(__file__)
CACHE_DIR = os.path.join(PLUGIN_ROOT, 'cache')

TEX = 64

DEFAULT_P = {
    'center_x': 50.0,
    'head_top': 5.0, 'head_bot': 17.0, 'body_bot': 55.0, 'leg_bot': 92.0,
    'head_half_w': 25.0, 'body_half_w': 36.0, 'arm_half_w': 9.0,
    'arm_w': 8.0, 'leg_w': 17.0,
    'lighting': 40.0,
    'overlay_alpha': 160.0,
    'bg_removal': True,
}


def _has_real_alpha(src):
    """True if the image has meaningful transparency variation (not all 255)."""
    a = src.getchannel('A')
    hist = a.histogram()
    total = sum(hist)
    if total == 0:
        return False
    nopaque = sum(hist[:240])
    return nopaque / float(total) > 0.01


def _remove_bg(src):
    """Remove background when image has no usable alpha (opaque/white bg)."""
    if not HAVE_CV2:
        return src
    if _has_real_alpha(src):
        return src
    img = np.array(src.convert('RGB'))
    h, w = img.shape[:2]
    if w < 8 or h < 8:
        return src
    # downscale for speed if large
    scale = 1.0
    work = img
    if w * h > 900 * 900:
        scale = min(1.0, (900.0 / max(w, h)))
        work = cv2.resize(img, (int(w * scale), int(h * scale)))
    mask = np.zeros(work.shape[:2], np.uint8)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    rw, rh = work.shape[1], work.shape[0]
    rect = (max(1, int(rw * 0.02)), max(1, int(rh * 0.02)),
            max(2, int(rw * 0.96)), max(2, int(rh * 0.96)))
    try:
        cv2.grabCut(work, mask, rect, bgd, fgd, 3, cv2.GC_INIT_WITH_RECT)
        fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        # flood-fill edges to kill border-ish background kept by grabcut
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        # re-open holes
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    except Exception:
        return src
    if scale != 1.0:
        fg = cv2.resize(fg, (w, h), interpolation=cv2.INTER_NEAREST)
    alpha = fg
    rgb = img
    out = np.dstack([rgb, alpha])
    return Image.fromarray(out, 'RGBA')


def _silhouette_rows(src):
    """Return per-row: (width, mid) for opaque pixels."""
    W, H = src.size
    a = src.getchannel('A')
    arr = np.asarray(a)
    step = max(1, H // 400)
    widths, mids = [], []
    for y in range(0, H, step):
        row = arr[y, :]
        cols = np.nonzero(row > 60)[0]
        if cols.size:
            widths.append(int(cols[-1] - cols[0]))
            mids.append(float((cols[0] + cols[-1]) / 2.0))
        else:
            widths.append(0)
            mids.append(W / 2.0)
    return widths, mids, step


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _tight_box(src, box):
    x0, y0, x1, y1 = box
    crop = src.crop((x0, y0, x1, y1))
    bbox = crop.getchannel('A').getbbox()
    if bbox is None:
        return box
    ox, oy, ex, ey = bbox
    return (x0 + ox, y0 + oy, x0 + ex, y0 + ey)


def _crop_cover(src, box, tw, th):
    box = _tight_box(src, box)
    x0, y0, x1, y1 = box
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    region = src.crop((x0, y0, x1, y1))
    scale = max(tw / bw, th / bh)
    nw = max(1, int(round(bw * scale)))
    nh = max(1, int(round(bh * scale)))
    region = region.resize((nw, nh), Image.LANCZOS)
    cx = (nw - tw) // 2
    cy = (nh - th) // 2
    return region.crop((cx, cy, cx + tw, cy + th))


def _bright(img, factor):
    return ImageEnhance.Brightness(img).enhance(factor)


def _alpha(img, factor):
    a = img.split()[3].point(lambda v: int(v * factor))
    r, g, b = img.split()[:3]
    return Image.merge('RGBA', (r, g, b, a))


def _regions(src, p):
    W, H = src.size
    cx = int(W * p['center_x'] / 100.0)
    hw = int(W * p['head_half_w'] / 200.0)
    bw = int(W * p['body_half_w'] / 200.0)
    aw = int(W * p['arm_w'] / 200.0) if p.get('arm_w') else int(W * p['arm_half_w'] / 200.0)
    lw = int(W * p['leg_w'] / 200.0) if p.get('leg_w') else int(bw * 3 // 5)
    head_box = (cx - hw, int(H * p['head_top'] / 100.0), cx + hw, int(H * p['head_bot'] / 100.0))
    ty0 = int(H * p['head_bot'] / 100.0)
    ty1 = int(H * p['body_bot'] / 100.0)
    torso_box = (cx - bw, ty0, cx + bw, ty1)
    arm_l_box = (cx - bw - aw, ty0, cx - bw, ty1)
    arm_r_box = (cx + bw, ty0, cx + bw + aw, ty1)
    ly0 = int(H * p['body_bot'] / 100.0)
    ly1 = int(H * p['leg_bot'] / 100.0)
    leg_l_box = (cx - lw, ly0, cx, ly1)
    leg_r_box = (cx, ly0, cx + lw, ly1)
    return {
        'head': head_box, 'torso': torso_box,
        'arm_l': arm_l_box, 'arm_r': arm_r_box,
        'leg_l': leg_l_box, 'leg_r': leg_r_box,
    }


def _auto_detect(src):
    W, H = src.size
    widths, mids, step = _silhouette_rows(src)
    maxw = max(widths) or 1
    # smooth
    k = max(1, len(widths) // 60)
    sm = []
    for i in range(len(widths)):
        lo, hi = max(0, i - k), min(len(widths), i + k + 1)
        sm.append(sum(widths[lo:hi]) / (hi - lo))
    # body bbox from alpha
    b = src.getchannel('A').getbbox()
    body_h = (b[3] - b[1]) if b else H
    body_cx = (b[0] + b[2]) / 2.0 if b else W / 2.0
    body_ymin = b[1] if b else 0
    body_ymax = b[3] if b else H
    # head: first row wide enough (>0.30*maxw) until shoulders (>0.62*maxw)
    head_top = int(H * 0.05)
    head_bot = head_top
    got_top = False
    for i, w in enumerate(sm):
        y = i * step
        if not got_top:
            if w > maxw * 0.30:
                head_top = y
                got_top = True
            continue
        if w > maxw * 0.62:
            head_bot = y
            break
        head_bot = y
    if head_bot - head_top < int(H * 0.04):
        head_bot = head_top + int(H * 0.12)
    # torso: from head_bot, first sustained narrowing below 0.58*maxw after +10%
    body_bot = int(H * 0.68)
    narrow_run = 0
    for i, w in enumerate(sm):
        y = i * step
        if y <= head_bot + int(H * 0.10):
            continue
        if w < maxw * 0.58:
            narrow_run += 1
        else:
            narrow_run = 0
        if narrow_run * step > int(H * 0.04):
            body_bot = y
            break
    # leg: last row with meaningful width
    leg_bot = int(H * 0.97)
    for i in range(len(sm) - 1, -1, -1):
        if sm[i] > maxw * 0.35:
            leg_bot = i * step
            break
    if b:
        leg_bot = min(leg_bot, b[3])
    bw = (b[2] - b[0]) / 2.0 if b else maxw / 2.0
    body_half_w = bw / W * 100.0

    # arm width: max of left/right protrusion vs torso within torso band
    arm_w = body_half_w * 0.26
    leg_w = body_half_w * 0.5
    if HAVE_CV2 and b:
        a = np.asarray(src.getchannel('A'))
        y0 = int(head_bot)
        y1 = int(body_bot)
        y0 = max(0, min(H - 1, y0))
        y1 = max(y0 + 1, min(H, y1))
        band = a[y0:y1, :]
        if band.shape[0] > 0 and band.shape[1] > 0:
            proj = (band > 60).sum(axis=0)
            cx = int(round(body_cx))
            lo = max(0, cx - int(bw))
            hi = min(W, cx + int(bw) + 1)
            max_in = proj[lo:hi].max() if hi > lo else 0
            l_out = proj[max(0, cx - int(bw * 1.8)):lo].max() if lo > 0 else 0
            r_out = proj[hi:min(W, cx + int(bw * 1.8))].max() if hi < W else 0
            out = max(l_out, r_out)
            if max_in > 0:
                arm_w = body_half_w * min(1.2, float(out) / max_in + 0.05)
    return {
        'center_x': _clamp(body_cx / W * 100.0, 20, 80),
        'head_top': _clamp(head_top / H * 100.0, 1, 40),
        'head_bot': _clamp(head_bot / H * 100.0, 8, 55),
        'body_bot': _clamp(body_bot / H * 100.0, 25, 85),
        'leg_bot': _clamp(leg_bot / H * 100.0, 55, 100),
        'head_half_w': _clamp(min(22.0, body_half_w * 0.45), 8, 30),
        'body_half_w': _clamp(body_half_w, 18, 45),
        'arm_half_w': _clamp(body_half_w * 0.26, 5, 14),
        'arm_w': _clamp(arm_w, 5, 22),
        'leg_w': _clamp(leg_w, 10, 30),
        '_body_h': _clamp(body_h / H * 100.0, 20, 100),
    }


def _build_skin(src, model, p=None):
    W, H = src.size
    slim = model == 'slim'
    p = p or dict(DEFAULT_P)
    regs = _regions(src, p)

    aw = 3 if slim else 4

    def split_h(box, k):
        x0, y0, x1, y1 = box
        mid = x0 + (x1 - x0) * k
        return (x0, y0, int(mid), y1), (int(mid), y0, x1, y1)

    def split_v(box, k):
        x0, y0, x1, y1 = box
        mid = y0 + (y1 - y0) * k
        return (x0, y0, x1, int(mid)), (x0, int(mid), x1, y1)

    def srcs_of(box):
        l, r = split_h(box, 0.5)
        t, b = split_v(box, 0.5)
        return {
            'front': box, 'back': box,
            'left': l, 'right': r,
            'top': t, 'bottom': b,
        }

    head_srcs = srcs_of(regs['head'])
    body_srcs = srcs_of(regs['torso'])
    arm_r_srcs = srcs_of(regs['arm_r'])
    arm_l_srcs = srcs_of(regs['arm_l'])
    leg_r_srcs = srcs_of(regs['leg_r'])
    leg_l_srcs = srcs_of(regs['leg_l'])

    # Standard 64x64 layout (matches skinview3d setSkinUVs)
    def box_uvs(u, v, w, h, d):
        return {
            'top': (u + d, v, w, d),
            'bottom': (u + w + d, v, w, d),
            'left': (u, v + d, d, h),
            'front': (u + d, v + d, w, h),
            'right': (u + w + d, v + d, d, h),
            'back': (u + w + d * 2, v + d, w, h),
        }

    head_uv = box_uvs(0, 0, 8, 8, 8)
    head2_uv = box_uvs(32, 0, 8, 8, 8)
    rleg_uv = box_uvs(0, 16, 4, 12, 4)
    rleg2_uv = box_uvs(0, 32, 4, 12, 4)
    body_uv = box_uvs(16, 16, 8, 12, 4)
    body2_uv = box_uvs(16, 32, 8, 12, 4)
    rarm_uv = box_uvs(40, 16, aw, 12, 4)
    rarm2_uv = box_uvs(40, 32, aw, 12, 4)
    larm_uv = box_uvs(32, 48, aw, 12, 4)
    larm2_uv = box_uvs(48, 48, aw, 12, 4)
    lleg_uv = box_uvs(16, 48, 4, 12, 4)
    lleg2_uv = box_uvs(0, 48, 4, 12, 4)

    img = Image.new('RGBA', (TEX, TEX), (0, 0, 0, 0))

    FACE_BRIGHT = {
        'front': 1.0,
        'right': 1.06,
        'left': 0.92,
        'top': 1.12,
        'bottom': 0.78,
        'back': 0.85,
    }
    # lighting: 0 => pure source colors, 100 => full legacy shading
    lighting = _clamp(float(p.get('lighting', 40.0)), 0, 100) / 100.0
    def bright_of(face, base):
        if lighting <= 0.01:
            return base
        return base * (1.0 - lighting) + base * FACE_BRIGHT.get(face, 1.0) * lighting

    overlay_alpha = _clamp(float(p.get('overlay_alpha', 160.0)), 0, 255)

    def paint(srcs, uv_map, target, alpha=255, base_bright=1.0):
        for face, uv in uv_map.items():
            u, v, w, h = uv
            tile = _crop_cover(src, srcs[face], w, h)
            tile = _bright(tile, bright_of(face, base_bright))
            if alpha < 255:
                tile = _alpha(tile, alpha / 255.0)
            target.paste(tile, (u, v))

    paint(head_srcs, head_uv, img, base_bright=1.0)
    paint(body_srcs, body_uv, img, base_bright=0.95)
    paint(arm_r_srcs, rarm_uv, img, base_bright=0.95)
    paint(leg_r_srcs, rleg_uv, img, base_bright=0.9)

    oa = overlay_alpha
    paint(head_srcs, head2_uv, img, alpha=oa, base_bright=1.08)
    paint(body_srcs, body2_uv, img, alpha=oa, base_bright=1.0)
    paint(arm_r_srcs, rarm2_uv, img, alpha=oa, base_bright=1.0)
    paint(leg_r_srcs, rleg2_uv, img, alpha=oa, base_bright=0.95)
    paint(leg_l_srcs, lleg_uv, img, alpha=oa, base_bright=0.9)
    paint(leg_l_srcs, lleg2_uv, img, alpha=oa, base_bright=0.95)
    paint(arm_l_srcs, larm_uv, img, alpha=oa, base_bright=0.95)
    paint(arm_l_srcs, larm2_uv, img, alpha=oa, base_bright=1.0)

    return img


PAINT_REGIONS = ['head', 'torso', 'arm_l', 'arm_r', 'leg_l', 'leg_r']


def _compose_on_white(region, size):
    """Composite region onto white and upscale to a square for img2img."""
    white = Image.new('RGBA', region.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, region).convert('RGB')
    return flat.resize((size, size), Image.LANCZOS)


def _paint_region(pipe2, region, prompt, neg, steps, cfg, strength, seed, size=512):
    init = _compose_on_white(region, size)
    import torch
    generator = None
    if seed >= 0:
        generator = torch.Generator().manual_seed(seed)
    res = pipe2(
        prompt=prompt or '',
        negative_prompt=neg or None,
        image=init,
        strength=max(0.05, min(0.95, float(strength or 0.45))),
        num_inference_steps=max(1, int(steps or 20)),
        guidance_scale=float(cfg or 7),
        generator=generator,
    )
    out = res.images[0].convert('RGBA')
    w, h = region.size
    out = out.resize((w, h), Image.LANCZOS)
    a = region.split()[3]
    r, g, b = out.split()[:3]
    return Image.merge('RGBA', (r, g, b, a))


def _run_paint(job):
    try:
        jid = job['id']
        src_path = job['_src_path']
        src = Image.open(src_path).convert('RGBA')
        if job.get('bg_removal'):
            src = _remove_bg(src)
        p = job['params']
        model_dir = job.get('model_dir') or DEFAULT_MODEL_DIR
        model_path = resolve_model(model_dir, job.get('model'))
        if not model_path:
            raise ValueError('未找到可用的 SD 模型，请检查模型目录')

        cfg = {'easy_negative': False, 'fix_vae': True}
        job['status'] = 'loading'
        pipe = get_pipe(model_path, None, model_dir, cfg)
        pipe2 = get_img2img(pipe)

        regs = _regions(src, p)
        painted = src.copy()
        total = len(PAINT_REGIONS)
        job['status'] = 'running'
        job['progress'] = 5
        for i, name in enumerate(PAINT_REGIONS):
            job['region'] = name
            box = regs[name]
            tight = _tight_box(src, box)
            region = src.crop(tight)
            if region.getchannel('A').getbbox() is None:
                job['progress'] = 5 + int((i + 1) / total * 90)
                continue
            new_region = _paint_region(
                pipe2, region,
                job.get('prompt'), job.get('negative_prompt'),
                job.get('steps'), job.get('cfg'),
                job.get('strength'), job.get('seed', -1),
            )
            painted.paste(new_region, tight)
            job['progress'] = 5 + int((i + 1) / total * 90)

        body = (job.get('body') or 'wide').lower()
        if body not in ('wide', 'slim'):
            body = 'wide'
        skin = _build_skin(painted, body, p)
        os.makedirs(CACHE_DIR, exist_ok=True)
        name = jid + '.png'
        out_path = os.path.join(CACHE_DIR, name)
        skin.save(out_path, 'PNG')
        buf = io.BytesIO()
        skin.save(buf, 'PNG')
        job['url'] = '/api/plugins/mcskin/cache/' + name
        job['size'] = list(skin.size)
        job['png'] = base64.b64encode(buf.getvalue()).decode()
        job['progress'] = 100
        job['status'] = 'done'
    except Exception as e:
        import traceback
        traceback.print_exc()
        job['status'] = 'error'
        job['error'] = str(e)
    finally:
        try:
            if job.get('_src_path') and os.path.isfile(job['_src_path']):
                os.remove(job['_src_path'])
        except Exception:
            pass


class _PaintManager(JobManager):
    def _run(self, job):
        _run_paint(job)


_paint_manager = _PaintManager()

HISTORY_FILE = os.path.join(CACHE_DIR, 'history.json')

TEXT2SKIN_STYLES = {
    'cyberpunk': '赛博朋克：霓虹灯、机械装甲、发光线条、科技感',
    'cute': '可爱：圆润、粉嫩、萌系、柔和',
    'mecha': '机甲：金属装甲、机械结构、硬朗',
    'ancient': '古风：汉服、飘逸、水墨、传统纹样',
    'animal': '动物：毛茸茸、兽耳、尾巴、自然色',
    'star': '星空：深蓝夜空、星光点缀、梦幻',
    'magic': '魔法：法袍、符文、神秘紫蓝、奇幻',
    'modern': '现代：休闲装、街头、简约、潮流',
}

TEXT2SKIN_TONES = {
    'any': '色调不限，自由发挥',
    'warm': '使用暖色调（橙、红、黄、棕）',
    'cool': '使用冷色调（蓝、青、紫、灰）',
    'bw': '使用黑白灰单色系',
}

TEXT2SKIN_SPEC_SCHEMA = '''请严格输出一个 JSON 对象（不要输出任何其他文字），描述 Minecraft 64x64 皮肤的配色与图案。schema：
{
  "palette": {"skin":"#肤色", "hair":"#发色", "shirt":"#上衣色", "pants":"#裤色", "shoes":"#鞋色", "sleeve":"#袖色", "accent":"#点缀色", "eye":"#眼睛色"},
  "head": {"hair_style":"full|fringe|spiky|bald", "face":"default|happy|serious"},
  "torso": {"pattern":"solid|stripe_v|stripe_h|grid|jacket|collar", "accent":"#点缀色", "belt":true或false},
  "arms": {"pattern":"solid|stripe_v|grid", "sleeve":true或false},
  "legs": {"pattern":"solid|stripe_v|grid", "shoes":true或false}
}'''


def _build_spec_prompt(prompt, style, tone, strength):
    style_desc = TEXT2SKIN_STYLES.get(style, '')
    tone_desc = TEXT2SKIN_TONES.get(tone, TEXT2SKIN_TONES['any'])
    strength_note = ''
    s = int(strength or 3)
    if s >= 4:
        strength_note = '风格要非常强烈、特征鲜明夸张。'
    elif s <= 2:
        strength_note = '风格要含蓄克制、尽量贴近普通休闲装。'
    user = '角色描述：%s\n风格要求：%s\n%s\n%s\n请只输出 JSON。' % (prompt, style_desc, tone_desc, strength_note)
    return TEXT2SKIN_SPEC_SCHEMA, user


def _render_candidate(spec, model='wide'):
    try:
        img = render_skin(spec, model)
    except Exception as e:
        img = render_skin({}, model)
    os.makedirs(CACHE_DIR, exist_ok=True)
    name = '%s_%s.png' % (new_llm_job_id(), random.randint(1000, 9999))
    out = os.path.join(CACHE_DIR, name)
    img.save(out, 'PNG')
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return {
        'url': '/api/plugins/mcskin/cache/' + name,
        'png': base64.b64encode(buf.getvalue()).decode(),
        'feedback': None,
    }


def _load_history():
    if os.path.isfile(HISTORY_FILE):
        try:
            return json.load(open(HISTORY_FILE, 'r', encoding='utf-8'))
        except Exception:
            return []
    return []


def _save_history(items):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def _run_text2skin(job):
    try:
        job['status'] = 'loading'
        job['progress'] = 5
        system_p, user_p = _build_spec_prompt(
            job.get('prompt') or '一个普通的角色', job.get('style'),
            job.get('tone'), job.get('strength'))
        job['status'] = 'running'
        raw = llm_generate(system_p, user_p, max_new_tokens=900, temperature=0.9)
        spec = extract_json(raw)
        if not spec:
            raise ValueError('LLM 未返回有效规格: %s' % (raw or '')[:200])
        job['spec'] = spec
        job['progress'] = 55
        cand = _render_candidate(spec, job.get('body') or 'wide')
        job['progress'] = 90
        item = {
            'id': job['id'],
            'created': time.time(),
            'prompt': job.get('prompt'),
            'style': job.get('style'),
            'tone': job.get('tone'),
            'strength': job.get('strength'),
            'model': job.get('body') or 'wide',
            'spec': spec,
            'candidates': [cand],
        }
        history = _load_history()
        history.insert(0, item)
        _save_history(history[:200])
        job['candidate'] = cand
        job['progress'] = 100
        job['status'] = 'done'
    except Exception as e:
        import traceback
        traceback.print_exc()
        job['status'] = 'error'
        job['error'] = str(e)


set_llm_runner(_run_text2skin)


class McSkinPlugin(Plugin):
    name = 'mcskin'
    label = '图片转皮肤'
    icon = ''
    description = '图片转 MC Java 皮肤：全身立绘映射、底+叠层、Steve/Alex 模型、3D 预览'

    def _register_routes(self):
        @self.route('/detect', methods=['POST'])
        def mcskin_detect():
            session = new_session(self.name)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            path = saved[0]['path']
            try:
                src = Image.open(path).convert('RGBA')
                if request.form.get('bg_removal', '1') not in ('0', 'false', 'False'):
                    src = _remove_bg(src)
                p = _auto_detect(src)
            except Exception as e:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': str(e)}), 500
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'params': p})

        @self.route('/convert', methods=['POST'])
        def mcskin_convert():
            session = new_session(self.name)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            model = (request.form.get('model') or 'wide').lower()
            if model not in ('wide', 'slim'):
                model = 'wide'
            path = saved[0]['path']
            try:
                src = Image.open(path).convert('RGBA')
            except Exception as e:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': '无法解析图片: %s' % e}), 400
            if request.form.get('bg_removal', '1') not in ('0', 'false', 'False'):
                src = _remove_bg(src)
            p = dict(DEFAULT_P)
            for k in p:
                if k == 'bg_removal':
                    continue
                v = request.form.get('p_' + k)
                if v is not None and v != '':
                    try:
                        p[k] = _clamp(float(v), 0, 255)
                    except (TypeError, ValueError):
                        pass
            try:
                skin = _build_skin(src, model, p)
            except Exception as e:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': '转换失败: %s' % e}), 500
            os.makedirs(CACHE_DIR, exist_ok=True)
            name = hashlib.md5(('%s-%s-%d' % (saved[0]['filename'], model, time.time())).encode()).hexdigest()[:16] + '.png'
            out = os.path.join(CACHE_DIR, name)
            skin.save(out, 'PNG')
            shutil.rmtree(session, ignore_errors=True)
            buf = io.BytesIO()
            skin.save(buf, 'PNG')
            return jsonify({
                'ok': True,
                'size': list(skin.size),
                'model': model,
                'has_overlay': True,
                'params': p,
                'url': '/api/plugins/mcskin/cache/' + name,
                'filename': '皮肤_%s_%s.png' % (model, time.strftime('%Y%m%d%H%M%S')),
                'png': base64.b64encode(buf.getvalue()).decode(),
            })

        @self.route('/paint/models', methods=['GET'])
        def paint_models():
            return jsonify({'ok': True, 'models': list_models(DEFAULT_MODEL_DIR)})

        @self.route('/paint', methods=['POST'])
        def mcskin_paint():
            session = new_session(self.name)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            path = saved[0]['path']
            src_path = os.path.join(CACHE_DIR, 'paint_%d.png' % int(time.time() * 1000))
            os.makedirs(CACHE_DIR, exist_ok=True)
            try:
                shutil.copyfile(path, src_path)
            except Exception as e:
                shutil.rmtree(session, ignore_errors=True)
                return jsonify({'ok': False, 'error': str(e)}), 500
            shutil.rmtree(session, ignore_errors=True)
            p = dict(DEFAULT_P)
            for k in p:
                if k == 'bg_removal':
                    continue
                v = request.form.get('p_' + k)
                if v is not None and v != '':
                    try:
                        p[k] = _clamp(float(v), 0, 255)
                    except (TypeError, ValueError):
                        pass
            body = (request.form.get('body') or 'wide').lower()
            if body not in ('wide', 'slim'):
                body = 'wide'
            jid = new_job_id()
            job = {
                'id': jid, 'status': 'queued', 'progress': 0, 'created': time.time(),
                '_src_path': src_path,
                'params': p,
                'bg_removal': request.form.get('bg_removal', '1') not in ('0', 'false', 'False'),
                'model': request.form.get('model'),
                'body': body,
                'prompt': request.form.get('prompt'),
                'negative_prompt': request.form.get('negative_prompt'),
                'steps': request.form.get('steps'),
                'cfg': request.form.get('cfg'),
                'strength': request.form.get('strength'),
                'seed': int(request.form.get('seed') or -1),
            }
            _paint_manager.enqueue(job)
            return jsonify({'ok': True, 'job_id': jid, 'status': 'queued'})

        @self.route('/paint/status/', methods=['GET'])
        def paint_status():
            jid = request.path.rstrip('/').rsplit('/', 1)[-1]
            if not jid:
                return jsonify({'ok': False, 'error': '缺少任务ID'}), 400
            j = _paint_manager.get(jid)
            if not j:
                return jsonify({'ok': False, 'error': '任务不存在'}), 404
            return jsonify({k: j.get(k) for k in (
                'id', 'status', 'progress', 'region', 'error', 'created',
                'url', 'size', 'png')})

        @self.route('/paint/cancel/', methods=['POST'])
        def paint_cancel():
            jid = request.path.rstrip('/').rsplit('/', 1)[-1]
            if not jid:
                return jsonify({'ok': False, 'error': '缺少任务ID'}), 400
            r = _paint_manager.cancel(jid)
            if r is None:
                return jsonify({'ok': False, 'error': '任务不存在'}), 404
            return jsonify({'ok': True, 'status': r})

        @self.route('/text2skin/models', methods=['GET'])
        def text2skin_models():
            return jsonify({'ok': True, 'models': list_llm_models()})

        @self.route('/text2skin/styles', methods=['GET'])
        def text2skin_styles():
            return jsonify({'ok': True, 'styles': TEXT2SKIN_STYLES, 'tones': TEXT2SKIN_TONES})

        @self.route('/text2skin', methods=['POST'])
        def text2skin():
            data = request.json or {}
            prompt = (data.get('prompt') or '').strip()
            if not prompt:
                return jsonify({'ok': False, 'error': '请输入角色描述'}), 400
            jid = new_llm_job_id()
            job = {
                'id': jid, 'status': 'queued', 'progress': 0, 'created': time.time(),
                'prompt': prompt,
                'style': (data.get('style') or 'modern'),
                'tone': (data.get('tone') or 'any'),
                'strength': data.get('strength', 3),
                'body': (data.get('body') or 'wide'),
            }
            enqueue_llm(job)
            return jsonify({'ok': True, 'job_id': jid, 'status': 'queued'})

        @self.route('/text2skin/status/', methods=['GET'])
        def text2skin_status():
            jid = request.path.rstrip('/').rsplit('/', 1)[-1]
            if not jid:
                return jsonify({'ok': False, 'error': '缺少任务ID'}), 400
            j = get_llm_job(jid)
            if not j:
                return jsonify({'ok': False, 'error': '任务不存在'}), 404
            return jsonify({k: j.get(k) for k in (
                'id', 'status', 'progress', 'error', 'created', 'spec', 'candidate')})

        @self.route('/text2skin/regenerate/', methods=['POST'])
        def text2skin_regenerate():
            jid = request.path.rstrip('/').rsplit('/', 1)[-1]
            history = _load_history()
            item = next((h for h in history if h.get('id') == jid), None)
            if not item:
                return jsonify({'ok': False, 'error': '历史不存在'}), 404
            njid = new_llm_job_id()
            job = {
                'id': njid, 'status': 'queued', 'progress': 0, 'created': time.time(),
                'prompt': item.get('prompt'), 'style': item.get('style'),
                'tone': item.get('tone'), 'strength': item.get('strength'),
                'body': item.get('model') or 'wide',
            }
            enqueue_llm(job)
            return jsonify({'ok': True, 'job_id': njid, 'status': 'queued'})

        @self.route('/text2skin/history', methods=['GET'])
        def text2skin_history():
            return jsonify({'ok': True, 'history': _load_history()})

        @self.route('/text2skin/feedback/', methods=['POST'])
        def text2skin_feedback():
            jid = request.path.rstrip('/').rsplit('/', 1)[-1]
            data = request.json or {}
            like = data.get('like')
            history = _load_history()
            item = next((h for h in history if h.get('id') == jid), None)
            if not item:
                return jsonify({'ok': False, 'error': '历史不存在'}), 404
            for c in item.get('candidates', []):
                c['feedback'] = 'like' if like else 'dislike'
            _save_history(history)
            return jsonify({'ok': True, 'status': 'like' if like else 'dislike'})
