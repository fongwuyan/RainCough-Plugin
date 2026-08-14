import os
import re
import json
import time
import random
import base64
from datetime import datetime
from flask import request, jsonify, send_from_directory
from PIL import Image
from io import BytesIO
from plugins.base import Plugin
from plugins.sd_common import (
    get_pipe, get_img2img, list_models, resolve_model,
    new_job_id, JobManager, pipe_state,
)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(PLUGIN_DIR, 'data.json')
DEFAULT_MODEL_DIR = '/opt/touchgal/models/aigen'
DEFAULT_OUTPUT_DIR = os.path.join(PLUGIN_DIR, 'output')

VAE_FILE = 'vae-ft-mse-840000-ema-pruned.safetensors'
EASY_FILE = 'EasyNegative.safetensors'
ESRGAN_X2 = 'RealESRGAN_x2.pth'
ESRGAN_X4 = 'RealESRGAN_x4.pth'
SD15_CONFIG_DIR = os.path.join(DEFAULT_MODEL_DIR, 'sd15-config')


DEFAULT_CONFIG = {
    'model_dir': DEFAULT_MODEL_DIR,
    'output_dir': DEFAULT_OUTPUT_DIR,
    'storage_paths': [DEFAULT_OUTPUT_DIR],
    'active_path': DEFAULT_OUTPUT_DIR,
    'easy_negative': True,
    'fix_vae': True,
    'upscale_default': 'none',
    'default_steps': 20,
    'default_cfg': 7,
    'default_width': 512,
    'default_height': 512,
}


def load_config():
    cfg = {}
    if os.path.isfile(DATA_FILE):
        try:
            cfg = json.load(open(DATA_FILE, 'r', encoding='utf-8'))
        except Exception:
            cfg = {}
    merged = dict(DEFAULT_CONFIG)
    merged.update(cfg)
    paths = merged.get('storage_paths') or []
    if DEFAULT_OUTPUT_DIR not in paths:
        paths.insert(0, DEFAULT_OUTPUT_DIR)
    merged['storage_paths'] = paths
    if merged.get('active_path') not in paths:
        merged['active_path'] = paths[0]
    return merged


def save_config(cfg):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _load_input_image(image, outdir):
    if not image:
        return None
    try:
        if isinstance(image, str) and image.startswith('data:'):
            b64 = image.split(',', 1)[1]
            img = Image.open(BytesIO(base64.b64decode(b64)))
        else:
            p = os.path.join(outdir, os.path.basename(str(image)))
            img = Image.open(p)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        w = max(64, img.width - (img.width % 8))
        h = max(64, img.height - (img.height % 8))
        if (w, h) != (img.width, img.height):
            img = img.resize((w, h), Image.LANCZOS)
        return img
    except Exception:
        return None


def _clamp_dim(v, default):
    try:
        v = int(v)
    except Exception:
        v = default
    v = max(256, min(1024, v))
    return v - (v % 8)


