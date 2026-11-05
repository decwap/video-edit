"""Cut a segment of the A-roll and remove its background -> transparent WebM for a DEPTH beat.

usage: python make_matte.py --src assets/aroll_wide.mp4 --start 11.84 --dur 2.16 --out assets/depth_a.webm
       [--cli hyperframes@0.8.106]   (pin the CLI the project was initialised with)

The matte starts at --start on the tightened timeline, so in a scene use data-media-start="<global - start>".
Cover consecutive DEPTH beats with one matte (it is the slow step: ~1.1 s per frame on CPU).
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--start", type=float, required=True)
ap.add_argument("--dur", type=float, required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--cli", default="hyperframes@0.8.106")
a = ap.parse_args()

tmp = Path(tempfile.mkdtemp()) / "seg.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-i", a.src, "-t", str(a.dur), "-c:v", "libx264",
                "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", "-an", str(tmp)], check=True)
# No shell=True: on Windows it exited 0 without writing anything. Resolve npx(.cmd) explicitly instead.
npx = shutil.which("npx") or "npx"
subprocess.run([npx, "--yes", a.cli, "remove-background", str(tmp), "-o", str(Path(a.out).resolve()), "--quality", "best"],
               check=True)
if not Path(a.out).exists() or Path(a.out).stat().st_size == 0:
    sys.exit(f"no matte written to {a.out}")
print("matte:", a.out)
