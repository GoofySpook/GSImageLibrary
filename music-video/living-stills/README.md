# Living stills (2.5D reels)

Still art that breathes: 1080x1920, voice, music, SFX, captions. First test 2026-11-03: 23 s, 7 plates,
19 min render on 2 cores, built in about 2 hours of session time including new effects.

- `template/assets/film.js`: shots, effects, captions. This is the file to change per reel.
- `tools/prep.py`: plates at 2048 high plus depth maps and coordinate grids (`sheets/g_*.jpg`).
- `tools/masks.py`: polygons on plate coordinates. R cloth (`pin` = fixed top), G flow, B rigid swing.
- `tools/mix.py`: synthesised SFX, voice, ducked music. Paths and times are this reel's; edit them.
- Voice: `npx hyperframes tts "line" -v bm_george -s 0.9 -o lN.wav`, one file per line, so cuts follow speech.

Effects: smoke, fog, light (flicker, can follow a swing), eyes (open and blink), lid (blink on painted
eyes), orb (swirl and pulse), glint (sweep along a blade), cloth, flow, swing, particles.
Add `assets/bands.js` with `../tools/analyze.py`, and `assets/mix.wav`, before rendering.
