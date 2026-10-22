#!/usr/bin/env python3
"""Find the beat grid of a music track: tempo, beat times, bar starts (4/4).

Usage:
  python3 beat_grid.py track.mp3 [--bpm 96] [--start 0 --dur 60] [--click check.wav]

--bpm     Use the tempo from the Suno style stack when you have it; the script then
          only solves the phase. Detection is reliable on Suno output with a clear
          pulse and shaky on beatless ambient pads. If there is no pulse, say so and
          cut on phrase starts instead of pretending to a grid.
--click   Writes the track with a click on every beat (accent on bar starts) so the
          grid can be checked by ear before anything is cut to it.

Prints JSON: {"bpm", "beat_sec", "first_beat", "beats": [...], "bars": [...], "confidence"}
Numpy and ffmpeg only.
"""
import argparse, json, subprocess, sys
import numpy as np

SR, HOP, NFFT = 22050, 256, 2048
LAT = 0.078   # flux rises as an onset enters the window, ~78 ms before it; measured


def load(path, start, dur):
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(start)]
    if dur: cmd += ["-t", str(dur)]
    cmd += ["-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)


def flux(x, lo_hz=None, hi_hz=None):
    win = np.hanning(NFFT).astype(np.float32)
    n = 1 + (len(x) - NFFT) // HOP
    fr = np.lib.stride_tricks.as_strided(x, (n, NFFT), (x.strides[0] * HOP, x.strides[0]))
    S = np.log1p(100 * np.abs(np.fft.rfft(fr * win, axis=1)))
    f = np.fft.rfftfreq(NFFT, 1 / SR)
    m = np.ones_like(f, bool)
    if lo_hz: m &= f >= lo_hz
    if hi_hz: m &= f <= hi_hz
    d = np.maximum(np.diff(S[:, m], axis=0), 0).sum(1)
    d = np.concatenate([[0], d])
    d -= np.convolve(d, np.ones(16) / 16, "same")           # remove slow trend
    d = np.maximum(d, 0)
    return d / (d.max() + 1e-9)


def tempo(env, bpm_hint=None):
    fps = SR / HOP
    if bpm_hint:
        return bpm_hint, 1.0
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    bpms = np.arange(60, 181, 0.25)
    lags = fps * 60 / bpms
    score = np.interp(lags, np.arange(len(ac)), ac)
    # Gentle prior toward 110 BPM: halves and doubles both autocorrelate well
    score *= np.exp(-0.5 * (np.log2(bpms / 110) / 0.9) ** 2)
    i = int(np.argmax(score))
    conf = float(score[i] / (np.median(score) + 1e-9))
    return float(bpms[i]), conf


def phase(env, period):
    """Best offset (in frames, fractional) so env peaks sit on k*period + offset."""
    n = len(env); best, bo = -1, 0.0
    for off in np.arange(0, period, 0.25):
        idx = np.round(off + np.arange(0, n - off, period)).astype(int)
        idx = idx[idx < n]
        s = env[idx].sum() + 0.5 * (env[np.clip(idx - 1, 0, n - 1)].sum() + env[np.clip(idx + 1, 0, n - 1)].sum())
        if s > best: best, bo = s, off
    return bo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--dur", type=float, default=0)
    ap.add_argument("--click")
    a = ap.parse_args()

    x = load(a.track, a.start, a.dur)
    if len(x) < SR * 4:
        sys.exit("Need at least 4 seconds of audio")
    # Low band carries the pulse (kick); full band alone locks onto off-beat hats
    env = 0.7 * flux(x, hi_hz=150) + 0.3 * flux(x)
    bpm, conf = tempo(env, a.bpm)
    fps = SR / HOP
    if not a.bpm:
        # Autocorrelation lags are whole frames; refine tempo on the comb score itself
        cands = np.arange(bpm - 2, bpm + 2.001, 0.05)
        scores = []
        for c in cands:
            per = fps * 60 / c; o = phase(env, per)
            idx = np.round(o + np.arange(0, len(env) - o, per)).astype(int)
            scores.append(env[idx[idx < len(env)]].mean())
        bpm = float(cands[int(np.argmax(scores))])
    period = fps * 60 / bpm
    off = phase(env, period)
    total = len(x) / SR
    beats = [round(a.start + (off + k * period) / fps + LAT, 3)
             for k in range(int((len(env) - off) / period) + 1)]
    beats = [b for b in beats if b <= a.start + total]
    # Drop grid points before the music actually starts
    first_on = a.start + int(np.argmax(env > 0.2)) / fps + LAT
    beats = [b for b in beats if b >= first_on - 0.06]

    # Downbeat: which of the 4 beat positions carries the most low-end attack
    low = flux(x, hi_hz=150)
    bidx = [int(round((b - a.start - LAT) * fps)) for b in beats]
    sums = [sum(low[min(i, len(low) - 1)] for i in bidx[r::4]) / max(1, len(bidx[r::4])) for r in range(4)]
    r0 = int(np.argmax(sums))
    bars = beats[r0::4]

    out = {"bpm": round(bpm, 2), "beat_sec": round(60 / bpm, 4), "first_beat": beats[0],
           "beats": beats, "bars": bars,
           "confidence": "given" if a.bpm else ("good" if conf > 2.0 else "weak — check by ear")}
    print(json.dumps(out))

    if a.click:
        sr = 48000
        y = load(a.track, a.start, a.dur)
        y = np.interp(np.arange(int(len(y) * sr / SR)) * SR / sr, np.arange(len(y)), y) * 0.6
        t = np.arange(int(0.03 * sr)) / sr
        for b in beats:
            hz, amp = (1760, 0.6) if b in bars else (1100, 0.35)
            c = amp * np.sin(2 * np.pi * hz * t) * np.exp(-t * 120)
            i = int((b - a.start) * sr)
            if i + len(c) < len(y): y[i:i + len(c)] += c
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "f32le", "-ar", str(sr),
                        "-ac", "1", "-i", "-", a.click], input=y.astype(np.float32).tobytes(), check=True)
        print(f"click track: {a.click}", file=sys.stderr)


if __name__ == "__main__":
    main()
