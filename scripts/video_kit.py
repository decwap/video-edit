"""video_kit — the motion-graphics kit of the video-edit skill (Paper-style reels from raw talking-head footage).

One import gives a scene script everything: the paper_reel library (Reel, scenes, captions), reel_kit (layouts,
plates, whip / flip / zoom-through / paper-cover / card-expand transitions, sound pre-mix) and the props below.

    import sys; from pathlib import Path
    sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "video-edit" / "scripts"))
    from video_kit import *
    configure(face_shift=640)          # aroll.py --face prints it; set_shift() changes it if the framing moves
    reel = Reel(total=75.4, fps=30, voice_dur=73.67)
    ...scenes...
    print(finish(reel, PROJECT, accent="#0B7A73"))   # write compositions + index, recolour the accent, pre-mix sounds

Adds to reel_kit:
  transitions  bars_out / bars_in (ink + accent bars sweep the cut), leak_out / leak_in (warm light-leak flash),
               viewfinder (REC corners over a punch-in)
  props        avatar, vcard (video card), eng (engagement icon bubble), retention (watch-time bar), doc_card (prompt /
               document card), keycap, btn, check_row, comment_box, dm_notif, swatch (style card), wave_chip (a sound
               drawn from its real waveform), edit_timeline + timeline_build, film_strip (raw -> edited, sprite from
               strip.py), profile_card, logo_tile, pwin (browser window around a real capture)
  helpers      plates / Pc (caption plates over footage), srow / nrow (serif / sans rows), g / gl / acc (grey, label and
               accent spans), card (paper CARD beat with an entrance), split_at / expand (SPLIT that knows the face shift),
               depth_keys, keys_cue, finish
Scene methods and helpers take GLOBAL seconds; JS lines are scene-local (s.L). Worked example: examples/scenes.py.
"""
import re
import subprocess
from pathlib import Path

import numpy as np

import reel_kit as rk
from reel_kit import *  # noqa: F401,F403
from paper_reel import browser, check, frame, phone, sans_row, serif_row, teaser_card, terminal  # noqa: F401
from face_panel import load_panel, panel, use_panel  # noqa: F401

SKILL = Path(__file__).resolve().parent.parent
pr = rk.pr
INK, PAPER, CARDW, LABEL, GREY = rk.INK, rk.PAPER, rk.CARDW, rk.LABEL, rk.GREY
TEAL, TEAL_D, TEAL_T = "#0B7A73", "#075450", "#D7ECE8"      # default accent family (Transformative Teal); finish() recolours
IMG = "assets/img/"

