# Motion catalogue — beats, transitions and props in `video_kit`

Everything here is imported by `from video_kit import *`. Helpers take GLOBAL seconds (`g0`, `g1`, `g_end`); raw `J(s,
…)` lines need scene-local times (`s.L(global)`). The worked example (`examples/scenes.py`, `scenes_b.py`) uses every
item below at least once — copy from it.

## Cadence
- **Something new every 2–3 s:** a layout change, a prop entering, a word slamming. Beats are 1.0–4.5 s; a CARD that
  runs longer than ~3 s changes inside (a vertical push to a second half, a list that keeps growing).
- **Every jump cut is covered** by a layout change, a framing change (face card 1.22×, punch vs wide) or a CARD/B-roll.
- **Vary the transition** at every cut; never the same one twice in a row. Rough mix for a 75 s reel: 6–8 face-card
  rise/expand, 3–4 paper covers, 3 whips, 2–3 zoom-throughs, 2 flips, 2 bar sweeps, 2 light leaks.
- **Three DEPTH words** on the payoff words, **one held beat** where only real footage moves, **one proof beat**
  (real product capture or the raw→edited strip), **one name reveal** (the hero chip slams, `thud`).

## Beat layouts
| Call | What it is | Use for |
| --- | --- | --- |
| `panel(s, name, g0, g1, tight=False)` + `s.paper` | the face panel: footage on the bottom third, head rising above its edge | the default talking beat; the stage above carries the graphic (`make_panel.py` first) |
| `split_at(s, name, g0, g1, zoom=1.0, shift=None)` | paper top half + speaker card (bottom, 80 px radius) that rises in | the old flat card, on request; top half carries the graphic |
| `punch(s, name, g0, g1)` | full-frame tight crop with a snap zoom | emphasis lines, hard cuts after a SPLIT |
| `fullv(s, name, g0, g1, A_WIDE, keys=depth_keys())` + `make_matte` | DEPTH: base → giant word → matte | 3 payoff words per reel |
| `card(s, name, g0, g1, inner, enter=…, dy=…)` | full paper card (grain + drifting fern / window-light shadow) | graphics without the speaker; keep the centre of mass near y 900 |
| `bv(s, name, g0, g1, clip)` | full-bleed B-roll clip | a real-world moment (from `assets/bv/`) |
| `plates(s, name, [Pc(text, g0, g1, kind, size, tone, how)])` | caption plates on footage | PUNCH / DEPTH / wide captions |
| `s.seam_caps([(text, g0, g1)])` | bold sans captions on the SPLIT seam (y 872) | SPLIT captions, word-group by word-group |
| `srow` / `nrow` | serif / sans centred lines (hidden until animated) | CARD headlines: grey connective words `g()`, ink keyword, accent `acc()` |

## Transitions
| Out (end of a beat) | In (start of the next) | Feel | Sound |
| --- | --- | --- | --- |
| `expand(s, face, g_end)` — the speaker card opens to full frame | `punch` / DEPTH beat | punch-in, energy | `ting` (T) |
| `paper_cover(s, name, g_end)` — paper slides up over footage | `card(..., enter="none")` | calm section change | `paper-slide` |
| `whip_out(s, wrap, g_end)` | `card(..., enter="whip")` or `whip_in` | fast, list-like | `whoosh-quick` / `whoosh` |
| `flip_out(s, wrap, g_end)` | `card(..., enter="flip")` | card-to-card | `swoosh-short` |
| `zoom_through(s, wrap, g_end, scale=1.8–2.2)` | `card(..., enter="zoom")`, PUNCH or DEPTH | push into the next idea / proof | `swoosh-up` |
| `bars_out(s, g_cut)` | `bars_in(s, g_cut)` — ink + accent bars sweep across | punchy section change into a list | `swoosh-short` |
| `leak_out(s, g_cut)` | `leak_in(s, g_cut)` — warm light-leak flash | soft, filmic; into a proof or a reveal | `whoosh-reverse` (into the cut) |
| — | `face_rise` (built into `split_at`) | the speaker returns | — |
| — | `viewfinder(cid)` layer + `blink(dot)` | "like this", "watch", "I filmed" | `shutter` |
Pairs that span a cut live in two scenes: the `_out` half in the outgoing scene, the `_in` half in the next one.

