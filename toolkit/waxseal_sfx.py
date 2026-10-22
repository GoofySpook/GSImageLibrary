"""Synthesise the Wax Seal sting soundtrack from the page's own event times.

Usage: python3 waxseal_sfx.py seal.html sfx.wav      (reads window.EVENTS from the page)
       python3 waxseal_sfx.py events.json sfx.wav    (or from a saved dump)

Page riffle, cover whoosh and thump, wax plop and hiss, a low swell as GS rises, and a boom
with a shimmer of bells on the hit. Loudness-normalised to -14 LUFS. Render the video with
--audio sfx.wav --audio-raw so the renderer does not fade or lift it again.
Every sound sits on a time the timeline exported, so retiming the page retimes the audio.
"""
import json, pathlib, subprocess, sys
import numpy as np

SR = 48000
src, out = sys.argv[1], sys.argv[2]
if src.endswith(".html"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto(pathlib.Path(src).resolve().as_uri()); pg.evaluate("window.ready")
        ev = json.loads(pg.evaluate("JSON.stringify({...EVENTS, dur: DURATION})")); b.close()
else:
    ev = json.load(open(src))
D = ev["dur"]; N = int(SR * D)
L = np.zeros(N); Rch = np.zeros(N)
rng = np.random.default_rng(7)


def band(n, lo, hi):
    x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)


def add(t0, sig, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[:N - i] * gain
    L[i:i + len(sig)] += sig * (1 - pan) ** .5 * 1.0
    Rch[i:i + len(sig)] += sig * (1 + pan) ** .5 * 1.0


def tone(n, f0, f1=None, decay=0.5, attack=0.002):
    t = np.arange(n) / SR
    f = f0 if f1 is None else f0 * (f1 / f0) ** (t / (n / SR))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, attack, decay)


# Low bed under everything, swelling into the seal
t = np.arange(N) / SR
hit, splat, close = ev["hit"], ev["splat"], ev["close"]
rise = splat + 0.95
bed = (0.5 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 82.4 * t + 1)) * 0.05
bed *= np.minimum(t / 1.2, 1) * (1 + 1.5 * np.clip((t - rise) / (hit - rise), 0, 1) * (t < hit + .1))
bed *= np.clip((D - t) / 1.2, 0, 1)
L += bed; Rch += bed

# Page riffle: a paper "fwip" per leaf at mid-flip and a soft slap on landing
for k, (s, d) in enumerate(ev["flips"]):
    speed = 0.6 / d
    n = int(SR * 0.16)
    fwip = band(n, 1200, 7000) * env(n, 0.012, 0.045)
    add(s + d * 0.45, fwip, 0.22 * min(1.0, 0.6 + 0.2 * speed), pan=0.35 - 0.7 * (k % 2))
    n2 = int(SR * 0.05)
    add(s + d, band(n2, 400, 3000) * env(n2, 0.001, 0.012), 0.12)

# Cover: heavy swing whoosh, then the thump
n = int(SR * 0.6)
add(close - 0.6, band(n, 150, 1200) * np.linspace(0, 1, n) ** 2 * env(n, 0.3, 0.4), 0.12)
n = int(SR * 0.9)
add(close, tone(n, 95, 45, decay=0.22) * 0.9 + band(n, 40, 400) * env(n, 0.002, 0.06) * 0.6, 0.55)

# Wax: plop, wet splash, hiss while hot
n = int(SR * 0.12)
add(splat, tone(n, 620, 170, decay=0.04), 0.35)
n = int(SR * 0.15)
add(splat, band(n, 700, 3500) * env(n, 0.002, 0.035), 0.2)
n = int(SR * 1.9)
add(splat + 0.05, band(n, 3500, 11000) * env(n, 0.08, 0.6), 0.05)

# GS rising: a low swell, then the hit with a shimmer of bells
n = int(SR * (hit - rise))
sw = band(n, 60, 600) * np.linspace(0, 1, n) ** 2.5
add(rise, sw, 0.18)
n = int(SR * 2.6)
boom = tone(n, 58, 38, decay=0.55) + 0.5 * tone(n, 41, 41, decay=0.9)
add(hit, boom, 0.6)
tt = np.arange(n) / SR
for i, (f, g) in enumerate([(880, .5), (1320, .35), (1760, .3), (2643, .2), (3520, .12)]):
    chime = np.sin(2 * np.pi * f * tt + 0.3 * np.sin(2 * np.pi * 5 * tt)) * env(n, 0.004, 0.7 - i * 0.08)
    add(hit + 0.01 * i, chime, 0.07 * g / .5, pan=(-.4, .4)[i % 2])

mix = np.stack([L, Rch], 1)
mix /= np.abs(mix).max() * 1.1
raw = out.replace(".wav", "_raw.wav")
subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "f64le", "-ar", str(SR), "-ac", "2",
                "-i", "-", raw], input=mix.astype(np.float64).tobytes(), check=True)
subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", raw,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", out], check=True)
print("wrote", out)