EXTRA_CSS = """
.tb-bar{position:absolute;left:-40px;width:1160px}
.leak{position:absolute;left:-540px;top:-200px;width:2160px;height:2320px;mix-blend-mode:screen;opacity:0;
  background:radial-gradient(ellipse 38% 30% at 50% 46%,rgba(255,196,128,.95),rgba(255,140,70,.55) 42%,rgba(255,110,60,0) 72%)}
.leak2{position:absolute;left:-200px;top:300px;width:1500px;height:1500px;mix-blend-mode:screen;opacity:0;
  background:radial-gradient(circle at 50% 50%,rgba(255,236,200,.9),rgba(255,170,110,.35) 40%,rgba(255,150,90,0) 70%)}
.vf{position:absolute;width:120px;height:120px;border-color:#FFF8EF;border-style:solid;filter:drop-shadow(0 2px 8px rgba(0,0,0,.45))}
.vf-rec{position:absolute;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:40px;letter-spacing:.12em;color:#FFF8EF;white-space:nowrap;text-shadow:0 2px 10px rgba(0,0,0,.5)}
.vf-dot{display:inline-block;width:30px;height:30px;border-radius:50%;background:#E5483B;margin-right:16px;vertical-align:-3px}
.av{position:absolute;border-radius:50%;box-shadow:0 18px 40px rgba(40,30,20,.18);border:8px solid #FFFDF9}
.av .avi{position:absolute;left:22%;top:20%;width:56%;height:56%}
.av .avi svg{display:block;width:100%;height:100%}
.av .avp{position:absolute;right:-10px;bottom:-6px;width:38%;height:38%;border-radius:50%;background:#17140F;border:5px solid #FFFDF9}
.av .avp:after{content:"";position:absolute;left:40%;top:28%;border-left:.9em solid #FFFFFF;border-top:.55em solid transparent;border-bottom:.55em solid transparent;font-size:14px}
.vc{position:absolute;background:#FFFDF9;border-radius:30px;box-shadow:0 18px 40px rgba(40,30,20,.16);overflow:hidden}
.vc .vct{position:absolute;left:0;top:0;width:100%;height:62%;background:#1B1915}
.vc .vct:after{content:"";position:absolute;left:50%;top:50%;margin:-26px 0 0 -16px;border-left:44px solid #FFFDF9;border-top:26px solid transparent;border-bottom:26px solid transparent}
.vc .vcl{position:absolute;left:24px;height:14px;border-radius:7px;background:#E6DED3}
.eng{position:absolute;width:104px;height:104px;border-radius:50%;background:#FFFFFF;box-shadow:0 14px 30px rgba(20,15,10,.22)}
.eng svg{position:absolute;left:26px;top:26px;width:52px;height:52px}
.ret{position:absolute;height:26px;border-radius:13px;background:#E6DED3;overflow:hidden}
.ret i{position:absolute;left:0;top:0;height:100%;width:100%;border-radius:13px;background:#0B7A73;transform-origin:0% 50%}
.tlc{position:absolute;background:#1B1915;border-radius:30px;box-shadow:0 30px 70px rgba(20,15,10,.35);overflow:hidden}
.tlc .tlh{position:absolute;left:0;top:0;width:100%;height:58px;border-bottom:2px solid #2C2925}
.tlc .tlh i{position:absolute;top:21px;width:16px;height:16px;border-radius:50%}
.tlc .tlh span{position:absolute;left:0;width:100%;top:15px;text-align:center;font-family:'JetBrains Mono',monospace;font-size:24px;color:#8E877C}
.tlc .trk{position:absolute;left:110px;right:28px;height:74px;border-radius:14px;background:#24211C}
.tlc .tlab{position:absolute;left:26px;width:70px;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:24px;color:#8E877C;line-height:74px}
.tlc .clp{position:absolute;top:8px;height:58px;border-radius:10px}
.tlc .ph{position:absolute;top:66px;bottom:16px;width:4px;margin-left:-2px;background:#FFF8EF;border-radius:2px}
.tlc .ph:before{content:"";position:absolute;left:-12px;top:-4px;border-top:18px solid #FFF8EF;border-left:14px solid transparent;border-right:14px solid transparent}
.strip{position:absolute;width:96px;height:171px}
.strip .fr{position:absolute;width:96px;height:171px;border-radius:12px;overflow:hidden;background:#1B1915}
.strip .fr img{position:absolute;left:0;top:0;width:100%;height:100%;object-fit:cover}
.strip .fr b{position:absolute;left:0;top:0;width:100%;height:100%;background:rgba(23,20,15,.55)}
.strip .fr b:before,.strip .fr b:after{content:"";position:absolute;left:44px;top:58px;width:8px;height:56px;border-radius:4px;background:#FFFFFF;transform:rotate(45deg)}
.strip .fr b:after{transform:rotate(-45deg)}
.strip .fr.k{box-shadow:0 0 0 5px #0B7A73}
.wv{position:absolute;background:#FFFFFF;border-radius:30px;border:3px solid #EDE5DA;box-shadow:0 16px 36px rgba(40,30,20,.14)}
.wv .wn{position:absolute;left:30px;top:22px;font-family:'JetBrains Mono',monospace;font-weight:700;font-size:30px;color:#17140F;letter-spacing:.02em;white-space:nowrap}
.wv .wbx{position:absolute;left:30px;right:30px;bottom:22px;height:70px}
.wv .wbx svg{position:absolute;left:0;top:0;width:100%;height:100%}
.wv .wpl{position:absolute;right:26px;top:18px;width:44px;height:44px;border-radius:50%;background:#EFE9E0}
.wv .wpl:after{content:"";position:absolute;left:17px;top:12px;border-left:16px solid #17140F;border-top:10px solid transparent;border-bottom:10px solid transparent}
.bdg{position:absolute;width:64px;height:64px;border-radius:50%;background:#0B7A73;box-shadow:0 8px 18px rgba(7,84,80,.30)}
.bdg:after{content:"";position:absolute;left:23px;top:13px;width:14px;height:27px;border:solid #FFFFFF;border-width:0 7px 7px 0;transform:rotate(45deg)}
.bdg.x{background:#17140F}
.bdg.x:before,.bdg.x:after{content:"";position:absolute;left:50%;top:22%;width:12%;height:56%;margin-left:-6%;border:0;border-radius:4px;background:#FFFFFF;transform:rotate(45deg)}
.bdg.x:before{transform:rotate(-45deg)}
.doc{position:absolute;background:#FFFDF9;border-radius:30px;box-shadow:0 26px 60px rgba(40,30,20,.20);overflow:hidden}
.doc .dt{position:absolute;font-family:'Instrument Serif',serif;font-style:italic;color:#17140F;letter-spacing:-.02em;line-height:1;white-space:nowrap}
.doc .ds{position:absolute;font-family:'JetBrains Mono',monospace;font-weight:600;color:#746D62;letter-spacing:.14em;white-space:nowrap}
.doc .dln{position:absolute;height:16px;border-radius:8px;background:#E6DED3}
.doc .dic{position:absolute;border-radius:20px;background:#0B7A73}
.doc .dic svg{position:absolute;left:22%;top:22%;width:56%;height:56%}
.kc{position:absolute;width:170px;height:170px;border-radius:30px;background:#FFFFFF;border:3px solid #E3DACD;border-bottom:14px solid #D8CFC1;box-shadow:0 14px 28px rgba(40,30,20,.16);font-family:'JetBrains Mono',monospace;font-weight:700;font-size:70px;color:#17140F;text-align:center;line-height:150px}
.btnt{position:absolute;border-radius:999px;background:#0B7A73;color:#FFFFFF;display:flex;align-items:center;justify-content:center;gap:22px;font-family:'Instrument Sans',sans-serif;font-weight:700;letter-spacing:-.02em;white-space:nowrap;box-shadow:0 20px 44px rgba(7,84,80,.30)}
.btnt .bi{display:block;width:1em;height:1em}
.btnt .bi svg{display:block;width:100%;height:100%}
.btnt.ink{background:#17140F;box-shadow:0 20px 44px rgba(20,15,10,.30)}
.btnt.off{background:#D9D1C5;color:#8F877B;box-shadow:none}
.ckl{position:absolute;left:110px;width:860px;height:150px;border-radius:30px;background:#FFFFFF;border:3px solid #EDE5DA;box-shadow:0 14px 30px rgba(40,30,20,.12);overflow:hidden}
.ckl .ci{position:absolute;left:30px;top:37px;width:76px;height:76px;border-radius:22px;background:#EFE9E0}
.ckl .ci svg{position:absolute;left:19px;top:19px;width:38px;height:38px}
.ckl .cl{position:absolute;left:134px;top:46px;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:50px;letter-spacing:-.02em;color:#17140F;white-space:nowrap}
.ckl .cb{position:absolute;right:34px;top:41px;width:68px;height:68px;border-radius:20px;border:5px solid #D8CFC1}
.ckl .ck{position:absolute;right:34px;top:41px;width:68px;height:68px;border-radius:20px;background:#0B7A73;opacity:0}
.ckl .ck:after{content:"";position:absolute;left:23px;top:10px;width:14px;height:29px;border:solid #FFFFFF;border-width:0 7px 7px 0;transform:rotate(45deg)}
.cmt{position:absolute;background:#FFFFFF;border-radius:999px;border:3px solid #E6DED1;box-shadow:0 18px 40px rgba(40,30,20,.18)}
.cmt .cav{position:absolute;left:18px;top:50%;width:76px;height:76px;margin-top:-38px;border-radius:50%;background:#D7ECE8}
.cmt .cav svg{position:absolute;left:18px;top:18px;width:40px;height:40px}
.cmt .ctx{position:absolute;left:116px;top:50%;margin-top:-34px;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:54px;line-height:68px;color:#17140F;white-space:nowrap}
.cmt .cph{position:absolute;left:116px;top:50%;margin-top:-30px;font-family:'Instrument Sans',sans-serif;font-weight:500;font-size:44px;line-height:60px;color:#A99E8D;white-space:nowrap}
.cmt .csd{position:absolute;right:16px;top:50%;width:80px;height:80px;margin-top:-40px;border-radius:50%;background:#0B7A73}
.cmt .csd svg{position:absolute;left:21px;top:21px;width:38px;height:38px}
.dm{position:absolute;background:rgba(255,255,255,.97);border-radius:34px;box-shadow:0 20px 44px rgba(20,15,10,.22)}
.dm .di{position:absolute;left:24px;top:26px;width:92px;height:92px;border-radius:24px;background:#0B7A73}
.dm .di svg{position:absolute;left:23px;top:23px;width:46px;height:46px}
.dm .da{position:absolute;left:140px;top:26px;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:28px;color:#746D62;letter-spacing:.02em;white-space:nowrap}
.dm .dh{position:absolute;left:140px;top:62px;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:40px;color:#17140F;white-space:nowrap}
.dm .dw{position:absolute;right:28px;top:26px;font-family:'Instrument Sans',sans-serif;font-weight:500;font-size:26px;color:#8F877B}
.pf{position:absolute;background:#FFFDF9;border-radius:40px;box-shadow:0 26px 60px rgba(40,30,20,.18);overflow:hidden}
.pf .pav{position:absolute;border-radius:50%;background:#D7ECE8;border:6px solid #FFFFFF;box-shadow:0 0 0 4px #0B7A73}
.pf .pav svg{position:absolute;left:22%;top:20%;width:56%;height:56%}
.pf .pst{position:absolute;text-align:center;font-family:'Instrument Sans',sans-serif;white-space:nowrap}
.pf .pst b{display:block;font-weight:700;font-size:44px;color:#17140F;line-height:1.1}
.pf .pst span{display:block;font-weight:500;font-size:26px;color:#746D62}
.pf .pln{position:absolute;height:18px;border-radius:9px;background:#E6DED3}
.pf .plk{position:absolute;border-radius:22px;background:#D7ECE8;display:flex;align-items:center;gap:16px;padding-left:24px;font-family:'Instrument Sans',sans-serif;font-weight:700;font-size:38px;color:#075450;white-space:nowrap}
.pf .plk svg{width:40px;height:40px}
.sw{position:absolute;border-radius:30px;background:#FFFDF9;box-shadow:0 20px 44px rgba(40,30,20,.18);overflow:hidden}
.sw .swb{position:absolute;left:0;top:0;width:100%;height:46%}
.sw .swt{position:absolute;left:26px;font-family:'Instrument Serif',serif;font-style:italic;font-size:62px;letter-spacing:-.02em;color:#17140F;white-space:nowrap}
.sw .swl{position:absolute;left:26px;height:14px;border-radius:7px;background:#E6DED3}
.sw .swc{position:absolute;right:22px;width:64px;height:64px;border-radius:50%}
.clk{position:absolute;font-family:'JetBrains Mono',monospace;font-weight:700;color:#17140F;white-space:nowrap;letter-spacing:-.01em}
.tl-tile{position:absolute;background:#FFFFFF;border-radius:26%;box-shadow:0 26px 60px rgba(40,30,20,.20),0 0 0 2px rgba(23,20,15,.05)}
.tl-tile img{position:absolute;object-fit:contain}
.pw{position:absolute;background:#FFFFFF;border-radius:26px;overflow:hidden;box-shadow:0 30px 70px rgba(40,30,20,.24)}
.pw .wb{position:absolute;left:0;top:0;width:100%;height:50px;background:#EFE9E0}
.pw .wb i{position:absolute;top:18px;width:14px;height:14px;border-radius:50%;background:#CFC5B6}
.pw .wu{position:absolute;top:11px;left:104px;right:34px;height:28px;border-radius:14px;background:#FFFDF9}
.pw .wbody{position:absolute;left:0;top:50px;right:0;bottom:0;overflow:hidden;background:#FFFFFF}
.pw .wbody img{position:absolute;left:0;top:0;width:100%}
.mcard{position:absolute;background:#FFFDF9;border-radius:30px;box-shadow:0 20px 50px rgba(40,30,20,.16)}
"""

