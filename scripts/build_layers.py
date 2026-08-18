#!/usr/bin/env python3
"""长安 / 边塞插画图层拆分 v2：仅自身颜色（非最近邻）+ 垂直扩散补全。"""
import os
import numpy as np
from PIL import Image

W, H = 1536, 960


def majority_filter(lab, n_cls, iters=2):
    out = lab
    for _ in range(iters):
        counts = np.zeros((n_cls, H, W), np.int16)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                counts += (np.roll(np.roll(out, dy, 0), dx, 1)[None] ==
                           np.arange(n_cls)[:, None, None])
        out = counts.argmax(0).astype(np.int32)
    return out


def vfill(color, known, cap=120):
    """垂直最近邻补全：仅延伸到自身像素 120px 内，更远处用本层中位色平铺。

    返回补全后的颜色图。近距离沿列取最近已知色（边缘连续），
    远距离平铺中位色（避免稀疏图层出现贯穿全图的竖纹）。
    """
    h = known.shape[0]
    median = np.median(color[known].reshape(-1, 3), axis=0) if known.any() else np.array([255, 255, 255])
    grid = np.broadcast_to(np.arange(h)[:, None], known.shape)

    best_color = np.full_like(color, median)
    best_dist = np.full(known.shape, 10 ** 9)

    for reverse in (False, True):
        idx = np.where(known, grid, -1)
        if reverse:
            idx = idx[::-1]
            idx = np.where(idx >= 0, idx, 10 ** 9)
            idx = np.minimum.accumulate(idx, axis=0)[::-1]
            idx = np.where(idx >= 10 ** 9, -1, idx)
        else:
            idx = np.maximum.accumulate(idx, axis=0)
        valid = idx >= 0
        dist = np.where(valid, np.abs(grid - idx), 10 ** 9)
        iy, ix = np.where(valid & (dist < best_dist))
        best_color[iy, ix] = color[idx[iy, ix], ix]
        best_dist[iy, ix] = dist[iy, ix]

    out = np.where((best_dist <= cap)[..., None], best_color,
                   np.broadcast_to(median, color.shape))
    out[known] = color[known]
    return out.astype(np.uint8)


