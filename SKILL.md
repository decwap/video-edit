---
name: video-edit
description: Edit raw vertical talking-head footage — a phone recording full of retakes, restarts, mistakes and long pauses — into a polished 9:16 reel (TikTok / Instagram Reels / YouTube Shorts) in a warm paper-editorial style, rendered in Full HD or 2K with HyperFrames. It keeps the best take of every line, tightens the pauses, adds captions, a motion graphic every 2–3 seconds (paper cards, kinetic serif words, a pop-out face panel with the head rising above its edge, giant words behind the speaker's head, split-screen and punch-ins), real B-roll, dynamic transitions and light sound effects. Use it whenever someone shares a raw or face-to-camera video and wants it edited, cut down, cleaned up, "made engaging", given motion graphics, captions, B-roll, transitions or sound effects, asks to remove repeated takes or keep the good takes, says "video-edit", "edit my raw footage" or "edit it like this reel" — even if they never name the skill.
compatibility: Claude Code (needs a shell and the local filesystem). Node.js 18+ (HyperFrames CLI via npx), ffmpeg + ffprobe with zscale and libvpx-vp9, Python 3.10+ with numpy, scipy, pillow and opencv-python. Windows, macOS or Linux.
---

# Video Edit

Turns one raw vertical recording into a finished reel: the best read of every line (retakes, tangents and dead air
removed), then the speaker alternating with paper cards, real B-roll and small UI props every 2–3 s, captions on every
line, three payoff words **behind the speaker's head**, varied transitions (face-card rise/expand, paper cover, whip,
flip, zoom-through, bar sweep, light-leak flash) and a light action sound on every visible event. Output:
`<name> (Edited).mp4` (1080×1920 Full HD, or 1440×2560 2K) and a frame sheet, next to the original.

**The face panel is the default speaker layout:** the speaker stays in a panel on the bottom third of the frame, with the head
rising above its edge onto a light stage that carries the graphics (`references/style.md`, "Face panel"). It replaces the
alternating full-frame layouts unless the user asks for them.

Worked example: a 5:26 iPhone recording → 16 takes → a 75 s reel with 34 beats — `examples/takes.json`,
`examples/STORYBOARD.md`, `examples/scenes.py` + `scenes_b.py`.

**Bundled:** `scripts/` — `phrases.py` (read the raw take, spot retakes), `takes.py` (best-take cuts snapped to the
audio), `aroll.py` (wide + punch intermediates + clean voice; HDR → SDR), `strip.py` (raw→edited proof strip),
`prep_broll.py` (clips from the creator's own videos), `stock.py` (Pexels B-roll), `screen_replace.py` (app screens on a
real phone), `make_panel.py` + `face_panel.py` (the pop-out face panel), `make_matte.py` (DEPTH cut-outs), `video_kit.py` (the scene kit, on `reel_kit.py` + `paper_reel.py`),
`verify_render.py`, `sync_check.py`, `make_sfx.py` + `make_voice_sfx.py` + `make_textures.py` (regenerate the
assets). `assets/` — fonts (OFL), original paper textures, 76 original sounds, Lucide icons (ISC, packed into one file, `assets/icons.json`). `references/` — `takes.md`, `style.md`, `motion.md`, `sound.md`, `pipeline.md`,
`storyboard-skeleton.md`.

Read `references/takes.md` before choosing takes, `style.md` + `motion.md` + `sound.md` before planning, and
`pipeline.md` before running commands. HyperFrames' own skills (`hyperframes-core`, `hyperframes-cli`) own the
composition contract — load them when you debug composition HTML.

## Defaults (settled — follow unless the user asks otherwise)
- 1080×1920 at the footage's own fps; **Full HD** delivery by default, **2K** (1440×2560) when asked for "2K",
  "1440p", "higher quality" or when the source is 2K/4K; 4K on request (pipeline.md §7). Never ship below 1080×1920.
- **Face panel for the whole reel:** the first frame is already the panel and the stage, and only the stage changes after
  that; captions are 1–3 words. Full-frame PUNCH, DEPTH and CARD beats and the old flat card (`split_at`) only when asked for.
- Keep the best take of each line and every word of it; pauses tightened to a breath (~0.2 s).
- **No colour grade, no vignette:** the footage keeps its own colours. HDR phone video is converted to SDR only so it
  doesn't play washed out.
- No music bed — light action sounds only (`references/sound.md`).
- Accent teal `#0B7A73` on paper `#F5F1EA`; Instrument Serif Italic + Instrument Sans + JetBrains Mono.
- Real visuals only: the creator's own videos, the product's real site/app, this recording's own frames. Never invent
  UI, logos, numbers or stats; keep links off screen when the CTA gates them ("comment X and I'll send it").
- Final mix −14 LUFS / −1 dBTP; deliver `<name> (Edited).mp4` next to the original; older versions stay in `renders/`.

## Intake (one short form — only what the request and the footage don't answer)
1. The CTA keyword, if they say "comment X" (ASR often mishears it; confirm the spelling).
2. Folders or files of their own earlier videos, demos or screen recordings to use as B-roll (strongly preferred).
3. Accent colour and resolution, if they care (default teal, Full HD).
4. Storyboard first, or straight to the render? Recommend "storyboard first, then render right away".

## Workflow
Track these as tasks; run long steps (A-roll, mattes, check, render) in the background with a log file.

1. **Set up** — check the tools (pipeline.md §0). `hyperframes init videos/<slug>`, copy `assets/fonts`,
   `assets/img/*.png` and `assets/sfx` from this skill into the project's `assets/`, write `BRIEF.md`
   (message, audience, length, CTA, B-roll sources, notes).
