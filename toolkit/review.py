#!/usr/bin/env python3
"""Check a rendered reel before it goes to Gus. Look at every image this writes.

Usage: python3 review.py OUT.mp4 [--hits hits.json] [--every 0.25]

Writes next to the video:
  <name>_sheet.png   contact sheet, one frame every --every seconds, timestamped
  <name>_hits.png    for each hit: the frames at -2, -1, 0, +1, +2 around it.
                     The hit must read on its own frame (frame 0), not one late.
  prints             integrated loudness (LUFS) and true peak (dBTP)

hits.json is written by render_motion.py from window.HITS.
"""
import argparse, json, pathlib, re, subprocess


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--hits")
    ap.add_argument("--every", type=float, default=0.25)
    a = ap.parse_args()
    v = pathlib.Path(a.video)
    stem = v.with_suffix("")

    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "csv=p=0", str(v)]).stdout.strip())
    n = int(dur / a.every) + 1
    cols = 8
    rows = (n + cols - 1) // cols
    sheet = f"{stem}_sheet.png"
    run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(v), "-vf",
         f"fps=1/{a.every},scale=180:-1,"
         "drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,"
         f"tile={cols}x{rows}:padding=4:color=gray", "-frames:v", "1", sheet])
    print("contact sheet:", sheet)

    hits = []
    hp = pathlib.Path(a.hits) if a.hits else v.parent / "hits.json"
    if hp.exists():
        hj = json.loads(hp.read_text()); hits = hj.get("hits", []); fps = hj.get("fps", 30)
    if hits:
        strips = []
        for k, h in enumerate(hits):
            f0 = round(h * fps)
            sel = "+".join(f"eq(n\\,{f0 + d})" for d in (-2, -1, 0, 1, 2) if f0 + d >= 0)
            out = f"{stem}_hit{k:02d}.png"
            run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", str(v), "-vf",
                 f"select='{sel}',scale=160:-1,tile=5x1:padding=3:color=red",
                 "-frames:v", "1", "-vsync", "0", out])
            strips.append(out)
        if len(strips) > 1:
            inputs = sum([["-i", s] for s in strips], [])
            run(["ffmpeg", "-nostdin", "-y", "-v", "error", *inputs, "-filter_complex",
                 f"vstack=inputs={len(strips)}", f"{stem}_hits.png"])
            for s in strips: pathlib.Path(s).unlink()
        else:
            pathlib.Path(strips[0]).rename(f"{stem}_hits.png")
        print(f"hit strips: {stem}_hits.png  ({len(hits)} hits; middle frame of each row is the hit)")

    r = run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(v), "-af", "ebur128=peak=true",
             "-f", "null", "-"])
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    if I:
        print(f"loudness: {I[-1]} LUFS integrated, true peak {P[-1] if P else '?'} dBTP "
              "(TikTok normalises toward about -14; quieter than -18 sounds weak next to other posts)")
    else:
        print("loudness: no audio stream")
    print(f"duration: {dur:.2f}s")


if __name__ == "__main__":
    main()
