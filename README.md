# GS Grimoire — Motion archive

Finished motion pieces and the code that renders them. This is the `motion` branch of
GSImageLibrary. It shares no history with `main`, so nothing here appears in the image
library's tree or affects its catalogue counts. Never merge it into `main`.

Each piece lives in its own folder with everything it needs: the page, fonts, GSAP, art,
a `render.sh` with the exact command used, and the finished MP4.

## Pieces

| Date | Piece | Length | Folder | Video |
|---|---|---|---|---|
| 2026-10-21 | **Gold Rune sting.** Rune circle draws, GS GRIMOIRE resolves out of blur, light hit, "The Archive is open" | 6.0 s | [`stings/2026-10-21-gold-rune`](stings/2026-10-21-gold-rune) | [MP4](stings/2026-10-21-gold-rune/GS_Grimoire_Sting_GoldRune_1080x1920.mp4) |
| 2026-10-21 | **Wax Seal sting.** A bestiary of real GS art riffles backwards, the book closes, hot wax drops, GS rises out of it, "Sealed in the Archive" | 9.4 s | [`stings/2026-10-21-wax-seal`](stings/2026-10-21-wax-seal) | [MP4](stings/2026-10-21-wax-seal/GS_Grimoire_Sting_WaxSeal_1080x1920.mp4) |

All pieces are 1080 × 1920, 30 fps, H.264 with `+faststart`, audio between −14 and −17 LUFS.

## Re-using a piece

From a Claude session (phone is fine): *"Clone the motion branch of GSImageLibrary and
re-render the wax seal with the tagline changed to …"*. By hand:

```bash
git clone -b motion --single-branch https://github.com/GoofySpook/GSImageLibrary gs-motion
cd gs-motion
bash stings/2026-10-21-wax-seal/render.sh
```

Needs ffmpeg, Python 3 with numpy and Playwright (Chromium). `toolkit/setup_motion.sh`
installs the Python side.

Common edits, all at the top of the piece's HTML file:

- **Wax Seal:** `#tag` text (tagline), `NAMES` (page headings), `art/aNN.jpg` (page art,
  see `art/SOURCES.md`), the `#b8141c` / `heat` colours for a different wax.
- **Gold Rune:** the title and subline text, `DUR` (length), `HIT` (moment of the flash).

## Toolkit

`toolkit/` is a **snapshot** of the motion scripts from the `gsgrimoire-tiktok-carousel` skill
on the date of the latest piece, so every folder here re-renders exactly as it did. The skill
holds the live copy and the templates for new pieces; use the skill to build something new and
this archive to revisit something finished.

| Script | Does |
|---|---|
| `render_motion.py` | Seeks the page frame by frame, screenshots at 3×, encodes the MP4. `--motion-blur` for fast stretches |
| `review.py` | Contact sheet, hit-frame strips, loudness. Look at both images before shipping |
| `beat_grid.py` | Tempo, beats and bars of a music track, with a click-track check |
| `waxseal_sfx.py` | Synthesises the Wax Seal soundtrack from the page's own event times |
| `setup_motion.sh` | Fresh workspace with GSAP and fonts (for new pieces) |

## Adding a piece

New folder under `stings/` or `reels/` named `YYYY-MM-DD-name`, self-contained as above, a
`render.sh`, the MP4, and a row in the table. Refresh `toolkit/` only if a script changed, and
check the older pieces still render.

Fonts are Cinzel and IM Fell English (SIL Open Font License). GSAP is under its standard
no-charge licence.
