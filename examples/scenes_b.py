# s08–s14 — exec'd by scenes.py (shares its namespace: reel, C, T, plates, Pc, srow, nrow, card, split_at, expand ...)
import json as _json

# ======================================================================================================
# S08 — "Claude Code, now Claude can do all your video editing for you without knowing how to code." (33.53–39.17)
#        CARD real Claude Code page (name reveal) → SPLIT timeline assembles itself → PUNCH "how to code" struck
# ======================================================================================================
s = reel.scene("s08", "reveal", 33.53, 39.17)
CCW = 940
cc = pwin("s08-cc", 70, 300, CCW, 50 + round(CCW * 562 / 1400), f"{IMG}cc/cc-hero.jpg")
inner = (cc + claude_tile("s08-ct", 440, 840, 200)
         + chip_c("s08-hc", "Claude&nbsp;Code", 1110, 104, "hero", "opacity:0")
        )
wrap = card(s, "a", 33.53, 34.53, inner, z=5, enter="zoom")
J(s, f'tl.fromTo($("s08-cc"), {{ opacity: 0, y: 80, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.36, ease: "power3.out" }}, {s.L(33.56)});')
J(s, f'pop($("s08-ct"), {s.L(33.70)}, {{ s: 0.3, d: 0.4, rot: -10 }});')
J(s, f'slam($("s08-hc"), {s.L(33.78)}, {{ s: 1.5, d: 0.3 }});')
J(s, f'tl.to($("s08-cc"), {{ scale: 1.04, duration: 0.7, ease: "none" }}, {s.L(33.92)});')
whip_out(s, wrap, 34.53, d=0.16, dx=-820)
C(33.56, "sparkle-3", 0.48); C(33.80, "thud", 0.36); C(34.40, "whoosh-quick", 0.26)
# B — SPLIT: the edit assembles itself
face = split_at(s, "b", 34.53, 37.27)
TLW, TLX, TLY = 960, 60, 170
tlc = edit_timeline("s08-tl", TLX, TLY, TLW, 470, "your video — edited by Claude")
lay(s, "b-top", 34.53, 37.27, 3, inner=tlc + claude_tile("s08-ct2", 900, 110, 120)
    + s.seam_caps([("now Claude can do", 34.53, 35.52), ("all your", 35.52, 35.92), ("video editing", 35.92, 36.72), ("for you", 36.72, 37.27)]))
J(s, f'whipIn($("s08-tl"), {s.L(34.56)}, 700, 0.28);')
J(s, f'pop($("s08-ct2"), {s.L(34.72)}, {{ s: 0.3, d: 0.36, rot: 10 }});')
n = timeline_build(s, "s08-tl", 34.86, 0.04)
J(s, f'tl.fromTo($("s08-tl-ph"), {{ x: 0 }}, {{ x: {TLW - 110 - 28}, duration: 1.5, ease: "none" }}, {s.L(35.70)});')
expand(s, face, 37.27)
C(34.56, "whoosh", 0.24); C(34.74, "sparkle-1", 0.36)
for i in range(0, n, 3):
    C(34.86 + i * 0.04, f"click-{(i // 3) % 3 + 1}", 0.15)
C(35.72, "swoosh-short", 0.16)
# C — PUNCH: without knowing how to code (</> struck)
punch(s, "c", 37.27, 39.17)
code_pl = ('<div class="pl-row" style="top:1110px"><span id="s08-cd" class="pl mono" style="font-size:64px;opacity:0">'
           '&lt;/&gt; code<i id="s08-cd-x" class="pl-strike"></i></span></div>')
lay(s, "c-code", 37.27, 39.17, 7, code_pl)
J(s, f'pop($("s08-cd"), {s.L(38.40)}, {{ s: 0.5, d: 0.3 }});')
J(s, f'tl.set($("s08-cd-x"), {{ scaleX: 0 }}, 0);')
strike(s, "s08-cd", 38.86)
plates(s, "ccap", [Pc("without knowing", 37.30, 38.32), Pc("how to code.", 38.32, 39.17)])
paper_cover(s, "cov", 39.17)
T(37.27); C(38.42, "pop-small", 0.26); C(38.88, "marker", 0.42)

# ======================================================================================================
# S09 — "And you don't need to be a video editor, you don't need to install any software with just Claude Code."
#        (39.17–44.47): CARD empty editor struck → install dialog struck → SPLIT real Claude Code terminal
# ======================================================================================================
s = reel.scene("s09", "nosoftware", 39.17, 44.47)
edit_body = ('<div style="position:absolute;left:40px;top:30px;width:520px;height:300px;border:5px dashed #CFC4B3;border-radius:20px;background:#FBF8F3"></div>'
             f'<div class="pr-ic" style="left:255px;top:130px;width:90px;height:90px">{icon("clapperboard", "#BDB4A6", 1.8)}</div>'
             + "".join(f'<div style="position:absolute;left:40px;top:{360 + k * 54}px;width:{720 - 0 * k}px;height:40px;border-radius:10px;background:#EFE9E0"></div>' for k in range(3))
             + '<div style="position:absolute;left:600px;top:30px;width:160px;height:300px;border-radius:20px;background:#EFE9E0"></div>'
             + cursor_el("s09-cur", 470, 250, 1.2))