EXTRA_JS = r"""
const wobble = (el, t, d, amp) => { const n = Math.round(d / 0.16); for (let i = 0; i < n; i++) tl.to(el, { rotation: (i % 2 ? -1 : 1) * amp * (0.6 + 0.4 * i / n), duration: 0.16, ease: "sine.inOut" }, t + i * 0.16); };
const countTo = (el, a, b, t, d, fmt) => { const p = { v: a }; tl.to(p, { v: b, duration: d, ease: "power2.out", onUpdate: () => { el.textContent = fmt(p.v); } }, t); };
const mmss = (v) => { const s = Math.round(v); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
const drawIn = (el, t, d) => tl.fromTo(el, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: d || 0.5, ease: "power2.out" }, t);
const growX = (el, t, d) => tl.fromTo(el, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, transformOrigin: "0% 50%", duration: d || 0.4, ease: "power3.out" }, t);
const dropIn = (el, t, o) => { o = Object.assign({ y: -140, r: -8, d: 0.5 }, o || {}); tl.fromTo(el, { opacity: 0, y: o.y, rotation: o.r, scale: 0.8 }, { opacity: 1, y: 0, rotation: 0, scale: 1, duration: o.d, ease: "back.out(1.7)" }, t); };
const floatY = (el, t, d, a) => tl.to(el, { y: a || -12, duration: d, ease: "sine.inOut" }, t);
"""


