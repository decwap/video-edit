"""Prepare the pop-out face panel for a whole A-roll: fit it to this speaker, cut the person out, track the head.

usage: python make_panel.py --src assets/aroll_wide.mp4
       [--out assets/person.webm] [--json build/panel.json] [--head-w 459] [--measure-only]
       [--cli hyperframes@0.8.106]   (pin the CLI the project was initialised with)

It writes the transparent cutout and build/panel.json, which face_panel.use_panel() reads. Every number is in
"1080 px": footage pixels on a frame scaled to 1080 wide, whatever the real size of the file.

  1. A quick pass on 15 frames measures the head's width and picks the footage scale, so the head lands at the size and
     height the speaker approved, on any framing.
  2. The upper part of the frame goes through `hyperframes remove-background`: a shorter strip gives the model more
     pixels on the head than a full 9:16 frame would. It runs on this computer (no upload, no credits), about 0.2 s per
     frame on Apple silicon and about 1 s on CPU, so run it in the background with a log.
  3. Footage and cutout both get bt709 colour tags. Without that the browser draws them at different brightness and a
     seam shows at the panel's edge.
  4. The head's top and centre are tracked on every frame, so each panel beat can centre the head and hold it at the
     same height, which also hides jump cuts.
"""
import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from face_panel import fit_panel  # noqa: E402

AW = 360                # analysis width in px
SAMPLES = 15
STRIP_H = 690           # strip height in 1080 px (a 1.57:1 strip keeps the head large for the model)
STRIP_MARGIN = 120      # room above the highest head position, in 1080 px
JUMP_PX = 12            # a head jump this big between frames is reported: cut a panel beat there


def run(*cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(str(c) for c in cmd)}\n{r.stderr[-800:]}")
    return r.stdout


def probe(path):
    out = run("ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
              "stream=codec_name,width,height,avg_frame_rate,color_transfer,color_primaries,color_space,nb_read_packets",
              "-show_entries", "format=duration", "-of", "json", path)
    d = json.loads(out)
    return {**d["streams"][0], "duration": float(d["format"]["duration"])}


def rate(text):
    a, _, b = text.partition("/")
    return float(a) / float(b or 1)


def even(v):
    return int(round(v / 2)) * 2


def remove_background(cli, src, out):
    # No shell=True: on Windows it exited 0 without writing anything. Resolve npx(.cmd) explicitly instead.
    npx = shutil.which("npx") or "npx"
    subprocess.run([npx, "--yes", cli, "remove-background", str(src), "-o", str(Path(out).resolve()), "--quality", "best"], check=True)
    if not Path(out).exists() or Path(out).stat().st_size == 0:
        sys.exit(f"no cutout written to {out}")


def alpha_frames(webm):
    """Yield the alpha of each frame as a bool array AW px wide. libvpx is required: ffmpeg's own VP9 decoder drops alpha."""
    p = probe(webm)
    h = even(p["height"] * AW / p["width"])
    pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", str(webm), "-vf", f"alphaextract,scale={AW}:{h}",
                             "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    size = AW * h
    while True:
        raw = pipe.stdout.read(size)
        if len(raw) < size:
            break
        yield np.frombuffer(raw, dtype=np.uint8).reshape(h, AW) > 128
    if pipe.wait():
        sys.exit("could not read the cutout's alpha: this ffmpeg needs the libvpx-vp9 decoder")


def measure_frame(mask):
    """Head top and head width of one silhouette, in analysis px."""
    counts = mask.sum(axis=1).astype(float)
    rows = np.where(counts >= 12)[0]
    if not len(rows):
        return None
    top = int(rows[0])
    w = np.convolve(counts, np.ones(7) / 7, mode="same")
    peak = 0.0
    for y in range(top, len(w)):             # the head's widest row comes just before the silhouette narrows into the neck
        peak = max(peak, w[y])
        if w[y] < 0.92 * peak:
            return top, float(peak)
    for y in range(top, len(w) - 10):        # no narrowing (long hair, a raised collar): where it first stops growing
        if w[y] >= 40 and w[y + 10] - w[y] < 0.05 * w[y]:
            return top, float(w[y])
    return top, float(peak)


def measure_head(src, cli, head_w):
    """Head width and highest head top in 1080 px, from a few frames spread across the video."""
    p = probe(src)
    scale = 1080 / AW
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        step = max(1, int(p["nb_read_packets"]) // SAMPLES)
        run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"select='not(mod(n,{step}))',scale=720:-2,setpts=N/25/TB", "-r", "25", "-an",
            "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", tmp / "samples.mp4")
        remove_background(cli, tmp / "samples.mp4", tmp / "samples.webm")
        found = [m for m in map(measure_frame, alpha_frames(tmp / "samples.webm")) if m]
    if not found:
        sys.exit("no person found in the sampled frames")
    tops = [m[0] * scale for m in found]
    widths = [m[1] * scale for m in found]
    head_w, note = (head_w, "--head-w") if head_w else (statistics.median(widths), f"measured {min(widths):.0f}-{max(widths):.0f}")
    print(f"head: top {min(tops):.0f}-{max(tops):.0f}, width {head_w:.0f} ({note})", flush=True)
    return head_w, min(tops)