editor = win("s09-ed", 140, 400, 800, 590, edit_body, "untitled project")
part_a = (srow("s09-a1", "you don't need to be", 210, 104, "grey")
          + editor
          + '<div style="position:absolute;left:0;width:1080px;top:1090px;text-align:center">'
            '<span id="s09-a2" class="bx-serif bx-ink" style="position:relative;display:inline-block;font-size:170px;opacity:0" data-layout-allow-overlap>'
            f'a video editor<i id="s09-a2x" style="position:absolute;left:-3%;width:106%;top:54%;height:22px;border-radius:11px;background:{TEAL}"></i></span></div>')
inst = (f'<div id="s09-in" class="doc" style="left:150px;top:420px;width:780px;height:520px">'
        f'<div class="dic" style="left:40px;top:44px;width:110px;height:110px">{icon("download", "#FFFFFF", 2.2)}</div>'
        f'<div class="dt" style="left:180px;top:52px;font-size:70px">Installing…</div>'
        f'<div class="ds" style="left:182px;top:132px;font-size:24px">VIDEO EDITING SOFTWARE</div>'
        f'<div style="position:absolute;left:40px;top:250px;width:700px;height:30px;border-radius:15px;background:#E6DED3;overflow:hidden">'
        f'<i id="s09-pg" style="position:absolute;left:0;top:0;width:100%;height:100%;background:#8F877B;transform-origin:0% 50%;transform:scaleX(0)"></i></div>'
        f'<div id="s09-pct" class="clk" style="left:40px;top:310px;font-size:44px;color:#746D62">0%</div>'
        f'<div style="position:absolute;left:40px;top:400px;width:300px;height:80px;border-radius:40px;background:#EFE9E0"></div>'
        f'<div style="position:absolute;left:440px;top:400px;width:300px;height:80px;border-radius:40px;background:#D8CFC1"></div></div>')
part_b = (srow("s09-b1", "or install", 210, 104, "grey") + inst
          + '<div style="position:absolute;left:0;width:1080px;top:1090px;text-align:center">'
            '<span id="s09-b2" class="bx-serif bx-ink" style="position:relative;display:inline-block;font-size:180px;opacity:0" data-layout-allow-overlap>'
            f'any software<i id="s09-b2x" style="position:absolute;left:-3%;width:106%;top:54%;height:22px;border-radius:11px;background:{TEAL}"></i></span></div>'
          + f'<div id="s09-x" class="bdg x" style="left:880px;top:380px;width:120px;height:120px;opacity:0"></div>')
