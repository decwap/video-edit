"""Raw -> edited proof: thumbnails of the raw recording every N seconds as ONE sprite image, plus which ones fall
inside a kept take. Feed it to video_kit.film_strip (repeated takes collapse, best takes gather, a clock counts the
raw length down to the edit length).

usage: python strip.py --src "<video>" --edl build/edl.json --out assets/img/strip [--every 10] [--start 5]
writes <out>/sprite.jpg (cells of 192x342, side by side) and <out>/strip.json {cells, every, start, kept[], raw_s, edit_s}
One sprite instead of dozens of <img> files: the renderer waits for every image at startup, and a long strip of
separate files timed out once (a kept thumbnail rendered black).
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--edl", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--every", type=float, default=10.0)
ap.add_argument("--start", type=float, default=5.0)
a = ap.parse_args()

out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
edl = json.loads(Path(a.edl).read_text())
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", a.src],
                           capture_output=True, text=True).stdout.strip())
trc = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer", "-of",
                      "default=nw=1:nk=1", a.src], capture_output=True, text=True).stdout.strip()
tm = (f"zscale=tin={trc}:pin=bt2020:min=bt2020nc:t=linear:npl={203 if trc == 'arib-std-b67' else 100},format=gbrpf32le,"
      "zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,") if trc in ("arib-std-b67", "smpte2084") else ""
times = []
t = a.start
while t < dur - 0.5:
    times.append(round(t, 2))
    t += a.every
tmp = Path(tempfile.mkdtemp())
for i, t in enumerate(times):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", a.src, "-frames:v", "1", "-vf",
                    f"scale=192:342:force_original_aspect_ratio=increase,crop=192:342,{tm}format=yuvj420p", "-q:v", "3",
                    str(tmp / f"s{i:03d}.jpg")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(tmp / "s%03d.jpg"), "-vf", f"tile={len(times)}x1",
                "-frames:v", "1", "-q:v", "3", str(out / "sprite.jpg")], check=True)
kept = [any(s <= t <= e for s, e in edl["takes_src"]) for t in times]
json.dump({"cells": len(times), "every": a.every, "start": a.start, "times": times, "kept": kept, "raw_s": round(dur, 2),
           "edit_s": edl["total"]}, open(out / "strip.json", "w"), indent=1)
print(f"{len(times)} cells, {sum(kept)} inside kept takes -> {out / 'sprite.jpg'}  (raw {dur:.0f}s -> edit {edl['total']:.0f}s)")
