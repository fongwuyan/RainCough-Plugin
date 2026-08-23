import os
import io
import re
import uuid
import glob
import zlib
import shutil
import zipfile
import hashlib
import struct
from datetime import datetime
from flask import request, jsonify
from plugins.base import Plugin
from plugins.yulotool_common import (
    find_tool, run_cmd, save_uploads, new_session, work_dir,
    safe_join, fmt_size, parse_7z_list, classify_ext,
)

PLUGIN = 'yulotool'

FORMATS = ['7z', 'zip', 'tar', 'gz', 'bz2', 'xz', 'rar']
ORGANIZE_MODES = ['none', 'type', 'date', 'ext', 'name']
IMG_EXT = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'ico', 'svg']
ALGOS = {'md5': hashlib.md5, 'sha1': hashlib.sha1, 'sha256': hashlib.sha256}

CHUNK = 32 * 1024 * 1024
FILE_CHUNK = 1024 * 1024


def clean_err(r, session):
    """Remove absolute work-dir paths from command error output."""
    err = r.get('error') or ''
    if session:
        err = err.replace(session + '/', '').replace(session, '[upload]')
    err = re.sub(r'/opt/[^\s\n]+?work/[a-f0-9]+/', '', err)
    return err.strip() or '操作失败'


# ---- videomerge footer ----
MAGIC = b'YLVFUSN1'
END_MAGIC = b'YLVFEND1'
FOOTER_LEN = 48
VERSION = 1
ARCH_ZIP = 1
ARCH_7Z = 2
ARCH_RAR = 3


def detect_archive_type(path):
    with open(path, 'rb') as f:
        head = f.read(8)
    if head[:2] == b'PK':
        return ARCH_ZIP
    if head[:6] == b'\x37\x7a\xbc\xaf\x27\x1c':
        return ARCH_7Z
    if head[:4] == b'Rar!':
        return ARCH_RAR
    return 0


def build_footer(arch_type, arch_size, crc32):
    buf = io.BytesIO()
    buf.write(MAGIC)
    buf.write(struct.pack('<I', VERSION))
    buf.write(struct.pack('<I', arch_type))
    buf.write(struct.pack('<Q', arch_size))
    buf.write(struct.pack('<I', crc32))
    buf.write(struct.pack('<8s', b'\x00' * 8))
    buf.write(struct.pack('<I', FOOTER_LEN))
    buf.write(END_MAGIC)
    return buf.getvalue()


def parse_footer(data):
    if len(data) < FOOTER_LEN or data[:8] != MAGIC:
        return None
    if data[8:12] != struct.pack('<I', VERSION):
        return None
    if data[40:48] != END_MAGIC:
        return None
    arch_type = struct.unpack('<I', data[12:16])[0]
    arch_size = struct.unpack('<Q', data[16:24])[0]
    crc32 = struct.unpack('<I', data[24:28])[0]
    return {'arch_type': arch_type, 'arch_size': arch_size, 'crc32': crc32}


def _u32(buf, off):
    return struct.unpack('<I', buf[off:off + 4])[0]


def _u64(buf, off):
    return struct.unpack('<Q', buf[off:off + 8])[0]


def _p32(buf, off, v):
    struct.pack_into('<I', buf, off, v)


def _p16(buf, off, v):
    struct.pack_into('<H', buf, off, v)


def _p64(buf, off, v):
    struct.pack_into('<Q', buf, off, v)


def fix_zip_offsets(fh, video_size, zip_size):
    """Rewrite ZIP central directory + EOCD so the archive is readable
    directly from the merged file (offsets shifted by video_size)."""
    eocd_off = video_size + zip_size - 22
    if eocd_off < 0:
        return None
    fh.seek(0, 2)
    file_end = fh.tell()
    probe = eocd_off
    found = False
    scan_limit = max(video_size, file_end - 64 * 1024)
    while probe >= scan_limit:
        fh.seek(probe)
        if fh.read(4) == b'PK\x05\x06':
            fh.seek(probe)
            eocd = fh.read(22)
            eocd_off = probe
            found = True
            break
        probe -= 1
    if not found:
        return '未找到 EOCD 签名'
    eocd = bytearray(eocd)
    cd_off = _u32(eocd, 16)
    total_entries = _u32(eocd, 8)
    cd_size = _u32(eocd, 12)

    zip64_eocd_off = -1
    if cd_off == 0xFFFFFFFF:
        scan_start = max(video_size, eocd_off - 128 * 1024)
        fh.seek(scan_start)
        scan = fh.read(eocd_off - scan_start)
        idx = scan.rfind(b'PK\x06\x06')
        if idx >= 0:
            zip64_eocd_off = scan_start + idx
            fh.seek(zip64_eocd_off)
            z64 = fh.read(56)
            if z64[:4] == b'PK\x06\x06':
                cd_off = _u64(z64, 48)
                cd_size = _u64(z64, 40)
                total_entries = _u64(z64, 32)

    new_cd_off = cd_off + video_size
    fh.seek(new_cd_off)
    cd = bytearray(fh.read(cd_size))

    pos = 0
    for i in range(total_entries):
        if pos + 46 > len(cd):
            break
        if cd[pos:pos + 4] != b'PK\x01\x02':
            return f'CD 条目 {i} 签名无效 (offset={new_cd_off + pos})'
        name_len = _u32(cd, pos + 28) & 0xFFFF
        extra_len = _u32(cd, pos + 30) & 0xFFFF
        comment_len = _u32(cd, pos + 32) & 0xFFFF
        old_off = _u32(cd, pos + 42)
        new_off = old_off + video_size

        if old_off == 0xFFFFFFFF:
            extra_start = pos + 46 + name_len
            extra_end = extra_start + extra_len
            ex = extra_start
            while ex + 12 <= extra_end:
                ext_id = struct.unpack('<H', cd[ex:ex + 2])[0]
                ext_sz = struct.unpack('<H', cd[ex + 2:ex + 4])[0]
                if ext_id == 0x0001 and ext_sz >= 8:
                    real_off = _u64(cd, ex + 4)
                    _p64(cd, ex + 4, real_off + video_size)
                    break
                ex += 4 + ext_sz
            pos += 46 + name_len + extra_len + comment_len
        elif new_off > 0xFFFFFFFF:
            _p32(cd, pos + 42, 0xFFFFFFFF)
            old_extra = bytes(cd[pos + 46 + name_len:pos + 46 + name_len + extra_len])
            zip64_ext = struct.pack('<HHQ', 0x0001, 8, new_off)
            new_extra = zip64_ext + old_extra
            new_extra_len = len(new_extra)
            _p16(cd, pos + 30, new_extra_len)
            rest = bytes(cd[pos + 46 + name_len + extra_len + comment_len:])
            head = bytes(cd[:pos + 46 + name_len]) + new_extra
            cd = bytearray(head + rest)
            pos += 46 + name_len + new_extra_len + comment_len
        else:
            _p32(cd, pos + 42, new_off)
            pos += 46 + name_len + extra_len + comment_len

    new_cd_size = len(cd)
    fh.seek(new_cd_off)
    fh.write(cd)

    if new_cd_off > 0xFFFFFFFF:
        _p32(eocd, 16, 0xFFFFFFFF)
    else:
        _p32(eocd, 16, new_cd_off)
    if new_cd_size > 0xFFFFFFFF:
        _p32(eocd, 12, 0xFFFFFFFF)
    else:
        _p32(eocd, 12, new_cd_size)
    _p16(eocd, 20, FOOTER_LEN)
    fh.seek(eocd_off)
    fh.write(eocd)

    if zip64_eocd_off >= 0:
        fh.seek(zip64_eocd_off)
        z64 = bytearray(fh.read(56))
        if z64[:4] == b'PK\x06\x06':
            _p64(z64, 48, new_cd_off)
            _p64(z64, 40, new_cd_size)
            _p64(z64, 32, total_entries)
            fh.seek(zip64_eocd_off)
            fh.write(z64)
    return None