2. **Look** — probe (HDR? fps? duration), a 1-per-5 s contact sheet; note framing changes (pipeline.md §1).
3. **Best takes** — transcribe → `phrases.py` → choose the last clean read of every line in the message's order →
   `build/takes.json` → `takes.py --show` → build the voice → **re-transcribe the cut voice and read it**; fix clipped or
   doubled words before anything else (`references/takes.md`). Note the jump-cut list.
4. **A-roll** — `aroll.py --face` writes `build/face/grid.jpg`; read the head top, eye line and face-centre x on it,
   then `aroll.py --head-top Y --eyes Y --face-x X` (prints and uses the punch crop + face shift; add
   `--size 1440x2560` for 2K).
5. **Plan** — map the clean read onto beats with `references/storyboard-skeleton.md`: something new on the stage every 2–3 s, every jump cut covered (`panel(tight=True)` or a new
   stage), 1 held beat, 1 proof beat, 1 name reveal. For a full-frame reel on request: 3 DEPTH words, transitions varied. Write
   `STORYBOARD.md` and show the table (beat · time · layout · on screen · why) with the clean read.
6. **B-roll & props** — `prep_broll.py` for the creator's own videos, real product captures, `strip.py` for a
   raw→edited proof, `stock.py` only when nothing real fits (pipeline.md §4). **No past videos?** Build the "styles
   like this" and held beats from clips of *this* recording in phone mockups, the raw→edited strip, captures of the
   named product, and stock clips of the named action; never fake someone else's content as the creator's.
7. **Face panel** — `make_panel.py --src assets/aroll_wide.mp4` as one background job: it fits the panel to this speaker,
   cuts the whole A-roll out and tracks the head (pipeline.md §5). DEPTH beats, if any: `make_matte.py` for each.
8. **Build** — `build/scenes.py` on `video_kit` (start from `examples/panel_scene.py`; props and patterns from
   `examples/scenes.py`): `use_panel(PROJECT / "build/panel.json")`, `reel.scene()`, `s.paper` + `panel` for the speaker, graphics
   in `framed` / `phone_vid` / `lay`, `s.seam_caps` inside `lay` for captions, props from `references/motion.md`, a sound cue for every visible action (`C(t, "sparkle-1", .4)`, `T(t)` on cuts into a
   punch-in or new section), then `print(finish(reel, PROJECT, accent=…))`. `Reel(total=voice + 1.5–2 s,
   voice_dur=voice)`: the end card holds silent after the last word.
9. **Verify** — `hyperframes lint` → `hyperframes check` until "Check passed" → `snapshot` one frame per beat and read
   every sheet (layout balance, nothing covering the face, captions in the safe zone) → fix → rebuild.
10. **Render & deliver** — HD or 2K (pipeline.md §7), check the render log for unready media, read a few real frames at the panel's edge
    (pipeline.md §5), `verify_render.py --sheet --normalize`, `sync_check.py` (+0.0 ms), copy `<name> (Edited).mp4` + frames sheet next to the original. Summarise:
    what was cut (raw length → edit length, takes kept), what was built, what was inferred (keyword spelling, caption
    corrections), and anything the footage couldn't support.

## Writing scenes well
- Text sizes are canvas pixels: seam caption 78 px; plates 78 px sans / 112–124 px serif; card keyword 150–300 px;
  DEPTH word 260–600 px. Captions stay inside y 760–1500, x 140–940.
- Ink = the word that matters, `g()` grey = connective words, `acc()` = the one accent word. One keyword per card.
- Ids are prefixed with the scene id; every timed element is a `.clip`; videos that start mid-scene live in `s.body`
  (`phone_vid`, `framed`, `win_vid` do it). Helpers take global seconds, `J(s, …)` lines take `s.L(global)`.
- Entrances 0.3–0.55 s (rise `power3.out`, pop `back.out(1.6–2.4)`, slam `expo.out` from 1.25–1.5×); captions pop in
  over 0.16–0.2 s and swap by hard cut.
- Balance every frame: CARD content centred near y 900 (`card(dy=…)`), props in a PUNCH above the shoulders not on the
  chin, a DEPTH word low enough that the hair covers its bottom edge, cursors entering from off-canvas.
- Product visuals are real captures inside phone / browser / frame props; steps, commands and file names quote the
  tool's own docs or the user's real prompt.

## Sound in one paragraph
Light and bright: crystal `sparkle-1..3` when a real visual appears, marimba `ting-1..5` (rotating, via `T(t)`) on
every cut into a punch-in or new section, wooden `click-1..3` per word or item as things stack in, `glint` when a big keyword lands, then the
literal action — `key-N` typing, `tap` presses, `ding` checks, `blip` steps, `riser`→`success` completions, `notify`
DMs, `shutter` cameras, `paper-slide` / `card-place-*` cards, `marker` strikes, `whoosh-*` / `swoosh-*` with whips and
zooms. One `thud` (the name reveal). Volumes 0.16–0.5, at most two sounds on one instant, quiet held beats. The
flavour library (meme / cinematic sounds) is opt-in by content — see `references/sound.md`.

## Gotchas that cost the most time
- Cutting on ASR times clips words: always `takes.py` (audio-snapped) and the re-transcription check.
- Phone HDR played as SDR looks washed out; phones are variable-frame-rate — `aroll.py` handles both.
- Many separate images → some render blank: one sprite (`strip.py`), and read the render log for readiness warnings.
- A line across the head at the panel's edge: footage and cutout have different colour tags; `make_panel.py` tags both.
- Full list: `references/pipeline.md` §8.
