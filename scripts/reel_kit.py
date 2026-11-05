"""reel_kit — transitions, props and stock-B-roll beats on top of paper_reel (built for the "Make Money with AI
Tools" reel, Oct 2026). Import it from a project's build script; it re-exports the paper_reel library:

    import sys; from pathlib import Path
    sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "video-edit" / "scripts"))
    from reel_kit import *     # (video_kit re-exports all of this)
    configure(face_shift=380)   # px the footage is lifted inside the SPLIT face card (camera framing, pipeline.md §1)

Adds to paper_reel:
  layouts      lay, card_layer, fullv (scale keyframes), punch (snap zoom), wide, bv (full-bleed stock B-roll), split
               (face card as a clip-path layer that can rise / expand), depth (giant word behind the head)
  props        plate (paper caption plates that read on footage), scrim, stamp_c, chip_c, rail, receipt / receipt_scene
               (example slip that prints out of a slot and tears off), framed / phone_vid / win_vid / win (video props
               living in the scene body), ic / svg_inline (Lucide icons from assets/icons.json, ISC), logo, cursor_el
  transitions  face_rise, card_expand, whip_in / whip_out (motion blur), flip_in / flip_out (3D), zoom_through,
               paper_cover, plate_show, strike, stamp_in
  sound        premix_sfx(reel, project) mixes every cue into assets/sfx_mix.wav (one <audio> instead of hundreds)
Scene methods and helpers take GLOBAL seconds; JS lines are scene-local (s.L). Worked example: examples/scenes.py (through video_kit).
"""
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
import paper_reel as pr  # noqa: E402

INK, TEAL, TEAL_D, TEAL_T, GREY, LABEL = "#17140F", "#0B7A73", "#075450", "#D7ECE8", "#8F877B", "#746D62"
PAPER, CARDW, PANEL = "#F5F1EA", "#FFFDF9", "#ECE6DC"
ICONS = SKILL / "assets" / "icons"          # optional loose .svg folder (older layout)
ICONS_JSON = SKILL / "assets" / "icons.json"  # Lucide line icons packed into one file (ISC, assets/icons-LICENSE.txt)
_ICON_CACHE = {}
BV = "assets/bv/"                            # prepared B-roll clips inside the reel project

