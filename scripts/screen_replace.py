"""Put the creator's real app screens onto a real hand-held phone (stock clip with a blank white screen).

Per output frame (25 fps): find the white screen (largest bright component that doesn't touch the frame edge), fit its
four edges with lines (rounded corners -> true corners), smooth the corners over time, warp the app screenshot into
that quad, and composite through the screen's own mask so the real notch, bezel and any finger stay on top. The white
screen's luminance is kept as a light shading map so the app picks up the shot's real light falloff.

usage: python <SK>/scripts/screen_replace.py <src.mp4> <start> <dur> <out.mp4> <img0>[@t,<img1>...] [--thr 232] [--slide 0.28]
       e.g. ... assets/img/app-reminder.png@0,assets/img/app-success.png@2.0
Source: a stock clip of a hand holding a phone with a plain white screen (stock.py search "holding phone white screen"),
centred enough that the screen never touches the frame edge. Check the result on a contact sheet before using it.
"""
import argparse
import subprocess

import cv2
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("start", type=float); ap.add_argument("dur", type=float); ap.add_argument("out")
ap.add_argument("screens")
ap.add_argument("--thr", type=int, default=232)
ap.add_argument("--slide", type=float, default=0.28)
ap.add_argument("--fps", type=float, default=25.0)
ap.add_argument("--grade", default="null", help="optional ffmpeg filter for the result; default: none (colours as shot)")
a = ap.parse_args()

W, H = 1080, 1920
screens = []
for part in a.screens.split(","):
    p, t = (part.split("@") + ["0"])[:2]
    screens.append((float(t), cv2.imread(p, cv2.IMREAD_COLOR)))

cap = cv2.VideoCapture(a.src)
src_fps = cap.get(cv2.CAP_PROP_FPS)
n_out = int(round(a.dur * a.fps))


def to_canvas(fr):
    h, w = fr.shape[:2]
    s = max(W / w, H / h)
    fr = cv2.resize(fr, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA)
    y0, x0 = (fr.shape[0] - H) // 2, (fr.shape[1] - W) // 2
    return fr[y0:y0 + H, x0:x0 + W]


frames = []
for i in range(n_out):
    t = a.start + i / a.fps
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * src_fps)))
    ok, fr = cap.read()
    if not ok:
        fr = frames[-1].copy()
    else:
        fr = to_canvas(fr)
    frames.append(fr)


def screen_mask(fr):
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    m = (g > a.thr).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    best, area = 0, 0
    for k in range(1, n):
        x, y, w, h, ar = st[k]
        if x == 0 or y == 0 or x + w >= W or y + h >= H:
            continue
        if not (1.5 < h / max(w, 1) < 2.7):
            continue
        if ar > area:
            best, area = k, ar
    mk = (lab == best).astype(np.uint8) * 255
    mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return mk, g


def quad_from_mask(mk):
    cnts, _ = cv2.findContours(mk, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    peri = cv2.arcLength(hull, True)
    approx = None
    for eps in np.linspace(0.01, 0.08, 30):
        ap_ = cv2.approxPolyDP(hull, eps * peri, True)
        if len(ap_) == 4:
            approx = ap_.reshape(4, 2).astype(np.float64)
            break
    if approx is None:
        r = cv2.minAreaRect(c)
        approx = cv2.boxPoints(r).astype(np.float64)
    # order tl, tr, br, bl
    s = approx.sum(1); d = np.diff(approx, axis=1).ravel()
    q = np.array([approx[np.argmin(s)], approx[np.argmin(d)], approx[np.argmax(s)], approx[np.argmax(d)]])
    # refine: fit a line to the straight middle part of each side, intersect neighbours (rounded corners -> true corners).
    # Fit on the filled convex hull, not the raw contour: the hull bridges the notch, so the top edge stays straight.
    hm = np.zeros_like(mk)
    cv2.fillConvexPoly(hm, hull, 255)
    hc, _ = cv2.findContours(hm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pts = max(hc, key=cv2.contourArea).reshape(-1, 2).astype(np.float64)
    lines = []
    for k in range(4):
        p0, p1 = q[k], q[(k + 1) % 4]
        v = p1 - p0; L = np.linalg.norm(v); u = v / L; nrm = np.array([-u[1], u[0]])
        rel = pts - p0
        along = rel @ u; off = rel @ nrm
        sel = (along > 0.2 * L) & (along < 0.8 * L) & (np.abs(off) < 12)
        if sel.sum() < 10:
            lines.append((p0, u)); continue
        vx, vy, x0, y0 = cv2.fitLine(pts[sel].astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        lines.append((np.array([x0, y0]), np.array([vx, vy])))

    def inter(l1, l2):
        (p, r), (q_, s_) = l1, l2
        A = np.array([[r[0], -s_[0]], [r[1], -s_[1]]])
        t = np.linalg.solve(A, q_ - p)
        return p + t[0] * r

    return np.array([inter(lines[(k - 1) % 4], lines[k]) for k in range(4)])


masks, quads, lums = [], [], []
for fr in frames:
    mk, g = screen_mask(fr)
    masks.append(mk); lums.append(g)
    quads.append(quad_from_mask(mk))
quads = np.array(quads)
# temporal smoothing (gaussian, +-3 frames) so the warp doesn't shimmer
k = np.exp(-0.5 * (np.arange(-3, 4) / 1.6) ** 2); k /= k.sum()
pad = np.pad(quads, ((3, 3), (0, 0), (0, 0)), mode="edge")
sq = np.stack([np.tensordot(k, pad[i:i + 7], axes=(0, 0)) for i in range(len(quads))])


def screen_img(t):
    """App screen at local time t, sliding to the next screenshot at its switch time."""
    cur = screens[0][1]
    for i, (ts, im) in enumerate(screens):
        if i == 0:
            continue
        if t >= ts + a.slide:
            cur = im
        elif t >= ts:
            prev = screens[i - 1][1]
            h, w = prev.shape[:2]
            im2 = cv2.resize(im, (w, h))
            f = (t - ts) / a.slide; f = 1 - (1 - f) ** 3
            off = int(round(w * f))
            out = np.zeros_like(prev)
            out[:, :w - off] = prev[:, off:]
            out[:, w - off:] = im2[:, :off]
            return out
    return cur


proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(a.fps),
                         "-i", "-", "-vf", a.grade, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                         "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
for i, fr in enumerate(frames):
    t = i / a.fps
    img = screen_img(t)
    h, w = img.shape[:2]
    q = sq[i]
    c = q.mean(0); q = c + (q - c) * 1.012                       # tiny overscan; the mask trims it back to the glass
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32(q))
    warped = cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_CUBIC)
    alpha = cv2.GaussianBlur(masks[i].astype(np.float32) / 255, (0, 0), 1.2)[..., None]
    g = lums[i].astype(np.float32)
    ref = np.percentile(g[masks[i] > 0], 95) if (masks[i] > 0).any() else 250
    shade = np.clip(g / max(ref, 1), 0.8, 1.04)[..., None]       # the real screen's light falloff
    comp = warped.astype(np.float32) * (0.9 + 0.1 * shade) * 0.985
    out = fr.astype(np.float32) * (1 - alpha) + comp * alpha
    proc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
proc.stdin.close(); proc.wait()
print("wrote", a.out, len(frames), "frames")