inner = f'<div id="s09-pa" class="pr-c">{part_a}</div><div id="s09-pb" class="pr-c">{part_b}</div>'
wrap = card(s, "a", 39.17, 43.03, inner, z=5, enter="none", dy=220)
J(s, f'tl.set([$("s09-a2x"), $("s09-b2x")], {{ scaleX: 0, transformOrigin: "0% 50%" }}, 0); tl.set($("s09-pb"), {{ y: 1960 }}, 0);')
J(s, f'rise($("s09-a1"), {s.L(39.22)}, {{ y: 30, d: 0.3 }});')
J(s, f'rise($("s09-ed"), {s.L(39.30)}, {{ y: 120, d: 0.4 }});')
J(s, f'tl.fromTo($("s09-cur"), {{ x: 0, y: 0 }}, {{ keyframes: [{{ x: -180, y: -80, duration: 0.5 }}, {{ x: 120, y: 60, duration: 0.5 }}, {{ x: -60, y: 140, duration: 0.4 }}], ease: "sine.inOut" }}, {s.L(39.50)});')
J(s, f'slam($("s09-a2"), {s.L(40.10)}, {{ s: 1.25, d: 0.26 }});')
J(s, f'growX($("s09-a2x"), {s.L(40.56)}, 0.24); tl.to($("s09-ed"), {{ opacity: 0.4, duration: 0.24 }}, {s.L(40.60)});')
J(s, f'tl.to($("s09-pa"), {{ y: -1960, duration: 0.3, ease: "power3.in" }}, {s.L(40.86)});')
J(s, f'tl.fromTo($("s09-pb"), {{ y: 1960 }}, {{ y: 0, duration: 0.3, ease: "power3.out" }}, {s.L(41.04)});')
J(s, f'tl.fromTo($("s09-b1"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {s.L(41.10)});')
J(s, f'tl.fromTo($("s09-pg"), {{ scaleX: 0 }}, {{ scaleX: 0.34, duration: 1.1, ease: "power1.in" }}, {s.L(41.40)});')
J(s, f'countTo($("s09-pct"), 0, 34, {s.L(41.40)}, 1.1, (v) => Math.round(v) + "%");')
J(s, f'slam($("s09-b2"), {s.L(42.40)}, {{ s: 1.25, d: 0.26 }});')
J(s, f'growX($("s09-b2x"), {s.L(42.62)}, 0.24); tick($("s09-x"), {s.L(42.66)});')
J(s, f'tl.to($("s09-in"), {{ opacity: 0.45, duration: 0.24 }}, {s.L(42.66)});')
J(s, f'shake($("s09-in"), {s.L(42.68)}, 12, 6, 0.04);')
C(39.24, "click-1", 0.2); C(39.34, "paper-slide", 0.26); C(40.12, "glint", 0.24); C(40.58, "marker", 0.42); C(40.88, "whoosh-quick", 0.26)
C(41.08, "pop-small", 0.24); C(41.5, "blip", 0.14); C(41.9, "blip", 0.14); C(42.3, "blip", 0.14); C(42.64, "marker", 0.4); C(42.68, "error", 0.26)
# B — SPLIT: with just Claude Code (real terminal capture)
face = split_at(s, "b", 43.03, 44.47)
term = (f'<div id="s09-tm" class="bx-frame" style="left:230px;top:120px;width:620px;height:620px;background-image:url({IMG}cc/cc-terminal.jpg)"></div>'
        + chip("s09-hc", "Claude&nbsp;Code", 300, 690, 76, "hero", "opacity:0"))
lay(s, "b-top", 43.03, 44.47, 3, inner=term + s.seam_caps([("with just", 43.03, 43.52), ("Claude Code.", 43.52, 44.47)]))
J(s, f'tl.fromTo($("s09-tm"), {{ opacity: 0, y: 240, rotation: -6, scale: 0.9 }}, {{ opacity: 1, y: 0, rotation: -2, scale: 1, duration: 0.46, ease: "back.out(1.4)" }}, {s.L(43.06)});')
J(s, f'slam($("s09-hc"), {s.L(43.56)}, {{ s: 1.4, d: 0.28 }});')
leak_out(s, 44.47)
C(43.08, "sparkle-1", 0.44); C(43.58, "pop", 0.28); C(44.32, "whoosh-reverse", 0.2)

# ======================================================================================================
# S10 — "You can edit your videos with animations, motion effects, and different sounds just like this."
#        (44.47–50.80): CARD the raw 5:26 strip collapses to the 1:14 edit → CARD sound chips (real waveforms)
# ======================================================================================================
s = reel.scene("s10", "proof", 44.47, 50.80)
ST_ = _json.loads((PROJECT / "assets" / "img" / "strip" / "strip.json").read_text())     # strip.py output
frames = [f"{IMG}strip/sprite.jpg"]
kept = ST_["kept"]
RAW_S, EDIT_S = round(ST_["raw_s"]), round(ST_["edit_s"])
strip = film_strip("s10-sp", frames, kept, 68, 470).replace('class="strip"', 'class="strip" data-layout-allow-overflow')
head = ('<div id="s10-lb" class="bx-mono bx-row" style="top:150px;font-size:32px;font-weight:700;letter-spacing:.22em;color:#746D62;opacity:0">'
        'IMG_2495.MOV · <span id="s10-st">RAW</span></div>'
        '<div id="s10-ck" class="clk" style="left:0;width:1080px;text-align:center;top:210px;font-size:170px;opacity:0">' + f'{RAW_S // 60}:{RAW_S % 60:02d}' + '</div>')
legend = ('<div id="s10-lg" class="bx-sans bx-row" style="top:690px;font-size:40px;color:#746D62;opacity:0">'
          f'repeated takes <span style="color:#17140F">✕</span> &nbsp;·&nbsp; best takes <span style="color:{TEAL}">✓</span></div>')
caps = (srow("s10-c1", "You can edit", 800, 110, "grey") + srow("s10-c2", "your videos", 920, 170))
chips = ('<div style="position:absolute;left:0;width:1080px;top:1180px;text-align:center">'
         '<span id="s10-h1" class="bx-chip" style="position:relative;display:inline-block;font-size:58px;opacity:0">animations</span>'
         '<span id="s10-h2" class="bx-chip" style="position:relative;display:inline-block;font-size:58px;margin-left:26px;opacity:0">motion effects</span></div>')
