"""Stock B-roll through the official Pexels API (Pexels License: free to use, no attribution required, but it's appreciated
and CREDITS.md keeps it). Run from the reel project folder (or pass --project <P>):

  python <SK>/scripts/stock.py search "<query>" [--orient portrait|landscape|square|any] [--n 18] [--tag <name>]
      -> build/stock/<tag>.json + build/stock/<tag>.jpg (labelled contact sheet of the results: look at it, pick ids)
  python <SK>/scripts/stock.py get <id> [<id> ...] [--h 1920]
      -> assets/broll/px-<id>.mp4 (the 1080x1920 rendition when there is one) + assets/broll/CREDITS.md

`search` needs a free API key in the PEXELS_API_KEY environment variable: https://www.pexels.com/api/ . `get` reads the saved
search results, so it makes no API call. The default limit is 200 requests an hour and 20,000 a month; each search is one.
Search one idea per spoken line ("small business owner", "contactless payment"); vertical results suit 9:16 reels.
"""
import argparse
import io
import json
import os
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
API = "https://api.pexels.com/v1/videos"
UA = "video-edit-skill (+https://github.com/decwap/video-edit)"
API_MAX_PER_PAGE = 80


def fetch(url, timeout=60, tries=3):
    """A public file (thumbnail or video) from a link the API returned. The API key is never sent here."""
    for k in range(tries):
        r = subprocess.run(["curl", "-s", "-f", "-L", "--max-time", str(timeout), "-A", UA, url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        time.sleep(6 * (k + 1))
    raise RuntimeError(f"curl {r.returncode} for {url}")


def api_key():
    key = os.environ.get("PEXELS_API_KEY", "").strip()
    if not key:
        sys.exit("PEXELS_API_KEY is not set, so stock search can't run. Get a free key at https://www.pexels.com/api/ and set it "
                 "in that environment variable, then restart Claude Code. Everything except stock search works without it.")
    if re.search(r'[\s"\\\x00-\x1f]', key):
        sys.exit("PEXELS_API_KEY contains spaces, quotes or other characters a key can't have. Copy it again from https://www.pexels.com/api/ .")
    return key


def api_get(path, params, tries=3):
    """One API request. The key reaches curl on stdin, which keeps it out of the process list, and redirects aren't followed,
    so it only ever goes to the API. Only server and network failures are retried: repeating a refused request can't help."""
    config = f'header = "Authorization: {api_key()}"\n'.encode()
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    problem = None
    for k in range(tries):
        if k:
            time.sleep(6 * k)
        r = subprocess.run(["curl", "-s", "--max-time", "60", "-A", UA, "-K", "-", "-w", "\n%{http_code}", url], input=config, capture_output=True)
        body, _, code = r.stdout.rpartition(b"\n")
        code = code.decode("ascii", "ignore").strip()
        if r.returncode:
            problem = f"curl error {r.returncode}"
        elif code == "200":
            return json.loads(body)
        elif code in ("401", "403"):
            sys.exit(f"Pexels refused PEXELS_API_KEY (http {code}). Check the key at https://www.pexels.com/api/ .")
        elif code == "429":
            sys.exit("Pexels rate limit reached (by default 200 requests an hour, 20,000 a month). Wait, then search again.")
        elif code.startswith("5"):
            problem = f"http {code}"
        else:
            sys.exit(f"Unexpected answer from the Pexels API: http {code}.")
    sys.exit(f"Could not get an answer from the Pexels API ({problem}). Try again later.")


def title_from(page, vid):
    """The API has no title field, but Pexels puts one in the page address: .../video/a-man-typing-on-a-laptop-123/"""
    slug = (page or "").rstrip("/").rsplit("/", 1)[-1]
    return re.sub(rf"(^|-){vid}$", "", slug).replace("-", " ").strip() or f"video {vid}"


def slim(v):
    files = sorted(({"w": f["width"], "h": f["height"], "fps": f.get("fps"), "link": f["link"]}
                    for f in v.get("video_files", [])
                    if f.get("link") and f.get("width") and f.get("height") and f.get("quality") != "hls" and f.get("file_type") == "video/mp4"),
                   key=lambda f: f["w"] * f["h"])
    return {"id": v["id"], "title": title_from(v.get("url"), v["id"]), "w": v.get("width"), "h": v.get("height"),
            "dur": v.get("duration"), "thumb": v.get("image"), "files": files,
            "author": (v.get("user") or {}).get("name") or "unknown", "page": v.get("url")}


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
        d.text((x + 6, y + th + 22), r["author"][:36], fill=(170, 165, 155), font=f2)
    out.save(path, quality=86)


def search(q, orient, n, tag):
    OUT.mkdir(parents=True, exist_ok=True)
    params = {"query": q, "per_page": min(n, API_MAX_PER_PAGE)}
    if orient != "any":
        params["orientation"] = orient
    videos = api_get("search", params)["videos"]
    res = [x for x in map(slim, videos) if x["files"]][:n]
    tag = tag or re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
    (OUT / f"{tag}.json").write_text(json.dumps({"q": q, "orient": orient, "results": res}, indent=1), encoding="utf-8")
    if not res:
        print(f"{tag}: no results for {q!r}. Try a broader search or another orientation.")
        return
    sheet(res, OUT / f"{tag}.jpg")
    print(f"{tag}: {len(res)} results -> build/stock/{tag}.jpg   (videos provided by Pexels: https://www.pexels.com)")
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
    lines = credits.read_text(encoding="utf-8").splitlines() if credits.exists() else ["# B-roll credits (videos provided by Pexels, https://www.pexels.com)", ""]
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
        line = f"- px-{vid}.mp4 — \"{r['title']}\" by {r['author']} on Pexels — {r['page']}"
        if line not in lines:
            lines.append(line)
    credits.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["search", "get"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--orient", default="portrait", choices=["portrait", "landscape", "square", "any"])
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