def stream_copy(src_path, dst_fh, start=0, size=None):
    with open(src_path, 'rb') as src:
        if start:
            src.seek(start)
        remaining = size if size is not None else None
        while True:
            if remaining is None:
                b = src.read(CHUNK)
                if not b:
                    break
                dst_fh.write(b)
            else:
                if remaining <= 0:
                    break
                b = src.read(min(CHUNK, remaining))
                if not b:
                    break
                dst_fh.write(b)
                remaining -= len(b)


def crc32_file(path):
    h = 0
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h = zlib.crc32(b, h)
    return h & 0xFFFFFFFF


# ---- generic helpers ----
def make_zip(src_dir, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for fn in files:
                fp = os.path.join(root, fn)
                arc = os.path.relpath(fp, src_dir)
                zf.write(fp, arc)


def make_zip_from_files(file_list, zip_path, arc_prefix=''):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in file_list:
            if os.path.isfile(p):
                zf.write(p, os.path.join(arc_prefix, os.path.basename(p)))


def hash_file(path, algo):
    h = ALGOS[algo]()
    with open(path, 'rb') as f:
        while True:
            b = f.read(FILE_CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def md5_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            b = f.read(FILE_CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def walk_files(root):
    for base, dirs, files in os.walk(root):
        for fn in files:
            yield os.path.join(base, fn)


def secure_wipe(path, passes=3):
    try:
        size = os.path.getsize(path)
        if size <= 0:
            os.remove(path)
            return True
        # 优先用 coreutils shred(内核级覆写, C 循环, 远快于 Python 逐块写)
        try:
            shred = shutil.which('shred')
        except Exception:
            shred = None
        if shred:
            rc = subprocess.run([shred, '-n', str(max(1, int(passes))), '-z', '-u', path],
                                capture_output=True, timeout=3600)
            if rc.returncode == 0:
                return not os.path.exists(path)
        with open(path, 'r+b') as f:
            for p in range(passes):
                f.seek(0)
                remaining = size
                while remaining > 0:
                    n = min(FILE_CHUNK, remaining)
                    f.write(os.urandom(n))
                    remaining -= n
                f.flush()
                os.fsync(f.fileno())
            f.seek(0)
            remaining = size
            while remaining > 0:
                n = min(FILE_CHUNK, remaining)
                f.write(b'\x00' * n)
                remaining -= n
            f.flush()
            os.fsync(f.fileno())
        os.remove(path)
        return not os.path.exists(path)
    except Exception:
        try:
            os.remove(path)
        except Exception:
            pass
        return not os.path.exists(path)


def count_pdf_pages(path):
    qpdf = find_tool('qpdf')
    if not qpdf:
        return 0
    r = run_cmd([qpdf, '--show-npages', path])
    try:
        return int(r['output'].strip())
    except ValueError:
        return 0


class YulotoolPlugin(Plugin):
    name = 'yulotool'
    label = '工具箱'
    icon = ''
    description = '解压压缩、目录分析、哈希、媒体处理、文档转换、网络工具、视频融合'

    def _register_routes(self):
        # ==================== decompress ====================
        @self.route('/decompress/check', methods=['GET'])
        def dc_check():
            tool = find_tool('7z')
            if not tool:
                return jsonify({'ok': False, 'error': '未安装 7z (p7zip-full)'})
            return jsonify({'ok': True, '7z': tool})

        @self.route('/decompress/list', methods=['POST'])
        def dc_list():
            tool = find_tool('7z')
            if not tool:
                return jsonify({'ok': False, 'error': '未安装 7z'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传压缩包'}), 400
            archive = saved[0]['path']
            r = run_cmd([tool, 'l', archive, '-slt', '-bsp0'])
            if not r['ok']:
                return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
            files = parse_7z_list(r['output'])
            total_size = sum(f.get('size', 0) for f in files if not f.get('isDir'))
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'name': saved[0]['filename'],
                            'files': files, 'total': len(files),
                            'total_size': total_size})

        @self.route('/decompress/extract', methods=['POST'])
        def dc_extract():
            tool = find_tool('7z')
            if not tool:
                return jsonify({'ok': False, 'error': '未安装 7z'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传压缩包'}), 400
            archive = saved[0]['path']
            password = (request.form.get('password') or '').strip()
            organize = request.form.get('organize') or 'none'
            if organize not in ORGANIZE_MODES:
                organize = 'none'
            out_dir = os.path.join(session, 'extracted')
            os.makedirs(out_dir, exist_ok=True)

            if organize != 'none':
                temp_dir = os.path.join(session, '_temp')
                args = [tool, 'x', archive, f'-o{temp_dir}']
                if password:
                    args.append(f'-p{password}')
                r = run_cmd(args)
                if not r['ok']:
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                count = 0
                for root, dirs, files in os.walk(temp_dir):
                    for fn in files:
                        src = os.path.join(root, fn)
                        mtime = datetime.fromtimestamp(os.path.getmtime(src))
                        ext = os.path.splitext(fn)[1][1:]
                        if organize == 'type':
                            target = os.path.join(out_dir, classify_ext(ext))
                        elif organize == 'date':
                            target = os.path.join(out_dir, mtime.strftime('%Y-%m-%d'))
                        elif organize == 'ext':
                            target = os.path.join(out_dir, f'.{ext}' if ext else 'no_ext')
                        else:
                            first = fn[:1].upper()
                            target = os.path.join(out_dir, first if first.isalpha() else '#')
                        os.makedirs(target, exist_ok=True)
                        dest = os.path.join(target, fn)
                        i = 1
                        while os.path.exists(dest):
                            base, e = os.path.splitext(fn)
                            dest = os.path.join(target, f'{base}_{i}{e}')
                            i += 1
                        shutil.copy2(src, dest)
                        count += 1
                shutil.rmtree(temp_dir, ignore_errors=True)
            else:
                args = [tool, 'x', archive, f'-o{out_dir}']
                if password:
                    args.append(f'-p{password}')
                r = run_cmd(args)
                if not r['ok']:
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                count = sum(len(fs) for _, _, fs in os.walk(out_dir))

            zip_path = os.path.join(session, f"{os.path.splitext(saved[0]['filename'])[0]}_extracted.zip")
            make_zip(out_dir, zip_path)
            return jsonify({'ok': True, 'count': count,
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(zip_path)}'})

        @self.route('/decompress/compress', methods=['POST'])
        def dc_compress():
            tool = find_tool('7z')
            if not tool:
                return jsonify({'ok': False, 'error': '未安装 7z'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传要压缩的文件'}), 400
            fmt = (request.form.get('format') or '7z').lower()
            if fmt not in FORMATS:
                fmt = '7z'
            try:
                level = int(request.form.get('level') or 5)
            except ValueError:
                level = 5
            password = (request.form.get('password') or '').strip()
            out_name = (request.form.get('name') or 'archive').strip() or 'archive'
            if fmt in ('gz', 'bz2', 'xz'):
                # 7z 无法直接创建 gz/bz2/xz：先打 tar，再用对应压缩器（tar.gz 两段式）
                comp = find_tool({'gz': 'gzip', 'bz2': 'bzip2', 'xz': 'xz'}[fmt])
                if not comp:
                    return jsonify({'ok': False, 'error': f'未安装 {fmt} 压缩器'}), 400
                tar_path = os.path.join(session, f'{out_name}.tar')
                args = [tool, 'a', '-ttar', tar_path] + [f['path'] for f in saved]
                r = run_cmd(args)
                if not r['ok'] or not os.path.isfile(tar_path):
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                out_path = f'{tar_path}.{fmt}'
                import subprocess as _sp
                with open(tar_path, 'rb') as srcf, open(out_path, 'wb') as dstf:
                    p = _sp.run([comp, '-c'], stdin=srcf, stdout=dstf)
                if p.returncode != 0 or not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
                    return jsonify({'ok': False, 'error': '压缩失败'}), 400
            else:
                out_path = os.path.join(session, f'{out_name}.{fmt}')
                args = [tool, 'a', f'-t{fmt}']
                if level > 0:
                    args.append(f'-mx{level}')
                if password:
                    args.append(f'-p{password}')
                args.append(out_path)
                args += [f['path'] for f in saved]
                r = run_cmd(args)
                if not r['ok']:
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                if not os.path.isfile(out_path):
                    return jsonify({'ok': False, 'error': '打包失败'}), 400
            return jsonify({'ok': True, 'size': os.path.getsize(out_path),
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(out_path)}'})

        @self.route('/decompress/convert', methods=['POST'])
        def dc_convert():
            tool = find_tool('7z')
            if not tool:
                return jsonify({'ok': False, 'error': '未安装 7z'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传压缩包'}), 400
            dst_fmt = (request.form.get('format') or '7z').lower()
            if dst_fmt not in ('7z', 'zip', 'tar'):
                dst_fmt = '7z'
            src = saved[0]['path']
            base = os.path.splitext(saved[0]['filename'])[0]
            out_path = os.path.join(session, f'{base}.{dst_fmt}')
            r = run_cmd([tool, 'a', f'-t{dst_fmt}', out_path, src])
            if not r['ok']:
                return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
            return jsonify({'ok': True, 'size': os.path.getsize(out_path),
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(out_path)}'})

        @self.route('/decompress/compare', methods=['POST'])
        def dc_compare():
            tool = find_tool('7z')
            if not tool:
                return jsonify({'ok': False, 'error': '未安装 7z'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if len(saved) < 2:
                return jsonify({'ok': False, 'error': '请上传两个压缩包'}), 400
            a, b = saved[0], saved[1]
            ra = run_cmd([tool, 'l', a['path'], '-slt', '-bsp0'])
            rb = run_cmd([tool, 'l', b['path'], '-slt', '-bsp0'])
            fa = {f['path']: f for f in parse_7z_list(ra['output']) if not f.get('isDir')}
            fb = {f['path']: f for f in parse_7z_list(rb['output']) if not f.get('isDir')}
            only_a = [f for f in fa if f not in fb]
            only_b = [f for f in fb if f not in fa]
            both = [f for f in fa if f in fb and fa[f].get('size') != fb[f].get('size')]
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'a': a['filename'], 'b': b['filename'],
                            'only_a': only_a, 'only_b': only_b, 'diff': both,
                            'same': len(fa) - len(only_a) - len(both)})

        # ==================== diranalyze ====================
        @self.route('/diranalyze/stats', methods=['POST'])
        def da_stats():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件或压缩包'}), 400
            unpacked = []
            for item in saved:
                p = item['path']
                if p.lower().endswith('.zip'):
                    try:
                        with zipfile.ZipFile(p, 'r') as zf:
                            zf.extractall(os.path.join(session, 'unpack'))
                        unpacked.append(p)
                    except Exception as e:
                        return jsonify({'ok': False, 'error': f'解压失败 {item["filename"]}: {e}'}), 400
            root = os.path.join(session, 'unpack') if unpacked else session
            total_files = 0
            total_size = 0
            type_count = {}
            type_size = {}
            for fp in walk_files(root):
                if not os.path.isfile(fp):
                    continue
                total_files += 1
                size = os.path.getsize(fp)
                total_size += size
                cat = classify_ext(os.path.splitext(fp)[1])
                type_count[cat] = type_count.get(cat, 0) + 1
                type_size[cat] = type_size.get(cat, 0) + size
            categories = []
            for name in ['图片', '视频', '音频', '文档', '压缩包', '代码', '其他']:
                categories.append({'name': name,
                                   'count': type_count.get(name, 0),
                                   'size': type_size.get(name, 0)})
            files = [{'name': os.path.relpath(fp, root),
                      'size': os.path.getsize(fp),
                      'type': classify_ext(os.path.splitext(fp)[1])}
                     for fp in walk_files(root) if os.path.isfile(fp)]
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'total_files': total_files,
                            'total_size': total_size,
                            'categories': categories, 'files': files})

        @self.route('/diranalyze/duplicate', methods=['POST'])
        def da_duplicate():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件或压缩包'}), 400
            unpacked = []
            for item in saved:
                p = item['path']
                if p.lower().endswith('.zip'):
                    try:
                        with zipfile.ZipFile(p, 'r') as zf:
                            zf.extractall(os.path.join(session, 'unpack'))
                        unpacked.append(p)
                    except Exception as e:
                        return jsonify({'ok': False, 'error': f'解压失败 {item["filename"]}: {e}'}), 400
            root = os.path.join(session, 'unpack') if unpacked else session
            size_groups = {}
            for fp in walk_files(root):
                if not os.path.isfile(fp):
                    continue
                size_groups.setdefault(os.path.getsize(fp), []).append(fp)
            duplicates = []
            for size, files in size_groups.items():
                if len(files) < 2:
                    continue
                hash_groups = {}
                for p in files:
                    hash_groups.setdefault(md5_file(p), []).append(p)
                for h, paths in hash_groups.items():
                    if len(paths) < 2:
                        continue
                    duplicates.append({'hash': h, 'size': size,
                                       'files': [{'name': os.path.relpath(p, root),
                                                  'size': size} for p in paths]})
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'total_groups': len(duplicates),
                            'duplicates': duplicates})

        # ==================== hash ====================
        @self.route('/hash/hash', methods=['POST'])
        def h_calc():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件'}), 400
            results = []
            for item in saved:
                p = item['path']
                size = os.path.getsize(p)
                results.append({
                    'name': item['filename'], 'size': size,
                    'md5': hash_file(p, 'md5'),
                    'sha1': hash_file(p, 'sha1'),
                    'sha256': hash_file(p, 'sha256'),
                })
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'results': results})

        @self.route('/hash/generate', methods=['POST'])
        def h_generate():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件'}), 400
            algo = (request.form.get('algo') or 'sha256').lower()
            if algo not in ALGOS:
                algo = 'sha256'
            lines = []
            for item in saved:
                p = item['path']
                h = hash_file(p, algo)
                name = item['filename']
                lines.append(f'{h}  {name}' if algo != 'md5' else f'{h} *{name}')
            out_path = os.path.join(session, f'checksums.{algo}')
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return jsonify({'ok': True, 'count': len(lines), 'algo': algo,
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(out_path)}'})

        @self.route('/hash/verify', methods=['POST'])
        def h_verify():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传校验文件与数据文件'}), 400
            check_file = None
            data_files = []
            for item in saved:
                base = item['filename'].lower()
                if base.endswith(('.md5', '.sha1', '.sha256')):
                    check_file = item
                else:
                    data_files.append(item)
            if not check_file:
                return jsonify({'ok': False, 'error': '缺少校验文件 (.md5/.sha1/.sha256)'}), 400
            algo = os.path.splitext(check_file['filename'])[1][1:].lower()
            content = open(check_file['path'], 'r', encoding='utf-8', errors='replace').read()
            by_name = {f['filename']: f['path'] for f in data_files}
            results = []
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                m = re.match(r'^([a-fA-F0-9]+)\s+[\* ](.+)$', line)
                if not m:
                    continue
                expected = m.group(1).lower()
                name = m.group(2).strip()
                fpath = by_name.get(name)
                if not fpath or not os.path.isfile(fpath):
                    results.append({'file': name, 'status': 'missing',
                                    'expected': expected})
                    continue
                actual = hash_file(fpath, algo)
                results.append({'file': name, 'status': 'ok' if actual == expected else 'mismatch',
                                'expected': expected, 'actual': actual})
            ok = sum(1 for r in results if r['status'] == 'ok')
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'total': len(results),
                            'passed': ok, 'failed': len(results) - ok,
                            'algo': algo, 'results': results})

        # ==================== mediatools ====================
        @self.route('/mediatools/image', methods=['POST'])
        def mt_image():
            magick = find_tool('convert')
            if not magick:
                return jsonify({'ok': False, 'error': '未安装 ImageMagick (imagemagick)'}), 400
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传图片'}), 400
            fmt = (request.form.get('format') or '').lower()
            resize = (request.form.get('resize') or '').strip()
            quality = request.form.get('quality')
            rotate = request.form.get('rotate')
            results = []
            outputs = []
            for item in saved:
                src = item['path']
                base, ext = os.path.splitext(item['filename'])
                out_ext = fmt or ext.lstrip('.').lower()
                out = os.path.join(session, f'{base}.{out_ext}')
                cmd = [magick, src]
                if resize:
                    cmd += ['-resize', resize]
                if quality:
                    try:
                        q = int(quality)
                        cmd += ['-quality', str(q)]
                    except ValueError:
                        pass
                if rotate:
                    try:
                        cmd += ['-rotate', str(int(rotate))]
                    except ValueError:
                        pass
                cmd.append(out)
                r = run_cmd(cmd)
                ok = os.path.isfile(out)
                results.append({'name': item['filename'], 'ok': ok,
                                'error': '' if ok else clean_err(r, session),
                                'output': os.path.basename(out) if ok else ''})
                if ok:
                    outputs.append(out)
            if len(outputs) == 1:
                return jsonify({'ok': True, 'results': results, 'single': True,
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(outputs[0])}'})
            zip_path = os.path.join(session, 'images_processed.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/images_processed.zip'})

        @self.route('/mediatools/pdf', methods=['POST'])
        def mt_pdf():
            qpdf = find_tool('qpdf')
            gs = find_tool('gs')
            if not qpdf or not gs:
                return jsonify({'ok': False, 'error': '未安装 qpdf 或 ghostscript'}), 400
            action = request.form.get('action') or 'merge'
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传 PDF 文件'}), 400
            files = [f['path'] for f in saved if f['path'].lower().endswith('.pdf')]
            if not files:
                return jsonify({'ok': False, 'error': '未找到 PDF 文件'}), 400

            if action == 'merge':
                out = os.path.join(session, 'merged.pdf')
                args = [qpdf, '--empty', '--pages'] + files + ['--', out]
                r = run_cmd(args)
                if not r['ok'] or not os.path.isfile(out):
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                return jsonify({'ok': True, 'pages': count_pdf_pages(out),
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/merged.pdf'})
            elif action == 'split':
                out_dir = os.path.join(session, 'pages')
                os.makedirs(out_dir, exist_ok=True)
                args = [qpdf, '--split-pages', files[0],
                        os.path.join(out_dir, 'page.pdf')]
                r = run_cmd(args)
                pages = sorted(glob.glob(os.path.join(out_dir, 'page*.pdf')))
                if not r['ok'] or not pages:
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                zip_path = os.path.join(session, 'pages.zip')
                make_zip_from_files(pages, zip_path)
                return jsonify({'ok': True, 'pages': len(pages),
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/pages.zip'})
            elif action == 'compress':
                dpi = request.form.get('dpi')
                try:
                    dpi = int(dpi) or 150
                except (TypeError, ValueError):
                    dpi = 150
                out = os.path.join(session, 'compressed.pdf')
                args = [gs, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                        '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dBATCH',
                        '-dDownsampleColorImages=true',
                        f'-dColorImageResolution={dpi}',
                        f'-sOutputFile={out}', files[0]]
                r = run_cmd(args)
                if not r['ok'] or not os.path.isfile(out):
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                return jsonify({'ok': True, 'input_size': os.path.getsize(files[0]),
                                'output_size': os.path.getsize(out),
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/compressed.pdf'})
            elif action == 'extract':
                fmt = (request.form.get('format') or 'png').lower()
                out_dir = os.path.join(session, 'images')
                os.makedirs(out_dir, exist_ok=True)
                args = [gs, '-sDEVICE=png16m', '-r150', '-o',
                        os.path.join(out_dir, f'page_%d.{fmt}'), files[0]]
                r = run_cmd(args)
                imgs = sorted(glob.glob(os.path.join(out_dir, f'page_*.{fmt}')))
                if not r['ok'] or not imgs:
                    return jsonify({'ok': False, 'error': clean_err(r, session)}), 400
                zip_path = os.path.join(session, 'pdf_images.zip')
                make_zip_from_files(imgs, zip_path)
                return jsonify({'ok': True, 'pages': len(imgs),
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/pdf_images.zip'})
            return jsonify({'ok': False, 'error': '未知操作'}), 400

        @self.route('/mediatools/media', methods=['POST'])
        def mt_media():
            ffmpeg = find_tool('ffmpeg')
            if not ffmpeg:
                return jsonify({'ok': False, 'error': '未安装 ffmpeg'}), 400
            action = request.form.get('action') or 'convert'
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传媒体文件'}), 400
            fmt = (request.form.get('format') or '').lower()
            try:
                crf = int(request.form.get('crf') or 28)
            except (TypeError, ValueError):
                crf = 28
            outputs = []
            results = []
            for item in saved:
                src = item['path']
                base, ext = os.path.splitext(item['filename'])
                if action == 'extract_audio':
                    out_ext = fmt or 'mp3'
                    out = os.path.join(session, f'{base}.{out_ext}')
                    codec = 'libmp3lame' if out_ext == 'mp3' else 'copy'
                    cmd = [ffmpeg, '-i', src, '-vn', '-acodec', codec, '-y', out]
                elif action == 'compress':
                    out_ext = fmt or ext.lstrip('.').lower() or 'mp4'
                    out = os.path.join(session, f'{base}_compressed.{out_ext}')
                    cmd = [ffmpeg, '-i', src, '-c:v', 'libx264', '-crf', str(crf),
                           '-c:a', 'aac', '-b:a', '128k', '-y', out]
                else:
                    out_ext = fmt or ext.lstrip('.').lower() or 'mp4'
                    out = os.path.join(session, f'{base}.{out_ext}')
                    cmd = [ffmpeg, '-i', src, '-c:v', 'libx264', '-crf', str(crf), '-y', out]
                r = run_cmd(cmd, timeout=1800)
                ok = os.path.isfile(out) and os.path.getsize(out) > 0
                results.append({'name': item['filename'], 'ok': ok,
                                'error': '' if ok else clean_err(r, session),
                                'output': os.path.basename(out) if ok else ''})
                if ok:
                    outputs.append(out)
            if len(outputs) == 1:
                return jsonify({'ok': True, 'results': results, 'single': True,
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(outputs[0])}'})
            zip_path = os.path.join(session, 'media_processed.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/media_processed.zip'})

        @self.route('/mediatools/info', methods=['POST'])
        def mt_info():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件'}), 400
            path = saved[0]['path']
            name = saved[0]['filename']
            ext = os.path.splitext(name)[1][1:].lower()
            result = {'name': name, 'size': os.path.getsize(path), 'ext': ext}
            if ext in IMG_EXT:
                magick = find_tool('identify')
                if magick:
                    r = run_cmd([magick, '-format', '%wx%h %m %b', path])
                    if r['ok']:
                        parts = r['output'].strip().split()
                        if parts:
                            dim = parts[0].split('x')
                            result['width'] = int(dim[0]) if len(dim) > 0 else 0
                            result['height'] = int(dim[1]) if len(dim) > 1 else 0
                            result['format'] = parts[1] if len(parts) > 1 else ''
                            result['size_str'] = parts[2] if len(parts) > 2 else ''
                result['type'] = '图片'
            elif ext == 'pdf':
                qpdf = find_tool('qpdf')
                if qpdf:
                    r = run_cmd([qpdf, '--show-npages', path])
                    if r['ok']:
                        try:
                            result['pages'] = int(r['output'].strip())
                        except ValueError:
                            pass
                result['type'] = 'PDF'
            elif ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm',
                         'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a']:
                ffmpeg = find_tool('ffmpeg')
                if ffmpeg:
                    r = run_cmd([ffmpeg, '-i', path])
                    out = r['output'] + '\n' + r['error']
                    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', out)
                    if m:
                        result['duration'] = f'{m.group(1)}:{m.group(2)}:{m.group(3)}'
                    m = re.search(r'bitrate: (\d+) kb/s', out)
                    if m:
                        result['bitrate'] = m.group(1)
                    m = re.search(r'Stream.*Video.* (\d+)x(\d+)', out)
                    if m:
                        result['width'] = int(m.group(1))
                        result['height'] = int(m.group(2))
                    result['video'] = bool(re.search(r'Stream.*Video', out))
                    result['audio'] = bool(re.search(r'Stream.*Audio', out))
                result['type'] = '视频' if ext in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm'] else '音频'
            else:
                result['type'] = classify_ext(ext)
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'info': result})

        # ==================== docconvert ====================
        EXT_MAP = {
            'docx': 'docx', 'html': 'html', 'htm': 'html', 'md': 'markdown',
            'markdown': 'markdown', 'epub': 'epub', 'latex': 'latex', 'tex': 'latex',
            'txt': 'markdown', 'csv': 'csv', 'json': 'json', 'xml': 'xml',
            'rst': 'rst', 'org': 'org', 'pptx': 'pptx', 'xlsx': 'xlsx', 'odt': 'odt',
        }

        @self.route('/docconvert/check', methods=['GET'])
        def doc_check():
            pandoc = find_tool('pandoc')
            if not pandoc:
                return jsonify({'ok': False, 'error': '未安装 pandoc'})
            r = run_cmd([pandoc, '--version'])
            version = ''
            m = r['output'].splitlines()
            if m:
                version = m[0]
            r2 = run_cmd([pandoc, '--list-output-formats'])
            formats = r2['output'].split()
            return jsonify({'ok': True, 'version': version, 'formats': formats})

        @self.route('/docconvert/convert', methods=['POST'])
        def doc_convert():
            pandoc = find_tool('pandoc')
            if not pandoc:
                return jsonify({'ok': False, 'error': '未安装 pandoc'}), 400
            to = (request.form.get('to') or 'html').strip()
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文档'}), 400
            results = []
            outputs = []
            for item in saved:
                src = item['path']
                ext = os.path.splitext(item['filename'])[1][1:].lower()
                from_fmt = EXT_MAP.get(ext, 'markdown')
                base = os.path.splitext(item['filename'])[0]
                out = os.path.join(session, f'{base}.{to}')
                r = run_cmd([pandoc, src, '-f', from_fmt, '-t', to, '-o', out], timeout=600)
                ok = os.path.isfile(out) and os.path.getsize(out) > 0
                results.append({'name': item['filename'], 'ok': ok,
                                'error': '' if ok else clean_err(r, session),
                                'output': os.path.basename(out) if ok else ''})
                if ok:
                    outputs.append(out)
            if len(outputs) == 1:
                return jsonify({'ok': True, 'results': results, 'single': True,
                                'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(outputs[0])}'})
            zip_path = os.path.join(session, 'converted.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/converted.zip'})

        # ==================== networktools ====================
        @self.route('/networktools/download', methods=['POST'])
        def nt_download():
            session = new_session(PLUGIN)
            data = request.get_json(silent=True) or {}
            urls = [u for u in (data.get('urls') or []) if isinstance(u, str) and u.strip()]
            if not urls:
                return jsonify({'ok': False, 'error': '请提供下载链接'}), 400
            pack = bool(data.get('pack'))
            import threading as _t
            import tasks as _taskmod

            def _work():
                tid = _taskmod.begin('yulotool', '下载 %d 个文件' % len(urls), kind='download')
                import requests as reqs
                results = []
                success = 0
                total = len(urls)
                for i, url in enumerate(urls):
                    if not url:
                        continue
                    _taskmod.update(tid, phase='downloading %d/%d' % (i + 1, total),
                                    message='正在下载 %s' % url[:60], progress=int(i / total * 100))
                    try:
                        from urllib.parse import urlparse, unquote
                        path = urlparse(url).path
                        name = unquote(os.path.basename(path)) if path else ''
                        if not name:
                            name = f'download_{uuid.uuid4().hex[:8]}'
                        name = re.sub(r'[^\w.\-\u4e00-\u9fff]', '_', name)[:120]
                        dest = os.path.join(session, name)
                        resp = reqs.get(url, timeout=300, stream=True,
                                        headers={'User-Agent': 'Mozilla/5.0'})
                        resp.raise_for_status()
                        size = 0
                        with open(dest, 'wb') as f:
                            for chunk in resp.iter_content(FILE_CHUNK):
                                if chunk:
                                    f.write(chunk)
                                    size += len(chunk)
                        results.append({'url': url, 'ok': True, 'name': name,
                                        'size': size})
                        success += 1
                    except Exception as e:
                        results.append({'url': url, 'ok': False, 'error': str(e)[:200]})
                _taskmod.update(tid, progress=100, phase='packing')
                try:
                    if pack and success:
                        tool = find_tool('7z')
                        archive = os.path.join(session, 'downloaded.7z')
                        files = [os.path.join(session, r['name']) for r in results if r['ok']]
                        if tool and files:
                            run_cmd([tool, 'a', archive] + files)
                        else:
                            archive = os.path.join(session, 'downloaded.zip')
                            make_zip_from_files(files, archive)
                        _taskmod.finish(tid, True, message='完成 %d/~%d' % (success, total),
                                        progress=100)
                        return
                except Exception:
                    pass
                _taskmod.finish(tid, True, message='完成 %d/%d' % (success, total), progress=100)

            _t.Thread(target=_work, daemon=True).start()
            return jsonify({'ok': True, 'message': '已开始下载 %d 个文件，稍后在任务队列中查看进度' % len(urls)})

        @self.route('/networktools/split', methods=['POST'])
        def nt_split():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件'}), 400
            try:
                chunk_mb = float(request.form.get('chunkSize') or 100)
            except ValueError:
                chunk_mb = 100
            if chunk_mb <= 0:
                chunk_mb = 100
            chunk_size = max(1, int(chunk_mb * 1024 * 1024))
            parts = []
            for item in saved:
                src = item['path']
                base = os.path.join(session, os.path.splitext(item['filename'])[0])
                with open(src, 'rb') as fh:
                    part = 0
                    while True:
                        part += 1
                        out_path = f'{base}.part{part:03d}'
                        written = 0
                        with open(out_path, 'wb') as out:
                            while written < chunk_size:
                                b = fh.read(min(FILE_CHUNK, chunk_size - written))
                                if not b:
                                    break
                                out.write(b)
                                written += len(b)
                        parts.append(out_path)
                        if written < chunk_size:
                            break
            zip_path = os.path.join(session, 'parts.zip')
            make_zip_from_files(parts, zip_path)
            return jsonify({'ok': True, 'parts': len(parts),
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/parts.zip'})

        @self.route('/networktools/join', methods=['POST'])
        def nt_join():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传分片文件'}), 400
            out_name = (request.form.get('name') or 'joined').strip() or 'joined'
            out = os.path.join(session, out_name)
            for item in sorted(saved, key=lambda s: s['filename']):
                with open(item['path'], 'rb') as src, open(out, 'ab') as dst:
                    shutil.copyfileobj(src, dst, FILE_CHUNK)
            return jsonify({'ok': True, 'files': len(saved),
                            'size': os.path.getsize(out),
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(out)}'})

        @self.route('/networktools/rename', methods=['POST'])
        def nt_rename():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传文件'}), 400
            mode = request.form.get('mode') or 'prefix'
            value = request.form.get('value') or ''
            value2 = request.form.get('value2') or ''
            try:
                start_index = int(request.form.get('index') or 1)
            except ValueError:
                start_index = 1
            results = []
            outputs = []
            for i, item in enumerate(saved):
                old = item['filename']
                base, ext = os.path.splitext(old)
                new_base = base
                if mode == 'prefix':
                    new_base = value + base
                elif mode == 'suffix':
                    new_base = base + value
                elif mode == 'replace':
                    new_base = base.replace(value, value2)
                elif mode == 'case':
                    new_base = base.upper() if value == 'upper' else base.lower()
                elif mode == 'regex':
                    try:
                        new_base = re.sub(value, value2, base)
                    except re.error:
                        new_base = base
                elif mode == 'number':
                    width = 3
                    try:
                        width = int(value2 or 3)
                    except ValueError:
                        pass
                    new_base = f'{value}{start_index + i:0{width}d}'
                new_name = new_base + ext
                new_path = os.path.join(session, new_name)
                if new_path != item['path']:
                    shutil.move(item['path'], new_path)
                results.append({'old': old, 'new': new_name, 'ok': True})
                outputs.append(new_path)
            zip_path = os.path.join(session, 'renamed.zip')
            make_zip_from_files(outputs, zip_path)
            return jsonify({'ok': True, 'results': results,
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/renamed.zip'})

        @self.route('/networktools/delete', methods=['POST'])
        def nt_delete():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传要安全删除的文件'}), 400
            try:
                passes = int(request.form.get('passes') or 3)
            except ValueError:
                passes = 3
            passes = max(1, min(passes, 35))
            results = []
            for item in saved:
                deleted = secure_wipe(item['path'], passes)
                results.append({'name': item['filename'], 'deleted': deleted})
            shutil.rmtree(session, ignore_errors=True)
            return jsonify({'ok': True, 'results': results})

        # ==================== videomerge ====================
        @self.route('/videomerge/merge', methods=['POST'])
        def vm_merge():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('files',))
            if len(saved) < 2:
                return jsonify({'ok': False, 'error': '请上传视频和压缩包'}), 400
            video = None
            archive = None
            for item in saved:
                t = detect_archive_type(item['path'])
                if t:
                    archive = item
                else:
                    video = item
            if not video or not archive:
                return jsonify({'ok': False, 'error': '需要同时上传一个视频和一个压缩包 (zip/7z/rar)'}), 400
            arch_type = detect_archive_type(archive['path'])
            video_size = os.path.getsize(video['path'])
            arch_size = os.path.getsize(archive['path'])
            out_name = (request.form.get('name') or
                        os.path.splitext(video['filename'])[0] + '_merged').strip() or 'merged'
            out_path = os.path.join(session, f'{out_name}.mp4')

            crc = crc32_file(archive['path'])

            with open(out_path, 'wb') as out:
                stream_copy(video['path'], out)
                stream_copy(archive['path'], out)
                footer = build_footer(arch_type, arch_size, crc)
                out.write(footer)

            if arch_type == ARCH_ZIP:
                with open(out_path, 'r+b') as out:
                    err = fix_zip_offsets(out, video_size, arch_size)
                    if err:
                        return jsonify({'ok': False, 'error': f'ZIP 偏移修正失败: {err}'}), 400
                with open(out_path, 'rb') as f:
                    f.seek(video_size)
                    h = 0
                    remaining = arch_size
                    while remaining > 0:
                        b = f.read(min(CHUNK, remaining))
                        if not b:
                            break
                        h = zlib.crc32(b, h)
                        remaining -= len(b)
                crc = h & 0xFFFFFFFF
                with open(out_path, 'r+b') as f:
                    f.seek(video_size + arch_size + 24)
                    f.write(struct.pack('<I', crc))
            return jsonify({'ok': True, 'video': video['filename'],
                            'archive': archive['filename'],
                            'arch_type': arch_type,
                            'arch_size': arch_size,
                            'output_size': os.path.getsize(out_path),
                            'crc32': f'{crc:08x}',
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/{os.path.basename(out_path)}'})

        @self.route('/videomerge/info', methods=['POST'])
        def vm_info():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传融合文件'}), 400
            path = saved[0]['path']
            total = os.path.getsize(path)
            with open(path, 'rb') as f:
                f.seek(max(0, total - FOOTER_LEN))
                footer_data = f.read(FOOTER_LEN)
            fmeta = parse_footer(footer_data)
            if not fmeta:
                return jsonify({'ok': False, 'error': '未检测到 YLVFUSN1 融合尾部'}), 400
            arch_offset = total - FOOTER_LEN - fmeta['arch_size']
            types = {ARCH_ZIP: 'ZIP', ARCH_7Z: '7z', ARCH_RAR: 'RAR'}
            fh = open(path, 'rb')
            fh.seek(arch_offset)
            h = 0
            remaining = fmeta['arch_size']
            while remaining > 0:
                b = fh.read(min(CHUNK, remaining))
                if not b:
                    break
                h = zlib.crc32(b, h)
                remaining -= len(b)
            fh.close()
            actual_crc = h & 0xFFFFFFFF
            return jsonify({'ok': True,
                            'arch_type': types.get(fmeta['arch_type'], fmeta['arch_type']),
                            'arch_size': fmeta['arch_size'],
                            'arch_offset': arch_offset,
                            'video_size': arch_offset,
                            'total_size': total,
                            'crc32': f'{fmeta["crc32"]:08x}',
                            'crc_ok': actual_crc == fmeta['crc32']})

        @self.route('/videomerge/extract', methods=['POST'])
        def vm_extract():
            session = new_session(PLUGIN)
            saved = save_uploads(request, session, fields=('file', 'files'))
            if not saved:
                return jsonify({'ok': False, 'error': '请上传融合文件'}), 400
            path = saved[0]['path']
            total = os.path.getsize(path)
            with open(path, 'rb') as f:
                f.seek(max(0, total - FOOTER_LEN))
                footer_data = f.read(FOOTER_LEN)
            fmeta = parse_footer(footer_data)
            if not fmeta:
                return jsonify({'ok': False, 'error': '未检测到 YLVFUSN1 融合尾部'}), 400
            arch_offset = total - FOOTER_LEN - fmeta['arch_size']
            types = {ARCH_ZIP: 'zip', ARCH_7Z: '7z', ARCH_RAR: 'rar'}
            ext = types.get(fmeta['arch_type'], 'bin')
            out_path = os.path.join(session, f'extracted.{ext}')
            with open(out_path, 'wb') as out:
                stream_copy(path, out, start=arch_offset, size=fmeta['arch_size'])
            return jsonify({'ok': True, 'arch_type': ext,
                            'arch_size': fmeta['arch_size'],
                            'crc32': f'{fmeta["crc32"]:08x}',
                            'download': f'/api/plugins/yulotool/file/{os.path.basename(session)}/extracted.{ext}'})
