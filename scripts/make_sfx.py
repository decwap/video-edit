"""video-edit sound palette v2 — 73 original, deterministic action sounds (synthesized: no samples, no third-party audio).

New timbres for the same jobs as the Paper Reel set (same file names, so every cue sheet keeps working):
  sparkle-1..3  tonal crystal grains (pentatonic, 4–9 kHz) over an airy bed — rising / falling / scattered
  ting-1..5     marimba-like bar (inharmonic partials 1 : 2.76 : 5.4) on an E-major pentatonic, so cuts form a melody
  click / key   wooden ticks and two-stage mechanical-keyboard keys; tap / ui-click / mouse-click glassy and crisp
  whoosh family band-pass air sweeps with flutter and stereo travel; risers end exactly on their peak
  tonal UI      blip, ding, notify, success (arpeggio), error, scan-beep; coins and a register for money moments
  textures      paper slide, card slaps (.ogg), marker scribbles, paper rip, stamp, crack, glitch, shutters
  cinematic     thud, bonk, bell, booms, sub drop, impact, rumble, bass pulse, drone, heartbeat, tension strings,
                dark piano, horror sting, suspense riser
Each sound is matched to a target duration, short-term loudness (loudest 100 ms) and peak, so existing cue volumes
(0.16–0.55) keep their balance under the voice. The voice reactions (voice-bruh / -huh / -fah) come from
make_voice_sfx.py (local TTS).

usage: python make_sfx.py [out_dir]      (default: ../assets/sfx next to this script's skill)
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal as sg

SR = 48000
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets" / "sfx"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2610)

# name: (duration s, loudest-100-ms RMS dBFS of the 0.707*(L+R) fold-down, old peak dBFS for reference)
TARGET = {
    "bass-impact": (2.3, -2.1, -1.0), "bass-pulse": (4.0, -9.5, -1.0), "bell-bong": (3.2, -9.4, -1.0), "blip": (0.35, -11.0, -3.0),
    "bonk": (0.55, -11.1, -1.0), "boom-dramatic": (2.3, -1.2, -1.0), "bubble-pop": (0.11, -12.9, -2.0), "camera-shutter": (0.28, -15.5, -3.0),
    "card-place-1": (0.689, -16.3, -1.0), "card-place-2": (0.457, -22.4, -1.0), "click-1": (0.09, -27.9, -5.0), "click-2": (0.09, -28.1, -5.0),
    "click-3": (0.09, -25.9, -5.0), "clock-ticking": (6.0, -23.2, -5.0), "coin": (0.7, -12.6, -4.0), "coins": (0.9, -14.8, -3.0),
    "crack": (0.6, -16.2, -1.0), "ding": (1.0, -8.9, -3.0), "drone-low": (8.0, -8.9, -2.0), "error": (0.3, -13.5, -5.0),
    "glint": (0.34, -18.8, -6.0), "glitch": (0.5, -14.9, -3.0), "heartbeat": (4.2, -7.2, -1.0), "impact-cinematic": (5.4, -6.3, -1.0),
    "kaching": (1.1, -11.5, -2.0), "key-0": (0.06, -23.9, -6.0), "key-1": (0.06, -25.0, -6.0), "key-2": (0.06, -23.3, -6.0),
    "key-3": (0.06, -24.0, -6.0), "key-4": (0.06, -24.7, -6.0), "key-5": (0.06, -26.3, -6.0), "marker": (0.45, -19.7, -7.0),
    "mouse-click": (0.13, -26.7, -4.0), "notify": (0.48, -13.0, -5.0), "paper-slide": (0.35, -21.4, -9.0), "piano-dark": (6.5, -9.9, -1.0),
    "pop-deep": (0.16, -13.9, -2.0), "pop-small": (0.09, -13.3, -2.0), "pop": (0.12, -13.8, -2.0), "popup": (0.22, -12.5, -4.0),
    "rip": (0.3, -18.3, -3.0), "riser-cinematic": (3.0, -11.9, -1.0), "riser-stop": (2.2, -13.1, -1.0), "riser-suspense": (4.0, -12.3, -2.0),
    "riser": (1.4, -14.9, -3.0), "rumble-sub": (5.0, -7.3, -1.0), "scan-beep": (0.18, -12.9, -9.0), "shutter": (0.16, -21.8, -5.0),
    "sparkle-1": (0.65, -19.2, -6.0), "sparkle-2": (0.55, -18.0, -6.0), "sparkle-3": (0.7, -19.0, -6.0), "stamp": (0.36, -13.6, -1.0),
    "sting-horror": (4.2, -9.1, -1.0), "strings-tension": (5.0, -13.3, -2.0), "sub-drop": (1.8, -1.3, -1.0), "success": (1.35, -10.4, -3.0),
    "swoosh-down": (0.5, -13.3, -1.0), "swoosh-short": (0.22, -14.0, -2.0), "swoosh-up": (0.7, -15.0, -1.0), "tap": (0.05, -24.3, -5.0),
    "thud": (0.5, -5.6, -1.0), "tick": (0.035, -23.5, -5.0), "ting-1": (0.9, -15.4, -4.0), "ting-2": (0.9, -15.3, -4.0),
    "ting-3": (0.9, -14.8, -4.0), "ting-4": (0.9, -15.0, -4.0), "ting-5": (0.9, -14.9, -4.0), "ui-click": (0.03, -20.2, -4.0),
    "whip": (0.26, -15.6, -3.0), "whoosh-quick": (0.26, -14.1, -1.0), "whoosh-reverse": (0.9, -12.7, -1.0), "whoosh": (0.42, -13.4, -1.0),
}


# ------------------------------------------------------------------ building blocks
def n_(d):
    return max(1, int(round(d * SR)))


def T(d):
    return np.arange(n_(d)) / SR


def noise(d):
    return rng.standard_normal(n_(d))


def env(d, a=0.002, tau=0.1, hold=0.0):
    """linear attack a, optional hold, exponential decay tau"""
    t = T(d)
    e = np.where(t < a, t / max(a, 1e-6), np.exp(-np.maximum(t - a - hold, 0) / tau))
    return e


def bp(x, lo, hi, order=2):
    return sg.sosfilt(sg.butter(order, [lo, min(hi, SR / 2 - 100)], btype="band", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sg.sosfilt(sg.butter(order, f, btype="high", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sg.sosfilt(sg.butter(order, min(f, SR / 2 - 100), btype="low", fs=SR, output="sos"), x)


def sweep(x, f0, f1, bw=0.9, blocks=120, curve=1.0):
    """time-varying band-pass (centre f0 -> f1, relative bandwidth bw), block-wise with carried state"""
    out = np.zeros_like(x)
    zi = None
    edges = np.linspace(0, len(x), blocks + 1).astype(int)
    for k in range(blocks):
        p = (k / max(1, blocks - 1)) ** curve
        fc = f0 * (f1 / f0) ** p
        lo, hi = fc / (1 + bw / 2), min(fc * (1 + bw / 2), SR / 2 - 200)
        sos = sg.butter(1, [lo, hi], btype="band", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        seg, zi = sg.sosfilt(sos, x[edges[k]:edges[k + 1]], zi=zi)
        out[edges[k]:edges[k + 1]] = seg
    return out


def partials(d, f0, ratios, amps, taus, a=0.002, detune=0.0):
    t = T(d)
    y = np.zeros_like(t)
    for r, am, tau in zip(ratios, amps, taus):
        f = f0 * r
        if f >= SR / 2 - 500:
            continue
        y += am * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
        if detune:
            y += 0.5 * am * np.sin(2 * np.pi * (f + detune) * t) * np.exp(-t / tau)
    att = np.clip(t / a, 0, 1)
    return y * att


def glide(d, f0, f1, tau=None, shape="sine", curve=1.0):
    t = T(d)
    p = (t / t[-1]) ** curve if len(t) > 1 else t
    f = f0 * (f1 / f0) ** p
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) if shape == "sine" else (2 * ((ph / (2 * np.pi)) % 1) - 1)
    return y * (np.exp(-t / tau) if tau else 1)


def click(width_ms=1.5, lo=2500, hi=12000, tau_ms=3.0):
    d = width_ms / 1000 + tau_ms * 6 / 1000
    return bp(noise(d), lo, hi) * env(d, 0.0003, tau_ms / 1000)


def mix(*parts):
    """sum mono parts of different lengths"""
    out = np.zeros(max(len(p) for p in parts))
    for p in parts:
        out[:len(p)] += p
    return out


def place(dst, src, t0, gain=1.0):
    i = int(round(t0 * SR))
    m = min(len(src), len(dst) - i)
    if m > 0:
        dst[i:i + m] += gain * src[:m]
    return dst


def fit(x, d):
    n = n_(d)
    y = np.zeros(n)
    y[:min(n, len(x))] = x[:n]
    k = min(int(0.006 * SR), n // 4)
    if k:
        y[-k:] *= np.linspace(1, 0, k)
    return y


def room(x, rt=0.6, mix=0.18, bright=6000):
    """small synthetic room: decaying filtered noise IR"""
    d = rt * 1.2
    ir = lp(noise(d), bright) * np.exp(-T(d) * 6.9 / rt)
    ir /= np.sqrt((ir ** 2).sum()) + 1e-9
    wet = sg.fftconvolve(x, ir)[:len(x)]
    return (1 - mix) * x + mix * wet * 3.0


def stereo(x, pan=0.0, width_ms=0.0, travel=None):
    """pan -1..1 (or travel=(p0,p1) moving across), Haas width in ms"""
    if travel:
        p = np.linspace(travel[0], travel[1], len(x))
    else:
        p = np.full(len(x), pan)
    ang = (p + 1) * np.pi / 4
    L, R = x * np.cos(ang), x * np.sin(ang)
    if width_ms:
        k = int(width_ms * SR / 1000)
        R = np.concatenate([np.zeros(k), R[:-k]]) if k else R
    return np.stack([L, R], axis=1) * np.sqrt(2)


def sat(x, drive=2.0):
    return np.tanh(drive * x) / np.tanh(drive)


# ------------------------------------------------------------------ the sounds
S = {}


def sparkle(seed_dir, d, n_grains, notes):
    t_end = d * 0.72
    y = np.zeros((n_(d), 2))
    for k in range(n_grains):
        p = k / max(1, n_grains - 1)
        t0 = (p ** 1.4) * t_end + rng.uniform(-0.01, 0.01)
        if seed_dir == "up":
            f = notes[min(len(notes) - 1, int(p * len(notes)))]
        elif seed_dir == "down":
            f = notes[max(0, len(notes) - 1 - int(p * len(notes)))]
        else:
            f = notes[rng.integers(len(notes))]
        g = partials(rng.uniform(0.06, 0.16), f * rng.uniform(0.997, 1.003), [1, 2.01], [1, 0.25],
                     [rng.uniform(0.025, 0.06), 0.015], a=0.0015)
        amp = 0.55 + 0.45 * (1 - p)
        st = stereo(g, pan=rng.uniform(-0.75, 0.75))
        i = int(max(0, t0) * SR)
        m = min(len(st), len(y) - i)
        if m > 0:
            y[i:i + m] += amp * st[:m]
    bed = hp(noise(d), 7500) * env(d, 0.025, 0.16) * 0.12
    y += stereo(bed, width_ms=0.4)
    return y


PENTA_HI = [4186.0, 4698.6, 5274.0, 6271.9, 7040.0, 8372.0, 9397.3]
S["sparkle-1"] = lambda: sparkle("up", 0.65, 26, PENTA_HI)
S["sparkle-2"] = lambda: sparkle("down", 0.55, 22, PENTA_HI)
S["sparkle-3"] = lambda: sparkle("scatter", 0.70, 30, PENTA_HI)


def bar(f0, d, tone=1.0):
    """marimba-like bar: inharmonic partials + soft mallet"""
    y = partials(d, f0, [1, 2.76, 5.40, 8.93], [1, 0.30 * tone, 0.10 * tone, 0.04 * tone], [0.38, 0.11, 0.045, 0.025],
                 a=0.0015, detune=1.3)
    m = bp(noise(0.012), 2500, 9000) * env(0.012, 0.0005, 0.003) * 0.35
    return place(y, m, 0.0)


for i, f in enumerate([1318.5, 1480.0, 1661.2, 1975.5, 2217.5], start=1):     # E F# G# B C# (E major pentatonic)
    S[f"ting-{i}"] = (lambda f=f: stereo(room(fit(bar(f, 0.9), 0.9), 0.5, 0.12), width_ms=0.5))

for i, fc in enumerate([3600, 4300, 5100], start=1):
    def _c(fc=fc):
        x = bp(noise(0.09), fc * 0.8, fc * 1.25, 2) * env(0.09, 0.0004, 0.006)
        x += 0.5 * hp(noise(0.09), 7000) * env(0.09, 0.0002, 0.0018)
        x += 0.25 * partials(0.09, fc * 0.62, [1], [1], [0.008])
        return stereo(fit(x, 0.09), width_ms=0.2)
    S[f"click-{i}"] = _c

for i in range(6):
    def _k(i=i):
        y = np.zeros(n_(0.06))
        down = bp(noise(0.03), 2200 + 300 * i, 7000) * env(0.03, 0.0003, 0.0035)
        thock = bp(noise(0.04), 380 + 60 * i, 900 + 80 * i) * env(0.04, 0.0006, 0.009) * 1.2
        place(y, down, 0.0)
        place(y, thock, 0.016 + 0.002 * (i % 3), 1.0)
        place(y, 0.4 * down[:400], 0.019 + 0.002 * (i % 3))
        return stereo(y, pan=(i - 2.5) * 0.08)
    S[f"key-{i}"] = _k

S["tap"] = lambda: stereo(fit(mix(partials(0.05, 2600, [1, 2.3], [1, 0.3], [0.008, 0.004]) * 0.8,
                                  0.9 * lp(noise(0.05), 400) * env(0.05, 0.0008, 0.012),
                                  0.4 * click(1, 3000, 9000, 1.2)), 0.05))
S["ui-click"] = lambda: stereo(fit(mix(click(1, 5000, 11000, 1.2), 0.6 * partials(0.03, 3200, [1], [1], [0.006])), 0.03))


def _mouse():
    y = np.zeros(n_(0.13))
    place(y, mix(click(1, 2500, 8000, 2.5), 0.5 * partials(0.02, 2100, [1], [1], [0.004])), 0.0)
    place(y, 0.6 * mix(click(1, 3500, 10000, 2.0), 0.4 * partials(0.02, 2700, [1], [1], [0.003])), 0.078)
    return stereo(y)


S["mouse-click"] = _mouse
S["tick"] = lambda: stereo(fit(mix(partials(0.035, 2800, [1, 2.18], [1, 0.45], [0.007, 0.004]), 0.3 * click(0.8, 3000, 9000, 1.5)), 0.035))


def _clock():
    y = np.zeros(n_(6.0))
    for k in range(12):
        f = 2650 if k % 2 == 0 else 2250
        tk = mix(partials(0.05, f, [1, 2.18, 3.6], [1, 0.4, 0.15], [0.008, 0.005, 0.003]), 0.3 * click(0.8, 2500, 8000, 1.5))
        place(y, tk, 0.05 + 0.5 * k, 1.0 if k % 2 == 0 else 0.8)
    return stereo(room(y, 0.35, 0.15))


S["clock-ticking"] = _clock


def _blip():
    d = 0.35
    t = T(d)
    f = np.where(t < 0.055, 1046.5 * (1568 / 1046.5) ** (t / 0.055), 1568.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(ph) + 0.18 * np.sin(2 * ph)) * env(d, 0.006, 0.075)
    return stereo(y, width_ms=0.3)


S["blip"] = _blip
S["ding"] = lambda: stereo(room(fit(partials(1.0, 1760, [1, 2.0, 2.76, 4.07, 5.2], [1, 0.35, 0.22, 0.09, 0.04],
                                             [0.42, 0.28, 0.14, 0.07, 0.04], a=0.001, detune=0.9), 1.0), 0.8, 0.16), width_ms=0.6)


def _success():
    y = np.zeros(n_(1.35))
    for k, (f, t0) in enumerate([(1046.5, 0.0), (1318.5, 0.085), (1568.0, 0.17), (2093.0, 0.29)]):
        place(y, bar(f, 1.0 if k == 3 else 0.6, tone=0.8), t0, 0.8 if k < 3 else 1.0)
    st = stereo(room(y, 0.9, 0.18), width_ms=0.6)
    sp = sparkle("up", 0.5, 10, PENTA_HI[2:]) * 0.35
    i = int(0.3 * SR)
    st[i:i + len(sp)] += sp[:len(st) - i]
    return st


S["success"] = _success


def _notify():
    y = np.zeros(n_(0.48))
    for f, t0, g in [(1568.0, 0.0, 0.85), (2349.3, 0.105, 1.0)]:
        x = partials(0.37, f, [1, 2, 3], [1, 0.25, 0.08], [0.11, 0.06, 0.03], a=0.004)
        place(y, x, t0, g)
    return stereo(room(y, 0.5, 0.12), width_ms=0.4)


S["notify"] = _notify


def _glint():
    d = 0.34
    x = sweep(noise(d), 8500, 15500, bw=0.6, curve=0.8) * env(d, 0.03, 0.08)
    x += 0.35 * partials(d, 7900, [1], [1], [0.04]) * (T(d) > 0.05)
    return stereo(fit(x, d), travel=(-0.4, 0.5))


S["glint"] = _glint


def pop_(d, f0, f1, tau, click_g=0.2):
    x = mix(glide(d, f0, f1, tau=tau, curve=0.5), click_g * click(0.6, 2000, 7000, 1.0))
    return stereo(fit(x, d))


S["pop"] = lambda: pop_(0.12, 560, 170, 0.03)
S["pop-small"] = lambda: pop_(0.09, 980, 430, 0.018)
S["pop-deep"] = lambda: pop_(0.16, 270, 85, 0.05, 0.1)
S["bubble-pop"] = lambda: stereo(fit(glide(0.11, 320, 1150, tau=0.03, curve=0.6) * np.clip(T(0.11) / 0.004, 0, 1), 0.11))


def _popup():
    y = np.zeros(n_(0.22))
    place(y, glide(0.12, 480, 1320, tau=0.05, curve=0.7), 0.0)
    place(y, 0.5 * partials(0.1, 3135, [1, 2.01], [1, 0.2], [0.03, 0.01]), 0.09)
    return stereo(y, width_ms=0.3)


S["popup"] = _popup


def air(d, f0, f1, peak_at=0.6, curve=1.0, bw=0.9, flutter=0.15, travel=(-0.6, 0.6)):
    t = T(d)
    p = t / d
    e = np.where(p < peak_at, (p / peak_at) ** 1.6, ((1 - p) / (1 - peak_at)) ** 1.3)
    x = sweep(noise(d), f0, f1, bw=bw, curve=curve) * e
    x *= 1 + flutter * np.sin(2 * np.pi * 27 * t)
    return stereo(fit(x, d), travel=travel)


S["whoosh"] = lambda: air(0.42, 420, 5600, 0.58)
S["whoosh-quick"] = lambda: air(0.26, 850, 7200, 0.5, travel=(0.6, -0.6))
S["swoosh-up"] = lambda: air(0.7, 300, 8200, 0.85, curve=1.3, travel=(-0.3, 0.3))
S["swoosh-down"] = lambda: air(0.5, 7200, 380, 0.3, curve=0.7, travel=(0.3, -0.3))
S["swoosh-short"] = lambda: air(0.22, 1600, 6400, 0.45, flutter=0.08)


def _wrev():
    x = air(0.9, 6200, 700, 0.12, curve=0.6, flutter=0.1, travel=(0.5, -0.5))
    return x[::-1].copy()


S["whoosh-reverse"] = _wrev


def _whip():
    st = air(0.26, 600, 9500, 0.42, curve=0.7, flutter=0.05, travel=(-0.7, 0.7))
    c = stereo(click(0.8, 3000, 14000, 2.0) * 0.9, pan=0.6)
    i = int(0.11 * SR)
    st[i:i + len(c)] += c[:len(st) - i]
    return st


S["whip"] = _whip


def riser_(d, stop=False, cinematic=False):
    t = T(d)
    p = t / d
    e = p ** 2.2
    x = sweep(noise(d), 280, 9800, bw=0.8, curve=1.6) * e * 0.9
    tone = glide(d, 110 if cinematic else 220, 440 if cinematic else 880, curve=1.5, shape="saw") * e * 0.22
    tone += glide(d, 110.6 if cinematic else 221, 442 if cinematic else 884, curve=1.5, shape="saw") * e * 0.2
    y = x + lp(tone, 5000)
    if cinematic:
        y += 0.5 * sweep(noise(d), 1200, 14000, bw=0.4, curve=2.0) * e ** 1.5
    k = int((0.004 if stop else 0.03) * SR)
    y[-k:] *= np.linspace(1, 0, k)
    return stereo(y, width_ms=0.6)


S["riser"] = lambda: riser_(1.4)
S["riser-stop"] = lambda: riser_(2.2, stop=True)
S["riser-cinematic"] = lambda: riser_(3.0, cinematic=True)


def _paper(d=0.35):
    t = T(d)
    grain = np.abs(lp(noise(d), 140)) * 2.5
    x = bp(noise(d), 1500, 7500) * (0.4 + grain) * env(d, 0.03, 0.12)
    return stereo(fit(x, d), travel=(-0.3, 0.35))


S["paper-slide"] = _paper


def card(d, bright=1.0):
    y = np.zeros(n_(d))
    place(y, bp(noise(0.02), 900 * bright, 6500) * env(0.02, 0.0004, 0.005) * 1.4, 0.0)
    place(y, partials(0.12, 205 * bright, [1, 2.3], [1, 0.3], [0.035, 0.015]) * 0.8, 0.0)
    rust = bp(noise(d), 2000, 8000) * np.abs(lp(noise(d), 90)) * 2.0 * env(d, 0.01, d * 0.25)
    place(y, 0.35 * rust, 0.01)
    return stereo(room(fit(y, d), 0.4, 0.12), width_ms=0.3)


S["card-place-1"] = lambda: card(0.689, 1.0)
S["card-place-2"] = lambda: card(0.457, 1.35)


def _marker():
    d = 0.45
    y = np.zeros(n_(d))
    for t0, dd in [(0.0, 0.17), (0.21, 0.2)]:
        t = T(dd)
        s = bp(noise(dd), 2600, 6800) * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * t) ** 2) * env(dd, 0.01, dd * 0.6, hold=dd * 0.3)
        s += 0.12 * glide(dd, 3000, 3350) * env(dd, 0.01, dd * 0.4)
        place(y, s, t0)
    return stereo(y, travel=(-0.2, 0.25))


S["marker"] = _marker


def _shutter():
    y = np.zeros(n_(0.16))
    place(y, click(1, 3000, 10000, 2.5), 0.0)
    place(y, 0.7 * click(1, 1800, 7000, 3.5), 0.055)
    place(y, 0.25 * partials(0.08, 1900, [1, 2.7], [1, 0.3], [0.015, 0.008]), 0.058)
    return stereo(y)


S["shutter"] = _shutter


def _camera():
    y = np.zeros(n_(0.28))
    place(y, 0.35 * bp(noise(0.08), 900, 3200) * env(0.08, 0.02, 0.04), 0.0)
    for t0, g in [(0.06, 1.0), (0.11, 0.7), (0.19, 0.85)]:
        place(y, g * click(1, 2200, 11000, 3.0), t0)
    place(y, 0.3 * partials(0.08, 2400, [1, 2.6], [1, 0.3], [0.02, 0.01]), 0.195)
    return stereo(y, width_ms=0.3)


S["camera-shutter"] = _camera


def coin_(f0, d=0.7):
    return partials(d, f0, [1, 1.58, 2.25, 2.84], [1, 0.7, 0.45, 0.3], [0.22, 0.16, 0.1, 0.07], a=0.0006)


def _coin():
    y = np.zeros(n_(0.7))
    place(y, coin_(2650), 0.0)
    place(y, 0.45 * coin_(2655, 0.5), 0.13)
    place(y, 0.2 * coin_(2660, 0.4), 0.21)
    return stereo(room(y, 0.5, 0.12), width_ms=0.4)


S["coin"] = _coin


def _coins():
    y = np.zeros((n_(0.9), 2))
    for k in range(8):
        f = 2650 * rng.uniform(0.85, 1.2)
        c = stereo(coin_(f, 0.45) * (0.9 - 0.08 * k), pan=rng.uniform(-0.6, 0.6))
        i = int((0.02 + 0.07 * k + rng.uniform(0, 0.03)) * SR)
        m = min(len(c), len(y) - i)
        y[i:i + m] += c[:m]
    return y


S["coins"] = _coins


def _kaching():
    y = np.zeros(n_(1.1))
    place(y, 0.5 * bp(noise(0.14), 700, 3000) * env(0.14, 0.02, 0.05), 0.0)
    place(y, partials(0.9, 2637, [1, 2.0, 2.76], [1, 0.4, 0.2], [0.35, 0.2, 0.1]), 0.12)
    place(y, 0.8 * partials(0.9, 3951, [1, 2.0], [1, 0.3], [0.3, 0.15]), 0.16)
    st = stereo(room(y, 0.7, 0.15), width_ms=0.5)
    jing = _coins()[: n_(0.6)] * 0.4
    i = int(0.18 * SR)
    st[i:i + len(jing)] += jing[:len(st) - i]
    return st


S["kaching"] = _kaching


def _stamp():
    y = np.zeros(n_(0.36))
    place(y, partials(0.3, 135, [1, 2.4], [1, 0.25], [0.045, 0.02]) + lp(noise(0.3), 800) * env(0.3, 0.001, 0.03), 0.0)
    place(y, 0.7 * bp(noise(0.03), 1000, 5200) * env(0.03, 0.0005, 0.006), 0.005)
    return stereo(room(y, 0.35, 0.1))


S["stamp"] = _stamp


def _error():
    y = np.zeros(n_(0.3))
    for f, t0 in [(523.3, 0.0), (392.0, 0.13)]:
        x = glide(0.15, f, f, shape="saw")
        x = lp(x, 1600) * env(0.15, 0.008, 0.06)
        place(y, x, t0)
    return stereo(y, width_ms=0.3)


S["error"] = _error


def _glitch():
    d = 0.5
    y = np.zeros(n_(d))
    t = 0.0
    while t < d - 0.02:
        L = rng.uniform(0.012, 0.045)
        if rng.uniform() < 0.72:
            kind = rng.integers(3)
            if kind == 0:
                seg = hp(noise(L), 1500) * 0.6
            elif kind == 1:
                seg = np.sign(np.sin(2 * np.pi * rng.choice([330, 660, 1320]) * T(L))) * 0.35
            else:
                seg = np.repeat(rng.uniform(-0.8, 0.8, max(1, int(L * 900))), int(SR / 900))[: n_(L)]
            place(y, seg * np.clip(T(len(seg) / SR) / 0.002, 0, 1), t)
        t += L
    return stereo(y, width_ms=0.8)


S["glitch"] = _glitch


def _crack():
    d = 0.6
    y = np.zeros(n_(d))
    place(y, hp(noise(0.004), 800) * 2.0, 0.0)
    place(y, partials(0.3, 115, [1, 2.2], [1, 0.3], [0.06, 0.02]) * 0.8, 0.0)
    for k in range(40):
        t0 = 0.01 + rng.exponential(0.09)
        if t0 < d - 0.02:
            place(y, bp(noise(0.006), 2000, 9000) * env(0.006, 0.0002, 0.0015) * rng.uniform(0.2, 0.9) * np.exp(-t0 / 0.12), t0)
    return stereo(room(y, 0.4, 0.1), width_ms=0.6)


S["crack"] = _crack


def _rip():
    d = 0.3
    t = T(d)
    am = np.abs(np.sin(2 * np.pi * (60 + 140 * t / d) * t)) ** 3
    x = hp(noise(d), 1800) * (0.3 + 0.7 * am) * env(d, 0.01, 0.12, hold=0.08)
    return stereo(fit(x, d), travel=(-0.5, 0.5))


S["rip"] = _rip


def _scan():
    y = np.zeros(n_(0.18))
    for t0 in (0.0, 0.085):
        b = glide(0.07, 2960, 2960, shape="saw")
        b = lp(b, 7000) * env(0.07, 0.002, 0.03, hold=0.03)
        place(y, b, t0)
    return stereo(y)


S["scan-beep"] = _scan
S["thud"] = lambda: stereo(fit(mix(glide(0.5, 88, 42, tau=0.12, curve=0.5), lp(noise(0.5), 300) * env(0.5, 0.001, 0.025) * 0.6,
                                   0.2 * click(0.8, 1500, 5000, 1.5)), 0.5))


def _bonk():
    d = 0.55
    t = T(d)
    f = 820 * (430 / 820) ** np.clip(t / 0.08, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.012 * np.sin(2 * np.pi * 9 * t))) / SR
    x = (np.sin(ph) + 0.35 * np.sin(2.6 * ph)) * np.exp(-t / 0.11)
    place(x, 0.4 * click(0.8, 1500, 6000, 1.5), 0.0)
    return stereo(room(fit(x, d), 0.4, 0.12))


S["bonk"] = _bonk


def _bell_bong():
    d = 3.2
    f0 = 392.0
    y = partials(d, f0, [0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 2.662, 3.011, 4.17],
                 [0.6, 1.0, 0.55, 0.4, 0.35, 0.22, 0.18, 0.12, 0.06], [2.2, 1.6, 1.2, 0.9, 0.7, 0.5, 0.45, 0.35, 0.2], a=0.002, detune=0.7)
    y = place(y, 0.3 * bp(noise(0.01), 1500, 8000), 0.0)
    return stereo(room(y, 1.6, 0.22), width_ms=0.7)


S["bell-bong"] = _bell_bong


def boom(d, f0, f1, tau, drive=2.5, noise_g=0.5, rt=1.4):
    t = T(d)
    x = glide(d, f0, f1, tau=tau, curve=0.4)
    x += noise_g * lp(noise(d), 1400) * env(d, 0.001, 0.06)
    x = sat(x, drive)
    return stereo(room(fit(x, d), rt, 0.2, 3000), width_ms=0.5)


S["boom-dramatic"] = lambda: boom(2.3, 62, 36, 0.9, 3.0, 0.6, 1.6)
S["bass-impact"] = lambda: boom(2.3, 95, 40, 0.5, 2.2, 0.7, 1.2)
S["sub-drop"] = lambda: stereo(fit(sat(glide(1.8, 120, 30, curve=0.7) * env(1.8, 0.01, 0.9, hold=0.4), 1.6), 1.8))


def _impact():
    d = 5.4
    st = boom(d, 70, 32, 1.4, 2.6, 0.8, 2.6)
    metal = partials(3.0, 310, [1, 1.47, 2.09, 2.95, 3.88, 5.1], [1, 0.8, 0.6, 0.45, 0.3, 0.2], [1.6, 1.3, 1.0, 0.8, 0.6, 0.4], a=0.001)
    st[: len(metal)] += stereo(room(metal, 2.4, 0.3, 5000), width_ms=1.0) * 0.35
    return st


S["impact-cinematic"] = _impact


def bed(d, x, fade_in=0.8, fade_out=1.2):
    t = T(d)
    e = np.clip(t / fade_in, 0, 1) * np.clip((d - t) / fade_out, 0, 1)
    return x * e


def _rumble():
    d = 5.0
    t = T(d)
    x = lp(noise(d), 110, 4) * 2.5 + 0.6 * np.sin(2 * np.pi * 38 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.6 * t))
    return stereo(bed(d, x, 1.0, 1.4), width_ms=1.2)


S["rumble-sub"] = _rumble


def _bass_pulse():
    d = 4.0
    y = np.zeros(n_(d))
    for k in range(8):
        p = glide(0.45, 58, 52, tau=0.16) * np.clip(T(0.45) / 0.012, 0, 1)
        place(y, sat(p, 1.8), 0.02 + 0.5 * k, 0.8 + 0.2 * (k % 2 == 0))
    return stereo(bed(d, y, 0.2, 0.4), width_ms=0.5)


S["bass-pulse"] = _bass_pulse


def _drone():
    d = 8.0
    t = T(d)
    x = sum(glide(d, f, f, shape="saw") for f in (55.0, 55.35, 82.4, 110.3)) * 0.25
    lfo = 260 + 160 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t))
    out = np.zeros_like(x)
    blocks = 160
    edges = np.linspace(0, len(x), blocks + 1).astype(int)
    zi = None
    for k in range(blocks):
        sos = sg.butter(2, lfo[edges[k]], btype="low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        out[edges[k]:edges[k + 1]], zi = sg.sosfilt(sos, x[edges[k]:edges[k + 1]], zi=zi)
    return stereo(bed(d, out, 1.2, 1.8), width_ms=1.5)


S["drone-low"] = _drone


def _heartbeat():
    d = 4.2
    y = np.zeros(n_(d))
    for k in range(5):
        t0 = 0.1 + 0.83 * k
        for dt, g, f in [(0.0, 1.0, 62), (0.19, 0.7, 54)]:
            th = glide(0.22, f, f * 0.8, tau=0.055) + 0.3 * lp(noise(0.22), 200) * env(0.22, 0.002, 0.03)
            place(y, th * np.clip(T(0.22) / 0.006, 0, 1), t0 + dt, g)
    return stereo(sat(y, 1.4), width_ms=0.4)


S["heartbeat"] = _heartbeat


def _strings():
    d = 5.0
    t = T(d)
    x = np.zeros_like(t)
    for f in (220.0, 233.1, 329.6, 349.2):
        for det in (-0.4, 0.4):
            x += glide(d, f + det, f + det, shape="saw")
    x = bp(x, 180, 3200) * 0.12
    trem = 0.65 + 0.35 * np.sin(2 * np.pi * 11.5 * t)
    cres = (t / d) ** 1.6 * 0.85 + 0.15
    return stereo(room(bed(d, x * trem * cres, 0.3, 0.6), 1.2, 0.2), width_ms=1.4)


S["strings-tension"] = _strings


def piano_note(f, d, g=1.0):
    B = 0.00035
    ks = np.arange(1, 13)
    ratios = ks * np.sqrt(1 + B * ks ** 2)
    amps = 1 / ks ** 1.1
    taus = 2.8 / (1 + 0.35 * (ks - 1))
    y = partials(d, f, ratios, amps, taus, a=0.003, detune=0.25)
    y = place(y, 0.15 * bp(noise(0.03), 400, 3000) * env(0.03, 0.001, 0.008), 0.0)
    return g * y


def _piano():
    d = 6.5
    y = np.zeros(n_(d))
    for f, g in [(73.42, 1.0), (110.0, 0.7), (146.83, 0.55), (174.61, 0.5)]:          # D minor, low
        place(y, piano_note(f, d, g), 0.0)
    place(y, piano_note(69.3, 4.8, 0.6), 1.7)                                          # a low C# leaning in
    return stereo(room(y, 2.2, 0.25, 4000), width_ms=1.0)


S["piano-dark"] = _piano


def _sting():
    d = 4.2
    t = T(d)
    swell = np.zeros_like(t)
    for f in (440.0, 466.2, 622.3, 659.3):
        swell += glide(d, f, f * 1.02, shape="saw")
    swell = bp(swell, 300, 5000) * 0.1 * np.clip(t / 1.4, 0, 1) ** 2 * np.exp(-np.maximum(t - 1.5, 0) / 1.2)
    screech = sum(glide(d, f, f * 1.06, shape="saw") for f in (1760.0, 1864.7)) * 0.05
    screech = hp(screech, 1200) * (t > 1.45) * np.exp(-np.maximum(t - 1.45, 0) / 0.9)
    y = swell + screech
    hit = sat(glide(2.0, 70, 35, tau=0.6), 2.5) * 0.9
    y = place(y, hit, 1.45)
    return stereo(room(y, 1.8, 0.25, 5000), width_ms=1.2)


S["sting-horror"] = _sting


def _suspense():
    d = 4.0
    t = T(d)
    x = np.zeros_like(t)
    for f in (110.0, 116.5, 164.8):
        x += glide(d, f, f * 1.5, curve=1.4, shape="saw")
    x = lp(x, 2400) * 0.15 * (0.6 + 0.4 * np.sin(2 * np.pi * (4 + 8 * t / d) * t))
    x *= (t / d) ** 1.8
    x += 0.5 * sweep(noise(d), 200, 6000, bw=0.7, curve=1.8) * (t / d) ** 2.5
    k = int(0.02 * SR)
    x[-k:] *= np.linspace(1, 0, k)
    return stereo(x, width_ms=1.0)


S["riser-suspense"] = _suspense


# ------------------------------------------------------------------ level matching + writing
def loud(x):
    m = (x[:, 0] + x[:, 1]) * 0.70710678 if x.ndim == 2 else x       # same fold-down as ffmpeg -ac 1 (the targets' unit)
    win = int(0.1 * SR)
    if len(m) <= win:
        return 10 * np.log10((m ** 2).mean() + 1e-12)
    c = np.convolve(m ** 2, np.ones(win) / win, mode="valid")
    return 10 * np.log10(c.max() + 1e-12)


def finish(name, x):
    d, target, peak_db = TARGET[name]
    if x.ndim == 1:
        x = stereo(x)
    n = n_(d)
    y = np.zeros((n, 2))
    y[:min(n, len(x))] = x[:n]
    k = min(int(0.005 * SR), n // 4)
    y[-k:] *= np.linspace(1, 0, k)[:, None]
    P = 10 ** (-1.0 / 20)                         # per-channel ceiling -1 dBFS (the table's peaks are folded-mono)
    for _ in range(6):                            # gain to the target loudness, soft-limit, repeat until it settles
        y *= 10 ** ((target - loud(y)) / 20)
        if np.abs(y).max() > P:
            y = P * np.tanh(y / P)
    return y


def write(name, y, ext="wav"):
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    path = OUT / f"{name}.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    if ext == "ogg":
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-c:a", "libvorbis", "-q:a", "6", str(OUT / f"{name}.ogg")],
                       check=True)
        path.unlink()


if __name__ == "__main__":
    for name in sorted(S):
        y = finish(name, S[name]())
        write(name, y, "ogg" if name.startswith("card-place") else "wav")
    with wave.open(str(OUT / "silence-0.5s.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.zeros((int(0.5 * SR), 2), np.int16).tobytes())
    missing = sorted(set(TARGET) - set(S))
    print(f"wrote {len(S) + 1} sounds to {OUT}" + (f"  (missing: {missing})" if missing else ""))
