from style import *


class Act6(FilmScene):
    DURATION = BUDGET["act6"]

    def construct(self):
        cols = [GOLD, CYAN, MAGENTA]
        theta = ValueTracker(PI / 2)
        R = ValueTracker(1.7)
        theta.add_updater(lambda m, dt: m.increment_value(dt * 0.9))
        self.add(theta)

        dots = []
        for i, c in enumerate(cols):
            d = glow_dot(ORIGIN, c, r=0.11, layers=8)
            d.add_updater(lambda m, i=i: m.move_to(
                R.get_value() * np.array([np.cos(theta.get_value() + TAU * i / 3),
                                          np.sin(theta.get_value() + TAU * i / 3) * 0.78, 0])))
            dots.append(d)
        trails = [TracedPath(d[-1].get_center, stroke_color=c, stroke_width=2.5,
                             stroke_opacity=[0, 0.7], dissipating_time=1.6)
                  for d, c in zip(dots, cols)]
        self.add(*trails)
        self.play(*[FadeIn(d, scale=0.4) for d in dots], run_time=0.9)      # 0.9

        # three lines, one per discipline
        lines = [("Mathematics is the language.", GOLD),
                 ("Physics is the world.", CYAN),
                 ("Computation is the process.", MAGENTA)]
        for i, (txt, c) in enumerate(lines):
            self.caption(txt, start=0.0, dur=1.85, color=c)
            self.play(Indicate(dots[i], scale_factor=1.9, color=c), run_time=1.5)
            self.wait(0.35)                                                  # +1.85 each -> 6.45

        # converge into a single point
        self.caption("They are one thing.", start=0.1, dur=2.4, color=WHITE_)
        self.play(R.animate.set_value(0.0), run_time=1.6, rate_func=smooth)  # 8.05
        flash = Circle(radius=0.2, stroke_width=0, fill_color=WHITE_, fill_opacity=0.9)
        self.play(flash.animate.scale(9).set_fill(opacity=0), run_time=0.9, rate_func=rush_from)  # 8.95
        self.remove(flash)
        theta.clear_updaters()

        # title
        core = glow_dot(UP * 0.85, WHITE_, r=0.09, layers=8)
        self.play(FadeIn(core, scale=0.5), run_time=0.01)
        for d in dots:
            d.clear_updaters(); self.remove(d)
        title = Text("THE SOURCE CODE OF EVERYTHING", font=FONT, font_size=46, weight=LIGHT,
                     color=WHITE_)
        title.scale_to_fit_width(min(title.width, 11.5)).move_to(DOWN * 0.15)
        title.set_stroke(BG, width=5, background=True)
        w = title.width * 0.9
        underline = VGroup(*[Line(LEFT * w / 2 + RIGHT * w * k / 3, LEFT * w / 2 + RIGHT * w * (k + 1) / 3,
                                  stroke_width=3, color=c)
                             for k, c in enumerate([GOLD, CYAN, MAGENTA])])
        underline.next_to(title, DOWN, buff=0.28)
        self.play(FadeIn(title, shift=UP * 0.15), LaggedStart(*[Create(l) for l in underline], lag_ratio=0.35), run_time=1.4)   # 10.36
        self.caption("And you are only just beginning.", start=0.0, dur=1.4)
        self.wait(1.0)                                                         # 11.4
        self.play(*[FadeOut(m) for m in [core, title, underline]] + [FadeOut(t) for t in trails],
                  run_time=0.55)
        self.pad_to()
