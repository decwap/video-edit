"""paper_reel - composition library for the Paper Reel talking-head style (HyperFrames).

Import it from a project's build script, declare scenes on a Reel, then reel.write(project_dir):

    import sys; sys.path.insert(0, r"<skill>/scripts")
    from paper_reel import *
    reel = Reel(total=66.6, fps=25, voice_dur=65.4)
    s = reel.scene("f01", "hook", 0.00, 4.24)        # global start/end seconds on the tightened timeline
    s.paper("a-bg", 0.00, 2.32, leaf_op=0.35)          # timed paper layer (+grain, drifting leaf)
    s.facecard("a-face", 0.00, 2.32)                   # SPLIT speaker card (aroll_wide; media start = global time)
    s.layer("a-over", 0.00, 2.32, 3, inner=phone("f01-phone", 150, 140, 330, 684, IMG + "screen.jpg")
            + s.seam_caps([("If you've", 0.00, 0.48), ("built", 0.48, 0.88)]))
    s.js.append('tl.fromTo($("f01-phone"), {opacity:0, y:260}, {opacity:1, y:0, duration:.6, ease:"back.out(1.4)"}, 0.36);')
    reel.cue(0.38, "sparkle-1", 0.55)                  # sounds from assets/sfx/ (references/sound.md)
    reel.ting(2.32)                                    # cut into a new section: rotating glassy ting
    print(reel.write("path/to/project"))               # compositions/*.html + index.html (voice + cues)

Scene methods take GLOBAL seconds; JS lines use scene-local seconds (convert with s.L(global)).
Ids must be unique across the assembled page: prefix every id with the scene id (s.id("name")).
JS helpers available inside every scene: $, show, rise, pop, slam, drift, typeIn, blink (see COMMON_JS).
"""
from pathlib import Path

A_WIDE, A_TIGHT, INSERT = "assets/aroll_wide.mp4", "assets/aroll_tight.mp4", "assets/insert.mp4"
IMG = "assets/img/"
SFX_DIR = "assets/sfx/"

FONTS = """
@font-face{font-family:'Instrument Serif';font-style:italic;font-weight:400;src:url(assets/fonts/InstrumentSerif-Italic.woff2) format('woff2')}
@font-face{font-family:'Instrument Serif';font-style:normal;font-weight:400;src:url(assets/fonts/InstrumentSerif-Regular.woff2) format('woff2')}
@font-face{font-family:'Instrument Sans';font-style:normal;font-weight:400 700;src:url(assets/fonts/InstrumentSans-var.woff2) format('woff2')}
@font-face{font-family:'JetBrains Mono';font-style:normal;font-weight:400 700;src:url(assets/fonts/JetBrainsMono-var.woff2) format('woff2')}
"""