wrap = card(s, "a", 44.47, 48.67, head + strip + legend + caps + chips, z=5, enter="none", dy=140)
leak_in(s, 44.47)
J(s, f'rise($("s10-lb"), {s.L(44.52)}, {{ y: 20, d: 0.26 }}); pop($("s10-ck"), {s.L(44.58)}, {{ s: 0.6, d: 0.32 }});')
J(s, f'tl.fromTo($("s10-sp"), {{ x: 1100 }}, {{ x: 0, duration: 0.7, ease: "power3.out" }}, {s.L(44.56)});')
J(s, f'rise($("s10-c1"), {s.L(44.66)}, {{ y: 30, d: 0.3 }});')
cut_i = [i for i, k in enumerate(kept) if not k]
for j, i in enumerate(cut_i):
    t0 = s.L(45.40) + j * 0.03
    J(s, f'tl.to($("s10-sp-f{i}"), {{ scale: 0, opacity: 0, duration: 0.2, ease: "power2.in" }}, {t0:.3f});')
T_GATHER = s.L(45.40) + len(cut_i) * 0.03
for k_, i in enumerate([i for i, k in enumerate(kept) if k]):
    J(s, f'tl.to($("s10-sp-f{i}"), {{ x: {(k_ - i) * STRIP_STEP}, duration: 0.5, ease: "power3.inOut" }}, {T_GATHER - 0.3:.3f});')
J(s, f'tl.to($("s10-sp"), {{ x: {round((1080 - (sum(kept) * STRIP_STEP - 10)) / 2 - 68)}, duration: 0.5, ease: "power3.inOut" }}, {T_GATHER - 0.3:.3f});')
J(s, f'tl.to($("s10-lg"), {{ opacity: 1, duration: 0.24 }}, {s.L(45.50)});')
J(s, f'slam($("s10-c2"), {s.L(45.76)}, {{ s: 1.3, d: 0.28 }});')
J(s, f'countTo($("s10-ck"), {RAW_S}, {EDIT_S}, {s.L(45.50)}, 1.1, mmss);')
J(s, f'tl.to($("s10-ck"), {{ color: "{TEAL}", duration: 0.2 }}, {s.L(46.60)}); tl.set($("s10-st"), {{ textContent: "EDITED" }}, {s.L(46.60)});')
J(s, f'tl.fromTo($("s10-ck"), {{ scale: 1 }}, {{ scale: 1.12, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, {s.L(46.60)});')
J(s, f'pop($("s10-h1"), {s.L(46.72)}, {{ s: 0.4, d: 0.34, rot: -4 }}); pop($("s10-h2"), {s.L(47.60)}, {{ s: 0.4, d: 0.34, rot: 4 }});')
J(s, f'floatY($("s10-h1"), {s.L(47.10)}, 1.4, -10);')
flip_out(s, wrap, 48.67)
C(44.56, "whoosh-quick", 0.3); C(44.62, "sparkle-2", 0.3)
for j in range(0, len(cut_i), 3):
    C(45.40 + j * 0.03, f"click-{(j // 3) % 3 + 1}", 0.16)
C(46.62, "ding", 0.38); C(46.74, "pop-small", 0.28); C(47.62, "pop-small", 0.28)
# B — CARD: different sounds, drawn from the real files
WV = [("sparkle-1.wav", "sparkle", 110, 560, 48.96), ("ting-3.wav", "ting", 560, 560, 49.28),
      ("whoosh-quick.wav", "whoosh", 110, 790, 49.58), ("click-2.wav", "click", 560, 790, 49.88)]
wvs = "".join(wave_chip(f"s10-w{i}", f, lab, x, y, 410, 190) for i, (f, lab, x, y, t) in enumerate(WV))
caps = (srow("s10-d1", "and different", 150, 110, "grey") + srow("s10-d2", "sounds", 270, 230)
        + nrow("s10-d3", f'{gl("just like")} this.', 1120, 84))
wrap = card(s, "b", 48.67, 50.80, wvs + caps, z=6, enter="flip", dy=150)
J(s, f'rise($("s10-d1"), {s.L(48.70)}, {{ y: 30, d: 0.3 }}); slam($("s10-d2"), {s.L(48.90)}, {{ s: 1.3, d: 0.28 }});')
for i, (f, lab, x, y, t) in enumerate(WV):
    J(s, f'pop($("s10-w{i}"), {s.L(48.76) + i * 0.06:.3f}, {{ s: 0.6, d: 0.32 }});')
    J(s, f'tl.fromTo($("s10-w{i}-on"), {{ clipPath: "inset(0% 100% 0% 0%)" }}, {{ clipPath: "inset(0% 0% 0% 0%)", duration: 0.34, ease: "none" }}, {s.L(t)});')
    J(s, f'tl.fromTo($("s10-w{i}"), {{ scale: 1 }}, {{ scale: 1.05, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out", immediateRender: false }}, {s.L(t)});')
    C(t, f.replace(".wav", ""), 0.36 if "click" not in f else 0.3)
