"""video-edit voice reactions v2 — made with the local Kokoro TTS (HyperFrames), then shaped with ffmpeg.

Original TTS performances of everyday reaction words; they fill the same comedic slot as popular meme clips without
copying any recording. New voices and shaping for video-edit (the Paper Reel set used other voices).
Writes voice-bruh / voice-huh / voice-fah to assets/sfx/ (or the folder given).

usage: python make_voice_sfx.py [out_dir]
Needs the HyperFrames CLI (npx); on first use it downloads the Kokoro model. If the TTS step fails, set
HYPERFRAMES_PYTHON to a Python that has kokoro-onnx + soundfile installed.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets" / "sfx"
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path(tempfile.mkdtemp())
NPX = shutil.which("npx") or "npx"

# name, text, voice, speed, ffmpeg shaping
LINES = [
    ("voice-bruh", "Bruuh.", "am_michael", 0.78, "asetrate=24000*0.8,aresample=48000,atempo=1.1"),           # low, flat, unimpressed
    ("voice-huh", "Huh?", "bm_george", 1.0, "asetrate=24000*1.1,aresample=48000"),                          # rising, confused
    ("voice-fah", "Faaah!", "am_adam", 0.72, "asetrate=24000*0.88,aresample=48000,aecho=0.8:0.5:45:0.3"),  # exasperated cry
]

env = dict(os.environ)
venv = Path.home() / ".cache" / "hfsep" / "Scripts" / "python.exe"
if "HYPERFRAMES_PYTHON" not in env and venv.exists():
    env["HYPERFRAMES_PYTHON"] = str(venv)

for name, text, voice, speed, shape in LINES:
    raw = TMP / f"{name}.wav"
    r = subprocess.run([NPX, "--yes", "hyperframes@0.8.106", "tts", text, "-v", voice, "-s", str(speed), "-o", str(raw)],
                       capture_output=True, text=True, env=env)
    if r.returncode or not raw.exists():
        sys.exit(f"tts failed for {name}: {r.stdout[-400:]} {r.stderr[-400:]}")
    chain = (f"{shape},silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
             "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
             "acompressor=threshold=-18dB:ratio=3:attack=3:release=80,loudnorm=I=-16:TP=-2,aresample=48000")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", chain, "-ac", "2", "-c:a", "pcm_s16le",
                    str(OUT / f"{name}.wav")], check=True)
    print("wrote", OUT / f"{name}.wav")
