"""A-roll intermediates on the tightened timeline, from build/edl.json — colours left exactly as shot.

  assets/aroll_wide.mp4   1080x1920, the full frame (SPLIT face card, DEPTH, wide beats)
  assets/aroll_tight.mp4  1080x1920 punch-in crop (default 1.4x) centred on the face
  assets/voice.wav        48 kHz stereo, micro-faded joins, highpass + light compression, -15 LUFS

Phones record HDR (HLG "arib-std-b67" on iPhone, PQ "smpte2084" on some Androids). Played as normal video that looks
washed out and grey, so HDR is converted to standard BT.709 (zscale + mobius tone-map) — a technical fix, not a look.
SDR footage passes through untouched. No grade, no vignette.

usage:
  python aroll.py --edl build/edl.json --assets assets --face        # measure the face first (prints the numbers)
  python aroll.py --edl build/edl.json --assets assets [--steps video,voice] [--tight 1.4 --tight-top 0.19 --tight-cx 0.5]
                  [--size 1440x2560]   # 2K / 4K delivery (pipeline.md §7); default 1080x1920
--face finds the face with OpenCV's Haar cascade when available (OpenCV 4.x) and always writes build/face/grid.jpg, four
frames across the edit with labelled y lines: read the head top, eye line and face-centre x there and pass them as
--head-top / --eyes / --face-x — the script prints and uses --tight-top / --tight-cx for the punch crop and the
face_shift for the SPLIT face card (video_kit.configure).
Variable-frame-rate phone video is conformed to a constant fps first, so frame counts match the voice exactly.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ap = argparse.ArgumentParser()
ap.add_argument("--edl", required=True)
ap.add_argument("--assets", required=True)
ap.add_argument("--steps", default="video,voice")
ap.add_argument("--face", action="store_true", help="measure the face and print crop / face_shift suggestions, then stop")
ap.add_argument("--tight", type=float, default=1.4)
ap.add_argument("--size", default="1080x1920", help="intermediate size: 1080x1920 (HD), 1440x2560 (2K) or 2160x3840 (4K)")
ap.add_argument("--tight-top", type=float, default=None, help="crop top as a fraction of height (default: from --face, else 0.12)")
ap.add_argument("--tight-cx", type=float, default=None, help="crop centre as a fraction of width (default: from --face, else 0.5)")
ap.add_argument("--head-top", type=float, default=None, help="measured head top (px on 1080x1920) -> prints crop + face_shift")
ap.add_argument("--eyes", type=float, default=None, help="measured eye line (px)")
ap.add_argument("--face-x", type=float, default=None, help="measured face centre x (px)")
a = ap.parse_args()

edl = json.loads(Path(a.edl).read_text())
SRC, FPS, segs = edl["src"], edl["fps"], edl["segments"]
ASSETS = Path(a.assets)
ASSETS.mkdir(parents=True, exist_ok=True)
fps_s = f"{FPS:g}"
X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv", "-g", fps_s, "-movflags", "+faststart", "-r", fps_s]


def run(cmd):
    print(">", " ".join(str(c) for c in cmd)[:220], flush=True)
    subprocess.run(cmd, check=True)


def probe():
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,color_transfer:stream_side_data=rotation", "-of", "json", SRC],
                       capture_output=True, text=True)
    st = json.loads(r.stdout)["streams"][0]
    return int(st["width"]), int(st["height"]), st.get("color_transfer", "")


W, H, TRC = probe()
HDR = TRC in ("arib-std-b67", "smpte2084")
TONEMAP = (f"zscale=tin={TRC}:pin=bt2020:min=bt2020nc:t=linear:npl={203 if TRC == 'arib-std-b67' else 100},format=gbrpf32le,"
           "zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,") if HDR else ""
if "video" in a.steps or a.face:
    print(f"source {W}x{H}  transfer={TRC or 'unknown'}  -> {'HDR: converting to SDR BT.709' if HDR else 'SDR: colours untouched'}")


def even(v):
    return int(v) // 2 * 2


if abs(W / H - 9 / 16) > 0.01:            # not 9:16 -> centre-crop to 9:16 first
    BW = even(min(W, H * 9 / 16))
    BH = even(BW * 16 / 9)
    BASE = f"crop={BW}:{BH}:{even((W - BW) / 2)}:{even((H - BH) / 2)},"
else:
    BW, BH, BASE = W, H, ""


def select_expr():
    eps = 0.001
    return "+".join(f"between(t,{s['src_start'] - eps:.4f},{s['src_end'] - eps - 1 / FPS / 2:.4f})" for s in segs)


def sample_times(n):
    total = sum(s["dur"] for s in segs)
    times, acc = [], 0.0
    for s in segs:                           # n evenly spread source times inside kept segments
        for k in range(n):
            t_dst = (k + 0.5) * total / n
            if acc <= t_dst < acc + s["dur"]:
                times.append(s["src_start"] + t_dst - acc)
        acc += s["dur"]
    return times


def suggest(head_top, eyes, face_x):
    cx = face_x / 1080
    tight_top = max(0.0, (eyes - 760 / a.tight) / 1920)
    face_shift = int(round(head_top + 1000 - 1075))
    print(f"head top {head_top:.0f}px, eyes {eyes:.0f}px, face centre x {face_x:.0f}px (on the 1080x1920 frame)")
    print(f"suggested:  --tight-cx {cx:.3f} --tight-top {tight_top:.3f}     video_kit.configure(face_shift={face_shift})")
    return cx, tight_top


def measure_face():
    """OpenCV 4.x: Haar cascade over ~24 frames. Otherwise (OpenCV 5 dropped it) write a labelled grid sheet to read by eye."""
    tmp = ASSETS.parent / "build" / "face"
    tmp.mkdir(parents=True, exist_ok=True)
    try:
        import cv2
        import numpy as np
        det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    except Exception:
        det = None
    if det is not None:
        boxes, times = [], sample_times(24)
        for i, t in enumerate(times):
            f = tmp / f"f{i:02d}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", SRC, "-frames:v", "1", "-vf",
                            f"{BASE}scale=540:960,{TONEMAP}format=gray", str(f)], check=True)
            g = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            found = det.detectMultiScale(g, 1.1, 6, minSize=(60, 60))
            if len(found):
                x, y, w, h = max(found, key=lambda b: b[2] * b[3])
                boxes.append((x * 2, y * 2, w * 2, h * 2))
        if boxes:
            x, y, w, h = (float(np.median([b[i] for b in boxes])) for i in range(4))
            print(f"face found in {len(boxes)}/{len(times)} frames")
            suggest(y - 0.35 * h, y + 0.4 * h, x + w / 2)
            print("If the speaker moved during the recording, also read the grid sheet below by eye for each part.")
    # labelled grid sheet: 4 frames across the edit, lines every 96 px with their y value
    times = sample_times(4)
    labels = "".join(f",drawtext=fontfile='{FONT}':text='{y}':x=4:y={y - 22}:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6"
                     for y in range(192, 1920, 192))
    for i, t in enumerate(times):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", SRC, "-frames:v", "1", "-vf",
                        f"{BASE}scale=1080:1920,{TONEMAP}drawgrid=w=108:h=96:t=1:c=yellow@0.35,drawgrid=w=1080:h=192:t=3:c=yellow@0.8{labels}",
                        str(tmp / f"g{i}.png")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + sum((["-i", str(tmp / f"g{i}.png")] for i in range(len(times))), []) +
                   ["-filter_complex", "".join(f"[{i}]" for i in range(len(times))) + f"hstack={len(times)},scale=1800:-2",
                    str(tmp / "grid.jpg")], check=True)
    print(f"grid sheet: {tmp / 'grid.jpg'}  (frames at src {', '.join(f'{t:.1f}' for t in times)} s; thick lines every 192 px, labelled)")
    print("Read head top, eye line and face-centre x (1080x1920 px) on it, then: aroll.py ... --head-top Y --eyes Y --face-x X")


FONT = {"nt": r"C\:/Windows/Fonts/arialbd.ttf", "posix": "/System/Library/Fonts/Supplemental/Arial Bold.ttf"}["nt" if __import__("os").name == "nt" else "posix"]
if __import__("sys").platform.startswith("linux"):
    FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def video(cx, top):
    cw, ch = even(BW / a.tight), even(BH / a.tight)
    x0 = even(min(max(0, BW * cx - cw / 2), BW - cw))
    y0 = even(min(BH - ch, BH * top))
    ow, oh = (int(v) for v in a.size.lower().split("x"))
    if ow > BW:
        print(f"note: --size {a.size} is larger than the source ({BW}x{BH}) — the footage is upscaled (no new detail)")
    fc = (f"[0:v]fps={fps_s},select='{select_expr()}',setpts=N/{fps_s}/TB,{TONEMAP}{BASE}split=2[w][t];"
          f"[w]scale={ow}:{oh}:flags=lanczos,setsar=1[wide];"
          f"[t]crop={cw}:{ch}:{x0}:{y0},scale={ow}:{oh}:flags=lanczos,setsar=1[tight]")
    run(["ffmpeg", "-v", "error", "-stats", "-y", "-i", SRC, "-filter_complex", fc,
         "-map", "[wide]", *X264, "-an", str(ASSETS / "aroll_wide.mp4"),
         "-map", "[tight]", *X264, "-an", str(ASSETS / "aroll_tight.mp4")])


def voice():
    n = len(segs)
    parts = [f"[0:a]asplit={n}" + "".join(f"[s{i}]" for i in range(n)) + ";"]
    for i, s in enumerate(segs):
        d = s["src_end"] - s["src_start"]
        fi = "" if i == 0 else "afade=t=in:st=0:d=0.008,"
        fo = "" if i == n - 1 else f"afade=t=out:st={d - 0.008:.4f}:d=0.008,"
        parts.append(f"[s{i}]atrim={s['src_start']}:{s['src_end']},asetpts=PTS-STARTPTS,{fi}{fo}anull[a{i}];")
    parts.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[cat];")
    chain = "highpass=f=75,lowpass=f=16000,acompressor=threshold=-22dB:ratio=2.4:attack=6:release=140:makeup=1.5"
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", SRC, "-filter_complex",
                           "".join(parts) + f"[cat]{chain},loudnorm=I=-15:LRA=8:TP=-1.5:print_format=json[out]",
                           "-map", "[out]", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", meas, re.S).group(0))
    ln = (f"loudnorm=I=-15:LRA=8:TP=-1.5:measured_I={m['input_i']}:measured_LRA={m['input_lra']}:"
          f"measured_TP={m['input_tp']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", "".join(parts) + f"[cat]{chain},{ln},aresample=48000[out]",
         "-map", "[out]", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(ASSETS / "voice.wav")])


if a.face:
    measure_face()
    raise SystemExit
if a.head_top is not None and a.eyes is not None and a.face_x is not None:
    sx, st = suggest(a.head_top, a.eyes, a.face_x)
    a.tight_cx = a.tight_cx if a.tight_cx is not None else sx
    a.tight_top = a.tight_top if a.tight_top is not None else st
cx = a.tight_cx if a.tight_cx is not None else 0.5
top = a.tight_top if a.tight_top is not None else 0.12
for step in a.steps.split(","):
    step = step.strip()
    if step == "video":
        video(cx, top)
    elif step == "voice":
        voice()
checks = []
if "video" in a.steps:
    checks.append(f"frames of aroll_wide.mp4 == {round(edl['total'] * FPS)}")
if "voice" in a.steps:
    checks.append(f"voice.wav lasts {edl['total']:.2f} s")
print("done - check: " + ", ".join(checks))