J(s, f'rise($("s10-d3"), {s.L(49.84)}, {{ y: 24, d: 0.26 }});')
zoom_through(s, wrap, 50.80, d=0.16, scale=2.0)
C(50.66, "swoosh-up", 0.24)

# ======================================================================================================
# S11 — "If you want to have an attention-grabbing video, then you need to use animation, motion styles, and some
#        B-rolls to keep your users watching all the time." (50.80–59.47): DEPTH → CARD checklist → SPLIT watch time
# ======================================================================================================
s = reel.scene("s11", "recipe", 50.80, 59.47)
KA = depth_keys()
fullv(s, "base", 50.80, 52.80, A_WIDE, 1, origin="550px 860px", keys=KA)
lay(s, "word", 50.80, 52.80, 2, srow("s11-w", "attention", 470, 262, "ink", "letter-spacing:-.03em"))
fullv(s, "matte", 50.80, 52.80, "assets/depth_attention.webm", 3, origin="550px 860px", keys=KA, media_start=round(50.80 - 50.77, 3))
J(s, f'slam($("s11-w"), {s.L(51.50)}, {{ s: 1.45, d: 0.3 }});')
J(s, f'tl.to($("s11-w"), {{ color: "{TEAL}", duration: 0.2 }}, {s.L(52.00)});')
plates(s, "acap", [Pc("If you want to have an", 50.84, 51.50), Pc("grabbing video,", 52.00, 52.80)])
bars_out(s, 52.80)
C(51.52, "glint", 0.34); C(51.54, "pop-deep", 0.2); C(52.66, "swoosh-short", 0.28)
# B — CARD checklist (52.80–57.40)
ROWS = [("wand-sparkles", "Animation", 54.08), ("activity", "Motion styles", 54.88), ("film", "B-roll", 56.35)]
rows = "".join(check_row(f"s11-r{i}", ic_, lab, 470 + i * 190) for i, (ic_, lab, t) in enumerate(ROWS))
caps = (srow("s11-c1", "then you need", 180, 120, "grey") + srow("s11-c2", "to use", 300, 120, "grey")
        + srow("s11-c3", f'{g("to keep your")} users', 1150, 130))
wrap = card(s, "b", 52.80, 57.40, caps + rows, z=5, enter="none", dy=110)
bars_in(s, 52.80)
J(s, f'rise($("s11-c1"), {s.L(52.90)}, {{ y: 30, d: 0.3 }}); rise($("s11-c2"), {s.L(53.50)}, {{ y: 30, d: 0.3 }});')
for i, (ic_, lab, t) in enumerate(ROWS):
    t_in = min(s.L(t) - 0.3, s.L(53.62) + i * 0.1) if i < 2 else s.L(t) - 0.34
    J(s, f'rise($("s11-r{i}"), {t_in:.3f}, {{ y: 50, x: 80, d: 0.34 }}); tick($("s11-r{i}-k"), {s.L(t) + 0.06:.3f});')
    C(t + 0.08, "ding", 0.32)
    C(t_in + s.start, "paper-slide" if i == 2 else "blip", 0.2)
bv_ = framed(s, "br", 56.01, 57.40, "gavel", 560, 110 + 470 + 2 * 190 + 13, 190, 124, z=7, media_start=0.0, radius=18)
J(s, f'tl.fromTo($("{bv_}"), {{ scale: 0.4, rotation: -8 }}, {{ scale: 1, rotation: -3, duration: 0.36, ease: "back.out(1.8)" }}, {s.L(56.05)});')
J(s, f'rise($("s11-c3"), {s.L(57.31) - 0.2:.3f}, {{ y: 24, d: 0.24 }});')
C(56.06, "sparkle-2", 0.38)
# C — SPLIT: watching, all the time
face = split_at(s, "c", 57.40, 59.47)
ph = phone_vid(s, "ph", 57.40, 59.47, "privacy-c", 390, 110, 300, 560, z=4, media_start=0.4)
rt = retention("s11-rt", 190, 714, 700) + f'<div id="s11-rp" class="eng" style="left:900px;top:668px;opacity:0">{icon("repeat", TEAL, 2.6)}</div>'
lay(s, "c-top", 57.40, 59.47, 5, inner=rt + s.seam_caps([("to keep your users", 57.40, 58.35), ("watching", 58.35, 58.83), ("all the time.", 58.83, 59.47)]))
J(s, f'tl.fromTo($("{ph}"), {{ y: 260 }}, {{ y: 0, duration: 0.4, ease: "back.out(1.4)" }}, {s.L(57.42)});')
J(s, f'tl.fromTo($("s11-rt-f"), {{ scaleX: 0 }}, {{ scaleX: 1, duration: 1.4, ease: "none" }}, {s.L(57.50)});')
J(s, f'pop($("s11-rp"), {s.L(58.86)}, {{ s: 0.3, d: 0.34 }}); tl.to($("s11-rp"), {{ rotation: 360, duration: 0.6, ease: "power2.inOut" }}, {s.L(59.0)});')
expand(s, face, 59.47)
C(57.44, "sparkle-1", 0.4); C(58.88, "ding", 0.3)

