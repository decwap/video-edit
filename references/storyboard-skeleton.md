# Storyboard skeleton

The proven shape of a 60–90 s reel cut from raw footage (the worked example `examples/STORYBOARD.md` is a 75 s, 34-beat
instance). Keep the rhythm and the roles; replace every word, prop and clip with this video's.

**Face panel:** the tables below come from a full-frame reel. By default the speaker stays in the panel for the whole reel, so read
SPLIT as PANEL, and turn each DEPTH, PUNCH or CARD beat into a new graphic on the stage, unless the user asks for full-frame beats.

## STORYBOARD.md format
```markdown
---
format: 1080x1920
fps: 30
duration: <total>
arc: Hook → Claim → … → CTA → End card
---
# <title> — storyboard
Jump cuts in the voice edit: <list from takes.py> — each lands on a layout change or is hidden under a CARD.

| # | Time | Layout | On screen | Transition in | Sound | Why |
|---|------|--------|-----------|---------------|-------|-----|
| 1 | 0.00–1.84 | DEPTH | giant **views** behind his head + trend arrow; plates "My video started" / "getting more" | open on a settle zoom | swoosh, glint | the promise in the first second |
…
## Decisions
- Hero chip, the three DEPTH words, held beat, proof beat, transition mix, sound character, anything inferred.
```
Present the same table to the user before building, unless they asked to go straight to the render. The `Why` column
says what each beat does for the viewer (hook, proof, covers a jump cut…).

**Length:** `TOTAL` = the voice length + 1.5–2 s for the end card (`Reel(total=TOTAL, fps=…, voice_dur=VOICE)`); the
last line of speech can run into the end card, which holds silent after the voice ends.

## The arc and its beats
| Role | Typical length | Layout | What carries it |
| --- | --- | --- | --- |
| **Hook** (first 2–3 s) | 1.5–2 s | DEPTH | the promise or pain as a giant word behind the head; plates for the line |
| Hook payoff | 1.5–2 s | SPLIT | a before/after pair, a real result, the thing being shown |
| Setup / tension | 1.5–3 s | PUNCH → CARD | the contrast or problem as a simple chart / icon card with a serif stack |
| **Claim** | 2–2.5 s | SPLIT | the hero chip debuts; the tool / method named (logo tile, the real prompt typing) |
| Who / why it matters | 2–2.5 s | CARD | avatars, a stat card *only with real numbers*, "most creators…" |
| Emphasis line | 1 s | PUNCH | one plate, accent word |
| Benefits ×2–3 | 2–4 s each | SPLIT / CARD | phones with real clips + engagement icons, watch-time bar, motion-graphics card |
| **Held beat** | 2–2.5 s | CARD | a grid of real clips playing (only the footage moves) |
| "like this" / self-reference | 1 s | PUNCH + viewfinder | REC corners, shutter |
| Personal proof | 3–3.5 s | SPLIT | the creator's own videos fanned in phones |
| **Payoff word** | 1.5–2 s | DEPTH | second giant word behind the head |
| Options / variety | 2–2.5 s | CARD | swatches, list cards, ⌘C copy |
| **Name reveal** | 1 s | CARD | the product's real page in a browser window; hero chip slams (`thud`) |
| How it works | 2.5–3 s | SPLIT | an edit timeline / terminal / app flow assembling itself |
| Objection killer | 2 s | PUNCH | "without knowing how to code" + struck chip |
| No-X / no-Y | 3.5–4 s | CARD (two halves, vertical push) | struck words over an empty editor, an install that never finishes |
| Back to the tool | 1.5 s | SPLIT | real terminal / app capture + hero chip |
| **Proof beat** | 4 s | CARD | raw → edited film strip with the clock counting down; feature chips |
| Sensory detail | 2 s | CARD | sound chips that light with their own sounds, "just like this" |
| **Payoff word** | 2 s | DEPTH | third giant word |
| The recipe | 3–4.5 s | CARD | checklist rows ticking, a real B-roll clip inside a row |
| Outcome | 2 s | SPLIT | phone + watch bar to 100 % + loop |
| CTA set-up | 1.5 s | PUNCH | "copy my style" + ⌘ C |
| CTA offer | 3.5–5.5 s | CARD (two halves) | real examples → the prompt card, blurred + locked, Download pressed |
| CTA action | 4 s | SPLIT | Follow → Following, comment box types the keyword, DM drops in |
| CTA fallback | 1.3 s + 1.9 s | PUNCH → CARD | "not in your DM?" → profile card, link-in-bio ring + tap |
| **End card** | 1.5–2 s | END CARD | two-line serif, hero chip, "comment KEYWORD" |

Not every reel has every role: map the transcript's lines onto the roles that exist, merge or drop the rest, and keep
the layout rhythm (never two identical layouts across a jump cut, no beat over ~4.5 s without an internal change).