EXTRA_CSS = """
.pr-c{position:absolute;left:0;top:0;width:1080px;height:1920px}
.pr-fc{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;clip-path:inset(1000px 0px 0px 0px round 80px 80px 0px 0px)}
.pr-logo{position:absolute;object-fit:contain}
.pr-ic{position:absolute}
.pr-ic svg{display:block;width:100%;height:100%}
.pr-scrim{position:absolute;left:0;width:1080px}
.pr-ripple{position:absolute;width:120px;height:120px;border-radius:50%;border:6px solid #0B7A73;opacity:0}
.pr-stamp{position:absolute;padding:.08em .34em .04em;border:.1em solid #0B7A73;border-radius:.18em;color:#0B7A73;font-family:'Instrument Sans',sans-serif;font-weight:700;letter-spacing:.07em;line-height:1;white-space:nowrap;background:rgba(255,253,249,.82)}
.pl-row{position:absolute;left:0;width:1080px;text-align:center}
.pl{position:relative;display:inline-block;background:#F5F1EA;color:#17140F;border-radius:24px;padding:.04em .36em .12em;box-shadow:0 18px 44px rgba(20,15,10,.30);white-space:nowrap;line-height:1.06}
.pl.serif{font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;letter-spacing:-.02em}
.pl.sans{font-family:'Instrument Sans',sans-serif;font-weight:700;letter-spacing:-.02em;padding:.16em .5em .2em}
.pl.mono{font-family:'JetBrains Mono',monospace;font-weight:600;padding:.2em .6em}
.pl.ink{background:#17140F;color:#F5F1EA}
.pl.teal{background:#0B7A73;color:#FFFFFF}
.pl .g{color:#746D62}
.pl-strike{position:absolute;left:-3%;width:106%;top:52%;height:.14em;border-radius:.07em;background:#0B7A73}
.pr-fv{position:absolute;overflow:hidden;border-radius:34px;background:#1B1915;box-shadow:0 30px 70px rgba(40,30,20,.26)}
.pr-fv video{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.pr-fv.paperedge{border:10px solid #FFFDF9}
.pr-phone{position:absolute;border:13px solid #17140F;border-radius:58px;overflow:hidden;background:#17140F;box-shadow:0 30px 60px rgba(40,30,20,.28)}
.pr-phone video,.pr-phone img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.pr-win{position:absolute;background:#FFFFFF;border-radius:26px;overflow:hidden;box-shadow:0 30px 70px rgba(40,30,20,.24)}
.pr-win .wb{position:absolute;left:0;top:0;width:100%;height:50px;background:#EFE9E0}
.pr-win .wb i{position:absolute;top:18px;width:14px;height:14px;border-radius:50%;background:#CFC5B6}
.pr-win .wu{position:absolute;top:11px;left:104px;right:34px;height:28px;border-radius:14px;background:#FFFDF9;font-family:'JetBrains Mono',monospace;font-size:18px;line-height:28px;color:#746D62;padding-left:16px;white-space:nowrap;overflow:hidden}
.pr-win .wbody{position:absolute;left:0;top:50px;right:0;bottom:0;overflow:hidden}
.pr-win .wbody video,.pr-win .wbody img.fill{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.pr-slip{position:absolute;background:#FFFDF9;box-shadow:0 26px 60px rgba(40,30,20,.22);-webkit-mask:linear-gradient(#000,#000) top/100% calc(100% - 22px) no-repeat,conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) bottom/44px 22px repeat-x;mask:linear-gradient(#000,#000) top/100% calc(100% - 22px) no-repeat,conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) bottom/44px 22px repeat-x}
.pr-slip .sl{position:absolute;left:0;width:100%;text-align:center;font-family:'JetBrains Mono',monospace;font-weight:600;color:#746D62;letter-spacing:.24em;white-space:nowrap}
.pr-slip .sn{position:absolute;left:0;width:100%;text-align:center;font-family:'Instrument Serif',serif;font-style:italic;color:#17140F;letter-spacing:-.03em;line-height:1;white-space:nowrap}
.pr-slip .hr{position:absolute;left:48px;right:48px;height:0;border-top:4px dashed #D8CFC1}
.pr-slip .sr{position:absolute;left:48px;right:48px;height:56px;font-family:'JetBrains Mono',monospace;font-size:30px;line-height:56px;color:#17140F;white-space:nowrap}
.pr-slip .sr b{font-weight:700;color:#0B7A73}
.pr-slip .sr span{position:absolute;right:0;top:0;color:#17140F}
.pr-slot{position:absolute;background:#17140F;border-radius:25px;box-shadow:0 12px 26px rgba(20,15,10,.25)}
.pr-slot:after{content:"";position:absolute;left:34px;right:34px;top:30px;height:8px;border-radius:4px;background:#3A352E}
.pr-nw{position:relative;display:inline-block;background:#FFFDF9;border:5px dashed #BDB4A6;border-radius:999px;padding:.32em .9em .32em 2.3em;font-family:'JetBrains Mono',monospace;font-weight:600;color:#746D62;white-space:nowrap;box-shadow:0 16px 36px rgba(20,15,10,.22)}
.pr-nw .gi{position:absolute;left:.7em;top:.36em;width:1.2em;height:1.2em}
.pr-nw .gx{position:absolute;right:-.5em;top:-.55em;width:1.3em;height:1.3em;border-radius:50%;background:#0B7A73;color:#FFFFFF;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:.9em;line-height:1.3em;text-align:center}
.pr-rail{position:absolute;left:0;width:1080px;display:flex;justify-content:center;gap:18px}
.pr-rail span{display:inline-block;font-family:'JetBrains Mono',monospace;font-weight:600;font-size:34px;padding:.22em .62em;border-radius:999px;background:#FFFFFF;color:#17140F;border:3px solid #D8CFC1;white-space:nowrap;box-shadow:0 10px 26px rgba(20,15,10,.18)}
.pr-tile{position:absolute;background:#FFFDF9;border-radius:34px;box-shadow:0 20px 50px rgba(40,30,20,.16)}
.pr-tile .ti{position:absolute;left:50%;top:50%;width:84px;height:84px;margin:-42px 0 0 -42px}
.pr-tile .ti svg{display:block;width:100%;height:100%}
.pr-row{position:absolute;left:0;width:100%;border-top:2px solid #EEE7DC}
.pr-row .rl{position:absolute;left:112px;font-family:'Instrument Sans',sans-serif;font-weight:700;letter-spacing:-.015em;color:#17140F;white-space:nowrap}
.pr-row .rb{position:absolute;left:36px;width:52px;height:52px;border-radius:14px;border:4px solid #D8CFC1}
.pr-row .rk{position:absolute;left:36px;width:52px;height:52px;border-radius:14px;background:#0B7A73}
.pr-row .rk:after{content:"";position:absolute;left:17px;top:8px;width:11px;height:22px;border:solid #FFFFFF;border-width:0 6px 6px 0;transform:rotate(45deg)}
.pr-bubble{position:absolute;background:#FFFFFF;border-radius:40px;padding:.18em .55em;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:54px;color:#17140F;box-shadow:0 16px 36px rgba(20,15,10,.22);white-space:nowrap}
.pr-bubble:after{content:"";position:absolute;bottom:-18px;left:38px;border-top:24px solid #FFFFFF;border-right:22px solid transparent}
.pr-coin{position:absolute;width:86px;height:86px;border-radius:50%;background:#0B7A73;box-shadow:inset 0 -6px 0 #075450,0 10px 20px rgba(20,15,10,.22);color:#FFFFFF;font-family:'Instrument Serif',serif;font-style:italic;font-size:60px;line-height:80px;text-align:center}
"""

