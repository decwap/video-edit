"""Voice sync check: cross-correlate the render's audio with assets/voice.wav in five windows (expect +0.0 ms).

usage: python sync_check.py renders/<file>.mp4 [--voice assets/voice.wav]
"""
import argparse
import subprocess

import numpy as np

SR = 8000
ap = argparse.ArgumentParser()
ap.add_argument("render")
ap.add_argument("--voice", default="assets/voice.wav")
a = ap.parse_args()


def pcm(path, t0, dur):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(dur), "-i", path, "-ac", "1", "-ar", str(SR),
                        "-f", "s16le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.int16).astype(float)


dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", a.voice],
                           capture_output=True, text=True).stdout.strip())
worst = 0.0
for k in range(5):
    t0 = round(1 + k * max(0.0, dur - 8) / 4, 1)
    x, y = pcm(a.render, t0, 6.0), pcm(a.voice, t0, 6.0)
    n = min(len(x), len(y))
    if n < SR:
        print(f"window {t0:6.1f}s: not enough audio")
        continue
    x, y = x[:n] - x[:n].mean(), y[:n] - y[:n].mean()
    lag = int(0.2 * SR)
    best = max(range(-lag, lag + 1), key=lambda j: np.dot(x[max(0, j):n + min(0, j)], y[max(0, -j):n - max(0, j)]))
    worst = max(worst, abs(best * 1000 / SR))
    print(f"window {t0:6.1f}s: offset {best * 1000 / SR:+.1f} ms")
print("in sync" if worst <= 1.0 else f"OUT OF SYNC by up to {worst:.0f} ms")
