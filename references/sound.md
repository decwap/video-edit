# Video Edit — sound playbook

Action sounds are part of the edit, not decoration: every sound answers something visible on screen, and the
choice follows what the video is about. The character is **light, bright and delicate — crystal sparkles, soft
marimba tings and wooden clicks — not heavy whooshes or bass booms**, and there is no music bed under the voice.
Every file in `assets/sfx/` is an original synthesis (`scripts/make_sfx.py`, deterministic) or a local TTS
performance (`scripts/make_voice_sfx.py`): no samples, no clips from anyone else's video, free to use in your reels.

## The core set (video-edit v2, Oct 2026)
| Sound | What it is | Where it goes |
| --- | --- | --- |
| Crystal sparkle `sparkle-1/2/3` | 0.55–0.7 s of tonal crystal grains (pentatonic, 4–9 kHz) over a faint airy bed — rising, falling, scattered | every reveal of a real visual: phone, website, app screen, video frame, logo tile, success state |
| Marimba ting `ting-1…5` | a soft wooden-bar note (partials 1 : 2.76 : 5.4) on E-major pentatonic, 0.9 s | every cut into a punch-in or a new section; rotating through 1…5 makes the cuts a little melody |
| Wooden click `click-1/2/3` | ~0.09 s woody tick with a bright edge | text or items stacking in, one click per word / item |
| Mechanical key `key-0…5` | two-stage keyboard key (click + bottom-out) | typing, ~0.08–0.1 s apart |
| Airy glint `glint` | 0.34 s high air sweep (8.5→15.5 kHz) with a tiny ping | a big serif keyword or DEPTH word landing |
Every sound keeps the length and loudness of the earlier Paper Reel sound with the same name, so cue volumes and
existing cue sheets carry over unchanged.

## Content → sound (use the action that matches what is on screen)
| On screen | Sound (`assets/sfx/`) | Level |
| --- | --- | --- |
| Cut into a punch-in, a new section or chapter | `ting-1…5`, rotate in order so the cuts form a little melody | 0.26–0.34 |
| A real product visual appears (phone, site, app screen, video frame, icon, storyboard, success state) | `sparkle-1/2/3` (+ `pop` if it physically lands) | 0.4–0.55 |
| Big serif keyword / depth word lands | `glint` (`thud` only for the one name reveal per reel) | 0.3–0.42 |
| Words type or stack in | `click-1/2/3`, one per word | 0.16–0.3 |
| Terminal / comment box typing | `key-0…5`, one per character group, ~0.08–0.1 s apart | 0.4 |
| Enter, button press, send | `tap` (+ `pop-small` on the button, `swoosh-down` when something is sent away) | 0.45–0.5 |
| Check mark, approved, saved | `ding` | 0.34–0.4 |
| Step completed, counter step, audience ping | `blip` | 0.16–0.32 |
| Render / export finished, published, app live | `success` (after a `riser` build-up) | 0.5 |
| Money, price, "free", earnings | `coin` | 0.5 |
| A sale lands, "charge them", "get paid", PAID stamp | `kaching` (cash register) | 0.45–0.5 |
| Revenue adds up (subscriptions, ads, purchases) | `coins` (short cascade) | 0.4 |
| Whip-pan between two B-roll shots | `whip` | 0.38–0.42 |
| A receipt / note / slip torn off | `rip` | 0.4 |
| Message / DM / notification | `notify` | 0.45 |
| Screenshot, frame captured, photo | `shutter` | 0.3 |
| Cards, slides, documents move | `paper-slide`; card deck → `card-place` | 0.3–0.48 |
| Underline, highlight, strike-through | `marker` | 0.3–0.5 |
| Clock, time, countdown | `tick` (fast run for "hours", three for a stopwatch) | 0.25–0.35 |
| Fast motion, "quickly", share | `whoosh-quick`; zoom-through → `swoosh-up` | 0.2–0.38 |
| Chips / small UI pop in | `pop-small` | 0.18–0.45 |
| A "REJECTED" / "APPROVED" stamp lands | `stamp` (knock + paper slap, no boom) | 0.5–0.6 |
| An app crashes, a screen glitches | `glitch` (0.5 s digital stutter) | 0.4–0.5 |
| A button does nothing, a wrong input | `error` (two soft descending tones) | 0.26–0.32 |
| Something breaks or cracks | `crack` (snap + crackle + soft knock) | 0.4–0.6 |

Pick by **meaning first**: a finance app gets `coin` on money moments, a messaging feature gets `notify`, a
camera feature gets `shutter`, a speed claim gets `whoosh-quick`. If no row fits, synthesize a new short sound
in the same light character, add it to `make_sfx.py` (with a `TARGET` length / loudness entry) and run the script.

## Rules
- One sound per visible action; at most two layered on the same instant (e.g. `sparkle` + `pop`).
- Density: an accent every 0.5–2 s, never a wall of sound; held beats stay quiet.
- Leave the held/proof frame almost silent so the product's own visuals carry it.
- Sounds sit under the voice: per-effect volume 0.16–0.55; the delivered mix is −14 LUFS / −1 dBTP.
- No music bed. In the default light set, no bass booms except the single name-reveal `thud`; heavier sounds come
  from the flavour library below, under its own rules.