EXTRA_JS = r"""
const shake = (el, t, amp, n, d) => {
  amp = amp || 16; n = n || 7; d = d || 0.045;
  const k = [[1, -0.6], [-0.85, 0.9], [0.7, -0.45], [-0.55, 0.6], [0.35, -0.3], [-0.2, 0.15], [0.1, -0.1]];
  for (let i = 0; i < n; i++) { const f = 1 - i / n; tl.to(el, { x: k[i % 7][0] * amp * f, y: k[i % 7][1] * amp * f, duration: d, ease: "none" }, t + i * d); }
  tl.to(el, { x: 0, y: 0, duration: d, ease: "none" }, t + n * d);
};
const ripple = (el, t) => tl.fromTo(el, { opacity: 0.9, scale: 0.3 }, { opacity: 0, scale: 1.8, duration: 0.45, ease: "power2.out", immediateRender: false }, t);
const press = (el, t) => { tl.to(el, { scale: 0.9, duration: 0.07, ease: "power2.in" }, t); tl.to(el, { scale: 1, duration: 0.28, ease: "back.out(3)" }, t + 0.07); };
const whipIn = (el, t, dx, d) => tl.fromTo(el, { x: dx == null ? 620 : dx, filter: "blur(22px)" }, { x: 0, filter: "blur(0px)", duration: d || 0.26, ease: "power3.out" }, t);
const whipOut = (el, t, dx, d) => tl.fromTo(el, { x: 0, filter: "blur(0px)" }, { x: dx == null ? -620 : dx, filter: "blur(22px)", duration: d || 0.2, ease: "power2.in", immediateRender: false }, t);
const stampIn = (el, t, rot) => tl.fromTo(el, { opacity: 0, scale: 2.3, rotation: rot }, { opacity: 1, scale: 1, rotation: rot, duration: 0.2, ease: "expo.in" }, t - 0.2);
const tick = (el, t) => tl.fromTo(el, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, duration: 0.34, ease: "back.out(2.6)" }, t);
const showAt = (el, t0, t1) => { tl.set(el, { opacity: 1 }, t0); if (t1 != null) tl.set(el, { opacity: 0 }, t1); };
const lit = (el, t) => tl.to(el, { backgroundColor: "#0B7A73", borderColor: "#0B7A73", color: "#FFFFFF", duration: 0.18, ease: "power2.out" }, t);
"""

_BASE_CSS, _BASE_JS = pr.COMMON_CSS, pr.COMMON_JS
from paper_reel import A_TIGHT, A_WIDE, CURSOR_SVG, IMG, Reel, chip  # noqa: E402,F401


def J(s, line):
    s.js.append(line)


# ---------------------------------------------------------------- icons, logos, text helpers (HTML strings)
def svg_inline(name, color=INK, sw=2.0):
    """Lucide SVG sized to fill its container (the file's own width/height="24" would pin it at 24 px)."""
    if not _ICON_CACHE and ICONS_JSON.exists():
        import json
        _ICON_CACHE.update(json.loads(ICONS_JSON.read_text(encoding="utf-8")))
    if name in _ICON_CACHE:
        svg = _ICON_CACHE[name]
    else:
        svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
    svg = re.sub(r'\s*class="[^"]*"', "", svg)
    svg = re.sub(r'\swidth="24"', ' width="100%"', svg, count=1)
    svg = re.sub(r'\sheight="24"', ' height="100%"', svg, count=1)
    svg = svg.replace("<svg", '<svg style="display:block"', 1)
    return svg.replace('stroke="currentColor"', f'stroke="{color}"').replace('stroke-width="2"', f'stroke-width="{sw}"')