COMMON_CSS = """
.bx-layer{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden}
.bx-paper{position:absolute;left:0;top:0;width:1080px;height:1920px;background:#F5F1EA}
.bx-grain{position:absolute;left:0;top:0;width:1080px;height:1920px;background:url(assets/img/paper-grain.png) center/cover;mix-blend-mode:soft-light;opacity:.55}
.bx-leaf{position:absolute;width:1500px;height:2600px;background:url(assets/img/leaf-shadow.png) 0 0/100% 100% no-repeat;mix-blend-mode:multiply}
.bx-facecard{position:absolute;left:0;top:1000px;width:1080px;height:920px;border-radius:80px 80px 0 0;overflow:hidden}
.bx-zoom{position:absolute;left:0;top:0;width:1080px;height:1920px}
.bx-cardvid{position:absolute;left:0;top:-280px;width:1080px;height:1920px;object-fit:cover}
.bx-full{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden}
.bx-fillvid{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover}
.bx-cap{position:absolute;left:60px;width:960px;top:872px;text-align:center;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:78px;letter-spacing:-.02em;line-height:1.1;color:#17140F;white-space:nowrap;opacity:0}
.bx-pserif{position:absolute;left:40px;width:1000px;text-align:center;font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;font-size:124px;line-height:1;color:#FFF8EF;text-shadow:0 4px 28px rgba(0,0,0,.5);white-space:nowrap;opacity:0}
.bx-psans{position:absolute;left:40px;width:1000px;text-align:center;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:92px;letter-spacing:-.025em;line-height:1.05;color:#FFF8EF;text-shadow:0 4px 28px rgba(0,0,0,.5);white-space:nowrap;opacity:0}
.bx-serif{position:absolute;font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;letter-spacing:-.02em;line-height:.95;white-space:nowrap}
.bx-sans{position:absolute;font-family:'Instrument Sans',sans-serif;font-weight:700;letter-spacing:-.02em;white-space:nowrap}
.bx-mono{position:absolute;font-family:'JetBrains Mono',monospace;white-space:nowrap}
.bx-row{left:0;width:1080px;text-align:center}
.bx-ink{color:#17140F}.bx-grey{color:#8F877B}.bx-coral{color:#0B7A73}
.bx-white{color:#FFF8EF;text-shadow:0 4px 26px rgba(0,0,0,.55)}
.bx-chip{position:absolute;font-family:'JetBrains Mono',monospace;font-weight:600;background:#0B7A73;color:#FFFFFF;border-radius:999px;padding:.2em .6em;white-space:nowrap;line-height:1.15}
.bx-chip.alt{background:#FFFFFF;color:#17140F;border:3px solid #D8CFC1}
.bx-chip.dark{background:#17140F;color:#F5F1EA}
.bx-card{position:absolute;background:#FFFDF9;border-radius:32px;box-shadow:0 20px 50px rgba(40,30,20,.14)}
.bx-browser{position:absolute;background:#FFFFFF;border-radius:26px;overflow:hidden;box-shadow:0 30px 70px rgba(40,30,20,.24)}
.bx-bbar{position:absolute;left:0;top:0;width:100%;height:46px;background:#EFE9E0}
.bx-bbar i{position:absolute;top:16px;width:14px;height:14px;border-radius:50%;background:#CFC5B6}
.bx-bbar b{position:absolute;top:10px;left:120px;width:42%;height:26px;border-radius:13px;background:#FFFDF9}
.bx-bbody{position:absolute;left:0;top:46px;width:100%;bottom:0;background-size:cover;background-position:center;overflow:hidden}
.bx-bvid{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.bx-phone{position:absolute;border:13px solid #17140F;border-radius:58px;overflow:hidden;background:#FFFFFF;box-shadow:0 30px 60px rgba(40,30,20,.28)}
.bx-phone img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.bx-isl{position:absolute;top:12px;left:50%;width:96px;height:26px;margin-left:-48px;border-radius:14px;background:#17140F}
.bx-term{position:absolute;background:#1B1915;border-radius:28px;overflow:hidden;box-shadow:0 30px 70px rgba(20,15,10,.35)}
.bx-tbar{position:absolute;left:0;top:0;width:100%;height:64px;border-bottom:2px solid #2C2925}
.bx-tbar i{position:absolute;top:23px;width:18px;height:18px;border-radius:50%}
.bx-tbar span{position:absolute;left:0;width:100%;top:18px;text-align:center;font-family:'JetBrains Mono',monospace;font-size:24px;color:#8E877C}
.bx-tl{position:absolute;left:44px;font-family:'JetBrains Mono',monospace;font-size:40px;line-height:1.2;color:#EDE6DA;white-space:nowrap}
.bx-caret{display:inline-block;width:.55em;height:1.05em;background:#0B7A73;vertical-align:-.15em;margin-left:.08em}
.bx-cursor{position:absolute;width:54px;height:80px}
.bx-frame{position:absolute;background-size:cover;background-position:center;border-radius:28px;box-shadow:0 30px 70px rgba(40,30,20,.25);overflow:hidden}
.bx-play{position:absolute;width:150px;height:150px;border-radius:50%;background:rgba(255,253,249,.94)}
.bx-play:after{content:"";position:absolute;left:58px;top:44px;border-left:48px solid #17140F;border-top:31px solid transparent;border-bottom:31px solid transparent}
.bx-check{position:absolute;width:64px;height:64px;border-radius:50%;background:#0B7A73}
.bx-check:after{content:"";position:absolute;left:22px;top:13px;width:14px;height:27px;border:solid #FFFFFF;border-width:0 7px 7px 0;transform:rotate(45deg)}
"""

