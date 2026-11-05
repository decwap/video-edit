# Video Edit — pipeline commands and gotchas

`<SK>` = this skill's folder (`~/.claude/skills/video-edit`). `<P>` = the HyperFrames project for this reel. Pin the
CLI the project was initialised with (`npx --yes hyperframes@0.8.106 …`). Run long steps (A-roll, mattes, `check`,
render) as tracked background jobs with a log file, so an interrupted session doesn't lose the work.

## Contents
0. Set up a new machine
1. Look at the footage
2. Transcribe, choose the best takes, verify the cut
3. A-roll intermediates (and HDR)
4. B-roll: own videos, product captures, the raw→edited strip, stock
5. The face panel and depth mattes
6. Build, check, review
7. Render (HD or 2K) and deliver
8. Gotchas we already paid for

## 0. Set up a new machine
Check: `node -v` (18+) · `ffmpeg -version` · `ffprobe -version` · `python --version` (3.10+) ·
`python -c "import numpy, scipy, PIL, cv2"`. Install what is missing:
- **Windows:** `winget install OpenJS.NodeJS.LTS Gyan.FFmpeg Python.Python.3.12` (open a new terminal afterwards).
- **macOS:** `brew install node ffmpeg python`.
- **Linux:** `sudo apt install nodejs npm ffmpeg python3-pip` (or the distro equivalent; Node 18+).
- Python packages: `python -m pip install numpy scipy pillow opencv-python`.
- HyperFrames: nothing to install — `npx --yes hyperframes@0.8.106 …` fetches the pinned CLI (and its headless Chrome on
  the first render). Its skills: `npx skills add heygen-com/hyperframes`; `hyperframes init` also links them per project.
- ffmpeg must have `zscale` for HDR phone footage (`ffmpeg -filters | grep zscale`); the gyan.dev / Homebrew builds do.
- The face panel also needs ffmpeg's `libvpx-vp9` decoder, to read the cutout's transparency (`ffmpeg -decoders | grep libvpx-vp9`).
First runs download models (Parakeet transcription, background removal); later runs use the cache.

## 1. Look at the footage
```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate,avg_frame_rate,color_transfer "<video>"
ffmpeg -v error -i "<video>" -vf "fps=1/5,scale=270:480,drawtext=fontfile='<font>':text='%{pts\:hms}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.7,tile=11x6" -frames:v 1 overview.jpg
```
- `color_transfer` = `arib-std-b67` (HLG, iPhone) or `smpte2084` (PQ) means HDR: add the tone-map from §3 to any frame
  you extract for looking, or the sheet will look grey and washed out. `aroll.py` and `strip.py` handle it themselves.
- `r_frame_rate` vs `avg_frame_rate`: phones record variable frame rate (e.g. 30/1 vs 29.99). Everything is conformed to
  the nominal fps and the reel renders at that fps (30 for iPhone, 25 for many cameras) — never 30 over 25 fps footage.
- `drawtext` needs an explicit `fontfile` on Windows: `C\:/Windows/Fonts/arialbd.ttf`; macOS
  `/System/Library/Fonts/Supplemental/Arial Bold.ttf`; Linux `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`.
- Long raw takes: one sheet every 5 s is enough to see framing changes (the speaker moved closer, re-sat, changed
  light). Note where they happen: the face-card shift and DEPTH word positions differ on each side.
- Map the framing on a grid frame (`drawgrid=w=108:h=192`): head top, chin, face centre. `aroll.py --face` measures it.

## 2. Transcribe, choose the best takes, verify the cut
```bash
ffmpeg -v error -y -i "<video>" -vn -ac 1 -ar 16000 build/audio16k.wav
npx --yes hyperframes@0.8.106 transcribe build/audio16k.wav --engine parakeet --language en --json -d build   # -> build/transcript.json
python <SK>/scripts/phrases.py build/transcript.json                 # one line per attempt: ↻ retakes, … cut off, ★ suggested keepers
python <SK>/scripts/phrases.py build/transcript.json --range 95-110  # exact word times for one stretch
#   write build/takes.json (references/takes.md), then:
python <SK>/scripts/takes.py --src "<video>" --words build/transcript.json --takes build/takes.json --out build --show
```
- `takes.py` prints each take's snapped boundaries and, with `--show`, an ASCII envelope (`#` loud … blank silent) with
  `|` at the cut: the cut must sit in blank/`.` space with the word's decay before it. It writes `edl.json`,
  `words.json` and the list of jump cuts on the new timeline.