def ic(cid, name, x, y, size, color=INK, sw=2.0, style=""):
    """Lucide line icon (ISC), inlined so it can be coloured."""
    return (f'<div id="{cid}" class="pr-ic" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;{style}">'
            f'{svg_inline(name, color, sw)}</div>')


def logo(cid, name, x, y, w, h=None, style=""):
    return (f'<img id="{cid}" class="pr-logo" src="{IMG}logo-{name}.svg" alt="" '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h or w}px;{style}" />')


def chip_c(cid, text, top, size=64, kind="hero", style=""):
    cls = {"hero": "bx-chip", "alt": "bx-chip alt", "dark": "bx-chip dark"}[kind]
    return (f'<div style="position:absolute;left:0;width:1080px;top:{top}px;text-align:center">'
            f'<span id="{cid}" class="{cls}" style="position:relative;display:inline-block;font-size:{size}px;{style}">{text}</span></div>')


def plate(cid, text, top, size=104, kind="serif", tone="", strike=False):
    """A caption on a paper plate (for footage): reads on any background. strike=True adds a hidden teal strike line."""
    st = f'<i id="{cid}-x" class="pl-strike"></i>' if strike else ""
    return (f'<div class="pl-row" style="top:{top}px"><span id="{cid}" class="pl {kind} {tone}" '
            f'style="font-size:{size}px;opacity:0">{text}{st}</span></div>')


_SCRIMS = [0]


def scrim(cid, top=980, h=940, a=0.46):
    _SCRIMS[0] += 1                                   # a scene can carry several scrims: keep ids unique
    cid = f"{cid}{_SCRIMS[0]}"
    return (f'<div id="{cid}" class="pr-scrim" style="top:{top}px;height:{h}px;'
            f'background:linear-gradient(rgba(10,8,6,0),rgba(10,8,6,{a}) 55%,rgba(10,8,6,{a}))"></div>')


def stamp_c(cid, text, top, size=120, rot=-8, extra=""):
    return (f'<div style="position:absolute;left:0;width:1080px;top:{top}px;text-align:center">'
            f'<div id="{cid}" class="pr-stamp" style="position:relative;display:inline-block;font-size:{size}px;opacity:0;{extra}" '
            f'data-layout-allow-overlap data-layout-allow-occlusion>{text}</div></div>')


def rail(cid, labels, top):
    spans = "".join(f'<span id="{cid}-{i}">{t}</span>' for i, t in enumerate(labels))
    return f'<div id="{cid}" class="pr-rail" style="top:{top}px;opacity:0">{spans}</div>'


def cursor_el(cid, x, y, scale=1.0):
    w, h = round(54 * scale), round(80 * scale)
    svg = CURSOR_SVG.replace('width="54" height="80"', f'width="{w}" height="{h}"')
    return f'<div id="{cid}" class="bx-cursor" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{svg}</div>'


def paper_sheet(lx=-260, ly=-180, leaf_op=0.55):
    return ('<div class="bx-paper"></div><div class="bx-grain"></div>'
            f'<div class="bx-leaf" data-layout-allow-overflow style="left:{lx}px;top:{ly}px;opacity:{leaf_op}"></div>')


# ---------------------------------------------------------------- layers
STAGE_DY = 0                               # px the stage moves down; face_panel.use_panel() sets it


def lay(s, name, g0, g1, z, inner, paper=False, leaf=None):
    """A timed layer whose content sits in one wrapper ({sid}-{name}-c) so transitions can move it as a whole."""
    if STAGE_DY:                           # face panel on: the stage sits lower (face_panel.use_panel)
        inner = f'<div style="position:absolute;left:0;top:{STAGE_DY}px;width:1080px;height:1920px" data-layout-allow-overflow>{inner}</div>'
    s.layer(name, g0, g1, z, inner=f'<div id="{s.id(name)}-c" class="pr-c">{inner}</div>', paper=paper, leaf=leaf)
    return f"{s.id(name)}-c"