COMMON_JS = r"""
const $ = (id) => document.getElementById(id);
const show = (el, t0, t1, o) => {
  o = Object.assign({ y: 16, s: 0.94, d: 0.16 }, o || {});
  tl.fromTo(el, { opacity: 0, y: o.y, scale: o.s }, { opacity: 1, y: 0, scale: 1, duration: o.d, ease: "power2.out" }, t0);
  if (t1 != null) tl.set(el, { opacity: 0 }, t1);
};
const rise = (el, t, o) => {
  o = Object.assign({ y: 70, d: 0.5, ease: "power3.out", rot: 0, x: 0 }, o || {});
  tl.fromTo(el, { opacity: 0, y: o.y, x: o.x, rotation: o.rot }, { opacity: 1, y: 0, x: 0, rotation: o.rot, duration: o.d, ease: o.ease }, t);
};
const pop = (el, t, o) => {
  o = Object.assign({ s: 0.55, d: 0.45, ease: "back.out(1.8)", rot: 0 }, o || {});
  tl.fromTo(el, { opacity: 0, scale: o.s, rotation: o.rot }, { opacity: 1, scale: 1, rotation: o.rot, duration: o.d, ease: o.ease }, t);
};
const slam = (el, t, o) => {
  o = Object.assign({ s: 1.35, d: 0.26 }, o || {});
  tl.fromTo(el, { opacity: 0, scale: o.s }, { opacity: 1, scale: 1, duration: o.d, ease: "expo.out" }, t);
};
const drift = (el, t0, d, dx, dy) => tl.fromTo(el, { x: 0, y: 0 }, { x: dx, y: dy, duration: d, ease: "none" }, t0);
const typeIn = (el, text, t, d) => {
  const p = { n: 0 };
  el.textContent = "";
  tl.to(p, { n: text.length, duration: d, ease: "none", onUpdate: () => { el.textContent = text.slice(0, Math.round(p.n)); } }, t);
};
const blink = (el, t, n) => tl.fromTo(el, { opacity: 1 }, { opacity: 0, duration: 0.24, ease: "steps(1)", repeat: n, yoyo: true }, t);
"""

CURSOR_SVG = ('<svg viewBox="0 0 54 80" width="54" height="80"><path d="M2 2 L2 66 L18 52 L29 76 L40 71 L29 47 L50 46 Z" '
              'fill="#17140F" stroke="#F5F1EA" stroke-width="3"/></svg>')