def tag_footage(src):
    """Give the footage bt709 colour tags in place, by stream copy (the picture is untouched)."""
    p = probe(src)
    if p.get("color_transfer") == "bt709" and p.get("color_primaries") == "bt709" and p.get("color_space") == "bt709":
        return
    bsf = {"h264": "h264_metadata", "hevc": "hevc_metadata"}.get(p["codec_name"])
    if not bsf:
        sys.exit(f"{src} is {p['codec_name']} with colour tags {p.get('color_transfer')}: re-encode it to H.264 bt709 first")
    tmp = Path(src).with_name(Path(src).stem + ".tagged" + Path(src).suffix)
    run("ffmpeg", "-v", "error", "-y", "-i", src, "-map", "0", "-c", "copy", "-bsf:v",
        f"{bsf}=transfer_characteristics=1:colour_primaries=1:matrix_coefficients=1",
        "-color_trc", "bt709", "-color_primaries", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", tmp)
    os.replace(tmp, src)
    print(f"footage tagged bt709 (was {p.get('color_transfer')}): {src}", flush=True)


def tag_cutout(path):
    tmp = Path(path).with_name(Path(path).stem + ".tagged.webm")
    run("ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-i", path, "-map", "0:v", "-c", "copy", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", "-metadata:s:v", "alpha_mode=1", tmp)
    os.replace(tmp, path)


def track_head(cutout, strip_top):
    """Head top and centre on every frame in 1080 px, gaps filled from the neighbours."""
    scale = 1080 / AW
    tops, cxs = [], []
    for mask in alpha_frames(cutout):
        rows = np.where(mask.sum(axis=1) >= 12)[0]
        if not len(rows):
            tops.append(np.nan)
            cxs.append(np.nan)
            continue
        t = int(rows[0])
        xs = np.where(mask[t:t + round(120 / scale)])[1]   # the crown only: the shoulders and hands do not pull the centre
        tops.append(strip_top + t * scale)
        cxs.append(float(xs.mean()) * scale)
    tops, cxs = np.array(tops), np.array(cxs)
    gaps = int(np.isnan(tops).sum())
    if gaps == len(tops):
        sys.exit("no person found in the cutout")
    if gaps:
        print(f"warning: no person on {gaps} of {len(tops)} frames, filled from the neighbours", flush=True)
        idx = np.arange(len(tops))
        ok = ~np.isnan(tops)
        tops, cxs = np.interp(idx, idx[ok], tops[ok]), np.interp(idx, idx[ok], cxs[ok])
    return tops, cxs


def main():
    ap = argparse.ArgumentParser(description="Prepare the pop-out face panel for an A-roll")
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default="assets/person.webm")
    ap.add_argument("--json", default="build/panel.json")
    ap.add_argument("--head-w", type=float, help="head width in 1080 px, when long hair or a hat throws the measurement off")
    ap.add_argument("--measure-only", action="store_true", help="print the fit and stop, before the slow cutout")
    ap.add_argument("--cli", default="hyperframes@0.8.106")
    a = ap.parse_args()

    p = probe(a.src)
    fps = rate(p["avg_frame_rate"])
    px = p["width"] / 1080         # real px per 1080 px
    head_w, top_min = measure_head(a.src, a.cli, a.head_w)
    fit = fit_panel(head_w)
    print(f"fit: scale {fit['k_wide']} wide / {fit['k_tight']} tight, head top at y {fit['head_at_wide']} / {fit['head_at_tight']}", flush=True)
    if fit["k_wide"] > 1.6:
        print(f"warning: scale {fit['k_wide']} enlarges the footage a lot, so the speaker will look soft. A closer shot or 2K source would help.", flush=True)
    frame_h = p["height"] / px
    if fit["head_at_wide"] - fit["k_wide"] * top_min + fit["k_wide"] * frame_h < 1920:
        print("warning: the head is very low in this footage, so the frame may not reach the bottom of the panel. Check a snapshot.", flush=True)
    if a.measure_only:
        return

    strip_top = max(0, even(top_min - STRIP_MARGIN))
    strip_h = even(min(STRIP_H, frame_h - strip_top))
    tag_footage(a.src)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        strip = Path(tmp) / "strip.mp4"
        run("ffmpeg", "-v", "error", "-y", "-i", a.src, "-vf",
            f"crop={p['width']}:{even(strip_h * px)}:0:{even(strip_top * px)}",
            "-c:v", "libx264", "-crf", "12", "-preset", "fast", "-pix_fmt", "yuv420p", "-an", strip)
        print(f"cutting out {p['nb_read_packets']} frames (strip y {strip_top}-{strip_top + strip_h}) ...", flush=True)
        remove_background(a.cli, strip, a.out)
    tag_cutout(a.out)

    tops, cxs = track_head(a.out, strip_top)
    jumps = np.where(np.abs(np.diff(tops)) > JUMP_PX)[0]
    print(f"head: top {tops.min():.0f}-{tops.max():.0f}, centre x {cxs.min():.0f}-{cxs.max():.0f}", flush=True)
    if len(jumps):
        print("head jumps: cut a panel beat at " + ", ".join(f"{(j + 1) / fps:.2f}s" for j in jumps[:20]), flush=True)
    if tops.min() < strip_top + 6:
        print("warning: the head touches the top of the strip on some frames, so its top may be cut off", flush=True)

    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps({
        "src": Path(a.src).as_posix(), "cut": Path(a.out).as_posix(), "fps": fps, "strip_top": strip_top, "strip_h": strip_h,
        "head_w": round(head_w, 1), **fit,
        "top": [round(float(v), 1) for v in tops], "cx": [round(float(v), 1) for v in cxs]}))
    print("panel:", a.json, flush=True)


if __name__ == "__main__":
    main()