def card_layer(s, name, g0, g1, inner, z=1, lx=-260, ly=-180, leaf_op=0.55, dx=34, dy=22):
    """Full paper card whose paper AND content move together (wrapper {sid}-{name}-c) — for covers / tear-offs."""
    cid = s.id(name)
    s.layer(name, g0, g1, z, inner=(f'<div id="{cid}-c" class="pr-c">'
                                    f'<div class="bx-paper"></div><div class="bx-grain"></div>'
                                    f'<div id="{cid}-leaf" class="bx-leaf" data-layout-allow-overflow style="left:{lx}px;top:{ly}px;opacity:{leaf_op}"></div>'
                                    f'{inner}</div>'))
    J(s, f'drift($("{cid}-leaf"), {s.L(g0)}, {round(g1 - g0, 3)}, {dx}, {dy});')
    return f"{cid}-c"


def fullv(s, name, g0, g1, src=A_TIGHT, z=1, origin="540px 760px", keys=((0, 1.12, "power3.out"), (0.3, 1.03, "none"), (None, 1.07, None)),
          media_start=None):
    """Full-frame video with scale keyframes [(rel_t, scale, ease_into_next)]; rel None = end of the beat.
    Ids: {id} (outer, free to move), {id}-z (zoom)."""
    t0, d = s.L(g0), round(g1 - g0, 3)
    ms = g0 if media_start is None else media_start
    vid = (f'<video id="{s.id(name)}-v" class="clip bx-fillvid" src="{src}" data-start="{t0}" data-duration="{d}" '
           f'data-media-start="{ms}" data-track-index="{s.next_track()}" muted playsinline></video>')
    s.body.append(f'<div id="{s.id(name)}" class="bx-full" style="z-index:{z}">'
                  f'<div id="{s.id(name)}-z" class="bx-zoom" data-layout-allow-overflow>{vid}</div></div>')
    pts = [(t0 + (d if rt is None else rt), sc, ez) for rt, sc, ez in keys]
    zid = f"{s.id(name)}-z"
    J(s, f'tl.set($("{zid}"), {{ scale: {pts[0][1]}, transformOrigin: "{origin}" }}, {pts[0][0]});')
    for (ta, sa, ea), (tb, sb, _) in zip(pts, pts[1:]):
        J(s, f'tl.fromTo($("{zid}"), {{ scale: {sa}, transformOrigin: "{origin}" }}, {{ scale: {sb}, transformOrigin: "{origin}", '
             f'duration: {round(tb - ta, 3)}, ease: "{ea}", immediateRender: false }}, {round(ta, 3)});')
    return s.id(name)


def punch(s, name, g0, g1, snap=True, z1=1.07, z=1):
    keys = ((0, 1.14, "power3.out"), (0.3, 1.03, "none"), (None, z1, None)) if snap else ((0, 1.0, "none"), (None, 1.06, None))
    return fullv(s, name, g0, g1, A_TIGHT, z, keys=keys)


def wide(s, name, g0, g1, z=1, keys=((0, 1.12, "power3.out"), (0.3, 1.0, "none"), (None, 1.03, None))):
    return fullv(s, name, g0, g1, A_WIDE, z, keys=keys)


def bv(s, name, g0, g1, clip, z=1, keys=((0, 1.0, "none"), (None, 1.08, None)), media_start=0.0, origin="540px 960px"):
    """Full-bleed stock B-roll beat from assets/bv/<clip>.mp4 (media_start = seconds into the prepared clip)."""
    return fullv(s, name, g0, g1, f"{BV}{clip}.mp4", z, origin=origin, keys=keys, media_start=media_start)


FACE_TOP = 1000                            # card top on the canvas; FACE_SHIFT (footage lift) is set by configure()
CLIP_CARD = "inset(1000px 0px 0px 0px round 80px 80px 0px 0px)"
CLIP_FULL = "inset(0px 0px 0px 0px round 0px 0px 0px 0px)"


def facecard_c(s, name, g0, g1, zoom=1.0, origin="540px 780px", z=2, src=A_WIDE):
    """SPLIT speaker card as a full-frame layer revealed through a clip-path. Ids: {id} (clip + slide),
    {id}-m (footage offset), {id}-z (zoom; origin in footage px)."""
    cid = s.id(name)
    t0, d = s.L(g0), round(g1 - g0, 3)
    vid = (f'<video id="{cid}-v" class="clip bx-fillvid" src="{src}" data-start="{t0}" data-duration="{d}" '
           f'data-media-start="{g0}" data-track-index="{s.next_track()}" muted playsinline></video>')
    s.body.append(f'<div id="{cid}" class="pr-fc" style="z-index:{z}"><div id="{cid}-m" class="bx-zoom" data-layout-allow-overflow>'
                  f'<div id="{cid}-z" class="bx-zoom" data-layout-allow-overflow>{vid}</div></div></div>')
    J(s, f'tl.set($("{cid}-m"), {{ y: {FACE_TOP - FACE_SHIFT} }}, 0);')
    if zoom != 1.0:
        J(s, f'tl.set($("{cid}-z"), {{ scale: {zoom}, transformOrigin: "{origin}" }}, 0);')
    return cid


