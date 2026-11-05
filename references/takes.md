# Choosing the best takes

Raw phone recordings are mostly retakes: the speaker starts a line, stumbles, starts again, sometimes five times, and
talks to themselves in between ("let's cancel that"). The edit keeps **one clean read of every line, in the order the
message needs**, and nothing else. In the worked example a 5:26 recording became a 73.7 s voice track from 16 takes
(`examples/takes.json`).

## 1. Read the recording as attempts
```bash
python <SK>/scripts/phrases.py build/transcript.json
```
Each line is one **attempt** with its source times — the take is split at sentence ends, at pauses and wherever the
speaker restarts, so every retake sits on its own line:
```
#12     …   45.48-  47.08  And this is how,
#13 ↻12 …   47.08-  49.32  and this is how most of your favorite,
#14 ↻13 ★   49.40-  53.16  and this is how most of your favorite content creators are using now.
```
- `↻n` opens like attempt n (same first three words) — another try at the same line.
- `…` cut off: it never reaches a sentence end and the next attempt restarts it.
- `★` complete and not retried within the next few attempts — usually the keeper.

The hints are a starting point, not a verdict (a line that changes its opening between tries isn't linked; a complete
attempt may still be the weaker read). Read the whole list first, write down the message as the speaker meant it, line
by line, then pick the best read of each line.

## 2. Pick the take for each line
- **Prefer the last complete read.** Speakers repeat until they are happy; the final attempt is usually the fluent one.
- **Complete beats perfect:** a take that says the whole line in one breath beats a splice of two half-takes. When no
  single take is complete, splice at a natural boundary (a comma, "and", "because") where the pitch matches: "…more
  views because | I made Claude do the editing for me."
- **Prefer takes that continue into the next line** — a continuous stretch (24.40–31.52 s in the example, two sentences)
  needs no join at all.
- **Drop tangents and meta talk** ("let's cancel that", "wait, again", counting in), false starts, and lines that only
  repeat an earlier point. Keep each idea once.
- **Keep the speaker's words.** Never splice words into a sentence they didn't say or reorder ideas into a new claim.
  Captions may show the intended word when the speaker slips ("in my DM" → caption "in your DM"); say so in the summary.
- **Watch the framing:** if the speaker moved mid-recording, takes from different parts look different — that is fine,
  every join is covered by a layout change anyway, but note where it happens for the face-card shift.

## 3. Write build/takes.json
Use ASR times: `from` = start of the first kept word, `to` = end of the last kept word.
```bash
python <SK>/scripts/phrases.py build/transcript.json --range 150-158     # word-by-word times for a stretch
```
```json
[
 {"from": 24.40, "to": 31.52, "say": "My video started getting more views because I changed my video style. And even though I have less followers,"},
 {"from": 38.28, "to": 43.40, "say": "I get more views because I made Claude do the editing for me."},
 {"from": 160.68, "to": 170.57, "exact_end": true, "say": "And you don't need to be a video editor, … motion effects"}
]
```
`say` is for you and the user (it is printed back); the times are what matter. `exact_end` / `exact_start` turn off
the gap snapping for that boundary.

## 4. Snap, tighten, check
```bash
python <SK>/scripts/takes.py --src "<video>" --words build/transcript.json --takes build/takes.json --out build --show
```
Read the printout: every boundary should say `gap a-b` (a real silence) and, with `--show`, the `|` should sit in the
quiet part of the envelope just after a word decays (end) or just before it starts (start). `NO GAP` means the times are
off by more than ~0.4 s — recheck the words with `--range`.

A `⚠ short gap` note on an end means the "gap" may be the closure of a stop consonant inside the last word (the k/t of
"effects", "code"): the cut can shave the end of the word, and the re-transcription does not always notice (Parakeet
still read "effects" with its final "s" cut). For those ends, look at the `--show` envelope: if sound resumes within
~0.1 s and belongs to the same word, move `to` past it; if it is the next word, keep the cut.

Then build the voice and **re-transcribe it** (pipeline.md §2). Read the result as a viewer would hear it:
- a word missing at a join → that take's `to` is too early (a stop consonant like the "k" in "effects" or "code"
  makes a 60–80 ms dip the gap finder mistakes for silence) — move `to` 0.2–0.5 s later;
- a word doubled across a join → the take ran into the start of the next line — set `to` before it, `exact_end: true`;
- a stray "and" / "now" in a join where the audio is silent → the ASR guessing; ignore it.
Repeat until the read is clean. Show the user the final read (a few lines) together with the storyboard.