class Scene:
    def __init__(self, sid, slug, start, dur):
        self.sid, self.slug, self.start, self.dur = sid, slug, start, dur
        self.body, self.css, self.js = [], [], []
        self.track = 0

    def L(self, g):
        return round(g - self.start, 3)

    def id(self, name):
        return f"{self.sid}-{name}"

    def next_track(self):
        self.track += 1
        return self.track

    # ---------- layers ----------
    def layer(self, name, g0, g1, z, inner="", paper=False, leaf=None):
        """A timed full-frame layer. leaf=(op, x, y, dx, dy) adds the drifting leaf shadow."""
        t0, d = self.L(g0), round(g1 - g0, 3)
        parts = []
        if paper:
            parts.append('<div class="bx-paper"></div><div class="bx-grain"></div>')
        if leaf:
            op, lx, ly, dx, dy = leaf
            parts.append(f'<div id="{self.id(name)}-leaf" class="bx-leaf" data-layout-allow-overflow style="left:{lx}px;top:{ly}px;opacity:{op}"></div>')
            self.js.append(f'drift($("{self.id(name)}-leaf"), {t0}, {d}, {dx}, {dy});')
        parts.append(inner)
        self.body.append(f'<div id="{self.id(name)}" class="clip bx-layer" data-start="{t0}" data-duration="{d}" '
                         f'data-track-index="{self.next_track()}" style="z-index:{z}">{"".join(parts)}</div>')

    def paper(self, name, g0, g1, leaf_op=0.55, lx=-260, ly=-180, dx=34, dy=22, z=1, inner=""):
        self.layer(name, g0, g1, z, inner=inner, paper=True, leaf=(leaf_op, lx, ly, dx, dy))

    def facecard(self, name, g0, g1, zoom=1.0, origin="520px 420px", z=2, src=A_WIDE):
        t0, d = self.L(g0), round(g1 - g0, 3)
        vid = (f'<video id="{self.id(name)}-v" class="clip bx-cardvid" src="{src}" data-start="{t0}" data-duration="{d}" '
               f'data-media-start="{g0}" data-track-index="{self.next_track()}" muted playsinline></video>')
        self.body.append(f'<div id="{self.id(name)}" class="bx-facecard" style="z-index:{z}">'
                         f'<div id="{self.id(name)}-z" class="bx-zoom" data-layout-allow-overflow>{vid}</div></div>')
        if zoom != 1.0:
            self.js.append(f'tl.set($("{self.id(name)}-z"), {{ scale: {zoom}, transformOrigin: "{origin}" }}, 0);')

    def fullvid(self, name, g0, g1, src, media_start, z, zoom=(1.0, 1.0), origin="540px 760px", ease="none"):
        t0, d = self.L(g0), round(g1 - g0, 3)
        vid = (f'<video id="{self.id(name)}-v" class="clip bx-fillvid" src="{src}" data-start="{t0}" data-duration="{d}" '
               f'data-media-start="{media_start}" data-track-index="{self.next_track()}" muted playsinline></video>')
        self.body.append(f'<div id="{self.id(name)}" class="bx-full" style="z-index:{z}">'
                         f'<div id="{self.id(name)}-z" class="bx-zoom" data-layout-allow-overflow>{vid}</div></div>')
        z0, z1 = zoom
        self.js.append(f'tl.fromTo($("{self.id(name)}-z"), {{ scale: {z0}, transformOrigin: "{origin}" }}, '
                       f'{{ scale: {z1}, transformOrigin: "{origin}", duration: {d}, ease: "{ease}" }}, {t0});')

    # ---------- captions ----------
    def seam_caps(self, cues):
        """cues: [(text, g0, g1)] — bold sans captions on the SPLIT seam."""
        out = []
        for i, (text, g0, g1) in enumerate(cues):
            cid = f"cap{len(self.js)}x{i}"
            out.append(f'<div id="{self.id(cid)}" class="bx-cap">{text}</div>')
            self.js.append(f'show($("{self.id(cid)}"), {self.L(g0)}, {self.L(g1)});')
        return "".join(out)

    def pcap(self, text, g0, g1, top, kind="sans", size=None):
        cls = "bx-pserif" if kind == "serif" else "bx-psans"
        cid = f"pc{len(self.js)}"
        st = f"top:{top}px;" + (f"font-size:{size}px;" if size else "")
        self.js.append(f'show($("{self.id(cid)}"), {self.L(g0)}, {None if g1 is None else self.L(g1)});'.replace("None", "null"))
        return f'<div id="{self.id(cid)}" class="{cls}" style="{st}">{text}</div>'

    # ---------- output ----------
    def write(self, comp_dir):
        root = f"{self.sid}-root"
        css = FONTS + f"#{root}{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;background:#F5F1EA;font-family:'Instrument Sans',sans-serif}}" + COMMON_CSS + "".join(self.css)
        js = "\n".join(self.js)
        html = f"""<!doctype html>
<html lang="en">
<head><meta charset="UTF-8" /><title>{self.sid} {self.slug}</title></head>
<body>
<template>
<style>{css}</style>
<div id="{root}" data-composition-id="{self.sid}" data-width="1080" data-height="1920">
{chr(10).join(self.body)}
</div>
<script>
(() => {{
const tl = gsap.timeline({{ paused: true }});
{COMMON_JS}
{js}
window.__timelines["{self.sid}"] = tl;
}})();
</script>
</template>
</body>
</html>
"""
        (Path(comp_dir) / f"{self.sid}-{self.slug}.html").write_text(html, encoding="utf-8")
        return f"compositions/{self.sid}-{self.slug}.html"