- Time sounds to the visual frame, not the word, when they differ by more than 0.08 s.

## Flavour library: meme and cinematic sounds (opt-in by content)
The light sparkle/ting/click set stays the default. Reach for these when the moment's tone asks for it: comedy
beats (a fail, an awkward pause, a punchline, a "wait, what?") or drama (suspense build, big reveal, a
before/after). All are original syntheses or local TTS performances. They do the same job as the famous meme
and trailer sounds without copying any specific recording, and the bell is a generic bell, not a brand's sound
mark. That keeps monetized posts safe from claims.

| Ask for | File (`assets/sfx/`) | Length | Use it for |
| --- | --- | --- | --- |
| Vine-boom-style dramatic boom | `boom-dramatic` | 2.3 s | the punchline / "caught you" freeze-frame, a deadpan reveal |
| "Fahhh / Faaah" | `voice-fah` | 1.0 s | exasperated reaction after a fail or a bad take |
| "Bruh" | `voice-bruh` | 0.7 s | unimpressed reaction to something silly or obvious |
| "Huh?" | `voice-huh` | 0.4 s | confusion, a weird result, a double-take |
| Bonk | `bonk` | 0.55 s | cartoon hit on a wrong answer, a facepalm, "go to jail" |
| Fast-food-style bell bong | `bell-bong` | 3.2 s | a big comedic "ding" moment; one hit, let it ring |
| Short whoosh / swoosh | `swoosh-short`, `whoosh-quick`, `whoosh` | 0.2–0.4 s | fast motion, a card flying in, a quick cut |
| UI click | `ui-click` | 0.03 s | a tap on an interface element |
| Mouse click | `mouse-click` | 0.13 s | a cursor click (press + release) |
| Bubble pop / pop-up | `bubble-pop`, `popup` | 0.1–0.2 s | a bubble, badge or notification appearing |
| Camera shutter | `camera-shutter` (light: `shutter`) | 0.3 s | a screenshot, a photo, a freeze-frame |
| Cinematic riser | `riser-cinematic` | 3 s | build-up that lands on a reveal (cue so it ends on the hit) |
| Bass impact / sub drop | `bass-impact`, `sub-drop` | 1.8–2.3 s | weight on a title slam, a drop after a riser |
| Suspense riser | `riser-suspense` | 4 s | "but then…", a cliffhanger line |
| Heartbeat | `heartbeat` | 4.2 s | nervous anticipation, a risky moment |
| Ticking clock | `clock-ticking` (single tick: `tick`) | 6 s | deadlines, "you only have…", time pressure |
| Low cinematic drone | `drone-low` | 8 s | a serious, documentary stretch under the voice |
| Horror / suspense sting | `sting-horror` | 4.2 s | a shocking stat, a warning, "this is bad" |
| Reverse whoosh | `whoosh-reverse` | 0.9 s | swells into a cut or a reveal (end it on the cut) |
| Sub-bass rumble | `rumble-sub` | 5 s | tension under a big claim, an approaching reveal |
| Tension strings | `strings-tension` | 5 s | a dramatic build, a problem getting worse |
| Pulsing bass | `bass-pulse` | 4 s | urgency, countdown energy, a montage push |
| Dark piano hit | `piano-dark` | 6.5 s | a sombre beat, "and that's when it went wrong" |
| Cinematic impact / boom | `impact-cinematic` | 5.4 s | the one biggest reveal of a dramatic reel |
| Riser with a sudden stop | `riser-stop` | 2.2 s | build-up that cuts to dead silence right before the reveal |
| Brief silence before the reveal | technique (+ `silence-0.5s`) | 0.3–0.6 s | see below |

**Brief silence before the reveal.** This is an edit, not a file. Leave 0.3–0.6 s with no effects right before
the reveal: end a `riser-stop` or `whoosh-reverse` on the silence, then land the reveal with a `glint`, `sparkle`,
`impact-cinematic` or `boom-dramatic`. If the speaker pauses there, keep the pause when tightening
(`"keep_pauses": true` on that take in `build/takes.json`) and hold the frame.

### Rules for the flavour library
- Match the topic and tone. A product tutorial stays light; a "my app got rejected" story can take a `sting-horror`;
  a fail compilation can take `voice-bruh` and `bonk`. Never put comedy sounds on serious topics (health, money
  loss, grief).
- Meme sounds are seasoning: two or three per reel at most, each on a clear comedic beat, never two in a row.
- Beds (`drone-low`, `strings-tension`, `rumble-sub`, `heartbeat`, `clock-ticking`, `bass-pulse`) run only for the
  tension stretch (2–8 s) at 0.12–0.25 volume, fade in and out, and stop before the payoff. They are not a music
  bed and never run under the whole video.
- One big cinematic impact per reel. Risers end exactly on the hit or on the silence before it.
- Voice reactions (`voice-*`) sit between the speaker's lines, never on top of a spoken word.
- To regenerate: `python scripts/make_sfx.py` (synthesized set) and `python scripts/make_voice_sfx.py` (TTS set;
  needs a Python with `kokoro-onnx` + `soundfile`, found automatically at `~/.cache/hfsep` or via `HYPERFRAMES_PYTHON`).