def split(s, name, g0, g1, zoom=1.0, leaf=0.3, rise=True):
    s.paper(f"{name}-bg", g0, g1, leaf_op=leaf)
    face = facecard_c(s, f"{name}-face", g0, g1, zoom=zoom)
    if rise:
        face_rise(s, face, g0)
    return face


def depth(s, name, g0, g1, word, matte, matte_t0, size, top, keys, origin="540px 760px", word_cls="bx-ink"):
    """DEPTH: base video -> giant word -> background-removed matte (same zoom keys)."""
    fullv(s, f"{name}-base", g0, g1, A_WIDE, 1, origin=origin, keys=keys)
    s.layer(f"{name}-word", g0, g1, 2, inner=f'<div id="{s.id(name)}-big" class="bx-serif bx-row {word_cls}" '
                                              f'style="top:{top}px;font-size:{size}px;opacity:0" data-layout-allow-overflow>{word}</div>')
    fullv(s, f"{name}-matte", g0, g1, matte, 3, origin=origin, keys=keys, media_start=round(g0 - matte_t0, 3))
    return f"{s.id(name)}-big"


# ---------------------------------------------------------------- video props living in the scene body
def _vid(cid, src, s, g0, g1, media_start):
    t0, d = s.L(g0), round(g1 - g0, 3)
    return (f'<video id="{cid}-v" class="clip" src="{src}" data-start="{t0}" data-duration="{d}" data-media-start="{media_start}" '
            f'data-track-index="{s.next_track()}" muted playsinline></video>')


