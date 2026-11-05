"""Cut B-roll moments out of the creator's own videos (earlier edits, product demos, screen recordings) into short
clips for phone / frame / full-bleed props: assets/bv/<name>.mp4 at the reel's fps.

usage: python prep_broll.py --fps 30 [--w 540] name=path@start+dur [name2=path2@start+dur ...]
  e.g. python prep_broll.py --fps 30 old-a="D:/Videos/My Old Reel (Edited).mp4"@3.0+4.0
--w 540 suits phone mockups (~300-400 px wide on the canvas); use --w 1080 for a full-bleed beat.
Clips are cut without audio. Make each clip a little longer than its beat (+0.5 s) so transitions have frames.
Look at a contact sheet first and pick bright, readable moments, never a fade or a dark stretch.
"""
import argparse
import re
import subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("clips", nargs="+")
ap.add_argument("--fps", default="30")
ap.add_argument("--w", type=int, default=540)
ap.add_argument("--out", default="assets/bv")
a = ap.parse_args()
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
for spec in a.clips:
    m = re.match(r"^([\w.-]+)=(.+)@([\d.]+)\+([\d.]+)$", spec)
    if not m:
        raise SystemExit(f"bad clip spec {spec!r}: use name=path@start+dur")
    name, path, ss, dur = m.group(1), m.group(2).strip('"'), m.group(3), m.group(4)
    h = a.w * 16 // 9
    vf = f"fps={a.fps},scale={a.w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={a.w}:{h},setsar=1"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", ss, "-t", dur, "-i", path, "-vf", vf, "-an", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-colorspace", "bt709", "-g", str(a.fps), "-movflags", "+faststart", str(OUT / f"{name}.mp4")], check=True)
    print(f"{name:14s} <- {Path(path).name} {ss}+{dur}")
