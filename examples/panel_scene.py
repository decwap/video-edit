"""The smallest reel with the pop-out face panel: copy this shape into build/scenes.py. Times are global seconds on the cut voice.

Before running it:  python <SK>/scripts/make_panel.py --src assets/aroll_wide.mp4
Run from the project folder:  VIDEO_EDIT_SCRIPTS=<SK>/scripts python build/scenes.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.environ["VIDEO_EDIT_SCRIPTS"])
from video_kit import *  # noqa: F401,F403,E402

PROJECT = Path(__file__).resolve().parent.parent
use_panel(PROJECT / "build/panel.json")             # from here on the stage sits lower and panel() works

reel = Reel(total=13.5, fps=25, voice_dur=12.0)     # the voice, then the end card holds silent
T = reel.ting


def C(t, name, vol=0.4):
    reel.cue(t, name, vol)


s = reel.scene("s01", "hook", 0.00, 12.00)
s.paper("bg", 0.00, 12.00, leaf_op=0.3)             # the stage: one sheet of paper for the whole scene

# One panel beat per stretch of footage, cut at every join make_panel.py reported. Nothing animates in: the first frame is
# already the panel and the stage, and only the stage changes after that.
panel(s, "f0", 0.00, 5.40)
panel(s, "f1", 5.40, 6.70, tight=True)              # the framing change that hides a jump cut
panel(s, "f2", 6.70, 12.00)

# A graphic on the stage, with its caption in a layer above it. Captions are one to three words and swap by hard cut.
fr = framed(s, "a", 0.00, 5.40, "clip-one", 60, 100, 960, 690, z=4)
lay(s, "at", 0.00, 5.40, 6, chip_c("s01-h", "Your hero line", 680, 88, "hero")
    + s.seam_caps([("one to three", 0.10, 1.40), ("words at a time", 1.40, 3.00), ("above the head", 3.00, 5.40)]))
C(0.10, "sparkle-1")

framed(s, "b", 5.40, 12.00, "clip-two", 60, 100, 960, 690, z=4)
lay(s, "bt", 5.40, 12.00, 6, s.seam_caps([("the panel stays", 5.46, 8.00), ("the stage changes", 8.00, 12.00)]))
T(5.40)

s = reel.scene("s02", "end", 12.00, 13.50)
end = srow("s02-e0", "build your own", 130, 124, "grey") + srow("s02-e1", "thing", 240, 320)
card(s, "a", 12.00, 13.50, end, z=1, enter="none", leaf=0.3)
panel(s, "f", 12.00, 13.50, media_start=11.90)      # a pause in the footage, so the speaker holds still over the silent end card

print(finish(reel, PROJECT))
