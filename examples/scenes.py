"""Worked example — "Claude edits my videos" (75.4 s, 30 fps), built with the video-edit skill.

Raw: one 5:26 iPhone take full of retakes -> 16 takes (examples/takes.json) -> a 73.67 s voice track.
Times are GLOBAL seconds on the tightened timeline (build/words.json). Run from the reel project: python build/scenes.py
-> compositions/*.html + index.html + assets/sfx_mix.wav. Scenes s01-s07 here, s08-s14 in scenes_b.py (exec'd below).

Assets this example expects (yours will be different — copy the patterns, not the files):
  assets/aroll_wide.mp4, aroll_tight.mp4, voice.wav   aroll.py
  assets/depth_views|styles|attention.webm            make_matte.py (DEPTH beats)
  assets/bv/*.mp4                                     prep_broll.py: moments of the creator's own earlier reels
  assets/img/strip/sprite.jpg + strip.json            strip.py (raw 5:26 -> edited 1:14 proof)
  assets/img/stills/raw.jpg                           one frame of the raw take ("before" phone; HDR converted)
  assets/img/stills/*.jpg                             frames of those reels; assets/img/cc/*.jpg captures of the
  assets/img/logo-claude.svg                          product's own website; the brand's own logo
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ.get("VIDEO_EDIT_SCRIPTS", str(Path.home() / ".claude" / "skills" / "video-edit" / "scripts")))
from video_kit import *  # noqa: F401,F403,E402
from video_kit import expand as _expand, keys_cue as _keys_cue, split_at as _split_at  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
TOTAL = 75.40
VOICE = 73.667
configure(face_shift=640)            # aroll.py --face: head top ~714 px in the first part of the recording
reel = Reel(total=TOTAL, fps=30, voice_dur=VOICE)
C = reel.cue
T = reel.ting
CLOSE_AT = 50.80                     # the speaker moved closer to the camera here: head top ~654 px


def shift_for(g):
    return 570 if g >= CLOSE_AT - 0.01 else 640


def split_at(s, name, g0, g1, **kw):
    return _split_at(s, name, g0, g1, shift=shift_for(g0), **kw)


def expand(s, face, g_end, d=0.28):
    set_shift(shift_for(g_end - 0.5))
    _expand(s, face, g_end, d)


def keys_cue(t0, n, gap=0.09, vol=0.22):
    _keys_cue(reel, t0, n, gap, vol)


def claude_tile(cid, x, y, size, style=""):
    return logo_tile(cid, f"{IMG}logo-claude.svg", x, y, size, style=style)


# ======================================================================================================
# S01 — Hook (0.00–3.73): DEPTH "views" behind his head → SPLIT before/after phones ("I changed my video style")
# ======================================================================================================
s = reel.scene("s01", "hook", 0.00, 3.73)
KV = ((0, 1.07, "power2.out"), (0.5, 1.0, "none"), (None, 1.035, None))
fullv(s, "base", 0.00, 1.84, A_WIDE, 1, origin="520px 900px", keys=KV)
word = (srow("s01-w", "views", 455, 440, "ink", "letter-spacing:-.03em")
        + f'<div id="s01-up" class="pr-ic" style="left:842px;top:350px;width:150px;height:150px;opacity:0">{icon("trending-up", TEAL, 2.6)}</div>')
lay(s, "mid", 0.00, 1.84, 2, word)
fullv(s, "matte", 0.00, 1.84, "assets/depth_views.webm", 3, origin="520px 900px", keys=KV, media_start=0.0)
J(s, f'slam($("s01-w"), {s.L(1.22)}, {{ s: 1.45, d: 0.3 }});')
J(s, f'tl.to($("s01-w"), {{ scale: 1.05, duration: 0.6, ease: "none" }}, {s.L(1.52)});')
J(s, f'pop($("s01-up"), {s.L(1.40)}, {{ s: 0.3, d: 0.36, rot: -10 }});')
plates(s, "cap", [Pc("My video started", 0.02, 0.80), Pc("getting more", 0.80, 1.84)])
C(0.02, "swoosh-up", 0.18); C(1.24, "glint", 0.34); C(1.40, "pop-small", 0.3)

# --- SPLIT: before / after (1.84–3.73) ----------------------------------------------------------------
face = split_at(s, "b", 1.84, 3.73)
pa = phone("s01-pa", 150, 150, 330, 640, IMG + "stills/raw.jpg")
lab = (chip("s01-la", "before", 228, 96, 40, "alt", "opacity:0") + chip("s01-lb", "after", 690, 96, 40, "hero", "opacity:0"))
lay(s, "b-top", 1.84, 3.73, 3, inner=pa + lab + s.seam_caps([("because I changed", 1.84, 2.88), ("my video style.", 2.88, 3.73)]))
pb = phone_vid(s, "pb", 2.40, 3.73, "africa-a", 600, 150, 330, 640, z=4, media_start=0.6)
J(s, f'tl.fromTo($("s01-pa"), {{ opacity: 0, y: 300, rotation: -12 }}, {{ opacity: 1, y: 0, rotation: -5, duration: 0.46, ease: "back.out(1.4)" }}, {s.L(1.90)});')
J(s, f'pop($("s01-la"), {s.L(2.04)}, {{ s: 0.4, d: 0.3, rot: -5 }});')
J(s, f'tl.fromTo($("{pb}"), {{ y: 340, rotation: 14, scale: 0.9 }}, {{ y: 0, rotation: 5, scale: 1, duration: 0.5, ease: "back.out(1.5)" }}, {s.L(2.40)});')
J(s, f'tl.to([$("s01-pa"), $("s01-la")], {{ opacity: 0.45, scale: 0.92, duration: 0.3, ease: "power2.out" }}, {s.L(2.50)});')
J(s, f'pop($("s01-lb"), {s.L(2.60)}, {{ s: 0.4, d: 0.34, rot: 5 }});')
J(s, f'tl.fromTo($("{pb}"), {{ scale: 1 }}, {{ scale: 1.06, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, {s.L(3.36)});')
expand(s, face, 3.73)
C(1.90, "paper-slide", 0.3); C(2.42, "sparkle-1", 0.46); C(2.62, "pop-small", 0.26); C(3.38, "glint", 0.24)

# ======================================================================================================
# S02 — "And even though I have less followers, I get more views because" (3.73–8.43): PUNCH → CARD bars
# ======================================================================================================
s = reel.scene("s02", "followers", 3.73, 8.43)
punch(s, "a", 3.73, 5.43)
plates(s, "acap", [Pc("And even though", 3.80, 4.80), Pc("I have", 4.80, 5.43)])
paper_cover(s, "cov", 5.43)
T(3.73)
BX0, BW, BASE = 230, 250, 1110
bars = (
    f'<div id="s02-fb" style="position:absolute;left:{BX0}px;top:{BASE - 190}px;width:{BW}px;height:190px;border-radius:30px 30px 10px 10px;background:#D8CFC1"></div>'
    f'<div id="s02-vb" style="position:absolute;left:{BX0 + 370}px;top:{BASE - 640}px;width:{BW}px;height:640px;border-radius:30px 30px 10px 10px;background:{TEAL};box-shadow:0 20px 44px rgba(7,84,80,.28)"></div>'
    f'<div style="position:absolute;left:150px;top:{BASE}px;width:780px;height:8px;border-radius:4px;background:#17140F"></div>'
    f'<div id="s02-fl" class="bx-sans" style="left:{BX0 - 20}px;width:{BW + 40}px;text-align:center;top:{BASE + 30}px;font-size:46px;color:#746D62">followers</div>'
    f'<div id="s02-vl" class="bx-sans" style="left:{BX0 + 350}px;width:{BW + 40}px;text-align:center;top:{BASE + 30}px;font-size:46px;color:#17140F">views</div>'
    f'<div id="s02-fi" class="pr-ic" style="left:{BX0 + 85}px;top:{BASE - 290}px;width:80px;height:80px">{icon("users", "#746D62", 2.2)}</div>'
    f'<div id="s02-vi" class="pr-ic" style="left:{BX0 + 455}px;top:{BASE - 750}px;width:80px;height:80px">{icon("eye", TEAL, 2.4)}</div>'
)
heads = (srow("s02-h1", f'{g("less")} followers,', 150, 150)
         + srow("s02-h2", f'{g("I get")} more views', 1260, 128)
         + nrow("s02-h3", f'{gl("because")}…', 1420, 64))
wrap = card(s, "b", 5.43, 8.43, heads + bars, z=5, enter="none")
J(s, f'rise($("s02-h1"), {s.L(5.46)}, {{ y: 40, d: 0.32 }});')
J(s, f'tl.fromTo($("s02-fb"), {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 0.4, ease: "back.out(1.6)" }}, {s.L(5.62)});')
J(s, f'tl.fromTo([$("s02-fl"), $("s02-fi")], {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.24 }}, {s.L(5.66)});')
J(s, f'tl.fromTo($("s02-vb"), {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, transformOrigin: "50% 100%", duration: 0.9, ease: "power3.out" }}, {s.L(6.80)});')
J(s, f'tl.fromTo($("s02-vi"), {{ opacity: 0, y: 560 }}, {{ opacity: 1, y: 0, duration: 0.9, ease: "power3.out" }}, {s.L(6.80)});')
J(s, f'tl.fromTo($("s02-vl"), {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.24 }}, {s.L(6.84)});')
J(s, f'tl.to($("s02-h1"), {{ opacity: 0.35, duration: 0.3 }}, {s.L(6.80)});')
J(s, f'slam($("s02-h2"), {s.L(7.10)}, {{ s: 1.3, d: 0.28 }});')
J(s, f'rise($("s02-h3"), {s.L(7.92)}, {{ y: 24, d: 0.24 }});')
whip_out(s, wrap, 8.43, d=0.18, dx=-760)
C(5.42, "paper-slide", 0.34); C(5.64, "click-1", 0.24); C(6.82, "riser", 0.2, 0.7); C(7.12, "glint", 0.34)
C(7.94, "click-2", 0.2); C(8.26, "whoosh-quick", 0.26)

# ======================================================================================================
# S03 — "I made Claude do the editing for me." (8.43–10.77): SPLIT Claude tile + hero chip debut + the real prompt
# ======================================================================================================
s = reel.scene("s03", "claude", 8.43, 10.77)
face = split_at(s, "a", 8.43, 10.77)
PROMPT = "edit this video @IMG_2495.MOV using /paper-reel"
prm = (f'<div id="s03-prm" class="bx-term" style="left:70px;top:440px;width:940px;height:330px">'
       f'<div class="bx-tbar"><i style="left:26px;background:#E06C55"></i><i style="left:56px;background:#E3B341"></i>'
       f'<i style="left:86px;background:#6CB27A"></i><span>claude</span></div>'
       f'<div class="bx-tl" style="top:96px;left:40px;right:40px;white-space:normal;font-size:44px;line-height:1.3">'
       f'<span style="color:{TEAL};font-weight:700">›</span> <span id="s03-typed"></span><span class="bx-caret"></span></div></div>')
top = claude_tile("s03-ct", 120, 110, 260) + chip("s03-hc", "Claude&nbsp;Code", 430, 190, 76, "hero", "opacity:0") + prm
lay(s, "a-top", 8.43, 10.77, 3, inner=top + s.seam_caps([("I made Claude", 8.43, 9.52), ("do the editing", 9.52, 10.32), ("for me.", 10.32, 10.77)]))
J(s, f'pop($("s03-ct"), {s.L(8.84)}, {{ s: 0.3, d: 0.42, rot: -8 }});')
J(s, f'pop($("s03-hc"), {s.L(9.00)}, {{ s: 0.4, d: 0.36, rot: -3 }});')
J(s, f'rise($("s03-prm"), {s.L(9.30)}, {{ y: 120, d: 0.36 }});')
J(s, f'typeIn($("s03-typed"), "{PROMPT}", {s.L(9.44)}, 1.05);')
leak_out(s, 10.77)
C(8.86, "sparkle-2", 0.46); C(9.02, "pop-small", 0.3); keys_cue(9.46, 10, 0.1, 0.2); C(10.62, "whoosh-reverse", 0.22)

# ======================================================================================================
# S04 — creators (10.77–16.07): CARD avatars → PUNCH "are using now." → SPLIT "make more videos" (video cards)
# ======================================================================================================
s = reel.scene("s04", "creators", 10.77, 16.07)
AVS = [(150, 560, 170), (350, 470, 200), (580, 450, 220), (820, 540, 160), (250, 790, 150), (720, 800, 170)]
avs = "".join(avatar(f"s04-av{i}", x, y, sz, i) for i, (x, y, sz) in enumerate(AVS))
caps = (srow("s04-c1", "most of your favorite", 170, 112, "grey")
        + srow("s04-c2", "content creators", 1060, 176))
wrap = card(s, "a", 10.77, 13.17, avs + caps, z=5, enter="none", dy=110)
leak_in(s, 10.77)
J(s, f'rise($("s04-c1"), {s.L(10.92)}, {{ y: 30, d: 0.3 }});')
for i in range(len(AVS)):
    J(s, f'pop($("s04-av{i}"), {s.L(11.05) + i * 0.13:.3f}, {{ s: 0.3, d: 0.4 }});')
    J(s, f'floatY($("s04-av{i}"), {s.L(11.6) + i * 0.05:.3f}, 1.2, {-14 if i % 2 else 12});')
J(s, f'slam($("s04-c2"), {s.L(12.24)}, {{ s: 1.35, d: 0.3 }});')
zoom_through(s, wrap, 13.17, d=0.18, scale=1.9)
for i in range(len(AVS)):
    C(11.07 + i * 0.13, f"click-{i % 3 + 1}", 0.2)
C(12.26, "glint", 0.32); C(13.02, "swoosh-up", 0.26)
# B — PUNCH
punch(s, "b", 13.17, 14.17)
plates(s, "bcap", [Pc(f'are using {acc("now.")}', 13.20, 14.17, "serif", 120, "", "pop")])
T(13.17)
# C — SPLIT: they make more videos (cards multiply)
face = split_at(s, "c", 14.17, 16.07)
VC = [(390, 190, 300, 420, 0), (200, 230, 260, 360, -10), (620, 230, 260, 360, 10), (90, 300, 220, 300, -18), (770, 300, 220, 300, 18)]
vcs = "".join(vcard(f"s04-v{i}", x, y, w, h, f"transform:rotate({r}deg)") for i, (x, y, w, h, r) in enumerate(VC))
lay(s, "c-top", 14.17, 16.07, 3, inner=vcs + s.seam_caps([("They are able to", 14.17, 14.96), ("make more videos,", 14.96, 16.07)]))
J(s, f'pop($("s04-v0"), {s.L(14.30)}, {{ s: 0.5, d: 0.38 }});')
for i in range(1, len(VC)):
    J(s, f'tl.fromTo($("s04-v{i}"), {{ opacity: 0, y: 260, x: {(-1 if VC[i][4] < 0 else 1) * -120} }}, {{ opacity: 1, y: 0, x: 0, duration: 0.4, ease: "back.out(1.5)" }}, {s.L(14.98) + (i - 1) * 0.14:.3f});')
C(14.32, "card-place-1.ogg", 0.3)
for i in range(4):
    C(15.00 + i * 0.14, "card-place-2.ogg" if i % 2 else "card-place-1.ogg", 0.26)

# ======================================================================================================
# S05 — "they're able to engage with their audience and keep their audience watching" (16.07–19.87)
# ======================================================================================================
s = reel.scene("s05", "engage", 16.07, 19.87)
face = split_at(s, "a", 16.07, 17.90, zoom=1.22, origin="520px 900px", rise=False)
ph = phone_vid(s, "ph", 16.07, 17.90, "brag-a", 390, 120, 300, 640, z=4, media_start=0.2)
ENG = [("heart", 170, 250, "#E5483B", 16.66), ("message-circle", 780, 300, INK, 16.96), ("bookmark", 160, 560, INK, 17.28), ("send", 790, 600, INK, 17.50)]
engs = "".join(eng(f"s05-e{i}", n, x, y, col) for i, (n, x, y, col, t) in enumerate(ENG))
lay(s, "a-top", 16.07, 17.90, 5, inner=engs + s.seam_caps([("they're able to engage", 16.07, 17.28), ("with their audience", 17.28, 17.90)]))
J(s, f'tl.fromTo($("{ph}"), {{ y: 300, rotation: 8 }}, {{ y: 0, rotation: 0, duration: 0.42, ease: "back.out(1.4)" }}, {s.L(16.10)});')
for i, (n, x, y, col, t) in enumerate(ENG):
    J(s, f'pop($("s05-e{i}"), {s.L(t)}, {{ s: 0.3, d: 0.36, rot: {-12 if i % 2 else 12} }});')
    J(s, f'floatY($("s05-e{i}"), {s.L(t) + 0.36:.3f}, 0.8, -16);')
paper_cover(s, "cov", 17.90)
C(16.12, "sparkle-3", 0.42)
for i, (n, x, y, col, t) in enumerate(ENG):
    C(t, "bubble-pop" if i % 2 == 0 else "pop-small", 0.26)
# B — CARD: keep them watching (retention bar fills to the end)
eye = f'<div id="s05-eye" class="pr-ic" style="left:440px;top:430px;width:200px;height:200px">{icon("eye", INK, 1.6)}</div>'
ret = retention("s05-rt", 160, 800, 760)
ticks = "".join(f'<div style="position:absolute;left:{160 + round(760 * k / 4) - 2}px;top:846px;width:4px;height:22px;border-radius:2px;background:#D8CFC1"></div>' for k in range(5))
pct = '<div id="s05-pc" class="clk" style="left:0;width:1080px;text-align:center;top:890px;font-size:56px;opacity:0">watch time</div>'
caps = srow("s05-c1", "and keep their audience", 170, 108, "grey") + srow("s05-c2", "watching", 1060, 250)
wrap = card(s, "b", 17.90, 19.87, eye + ret + ticks + pct + caps, z=6, enter="none", dy=170)
J(s, f'rise($("s05-c1"), {s.L(17.94)}, {{ y: 30, d: 0.3 }}); pop($("s05-eye"), {s.L(18.00)}, {{ s: 0.5, d: 0.4 }});')
J(s, f'tl.fromTo($("s05-rt-f"), {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.5, ease: "power1.inOut" }}, {s.L(18.20)});')
J(s, f'tl.to($("s05-pc"), {{ opacity: 1, duration: 0.2 }}, {s.L(18.24)});')
J(s, f'tl.fromTo($("s05-eye"), {{ scaleY: 1 }}, {{ scaleY: 0.1, duration: 0.07, yoyo: true, repeat: 1, ease: "power2.in", immediateRender: false }}, {s.L(18.90)});')
J(s, f'slam($("s05-c2"), {s.L(19.36)}, {{ s: 1.35, d: 0.3 }});')
flip_out(s, wrap, 19.87)
C(17.88, "paper-slide", 0.32); C(18.22, "tick", 0.2); C(18.62, "tick", 0.2); C(19.02, "tick", 0.2); C(19.38, "glint", 0.3); C(19.70, "ding", 0.3)

# ======================================================================================================
# S06 — "because they have motion graphics, animations, and different styles like this" (19.87–26.00)
# ======================================================================================================
s = reel.scene("s06", "motion", 19.87, 26.00)
curve = ('<svg id="s06-sv" style="position:absolute;left:140px;top:420px;width:800px;height:520px;overflow:visible" viewBox="0 0 800 520">'
         '<path d="M40 480 L760 480" stroke="#D8CFC1" stroke-width="6" stroke-linecap="round"/>'
         '<path d="M40 480 L40 40" stroke="#D8CFC1" stroke-width="6" stroke-linecap="round"/>'
         '<path id="s06-cv" d="M40 480 C 330 480, 380 40, 760 40" fill="none" stroke="#0B7A73" stroke-width="14" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
         '<line x1="40" y1="480" x2="330" y2="480" stroke="#17140F" stroke-width="4" stroke-dasharray="10 10"/>'
         '<line x1="760" y1="40" x2="380" y2="40" stroke="#17140F" stroke-width="4" stroke-dasharray="10 10"/>'
         '<circle cx="330" cy="480" r="16" fill="#17140F"/><circle cx="380" cy="40" r="16" fill="#17140F"/></svg>')
dot = '<div id="s06-dot" style="position:absolute;left:160px;top:880px;width:44px;height:44px;border-radius:50%;background:#17140F;box-shadow:0 8px 18px rgba(20,15,10,.3)"></div>'
shapes = ('<div id="s06-sq" style="position:absolute;left:790px;top:300px;width:110px;height:110px;border-radius:26px;background:#0B7A73"></div>'
          '<div id="s06-ci" style="position:absolute;left:160px;top:300px;width:120px;height:120px;border-radius:50%;background:#E3B341"></div>'
          '<div id="s06-tr" style="position:absolute;left:520px;top:990px;width:0;height:0;border-left:70px solid transparent;border-right:70px solid transparent;border-bottom:120px solid #17140F"></div>')
kf = "".join(f'<div id="s06-k{i}" style="position:absolute;left:{210 + i * 160}px;top:1010px;width:40px;height:40px;background:#0B7A73;transform:rotate(45deg);border-radius:6px"></div>' for i in range(5))
caps = srow("s06-c1", "because they have", 150, 104, "grey") + srow("s06-c2", "motion graphics", 1150, 176)
wrap = card(s, "a", 19.87, 22.67, curve + dot + shapes + kf.replace('top:1010px', 'top:1380px') + caps, z=5, enter="flip", dy=110)
J(s, f'rise($("s06-c1"), {s.L(19.96)}, {{ y: 30, d: 0.3 }});')
J(s, f'tl.to($("s06-cv"), {{ strokeDashoffset: 0, duration: 0.8, ease: "power2.inOut" }}, {s.L(20.30)});')
J(s, f'tl.fromTo($("s06-dot"), {{ x: 0, y: 0 }}, {{ keyframes: [{{ x: 180, y: -20, duration: 0.25 }}, {{ x: 400, y: -250, duration: 0.3 }}, {{ x: 720, y: -440, duration: 0.25 }}], ease: "none" }}, {s.L(20.30)});')
J(s, f'tl.fromTo($("s06-sq"), {{ opacity: 0, rotation: -90, scale: 0.2 }}, {{ opacity: 1, rotation: 0, scale: 1, duration: 0.5, ease: "back.out(2)" }}, {s.L(20.50)});')
J(s, f'tl.fromTo($("s06-ci"), {{ opacity: 0, y: -300 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "bounce.out" }}, {s.L(20.60)});')
J(s, f'tl.fromTo($("s06-tr"), {{ opacity: 0, x: 400, rotation: 120 }}, {{ opacity: 1, x: 0, rotation: 0, duration: 0.5, ease: "power3.out" }}, {s.L(20.80)});')
J(s, f'slam($("s06-c2"), {s.L(20.96)}, {{ s: 1.35, d: 0.3 }});')
for i in range(5):
    J(s, f'pop($("s06-k{i}"), {s.L(21.30) + i * 0.08:.3f}, {{ s: 0.2, d: 0.3, rot: 45 }});')
J(s, f'tl.to($("s06-sq"), {{ rotation: 180, borderRadius: "60px", duration: 0.7, ease: "power2.inOut" }}, {s.L(21.60)});')
J(s, f'tl.to($("s06-ci"), {{ scale: 1.25, duration: 0.35, yoyo: true, repeat: 1, ease: "sine.inOut" }}, {s.L(21.70)});')
whip_out(s, wrap, 22.67, d=0.18, dx=-800)
C(19.87, "whoosh", 0.26); C(20.32, "swoosh-up", 0.22); C(20.52, "pop", 0.26); C(20.66, "bubble-pop", 0.22); C(20.98, "glint", 0.34)
for i in range(5):
    C(21.30 + i * 0.08, "click-3", 0.16)
C(22.50, "whoosh-quick", 0.26)
# B — CARD (held): animations + four of his reels in four styles
words = "".join(f'<span id="s06-a{i}" style="display:inline-block">{ch}</span>' for i, ch in enumerate("animations,"))
anim = srow("s06-an", words, 96, 170)
sty = srow("s06-st", f'{g("different")} styles', 1490, 150)
GRID = [("brag-b", 190, 300, 0.3), ("privacy-a", 590, 300, 0.0), ("money-a", 190, 870, 0.2), ("africa-b", 590, 870, 0.4)]
wrap = card(s, "b", 22.67, 25.03, anim + sty, z=5, enter="whip")
for i, (clip, x, y, ms) in enumerate(GRID):
    pid = phone_vid(s, f"g{i}", 22.67, 25.03, clip, x, y, 300, 540, z=6, media_start=ms)
    J(s, f'tl.fromTo($("{pid}"), {{ scale: 0.6, y: 120 }}, {{ scale: 1, y: 0, duration: 0.42, ease: "back.out(1.5)" }}, {s.L(22.72) + i * 0.1:.3f});')
J(s, f'tl.set($("s06-an"), {{ opacity: 1 }}, {s.L(22.70)});')
for i in range(11):
    J(s, f'tl.fromTo($("s06-a{i}"), {{ y: -160, scaleY: 1.4, opacity: 0 }}, {{ y: 0, scaleY: 1, opacity: 1, duration: 0.5, ease: "bounce.out" }}, {s.L(22.72) + i * 0.035:.3f});')
J(s, f'slam($("s06-st"), {s.L(24.16)}, {{ s: 1.3, d: 0.3 }});')
zoom_through(s, wrap, 25.03, d=0.16, scale=1.8)
C(22.76, "sparkle-2", 0.46); C(22.90, "bubble-pop", 0.2); C(24.18, "glint", 0.3); C(24.90, "swoosh-up", 0.24)
# C — PUNCH "like this." in a camera viewfinder
punch(s, "c", 25.03, 26.00)
lay(s, "c-vf", 25.03, 26.00, 5, viewfinder("s06-vf"))
J(s, f'tl.fromTo($("s06-vf"), {{ opacity: 0, scale: 1.12 }}, {{ opacity: 1, scale: 1, duration: 0.22, ease: "power3.out" }}, {s.L(25.08)});')
J(s, f'blink($("s06-vf-dot"), {s.L(25.30)}, 3);')
plates(s, "ccap", [Pc(f'like {acc("this.")}', 25.10, 26.00, "serif", 124, "", "pop")])
T(25.03); C(25.12, "shutter", 0.34)

# ======================================================================================================
# S07 — "And this is how I'm also able to keep my followers' attention using these same styles. And there are
#        different styles that you can copy." (26.00–33.53): SPLIT his reels → DEPTH "styles" → CARD swatches + ⌘C
# ======================================================================================================
s = reel.scene("s07", "mine", 26.00, 33.53)
face = split_at(s, "a", 26.00, 29.43)
FAN = [("privacy-b", 110, 190, -9, 0.0), ("money-b", 720, 190, 9, 0.3), ("africa-a", 390, 130, 0, 0.4)]
for i, (clip, x, y, r, ms) in enumerate(FAN):
    pid = phone_vid(s, f"f{i}", 26.00, 29.43, clip, x, y, 300, 600, z=4 + i, media_start=ms)
    J(s, f'tl.fromTo($("{pid}"), {{ y: 420, rotation: {r * 2} }}, {{ y: 0, rotation: {r}, duration: 0.5, ease: "back.out(1.4)" }}, {s.L(26.10) + i * 0.12:.3f});')
ring = (f'<div id="s07-ring" style="position:absolute;left:372px;top:112px;width:336px;height:636px;border-radius:66px;border:8px solid {TEAL};opacity:0"></div>'
        f'<div id="s07-eye" class="eng" style="left:488px;top:690px;opacity:0">{icon("eye", TEAL, 2.4)}</div>')
lay(s, "a-top", 26.00, 29.43, 8, inner=ring + s.seam_caps([("And this is how", 26.00, 26.72), ("I'm also able", 26.72, 27.60),
                                                            ("to keep my followers'", 27.60, 28.80), ("attention", 28.80, 29.43)]))
J(s, f'tl.fromTo($("s07-ring"), {{ opacity: 0, scale: 1.12 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {s.L(28.80)});')
J(s, f'pop($("s07-eye"), {s.L(28.86)}, {{ s: 0.3, d: 0.34 }});')
expand(s, face, 29.43)
C(26.12, "sparkle-1", 0.44); C(26.24, "card-place-1.ogg", 0.24); C(26.36, "card-place-2.ogg", 0.24); C(28.82, "blip", 0.3)
# B — DEPTH "styles"
KS = depth_keys()
fullv(s, "base", 29.43, 31.10, A_WIDE, 1, origin="520px 900px", keys=KS)
lay(s, "word", 29.43, 31.10, 2, srow("s07-w", "styles", 380, 420, "ink", "letter-spacing:-.03em"))
fullv(s, "matte", 29.43, 31.10, "assets/depth_styles.webm", 3, origin="520px 900px", keys=KS, media_start=round(29.43 - 29.40, 3))
J(s, f'slam($("s07-w"), {s.L(30.40)}, {{ s: 1.45, d: 0.3 }});')
plates(s, "bcap", [Pc("using these same", 29.48, 30.40)])
bars_out(s, 31.10)
C(30.42, "glint", 0.34); C(30.44, "pop-deep", 0.2); C(30.96, "swoosh-short", 0.28)
# C — CARD: different styles you can copy (⌘C duplicates a style card)
SW = [("s07-s0", 90, 330, TEAL, -8), ("s07-s1", 300, 300, "#D9653B", -3), ("s07-s2", 520, 300, "#C9271C", 3), ("s07-s3", 730, 330, "#2F6B4A", 8)]
sws = "".join(swatch(cid, x, y, 270, 380, col, "Aa", f"transform:rotate({r}deg)") for cid, x, y, col, r in SW)
copy = swatch("s07-cp", 300, 300, 270, 380, "#D9653B", "Aa", "opacity:0;transform:rotate(-3deg)")
keys = keycap("s07-k1", "⌘", 360, 900) + keycap("s07-k2", "C", 560, 900)
caps = (srow("s07-c1", f'{g("different")} styles', 1190, 150)
        + srow("s07-c2", f'{g("that you can")} {acc("copy")}', 1360, 128))
wrap = card(s, "c", 31.10, 33.53, sws + copy + keys + caps, z=5, enter="none")
bars_in(s, 31.10)
for i, (cid, x, y, col, r) in enumerate(SW):
    J(s, f'tl.fromTo($("{cid}"), {{ opacity: 0, y: 380, rotation: {r * 3} }}, {{ opacity: 1, y: 0, rotation: {r}, duration: 0.42, ease: "back.out(1.5)" }}, {s.L(31.20) + i * 0.12:.3f});')
J(s, f'slam($("s07-c1"), {s.L(31.60)}, {{ s: 1.25, d: 0.28 }});')
J(s, f'pop($("s07-k1"), {s.L(32.40)}, {{ s: 0.4, d: 0.3 }}); pop($("s07-k2"), {s.L(32.50)}, {{ s: 0.4, d: 0.3 }});')
J(s, f'press($("s07-k1"), {s.L(33.00)}); press($("s07-k2"), {s.L(33.02)});')
J(s, f'rise($("s07-c2"), {s.L(32.40)}, {{ y: 30, d: 0.3 }});')
J(s, f'tl.fromTo($("s07-cp"), {{ opacity: 0, x: 0, y: 0, rotation: -3 }}, {{ opacity: 1, x: 120, y: 120, rotation: 6, duration: 0.36, ease: "back.out(1.6)" }}, {s.L(33.06)});')
zoom_through(s, wrap, 33.53, d=0.16, scale=2.0)
for i in range(4):
    C(31.22 + i * 0.12, "card-place-1.ogg" if i % 2 == 0 else "card-place-2.ogg", 0.24)
C(31.62, "glint", 0.26); C(32.42, "pop-small", 0.22); C(33.00, "key-2", 0.4); C(33.03, "key-4", 0.36); C(33.08, "paper-slide", 0.3)
C(33.40, "swoosh-up", 0.24)

exec(compile((Path(__file__).resolve().parent / "scenes_b.py").read_text(encoding="utf-8"), "scenes_b.py", "exec"))

print(finish(reel, PROJECT))