# ---------------------------------------------------------------- props (return HTML strings)
def chip(cid, text, x, y, size=58, kind="hero", style=""):
    """kind: hero (teal), alt (quiet white label), dark (result chip)."""
    k = {"hero": "bx-chip", "alt": "bx-chip alt", "dark": "bx-chip dark"}[kind]
    return f'<div id="{cid}" class="{k}" style="left:{x}px;top:{y}px;font-size:{size}px;{style}">{text}</div>'


def serif_row(cid, text, top, size, color="ink", extra=""):
    return f'<div id="{cid}" class="bx-serif bx-row bx-{color}" style="top:{top}px;font-size:{size}px" {extra}>{text}</div>'


def sans_row(cid, text, top, size, color="ink", extra=""):
    return f'<div id="{cid}" class="bx-sans bx-row bx-{color}" style="top:{top}px;font-size:{size}px" {extra}>{text}</div>'


def phone(cid, x, y, w, h, img):
    return (f'<div id="{cid}" class="bx-phone" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<img src="{img}" alt="" /><div class="bx-isl"></div></div>')


def browser(cid, x, y, w, h, img=None, video=None):
    """video: dict(id, src, start, dur, media_start[, track]) with a scene-local start; img: background image."""
    body = '<div class="bx-bbody"' + (f' style="background-image:url({img})"' if img else "") + ">"
    if video:
        body += (f'<video id="{video["id"]}" class="clip bx-bvid" src="{video["src"]}" data-start="{video["start"]}" '
                 f'data-duration="{video["dur"]}" data-media-start="{video["media_start"]}" '
                 f'data-track-index="{video.get("track", 9)}" muted playsinline></video>')
    body += "</div>"
    return (f'<div id="{cid}" class="bx-browser" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            '<div class="bx-bbar"><i style="left:20px"></i><i style="left:44px"></i><i style="left:68px"></i><b></b></div>'
            f'{body}</div>')


def terminal(cid, lines_html, title="Terminal", x=80, y=170, w=920, h=600):
    """lines_html: rows like '<div class="bx-tl" style="top:110px">...</div>' (70 px apart)."""
    return (f'<div id="{cid}" class="bx-term" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            '<div class="bx-tbar"><i style="left:26px;background:#E06C55"></i><i style="left:56px;background:#E3B341"></i>'
            f'<i style="left:86px;background:#6CB27A"></i><span>{title}</span></div>' + lines_html + '</div>')


