#!/usr/bin/env python3
"""styles — one finished edit in every style, side by side, so the creator picks the look before anything renders.

    python styles.py build  <project> [--styles paper,glow]   # styles/<id>/ for every style + picker.html
    python styles.py serve  <project> [--port 8770]           # the Style Picker: every style playing live, in sync
    python styles.py pick   <project> [<id>]                  # record the pick (no id: print the current pick)
    python styles.py check  <project> [--styles paper,glow]   # hyperframes lint + check in every style folder
    python styles.py snap   <project> [--styles] [--at 3,9.5] # snapshots of every style -> styles/<id>/snapshots/
    python styles.py sheet  <project> [--styles] [--at 3,9.5] # every style at the same moments -> styles/sheet.jpg
    python styles.py list                                      # the styles, one line each

Run `build` after `python build/scenes.py` has written the edit (compositions/*.html + index.html, the Warm Paper look).
A style changes the look only: the ground, colours, type, cards, captions and texture. The cut, the captions' words and
timing, the B-roll, the face panel, the motion and the sound stay exactly as built, so every style tells the same edit.

How a style is applied, on a copy of every composition:
  colours  every warm neutral of the kit (paper, ink, greys, borders) moves onto the style's ground and ink with the same
           contrast it had on paper, so text that passed the WCAG check still passes; the teal accent family becomes the
           style's accent; warm shadows take the style's shadow colour. Other colours (a green gain, a red loss) stay.
           An accent the creator chose with finish(accent=...) is not teal any more, so it carries into every style.
  type     the @font-face rules of Instrument Serif / Instrument Sans / JetBrains Mono point at the style's fonts, scaled
           with size-adjust so a line keeps the width it had (no word runs off the canvas because a font is wider).
  look     the style's own CSS: the ground's decor (grid, ruled lines, halftone, light), card and caption treatment.
  fixes    <project>/build/style-overrides/<id>.css, if present, is added last: the place for a per-video fix.

Each style folder is a full HyperFrames project (render it like the main one) whose assets/ links to the project's
assets/, so the footage is never copied. Python 3.10+ standard library only.
"""
import argparse
import datetime
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SKILL = Path(__file__).resolve().parent.parent
HF = "hyperframes@0.8.106"
RANGE_SLICE = 2 << 20          # bytes per answer to a video range request (the picker's server)
PLAYER_URL = f"https://cdn.jsdelivr.net/npm/{HF}/dist/hyperframes-player.global.js"

BASE_PAPER, BASE_INK = "#F5F1EA", "#17140F"
TEAL, TEAL_D, TEAL_T, TEAL_T2 = "#0B7A73", "#075450", "#D7ECE8", "#BFDDD7"
PROTECT = {"#FFF8EF"}          # caption text over footage: it sits on the video, not on the ground
WARM_SHADOWS = {(40, 30, 20), (20, 15, 10), (23, 20, 15), (10, 8, 6)}
FAMILIES = {"serif": "Instrument Serif", "sans": "Instrument Sans", "mono": "JetBrains Mono"}
# Card-like surfaces of the kit (reel_kit, video_kit, paper_reel): a style restyles them together.
SURF = (".bx-card,.mcard,.pr-tile,.doc,.vc,.sw,.pf,.dm,.ckl,.tlc,.wv,.kc,.pr-bubble,.bx-browser,.pr-win,.pw,"
        ".bx-frame,.pr-fv")
SERIF = ".bx-serif,.bx-pserif,.pl.serif,.doc .dt,.sw .swt,.pr-slip .sn"