def build(name, assign_fn, layer_names):
    rgb = np.asarray(Image.open(f'image/{name}.png').convert('RGB'))
    lab = np.load(f'image/layers/{name}-labels.npy')
    cen = np.load(f'image/layers/{name}-centers.npy')
    lab = majority_filter(lab, len(cen))
    assign = assign_fn(lab, rgb.astype(int))
    L = len(layer_names)

    short = name.split('-')[1]
    outdir = f'image/layers/{short}'
    os.makedirs(outdir, exist_ok=True)

    layers_rgba = []
    for i in range(L):
        own = assign == i
        opaque = assign >= i
        color = vfill(rgb, own) if (assign > i).any() else rgb
        rgba = np.dstack([color, np.where(opaque, 255, 0).astype(np.uint8)])
        layers_rgba.append(rgba)
        Image.fromarray(rgba, 'RGBA').save(f'{outdir}/{i + 1:02d}-{layer_names[i]}.png')
        print(f'  {outdir}/{i + 1:02d}-{layer_names[i]}.png  覆盖率 {own.mean() * 100:.1f}%')

    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for rgba in layers_rgba:
        canvas = Image.alpha_composite(canvas, Image.fromarray(rgba, 'RGBA'))
    diff = np.abs(np.asarray(canvas.convert('RGB')).astype(np.int16) - rgb.astype(np.int16)).max()
    print(f'  叠放还原最大像素差: {diff}')

    checker = ((np.indices((H, W)).sum(0) // 16) % 2 == 0)
    bg = np.where(checker[..., None], 225, 190).astype(np.uint8)
    bg = np.repeat(bg, 3, axis=2) if bg.shape[2] == 1 else bg
    tiles = [Image.fromarray(rgb), canvas.convert('RGB')]
    for rgba in layers_rgba:
        a = rgba[..., 3:4].astype(np.float32) / 255
        tiles.append(Image.fromarray((rgba[..., :3] * a + bg * (1 - a)).astype(np.uint8)))
    tw, th = W // 2, H // 2
    cols = 4
    sheet = Image.new('RGB', (cols * tw, ((len(tiles) + cols - 1) // cols) * th), (255, 0, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t.resize((tw, th), Image.LANCZOS), ((k % cols) * tw, (k // cols) * th))
    sheet.save(f'image/layers/{name}-layers-montage.png')
    print(f'  预览: image/layers/{name}-layers-montage.png')


def assign_frontier(lab, rgb):
    ys, xs = np.mgrid[0:H, 0:W]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    bright = (r + g + b) / 3
    red = (r > 120) & (r - g > 35) & (r - b > 35)
    m = np.select(
        [lab == 5, lab == 2, lab == 1, lab == 4, lab == 3, lab == 7, lab == 0, lab == 6, lab == 8],
        [0, np.where(ys < 600, 1, 4), 2, 2, 3, 3, np.where(ys < 560, 3, 4), np.where(ys < 600, 1, 4), 4],
    )
    # 云雾/敌楼浅色体（与天色相同的簇 5 在山区的部分）归入天空，避免远山层出现竖纹
    m[(lab == 5) & (ys >= 380)] = 0
    # 敌楼整体强制归入主峰长城层（v4 图中敌楼位于 x≈850-1030, y≈115-355）
    tower_rect = (xs > 840) & (xs < 1040) & (ys > 115) & (ys < 355)
    m[tower_rect] = 3
    text_zone = (xs < 270) & (ys < 470) & ((bright < 150) | red)
    moon = (r > 225) & (g > 225) & (b > 215) & (ys < 300) & (xs > 900)
    birds = (bright < 130) & (ys < 340) & ~text_zone & ~tower_rect
    m[text_zone | moon | birds] = 0
    # 红旗 + 右下山脚暗色（士兵/马匹，含蓝灰甲胄）→ 士兵层
    m[red & (ys > 400)] = 4
    m[(bright < 175) & (ys > 600) & (xs > 620)] = 4
    # 兜底：天空层不应含有暗色/红色像素（题字/月亮/飞鸟除外）
    decor = text_zone | moon | birds
    bad = (m == 0) & ~decor & ((bright < 150) | red)
    m[bad & (ys < 600)] = 2
    m[bad & (ys >= 600)] = 4
    return m.astype(np.int32)


def assign_changan(lab, rgb):
    ys, xs = np.mgrid[0:H, 0:W]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    bright = (r + g + b) / 3
    bgzone = (ys > 330) & (ys < 760) & ((xs < 560) | (xs > 1300))
    m = np.select(
        [lab == 2, lab == 1, lab == 4, lab == 0, lab == 3, lab == 5, lab == 6, lab == 7, lab == 8],
        [np.where(ys < 830, 0, 3),
         np.where((ys < 240) & (xs > 1100), 0, 2),
         2, 2, 2,
         np.where(bgzone, 1, np.where(ys < 830, 2, 3)),   # 5 浅赭: 雁塔(背景区)/门楼细节/地
         np.where(bgzone, 1, np.where(ys < 830, 2, 3)),   # 6 中棕: 背景树影/门楼阴影/地
         2,                                              # 7 深褐: 屋顶/枝干
         np.where(bgzone, 1, np.where(ys < 830, 2, 3))],  # 8 橄榄: 树
    )
    text_zone = (xs < 270) & (ys < 470) & ((bright < 140) | ((r > 120) & (r - g > 40) & (r - b > 40)))
    m[text_zone] = 0
    # 太阳整体归天空层（含被标成深赭色的内部像素）
    sun_region = (xs > 1150) & (ys < 230)
    m[sun_region & (bright < 225)] = 0
    # 米白簇的"孤立碎片"（邻域内米白密度低 = 嵌在深色物体内部）归所属物体层；
    # 大片连通的天空/云密度高，保持天空层
    integral = (lab == 2).astype(np.float64).cumsum(0).cumsum(1)
    r_ = 12
    y0 = np.clip(np.arange(H) - r_, 0, H); y1 = np.clip(np.arange(H) + r_ + 1, 0, H)
    x0 = np.clip(np.arange(W) - r_, 0, W); x1 = np.clip(np.arange(W) + r_ + 1, 0, W)
    area = (y1 - y0)[:, None] * (x1 - x0)[None, :]
    s = integral[np.ix_(y1 - 1, x1 - 1)] if False else None
    # 用边界安全的方式计算盒滤波
    def box_at(ii, xx):
        return integral[np.clip(ii, 0, H - 1)][:, np.clip(xx, 0, W - 1)]
    s = (box_at(y1 - 1, x1 - 1)
         - box_at(y0 - 1, x1 - 1) * (y0 > 0)[:, None]
         - box_at(y1 - 1, x0 - 1) * (x0 > 0)[None, :]
         + box_at(y0 - 1, x0 - 1) * ((y0 > 0)[:, None] & (x0 > 0)[None, :]))
    density = s / area
    frag = (lab == 2) & (density < 0.55)
    gate_rect = (xs > 560) & (xs < 1440) & (ys > 150) & (ys < 880)
    m[frag & gate_rect] = 2
    m[frag & bgzone] = 1
    # 背景区里的深色轮廓（雁塔檐线等）也归入远景
    m[bgzone & (lab == 7)] = 1
    ground = (ys >= 880) | ((ys >= 830) & np.isin(lab, [2, 5, 6, 8]))
    m[ground] = 3
    boxes = (((xs > 250) & (xs < 370)) | ((xs > 460) & (xs < 570)) | ((xs > 1090) & (xs < 1260)))
    figures = boxes & (ys > 780) & (ys < 960) & ((bright < 150) | ((r > 130) & (r - g > 45)))
    m[figures] = 3
    # 兜底：天空层不应含有暗色/红色像素（标签平滑把细线条标成了天空色）
    notdecor = ~((xs < 270) & (ys < 470))
    bad = (m == 0) & notdecor & ~sun_region & ((bright < 150) | ((r > 120) & (r - g > 40) & (r - b > 40)))
    m[bad & (xs >= 560) & (xs <= 1440)] = 2
    m[bad & ((xs < 560) | (xs > 1440))] = 1
    return m.astype(np.int32)


if __name__ == '__main__':
    print('== 边塞 ==')
    build('act2-frontier', assign_frontier, ['sky-decor', 'mountains-far', 'mountains-mid', 'peak-wall', 'ground-soldiers'])
    print('== 长安 ==')
    build('act2-changan', assign_changan, ['sky-decor', 'city-far', 'gate-wall', 'ground-figures'])