def J(s, line):
    s.js.append(line)


def icon(name, color=INK, sw=2.0):
    """A Lucide icon (assets/icons.json, ISC) as inline SVG that fills its container."""
    return svg_inline(name, color, sw)


def configure(face_shift=380):
    """Install the kit's CSS / JS into every scene and set the SPLIT face-card shift (px the footage is lifted inside
    the card; aroll.py --face prints a value). Call it once before building scenes."""
    rk.configure(face_shift)
    pr.COMMON_CSS = pr.COMMON_CSS + EXTRA_CSS
    pr.COMMON_JS = pr.COMMON_JS + EXTRA_JS


def set_shift(face_shift):
    """Change the face-card shift for the SPLIT / expand calls that follow (the speaker moved in the frame)."""
    rk.FACE_SHIFT = face_shift


configure()




# ---------------------------------------------------------------- transitions
BAR_N = 6


def bars_out(s, g_cut, d=0.2, color=INK):
    """Bars sweep in from the left (staggered) and cover the frame exactly at g_cut."""
    g0 = round(g_cut - d - 0.04, 3)
    h = 1920 / BAR_N
    bars = "".join(f'<div id="{s.id("bo")}{i}" class="tb-bar" style="top:{round(i * h - 2)}px;height:{round(h + 4)}px;'
                   f'background:{color if i % 2 == 0 else TEAL}" data-layout-allow-overflow></div>' for i in range(BAR_N))
    s.layer("bo", g0, g_cut, 90, inner=bars)
    for i in range(BAR_N):
        st = i * 0.022
        J(s, f'tl.fromTo($("{s.id("bo")}{i}"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, transformOrigin: "0% 50%", '
             f'duration: {round(d - st, 3)}, ease: "power3.in" }}, {s.L(g0) + st:.3f});')


def bars_in(s, g_cut, d=0.26, color=INK):
    """Continues bars_out on the next scene: full bars retract to the right (staggered)."""
    h = 1920 / BAR_N
    bars = "".join(f'<div id="{s.id("bi")}{i}" class="tb-bar" style="top:{round(i * h - 2)}px;height:{round(h + 4)}px;'
                   f'background:{color if i % 2 == 0 else TEAL}" data-layout-allow-overflow></div>' for i in range(BAR_N))
    s.layer("bi", g_cut, round(g_cut + d + 0.06, 3), 90, inner=bars)
    t0 = s.L(g_cut)
    for i in range(BAR_N):
        st = i * 0.024
        J(s, f'tl.fromTo($("{s.id("bi")}{i}"), {{ scaleX: 1, transformOrigin: "100% 50%" }}, {{ scaleX: 0, transformOrigin: "100% 50%", '
             f'duration: {round(d - st, 3)}, ease: "power3.out", immediateRender: false }}, {t0 + 0.04 + st:.3f});')


def leak_out(s, g_cut, d=0.22):
    """Warm light leak swells across the frame into the cut (pair with leak_in on the next scene)."""
    g0 = round(g_cut - d, 3)
    s.layer("lko", g0, g_cut, 88, inner=f'<div id="{s.id("lko")}-a" class="leak" data-layout-allow-overflow></div>'
                                         f'<div id="{s.id("lko")}-b" class="leak2" data-layout-allow-overflow></div>')
    J(s, f'tl.fromTo($("{s.id("lko")}-a"), {{ opacity: 0, x: -520, scale: 0.8 }}, {{ opacity: 1, x: 0, scale: 1.1, duration: {d}, ease: "power2.in" }}, {s.L(g0)});')
    J(s, f'tl.fromTo($("{s.id("lko")}-b"), {{ opacity: 0 }}, {{ opacity: 0.9, duration: {d}, ease: "power2.in" }}, {s.L(g0)});')