# ======================================================================================================
# S12 — "If you want to copy my style, if you want to have attention videos like this, then I have created a prompt
#        that you can download." (59.47–66.50): PUNCH ⌘C → CARD stills → the prompt card (blurred, locked) + Download
# ======================================================================================================
s = reel.scene("s12", "prompt", 59.47, 66.50)
pv = punch(s, "a", 59.47, 60.87)
keys = (keycap("s12-k1", "⌘", 110, 250, "transform:scale(.8)") + keycap("s12-k2", "C", 290, 250, "transform:scale(.8)"))
lay(s, "a-keys", 59.47, 60.87, 5, keys)
J(s, f'pop($("s12-k1"), {s.L(59.98)}, {{ s: 0.4, d: 0.3 }}); pop($("s12-k2"), {s.L(60.06)}, {{ s: 0.4, d: 0.3 }});')
J(s, f'press($("s12-k1"), {s.L(60.36)}); press($("s12-k2"), {s.L(60.38)});')
plates(s, "acap", [Pc("If you want to", 59.50, 59.95), Pc(f'{acc("copy")} my style,', 59.95, 60.87, "serif", 124, "", "pop")])
whip_out(s, pv, 60.87, d=0.18, dx=-800)
T(59.47); C(60.0, "pop-small", 0.24); C(60.36, "key-1", 0.4); C(60.39, "key-3", 0.36); C(60.72, "whoosh-quick", 0.26)
# B — CARD
ST = [("brag", 120, 860, -8), ("privacy", 390, 820, 0), ("africa", 660, 860, 8)]
stills = "".join(phone(f"s12-p{i}", x, y, 300, 540, f"{IMG}stills/{n}.jpg").replace('class="bx-phone" style="', f'class="bx-phone" style="transform:rotate({r}deg);')
                 for i, (n, x, y, r) in enumerate(ST))
part_a = (srow("s12-t1", "if you want to have", 250, 104, "grey") + srow("s12-t2", "attention videos", 380, 160)
          + srow("s12-t3", "like this,", 580, 120, "grey") + stills)
blur_lines = "".join(f'<div class="dln" style="left:40px;top:{190 + k * 50}px;width:{[600, 520, 640, 480, 610, 560, 430][k]}px;background:#B9AF9F"></div>' for k in range(7))
doc = doc_card("s12-doc", 170, 330, 740, 640, "My video style", "PROMPT", "file-text", 0, 72,
               body=f'<div id="s12-bl" style="position:absolute;left:0;top:0;width:100%;height:100%;filter:blur(12px)">{blur_lines}</div>'
                    f'<div class="lk" style="position:absolute;left:315px;top:320px;width:110px;height:110px;border-radius:50%;background:#17140F">'
                    f'<div class="pr-ic" style="left:27px;top:25px;width:56px;height:56px">{icon("lock", "#F5F1EA", 2.4)}</div></div>')
pchip = chip("s12-pc", "prompt", 760, 290, 54, "hero", "opacity:0")
dl = btn("s12-dl", "Download", 290, 1030, 500, 140, 60, "download")
fill = f'<div id="s12-fl" style="position:absolute;left:290px;top:1030px;width:500px;height:140px;border-radius:999px;background:rgba(255,255,255,.28);transform-origin:0% 50%;transform:scaleX(0)"></div>'
cur = cursor_el("s12-cur", 900, 2000, 1.3)
part_b = (doc + pchip + dl + fill + cur
          + srow("s12-b1", f'{g("that you can")} download', 1260, 128))
inner = f'<div id="s12-pa" class="pr-c">{part_a}</div><div id="s12-pb" class="pr-c">{part_b}</div>'
wrap = card(s, "b", 60.87, 66.50, inner, z=5, enter="whip")
J(s, f'tl.set($("s12-pb"), {{ y: 1960 }}, 0);')
J(s, f'rise($("s12-t1"), {s.L(60.95)}, {{ y: 30, d: 0.3 }}); slam($("s12-t2"), {s.L(61.63)}, {{ s: 1.3, d: 0.28 }});')
J(s, f'rise($("s12-t3"), {s.L(62.51)}, {{ y: 24, d: 0.26 }});')
for i in range(3):
    J(s, f'tl.fromTo($("s12-p{i}"), {{ opacity: 0, y: 420 }}, {{ opacity: 1, y: 0, duration: 0.44, ease: "back.out(1.4)" }}, {s.L(61.70) + i * 0.1:.3f});')
