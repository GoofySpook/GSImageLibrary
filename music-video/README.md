# Music video toolkit

Two products for a Suno track. Instructions live in the `gsgrimoire-music-video` skill.

- **Teaser** (`template/`): 30 s Hyperframes film for social media. WebGL shader: depth parallax,
  shockwave rings, bass-driven glow, particles, split-screen seam. Everything song-specific is in
  `assets/film.js`, `assets/bands.js`, `assets/plates/` and `compositions/title.html`.
- **Full song** (`tools/lowrender.py`): one image, slow zoom, occasional glitch. 3:54 song took 2 min 17 s.
  It stops before the mix if the cycle has a visible seam; `--no-seam-check` overrides that.

Pinned: hyperframes 0.9.6, gsap 3.12.5. Telemetry off: `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1`.

Known limits: `hyperframes check` hung on the WebGL page; use `snapshot`. Eye lights in `world.html`
are hard-coded for the plate called `icedr` (edit the two coordinates or the plate name).