- **Verify by ear-proxy:** build the voice (`aroll.py --steps voice`), re-transcribe it and read it start to finish:
  ```bash
  ffmpeg -v error -y -i assets/voice.wav -ac 1 -ar 16000 build/vcheck/voice16k.wav
  npx --yes hyperframes@0.8.106 transcribe build/vcheck/voice16k.wav --engine parakeet --language en --json -d build/vcheck
  python <SK>/scripts/phrases.py build/vcheck/transcript.json --gap 0.35
  ```
  A missing last word ("how to … And" instead of "how to code. And") means a take end landed on a stop-consonant
  closure: move `to` later. A doubled word ("effects, and … and different") means the take ran into the next line:
  set `to` before it with `"exact_end": true`. A lone "and"/"now" at a join with nothing in the audio is the ASR
  inventing a word in a short silence — ignore it. Rebuild until the read is clean, then use this re-transcription
  (`build/vcheck/transcript.json`) for caption timing: it is measured on the final voice.
- Every jump cut printed by `takes.py` must land on a layout or framing change in the plan (or under a CARD/B-roll beat).

## 3. A-roll intermediates (and HDR)
```bash
python <SK>/scripts/aroll.py --edl build/edl.json --assets assets --face          # grid sheet (+ Haar estimate on OpenCV 4)
python <SK>/scripts/aroll.py --edl build/edl.json --assets assets --head-top 714 --eyes 870 --face-x 520 [--size 1440x2560]
python <SK>/scripts/aroll.py --edl build/edl.json --assets assets --steps voice      # voice only (the §2 check)
```
- One decode pass → `aroll_wide.mp4` (SPLIT card, DEPTH, wide), `aroll_tight.mp4` (PUNCH, 1.4× crop), `voice.wav`
  (highpass, light compression, −15 LUFS). Frames = round(total × fps); check with
  `ffprobe -count_frames -show_entries stream=nb_read_frames`.
- **No colour grade.** Footage keeps the colours it was shot with. HDR (HLG/PQ) is converted to SDR BT.709 only
  because it plays washed out otherwise: `zscale=tin=arib-std-b67:pin=bt2020:min=bt2020nc:t=linear:npl=203,
  format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`.