def leak_in(s, g_cut, d=0.34):
    s.layer("lki", g_cut, round(g_cut + d, 3), 88, inner=f'<div id="{s.id("lki")}-a" class="leak" data-layout-allow-overflow></div>'
                                                      f'<div id="{s.id("lki")}-b" class="leak2" data-layout-allow-overflow></div>')
    t = s.L(g_cut)
    J(s, f'tl.fromTo($("{s.id("lki")}-a"), {{ opacity: 1, x: 0, scale: 1.1 }}, {{ opacity: 0, x: 560, scale: 1.25, duration: {d}, ease: "power2.out", immediateRender: false }}, {t});')
    J(s, f'tl.fromTo($("{s.id("lki")}-b"), {{ opacity: 0.9 }}, {{ opacity: 0, duration: {round(d * 0.8, 3)}, ease: "power2.out", immediateRender: false }}, {t});')
    J(s, f'tl.set($("{s.id("lki")}-a"), {{ opacity: 1 }}, 0); tl.set($("{s.id("lki")}-b"), {{ opacity: 0.9 }}, 0);')


def viewfinder(cid):
    corners = (f'<div class="vf" style="left:70px;top:250px;border-width:10px 0 0 10px;border-radius:26px 0 0 0"></div>'
               f'<div class="vf" style="right:70px;top:250px;border-width:10px 10px 0 0;border-radius:0 26px 0 0"></div>'
               f'<div class="vf" style="left:70px;bottom:250px;border-width:0 0 10px 10px;border-radius:0 0 0 26px"></div>'
               f'<div class="vf" style="right:70px;bottom:250px;border-width:0 10px 10px 0;border-radius:0 0 26px 0"></div>')
    rec = (f'<div class="vf-rec" style="left:110px;top:296px"><span id="{cid}-dot" class="vf-dot"></span>REC</div>'
           f'<div class="vf-rec" style="right:110px;top:296px">4K · 30</div>')
    return f'<div id="{cid}" class="pr-c" style="opacity:0">{corners}{rec}</div>'


# ---------------------------------------------------------------- props (HTML strings)
AV_COLORS = ["#D7ECE8", "#F3DCCB", "#E4DDF2", "#DCE8F3", "#F2E3C4", "#E9D6D6"]


def avatar(cid, x, y, size, k=0, style=""):
    col = AV_COLORS[k % len(AV_COLORS)]
    return (f'<div id="{cid}" class="av" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;background:{col};{style}">'
            f'<div class="avi">{icon("user-round", "#17140F", 1.8)}</div><div class="avp" style="font-size:{round(size / 10)}px"></div></div>')


def vcard(cid, x, y, w, h, style=""):
    lines = (f'<div class="vcl" style="top:{round(h * 0.7)}px;width:{round(w * 0.62)}px"></div>'
             f'<div class="vcl" style="top:{round(h * 0.7) + 30}px;width:{round(w * 0.4)}px"></div>')
    return f'<div id="{cid}" class="vc" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}"><div class="vct"></div>{lines}</div>'


def eng(cid, name, x, y, color=INK, style=""):
    return f'<div id="{cid}" class="eng" style="left:{x}px;top:{y}px;{style}">{icon(name, color, 2.4)}</div>'


def retention(cid, x, y, w):
    return f'<div id="{cid}" class="ret" style="left:{x}px;top:{y}px;width:{w}px"><i id="{cid}-f"></i></div>'


def doc_card(cid, x, y, w, h, title, sub, ic="file-text", lines=7, title_size=64, style="", body=""):
    head = (f'<div class="dic" style="left:34px;top:34px;width:84px;height:84px">{icon(ic, "#FFFFFF", 2.2)}</div>'
            f'<div class="dt" style="left:140px;top:30px;font-size:{title_size}px" data-layout-allow-overlap>{title}</div>'
            f'<div class="ds" style="left:142px;top:{50 + round(title_size * 1.04)}px;font-size:22px" data-layout-allow-overlap>{sub}</div>')
    if not body:
        ws = [0.92, 0.78, 0.86, 0.64, 0.9, 0.72, 0.84, 0.58, 0.88, 0.7]
        body = "".join(f'<div class="dln" style="left:36px;top:{176 + i * 44}px;width:{round((w - 72) * ws[i % len(ws)])}px"></div>'
                       for i in range(lines))
    return f'<div id="{cid}" class="doc" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">{head}{body}</div>'


def keycap(cid, label, x, y, style=""):
    return f'<div id="{cid}" class="kc" style="left:{x}px;top:{y}px;{style}">{label}</div>'


def btn(cid, label, x, y, w, h, size=64, icon_name=None, cls="btnt", style=""):
    ic_ = f'<span class="bi">{icon(icon_name, "#FFFFFF", 2.4)}</span>' if icon_name else ""
    return (f'<div id="{cid}" class="{cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;font-size:{size}px;{style}">'
            f'{ic_}<span id="{cid}-t" data-layout-allow-overlap>{label}</span></div>')


def check_row(cid, icon_name, label, top, extra=""):
    return (f'<div id="{cid}" class="ckl" style="top:{top}px"><div class="ci">{icon(icon_name, INK, 2.2)}</div>'
            f'<div class="cl">{label}</div>{extra}<div class="cb"></div><div id="{cid}-k" class="ck"></div></div>')


