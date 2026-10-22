#!/usr/bin/env bash
# Re-render the Wax Seal sting from this folder. Needs ffmpeg, python3, numpy, playwright.
# About 6 minutes on two workers; the riffle (0.4-4.45 s) is rendered with 6-sub-frame motion blur.
set -euo pipefail
cd "$(dirname "$0")"
T=../../toolkit
python3 $T/waxseal_sfx.py seal.html sfx.wav          # sound, timed to the page's own EVENTS
python3 $T/render_motion.py seal.html GS_Grimoire_Sting_WaxSeal_1080x1920.mp4 \
        --audio sfx.wav --audio-raw --motion-blur 6 --blur-window 0.4 4.45 --workers 2
python3 $T/review.py GS_Grimoire_Sting_WaxSeal_1080x1920.mp4 --every 0.5
rm -f sfx.wav sfx_raw.wav hits.json
