# Video Edit — style reference

A vertical talking-head reel in the warm-paper editorial look: the speaker alternates with paper cards of italic-serif
kinetic words, real B-roll and small UI props, changing every 2–3 s. Swap only the accent colour, the hero chip text
and the B-roll per video; everything else stays.

## Canvas & pacing
- 1080 × 1920 canvas (the composition is always authored at this size; 2K/4K come from the render, pipeline.md §7).
- Render at the footage's own fps (30 for iPhones, 25 for many cameras).
- A layout or graphic change every 2–3 s; one idea per beat. Every jump cut lands on a layout or framing change.
- **Safe zone for captions:** y 760–1500, x 140–940 (clear of the platform's top bar, description and icon rail). Big
  DEPTH words and CARD headlines may sit higher on paper or background.
- **Centre of mass:** a CARD's content block should centre near y 900; a card with everything in the top half and an
  empty bottom third looks unfinished (use `card(dy=…)`).

## Footage
- **No colour grade.** The speaker's footage keeps the colours it was shot with. Phone HDR (HLG / PQ) is converted to
  standard video only so it doesn't play washed out (`aroll.py` does it automatically).
- Wide = the full frame (SPLIT card, DEPTH, wide beats); tight = a 1.4× punch crop centred on the face.

## Palette (by role)
| Role | Hex | Use |
| --- | --- | --- |
| paper | `#F5F1EA` | every CARD / SPLIT background, end card |
| panel | `#ECE6DC` | sheet surfaces, quiet panels |
| card | `#FFFDF9` | floating cards (documents, profile, checklist) |
| ink | `#17140F` | key words, UI text, phone bezel |
| grey | `#8F877B` | connective serif words (large type only); small labels use `#746D62` (AA contrast) |
| accent | `#0B7A73` teal by default | hero chip, checks, strike lines, progress fills, highlighted words, focus rings |
| accent-deep / tint | `#075450` / `#D7ECE8` | pressed states, shadows / quiet fills behind ink text |
| on-accent | `#FFFFFF` | text on an accent fill |
| caption-on-video | `#FFF8EF` + shadow | only on dark footage; on light shirts and walls use paper plates |
Any accent works: `finish(reel, PROJECT, accent="#C9271C")` recolours the whole teal family (red, blue, orange…).
Pick one with ≥ 4.5:1 contrast on paper for text. Product colours appear only inside real product footage or captures.

## Type
- Display: **Instrument Serif Italic** 96–600 px, tracking −0.02 em, line-height .95 — kinetic words, DEPTH words, card headlines.
- Captions: **Instrument Sans 700** 56–96 px, tracking −0.02 em.
- Mono: **JetBrains Mono** 600 — hero chip, terminals, file names, labels.
- Local woff2 in `assets/fonts/` (SIL OFL), declared inside every composition by the library.
- Hierarchy: ink = the word that matters, grey = the connective words around it ("most of your favorite" grey over
  "content creators" ink). One keyword per card.

## Face panel (the default speaker layout)
The speaker sits at the bottom of the frame and stays there. The head rises above the panel's edge onto a light stage that
carries the graphic, so the speaker and the graphic are always on screen together.
- **Panel:** the bottom third of the frame (y 1280–1920, 80 px top radius): the real footage with its own wall behind the speaker.
- **Head:** a cutout of the same frames carries the head above the edge. The edge crosses the head about a third of the way
  down; the head's top lands at y 1061 (tight 1041) and the frame ends near the shoulders. `make_panel.py` sets the
  footage's scale from the measured head width, so this holds on any framing. Never fill the panel with an oversized head.
- **Stage:** paper above the panel. Graphics fill y 100–880. The kit moves `lay`, `framed`, `phone_vid`, `win_vid` and `card` down
  60 px for you.
- **Captions:** one to three words, Instrument Sans 700, 78 px, swapping with the speech (`s.seam_caps` inside `lay`). They land
  at y 932, just above the head.
- **Motion:** the panel never rises or leaves between beats, and nothing animates in on the first frame. `face_rise` and
  `expand` belong to the old flat card and do not apply.
- **Jump cuts:** every panel beat centres the head and holds it at the same height, which hides most of the jump. `tight=True`
  is the framing change for the rest. Cut a new beat at every join in the footage.

## Layouts (canvas px)
1. **PANEL** — the face panel above, for every talking beat. The stage carries the beat's graphic.
   The old flat **SPLIT** (`split_at`: a card at y 1000–1920 covering the whole head, caption at y 872) stays only for when
   someone asks for it or a clean cutout isn't possible.
2. **CARD** — full paper (grain + drifting fern / window-light shadow), no speaker. A graphic plus a serif stack: grey connective words
   + one big ink keyword (150–300 px) that lands on the spoken word.
3. **PUNCH** — speaker full-frame from the tight crop, snap zoom 1.14 → 1.03 → slow push. Caption plates at y ~1262–1290.
4. **DEPTH** — speaker full-frame (wide); a giant serif word (260–600 px) sits behind the head: base video → word →
   background-removed matte of the same footage. The hair should cover the bottom 10–20 % of the letters. 3 per reel.
5. **END CARD** — paper, two-line serif ("copy my / style"), the hero chip, the CTA ("comment REEL").

## Captions
- Every spoken word is on screen in some form: seam captions (SPLIT), plates (PUNCH / DEPTH / wide), or the CARD's serif
  stack (which may compress a phrase to its key words, never change its meaning).
- **Paper plates** (`plates`): paper-coloured pills with ink text — they read on any shirt or wall; serif plates for the
  emphasised line, accent word inside (`acc("now.")`).
- Captions show the intended word when the speaker or the ASR slips; never add a claim the speaker didn't make.
- Swap by hard cut, pop in over 0.16–0.2 s; end them 0.1–0.2 s before a wipe covers them.

## Recurring components
- Hero chip: accent mono pill with the topic's name or command (e.g. `Claude Code`, `/paper-reel`, `REEL`); debuts on
  the claim, returns 3–4 times (name reveal, proof, CTA) and closes the film.
- Phone mockups with real clips; browser windows with real captures; the creator's own earlier videos as "styles like
  this" grids; before/after phone pairs.
- Proof props: raw → edited film strip with a counting clock; an edit timeline assembling itself; sound chips drawn
  from the real waveforms.
- CTA props: Follow → Following, a comment box typing the keyword and sending, a DM notification, a "link in bio"
  profile card; a prompt / document card whose content stays blurred and locked when the CTA gates it.

## Texture & depth
- `assets/img/paper-grain.png` (cotton-rag paper: curly fibres, soft mottling, tiny flecks) soft-light .55 over paper;
  `assets/img/leaf-shadow.png` (window light: fern fronds from the top-left and bottom-right corners and a soft
  window-frame shadow) multiply .3 (SPLIT) – .55 (CARD), drifting ~35 px over the beat. Both are made by
  `scripts/make_textures.py` (deterministic).
- Floating media shadow `0 30px 70px rgba(40,30,20,.22)`; paper cards `0 20px 50px rgba(40,30,20,.14)`.

## Motion
See `references/motion.md` (beats, transitions, props). Entrances .3–.55 s; enter from below or the right, exit up or
left; hard cuts between beats; ambient motion only (leaf drift, slow push, gentle float) — no looping screensaver motion.

## Sound
See `references/sound.md`: light action sounds that answer what is on screen; no music bed.

## Do / don't
- Do: real footage, real captures, the creator's own videos; quote a tool's own docs for steps and commands; keep
  install links off screen when the CTA gates them.
- Don't: colour-grade the speaker, gradient text, glow/neon, emoji, invented UI, invented numbers or stats, mascots or
  characters you didn't design, slideshow beats, a music bed under the voice (unless asked).
