#!/usr/bin/env python3
"""Render a seekable HTML/GSAP page to a 1080x1920 MP4.

The page must expose:
  window.DURATION   total seconds
  window.seek(t)    draws the exact state at time t (synchronous, deterministic)
  window.ready      a Promise that resolves when fonts and images are decoded
  window.HITS       optional list of seconds where a hit must land (used by review.py)

Usage:
  python3 render_motion.py reel.html OUT.mp4 [--audio track.mp3 --audio-start 0]
                           [--fps 30] [--workers 2] [--synth-hit 2.35] [--keep]
                           [--motion-blur 6 --blur-window 0.4 3.8] [--audio-raw]

--motion-blur N averages N sub-frames across a 180-degree shutter, which is real
motion blur rather than a CSS blur on the moving thing. Use it for anything fast
(page riffles, whip moves). It costs N times the frames, so limit it to the fast
stretch with --blur-window START END.
--audio-raw takes --audio as a finished mix: no fades, no lift.

Frames are shot at 360x640 with device_scale_factor 3, so every type size in the
Bare Reel spec applies unchanged. JPEG frames at q95: PNG encoding of a 1080x1920
frame is the slowest step and buys nothing once x264 has had its turn.
"""
import argparse, json, multiprocessing as mp, pathlib, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor

W, H, DSF = 360, 640, 3


def shoot(args):
    url, fdir, idxs, fps, nblur, win = args
    import io
    import numpy as np
    from PIL import Image
    from playwright.sync_api import sync_playwright
    clip = {"x": 0, "y": 0, "width": W, "height": H}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=DSF)
        pg.goto(url)
        pg.evaluate("window.ready")
        for i in idxs:
            t = i / fps
            out = f"{fdir}/{i:05d}.jpg"
            if nblur > 1 and win[0] <= t <= win[1]:
                acc = None
                for k in range(nblur):                       # 180-degree shutter
                    pg.evaluate(f"void window.seek({t + k * 0.5 / fps / nblur:.6f})")
                    im = np.asarray(Image.open(io.BytesIO(pg.screenshot(type="jpeg", quality=100, clip=clip))).convert("RGB"),
                                    dtype=np.float32)
                    acc = im if acc is None else acc + im
                Image.fromarray((acc / nblur).round().astype(np.uint8)).save(out, quality=95)
            else:
                pg.evaluate(f"void window.seek({t:.6f})")   # void: never ship a GSAP object back
                pg.screenshot(path=out, type="jpeg", quality=95, clip=clip)
        b.close()
    return len(idxs)


def meta(url):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.evaluate("window.ready")
        d = pg.evaluate("window.DURATION")
        hits = pg.evaluate("window.HITS || []")
        b.close()
    if errs:
        sys.exit("Page errors:\n" + "\n".join(errs))
    if not d:
        sys.exit("window.DURATION is missing or zero")
    return float(d), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html"); ap.add_argument("out")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--audio", help="music track (Suno export, Free Song Sunday, etc.)")
    ap.add_argument("--audio-start", type=float, default=0.0,
                    help="seconds into the track where the video starts")
    ap.add_argument("--lift", type=float, default=1.15,
                    help="volume lift; GS ambient masters run quiet")
    ap.add_argument("--synth-hit", type=float,
                    help="no track: synthesise a swell into a low hit at this second")
    ap.add_argument("--keep", action="store_true", help="keep the frame JPEGs")
    ap.add_argument("--motion-blur", type=int, default=1, help="sub-frames per frame (1 = off)")
    ap.add_argument("--blur-window", type=float, nargs=2, default=[0, 1e9], metavar=("START", "END"))
    ap.add_argument("--audio-raw", action="store_true", help="--audio is a finished mix")
    a = ap.parse_args()

    src = pathlib.Path(a.html).resolve()
    url = src.as_uri()
    fdir = src.parent / "frames"
    shutil.rmtree(fdir, ignore_errors=True); fdir.mkdir()

    dur, hits = meta(url)
    n = int(round(dur * a.fps))
    (src.parent / "hits.json").write_text(json.dumps({"fps": a.fps, "duration": dur, "hits": hits}))
    print(f"{n} frames, {dur:.2f}s, {len(hits)} hits, {a.workers} workers")

    t0 = time.time()
    w = max(1, a.workers)
    chunks = [list(range(k, n, w)) for k in range(w)]          # interleaved: even load
    # spawn, not fork: a forked child inherits the parent's Playwright loop and hangs
    with ProcessPoolExecutor(w, mp_context=mp.get_context("spawn")) as ex:
        list(ex.map(shoot, [(url, str(fdir), c, a.fps, a.motion_blur, a.blur_window) for c in chunks]))
    print(f"frames shot in {time.time() - t0:.0f}s")

    cmd = ["ffmpeg", "-nostdin", "-y", "-v", "error",
           "-framerate", str(a.fps), "-i", str(fdir / "%05d.jpg")]
    if a.audio:
        cmd += ["-ss", f"{a.audio_start:.3f}", "-i", a.audio]
        af = (f"atrim=0:{dur:.3f},asetpts=PTS-STARTPTS" if a.audio_raw else
              f"atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.8,"
              f"afade=t=out:st={max(dur - 2.2, 0):.3f}:d=2.2,volume={a.lift}")
    elif a.synth_hit is not None:
        h = a.synth_hit
        cmd += ["-f", "lavfi", "-i",
                f"aevalsrc='0.25*sin(2*PI*55*t)*min(t/{h},1)*exp(-max(t-{h},0)*0.9)"
                f"+0.5*sin(2*PI*41*t)*exp(-max(t-{h},0)*3)*gte(t,{h})"
                f"+0.2*(random(0)-0.5)*exp(-max(t-{h},0)*6)*gte(t,{h})':s=48000:d={dur:.3f}"]
        af = f"afade=t=out:st={max(dur - 0.8, 0):.3f}:d=0.8,loudnorm=I=-14:TP=-1"
    else:
        af = None
    if af:
        cmd += ["-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-level", "4.1", "-g", "60", "-movflags", "+faststart",
            "-t", f"{dur:.3f}", a.out]
    subprocess.run(cmd, check=True)
    if not a.keep:
        shutil.rmtree(fdir)
    print("wrote", a.out, f"({time.time() - t0:.0f}s total)")


if __name__ == "__main__":
    main()
