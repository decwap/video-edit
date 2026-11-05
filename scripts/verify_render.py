"""Verify a rendered MP4: format, duration, loudness, and a beat-midpoint contact sheet.

usage: python verify_render.py <video.mp4> [--sheet out.jpg] [--times 1.9,3.9,...] [--normalize out.mp4]
  --times      comma-separated seconds for the sheet (default: 36 evenly spaced frames)
  --normalize  re-encode ONLY the audio to -14 LUFS / -1 dBTP (video stream copied)
"""
import json, re, subprocess, sys
from pathlib import Path

TIMES = None

def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def probe(p):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of", "json", p])
    return json.loads(r.stdout)

def loudness(p):
    err = sh(["ffmpeg", "-hide_banner", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    summ = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", summ); lra = re.search(r"LRA:\s+([\d.]+) LU", summ)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
    return (float(i.group(1)) if i else None, float(lra.group(1)) if lra else None, float(tp.group(1)) if tp else None)

FONT_CANDIDATES = ["C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                   "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]


def label_font():
    """drawtext needs an explicit fontfile (fontconfig crashes on Windows); escape the drive colon for the filter."""
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            return f.replace(":", "\\:")
    return None


def sheet(p, out):
    times = TIMES or [round((k + 0.5) * float(probe(p)['format']['duration']) / 36, 2) for k in range(36)]
    tmp = Path(out).with_suffix("")
    tmp.mkdir(exist_ok=True)
    font = label_font()
    for k, t in enumerate(times):
        label = (f",drawtext=fontfile='{font}':text='{t:.2f}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6"
                 if font else "")
        sh(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", p, "-frames:v", "1", "-vf", f"scale=216:384{label}",
            str(tmp / f"{k:02d}.png")])
    sh(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(tmp / "%02d.png"), "-vf", "tile=9x4:margin=4:padding=4:color=0x2a2622",
        "-frames:v", "1", "-q:v", "3", out])

def normalize(p, out):
    first = sh(["ffmpeg", "-hide_banner", "-i", p, "-af", "loudnorm=I=-14:TP=-1:LRA=9:print_format=json", "-f", "null", "-"]).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", first, re.S).group(0))
    ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={m['input_i']}:measured_LRA={m['input_lra']}:measured_TP={m['input_tp']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    r = sh(["ffmpeg", "-v", "error", "-y", "-i", p, "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-af", f"{ln},aresample=48000",
            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out])
    if r.returncode:
        print(r.stderr)

if __name__ == "__main__":
    vid = sys.argv[1]
    if "--times" in sys.argv:
        TIMES = [float(x) for x in sys.argv[sys.argv.index("--times") + 1].split(",")]
    info = probe(vid)
    print(json.dumps(info, indent=1))
    print("loudness I/LRA/TP:", loudness(vid))
    if "--sheet" in sys.argv:
        sheet(vid, sys.argv[sys.argv.index("--sheet") + 1]); print("sheet written")
    if "--normalize" in sys.argv:
        out = sys.argv[sys.argv.index("--normalize") + 1]
        normalize(vid, out)
        print("normalized:", out, loudness(out))
