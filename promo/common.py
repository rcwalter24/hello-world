"""Shared palette, typography and helpers for the promo film."""
from manim import *
import numpy as np

MATH = "#58C4DD"   # mathematics – the language
PHYS = "#FF9F43"   # physics     – the story
CODE = "#7BED9F"   # computation – the pen
BG = "#0B0E14"

TITLE_FONT = "Montserrat"
BODY_FONT = "Inter"
MONO_FONT = "DejaVu Sans Mono"

config.background_color = BG

TAGS = {"M": ("MATH", MATH), "P": ("PHYSICS", PHYS), "C": ("CODE", CODE)}


def T(s, size=36, color=WHITE, font=BODY_FONT, weight=NORMAL, **kw):
    return Text(s, font=font, font_size=size, color=color, weight=weight, **kw)


def tag_row(keys, size=18):
    row = VGroup()
    for k in keys:
        name, col = TAGS[k]
        row.add(VGroup(Dot(radius=0.07 * size / 18, color=col),
                       T(name, size, col, weight=BOLD)).arrange(RIGHT, buff=0.12))
    return row.arrange(RIGHT, buff=0.35)


def glow_dot(color=WHITE, radius=0.08, layers=10, spread=0.05, opacity=0.07):
    halo = VGroup(*[Circle(radius=radius + spread * i, stroke_width=0,
                           fill_color=color, fill_opacity=opacity)
                    for i in range(1, layers + 1)])
    return VGroup(halo, Dot(radius=radius, color=color))


def colormap(v, stops):
    """Map an array v in [0,1] through a list of hex colour stops -> uint8 RGB."""
    v = np.clip(v, 0, 1)
    cols = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in stops], float)
    x = v * (len(stops) - 1)
    i = np.clip(np.floor(x).astype(int), 0, len(stops) - 2)
    f = (x - i)[..., None]
    return (cols[i] * (1 - f) + cols[i + 1] * f).astype(np.uint8)


def rgba(rgb):
    a = np.full(rgb.shape[:2] + (1,), 255, np.uint8)
    return np.concatenate([rgb, a], axis=2)


def make_corner(num, title, keys):
    return VGroup(T(f"{num}  {title}", 18, GREY_B, TITLE_FONT, weight=MEDIUM),
                  tag_row(keys, 14)).arrange(RIGHT, buff=0.4).to_corner(UL, buff=0.35)


class Base(Scene):
    """Scene with chapter cards and a single caption slot at the bottom."""

    caption = None
    corner = None

    def chapter(self, num, title, keys, subtitle=None):
        n = T(num, 30, GREY_B, TITLE_FONT, weight=MEDIUM)
        t = T(title, 76, WHITE, TITLE_FONT, weight=BOLD)
        line = Line(LEFT * 3.2, RIGHT * 3.2, stroke_width=3)
        line.set_color([TAGS[k][1] for k in keys] if len(keys) > 1 else TAGS[keys[0]][1])
        g = VGroup(n, t, line)
        if subtitle:
            g.add(T(subtitle, 28, GREY_A))
        g.arrange(DOWN, buff=0.35)
        tg = tag_row(keys).next_to(g, DOWN, buff=0.55)
        self.play(FadeIn(n, shift=DOWN * 0.2), FadeIn(t, shift=UP * 0.3),
                  GrowFromCenter(line), *[FadeIn(x) for x in g[3:]], run_time=1.2)
        self.play(LaggedStart(*[FadeIn(x, scale=0.6) for x in tg], lag_ratio=0.25), run_time=0.9)
        self.wait(1.2)
        self.corner = make_corner(num, title, keys)
        self.play(FadeOut(VGroup(g, tg), shift=UP * 0.3), FadeIn(self.corner), run_time=0.8)

    def continue_chapter(self, num, title, keys):
        self.corner = make_corner(num, title, keys)
        self.add(self.corner)

    def say(self, text, size=30, color=GREY_A, wait=None, **kw):
        new = T(text, size, color, **kw)
        if new.width > config.frame_width - 1:
            new.scale_to_fit_width(config.frame_width - 1)
        new.to_edge(DOWN, buff=0.45)
        new = VGroup(BackgroundRectangle(new, color=BG, fill_opacity=0.72, buff=0.14,
                                         corner_radius=0.08), new)
        if self.caption is not None:
            self.play(FadeOut(self.caption, shift=UP * 0.1), run_time=0.3)
        self.play(FadeIn(new, shift=UP * 0.15), run_time=0.5)
        self.caption = new
        if wait:
            self.wait(wait)
        return new

    def unsay(self):
        if self.caption is not None:
            self.play(FadeOut(self.caption), run_time=0.5)
            self.caption = None

    def clear_all(self, run_time=0.8, keep_corner=True):
        mobs = [m for m in self.mobjects if not (keep_corner and m is self.corner)]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        self.caption = None
        if not keep_corner:
            self.corner = None
