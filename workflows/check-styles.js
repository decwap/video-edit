export const meta = {
  name: 'check-styles',
  description: 'Check every style of a finished video edit (lint, check, frames) and fix what breaks, one agent per style, before the Style Picker opens',
  whenToUse: 'video-edit, after `styles.py build`: args {project, skill, styles?, times?, python?}',
  phases: [
    { title: 'Reference', detail: 'snapshots of the Warm Paper edit at the review moments' },
    { title: 'Styles', detail: 'one agent per style: lint + check, frames, fixes in build/style-overrides/<id>.css' },
  ],
}

// args: {
//   project: absolute path of the HyperFrames project (the edit: index.html + compositions/, styles/ already built)
//   skill:   absolute path of the video-edit skill (the folder with SKILL.md and scripts/styles.py)
//   styles:  optional list of style ids (default: every style except paper, which is the edit itself)
//   times:   optional list of seconds to review (default: one moment per scene, from index.html)
//   python:  optional interpreter (default python3; pass "python" on Windows)
// }
const STYLES = {
  glow: 'Midnight Glow: near-black ground, cyan and violet light, a faint grid, glassy cards, Outfit',
  doodle: 'Storybook Doodle: notebook paper, ruled lines, a red margin, hand-drawn ink outlines, Caveat + Nunito',
  editorial: 'Bold Editorial: newsprint, halftone corners, black rules, uppercase League Gothic, captions on black bars',
  block: 'Colour Block: a flat full-bleed colour per scene (blue, bone, black, lime, vermilion), uppercase Anton, flat cards',
  riso: 'Riso Print: ultramarine and fluorescent pink on grainy paper, halftone discs, offset pink shadows, Bodoni Moda',
  terminal: 'Signal Terminal: black screen, scanlines, lime glow, everything in JetBrains Mono, outlined panels',
  sticker: 'Sticker Board: cream board, dot grid, thick black outlines and hard shadows, Bricolage Grotesque',
  aurora: 'Aurora: pale cool ground lit by lavender, peach, mint and sky light, a dot grid, glass cards, serif italic',
}

if (!args || !args.project || !args.skill) {
  throw new Error('check-styles needs args {project, skill}: the HyperFrames project and the video-edit skill folder')
}
const P = String(args.project).replace(/\/+$/, '')
const SK = String(args.skill).replace(/\/+$/, '')
const PY = args.python || 'python3'
const TOOL = `${PY} "${SK}/scripts/styles.py"`
const AT = Array.isArray(args.times) && args.times.length ? ` --at ${args.times.join(',')}` : ''
const ids = (Array.isArray(args.styles) && args.styles.length ? args.styles : Object.keys(STYLES))
  .filter((id) => id !== 'paper')
const unknown = ids.filter((id) => !STYLES[id])
if (unknown.length) throw new Error(`unknown style(s) ${unknown.join(', ')}; the styles are ${Object.keys(STYLES).join(', ')}`)

const RESULT = {
  type: 'object',
  properties: {
    style: { type: 'string' },
    lint_ok: { type: 'boolean' },
    check_passed: { type: 'boolean', description: 'styles/<id>/check.log ends with "Check passed" after your last build' },
    verdict: { type: 'string', enum: ['good', 'usable', 'broken'], description: 'good: ready to show; usable: small flaws listed; broken: do not show it' },
    fixes: { type: 'array', items: { type: 'string' }, description: 'each fix you made, one line: what was wrong, where (scene / time), the rule you added' },
    remaining_issues: { type: 'array', items: { type: 'string' }, description: 'what is still wrong, with the scene or time' },
    contact_sheet: { type: 'string', description: 'absolute path of the first contact sheet in styles/<id>/snapshots/' },
  },
  required: ['style', 'lint_ok', 'check_passed', 'verdict', 'fixes', 'remaining_issues', 'contact_sheet'],
}

phase('Reference')
const ref = await agent(
  `Make the reference frames for a style review of a video edit. Run shell commands only; change no files.

Project: ${P}
1. If ${P}/styles/paper/index.html is missing, run: ${TOOL} build "${P}"
2. Run: ${TOOL} snap "${P}" --styles paper${AT}
3. Return ok=true when the command printed N/N frames, and the absolute path of ${P}/styles/paper/snapshots.`,
  {
    label: 'reference:paper', phase: 'Reference', effort: 'low',
    schema: {
      type: 'object',
      properties: { ok: { type: 'boolean' }, snapshots: { type: 'string' }, error: { type: 'string' } },
      required: ['ok', 'snapshots'],
    },
  },
)
if (!ref || !ref.ok) log(`Reference frames failed (${(ref && ref.error) || 'no result'}); the style agents will review without them`)

phase('Styles')
log(`Checking ${ids.length} style(s): ${ids.join(', ')}`)
const results = await pipeline(ids, (id) => agent(
  `You check one style of a finished video edit before the creator sees it in the Style Picker, and fix what is broken.

Project: ${P}  (a HyperFrames project: the edit is index.html + compositions/, in the Warm Paper look)
Style: ${id}  (${STYLES[id]})
Style folder: ${P}/styles/${id}/  (generated from the edit by styles.py; every build overwrites it, so never edit it by hand)
Your only place for fixes: ${P}/build/style-overrides/${id}.css  (plain CSS, added last to every composition of this
style; scope a rule to one scene with that scene's ids, which all start with the scene id, e.g. #s07-..., or use the
kit's classes). How the styles work and the usual fixes: ${SK}/references/styles.md. Tool: ${TOOL}

1. Check. Run: ${TOOL} check "${P}" --styles ${id}
   It runs hyperframes lint + check and writes ${P}/styles/${id}/check.log. If it fails, read the log, fix the cause in
   the override file, rebuild with: ${TOOL} build "${P}" --styles ${id}  and check again (at most 3 rounds). A contrast
   warning is not a failure, but fix one on text the viewer has to read.
2. Look. Run: ${TOOL} snap "${P}" --styles ${id}${AT}
   Read every ${P}/styles/${id}/snapshots/contact-sheet*.jpg (a long edit gets several), then open the full frames wherever something looks off. Compare
   each frame with the same moment in Warm Paper (${ref && ref.ok ? ref.snapshots : `${P}/styles/paper/snapshots`}/frame-NN-*.png, same NN): the
   layout must match; only the look changes. Look for: text or a card that vanishes into the ground; words in a
   fallback font (Times or Arial instead of the style's font); a line that runs off the canvas or wraps differently
   from Warm Paper; decor (grid, ruled lines, halftone, light, scanlines) over text or over the speaker's face; a
   caption that can't be read on its footage; anything that looks broken or unfinished.
3. Fix what you found (override file, build, snap again), at most 2 rounds. Never change the words, timing, footage,
   motion or sound; never touch other styles, the edit's own files or the skill. If a fix needs more than CSS, leave it
   and list it in remaining_issues.

Return the result for style ${id}.`,
  { label: `style:${id}`, phase: 'Styles', schema: RESULT },
))

const done = results.filter(Boolean)
const missing = ids.filter((id) => !done.some((r) => r.style === id))
const ready = done.filter((r) => r.check_passed && r.lint_ok && r.verdict !== 'broken').map((r) => r.style)
const attention = done.filter((r) => !ready.includes(r.style)).map((r) => r.style).concat(missing)
log(`Ready for the picker: paper, ${ready.join(', ') || 'none'}${attention.length ? ` · needs attention: ${attention.join(', ')}` : ''}`)
return { project: P, ready: ['paper', ...ready], needs_attention: attention, results: done }
