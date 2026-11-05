"""Read a raw take the way an editor does: one line per ATTEMPT, so every retake sits on its own line with its times.

usage:
  python phrases.py build/transcript.json                  # attempts + retake hints
  python phrases.py build/transcript.json --gap 0.35       # also split at shorter pauses
  python phrases.py build/transcript.json --range 95-110   # every word with its time in a range (for takes.json)

An attempt ends at a sentence end (. ? !), at a pause longer than --gap, or where the speaker restarts (the next three
words repeat how the current attempt — or the previous one — began: "and this is how, | and this is how most of…").

Markers in front of each attempt:
  ↻n   opens like attempt n (same first three words): another try at the same line
  …    cut off: it doesn't reach a sentence end and the next attempt restarts it
  ★    suggested keeper: complete (ends a sentence), 5+ words, not retried in the next few attempts
  ✗    talking to yourself ("let's cancel that", "one more time") — never in the edit
Short complete attempts ("my video style.", "You don't know how.") are often the tail of the previous attempt or a
fragment: join them to the attempt before when that makes the full line, otherwise drop them.
The hints are a starting point: read everything, then pick the best complete read of every line (references/takes.md).
ASR times run ~0.1–0.3 s early; takes.py snaps cuts into the real gaps, so copy times as printed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")      # Windows consoles / pipes default to cp1252

ap = argparse.ArgumentParser()
ap.add_argument("words")
ap.add_argument("--gap", type=float, default=0.5, help="a pause longer than this (s) ends an attempt")
ap.add_argument("--range", default="", help="a-b: print every word with its time inside this source range")
ap.add_argument("--width", type=int, default=150, help="truncate long lines")
a = ap.parse_args()

raw = json.loads(Path(a.words).read_text(encoding="utf-8"))
W = raw.get("words", raw) if isinstance(raw, dict) else raw


def norm(t):
    return re.sub(r"[^a-z0-9']", "", t.lower())


if a.range:
    r0, r1 = (float(x) for x in a.range.split("-"))
    for w in W:
        if r0 <= w["start"] <= r1:
            print(f"{w['start']:8.2f} {w['end']:8.2f}  {w['text']}")
    raise SystemExit

toks = [norm(w["text"]) for w in W]
attempts, cur = [], []


def opening(ws, n=2):
    t = [norm(w["text"]) for w in ws if norm(w["text"])]
    return tuple(x[:-1] if len(x) > 3 and x.endswith("s") else x for x in t[:n])     # "videos" ~ "video"


META = re.compile(r"\b(cancel that|let me (start|try|do) (that|it|this) again|one more time|start (over|again)|"
                  r"from the top|let's (go|do it|try) again|take (two|three|\d))\b", re.I)


for i, w in enumerate(W):
    if cur:
        pause = w["start"] - cur[-1]["end"] > a.gap
        nxt = opening(W[i:i + 3], 3)
        restart = len(cur) >= 3 and len(nxt) == 3 and (nxt == opening(cur, 3) or (attempts and nxt == opening(attempts[-1], 3)))
        if pause or restart:
            attempts.append(cur)
            cur = []
    cur.append(w)
    if w["text"].rstrip().endswith((".", "?", "!")):
        attempts.append(cur)
        cur = []
if cur:
    attempts.append(cur)

rows = []
for k, ws in enumerate(attempts):
    rows.append({"n": k + 1, "ws": ws, "open": opening(ws, 3), "complete": ws[-1]["text"].rstrip().endswith((".", "?", "!"))})
for r in rows:
    r["retake_of"] = next((q["n"] for q in reversed(rows[max(0, r["n"] - 11):r["n"] - 1]) if q["open"] == r["open"] and r["open"]), None)
    nxt = rows[r["n"]] if r["n"] < len(rows) else None
    r["cut"] = (not r["complete"]) and nxt is not None and nxt["open"][:2] == r["open"][:2]
    later = [q for q in rows[r["n"]:r["n"] + 6] if q["open"] == r["open"] and q["open"]]
    text = " ".join(w["text"] for w in r["ws"])
    r["meta"] = bool(META.search(text)) and len(r["ws"]) <= 8
    r["keep"] = r["complete"] and not later and len(r["ws"]) >= 5 and not r["meta"]

for r in rows:
    ws = r["ws"]
    tag = (f"↻{r['retake_of']:<3}" if r["retake_of"] else "    ") + ("★" if r["keep"] else "…" if r["cut"] else "✗" if r["meta"] else " ")
    text = " ".join(w["text"] for w in ws)
    line = f"#{r['n']:<3}{tag} {ws[0]['start']:7.2f}-{ws[-1]['end']:7.2f}  {text}"
    print(line if len(line) <= a.width else line[:a.width - 1] + "…")
print(f"\n{len(rows)} attempts, {sum(r['keep'] for r in rows)} suggested keepers (★). Pick the best complete read of every "
      f"line, write build/takes.json (references/takes.md), run takes.py.")
