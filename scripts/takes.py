"""Best-take edit decision list for raw talking-head footage (retakes, restarts, long pauses).

You choose the takes (references/takes.md); this script makes the cuts clean:
  1. every take boundary is snapped into a real gap of the audio envelope (ASR times run ~0.1–0.3 s early and
     word ends swallow pauses, so cutting on ASR times clips words or leaves breaths);
  2. pauses inside a take are tightened to a breath (a little more air after a sentence end);
  3. cuts land on the source frame grid; words are remapped onto the new timeline.

usage:
  python takes.py --src "<video>" --words build/transcript.json --takes build/takes.json --out build [--show] [--dry]
        [--fix "Cloud=Claude,rules=rolls"] [--gate -40]

build/takes.json — in speaking order:
  [{"from": 24.40, "to": 31.52, "say": "My video started getting more views because ..."},
   {"from": 160.68, "to": 170.57, "exact_end": true, "say": "... motion effects"}]
  from / to   = ASR start of the first word and ASR end of the last word you keep
  exact_end   = cut exactly at "to" (use when a stop consonant's closure fools the gap finder: the
                re-transcription check showed a clipped or a doubled word). exact_start works the same way.
  keep_pauses = leave every pause inside this take untouched (a dramatic beat before a reveal)

writes <out>/edl.json  {fps, src, total, takes_src, take_joins_dst, segments[{src_start, src_end, dst_start, dur}]}
       <out>/words.json [{id, text, start, end, src_start, src_end}]   (kept words on the new timeline)
       <out>/env20.npy  (audio envelope, 20 ms hops, dB)
Then re-transcribe the cut voice (pipeline.md §2) and fix any clipped or doubled word before building anything.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows consoles / pipes default to cp1252

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--words", required=True)
ap.add_argument("--takes", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--gate", type=float, default=-40.0, help="dB below which a 20 ms hop counts as pause")
ap.add_argument("--pause-min", type=float, default=0.24, help="pauses longer than this are tightened")
ap.add_argument("--tail", type=float, default=0.10, help="air kept after speech inside a take")
ap.add_argument("--head", type=float, default=0.10, help="air kept before speech inside a take")
ap.add_argument("--fix", default="", help="ASR fixes 'wrong=right,...' applied to words.json")
ap.add_argument("--show", action="store_true", help="print the envelope around every take boundary")
ap.add_argument("--dry", action="store_true")
a = ap.parse_args()

HOP = 0.02
OUT = Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
SRC = str(Path(a.src).resolve())


def probe(entries, stream="v:0"):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", entries, "-of",
                           "default=nw=1:nk=1", SRC], capture_output=True, text=True).stdout.strip().splitlines()


num, den = probe("stream=r_frame_rate")[0].split("/")
FPS = round(float(num) / float(den), 3)
SRC_END = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", SRC],
                               capture_output=True, text=True).stdout.strip())

env_path = OUT / "env20.npy"
if env_path.exists() and env_path.stat().st_mtime > Path(SRC).stat().st_mtime:
    db = np.load(env_path)
else:
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    hop = int(HOP * 16000)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12))
    np.save(env_path, db)

raw = json.loads(Path(a.words).read_text(encoding="utf-8"))
WORDS = raw.get("words", raw) if isinstance(raw, dict) else raw
TAKES = json.loads(Path(a.takes).read_text(encoding="utf-8"))


def gaps(t0, t1, min_len=0.06):
    i0, i1 = max(0, int(round(t0 / HOP))), min(len(db), int(round(t1 / HOP)))
    out, run = [], None
    for i in range(i0, i1):
        q = db[i] < a.gate
        if q and run is None:
            run = i
        if (not q or i == i1 - 1) and run is not None:
            e = i if not q else i + 1
            if (e - run) * HOP >= min_len:
                out.append((run * HOP, e * HOP))
            run = None
    return out


def start_cut(t):
    g = [x for x in gaps(t - 0.6, t + 0.45) if x[1] <= t + 0.45]
    if not g:
        return t, "NO GAP — check this start"
    best = min(g, key=lambda x: abs(x[1] - (t + 0.12)))
    return max(best[0], best[1] - 0.08), f"gap {best[0]:.2f}-{best[1]:.2f}"


def end_cut(e):
    g = [x for x in gaps(e - 0.3, e + 0.7) if x[0] >= e - 0.3 - HOP]
    if not g:
        i = int(round(e / HOP))
        if 0 <= i < len(db) and db[i] < a.gate:          # "to" already sits in silence: find where that silence began
            while i > 0 and db[i - 1] < a.gate:
                i -= 1
            return i * HOP + 0.10, f"inside silence from {i * HOP:.2f}"
        return e, "NO GAP — check this end"
    g0, g1 = g[0]
    why = f"gap {g0:.2f}-{g1:.2f}"
    resumes = int(round(g1 / HOP)) < len(db) and db[int(round(g1 / HOP))] >= a.gate
    if g1 - g0 < 0.15 and resumes:
        why += (f"  ⚠ short gap ({g1 - g0:.2f}s) with sound right after: may be a stop consonant inside the last word "
                f"(the 'k'/'t' of 'effects', 'code') — if the re-read clips or loses it, move 'to' past the next real gap")
    return min(g1, g0 + 0.10), why


def ascii_env(t0, t1, mark):
    """one character per 20 ms: # loud, + speech, - soft, . breath, blank silence; ^ marks the cut, ' every 0.1 s"""
    i0, i1 = max(0, int(round(t0 / HOP))), min(len(db), int(round(t1 / HOP)))
    env = "".join("#" if v > -25 else "+" if v > -35 else "-" if v > -45 else "." if v > -55 else " " for v in db[i0:i1])
    ruler = "".join("^" if abs(i * HOP - mark) < HOP / 2 else ("'" if i % 5 == 0 else " ") for i in range(i0, i1))
    return f"{i0 * HOP:7.2f} [{env}] {i1 * HOP:.2f}\n{'':9}{ruler}"