def _upscale(src, scale, model_path):
    import torch
    from torch import nn
    from torch.nn import functional as F
    import numpy as np

    class _RDB5C(nn.Module):
        def __init__(self, num_feat=64, num_grow_ch=32):
            super(_RDB5C, self).__init__()
            self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
            self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv3 = nn.Conv2d(num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv4 = nn.Conv2d(num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x):
            x1 = self.lrelu(self.conv1(x))
            x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
            x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
            x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
            x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
            return x5 * 0.2 + x

    class _RRDB(nn.Module):
        def __init__(self, num_feat=64, num_grow_ch=32):
            super(_RRDB, self).__init__()
            self.rdb1 = _RDB5C(num_feat, num_grow_ch)
            self.rdb2 = _RDB5C(num_feat, num_grow_ch)
            self.rdb3 = _RDB5C(num_feat, num_grow_ch)

        def forward(self, x):
            return self.rdb3(self.rdb2(self.rdb1(x))) * 0.2 + x

    class _RRDBNet(nn.Module):
        def __init__(self, num_in_ch=3, num_out_ch=3, scale=4, num_feat=64, num_block=23, num_grow_ch=32):
            super(_RRDBNet, self).__init__()
            self.scale = scale
            if scale == 2:
                num_in_ch *= 4
            elif scale == 1:
                num_in_ch *= 16
            self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
            blocks = []
            for _ in range(num_block):
                blocks.append(_RRDB(num_feat, num_grow_ch))
            self.body = nn.Sequential(*blocks)
            self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_last = nn.Conv2d(num_feat, num_out_ch, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x):
            if self.scale == 2:
                x = F.pixel_unshuffle(x, 2)
            elif self.scale == 1:
                x = F.pixel_unshuffle(x, 4)
            feat = self.conv_first(x)
            feat = feat + self.conv_body(self.body(feat))
            feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode='nearest')))
            feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode='nearest')))
            return self.conv_last(self.lrelu(self.conv_hr(feat)))

    sd = torch.load(model_path, map_location='cpu')
    if 'params_ema' in sd:
        sd = sd['params_ema']
    elif 'params' in sd:
        sd = sd['params']
    model = _RRDBNet(scale=scale)
    model.load_state_dict(sd, strict=True)
    model.eval()

    img = Image.open(src).convert('RGB')
    w, h = img.size
    if w * h > 1024 * 1024:
        ratio = (1024 * 1024 / float(w * h)) ** 0.5
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    x = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).contiguous()
    with torch.no_grad():
        y = model(x).clamp_(0, 1)
    out = (y.squeeze(0).permute(1, 2, 0).numpy() * 255.0).round().astype(np.uint8)
    dst = src.rsplit('.', 1)[0] + '_x%d.png' % scale
    Image.fromarray(out).save(dst)
    return dst


class _JobCancelled(Exception):
    pass


def _run_job(job):
    jid = job['id']
    try:
        cfg = load_config()
        model_dir = cfg.get('model_dir') or DEFAULT_MODEL_DIR
        outdir = cfg.get('output_dir') or DEFAULT_OUTPUT_DIR
        os.makedirs(outdir, exist_ok=True)
        model_path = resolve_model(model_dir, job.get('model'))
        if not model_path:
            raise ValueError('未找到可用的主模型，请检查模型目录')
        lora = job.get('lora') or ''
        lora_path = os.path.join(model_dir, lora) if lora else None

        job['status'] = 'loading'
        pipe = get_pipe(model_path, lora_path, model_dir, cfg)

        job['status'] = 'running'
        job['progress'] = 0
        steps = max(1, int(job.get('steps') or cfg.get('default_steps') or 20))
        steps = min(60, steps)

        def cb(step, t, latents):
            if job.get('_cancel'):
                raise _JobCancelled()
            job['progress'] = int(step / max(1, t) * 100)
            return True

        seed = -1
        try:
            seed = int(job.get('seed') or -1)
        except Exception:
            seed = -1
        generator = None
        if seed >= 0:
            import torch
            generator = torch.Generator().manual_seed(seed)

        neg = (job.get('negative_prompt') or '').strip()
        if cfg.get('easy_negative', True) and job.get('use_easy_negative', True):
            neg = (neg + ', EasyNegative') if neg else 'EasyNegative'

        kwargs = dict(
            prompt=job.get('prompt') or '',
            negative_prompt=neg or None,
            width=_clamp_dim(job.get('width'), cfg.get('default_width') or 512),
            height=_clamp_dim(job.get('height'), cfg.get('default_height') or 512),
            num_inference_steps=steps,
            guidance_scale=float(job.get('cfg') or cfg.get('default_cfg') or 7),
            num_images_per_prompt=max(1, min(4, int(job.get('count') or 1))),
            generator=generator,
            callback=cb,
            callback_steps=1,
        )

        if job.get('mode') == 'img2img':
            img = _load_input_image(job.get('image'), outdir)
            if img is None:
                raise ValueError('无法解析输入图片')
            pipe2 = get_img2img(pipe)
            kwargs.update(image=img, strength=max(0.05, min(0.95, float(job.get('strength') or 0.6))))
            result = pipe2(**kwargs)
        else:
            result = pipe(**kwargs)

        if job.get('_cancel'):
            job['status'] = 'cancelled'
            return
        images = result.images
        urls = []
        upscale = job.get('upscale') or cfg.get('upscale_default') or 'none'
        for i, img in enumerate(images):
            rel = '%s_%d.png' % (jid, i)
            img.save(os.path.join(outdir, rel))
            url = '/api/plugins/aigen/output/' + rel
            if upscale in ('x2', 'x4'):
                scale = int(upscale[1])
                model_file = ESRGAN_X2 if scale == 2 else ESRGAN_X4
                model_path_u = os.path.join(model_dir, model_file)
                if os.path.isfile(model_path_u):
                    try:
                        up_path = _upscale(os.path.join(outdir, rel), scale, model_path_u)
                        url = '/api/plugins/aigen/output/' + os.path.basename(up_path)
                    except Exception:
                        pass
            urls.append(url)
        job['images'] = urls
        job['progress'] = 100
        job['status'] = 'done'
    except _JobCancelled:
        job['status'] = 'cancelled'
    except Exception as e:
        import traceback
        traceback.print_exc()
        job['status'] = 'error'
        job['error'] = str(e)