def comment_box(cid, x, y, w, h=120, style=""):
    return (f'<div id="{cid}" class="cmt" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">'
            f'<div class="cav">{icon("user-round", TEAL_D, 2.2)}</div>'
            f'<div id="{cid}-ph" class="cph">Add a comment…</div><div id="{cid}-tx" class="ctx"></div>'
            f'<div id="{cid}-sd" class="csd">{icon("send", "#FFFFFF", 2.4)}</div></div>')


def dm_notif(cid, x, y, w, head, sub="Direct message", when="now", style=""):
    return (f'<div id="{cid}" class="dm" style="left:{x}px;top:{y}px;width:{w}px;height:144px;{style}">'
            f'<div class="di">{icon("message-circle", "#FFFFFF", 2.4)}</div><div class="da">{sub}</div>'
            f'<div class="dh">{head}</div><div class="dw">{when}</div></div>')


def swatch(cid, x, y, w, h, color, title, style=""):
    return (f'<div id="{cid}" class="sw" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">'
            f'<div class="swb" style="background:{color}"></div>'
            f'<div class="swt" style="top:{round(h * 0.5)}px">{title}</div>'
            f'<div class="swl" style="top:{round(h * 0.5) + 86}px;width:{round(w * 0.6)}px"></div>'
            f'<div class="swl" style="top:{round(h * 0.5) + 116}px;width:{round(w * 0.42)}px"></div>'
            f'<div class="swc" style="top:{round(h * 0.46) - 32}px;background:{color};border:6px solid #FFFDF9"></div></div>')


