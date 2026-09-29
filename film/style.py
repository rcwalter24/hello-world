"""Shared style + helpers for 'The Source Code of Everything'.

Every act is one Manim Scene subclass of FilmScene with a fixed DURATION.
Captions/tags are non-blocking (time-driven updaters), so they never
affect scene timing.  Call self.pad_to(DURATION) as the LAST line of construct().
"""
from manim import *
import numpy as np

# ---- palette -------------------------------------------------------------
BG      = "#070A14"
GOLD    = "#F5C451"   # mathematics
CYAN    = "#4CC9F0"   # physics
MAGENTA = "#F72585"   # computer science
WHITE_  = "#F4F6FF"
DIM     = "#5B6478"
FONT    = "Inter"
MONO    = "DejaVu Sans Mono"

config.background_color = BG
# resolution/fps come from CLI flags (-ql preview; build.sh passes --resolution 1920,1080 --fps 30)

# ---- act time budget (seconds) ------------------------------------------
BUDGET = {"act0": 15, "act1": 25, "act2": 30, "act3": 35,
          "act4": 35, "act5": 28, "act6": 12}   # sum = 180


def glow_dot(pos=ORIGIN, color=WHITE_, r=0.07, layers=7):
    """Dot with a soft radial halo.
    NOTE: never call .set_opacity()/animate.set_opacity on it (that flattens the
    halo layers to opaque). Use FadeIn / FadeOut instead."""
    g = VGroup()
    for i in range(layers, 0, -1):
        g.add(Circle(radius=r * (1 + 0.85 * i), stroke_width=0,
                     fill_color=color, fill_opacity=0.045 + 0.02 * (layers - i) / layers))
    g.add(Dot(radius=r, color=WHITE_))
    return g.move_to(pos)


def neon(mob, color, width=4.0, halo=True):
    """Style a VMobject as a neon line (adds a wide faint background stroke)."""
    mob.set_stroke(color, width=width)
    if halo:
        mob.set_stroke(color, width=width * 3.2, opacity=0.18, background=True)
    return mob


def label(text, color=WHITE_, size=26, **kw):
    return Text(text, font=FONT, font_size=size, color=color, **kw)


class FilmScene(Scene):
    DURATION = 10

    # ---- non-blocking overlays ------------------------------------------
    def _timed(self, mob, start, dur, fade=0.45, max_op=1.0):
        st = {"t": -start}
        mob.set_opacity(0)

        def upd(m, dt):
            st["t"] += dt
            t = st["t"]
            if t < 0:
                a = 0.0
            elif t < fade:
                a = t / fade
            elif t < dur - fade:
                a = 1.0
            elif t < dur:
                a = (dur - t) / fade
            else:
                a = 0.0
            m.set_opacity(a * max_op)
            if t >= dur:
                m.remove_updater(upd)
                self.remove(m)
        mob.add_updater(upd)
        mob.set_z_index(1000)
        self.add(mob)
        return mob

    def caption(self, text, start=0.0, dur=3.5, color=WHITE_):
        """Subtitle at bottom centre. start/dur are seconds from *now*."""
        m = Text(text, font=FONT, font_size=30, color=color)
        m.set_stroke(BG, width=6, background=True)
        if m.width > 12.4:
            m.scale_to_fit_width(12.4)
        m.to_edge(DOWN, buff=0.5)
        return self._timed(m, start, dur)

    def tag(self, num, text, color=WHITE_, start=0.0, dur=4.0):
        """Chapter tag, top-left, e.g. tag('01', 'BASICS')."""
        n = Text(num, font=MONO, font_size=20, color=color)
        t = Text(text, font=FONT, font_size=22, color=color, weight=BOLD)
        g = VGroup(n, t).arrange(RIGHT, buff=0.25).to_corner(UL, buff=0.5)
        return self._timed(g, start, dur, max_op=0.85)

    # ---- timing ---------------------------------------------------------
    def fade_all(self, t=0.6):
        objs = [m for m in self.mobjects if m.get_z_index() < 1000]
        if objs:
            self.play(*[FadeOut(m) for m in objs], run_time=t)

    def pad_to(self, total=None):
        total = total or self.DURATION
        remain = total - self.renderer.time
        if remain < -0.05:
            print(f"!! {type(self).__name__} over budget by {-remain:.2f}s")
        elif remain > 0:
            self.wait(remain)