J(s, f'tl.to($("s12-pa"), {{ y: -1960, duration: 0.3, ease: "power3.in" }}, {s.L(62.92)});')
J(s, f'tl.fromTo($("s12-pb"), {{ y: 1960 }}, {{ y: 0, duration: 0.32, ease: "power3.out" }}, {s.L(63.10)});')
J(s, f'tl.fromTo($("s12-bl"), {{ filter: "blur(22px)" }}, {{ filter: "blur(12px)", duration: 0.6 }}, {s.L(63.20)});')
J(s, f'pop($("s12-pc"), {s.L(64.43)}, {{ s: 0.4, d: 0.34, rot: 6 }});')
J(s, f'rise($("s12-b1"), {s.L(65.15)}, {{ y: 30, d: 0.3 }});')
J(s, f'tl.fromTo($("s12-cur"), {{ x: 0, y: 0 }}, {{ x: -380, y: -900, duration: 0.6, ease: "power3.out" }}, {s.L(65.10)});')
J(s, f'press($("s12-cur"), {s.L(65.80)}); press($("s12-dl"), {s.L(65.82)});')
J(s, f'tl.fromTo($("s12-fl"), {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.42, ease: "power1.inOut" }}, {s.L(65.86)});')
J(s, f'tl.set($("s12-dl-t"), {{ textContent: "Downloaded" }}, {s.L(66.30)}); tl.to($("s12-dl"), {{ backgroundColor: "#17140F", duration: 0.16 }}, {s.L(66.30)});')
C(60.9, "whoosh", 0.22); C(61.65, "glint", 0.28); C(61.72, "card-place-1.ogg", 0.26); C(61.92, "card-place-2.ogg", 0.26)
C(62.94, "whoosh-quick", 0.24); C(63.12, "paper-slide", 0.34); C(64.45, "pop", 0.3); C(65.82, "tap", 0.42); C(66.30, "success", 0.36)

# ======================================================================================================
# S13 — "If you follow me here and you comment REEL, I'm gonna send it into your DM. If you don't find it in your DM,
#        then make sure to check it in my bio." (66.50–73.67): SPLIT follow + comment + DM → PUNCH → CARD bio
# ======================================================================================================
s = reel.scene("s13", "cta", 66.50, 73.67)
face = split_at(s, "a", 66.50, 70.47)
fol = btn("s13-fol", "Follow", 300, 130, 480, 130, 62, "user-plus")
rip = '<div id="s13-rip" class="pr-ripple" style="left:480px;top:135px"></div>'
cmt = comment_box("s13-cm", 90, 360, 900, 130)
dm = dm_notif("s13-dm", 90, 560, 900, "Sent you the prompt")
cur = cursor_el("s13-cur", 880, 700, 1.3)
lay(s, "a-top", 66.50, 70.47, 3, inner=fol + rip + cmt + dm + cur + s.seam_caps([
    ("If you follow me here", 66.50, 67.55), ("and you comment", 67.55, 68.27),
    (f'<span style="color:{TEAL}">“REEL”</span>', 68.27, 68.75), ("I'm gonna send it", 68.75, 69.55), ("into your DM.", 69.55, 70.47)]))