def framed(s, name, g0, g1, clip, x, y, w, h, z=3, media_start=0.0, radius=34, extra_cls="", inner=""):
    """A rounded frame with a stock clip inside. Shown at g0, hidden at g1 (animate the frame id for entrances)."""
    y += STAGE_DY
    cid = s.id(name)
    s.body.append(f'<div id="{cid}" class="pr-fv {extra_cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                  f'border-radius:{radius}px;z-index:{z};opacity:0">{_vid(cid, BV + clip + ".mp4", s, g0, g1, media_start)}{inner}</div>')
    J(s, f'showAt($("{cid}"), {s.L(g0)}, {s.L(g1)});')
    return cid


def phone_vid(s, name, g0, g1, clip, x, y, w, h, z=3, media_start=0.0, inner=""):
    y += STAGE_DY
    cid = s.id(name)
    s.body.append(f'<div id="{cid}" class="pr-phone" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;z-index:{z};opacity:0">'
                  f'{_vid(cid, BV + clip + ".mp4", s, g0, g1, media_start)}{inner}<div class="bx-isl"></div></div>')
    J(s, f'showAt($("{cid}"), {s.L(g0)}, {s.L(g1)});')
    return cid


def win_vid(s, name, g0, g1, src, x, y, w, h, z=3, media_start=0.0, url="", inner=""):
    """Browser window with a video body (src is a full asset path)."""
    y += STAGE_DY
    cid = s.id(name)
    s.body.append(f'<div id="{cid}" class="pr-win" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;z-index:{z};opacity:0">'
                  f'<div class="wb"><i style="left:20px"></i><i style="left:44px"></i><i style="left:68px"></i><div class="wu">{url}</div></div>'
                  f'<div class="wbody">{_vid(cid, src, s, g0, g1, media_start)}{inner}</div></div>')
    J(s, f'showAt($("{cid}"), {s.L(g0)}, {s.L(g1)});')
    return cid


def win(cid, x, y, w, h, body, url="", style=""):
    """Static browser window (HTML string) around arbitrary body HTML."""
    return (f'<div id="{cid}" class="pr-win" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">'
            f'<div class="wb"><i style="left:20px"></i><i style="left:44px"></i><i style="left:68px"></i><div class="wu">{url}</div></div>'
            f'<div class="wbody">{body}</div></div>')


# ---------------------------------------------------------------- the example receipt slip
def receipt(cid, n, rows, x=220, y=500, w=640):
    """Receipt slip under a printer slot: EXAMPLE / big number / of 04 / dashed rule / rows. rows=[(KEY, value)]."""
    h = 640 + 66 * len(rows)
    rr = "".join(f'<div class="sr" style="top:{560 + 66 * i}px"><b>{k}</b><span>{v}</span></div>' for i, (k, v) in enumerate(rows))
    return (f'<div id="{cid}" class="pr-slip" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="sl" style="top:56px;font-size:30px" data-layout-allow-overlap>EXAMPLE</div>'
            f'<div class="sn" style="top:106px;font-size:320px" data-layout-allow-overlap>{n:02d}</div>'
            f'<div class="sl" style="top:440px;font-size:28px" data-layout-allow-overlap>OF 04</div>'
            f'<div class="hr" style="top:510px"></div>{rr}'
            f'<div class="hr" style="top:{560 + 66 * len(rows) + 14}px"></div></div>'
            f'<div id="{cid}-slot" class="pr-slot" style="left:{x - 50}px;top:{y - 36}px;width:{w + 100}px;height:50px"></div>')


def receipt_scene(s, name, g0, g_tear, n, rows, z=50):
    """Paper card + slip that prints out of a slot (clip reveal, printer steps) and tears off upward at g_tear,
    revealing what is underneath (anything already playing below this layer). Returns the card wrapper id."""
    cid = s.id(name)
    wrap = card_layer(s, name, g0, round(g_tear + 0.26, 3), receipt(f"{cid}-slip", n, rows), z=z, leaf_op=0.5)
    t = s.L(g0)
    J(s, f'tl.fromTo($("{cid}-slip-slot"), {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.18, ease: "power2.out" }}, {t});')
    J(s, f'tl.fromTo($("{cid}-slip"), {{ clipPath: "inset(0% 0% 100% 0%)", y: -60 }}, {{ clipPath: "inset(0% 0% 0% 0%)", y: 0, duration: 0.34, ease: "steps(8)" }}, {round(t + 0.12, 3)});')
    tt = s.L(g_tear)
    J(s, f'tl.to($("{cid}-slip"), {{ y: -1500, rotation: -9, duration: 0.24, ease: "power2.in" }}, {tt});')
    J(s, f'tl.to($("{wrap}"), {{ y: -1960, duration: 0.24, ease: "power3.in" }}, {round(tt + 0.02, 3)});')
    return wrap


# ---------------------------------------------------------------- transitions
def face_rise(s, face, g, d=0.36):
    J(s, f'tl.fromTo($("{face}"), {{ y: 940 }}, {{ y: 0, duration: {d}, ease: "power3.out" }}, {s.L(g)});')


def card_expand(s, face, g_end, d=0.28):
    """SPLIT → PUNCH / FULL: the speaker card opens up to full frame just before the cut."""
    t = round(s.L(g_end) - d - 0.04, 3)
    J(s, f'tl.fromTo($("{face}"), {{ clipPath: "{CLIP_CARD}" }}, {{ clipPath: "{CLIP_FULL}", duration: {d}, ease: "power3.in", immediateRender: false }}, {t});')
    J(s, f'tl.fromTo($("{face}-m"), {{ y: {FACE_TOP - FACE_SHIFT} }}, {{ y: 0, duration: {d}, ease: "power3.in", immediateRender: false }}, {t});')


def whip_out(s, el, g_end, d=0.18, dx=-620):
    J(s, f'whipOut($("{el}"), {round(s.L(g_end) - d, 3)}, {dx}, {d});')


def whip_in(s, el, g, d=0.26, dx=620):
    J(s, f'whipIn($("{el}"), {s.L(g)}, {dx}, {d});')


def paper_cover(s, name, g_end, d=0.3, lx=-260, ly=-180, leaf_op=0.55):
    """A paper sheet slides up over the frame and covers it at the cut (match the next CARD's paper)."""
    g0 = round(g_end - d - 0.04, 3)
    s.layer(name, g0, g_end, 40, inner=f'<div id="{s.id(name)}-sh" class="pr-c" style="box-shadow:0 -40px 70px rgba(40,30,20,.22)">{paper_sheet(lx, ly, leaf_op)}</div>')
    J(s, f'tl.fromTo($("{s.id(name)}-sh"), {{ y: 1960 }}, {{ y: 0, duration: {d}, ease: "power3.in" }}, {s.L(g0)});')


def flip_out(s, el, g_end, d=0.16):
    J(s, f'tl.fromTo($("{el}"), {{ rotationY: 0, transformPerspective: 1600 }}, {{ rotationY: 88, transformPerspective: 1600, duration: {d}, ease: "power2.in", immediateRender: false }}, {round(s.L(g_end) - d, 3)});')


def flip_in(s, el, g, d=0.22):
    J(s, f'tl.fromTo($("{el}"), {{ rotationY: -88, transformPerspective: 1600 }}, {{ rotationY: 0, transformPerspective: 1600, duration: {d}, ease: "power2.out" }}, {s.L(g)});')


def zoom_through(s, el, g_end, d=0.16, scale=1.7):
    """Push the outgoing picture past the camera (scale up + blur + fade) right before the cut."""
    J(s, f'tl.fromTo($("{el}"), {{ scale: 1, opacity: 1, filter: "blur(0px)" }}, {{ scale: {scale}, opacity: 0, filter: "blur(14px)", duration: {d}, ease: "power2.in", immediateRender: false }}, {round(s.L(g_end) - d, 3)});')


def plate_show(s, cid, g0, g1=None, how="rise"):
    t0 = s.L(g0)
    if how == "pop":
        J(s, f'pop($("{cid}"), {t0}, {{ s: 0.6, d: 0.34 }});')
    elif how == "slam":
        J(s, f'slam($("{cid}"), {t0}, {{ s: 1.25, d: 0.26 }});')
    else:
        J(s, f'tl.fromTo($("{cid}"), {{ opacity: 0, y: 26, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.2, ease: "power2.out" }}, {t0});')
    if g1 is not None:
        J(s, f'tl.set($("{cid}"), {{ opacity: 0 }}, {s.L(g1)});')


def strike(s, cid, g, d=0.26):
    J(s, f'tl.fromTo($("{cid}-x"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: {d}, ease: "power2.out" }}, {s.L(g)});')


def stamp_in(s, cid, g, rot=-8):
    J(s, f'stampIn($("{cid}"), {s.L(g)}, {rot});')


# ---------------------------------------------------------------- sound: pre-mix every cue into one track
def premix_sfx(reel, project, sr=48000):
    """Mix reel.cues into assets/sfx_mix.wav and replace the per-cue <audio> tags in index.html with one track
    (hundreds of separate tracks overflow the renderer's audio command line on Windows: spawn ENAMETOOLONG)."""
    import subprocess
    import numpy as np
    project = Path(project)
    n = int(round(sr * reel.total))
    mix = np.zeros((n, 2), dtype=np.float32)
    cache = {}
    for t, f, vol, dur in reel.cues:
        if f not in cache:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(project / "assets" / "sfx" / f), "-f", "f32le", "-ac", "2",
                                  "-ar", str(sr), "-"], capture_output=True, check=True).stdout
            cache[f] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
        x = cache[f]
        if dur:                                          # data-duration cut, with a 30 ms fade so it doesn't click
            x = x[:int(dur * sr)].copy()
            k = min(int(0.03 * sr), len(x))
            x[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
        i = int(round(t * sr))
        m = min(len(x), n - i)
        if m > 0:
            mix[i:i + m] += np.float32(vol) * x[:m]
    out = project / "assets" / "sfx_mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", "-", "-c:a", "pcm_f32le", str(out)],
                   input=mix.tobytes(), check=True)
    html = (project / "index.html").read_text(encoding="utf-8")
    html = re.sub(r'<audio id="sfx-\d+"[^>]*></audio>\n', "", html)
    tag = (f'<audio id="sfx-mix" src="assets/sfx_mix.wav" data-start="0" data-duration="{reel.total}" data-track-index="20" '
           f'data-volume="1" data-audio-group="sfx"></audio>\n')
    html = html.replace("</div>\n<script>", tag + "</div>\n<script>", 1)
    (project / "index.html").write_text(html, encoding="utf-8")
    return f"sfx mix: {len(reel.cues)} cues, peak {float(np.abs(mix).max()):.2f} -> {out.name}"


# ---------------------------------------------------------------- setup
def configure(face_shift=380):
    """Install the kit's CSS / JS into every scene the library writes, and set how far the footage is lifted inside the
    SPLIT face card. It depends on the camera framing: Brag reel 280, App Store reel 358, Make Money reel 380."""
    global FACE_SHIFT
    FACE_SHIFT = face_shift
    pr.COMMON_CSS = _BASE_CSS + f"\n.bx-cardvid{{top:-{face_shift}px}}" + EXTRA_CSS
    pr.COMMON_JS = _BASE_JS + EXTRA_JS


configure()
