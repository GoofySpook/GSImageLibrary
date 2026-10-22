#!/usr/bin/env bash
# Re-render the Gold Rune sting. About 30 seconds. The boom is synthesised by ffmpeg at the HIT time.
set -euo pipefail
cd "$(dirname "$0")"
T=../../toolkit
python3 $T/render_motion.py sting.html GS_Grimoire_Sting_GoldRune_1080x1920.mp4 --synth-hit 2.35 --workers 2
python3 $T/review.py GS_Grimoire_Sting_GoldRune_1080x1920.mp4
rm -f hits.json