# ---------------------------------------------------------------- waveform chips from the real SFX files
def waveform_svg(sfx_file, n=44, color="#D8CFC1"):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(SKILL / "assets" / "sfx" / sfx_file), "-ac", "1", "-ar", "8000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.abs(np.frombuffer(raw, np.float32))
    x = x[: max(n, len(x) // n * n)]
    env = x.reshape(n, -1).max(1) if len(x) >= n else np.pad(x, (0, n - len(x)))
    env = env / (env.max() + 1e-9)
    env = np.clip(env ** 0.6, 0.08, 1.0)
    bw = 100 / n
    rects = "".join(f'<rect x="{i * bw + bw * 0.18:.2f}" y="{50 - v * 48:.2f}" width="{bw * 0.64:.2f}" height="{v * 96:.2f}" rx="{bw * 0.3:.2f}"/>'
                    for i, v in enumerate(env))
    return f'<svg viewBox="0 0 100 100" preserveAspectRatio="none"><g fill="{color}">{rects}</g></svg>'


def wave_chip(cid, sfx_file, label, x, y, w=440, h=170, style=""):
    """Sound chip: name + the file's own waveform (grey) with a teal copy revealed by a clip-path (id {cid}-on)."""
    grey = waveform_svg(sfx_file)
    teal = waveform_svg(sfx_file, color=TEAL)
    return (f'<div id="{cid}" class="wv" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">'
            f'<div class="wn">{label}</div><div class="wpl"></div>'
            f'<div class="wbx">{grey}<div id="{cid}-on" style="position:absolute;left:0;top:0;width:100%;height:100%;clip-path:inset(0 100% 0 0)">{teal}</div></div></div>')


# ---------------------------------------------------------------- editing timeline that assembles itself
def edit_timeline(cid, x, y, w, h, title="IMG_2495.MOV — edit"):
    """Dark NLE timeline: four tracks (V1 footage, GFX, CAP captions, SFX). Clip ids: {cid}-c{track}{i}; playhead {cid}-ph."""
    tracks = [("V1", [(0.00, 0.30, "#8C6A5A"), (0.31, 0.22, "#8C6A5A"), (0.54, 0.24, "#8C6A5A"), (0.79, 0.21, "#8C6A5A")]),
              ("GFX", [(0.04, 0.16, TEAL), (0.25, 0.12, TEAL), (0.44, 0.18, TEAL), (0.70, 0.14, TEAL), (0.88, 0.10, TEAL)]),
              ("CAP", [(0.00, 0.12, "#EDE6DA"), (0.13, 0.10, "#EDE6DA"), (0.24, 0.14, "#EDE6DA"), (0.39, 0.12, "#EDE6DA"),
                       (0.52, 0.11, "#EDE6DA"), (0.64, 0.13, "#EDE6DA"), (0.78, 0.10, "#EDE6DA"), (0.89, 0.11, "#EDE6DA")]),
              ("SFX", [(0.03, 0.05, "#E3B341"), (0.24, 0.05, "#E3B341"), (0.43, 0.06, "#E3B341"), (0.62, 0.05, "#E3B341"), (0.86, 0.06, "#E3B341")])]
    tw = w - 110 - 28
    out = [f'<div class="tlh"><i style="left:24px;background:#E06C55"></i><i style="left:52px;background:#E3B341"></i>'
           f'<i style="left:80px;background:#6CB27A"></i><span>{title}</span></div>']
    for k, (lab, clips) in enumerate(tracks):
        ty = 90 + k * 92
        out.append(f'<div class="tlab" style="top:{ty}px">{lab}</div><div class="trk" style="top:{ty}px">')
        for i, (a, b, col) in enumerate(clips):
            out.append(f'<div id="{cid}-c{k}{i}" class="clp" style="left:{round(a * tw)}px;width:{round(b * tw)}px;background:{col}"></div>')
        out.append('</div>')
    out.append(f'<div id="{cid}-ph" class="ph" style="left:110px"></div>')
    return f'<div id="{cid}" class="tlc" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{"".join(out)}</div>'


def timeline_build(s, cid, g0, step=0.035):
    """Clips pop onto their tracks in order (track by track), then the playhead sweeps."""
    n = 0
    for k, cnt in enumerate((4, 5, 8, 5)):
        for i in range(cnt):
            J(s, f'tl.fromTo($("{cid}-c{k}{i}"), {{ opacity: 0, scaleX: 0.2, y: -26 }}, {{ opacity: 1, scaleX: 1, y: 0, duration: 0.26, '
                 f'ease: "back.out(2)", transformOrigin: "0% 50%" }}, {s.L(g0) + n * step:.3f});')
            n += 1
    return n


# ---------------------------------------------------------------- the raw-footage strip (real thumbnails)
STRIP_STEP = 106                    # px per strip cell (96 px thumbnail + 10 px gap)


def film_strip(cid, frames, kept, x, y):
    """frames: [img src]; kept: [bool]. Cut frames carry an X and can collapse (ids {cid}-f{i})."""
    n = len(frames)          # frames = sprite path (one image, n cells) so every thumbnail is ready at capture
    sprite = frames[0] if isinstance(frames, list) else frames
    n = len(kept)
    cells = "".join(f'<div id="{cid}-f{i}" class="fr{" k" if k else ""}" style="position:absolute;left:{i * STRIP_STEP}px;top:0;'
                    f'background-image:url({sprite});background-size:{n * 96}px 171px;background-position:-{i * 96}px 0px">'
                    f'{"" if k else "<b></b>"}</div>'
                    for i, k in enumerate(kept))
    return f'<div id="{cid}" class="strip" style="left:{x}px;top:{y}px">{cells}</div>'


def profile_card(cid, x, y, w, h):
    stats = "".join(f'<div class="pst" style="left:{round(w * (0.36 + 0.21 * i))}px;top:66px;width:{round(w * 0.2)}px">'
                    f'<b style="margin:0 auto 10px;width:62%;height:34px;border-radius:17px;background:#E6DED3"></b><span>{lab}</span></div>'
                    for i, lab in enumerate(("posts", "followers", "following")))
    return (f'<div id="{cid}" class="pf" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="pav" style="left:40px;top:40px;width:170px;height:170px">{icon("user-round", TEAL_D, 1.8)}</div>{stats}'
            f'<div class="pln" style="left:44px;top:250px;width:{round(w * 0.36)}px;background:#17140F;height:26px;border-radius:13px"></div>'
            f'<div class="pln" style="left:44px;top:300px;width:{round(w * 0.72)}px"></div>'
            f'<div class="pln" style="left:44px;top:334px;width:{round(w * 0.56)}px"></div>'
            f'<div id="{cid}-lk" class="plk" style="left:36px;top:378px;width:{w - 72}px;height:92px">{icon("link", TEAL_D, 2.4)}'
            f'<span>link in bio</span></div>'
            f'<div id="{cid}-ring" style="position:absolute;left:24px;top:366px;width:{w - 48}px;height:116px;border-radius:30px;border:6px solid {TEAL};opacity:0"></div>'
            f'</div>')




# ---------------------------------------------------------------- logos and captures
def logo_tile(cid, src, x, y, size, pad=0.2, style=""):
    """App-icon style tile holding one logo image (use the brand's own mark from its site or press kit)."""
    w = 1 - 2 * pad
    return (f'<div id="{cid}" class="tl-tile" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;{style}">'
            f'<img src="{src}" alt="" style="left:{pad * 100:.0f}%;top:{pad * 100:.0f}%;width:{w * 100:.0f}%;height:{w * 100:.0f}%" /></div>')


def pwin(cid, x, y, w, h, img, img_style=""):
    """Browser window around a real capture (the image fills the width; scroll it by tweening y of {cid}-img)."""
    return (f'<div id="{cid}" class="pw" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            '<div class="wb"><i style="left:20px"></i><i style="left:44px"></i><i style="left:68px"></i><div class="wu"></div></div>'
            f'<div class="wbody"><img id="{cid}-img" src="{img}" alt="" style="{img_style}" /></div></div>')


# ---------------------------------------------------------------- text + layout helpers used by every beat
PL_Y, PS_Y = 1290, 1262          # sans / serif caption plates sit on the chest, inside the y 760-1500 safe band


def g(t):
    return f'<span style="color:#8F877B">{t}</span>'


def gl(t):
    return f'<span style="color:#746D62">{t}</span>'


def acc(t):
    return f'<span style="color:{TEAL}">{t}</span>'


def srow(cid, html, top, size, color="ink", style=""):
    """A centred serif line, hidden until animated (rise / slam / show)."""
    return (f'<div id="{cid}" class="bx-serif bx-row bx-{color}" style="top:{top}px;font-size:{size}px;opacity:0;{style}" '
            f'data-layout-allow-overlap data-layout-allow-overflow>{html}</div>')


def nrow(cid, html, top, size, color="ink", style=""):
    """A centred sans line, hidden until animated."""
    return (f'<div id="{cid}" class="bx-sans bx-row bx-{color}" style="top:{top}px;font-size:{size}px;opacity:0;{style}" '
            f'data-layout-allow-overlap data-layout-allow-overflow>{html}</div>')


def Pc(txt, g0, g1, kind="sans", size=None, tone="", how="rise"):
    """One caption-plate cue: kind sans | serif, how rise | pop | slam, g1 None = until the scene ends."""
    return (txt, g0, g1, kind, size or (112 if kind == "serif" else 78), tone, how)


def plates(s, name, cues, z=6):
    """Caption plates over footage (paper pills that read on any shirt or wall), swapped by hard cut."""
    html = ""
    for i, (txt, g0, g1, kind, size, tone, how) in enumerate(cues):
        cid = s.id(f"{name}{i}")
        html += plate(cid, txt, PS_Y if kind == "serif" else PL_Y, size, kind, tone)
        plate_show(s, cid, g0, g1, how)
    g_start = min(c[1] for c in cues)
    g_end = max((c[2] if c[2] is not None else s.start + s.dur) for c in cues)
    lay(s, name, round(g_start - 0.02, 3) if g_start - 0.02 >= s.start else s.start, round(g_end, 3), z, html)


def card(s, name, g0, g1, inner, z=5, enter="up", leaf=0.5, dy=0):
    """A paper CARD beat. enter: up | right | whip | flip | zoom | none (when a transition already covers the cut).
    dy moves the whole composition down: keep its centre of mass near y 900, never a top-heavy card."""
    dy += rk.STAGE_DY
    if dy:
        inner = f'<div class="pr-c" style="transform:translateY({dy}px)">{inner}</div>'
    wrap = card_layer(s, name, g0, g1, inner, z=z, leaf_op=leaf)
    t = s.L(g0)
    if enter == "up":
        J(s, f'tl.fromTo($("{wrap}"), {{ y: 1960 }}, {{ y: 0, duration: 0.26, ease: "power3.out" }}, {t});')
    elif enter == "right":
        J(s, f'tl.fromTo($("{wrap}"), {{ x: 1100 }}, {{ x: 0, duration: 0.26, ease: "power3.out" }}, {t});')
    elif enter == "whip":
        J(s, f'whipIn($("{wrap}"), {t}, 760, 0.28);')
    elif enter == "flip":
        J(s, f'tl.fromTo($("{wrap}"), {{ rotationY: -80, transformPerspective: 1800, opacity: 0.4 }}, {{ rotationY: 0, transformPerspective: 1800, opacity: 1, duration: 0.3, ease: "power3.out" }}, {t});')
    elif enter == "zoom":
        J(s, f'tl.fromTo($("{wrap}"), {{ scale: 0.72, filter: "blur(16px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.3, ease: "power3.out" }}, {t});')
    return wrap


def split_at(s, name, g0, g1, zoom=1.0, leaf=0.3, rise=True, origin="540px 900px", shift=None):
    """SPLIT beat (paper top half, speaker card bottom half). zoom 1.22 is the framing change that hides a jump cut
    between two SPLIT beats; shift sets the face-card shift from here on (the speaker moved in the frame)."""
    if shift is not None:
        set_shift(shift)
    s.paper(f"{name}-bg", g0, g1, leaf_op=leaf)
    face = facecard_c(s, f"{name}-face", g0, g1, zoom=zoom, origin=origin)
    if rise:
        face_rise(s, face, g0)
    return face


def expand(s, face, g_end, d=0.28):
    """The SPLIT card opens to full frame right before a cut to a PUNCH or DEPTH beat."""
    card_expand(s, face, g_end, d)


def depth_keys():
    return ((0, 1.08, "power3.out"), (0.36, 1.0, "none"), (None, 1.035, None))


def keys_cue(reel, t0, n, gap=0.09, vol=0.22):
    """n keyboard clicks for typed text."""
    for i in range(n):
        reel.cue(t0 + i * gap, f"key-{i % 6}", vol)


# ---------------------------------------------------------------- write everything
def _shade(hex_, f):
    h = hex_.lstrip("#")
    r, g_, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if f < 0:                                                      # darker
        r, g_, b = (round(c * (1 + f)) for c in (r, g_, b))
    else:                                                          # towards white
        r, g_, b = (round(c + (255 - c) * f) for c in (r, g_, b))
    return f"#{r:02X}{g_:02X}{b:02X}"


def finish(reel, project, accent=None):
    """Write compositions/*.html + index.html, recolour the teal accent family to `accent` (e.g. "#C9271C" red,
    "#2D5BFF" blue) everywhere, and pre-mix every sound cue into assets/sfx_mix.wav. Returns a short report."""
    project = Path(project)
    out = [reel.write(project)]
    if accent and accent.upper() != TEAL:
        deep = _shade(accent, -0.32)
        fam = {TEAL: accent.upper(), TEAL_D: deep, TEAL_T: _shade(accent, 0.84), "#BFDDD7": _shade(accent, 0.72),
               "rgba(7,84,80,": "rgba({},{},{},".format(*(int(deep[i:i + 2], 16) for i in (1, 3, 5)))}
        for f in list((project / "compositions").glob("*.html")) + [project / "index.html"]:
            t = f.read_text(encoding="utf-8")
            for a_, b_ in fam.items():
                t = re.sub(re.escape(a_), b_, t, flags=re.I)
            f.write_text(t, encoding="utf-8")
        out.append(f"accent -> {accent}")
    out.append(premix_sfx(reel, project))
    return "\n".join(out)


__all__ = [n for n in dir() if not n.startswith("__")]
