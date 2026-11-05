"""The pop-out face panel: the speaker at the bottom of the frame, with the head rising above the panel's edge onto a light
stage. See references/style.md ("Face panel") for the look and references/pipeline.md §5b for the steps.

    from video_kit import *
    use_panel(PROJECT / "build/panel.json")          # written by make_panel.py
    s = reel.scene("s01", "hook", 0.00, 11.24)
    s.paper("bg", 0.00, 11.24, leaf_op=0.3)          # the stage
    panel(s, "f0", 0.00, 5.44)                       # wide
    panel(s, "f1", 5.44, 6.68, tight=True)           # the framing change that hides a jump cut
    panel(s, "f2", 6.68, 11.24)
    lay(s, "t", 0.00, 5.44, 6, s.seam_caps([("three words max", 0.10, 1.20)]))

Two copies of the same frames are stacked with identical transforms: the footage, clipped to the panel, and its cutout,
clipped to everything above the panel's edge. The panel never rises or leaves between beats; only the stage above it changes.
"""
import json
from pathlib import Path

import paper_reel as pr
import reel_kit as rk

PANEL_TOP = 1280        # the panel's background is the bottom third of the frame
STAGE_DY = 60           # graphics and captions sit this much lower than the kit's layout, to fill the room the lower panel leaves
OVERLAP = 2             # px the cutout runs past the panel's edge, so no line of wall shows between them
# Calibrated on the look the speaker approved. Head width = the widest part of the head and hair, as drawn on the 1080 x 1920
# canvas; it measured steadier than head height, which moves with the chin (+/-2 % against +/-20 % across one recording).
HEAD_W_WIDE = 487
HEAD_W_TIGHT = 532
EDGE_AT = 0.45          # the panel's edge sits this many head widths below the top of the head: about a third of the way down it,
                        # which leaves the frame ending near the shoulders

CSS = f"""
.pop-bg{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;clip-path:inset({PANEL_TOP}px 0px 0px 0px round 80px 80px 0px 0px)}}
.pop-head{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;clip-path:inset(0px 0px {1920 - PANEL_TOP - OVERLAP}px 0px)}}
.pop-cut{{position:absolute;left:0;width:1080px;object-fit:fill}}
"""
# A zero-duration set at time 0 does not fire on a composition's first rendered frame (the playhead has not moved yet), so
# whatever it places would arrive one frame late at every scene start. Apply those sets at build time instead.
JS = r"""
const _set0 = tl.set.bind(tl);
tl.set = (el, v, p) => _set0(el, p === 0 ? Object.assign({}, v, { immediateRender: true }) : v, p);
"""

_data = None


def fit_panel(head_w):
    """Footage scale and head position for a head this wide (1080 px), so it lands at the approved size. Footage is never
    scaled below 1.0: it has to cover the frame's width."""
    k_wide, k_tight = max(1.0, HEAD_W_WIDE / head_w), max(1.0, HEAD_W_TIGHT / head_w)
    return {"k_wide": round(k_wide, 3), "k_tight": round(k_tight, 3),
            "head_at_wide": round(PANEL_TOP - EDGE_AT * k_wide * head_w),
            "head_at_tight": round(PANEL_TOP - EDGE_AT * k_tight * head_w)}


def use_panel(path):
    """Turn the panel on for every scene built after this call: load make_panel.py's data, add its CSS and JS, and move the
    stage (lay, framed, phone_vid, win_vid, card) down by STAGE_DY. Returns the data, for panel(data=...) with a second clip."""
    global _data
    _data = load_panel(path)
    rk.STAGE_DY = STAGE_DY
    _install()
    return _data


def load_panel(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _install():
    # checked here too because configure() rebuilds the kit's CSS and JS
    if ".pop-bg" not in pr.COMMON_CSS:
        pr.COMMON_CSS += CSS
    if "_set0" not in pr.COMMON_JS:
        pr.COMMON_JS += JS


def _median(values):
    return sorted(values)[len(values) // 2]


def panel(s, name, g0, g1, tight=False, data=None, media_start=None):
    """One beat of the face panel (global seconds). The head is centred and held at the same height for the whole beat, from
    its median position in these frames, so cut a new beat at every join in the footage. tight=True is the framing change for
    a jump cut. data + media_start play a second clip prepared by make_panel.py, such as an end-card hold."""
    d = data or _data
    if d is None:
        raise RuntimeError("call use_panel(path) before panel()")
    _install()
    ms = g0 if media_start is None else media_start
    a = max(0, min(round(ms * d["fps"]), len(d["top"]) - 1))
    b = min(len(d["top"]), max(a + 1, round((ms + g1 - g0) * d["fps"])))
    top, cx = _median(d["top"][a:b]), _median(d["cx"][a:b])
    k = d["k_tight"] if tight else d["k_wide"]
    head_at = d["head_at_tight"] if tight else d["head_at_wide"]
    x = max(round(1080 - 1080 * k), min(0, round(540 - k * cx)))
    y = round(head_at - k * top)
    tf = f"transform:translate({x}px,{y}px) scale({k});transform-origin:0px 0px"
    cid, t0, dur = s.id(name), s.L(g0), round(g1 - g0, 3)
    s.body.append(
        f'<div id="{cid}" class="pop-bg" style="z-index:2"><div class="bx-zoom" style="{tf}" data-layout-allow-overflow>'
        f'<video id="{cid}-v" class="clip bx-fillvid" src="{d["src"]}" data-start="{t0}" data-duration="{dur}" data-media-start="{ms}" '
        f'data-track-index="{s.next_track()}" muted playsinline></video></div></div>'
        f'<div id="{cid}-o" class="pop-head" style="z-index:3"><div class="bx-zoom" style="{tf}" data-layout-allow-overflow>'
        f'<video id="{cid}-c" class="clip pop-cut" style="top:{d["strip_top"]}px;height:{d["strip_h"]}px" src="{d["cut"]}" data-start="{t0}" '
        f'data-duration="{dur}" data-media-start="{ms}" data-track-index="{s.next_track()}" muted playsinline></video></div></div>')
    return cid