class _GenManager(JobManager):
    def _run(self, job):
        _run_job(job)


_manager = _GenManager()


class AigenPlugin(Plugin):
    name = 'aigen'
    label = 'AI 生图'
    icon = ''
    description = '本地 SD1.5 文生图/图生图，支持 EasyNegative、VAE 修复、Real-ESRGAN 超分'

    def storage_provider(self):
        cfg = load_config()
        return {
            'name': 'aigen',
            'label': 'AI 生图输出目录',
            'paths': cfg.get('storage_paths', [DEFAULT_OUTPUT_DIR]),
            'active_path': cfg.get('active_path'),
            'auto_switch_full': False,
            'full_threshold_mb': 0,
        }

    def _register_routes(self):

        def _tail(prefix):
            idx = request.path.find(prefix)
            if idx < 0:
                return ''
            return request.path[idx + len(prefix):].lstrip('/')

        @self.route('/ping', methods=['GET'])
        def ping():
            cfg = load_config()
            model_dir = cfg.get('model_dir') or DEFAULT_MODEL_DIR
            listing = list_models(model_dir)
            st = pipe_state()
            return jsonify({
                'ok': bool(listing['models']),
                'models': listing,
                'pipe_loaded': st['pipe'] is not None,
                'current_model': st['model'],
                'output_dir': cfg.get('output_dir'),
                'config': cfg,
            })

        @self.route('/models', methods=['GET'])
        def models():
            model_dir = load_config().get('model_dir') or DEFAULT_MODEL_DIR
            return jsonify(list_models(model_dir))

        @self.route('/generate', methods=['POST'])
        def generate():
            data = request.json or {}
            prompt = (data.get('prompt') or '').strip()
            if not prompt:
                return jsonify({'error': '请输入提示词'}), 400
            jid = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
            job = {
                'id': jid, 'mode': 'text2img', 'status': 'queued', 'progress': 0,
                'created': time.time(), 'prompt': prompt,
                'negative_prompt': data.get('negative_prompt'),
                'width': data.get('width'), 'height': data.get('height'),
                'steps': data.get('steps'), 'cfg': data.get('cfg'),
                'seed': data.get('seed', -1), 'count': data.get('count', 1),
                'lora': data.get('lora'), 'model': data.get('model'),
                'upscale': data.get('upscale'),
                'use_easy_negative': data.get('use_easy_negative', True),
            }
            _manager.enqueue(job)
            return jsonify({'job_id': jid, 'status': 'queued'})

        @self.route('/img2img', methods=['POST'])
        def img2img():
            data = request.json or {}
            prompt = (data.get('prompt') or '').strip()
            if not prompt:
                return jsonify({'error': '请输入提示词'}), 400
            if not data.get('image'):
                return jsonify({'error': '请上传输入图片'}), 400
            jid = datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000, 9999))
            job = {
                'id': jid, 'mode': 'img2img', 'status': 'queued', 'progress': 0,
                'created': time.time(), 'prompt': prompt,
                'image': data.get('image'), 'strength': data.get('strength', 0.6),
                'negative_prompt': data.get('negative_prompt'),
                'width': data.get('width'), 'height': data.get('height'),
                'steps': data.get('steps'), 'cfg': data.get('cfg'),
                'seed': data.get('seed', -1), 'count': data.get('count', 1),
                'lora': data.get('lora'), 'model': data.get('model'),
                'upscale': data.get('upscale'),
                'use_easy_negative': data.get('use_easy_negative', True),
            }
            _manager.enqueue(job)
            return jsonify({'job_id': jid, 'status': 'queued'})

        @self.route('/status/', methods=['GET'])
        def status():
            jid = _tail('/status/')
            if not jid:
                return jsonify({'error': '缺少任务ID'}), 400
            j = _manager.get(jid)
            if not j:
                return jsonify({'error': '任务不存在'}), 404
            return jsonify({k: j.get(k) for k in (
                'id', 'status', 'progress', 'images', 'error', 'mode', 'created')})

        @self.route('/cancel/', methods=['POST'])
        def cancel():
            jid = _tail('/cancel/')
            if not jid:
                return jsonify({'error': '缺少任务ID'}), 400
            r = _manager.cancel(jid)
            if r is None:
                return jsonify({'error': '任务不存在'}), 404
            if r == 'cancelled':
                return jsonify({'message': '已取消', 'status': 'cancelled'})
            if r == 'cancelling':
                return jsonify({'message': '正在取消…', 'status': 'cancelling'})
            return jsonify({'message': '任务已结束，无法取消', 'status': r})

        @self.route('/output/', methods=['GET'])
        def output():
            fn = os.path.basename(_tail('/output/'))
            outdir = load_config().get('output_dir') or DEFAULT_OUTPUT_DIR
            if not fn or not os.path.isfile(os.path.join(outdir, fn)):
                return jsonify({'error': '文件不存在'}), 404
            return send_from_directory(outdir, fn)

        @self.route('/gallery', methods=['GET'])
        def gallery():
            outdir = load_config().get('output_dir') or DEFAULT_OUTPUT_DIR
            limit, offset = 120, 0
            try:
                limit = max(1, min(500, int(request.args.get('limit', 120))))
                offset = max(0, int(request.args.get('offset', 0)))
            except Exception:
                pass
            exts = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
            items = []
            try:
                names = os.listdir(outdir)
            except Exception:
                names = []
            for n in names:
                if not n.lower().endswith(exts):
                    continue
                p = os.path.join(outdir, n)
                if not os.path.isfile(p):
                    continue
                try:
                    st = os.stat(p)
                    items.append({
                        'name': n,
                        'size': st.st_size,
                        'mtime': int(st.st_mtime),
                        'url': '/api/plugins/aigen/output/' + n,
                    })
                except Exception:
                    continue
            items.sort(key=lambda x: x['mtime'], reverse=True)
            total = len(items)
            items = items[offset:offset + limit]
            return jsonify({'items': items, 'total': total, 'limit': limit, 'offset': offset})

        @self.route('/gallery/', methods=['DELETE'])
        def gallery_delete():
            name = os.path.basename(_tail('/gallery/'))
            outdir = load_config().get('output_dir') or DEFAULT_OUTPUT_DIR
            base = os.path.abspath(outdir)
            if not name:
                return jsonify({'error': '缺少文件名'}), 400
            p = os.path.join(base, name)
            if not os.path.isfile(p) or not os.path.abspath(p).startswith(base + os.sep):
                return jsonify({'error': '文件不存在'}), 404
            try:
                os.remove(p)
                return jsonify({'ok': True, 'name': name})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.route('/config', methods=['GET', 'POST'])
        def config():
            if request.method == 'POST':
                new_cfg = request.json or {}
                cfg = load_config()
                if 'storage_paths' in new_cfg:
                    paths = [p for p in new_cfg['storage_paths']
                             if isinstance(p, str) and p.strip()]
                    outdir = new_cfg.get('output_dir') or cfg.get('output_dir')
                    if outdir and outdir not in paths:
                        paths.insert(0, outdir)
                    cfg['storage_paths'] = paths
                    if new_cfg.get('active_path') not in paths:
                        cfg['active_path'] = paths[0]
                    else:
                        cfg['active_path'] = new_cfg['active_path']
                for k in ('model_dir', 'output_dir', 'default_steps', 'default_cfg',
                          'default_width', 'default_height', 'upscale_default'):
                    if k in new_cfg:
                        cfg[k] = new_cfg[k]
                for k in ('easy_negative', 'fix_vae'):
                    if k in new_cfg:
                        cfg[k] = bool(new_cfg[k])
                save_config(cfg)
                return jsonify({'message': '设置已保存', 'config': load_config()})
            return jsonify(load_config())
