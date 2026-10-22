#!/usr/bin/env bash
# Prepare a motion working folder: GSAP + local fonts + the templates.
# Usage: bash setup_motion.sh /home/claude/motion
# fonts.googleapis.com is blocked in the container; npm is not.
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${1:-/home/claude/motion}"
mkdir -p "$WORK"/{lib,fonts,plates,frames}
cd "$WORK"
[ -f package.json ] || npm init -y >/dev/null
npm i --silent gsap @fontsource/anton @fontsource/archivo-black @fontsource/cinzel \
  @fontsource/im-fell-english @fontsource/alegreya >/dev/null
cp node_modules/gsap/dist/gsap.min.js lib/
F=node_modules/@fontsource
cp $F/anton/files/anton-latin-400-normal.woff2                   fonts/Anton.woff2
cp $F/archivo-black/files/archivo-black-latin-400-normal.woff2   fonts/ArchivoBlack.woff2
cp $F/cinzel/files/cinzel-latin-600-normal.woff2                 fonts/Cinzel600.woff2
cp $F/im-fell-english/files/im-fell-english-latin-400-italic.woff2 fonts/FellItalic.woff2
cp $F/alegreya/files/alegreya-latin-400-normal.woff2             fonts/Alegreya.woff2
cp $F/alegreya/files/alegreya-latin-700-normal.woff2             fonts/Alegreya700.woff2
cp --update=none "$SKILL"/assets/motion_reel_template.html "$WORK"/reel.html
cp --update=none "$SKILL"/assets/motion_sting_template.html "$WORK"/sting.html
for t in ffmpeg node python3; do command -v $t >/dev/null || echo "MISSING: $t"; done
python3 -c "import playwright" 2>/dev/null || pip install -q playwright --break-system-packages
python3 -c "import numpy" 2>/dev/null || pip install -q numpy --break-system-packages
echo "Motion workspace ready: $WORK"