## Props (HTML builders; animate their ids with pop / rise / slam / dropIn / floatY / growX / press / tick)
| Call | Use |
| --- | --- |
| `phone_vid(s, name, g0, g1, clip, x, y, w, h, media_start=)` | a real clip (`assets/bv/<clip>.mp4`) inside a phone; grids of 4 = "styles like this" |
| `phone(cid, x, y, w, h, img)` | a still in a phone (before/after pairs, thumbnails) |
| `framed(...)`, `win_vid(...)`, `pwin(cid, x, y, w, h, img)` | clip in a rounded frame; clip / capture in a browser window |
| `logo_tile(cid, src, x, y, size)` | a product's own logo as an app-icon tile |
| `chip(cid, text, x, y, size, kind)`, `chip_c(cid, text, top, size, kind)` | the hero chip (accent mono pill): debut, 3–4 returns, end card |
| `avatar(cid, x, y, size, k)` | generic creator/audience avatars (never a real person's face) |
| `vcard(cid, x, y, w, h)` | video cards fanning out ("more videos") |
| `eng(cid, icon, x, y, color)` | engagement bubbles (heart, comment, bookmark, send) around a phone |
| `retention(cid, x, y, w)` + `{cid}-f` scaleX | watch-time / progress bar |
| `edit_timeline(cid, x, y, w, h, title)` + `timeline_build(s, cid, g0)` | an edit assembling itself (V1, GFX, CAP, SFX tracks) + playhead |
| `film_strip(cid, [sprite], kept, x, y)` + `strip.json` | raw → edited proof: cut frames shrink away, best takes gather, `countTo(..., mmss)` clock |
| `wave_chip(cid, sfx_file, label, x, y)` | a sound drawn from its real waveform; reveal `{cid}-on` with its own sound |
| `doc_card(cid, x, y, w, h, title, sub, icon, lines, body=)` | a prompt / document card; blur the body + lock when the CTA gates it |
| `keycap(cid, label, x, y)` | ⌘ / C keys for "copy", shortcuts |
| `btn(cid, label, x, y, w, h, size, icon)` | Follow / Download / Publish buttons (`press`, then swap `{cid}-t` text) |
| `check_row(cid, icon, label, top)` | checklist rows that tick (`tick($("{cid}-k"), t)`) |
| `comment_box(cid, x, y, w)` | comment that types the CTA keyword (`typeIn` into `{cid}-tx`) and sends |
| `dm_notif(cid, x, y, w, head)` | DM notification dropping in |
| `profile_card(cid, x, y, w, h)` | a generic profile with a "link in bio" row and a ring (`{cid}-ring`) |
| `swatch(cid, x, y, w, h, color, title)` | style cards (different accents = "different styles") |
| `cursor_el(cid, x, y, scale)` + `ripple` | a cursor that moves and clicks — start it off-canvas |
| `ic(cid, icon, x, y, size, color)` / `icon(name, color)` | Lucide icons (assets/icons.json — one file, 209 icons, ISC) |
| `teaser_card(...)` | blurred list preview with number badges (list beats) |

## JS helpers available inside every scene
`show, rise, pop, slam, drift, typeIn, blink` (paper_reel) · `shake, ripple, press, whipIn, whipOut, stampIn, tick,
showAt, lit` (reel_kit) · `wobble, countTo, mmss, drawIn, growX, dropIn, floatY` (video_kit).
Entrances 0.3–0.55 s: `power3.out` rises, `back.out(1.5–2.4)` pops, `expo.out` slams from 1.25–1.5×. Exits are hard
cuts or the transition out — no fades to nothing.
