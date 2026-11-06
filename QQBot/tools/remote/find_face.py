# -*- coding: utf-8 -*-
"""在立绘/回忆大厅图里自动定位角色脸部（利用星野的金色左眼）。

思路：找「金黄色」像素簇 → 得到左眼位置 → 以眼睛为基准外扩一个方形框。
比手填坐标靠谱，改图/换源也不用重调。

用法:
    /opt/rcbot/venv/bin/python find_face.py <图片> [--side 110] [--dy 40]
"""
import sys
from PIL import Image


def find_gold(im, tol=70):
    W, H = im.size
    px = im.convert('RGB').load()
    xs, ys = [], []
    step = 1
    for y in range(0, H, step):
        for x in range(0, W, step):
            r, g, b = px[x, y]
            # 金黄瞳：高 R、中高 G、低 B；皮肤是低饱和（r≈g≈b），排除
            if r > 190 and g > 140 and b < 150 and (r - b) > 70 and abs(r - g) < 90:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def main():
    path = sys.argv[1]
    side = int(sys.argv[sys.argv.index('--side') + 1]) if '--side' in sys.argv else 110
    dy = int(sys.argv[sys.argv.index('--dy') + 1]) if '--dy' in sys.argv else 40
    im = Image.open(path)
    box = find_gold(im)
    if not box:
        print('ERR 找不到金色像素')
        return 1
    l, t, r, b = box
    cx = (l + r) // 2
    cy = (t + b) // 2
    # 眼睛在整个头部的上半部分 → 脸中心比眼睛低一点
    face_cx = cx
    face_cy = cy + dy
    out = (face_cx - side, face_cy - side, face_cx + side, face_cy + side)
    print('gold=%s eye=(%d,%d) face_box=%d,%d,%d,%d' %
          (box, cx, cy, out[0], out[1], out[2], out[3]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
