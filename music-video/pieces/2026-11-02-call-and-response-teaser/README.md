# Call and Response, teaser (2026-11-02)

30 s, 1920x1080, track window 0:32.585 to 1:02.585, built on `../../template`.
Copy the template, then lay this folder's `assets/` over it. The track is left out of this public
branch; recreate `assets/track.wav` with:

    ffmpeg -ss 32.585 -t 30 -i Call_and_Response.wav -af "afade=t=in:st=0:d=0.25,afade=t=out:st=28.76:d=1.24,volume=-0.6dB" -ar 48000 -c:a pcm_s16le assets/track.wav

Render took 20 min on 2 cores. Afterwards re-encode (`-crf 19`, +1.6 dB): the raw render is 166 MB.