def frame(cid, x, y, w, h, img, play=False):
    p = f'<div id="{cid}-play" class="bx-play" style="right:36px;bottom:36px"></div>' if play else ""
    return (f'<div id="{cid}" class="bx-frame" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'background-image:url({img})">{p}</div>')


def check(cid, x, y):
    return f'<div id="{cid}" class="bx-check" style="left:{x}px;top:{y}px"></div>'


def teaser_card(cid, n, x, y, w, h, inner, blur=20, accent="#0B7A73", rot=0):
    """Blurred list-preview card (retention): content under a blur, crisp number badge + lock on top.
    Animate entry with e.g. tl.fromTo($(cid + "-bl"), {filter:"blur(30px)"}, {filter:"blur(20px)"}) — never clear it;
    the chapter cards reveal the items. Ids: {cid}, {cid}-bl (blurred content), {cid}-n (badge)."""
    lock = ('<svg viewBox="0 0 24 24" width="100%" height="100%" fill="none" stroke="#17140F" stroke-width="2.4" '
            'stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2"/>'
            '<path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>')
    return (f'<div id="{cid}" class="bx-card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)">'
            f'<div id="{cid}-bl" style="position:absolute;left:0;top:0;width:100%;height:100%;filter:blur({blur}px)">{inner}</div>'
            f'<div id="{cid}-n" class="bx-chip" style="left:{w // 2 - 50}px;top:-30px;width:100px;text-align:center;font-size:40px;'
            f'background:{accent}" data-layout-allow-overlap>{n:02d}</div>'
            f'<div style="position:absolute;left:{w // 2 - 36}px;top:{h // 2 - 50}px;width:72px;height:72px">{lock}</div></div>')


def cursor(cid, x, y):
    return f'<div id="{cid}" class="bx-cursor" style="left:{x}px;top:{y}px">{CURSOR_SVG}</div>'


# ---------------------------------------------------------------- the reel: scenes + sound cues + root
class Reel:
    def __init__(self, total, fps=25, voice="assets/voice.wav", voice_dur=None):
        self.total, self.fps, self.voice, self.voice_dur = total, fps, voice, voice_dur or total
        self.scenes, self.cues = [], []
        self._ting = 0

    def scene(self, sid, slug, start, end):
        s = Scene(sid, slug, start, round(end - start, 3))
        self.scenes.append(s)
        return s

    def cue(self, t, name, vol=0.4, dur=None):
        """name: a file in assets/sfx/; '.wav' is added when no extension is given ('sparkle-1')."""
        f = name if "." in name else f"{name}.wav"
        self.cues.append((round(t, 3), f, vol, dur))

    def ting(self, t, vol=0.32):
        """A cut into a punch-in or new section: rotate ting-1..5 so the cuts form a melody."""
        self._ting = self._ting % 5 + 1
        self.cue(t, f"ting-{self._ting}", vol)

    def write(self, project):
        project = Path(project)
        comp = project / "compositions"
        comp.mkdir(parents=True, exist_ok=True)
        hosts = []
        for sc in self.scenes:
            path = sc.write(comp)
            hosts.append(f'<div id="el-{sc.sid}" data-composition-id="{sc.sid}" data-composition-src="{path}" '
                         f'data-start="{sc.start}" data-duration="{sc.dur}" data-track-index="1" '
                         f'data-width="1080" data-height="1920"></div>')
        audio = [f'<audio id="voice" src="{self.voice}" data-start="0" data-duration="{self.voice_dur}" '
                 f'data-track-index="10" data-volume="1" data-audio-group="voiceover"></audio>']
        for i, (t, f, v, d) in enumerate(sorted(self.cues, key=lambda c: (c[0], c[1]))):
            dur = f' data-duration="{d}"' if d else ""
            audio.append(f'<audio id="sfx-{i:03d}" src="{SFX_DIR}{f}" data-start="{t}"{dur} data-track-index="{20 + i}" '
                         f'data-volume="{v}" data-audio-group="sfx"></audio>')
        nl = chr(10)
        index = (
            "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\" />\n"
            "<meta name=\"viewport\" content=\"width=1080, height=1920\" />\n"
            "<script src=\"https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js\"></script>\n<style>\n"
            "* { margin: 0; padding: 0; box-sizing: border-box; }\n"
            "html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #F5F1EA; }\n"
            "#root { position: relative; width: 100%; height: 100%; overflow: hidden; background: #F5F1EA; }\n"
            "[data-composition-id=\"main\"] > div[data-composition-src] { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }\n"
            "</style>\n</head>\n<body>\n"
            f'<div id="root" data-composition-id="main" data-start="0" data-duration="{self.total}" '
            f'data-fps="{self.fps:g}" data-width="1080" data-height="1920">\n'
            + nl.join(hosts) + nl + nl.join(audio) + nl
            + "</div>\n<script>\nwindow.__timelines[\"main\"] = gsap.timeline({ paused: true });\n</script>\n</body>\n</html>\n"
        )
        (project / "index.html").write_text(index, encoding="utf-8")
        return f"wrote {len(self.scenes)} scenes, {len(self.cues)} sound cues, {self.total}s"


__all__ = ["Reel", "Scene", "A_WIDE", "A_TIGHT", "INSERT", "IMG", "SFX_DIR", "CURSOR_SVG", "FONTS", "COMMON_CSS",
           "COMMON_JS", "chip", "teaser_card", "serif_row", "sans_row", "phone", "browser", "terminal", "frame", "check", "cursor"]
