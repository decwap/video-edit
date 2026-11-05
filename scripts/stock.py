"""Stock B-roll from Pexels (Pexels License: free to use, no attribution required). Run from the reel project folder
(or pass --project <P>):

  python <SK>/scripts/stock.py search "<query>" [--orient portrait|landscape|any] [--n 18] [--tag <name>]
      -> build/stock/<tag>.json + build/stock/<tag>.jpg (labelled contact sheet of the results: look at it, pick ids)
  python <SK>/scripts/stock.py get <id> [<id> ...] [--h 1920]
      -> assets/broll/px-<id>.mp4 (the 1080x1920 rendition when there is one) + assets/broll/CREDITS.md

Search pages are read like a browser would (no API key needed); files come from the public videos.pexels.com CDN.
Search one idea per spoken line ("small business owner", "contactless payment"); vertical results suit 9:16 reels.
"""
import argparse
import io
import json
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = OUT = BROLL = None


def set_project(path):
    global ROOT, OUT, BROLL
    ROOT = Path(path).resolve()
    OUT = ROOT / "build" / "stock"
    BROLL = ROOT / "assets" / "broll"


set_project(".")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"


def fetch(url, timeout=60, tries=3):
    """curl, not urllib: the search pages answer curl's TLS handshake but refuse Python's (403). Rapid searches are
    sometimes refused (curl 22), so retry after a pause."""
    for k in range(tries):
        r = subprocess.run(["curl", "-s", "-f", "-L", "--max-time", str(timeout), "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", url],
                           capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(6 * (k + 1))
    raise RuntimeError(f"curl {r.returncode} for {url}")


def items_from(html):
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    found, seen = [], set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "video" and isinstance(o.get("attributes"), dict):
                a = o["attributes"]
                if a.get("id") not in seen and a.get("video"):
                    seen.add(a.get("id"))
                    found.append(a)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    if m:
        walk(json.loads(m.group(1)))
    return found


def slim(a):
    v = a["video"]
    files = sorted(({"w": f["width"], "h": f["height"], "fps": f.get("fps"), "link": f["link"]}
                    for f in v.get("video_files", []) if f.get("link")), key=lambda f: f["w"] * f["h"])
    return {"id": a["id"], "title": a.get("title") or a.get("slug"), "desc": a.get("description") or "",
            "w": a.get("width"), "h": a.get("height"), "dur": a.get("duration"), "fps": a.get("fps"),
            "thumb": v["thumbnail"]["medium"], "files": files,
            "author": " ".join(x for x in [a.get("user", {}).get("first_name"), a.get("user", {}).get("last_name")] if x),
            "page": f"https://www.pexels.com/video/{a.get('slug', '')}-{a['id']}/"}


def font(sz):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(res, path, cols=6, tw=240):
    th = round(tw * 16 / 9)
    rows = (len(res) + cols - 1) // cols
    out = Image.new("RGB", (cols * tw, rows * (th + 46)), (24, 22, 20))
    d = ImageDraw.Draw(out)
    f1, f2 = font(17), font(13)
    for i, r in enumerate(res):
        x, y = (i % cols) * tw, (i // cols) * (th + 46)
        try:
            im = Image.open(io.BytesIO(fetch(r["thumb"]))).convert("RGB")
            s = max(tw / im.width, th / im.height)
            im = im.resize((round(im.width * s), round(im.height * s)))
            im = im.crop(((im.width - tw) // 2, (im.height - th) // 2, (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))
            out.paste(im, (x, y))
        except Exception as e:  # noqa: BLE001
            d.text((x + 8, y + 8), f"thumb fail {e}", fill=(255, 80, 80), font=f2)
        d.rectangle((x, y, x + tw - 1, y + 24), fill=(0, 0, 0))
        d.text((x + 6, y + 3), f"{r['id']}  {r['dur']}s  {r['w']}x{r['h']}", fill=(255, 230, 0), font=f1)
        d.text((x + 6, y + th + 4), (r["title"] or "")[:34], fill=(235, 230, 220), font=f2)
        d.text((x + 6, y + th + 22), (r["desc"] or "")[:36], fill=(170, 165, 155), font=f2)
    out.save(path, quality=86)


def search(q, orient, n, tag):
    OUT.mkdir(parents=True, exist_ok=True)
    url = f"https://www.pexels.com/search/videos/{urllib.parse.quote(q)}/"
    if orient != "any":
        url += f"?orientation={orient}"
    html = fetch(url).decode("utf-8", "ignore")
    res = [slim(a) for a in items_from(html)][:n]
    tag = tag or re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
    (OUT / f"{tag}.json").write_text(json.dumps({"q": q, "orient": orient, "results": res}, indent=1), encoding="utf-8")
    sheet(res, OUT / f"{tag}.jpg")
    print(f"{tag}: {len(res)} results -> build/stock/{tag}.jpg")
    for r in res:
        print(f"  {r['id']:>10} {r['dur']:>3}s {r['w']}x{r['h']}  {r['title'][:60]}")


def lookup(vid):
    for p in OUT.glob("*.json"):
        for r in json.loads(p.read_text(encoding="utf-8"))["results"]:
            if str(r["id"]) == str(vid):
                return r
    return None


def get(ids, h):
    BROLL.mkdir(parents=True, exist_ok=True)
    credits = BROLL / "CREDITS.md"
    lines = credits.read_text(encoding="utf-8").splitlines() if credits.exists() else ["# B-roll credits (Pexels License)", ""]
    for vid in ids:
        r = lookup(vid)
        if not r:
            print("not in any search result:", vid)
            continue
        files = r["files"]
        portrait = (r["h"] or 0) >= (r["w"] or 0)
        want = (lambda f: f["h"] == h) if portrait else (lambda f: f["w"] == h)
        pick = next((f for f in files if want(f)), None) or files[-1]
        out = BROLL / f"px-{vid}.mp4"
        if not out.exists():
            out.write_bytes(fetch(pick["link"], timeout=300))
            time.sleep(0.5)
        print(f"px-{vid}.mp4  {pick['w']}x{pick['h']}  {out.stat().st_size / 1e6:.1f} MB  {r['title']}")
        line = f"- px-{vid}.mp4 — \"{r['title']}\" by {r['author']} — {r['page']}"
        if line not in lines:
            lines.append(line)
    credits.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["search", "get"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--orient", default="portrait")
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--tag")
    ap.add_argument("--h", type=int, default=1920)
    ap.add_argument("--project", default=".", help="reel project folder (default: current directory)")
    a = ap.parse_args()
    set_project(a.project)
    if a.cmd == "search":
        search(" ".join(a.args), a.orient, a.n, a.tag)
    else:
        get(a.args, a.h)
    sys.stdout.flush()
