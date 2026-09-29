# Production brief — "The Source Code of Everything" (3:00, English, no voice-over)

Music + on-screen captions only. Captions ARE the narration: short, plain English, at most ~12 words.
Film = 7 acts rendered separately by Manim CE 0.21, concatenated by `build.sh`.
Python: `/opt/mv/bin/python` (manim, numpy, scipy installed; LaTeX + ffmpeg available). Font: Inter.

## Look
Deep navy background (BG), thin glowing neon lines, generous empty space, one idea on screen at a time.
Colour code (never break it): **GOLD = mathematics, CYAN = physics, MAGENTA = computer science**, white for neutral.
Deeper acts (4, 5) increasingly *mix* the three colours in one picture; act 5 braids them.
Reference tone: 3Blue1Brown clarity + a cinematic trailer's pacing. Slow, confident, beautiful. No clutter, no walls of text.
Every act begins by fading in from the background and ends by fading everything out to the background
(so acts butt-join cleanly): use `self.fade_all(~0.7)` near the end.

## Code contract  (read /home/user/hello-world/film/style.py and act0_point.py first)
- File name and class are fixed per act (see your task). `class ActN(FilmScene)`, `DURATION = BUDGET["actN"]`.
- `from style import *`. Use GOLD/CYAN/MAGENTA/WHITE_/DIM/BG/FONT/MONO, `glow_dot`, `neon`, `label`.
- Captions/tags are non-blocking: `self.caption("text", start=<s from now>, dur=<s>)`, `self.tag("02", "HIGH SCHOOL", color, start, dur)`.
- Last line of construct(): `self.pad_to()`. Total time must land within the budget: track it with comments like act0 does.
  If pad_to prints "over budget", trim run_times. build.sh hard-cuts at the budget, so overshoot = lost ending.
- Never `set_opacity` on `glow_dot`s; use FadeIn/FadeOut. Avoid `Text` for math — use `MathTex` (LaTeX is installed).
  Avoid huge point counts in VMobjects (ParametricFunction with >2000 points, many hundred-object VGroups) — render time.
- Heavy pixel stuff (fractals, lensing, interference): compute with numpy → `ImageMobject(np_uint8_array)`,
  update frames with `always_redraw`/`ValueTracker` or pre-render a few dozen keyframes. Keep each act's 1080p30 render < ~6 min.
- Do NOT edit style.py, build.sh or other acts' files. If you need a helper, define it locally in your file.
  Do NOT run git. Render only your own act, into your own media dir.

## How to work
1. Write the file. 2. Preview: `cd /home/user/hello-world/film && /opt/mv/bin/python -m manim -ql --disable_caching --media_dir media/actN actN_x.py ActN`
   (output: media/actN/videos/actN_x/480p15/ActN.mp4).
3. **Look at it**: extract ≥6 frames spread over the act with ffmpeg (`-ss t -frames:v 1`), stitch a contact sheet,
   view with the Read tool, and fix anything ugly: overlaps, off-screen objects, tiny text, dead time, captions colliding with the drawing
   (bottom 1.3 units are reserved for captions; top-left corner for the chapter tag — keep the drawing out of them).
4. Final check at production quality: `--resolution 1920,1080 --fps 30`, confirm duration ≈ budget with ffprobe.
5. Report back in ≤10 lines: file, actual duration, anything skipped/simplified, anything the director should know.

## Timeline of the whole film (for context)
0:00 act0 Point 15s | 0:15 act1 BASICS 25s | 0:40 act2 HIGH SCHOOL 30s | 1:10 act3 UNIVERSITY 35s
1:45 act4 BEYOND 35s | 2:20 act5 FRONTIER 28s | 2:48 act6 Finale 12s
Each of acts 1–4 carries three parallel threads (math/physics/CS); give each ≈1/3 of the time, in that order or interleaved,
with a chapter tag in the first seconds. Show the *idea* visually — the viewer should "get" it without reading.