- `--size 1440x2560` (2K) or `2160x3840` (4K) for a high-resolution delivery (§7); use it when the source is at least
  that big — upscaling 1080p footage adds no detail (the graphics still get sharper at 2K, the face doesn't).
- If the speaker moved during the recording, `--face` reports the median; measure each part on a grid frame and pass
  the per-part face shift to the scenes (`split_at(..., shift=...)`).

## 4. B-roll: own videos, product captures, the raw→edited strip, stock
Priority: (1) the creator's own videos — earlier edits, demos, screen recordings — they are real proof of "videos like
this"; (2) real captures of the product/tool being named (its own website, its own app screens); (3) `strip.py` thumbnails
of this very recording for a raw→edited proof beat; (4) stock only when nothing real fits.
```bash
ffmpeg -v error -i "<old reel>.mp4" -vf "fps=1/2,scale=120:-2,tile=20x4" -frames:v 1 build/look/reel-a.jpg   # pick moments
python <SK>/scripts/prep_broll.py --fps 30 old-a="<old reel>.mp4"@3.0+4.0 old-b="<other>.mp4"@10.6+4.0   # -> assets/bv/
python <SK>/scripts/strip.py --src "<video>" --edl build/edl.json --out assets/img/strip                 # sprite + strip.json
python <SK>/scripts/stock.py search "content creator filming" --tag creator   # look at build/stock/creator.jpg, then:
python <SK>/scripts/stock.py get <id> <id>                                       # -> assets/broll/px-<id>.mp4 + CREDITS.md
```
- Pick bright, readable, mid-hold moments (never a fade or a dark stretch); clips 0.3–0.5 s longer than their beat.
- Product sites: capture the official page with headless Chrome (puppeteer-core from the HyperFrames install) or
  download the official mark from the brand's press kit. Never redraw a product UI or a logo.
- `screen_replace.py` puts the creator's own app screens onto a stock clip of a hand holding a white-screen phone.
- Stills for phone mockups: one frame of each clip (`ffmpeg -ss 1.0 -i assets/bv/x.mp4 -frames:v 1 assets/img/stills/x.jpg`).

## 5. The face panel and depth mattes
```bash
python <SK>/scripts/make_panel.py --src assets/aroll_wide.mp4     # writes assets/person.webm + build/panel.json
```
- It cuts out the whole A-roll on this computer, with no upload and no credits: about 0.2 s per frame on Apple silicon and about 1 s on
  CPU, plus a model download on the first run. Run it as a background job with a log. `--measure-only` prints the fit first.
- It sets the footage's scale from the measured head width (`--head-w` overrides it when long hair or a hat throws it off) and warns
  when the speaker is so far away that the scale goes past 1.6, because the speaker will look soft.
- "head jumps: cut a panel beat at …" lists the joins where the speaker moved: start a new `panel()` beat at each one.
- In the scene: `use_panel(PROJECT / "build/panel.json")`, then `s.paper` + `panel(s, name, g0, g1, tight=False)`
  (`examples/panel_scene.py`). Scenes built without `use_panel` behave as before.
- A second clip, such as an end-card hold: `make_panel.py --src assets/bv/endface.mp4 --out assets/person_end.webm --json
  build/panel_end.json`, then `panel(s, name, g0, g1, data=load_panel("build/panel_end.json"), media_start=0.1)`.
- Check the panel on real render frames, read by index, because snapshots use a different pipeline from the render:
  `ffmpeg -i final.mp4 -vf "select='eq(n,1500)'" -fps_mode passthrough -frames:v 1 f.png`. Look at the head's edge and for a line across
  the head at y 1282.

Depth mattes, for DEPTH beats:
```bash
python <SK>/scripts/make_matte.py --src assets/aroll_wide.mp4 --start 29.40 --dur 1.76 --out assets/depth_styles.webm
```
- Start 0.03–0.05 s before the beat and run a little past it; in the scene `media_start = beat start − matte start`.
- Use the **wide** framing (in the tight crop the head covers the whole word). ~0.6–1.2 s per frame on CPU: run all
  mattes in one background job and confirm each `.webm` duration with ffprobe.
- In the scene: base video → word layer → matte video (identical zoom keys) → captions on top.

## 6. Build, check, review
```bash
npx --yes hyperframes@0.8.106 init "videos/<slug>" --non-interactive --example=blank --skill=general-video
#   copy <SK>/assets/fonts, <SK>/assets/img/*.png, <SK>/assets/sfx into <P>/assets/ ; Lucide icons stay in the skill
python build/scenes.py                       # on video_kit, pattern: <SK>/examples/scenes.py (+ scenes_b.py)
npx --yes hyperframes@0.8.106 lint
npx --yes hyperframes@0.8.106 check          # must end "Check passed" (layout, motion, WCAG contrast)
npx --yes hyperframes@0.8.106 snapshot --at <one moment per beat, comma-separated> --no-end --timeout 30000 --describe false
```
- Read every contact sheet. Typical fixes: a CARD whose content sits in the top half (move it down with `card(dy=…)`),
  props covering the chin in a PUNCH (move them to the background above the shoulders), a DEPTH word that floats above
  the head instead of behind it (lower it until the hair covers its bottom 10–20 %), a cursor parked on screen before it
  moves (start it off-canvas).

## 7. Render (HD or 2K) and deliver
**HD (default) — 1080×1920:**
```bash
npx --yes hyperframes@0.8.106 render --fps 30 --quality delivery --crf 14 --output renders/<slug>_master.mp4
```
**2K — 1440×2560:** the renderer scales by whole numbers only (1080p or 4K), so render at 4K and downsample — the
graphics and text come out sharper than a 1080p render, and nothing is upscaled:
```bash
npx --yes hyperframes@0.8.106 render --fps 30 --quality delivery --crf 12 --resolution portrait-4k --output renders/<slug>_4k.mp4
ffmpeg -v error -y -i renders/<slug>_4k.mp4 -vf "scale=1440:2560:flags=lanczos" -c:v libx264 -preset slow -crf 14 \
       -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a copy -movflags +faststart renders/<slug>_master.mp4
```
(4K delivery: keep `renders/<slug>_4k.mp4` itself. 4K takes ~3–4× longer to render than HD.)
Then, for every resolution:
```bash
python <SK>/scripts/verify_render.py renders/<slug>_master.mp4 --sheet renders/sheet.jpg --normalize renders/<slug>_final.mp4
python <SK>/scripts/sync_check.py renders/<slug>_final.mp4          # every window +0.0 ms
```
- Read the render log for `media_readiness_timeout` / "did not load": an image that wasn't ready renders blank in some
  frames. Fix the cause (fewer separate images — one sprite; smaller files) and render again.
- `--normalize` re-encodes only the audio to −14 LUFS / −1 dBTP (video stream copied, no quality loss).
- Copy the final next to the original as `<name> (Edited).mp4` and the sheet as `<name> (Edited) - frames.jpg`; keep
  older renders in `renders/`.

## 8. Gotchas we already paid for
- **Times:** scene methods take global seconds; JS positions are scene-local — use `s.L(global)` in every `J(s, …)`.
- **Lint `nested_media_start_basis_ambiguous`:** informational for videos that start mid-scene; leave it.
- **Lint `video_nested_in_timed_element` (error):** a `<video>` inside a layer that starts mid-scene plays the wrong
  frames. Phone / frame / window clips live in `s.body` (`phone_vid`, `framed`, `win_vid` do this) and show via opacity.
- **Many images → blank frames:** a film strip of 33 separate `<img>` files timed out at render start and one thumbnail
  rendered black. Use one sprite (`strip.py`) or few, small images.
- **ffmpeg + a looped still as a mask:** give the still `-loop 1 -framerate <fps>` and the blend `shortest=1`, or the
  output runs forever and duplicates frames (the old vignette step did this).
- **ffprobe takes one input** — probing several files in one call fails with "provided as input filename"; loop instead.
- **Stop consonants fool gap finding:** the closure inside "effects", "code", "takes" looks like a 60–80 ms gap. Always
  verify the cut voice (§2); fix with a later `to` or `exact_end`.
- **ASR timing:** Parakeet word starts run ~0.1–0.3 s early and ends swallow pauses. Fine for captions (slightly early
  reads well), wrong for cuts — `takes.py` snaps cuts to the audio.
- **Layout errors from tight serif stacks:** `data-layout-allow-overlap` on each line element (srow / nrow add it); keep
  ~0.18 em between a descender and the next line.
- **Contrast:** small labels on paper need ≥ `#746D62`; grey `#8F877B` only at 24 px+.
- **Fonts:** every composition carries its own `@font-face` (the library does it); never reference Google Fonts.
- **Jump cuts:** two same-layout beats either side of a cut need a framing change (face card 1.22×, punch vs wide).
- **Hidden-until-fired effects:** a `fromTo` from a visible state (ripples, rings) needs `immediateRender: false`.
- **Too many sound cues (Windows):** hundreds of `<audio>` tags overflow the renderer (`spawn ENAMETOOLONG`):
  `finish()` pre-mixes every cue into one `assets/sfx_mix.wav`.
- **A line across the head at the panel's edge:** the browser draws footage and cutout at different brightness when their colour
  tags differ (some cameras tag `iec61966-2-4`). Both need identical bt709 tags and the same `data-media-start`; `make_panel.py`
  tags both, and any file you swap in later needs the same.
- **The speaker moves between takes:** read the head from the cutout's alpha (`make_panel.py`), not by eye. A median per beat keeps
  the head still across a join, and head width is a steadier measure of size than head height, which moves with the chin.
- **`snapshot` and privacy:** keep `--describe false`; without it frames are sent to Gemini to be described.
- **`nested_media_start_basis_ambiguous` from `lint`:** expected on scene videos. Their `data-start` is local to the scene, as the
  warning's first case says.
- **Face card that must expand:** animating `top`/`height` fails lint; the kit's face card is a clip-path layer
  (`face_rise`, `expand`).
- **Duplicate ids:** `getElementById` returns the first match — prefix every id with the scene id and scan the built
  HTML for repeats.
- **Text under a wipe:** captions still visible while a paper sheet slides over them fail the contrast audit; end them
  0.1–0.2 s before the wipe reaches their y.
- **Windows shell:** inline Python with quotes inside bash heredocs breaks easily — write scripts to files.
- **Background jobs:** start long steps as tracked background tasks with a log; a bare trailing `&` dies with its shell.