# ---------------------------------------------------------------- the styles
# palette: paper (the ground), ink (main text), card (surfaces lighter than paper), accent / accent_deep / accent_tint,
# shadow (rgb of soft shadows) and shadow_k (alpha multiplier). fonts: family -> (file in assets/fonts, size-adjust),
# measured so each line keeps Instrument's width. css: $token is replaced by the palette value.
STYLES = [
    {
        "id": "paper", "label": "Warm Paper",
        "about": "the original: cream paper, grain and window-light leaves, serif italic words, teal accent",
        "best": "calm tutorials, AI tools, personal finance",
        "palette": None, "fonts": {}, "css": "",
    },
    {
        "id": "glow", "label": "Midnight Glow",
        "about": "near-black ground with cyan and violet light and a faint grid; glassy cards; bold geometric type",
        "best": "tech, AI, data, what comes next",
        "palette": {"paper": "#070A14", "ink": "#EEF1FA", "card": "#141C33", "accent": "#36D6EE",
                    "accent_deep": "#1592AB", "accent_tint": "#0E2A3A", "shadow": (0, 0, 0), "shadow_k": 2.4},
        "fonts": {"serif": ("outfit-800-normal.woff2", 0.78), "sans": ("outfit-700-normal.woff2", 1.0)},
        "css": f"""
.bx-paper{{background:radial-gradient(900px 760px at 12% 6%,rgba(54,214,238,.22),rgba(54,214,238,0) 70%),
 radial-gradient(1000px 900px at 92% 62%,rgba(139,92,246,.24),rgba(139,92,246,0) 70%),
 radial-gradient(900px 700px at 25% 104%,rgba(236,72,153,.14),rgba(236,72,153,0) 70%),
 linear-gradient(rgba(255,255,255,.035) 2px,transparent 2px) 0 0/72px 72px,
 linear-gradient(90deg,rgba(255,255,255,.035) 2px,transparent 2px) 0 0/72px 72px,$paper}}
.bx-grain{{opacity:.10}}.bx-leaf{{display:none}}
{SURF}{{box-shadow:inset 0 0 0 2px rgba(255,255,255,.09),0 30px 70px rgba(0,0,0,.55)}}
.pl{{box-shadow:inset 0 0 0 2px rgba(255,255,255,.10),0 18px 44px rgba(0,0,0,.6)}}
.bx-serif,.bx-sans{{letter-spacing:-.01em}}
.bx-coral{{text-shadow:0 0 34px rgba(54,214,238,.55)}}
.bx-phone,.pr-phone{{border-color:#02040A;background:#02040A}}.bx-isl{{background:#02040A}}
""",
    },
    {
        "id": "doodle", "label": "Storybook Doodle",
        "about": "notebook paper with ruled lines and a red margin; hand-drawn ink outlines; handwritten words",
        "best": "beginners, kids, light topics",
        "palette": {"paper": "#FBF6EA", "ink": "#2B2A33", "card": "#FFFFFF", "accent": "#D9453A",
                    "accent_deep": "#9E2B23", "accent_tint": "#FBE1DC", "shadow": (43, 42, 51), "shadow_k": 0.8},
        "fonts": {"serif": ("caveat-700-normal.woff2", 1.05), "sans": ("nunito-900-normal.woff2", 0.96)},
        "css": f"""
.bx-paper{{background:linear-gradient(90deg,transparent 116px,rgba(232,90,79,.55) 116px,rgba(232,90,79,.55) 120px,transparent 120px),
 repeating-linear-gradient(180deg,transparent 0 62px,rgba(88,136,196,.24) 62px 64px),$paper}}
.bx-grain{{opacity:.35}}.bx-leaf{{display:none}}
{SURF}{{border:4px solid $ink;box-shadow:6px 7px 0 rgba(43,42,51,.85);border-radius:30px 22px 34px 18px/22px 32px 18px 28px}}
.pl{{border:4px solid $ink;box-shadow:5px 6px 0 rgba(43,42,51,.85);border-radius:26px 18px 28px 16px/18px 26px 16px 24px}}
.btnt{{border:4px solid $ink;box-shadow:5px 6px 0 rgba(43,42,51,.85)}}
.bx-serif{{letter-spacing:0}}
""",
    },
    {
        "id": "editorial", "label": "Bold Editorial",
        "about": "newsprint with halftone corners and black rules; tall condensed capitals; captions on black bars",
        "best": "news, hot takes, market moves",
        "palette": {"paper": "#EFE9DD", "ink": "#111111", "card": "#FFFFFF", "accent": "#D42B26",
                    "accent_deep": "#97201C", "accent_tint": "#F6D5D2", "shadow": (17, 17, 17), "shadow_k": 0.9},
        "fonts": {"serif": ("league-gothic-400-normal.woff2", 1.1), "sans": ("archivo-black-400-normal.woff2", 0.86),
                  "mono": ("ibm-plex-mono-600-normal.woff2", 1.0)},
        "css": f"""
.bx-paper::before{{content:"";position:absolute;left:0;top:0;width:1080px;height:1920px;
 background:radial-gradient(circle,rgba(17,17,17,.24) 2.6px,transparent 3px) 0 0/24px 24px;
 -webkit-mask:radial-gradient(560px 560px at 0 0,#000,transparent 70%),radial-gradient(620px 620px at 100% 100%,#000,transparent 70%);
 mask:radial-gradient(560px 560px at 0 0,#000,transparent 70%),radial-gradient(620px 620px at 100% 100%,#000,transparent 70%)}}
.bx-paper::after{{content:"";position:absolute;left:60px;width:960px;top:70px;height:10px;background:$ink;box-shadow:0 22px 0 -7px $ink}}
.bx-grain{{opacity:.45}}.bx-leaf{{display:none}}
{SERIF}{{text-transform:uppercase;letter-spacing:.005em}}
{SURF}{{border-radius:3px;box-shadow:0 0 0 3px $ink,0 18px 36px rgba(17,17,17,.22)}}
.pl{{border-radius:0;background:$ink;color:$paper;box-shadow:none}}.pl .g{{color:#B9B2A6}}
.btnt{{border-radius:4px}}
""",
    },
    {
        "id": "block", "label": "Colour Block",
        "about": "flat full-bleed colour that changes scene by scene; huge condensed capitals; flat cards",
        "best": "hooks, punchy lessons, money tips",
        # one ground per scene, in turn; the neutrals of each scene move onto that scene's ground and ink
        "grounds": [
            {"paper": "#1F3BFF", "ink": "#FFFFFF", "card": "#3550FF", "accent": "#C8F01E", "accent_deep": "#9DBF0C",
             "accent_tint": "#2B44E0", "shadow": (8, 14, 70), "shadow_k": 1.2},
            {"paper": "#F1EDE0", "ink": "#0B0B0F", "card": "#FFFFFF", "accent": "#E8401A", "accent_deep": "#A82C10",
             "accent_tint": "#FBD9CE", "shadow": (11, 11, 15), "shadow_k": 0.8},
            {"paper": "#0B0B0F", "ink": "#F1EDE0", "card": "#1C1C24", "accent": "#C8F01E", "accent_deep": "#9DBF0C",
             "accent_tint": "#23280E", "shadow": (0, 0, 0), "shadow_k": 2.0},
            {"paper": "#C8F01E", "ink": "#0B0B0F", "card": "#E2FA7A", "accent": "#1F3BFF", "accent_deep": "#152AB8",
             "accent_tint": "#DDF77E", "shadow": (40, 50, 0), "shadow_k": 0.9},
            {"paper": "#FF4A1C", "ink": "#0B0B0F", "card": "#FF7A55", "accent": "#FFFFFF", "accent_deep": "#0B0B0F",
             "accent_tint": "#FF6A40", "shadow": (70, 10, 0), "shadow_k": 1.0},
        ],
        "fonts": {"serif": ("anton-400-normal.woff2", 0.89), "sans": ("inter-900-normal.woff2", 0.96)},
        "css": f"""
.bx-paper{{background:$paper}}.bx-grain{{display:none}}.bx-leaf{{display:none}}
{SERIF}{{text-transform:uppercase;letter-spacing:.005em}}
{SURF}{{border-radius:0;box-shadow:none}}
.pl{{border-radius:0;background:#0B0B0F;color:#FFFFFF;box-shadow:none}}.pl .g{{color:#B8B8C2}}
.btnt{{border-radius:0;box-shadow:none}}
""",
    },
    {
        "id": "riso", "label": "Riso Print",
        "about": "two-ink zine: ultramarine and fluorescent pink on grainy paper, a halftone disc, offset print shadows",
        "best": "stories, data, thoughtful topics",
        "palette": {"paper": "#EFE8D8", "ink": "#2A24C4", "card": "#F8F3E8", "accent": "#E23A7A",
                    "accent_deep": "#A8245A", "accent_tint": "#F9D6E4", "shadow": (42, 36, 196), "shadow_k": 0.55},
        "fonts": {"serif": ("bodoni-moda-800-normal.woff2", 0.73), "sans": ("inter-800-normal.woff2", 0.97)},
        "css": f"""
.bx-paper::before{{content:"";position:absolute;width:780px;height:780px;left:520px;top:-200px;border-radius:50%;
 background:radial-gradient(circle,rgba(255,92,147,.55) 3.4px,transparent 3.9px) 0 0/16px 16px}}
.bx-paper::after{{content:"";position:absolute;width:520px;height:520px;left:-200px;top:1500px;border-radius:50%;
 background:radial-gradient(circle,rgba(42,36,196,.30) 3px,transparent 3.5px) 0 0/16px 16px}}
.bx-grain{{opacity:.85}}.bx-leaf{{display:none}}
.bx-serif{{text-shadow:6px 4px 0 rgba(255,92,147,.55)}}
{SURF}{{border-radius:8px;box-shadow:9px 8px 0 rgba(255,92,147,.50)}}
.pl{{box-shadow:6px 5px 0 rgba(255,92,147,.60)}}
""",
    },
    {
        "id": "terminal", "label": "Signal Terminal",
        "about": "black screen with scanlines and a lime glow; everything in monospace; outlined panels",
        "best": "tech, AI, coding, how-to",
        "palette": {"paper": "#070907", "ink": "#E6FFDA", "card": "#0F150F", "accent": "#B6FF2E",
                    "accent_deep": "#7DBA0A", "accent_tint": "#1B2A0B", "shadow": (0, 0, 0), "shadow_k": 2.4},
        "fonts": {"serif": ("jetbrains-mono-700-normal.woff2", 0.64), "sans": ("jetbrains-mono-700-normal.woff2", 0.8)},
        "css": f"""
.bx-paper{{background:repeating-linear-gradient(0deg,rgba(182,255,46,.05) 0 2px,transparent 2px 6px),
 radial-gradient(1200px 1000px at 50% 30%,rgba(182,255,46,.08),rgba(182,255,46,0) 70%),$paper}}
.bx-grain{{display:none}}.bx-leaf{{display:none}}
{SURF}{{border-radius:8px;box-shadow:inset 0 0 0 2px rgba(182,255,46,.45),0 0 44px rgba(182,255,46,.10)}}
.pl{{border-radius:6px;box-shadow:inset 0 0 0 2px rgba(182,255,46,.50)}}
.btnt{{border-radius:8px}}.bx-chip{{border-radius:6px}}
.bx-serif,.bx-sans,.bx-cap{{letter-spacing:0}}
.bx-coral{{text-shadow:0 0 26px rgba(182,255,46,.45)}}
.bx-phone,.pr-phone{{border-color:#020302;background:#020302}}.bx-isl{{background:#020302}}
""",
    },
    {
        "id": "sticker", "label": "Sticker Board",
        "about": "cream board with a dot grid; every card a sticker with a thick black outline and a hard shadow",
        "best": "how something works, step by step",
        "palette": {"paper": "#FDF8E6", "ink": "#111111", "card": "#FFFFFF", "accent": "#E0399E",
                    "accent_deep": "#A11F70", "accent_tint": "#FFE0F3", "shadow": (17, 17, 17), "shadow_k": 0.8},
        "fonts": {"serif": ("bricolage-grotesque-800-normal.woff2", 0.725),
                  "sans": ("bricolage-grotesque-800-normal.woff2", 0.97)},
        "css": f"""
.bx-paper{{background:radial-gradient(circle,rgba(17,17,17,.13) 2.6px,transparent 3px) 0 0/44px 44px,$paper}}
.bx-grain{{opacity:.25}}.bx-leaf{{display:none}}
{SURF}{{box-shadow:0 0 0 5px #111111,10px 10px 0 5px #111111}}
.pl{{box-shadow:0 0 0 4px #111111,7px 7px 0 4px #111111}}
.btnt,.bx-chip{{box-shadow:0 0 0 4px #111111,6px 6px 0 4px #111111}}
.bx-serif{{letter-spacing:-.025em}}
""",
    },
    {
        "id": "aurora", "label": "Aurora",
        "about": "cool pale ground lit by lavender, peach, mint and sky light, a dot grid, glass cards; serif italic",
        "best": "AI tools, apps and how-tos, a calm modern feel",
        "palette": {"paper": "#EEF0F7", "ink": "#14151A", "card": "#FFFFFF", "accent": TEAL,
                    "accent_deep": TEAL_D, "accent_tint": TEAL_T, "shadow": (40, 40, 90), "shadow_k": 1.0},
        "fonts": {},
        "css": f"""
.bx-paper{{background:radial-gradient(1300px 1300px at 0% 0%,rgba(194,178,255,.80),rgba(194,178,255,0) 60%),
 radial-gradient(1250px 1250px at 100% 45%,rgba(255,196,163,.70),rgba(255,196,163,0) 60%),
 radial-gradient(1300px 1300px at 0% 88%,rgba(166,232,214,.80),rgba(166,232,214,0) 60%),
 radial-gradient(900px 900px at 82% 100%,rgba(186,214,255,.70),rgba(186,214,255,0) 60%),$paper}}
.bx-paper::before{{content:"";position:absolute;left:0;top:0;width:1080px;height:1920px;
 background:radial-gradient(rgba(20,22,40,.10) 2.6px,transparent 3px) 0 0/46px 46px}}
.bx-grain{{opacity:.18}}.bx-leaf{{display:none}}
{SURF}{{box-shadow:0 30px 70px rgba(40,40,90,.16),inset 0 0 0 2px rgba(255,255,255,.95)}}
.pl{{border-radius:999px;box-shadow:0 16px 40px rgba(40,40,90,.18)}}
""",
    },
]
BY_ID = {s["id"]: s for s in STYLES}