J(s, f'pop($("s13-fol"), {s.L(66.56)}, {{ s: 0.5, d: 0.36 }});')
J(s, f'tl.fromTo($("s13-cur"), {{ x: 0, y: 0 }}, {{ x: -310, y: -520, duration: 0.42, ease: "power3.out" }}, {s.L(66.62)});')
J(s, f'press($("s13-cur"), {s.L(67.06)}); press($("s13-fol"), {s.L(67.08)}); ripple($("s13-rip"), {s.L(67.08)});')
J(s, f'tl.to($("s13-fol"), {{ backgroundColor: "#17140F", duration: 0.16 }}, {s.L(67.12)}); tl.set($("s13-fol-t"), {{ textContent: "Following" }}, {s.L(67.12)});')
J(s, f'tl.to($("s13-cur"), {{ x: 60, y: -180, duration: 0.5, ease: "power2.inOut" }}, {s.L(67.40)});')
J(s, f'rise($("s13-cm"), {s.L(67.50)}, {{ y: 80, d: 0.34 }});')
J(s, f'tl.set($("s13-cm-ph"), {{ opacity: 0 }}, {s.L(68.24)}); typeIn($("s13-cm-tx"), "REEL", {s.L(68.26)}, 0.3);')
J(s, f'tl.to($("s13-cur"), {{ x: 60, y: -262, duration: 0.24, ease: "power2.out" }}, {s.L(68.40)});')
J(s, f'press($("s13-cm-sd"), {s.L(68.72)}); press($("s13-cur"), {s.L(68.70)});')
J(s, f'tl.to($("s13-cm"), {{ y: -300, opacity: 0, scale: 0.9, duration: 0.32, ease: "power2.in" }}, {s.L(68.86)});')
J(s, f'tl.to($("s13-cur"), {{ opacity: 0, duration: 0.2 }}, {s.L(68.90)});')
J(s, f'tl.fromTo($("s13-dm"), {{ opacity: 0, y: -460 }}, {{ opacity: 1, y: -200, duration: 0.42, ease: "back.out(1.5)" }}, {s.L(69.50)});')
J(s, f'shake($("s13-dm"), {s.L(69.94)}, 8, 5, 0.04);')
expand(s, face, 70.47)
C(66.58, "pop", 0.28); C(67.08, "tap", 0.4); C(67.52, "pop-small", 0.24)
keys_cue(68.27, 4, 0.08, 0.34); C(68.72, "tap", 0.36); C(68.88, "swoosh-up", 0.3); C(69.52, "notify", 0.44)
# B — PUNCH
punch(s, "b", 70.47, 71.79)
plates(s, "bcap", [Pc("If you don't find it", 70.50, 71.15), Pc(f'in your {acc("DM,")}', 71.15, 71.79, "serif", 120, "", "pop")])
paper_cover(s, "cov", 71.79)
T(70.47)
# C — CARD: check my bio
pf = profile_card("s13-pf", 140, 380, 800, 520)
cur2 = cursor_el("s13-cur2", 900, 1960, 1.3)
rip2 = '<div id="s13-rip2" class="pr-ripple" style="left:480px;top:744px"></div>'
caps = (srow("s13-c1", "then make sure to check", 170, 100, "grey") + srow("s13-c2", f'{g("my")} bio', 1000, 230))
wrap = card(s, "c", 71.79, 73.67, pf + rip2 + cur2 + caps, z=6, enter="none")
J(s, f'rise($("s13-c1"), {s.L(71.84)}, {{ y: 30, d: 0.3 }}); rise($("s13-pf"), {s.L(71.86)}, {{ y: 120, d: 0.4 }});')
J(s, f'tl.fromTo($("s13-pf-ring"), {{ opacity: 0, scale: 1.08 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {s.L(72.56)});')
J(s, f'tl.fromTo($("s13-cur2"), {{ x: 0, y: 0 }}, {{ x: -340, y: -1120, duration: 0.5, ease: "power3.out" }}, {s.L(72.40)});')
J(s, f'press($("s13-cur2"), {s.L(72.94)}); ripple($("s13-rip2"), {s.L(72.96)});')
J(s, f'slam($("s13-c2"), {s.L(73.07)}, {{ s: 1.3, d: 0.28 }});')
C(71.80, "paper-slide", 0.3); C(72.58, "pop-small", 0.26); C(72.96, "tap", 0.38); C(73.09, "glint", 0.3)

# ======================================================================================================
# S14 — END CARD (73.67–75.40)
# ======================================================================================================
s = reel.scene("s14", "end", 73.67, TOTAL)
end = (srow("s14-e1", "copy my", 330, 140, "grey") + srow("s14-e2", "style", 460, 330)
       + chip_c("s14-hc", "Claude&nbsp;Code", 900, 76, "hero", "opacity:0")
       + '<div style="position:absolute;left:0;width:1080px;top:1110px;text-align:center">'
         '<span id="s14-cm" class="bx-sans" style="position:relative;display:inline-block;font-size:64px;color:#746D62;opacity:0">comment</span>'
         '<span id="s14-rl" class="bx-chip dark" style="position:relative;display:inline-block;font-size:64px;margin-left:22px;opacity:0">REEL</span></div>')
wrap = card(s, "a", 73.67, TOTAL, end, z=5, enter="up")
J(s, f'rise($("s14-e1"), {s.L(73.74)}, {{ y: 30, d: 0.3 }}); slam($("s14-e2"), {s.L(73.92)}, {{ s: 1.3, d: 0.3 }});')
J(s, f'pop($("s14-hc"), {s.L(74.20)}, {{ s: 0.4, d: 0.36, rot: -3 }});')
J(s, f'rise($("s14-cm"), {s.L(74.44)}, {{ y: 20, d: 0.26 }}); pop($("s14-rl"), {s.L(74.54)}, {{ s: 0.4, d: 0.34, rot: 4 }});')
T(73.67); C(73.94, "glint", 0.3); C(74.22, "pop-small", 0.26); C(74.56, "pop", 0.26)