takes = []
for tk in TAKES:
    s, why_s = (tk["from"], "exact") if tk.get("exact_start") else start_cut(tk["from"])
    e, why_e = (tk["to"], "exact") if tk.get("exact_end") else end_cut(tk["to"])
    takes.append((max(0.0, s), min(SRC_END, e), tk.get("say", ""), why_s, why_e))

sentence_ends = [w["end"] for w in WORDS if w["text"].rstrip().endswith((".", "?", "!"))]
keep = []
for (s, e, *_), tk in zip(takes, TAKES):
    cur = s
    for g0, g1 in ([] if tk.get("keep_pauses") else gaps(s + 0.05, e - 0.05, min_len=a.pause_min)):
        sent = any(abs(g0 - t) < 0.35 for t in sentence_ends)
        tail, head = (a.tail + 0.03, a.head + 0.02) if sent else (a.tail, a.head)
        x0, x1 = g0 + tail, g1 - head
        if x1 - x0 >= 2 / FPS:
            keep.append((cur, x0))
            cur = x1
    keep.append((cur, e))


def snap(t):
    return round(round(t * FPS) / FPS, 4)


segs, dst = [], 0.0
for k0, k1 in keep:
    k0, k1 = snap(k0), snap(k1)
    if k1 - k0 < 2 / FPS:
        continue
    segs.append({"src_start": k0, "src_end": k1, "dst_start": round(dst, 4), "dur": round(k1 - k0, 4)})
    dst += k1 - k0
total = round(dst, 4)


def remap(t):
    for sg in segs:
        if sg["src_start"] - 1e-6 <= t <= sg["src_end"] + 1e-6:
            return round(sg["dst_start"] + (t - sg["src_start"]), 3)
    return None


def near_dst(t):
    """nearest kept time for a source time that fell inside a removed pause"""
    best = min(segs, key=lambda sg: min(abs(t - sg["src_start"]), abs(t - sg["src_end"])))
    return round(best["dst_start"] + (0 if abs(t - best["src_start"]) < abs(t - best["src_end"]) else best["dur"]), 3)


fix = dict(p.split("=", 1) for p in a.fix.split(",") if "=" in p)
words = []
for i, w in enumerate(WORDS):
    host = next(((s, e) for s, e, *_ in takes if s - 0.15 <= w["start"] <= e and w["end"] <= e + 0.6), None)
    if not host:
        continue
    st = remap(max(w["start"], host[0])) or near_dst(w["start"])
    en = remap(min(w["end"], host[1])) or near_dst(w["end"])
    txt = w["text"]
    core = txt.strip(".,!?;:'\"")
    if core in fix:
        txt = txt.replace(core, fix[core])
    words.append({"id": f"w{i}", "text": txt, "start": st, "end": max(en, st + 0.04), "src_start": w["start"], "src_end": w["end"]})

joins = []
for s, *_ in takes[1:]:
    sg = min(segs, key=lambda q: abs(q["src_start"] - snap(s)))
    joins.append(sg["dst_start"])

for (s, e, say, why_s, why_e) in takes:
    print(f"{s:8.2f}-{e:8.2f}  [{why_s} | {why_e}]  {say[:64]}")
    if a.show:
        print("   start " + ascii_env(s - 0.6, s + 0.6, s).replace("\n", "\n         "))
        print("   end   " + ascii_env(e - 0.6, e + 0.6, e).replace("\n", "\n         "))
print(f"fps={FPS:g}  takes={len(takes)}  segments={len(segs)}  total={total:.2f}s  (source {SRC_END:.1f}s)")
print("take joins at dst:", ", ".join(f"{t:.2f}" for t in joins))
print("jump cuts (all) at dst:", ", ".join(f"{sg['dst_start']:.2f}" for sg in segs[1:]))
if not a.dry:
    json.dump({"fps": FPS, "src": SRC, "total": total, "inserts_dst": [], "takes_src": [[s, e] for s, e, *_ in takes],
               "take_joins_dst": joins, "segments": segs}, open(OUT / "edl.json", "w"), indent=1)
    json.dump(words, open(OUT / "words.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"wrote {OUT / 'edl.json'} and words.json ({len(words)} words)")