# ---------------------------------------------------------------- colour
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*(max(0, min(255, round(c))) for c in rgb))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _delin(v):
    v = max(0.0, min(1.0, v))
    return 255 * (v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055)


def lum(rgb):
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(_rgb(a)), lum(_rgb(b))
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _mix(a, b, w):
    """a -> b by w, in linear light (so luminance moves linearly with w)."""
    return tuple(_delin(_lin(x) + (_lin(y) - _lin(x)) * w) for x, y in zip(a, b))


class Palette:
    def __init__(self, p):
        self.p = p
        self.paper, self.ink, self.card = _rgb(p["paper"]), _rgb(p["ink"]), _rgb(p["card"])
        self.Lp, self.Li = lum(self.paper), lum(self.ink)
        self.cmax = (max(self.Lp, self.Li) + 0.05) / (min(self.Lp, self.Li) + 0.05)
        self.ink_darker = self.Li < self.Lp
        self.fam = {TEAL: p["accent"].upper(), TEAL_D: p["accent_deep"].upper(), TEAL_T: p["accent_tint"].upper(),
                    TEAL_T2: _hex(_mix(_rgb(p["accent_tint"]), _rgb(p["accent"]), 0.25))}
        self.shadow, self.shadow_k = p["shadow"], p["shadow_k"]

    def hex(self, h):
        u = "#" + h.lstrip("#").upper()
        if u in PROTECT:
            return h
        if u in self.fam:
            return self.fam[u]
        rgb = _rgb(u)
        if (max(rgb) - min(rgb)) / 255 > 0.13:          # a real colour (green gain, red loss, yellow): keep it
            return h
        return _hex(self.neutral(rgb))

    def neutral(self, rgb):
        """Move a warm neutral onto this style's paper/ink, keeping its contrast against the paper."""
        Lc, Lp0 = lum(rgb), lum(_rgb(BASE_PAPER))
        if Lc <= Lp0:                                   # towards ink: same contrast, capped at the style's ink
            ct = min((Lp0 + 0.05) / (Lc + 0.05), self.cmax)
            lt = (self.Lp + 0.05) / ct - 0.05 if self.ink_darker else (self.Lp + 0.05) * ct - 0.05
            w = 0.0 if self.Li == self.Lp else (lt - self.Lp) / (self.Li - self.Lp)
            return _mix(self.paper, self.ink, max(0.0, min(1.0, w)))
        q = math.log((Lc + 0.05) / (Lp0 + 0.05)) / math.log(1.05 / (Lp0 + 0.05))   # towards white: paper -> card
        return _mix(self.paper, self.card, max(0.0, min(1.0, q)))

    def rgba(self, m):
        r, g, b, a = int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
        if (r, g, b) in WARM_SHADOWS:
            sr, sg, sb = self.shadow
            return f"rgba({sr},{sg},{sb},{min(0.92, a * self.shadow_k):.2f})"
        if (r, g, b) == (7, 84, 80):
            return "rgba({},{},{},".format(*_rgb(self.p["accent_deep"])) + f"{a})"
        if (r, g, b) == (255, 253, 249):
            return "rgba({},{},{},".format(*self.card) + f"{a})"
        return m.group(0)

    def apply(self, text):
        text = re.sub(r"#[0-9A-Fa-f]{6}\b", lambda m: self.hex(m.group(0)), text)
        return re.sub(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", self.rgba, text)

    def tokens(self, css):
        vals = {k: v for k, v in self.p.items() if isinstance(v, str)}
        return re.sub(r"\$(\w+)", lambda m: vals.get(m.group(1), m.group(0)), css)


# ---------------------------------------------------------------- fonts
FACE_RE = re.compile(r"@font-face\{[^}]*font-family:'(?:Instrument Serif|Instrument Sans|JetBrains Mono)'[^}]*\}\s*")


def _family(style, key):
    """The style's own name for a replaced family. A name of its own, so no other style on the picker page and no
    font the renderer knows by name ('Instrument Serif' is a Google font) can stand in for it."""
    return f"ve-{style['id']}-{key}"


def _faces(style):
    """@font-face rules for this style's fonts, at the measured size-adjust."""
    out = []
    for key, (f, adj) in style["fonts"].items():
        for st in (("italic", "normal") if key == "serif" else ("normal",)):
            out.append(f"@font-face{{font-family:'{_family(style, key)}';font-style:{st};font-weight:100 900;"
                       f"src:url(assets/fonts/{f}) format('woff2');size-adjust:{adj * 100:.1f}%}}")
    return "\n".join(out) + "\n"


def restyle(text, style, pal, extra_css=""):
    """One composition (or index.html) in this style."""
    if pal:
        text = pal.apply(text)
    if style.get("fonts") and "@font-face" in text:
        text = FACE_RE.sub(lambda m: m.group(0) if not _owned(m.group(0), style["fonts"]) else "", text)
        for key in style["fonts"]:
            text = text.replace(f"'{FAMILIES[key]}'", f"'{_family(style, key)}'")
        i = text.find("<style>")
        if i >= 0:
            text = text[:i + 7] + "\n" + _faces(style) + text[i + 7:]
    css = (pal.tokens(style["css"]) if pal else style["css"]) + extra_css
    if css.strip():
        j = text.find("</style>")
        if j >= 0:
            text = text[:j] + f"\n/* style: {style['id']} */\n" + css.strip() + "\n" + text[j:]
    return text


def _owned(rule, fonts):
    return any(f"font-family:'{FAMILIES[k]}'" in rule for k in fonts)


# ---------------------------------------------------------------- build
def _scene_files(project):
    """Composition files in timeline order (from index.html), so per-scene grounds follow the edit."""
    idx = (project / "index.html").read_text(encoding="utf-8")
    order = re.findall(r'data-composition-src="(compositions/[^"]+)"', idx)
    rest = sorted(p.relative_to(project).as_posix() for p in (project / "compositions").glob("*.html"))
    return order + [r for r in rest if r not in order]


def _link_assets(dst, project):
    link = dst / "assets"
    if link.is_symlink():
        link.unlink()
    elif _is_junction(link):
        os.rmdir(link)
    elif link.exists():
        raise SystemExit(f"{link} is a real folder or file; move it away so it can link to the project's assets/")
    try:
        os.symlink(os.path.relpath(project / "assets", dst), link, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            raise
        import _winapi  # Windows without symlink rights: a directory junction needs none
        _winapi.CreateJunction(str((project / "assets").resolve()), str(link))


def _is_junction(p):
    try:
        return bool(os.readlink(p))
    except OSError:
        return False


def _write(path, text):
    """Write through a temporary file and rename: the style agents rebuild in parallel, and the picker's server may be
    reading styles.json / picker.html at that moment."""
    tmp = Path(f"{path}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _fonts_into(project, styles):
    """Copy every font file the styles use (and their licences) into <project>/assets/fonts."""
    dst = project / "assets" / "fonts"
    dst.mkdir(parents=True, exist_ok=True)
    src = SKILL / "assets" / "fonts"
    files = {f for s in styles for f, _ in s.get("fonts", {}).values()}
    for f in sorted(files) + [p.name for p in src.glob("OFL-*.txt")]:
        if not (dst / f).exists():
            tmp = dst / f"{f}.{os.getpid()}.{threading.get_ident()}.tmp"
            shutil.copy2(src / f, tmp)
            os.replace(tmp, dst / f)


def build(project, ids):
    project = Path(project).resolve()
    if not (project / "index.html").exists():
        raise SystemExit(f"{project}/index.html is missing: run build/scenes.py first (it writes the edit)")
    styles = [BY_ID[i] for i in ids]
    _fonts_into(project, styles)
    files = _scene_files(project)
    root = project / "styles"
    root.mkdir(exist_ok=True)
    built = []
    for st in styles:
        out = root / st["id"]
        if (out / "compositions").exists():
            shutil.rmtree(out / "compositions")
        (out / "compositions").mkdir(parents=True)
        fix = project / "build" / "style-overrides" / f"{st['id']}.css"
        extra = ("\n/* per-video fixes: build/style-overrides */\n" + fix.read_text(encoding="utf-8")) if fix.exists() else ""
        grounds = st.get("grounds") or ([st["palette"]] if st.get("palette") else [None])
        pals = [Palette(g) if g else None for g in grounds]
        for k, rel in enumerate(files):
            text = (project / rel).read_text(encoding="utf-8")
            (out / rel).write_text(restyle(text, st, pals[k % len(pals)], extra), encoding="utf-8")
        idx = (project / "index.html").read_text(encoding="utf-8")
        (out / "index.html").write_text(pals[0].apply(idx) if pals[0] else idx, encoding="utf-8")
        for name in ("hyperframes.json", "package.json"):
            if (project / name).exists():
                shutil.copy2(project / name, out / name)
        meta = {"id": f"{project.name}-{st['id']}", "name": f"{project.name} · {st['label']}",
                "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        _link_assets(out, project)
        built.append(st["id"])
    manifest = {"built": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "duration": _duration(project), "styles": [s["id"] for s in STYLES if (root / s["id"]).exists()]}
    _write(root / "styles.json", json.dumps(manifest, indent=2))
    _write(project / "picker.html", picker_html(project, manifest))
    return built


def _duration(project):
    m = re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"',
                  (project / "index.html").read_text(encoding="utf-8"))
    return float(m.group(1)) if m else 0.0


def current_pick(project):
    f = Path(project) / "styles" / "pick.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("style")
    except (OSError, ValueError):
        return None


def set_pick(project, sid):
    if sid not in BY_ID:
        raise SystemExit(f"unknown style {sid!r}: {', '.join(BY_ID)}")
    if not (Path(project) / "styles" / sid / "index.html").exists():
        raise SystemExit(f"styles/{sid} isn't built yet: python styles.py build <project> --styles {sid}")
    f = Path(project) / "styles" / "pick.json"
    _write(f, json.dumps({"style": sid, "label": BY_ID[sid]["label"],
                          "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}, indent=2))
    return sid


# ---------------------------------------------------------------- the picker
def picker_html(project, manifest):
    title = html.escape(project.name)
    dur = manifest["duration"]
    pick = current_pick(project)
    cards = []
    for k, sid in enumerate(manifest["styles"]):
        s = BY_ID[sid]
        letter = chr(65 + k)
        cards.append(f"""  <figure class="st{' picked' if sid == pick else ''}" data-style="{sid}" tabindex="0">
    <div class="frame"><hyperframes-player src="styles/{sid}/index.html" muted></hyperframes-player></div>
    <figcaption><b>{letter} · {html.escape(s['label'])}</b>{'<span class="star">★ Your pick</span>' if sid == pick else ''}
      <span class="about">{html.escape(s['about'])}</span>
      <span class="best">Good for {html.escape(s['best'])}</span>
      <button class="pickbtn" type="button" data-style="{sid}">{'★ Picked' if sid == pick else '☆ Use this style'}</button>
    </figcaption>
  </figure>""")
    cards = "\n".join(cards)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} · Style Picker</title>
<script src="{PLAYER_URL}"></script>
<style>
  :root {{ color-scheme: dark; --bg: #111214; --panel: #1b1c20; --line: #2c2e34; --text: #f2f2f4; --muted: #9a9ca5; --accent: #2fc4b2; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text); font: 15px/1.45 -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
  header {{ position: sticky; top: 0; z-index: 2; display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center; padding: 14px 18px; background: rgba(17,18,20,.92); border-bottom: 1px solid var(--line); backdrop-filter: blur(8px); }}
  h1 {{ margin: 0; font-size: 18px; }}
  header p {{ margin: 0; color: var(--muted); }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; flex: 1 1 380px; }}
  button {{ background: var(--panel); color: var(--text); border: 1px solid var(--line); border-radius: 10px; padding: 8px 14px; font: inherit; cursor: pointer; white-space: nowrap; }}
  button:hover {{ border-color: var(--accent); }}
  input[type=range] {{ flex: 1; min-width: 140px; accent-color: var(--accent); }}
  label {{ color: var(--muted); display: flex; gap: 6px; align-items: center; white-space: nowrap; }}
  #time {{ font-variant-numeric: tabular-nums; color: var(--muted); min-width: 62px; text-align: right; }}
  #msg {{ color: var(--accent); font-weight: 600; }}
  main {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; padding: 18px; }}
  .st {{ margin: 0; padding: 10px; border: 2px solid var(--line); border-radius: 18px; background: var(--panel); cursor: pointer; }}
  .st.selected {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(47,196,178,.25); }}
  .st.picked {{ border-color: #e8c35a; }}
  .frame {{ position: relative; width: 100%; aspect-ratio: 9 / 16; border-radius: 12px; overflow: hidden; background: #000; }}
  hyperframes-player {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
  figcaption {{ display: flex; flex-direction: column; gap: 3px; padding: 10px 4px 2px; }}
  .about, .best {{ color: var(--muted); font-size: 13px; }}
  .star {{ color: #e8c35a; font-weight: 700; font-size: 13px; }}
  .pickbtn {{ margin-top: 6px; align-self: flex-start; padding: 5px 10px; font-size: 13px; border-color: var(--accent); }}
  .st.picked .pickbtn {{ border-color: #e8c35a; color: #e8c35a; }}
</style>
</head>
<body>
<header>
  <h1>Pick a style</h1>
  <p>{title} · {dur:.1f} s · the same edit in every style, playing live · nothing renders until you pick</p>
  <div class="controls">
    <button id="play" type="button">▶ Play</button>
    <button id="pause" type="button">❚❚ Pause</button>
    <input id="scrub" type="range" min="0" max="{dur}" step="0.01" value="0" aria-label="Time" />
    <span id="time">0.0 s</span>
    <label title="Playing every style at once needs a fast computer; this plays only the one you selected and keeps the rest on the same frame"><input id="solo" type="checkbox" /> Play only the selected style</label>
  </div>
  <span id="msg">Click a style to hear it. Then press “Use this style”, or tell Claude which one you want.</span>
</header>
<main>
{cards}
</main>
<script>
  const DRIFT = 0.12;
  const figs = [...document.querySelectorAll('.st')];
  const players = figs.map((f) => f.querySelector('hyperframes-player'));
  let selected = players[0];
  let playing = false;
  const solo = document.getElementById('solo');
  const msg = document.getElementById('msg');
  const label = (f) => f.querySelector('b').textContent.replace(/^[A-Z] · /, '');
  function select(fig) {{
    figs.forEach((f) => f.classList.toggle('selected', f === fig));
    selected = fig.querySelector('hyperframes-player');
    players.forEach((p) => {{ p.muted = p !== selected; }});
    if (playing) start();
    msg.textContent = 'Listening to ' + label(fig) + '. To keep it, press “Use this style”, or tell Claude: use ' + label(fig) + '.';
  }}
  figs.forEach((f) => {{
    f.addEventListener('click', () => select(f));
    f.addEventListener('keydown', (e) => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); select(f); }} }});
  }});
  const active = () => (solo.checked ? [selected] : players);
  function seekAll(t) {{ players.forEach((p) => {{ p.currentTime = t; }}); }}
  function start() {{
    const t = selected.currentTime || 0;
    seekAll(t);
    players.forEach((p) => {{ if (active().includes(p)) p.play(); else p.pause(); }});
    playing = true;
  }}
  document.getElementById('play').addEventListener('click', start);
  document.getElementById('pause').addEventListener('click', () => {{ players.forEach((p) => p.pause()); playing = false; seekAll(selected.currentTime || 0); }});
  solo.addEventListener('change', () => {{ if (playing) start(); }});
  const scrub = document.getElementById('scrub');
  scrub.addEventListener('input', () => seekAll(+scrub.value));
  document.querySelectorAll('.pickbtn').forEach((btn) => {{
    btn.addEventListener('keydown', (e) => e.stopPropagation());
    btn.addEventListener('click', async (e) => {{
      e.stopPropagation();
      const fig = btn.closest('.st');
      try {{
        const r = await fetch('__ve/pick?style=' + encodeURIComponent(btn.dataset.style), {{ method: 'POST', headers: {{ 'x-ve': '1' }} }});
        const j = await r.json();
        if (!j.ok) throw new Error(j.error || r.statusText);
        figs.forEach((f) => {{ f.classList.toggle('picked', f === fig); const b = f.querySelector('.pickbtn'); b.textContent = f === fig ? '★ Picked' : '☆ Use this style'; }});
        msg.textContent = '★ ' + label(fig) + ' is your pick. Tell Claude “render it” and only this style is rendered.';
      }} catch (err) {{
        msg.textContent = 'Could not save the pick (' + err.message + '). Tell Claude: use ' + label(fig) + '.';
      }}
    }});
  }});
  select(figs.find((f) => f.classList.contains('picked')) || figs[0]);
  (function tick() {{
    const t = selected.currentTime || 0;
    if (document.activeElement !== scrub) scrub.value = t;
    document.getElementById('time').textContent = t.toFixed(1) + ' s';
    if (playing) active().forEach((p) => {{ if (p !== selected && Math.abs((p.currentTime || 0) - t) > DRIFT) p.currentTime = t; }});
    requestAnimationFrame(tick);
  }})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- serve (with byte ranges, so video seeks)
def serve(project, port):
    project = Path(project).resolve()
    if not (project / "picker.html").exists():
        raise SystemExit("no picker.html yet: python styles.py build <project> first")

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(project), **k)

        def log_message(self, *a):
            pass

        def end_headers(self):
            self.send_header("Accept-Ranges", "bytes")
            # pages and the manifest change on every build; fonts, images and footage don't, and nine players load
            # each font once per scene, so let the browser keep those
            fresh = urlparse(self.path).path.endswith((".html", ".json", "/"))
            self.send_header("Cache-Control", "no-store" if fresh else "max-age=600")
            super().end_headers()

        def do_POST(self):
            u = urlparse(self.path)
            if u.path != "/__ve/pick" or self.headers.get("x-ve") != "1":
                return self.send_error(HTTPStatus.NOT_FOUND)
            try:
                sid = set_pick(project, (parse_qs(u.query).get("style") or [""])[0])
                body = json.dumps({"ok": True, "style": sid}).encode()
            except SystemExit as e:
                body = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def send_head(self):
            rng = self.headers.get("Range")
            path = self.translate_path(self.path)
            if not rng or not os.path.isfile(path):
                return super().send_head()
            m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
            size = os.path.getsize(path)
            if not m or (not m.group(1) and not m.group(2)):
                return super().send_head()
            if m.group(1):
                start, end = int(m.group(1)), int(m.group(2)) if m.group(2) else size - 1
            else:
                start, end = max(0, size - int(m.group(2))), size - 1
            # an open range ("bytes=N-") on a 400 MB clip would hold one of the browser's six connections for the
            # whole download; nine players then starve the fonts. Answer in slices; the player asks for the next one.
            end = min(end, size - 1, start + RANGE_SLICE - 1)
            if start > end:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return None
            f = open(path, "rb")
            f.seek(start)
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()
            return _Slice(f, end - start + 1)

        def copyfile(self, source, outputfile):
            if isinstance(source, _Slice):
                left = source.n
                while left > 0:
                    chunk = source.f.read(min(1 << 16, left))
                    if not chunk:
                        break
                    try:
                        outputfile.write(chunk)
                    except (BrokenPipeError, ConnectionResetError):
                        break
                    left -= len(chunk)
                return
            try:
                super().copyfile(source, outputfile)
            except (BrokenPipeError, ConnectionResetError):
                pass

    for p in range(port, port + 20):            # another picker (or anything) on the port: take the next free one
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", p), Handler)
            break
        except OSError:
            continue
    else:
        raise SystemExit(f"ports {port}-{port + 19} are all busy; pass --port")
    print(f"Style Picker: http://127.0.0.1:{httpd.server_port}/picker.html  (Ctrl+C to stop)", flush=True)
    httpd.serve_forever()


class _Slice:
    def __init__(self, f, n):
        self.f, self.n = f, n

    def close(self):
        self.f.close()


# ---------------------------------------------------------------- check
def check(project, ids):
    """hyperframes lint + check in each style folder; prints one line per style and returns the failures."""
    project = Path(project).resolve()
    npx = shutil.which("npx") or "npx"
    failed = []
    for sid in ids:
        d = project / "styles" / sid
        if not (d / "index.html").exists():
            print(f"{sid:10s} not built")
            failed.append(sid)
            continue
        log = d / "check.log"
        with open(log, "w", encoding="utf-8") as lf:
            r1 = subprocess.run([npx, "--yes", HF, "lint"], cwd=d, stdout=lf, stderr=subprocess.STDOUT)
            r2 = subprocess.run([npx, "--yes", HF, "check"], cwd=d, stdout=lf, stderr=subprocess.STDOUT)
        ok = "Check passed" in log.read_text(encoding="utf-8", errors="replace")
        print(f"{sid:10s} lint {'ok' if r1.returncode == 0 else 'FAILED'} · check {'passed' if ok else 'FAILED'}  ({log})",
              flush=True)
        if not ok or r1.returncode != 0:
            failed.append(sid)
    return failed


# ---------------------------------------------------------------- snapshots and the all-styles sheet
def scene_times(project, k=None):
    """One moment per scene, late in it (everything has built in, the exit hasn't started), in timeline order; k of
    them spread over the edit."""
    idx = (Path(project) / "index.html").read_text(encoding="utf-8")
    times = []
    for tag in re.findall(r"<div[^>]*data-composition-src=\"[^\"]+\"[^>]*>", idx):
        s, d = re.search(r'data-start="([\d.]+)"', tag), re.search(r'data-duration="([\d.]+)"', tag)
        if s and d:
            start, dur = float(s.group(1)), float(d.group(1))
            times.append(round(start + dur - min(0.5, 0.15 * dur), 2))
    if not times:
        dur = _duration(Path(project))
        times = [round(dur * (i + 0.5) / (k or 6), 2) for i in range(k or 6)]
    if k and len(times) > k:
        times = [times[min(len(times) - 1, round((i + 0.5) * len(times) / k))] for i in range(k)]
    return times


def snap(project, ids, times, jobs=3):
    """hyperframes snapshot of every style at the same moments -> styles/<id>/snapshots/ (frames + contact sheets:
    contact-sheet.jpg, or contact-sheet-1.jpg, -2.jpg... when there are many frames).
    --describe false: frames stay on this computer (without it they go to Gemini when GEMINI_API_KEY is set)."""
    from concurrent.futures import ThreadPoolExecutor
    project = Path(project).resolve()
    npx = shutil.which("npx") or "npx"
    at = ",".join(f"{t:g}" for t in times)

    def one(sid):
        d = project / "styles" / sid
        if not (d / "index.html").exists():
            return sid, [], f"styles/{sid} isn't built"
        out = d / "snapshots"
        if out.exists():
            shutil.rmtree(out)
        r = subprocess.run([npx, "--yes", HF, "snapshot", "--at", at, "--no-end", "--timeout", "30000",
                            "--describe", "false", "-o", "snapshots"], cwd=d, capture_output=True, text=True)
        frames = sorted(out.glob("frame-*.png"))
        return sid, frames, "" if len(frames) == len(times) else (r.stdout + r.stderr)[-1500:]

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        res = list(ex.map(one, ids))
    for sid, frames, err in res:
        sheets = sorted(p.name for p in (project / "styles" / sid / "snapshots").glob("contact-sheet*.jpg"))
        print(f"{sid:10s} {len(frames)}/{len(times)} frames -> styles/{sid}/snapshots/ ({', '.join(sheets) or 'no contact sheet'})"
              + (f"\n{err}" if err else ""), flush=True)
    return {sid: frames for sid, frames, _ in res}


def sheet(project, ids, times):
    """Every style at the same few moments on one labelled image: styles/sheet.jpg (rows = styles, columns = times).
    Made with HyperFrames itself (a one-frame page of the snapshots), so it needs nothing beyond the render tools."""
    project = Path(project).resolve()
    frames = snap(project, ids, times)
    ids = [i for i in ids if len(frames.get(i, [])) == len(times)]
    if not ids:
        raise SystemExit("no style produced its snapshots; see the errors above")
    work = project / "styles" / "_sheet"
    if work.exists():
        shutil.rmtree(work)
    (work / "img").mkdir(parents=True)
    ff = shutil.which("ffmpeg") or "ffmpeg"
    LW, GAP, PAD, HEAD = 250, 12, 28, 56
    # the snapshot browser stops at 4096 px a side: size the tiles so every row fits
    TH = min(480, (4000 - 2 * PAD - HEAD - (len(ids) - 1) * GAP) // len(ids),
             (4000 - 2 * PAD - LW - (len(times) - 1) * GAP) // len(times) * 16 // 9)
    TW = TH * 9 // 16
    for sid in ids:
        for j, f in enumerate(frames[sid]):
            subprocess.run([ff, "-v", "error", "-y", "-i", str(f), "-vf", f"scale={TW * 2}:{TH * 2}:flags=lanczos",
                            "-q:v", "3", str(work / "img" / f"{sid}-{j}.jpg")], check=True)
    shutil.copy2(SKILL / "assets" / "fonts" / "inter-800-normal.woff2", work / "inter.woff2")
    W = PAD * 2 + LW + len(times) * TW + (len(times) - 1) * GAP
    H = PAD * 2 + HEAD + len(ids) * TH + (len(ids) - 1) * GAP
    rows = []
    for k, sid in enumerate(ids):
        s = BY_ID[sid]
        y = PAD + HEAD + k * (TH + GAP)
        rows.append(f'<div class="lab" style="top:{y}px"><b>{chr(65 + STYLES.index(s))} · {html.escape(s["label"])}</b>'
                    f'<span>{html.escape(s["best"])}</span><i>{sid}</i></div>')
        for j in range(len(times)):
            rows.append(f'<img src="img/{sid}-{j}.jpg" style="left:{PAD + LW + j * (TW + GAP)}px;top:{y}px" />')
    heads = "".join(f'<div class="t" style="left:{PAD + LW + j * (TW + GAP)}px">{t:g} s</div>' for j, t in enumerate(times))
    (work / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:'ve-sheet';src:url(inter.woff2) format('woff2');font-weight:800}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#111214}}
#root{{position:relative;width:{W}px;height:{H}px;background:#111214;font-family:'ve-sheet',sans-serif;color:#F2F2F4}}
img{{position:absolute;width:{TW}px;height:{TH}px;border-radius:14px}}
.t{{position:absolute;top:{PAD}px;width:{TW}px;height:{HEAD - 12}px;line-height:{HEAD - 12}px;text-align:center;font-size:24px;color:#9A9CA5}}
.lab{{position:absolute;left:{PAD}px;width:{LW - 24}px;height:{TH}px;display:flex;flex-direction:column;justify-content:center;gap:10px}}
.lab b{{font-size:30px;line-height:1.1}}.lab span{{font-size:19px;line-height:1.3;color:#9A9CA5}}.lab i{{font-style:normal;font-size:18px;color:#2FC4B2}}
</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="1" data-fps="30" data-width="{W}" data-height="{H}">
{heads}
{chr(10).join(rows)}
</div>
<script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
</body></html>
""", encoding="utf-8")
    npx = shutil.which("npx") or "npx"
    r = subprocess.run([npx, "--yes", HF, "snapshot", "--at", "0.5", "--no-end", "--timeout", "30000",
                        "--describe", "false", "-o", "out"], cwd=work, capture_output=True, text=True)
    png = sorted((work / "out").glob("frame-*.png"))
    if not png:
        raise SystemExit("the sheet didn't render:\n" + (r.stdout + r.stderr)[-1500:])
    dst = project / "styles" / "sheet.jpg"
    subprocess.run([ff, "-v", "error", "-y", "-i", str(png[0]), "-q:v", "3", str(dst)], check=True)
    shutil.rmtree(work)
    return dst


# ---------------------------------------------------------------- cli
def _times(arg):
    try:
        return [float(t) for t in arg.split(",") if t.strip()]
    except ValueError:
        raise SystemExit(f"--at takes seconds, comma-separated (e.g. 12.5,30,48): {arg!r}")


def _ids(arg):
    if not arg or arg == "all":
        return [s["id"] for s in STYLES]
    ids = [i.strip() for i in arg.split(",") if i.strip()]
    bad = [i for i in ids if i not in BY_ID]
    if bad:
        raise SystemExit(f"unknown style(s) {', '.join(bad)}; the styles are {', '.join(BY_ID)}")
    return ids


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("project")
    b.add_argument("--styles", default="all")
    s = sub.add_parser("serve")
    s.add_argument("project")
    s.add_argument("--port", type=int, default=8770)
    p = sub.add_parser("pick")
    p.add_argument("project")
    p.add_argument("style", nargs="?")
    c = sub.add_parser("check")
    c.add_argument("project")
    c.add_argument("--styles", default="all")
    for name in ("snap", "sheet"):
        x = sub.add_parser(name)
        x.add_argument("project")
        x.add_argument("--styles", default="all")
        x.add_argument("--at", help="seconds, comma-separated (default: one moment per scene; sheet: 5 of them)")
    sub.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        done = build(a.project, _ids(a.styles))
        print(f"built {len(done)} style(s): {', '.join(done)} -> {Path(a.project).resolve() / 'styles'}")
        print(f"picker: {Path(a.project).resolve() / 'picker.html'}  (open it with: python {Path(__file__).name} serve {a.project})")
    elif a.cmd == "serve":
        serve(a.project, a.port)
    elif a.cmd == "pick":
        if a.style:
            set_pick(a.project, a.style)
            print(f"pick: {a.style} ({BY_ID[a.style]['label']}) -> render {Path(a.project).resolve() / 'styles' / a.style}")
        else:
            sid = current_pick(a.project)
            print(f"pick: {sid} ({BY_ID[sid]['label']})" if sid else "no pick yet")
    elif a.cmd == "check":
        failed = check(a.project, _ids(a.styles))
        sys.exit(1 if failed else 0)
    elif a.cmd == "snap":
        got = snap(a.project, _ids(a.styles), _times(a.at) if a.at else scene_times(a.project))
        sys.exit(0 if all(got.values()) else 1)
    elif a.cmd == "sheet":
        print(f"sheet: {sheet(a.project, _ids(a.styles), _times(a.at) if a.at else scene_times(a.project, 5))}")
    elif a.cmd == "list":
        for st in STYLES:
            print(f"{st['id']:10s} {st['label']:17s} {st['about']}  · good for {st['best']}")


if __name__ == "__main__":
    main()
