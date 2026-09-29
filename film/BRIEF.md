# Production brief v2 — "The Source Code of Everything" (3:00, English, captions + score only)

## The idea (read this first)
v1 cut between maths / physics / CS as three unrelated montages. **v2 is organised by concept, not by discipline.**
Each of acts 1–5 follows ONE idea that genuinely runs through all three fields, and *hands one visual object* from
discipline to discipline (matching-cut / morph — never a hard cut): e.g. a gold circle becomes a cyan wave becomes magenta spectrum bars.
Inside every act the difficulty climbs BASICS → HIGH SCHOOL → UNIVERSITY → FRONTIER, and the ladder is shown on screen.
The viewer must feel: "it is the *same thing* wearing three costumes."

Acts (fixed budgets, sum 180 s):
0 The Point 15s (done) | **1 ROTATION 25s** | **2 MINIMIZATION 30s** | **3 INFORMATION 35s** | **4 SELF-REFERENCE 35s** | **5 QUANTUM 28s** | 6 Finale 12s (done)
Cross-links to plant (small visual/caption echoes make the whole film cohere):
rotation (act1) = phase = the arrows in quantum (act5) · least-time/least-action (act2) = "the arrows cancel except the shortest path" (act5) ·
bits (act3) = qubits (act5) = black-hole horizon (act3) · halting/self-reference (act4) = Curry–Howard "a proof is a program" (act4).

## Look
Deep navy background, thin glowing neon lines, generous empty space, ONE idea on screen at a time.
Colour code (never break it): **GOLD = mathematics, CYAN = physics, MAGENTA = computer science**, white neutral.
The hand-off object changes colour as it changes discipline. Frontier beats mix colours (two- or three-colour gradients).
Tone: 3Blue1Brown clarity + cinematic trailer pacing. Slow, confident, beautiful. No clutter, no walls of text.
Every act fades in from the background at its start and ends with `self.fade_all(~0.7)` (acts butt-join cleanly).

## Code contract  (read style.py, act0_point.py, act6_finale.py first; old v1 acts are in old/ — REUSE their code/ideas)
- Fixed file + class per act (see your task). `from style import *`; `DURATION = BUDGET["actN"]`.
- Overlays are non-blocking: `self.caption(text, start, dur)`, `self.tag("02", "MINIMIZATION", WHITE_, start, dur)` (concept tag, top-left, once at start ~ dur 3.5),
  `self.badge("MATHEMATICS", GOLD, start, dur)` (discipline, under tag; one per beat), `self.level(idx, color, start, dur)` (ladder, top-right; one per beat, idx 0..3).
  Bottom 1.3 units = captions; top strip ≈ 1 unit = tag/badge/ladder. Keep drawings out of both.
- One caption per beat (≤ 14 words), timed to the beat. Captions are the narration.
- Last line of construct(): `self.pad_to()`. Track running time in comments. If "over budget" prints, trim run_times (30 fps: preview with `--resolution 854,480 --fps 30`, not -ql which is 15 fps and rounds).
- Never `set_opacity` on `glow_dot`s (use FadeIn/FadeOut). Use MathTex for maths. Avoid >2000-point VMobjects and hundreds-object VGroups.
- Manim gotcha: a mobject changed only by *another* mobject's updater can freeze in the cached static layer — give it a no-op updater.
- numpy for heavy pixel scenes → ImageMobject keyframes; precompute once at top of construct. Full 1080p30 act render should stay < ~6 min.
- Do NOT edit style.py, build.sh, act0/act6 or other acts. Helpers go in your own file. Do NOT run git. Render only your own act into media/actN.
- Scientific accuracy: keep every claim modest and correct. Open research questions keep their question mark.

## How to work
1. Read the old v1 code that matches your beats (old/act*.py) and lift what works; rewrite the glue so objects hand off between disciplines.
2. Preview: `cd /home/user/hello-world/film && /opt/mv/bin/python -m manim --resolution 854,480 --fps 30 --disable_caching --media_dir media/actN actN_x.py ActN`
3. LOOK at it: contact sheet of ≥12 frames incl. every hand-off moment, read it with the Read tool, fix overlaps/off-screen/tiny text/dead time.
4. Final: `--resolution 1920,1080 --fps 30`; ffprobe duration ≈ budget.
5. Report in ≤10 lines: file, duration, what you cut/simplified, anything the director should know.
