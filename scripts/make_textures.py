"""video-edit textures v2 — procedural, deterministic (seeded). Same file names and formats as before, so every
composition keeps working:

  paper-grain.png  1080x1920 grey (128 = neutral) for the soft-light overlay: cotton-rag paper — curly fibres in every
                   direction, soft cloudy mottling, tiny inclusions
  leaf-shadow.png  1500x2600 RGBA warm shadow for the multiply overlay (window-light gobo): arching fern fronds from
                   the top-left and bottom-right corners, and a faint, very soft window-frame shadow

usage: python make_textures.py [out_dir]      (default: ../assets/img)
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20261015)


def field(w, h, scale, sigma):
    small = rng.normal(0, 1, (h // scale + 2, w // scale + 2))
    img = Image.fromarray(((small - small.min()) / np.ptp(small) * 255).astype(np.uint8))
    a = np.asarray(img.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))).astype(float)
    return (a - a.mean()) / (a.std() + 1e-6)


def paper_grain(w=1080, h=1920):
    fine = rng.normal(0, 1, (h, w))
    mottle = field(w, h, 60, 18) * 0.7 + field(w, h, 14, 4) * 0.5
    fib = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(fib)
    for _ in range(3400):                                  # curly cotton fibres, any direction
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        ang = rng.uniform(0, 2 * math.pi)
        curl = rng.normal(0, 0.18)
        pts = [(x, y)]
        for _ in range(int(rng.uniform(4, 11))):
            ang += curl + rng.normal(0, 0.12)
            step = rng.uniform(3.5, 6.5)
            x, y = x + step * math.cos(ang), y + step * math.sin(ang)
            pts.append((x, y))
        d.line(pts, fill=int(rng.uniform(50, 140)), width=1)
    fib = np.asarray(fib.filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255
    fleck = np.zeros((h, w))
    for _ in range(900):                                   # tiny inclusions, mostly darker
        cx, cy = rng.integers(0, w), rng.integers(0, h)
        fleck[max(0, cy - 1):cy + 1, max(0, cx - 1):cx + 1] = rng.choice([-1.0, -1.0, -1.0, 0.6])
    fleck = np.asarray(Image.fromarray(((fleck + 1) * 127).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 127 - 1
    tex = 128 + fine * 8 + mottle * 7 - fib * 20 + fleck * 18
    Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8)).save(OUT / "paper-grain.png", optimize=True)


def leaflet(draw, x, y, length, width, ang):
    pts = []
    for i in range(25):
        t = i / 24
        pts.append((t * length, math.sin(math.pi * t) ** 0.7 * width / 2 * (1 - 0.35 * t)))
    pts += [(px, -py) for px, py in reversed(pts)]
    ca, sa = math.cos(ang), math.sin(ang)
    draw.polygon([(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts], fill=255)


def frond(draw, x, y, ang, length, bend, n, scale):
    """an arching fern frond: a curved stem with paired leaflets that shrink towards the tip"""
    pts = [(x, y)]
    a = ang
    step = length / 60
    for _ in range(60):
        a += bend / 60
        x, y = x + step * math.cos(a), y + step * math.sin(a)
        pts.append((x, y))
    draw.line(pts, fill=255, width=max(3, int(5 * scale)))
    for i in range(1, n + 1):
        k = int(i / (n + 1) * 60)
        px, py = pts[k]
        tan = math.atan2(pts[min(60, k + 1)][1] - pts[k][1], pts[min(60, k + 1)][0] - pts[k][0])
        shrink = 1 - 0.65 * i / (n + 1)
        for side in (-1, 1):
            leaflet(draw, px, py, rng.uniform(150, 200) * scale * shrink, rng.uniform(46, 60) * scale * shrink,
                    tan + side * rng.uniform(0.95, 1.25))


def leaf_shadow(w=1500, h=2600):
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    for (x, y, ang, ln, bend, n, sc) in [                  # fronds enter from the top-left and the bottom-right
        (-60, -40, 0.95, 1350, 0.55, 22, 1.1), (-80, 420, 0.35, 1100, 0.45, 18, 0.95),
        (200, -120, 1.35, 950, 0.35, 15, 0.85), (1560, 2650, -2.25, 1250, 0.5, 21, 1.05),
        (1580, 2150, -2.75, 950, 0.4, 15, 0.9)]:
        frond(d, x, y, ang, ln, bend, n, sc)
    soft = np.asarray(mask.filter(ImageFilter.GaussianBlur(24))).astype(float)
    crisp = np.asarray(mask.filter(ImageFilter.GaussianBlur(5))).astype(float)
    a = soft * 0.6 + crisp * 0.4
    win = Image.new("L", (w, h), 0)                        # faint window-frame shadow (a soft cross), upper right
    dw = ImageDraw.Draw(win)
    dw.rectangle([980, 0, 1050, 1500], fill=255)
    dw.rectangle([620, 700, 1500, 770], fill=255)
    win = np.asarray(win.filter(ImageFilter.GaussianBlur(45))).astype(float) * 0.5
    a = np.maximum(a, win)
    alpha = (a / 255 * 0.42 * 255).astype(np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 64, 56, 46   # warm grey-brown shadow
    rgba[..., 3] = alpha
    Image.fromarray(rgba, "RGBA").save(OUT / "leaf-shadow.png", optimize=True)


paper_grain()
leaf_shadow()
print("textures written to", OUT)
