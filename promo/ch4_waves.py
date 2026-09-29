from common import *


class S04_Waves(Base):
    def construct(self):
        self.chapter("IV", "WAVES", "MPC", "circles, complex numbers & everything that vibrates")
        self.euler()
        self.fourier_pi()
        self.square_wave()
        self.clear_all(keep_corner=False)

    def euler(self):
        R = 1.5
        c = LEFT * 4.4 + DOWN * 0.2
        circle = Circle(R, color=GREY_B, stroke_width=2).move_to(c)
        axes = VGroup(Line(c + LEFT * 2, c + RIGHT * 2, color=GREY_D, stroke_width=1.5),
                      Line(c + DOWN * 2, c + UP * 2, color=GREY_D, stroke_width=1.5))
        lab1 = MathTex("1", font_size=30, color=GREY_B).next_to(c + RIGHT * R, DR, 0.08)
        labi = MathTex("i", font_size=30, color=GREY_B).next_to(c + UP * R, UL, 0.08)
        th = ValueTracker(0)
        tip = lambda: c + R * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0])
        vec = always_redraw(lambda: Arrow(c, tip(), buff=0, color=MATH, stroke_width=5,
                                          max_tip_length_to_length_ratio=0.12))
        dot = always_redraw(lambda: Dot(tip(), color=MATH))
        arc = always_redraw(lambda: Arc(0.45, 0, max(th.get_value() % TAU, 1e-3),
                                        arc_center=c, color=PHYS))
        x0, sx = -2.3, 0.62
        wave = always_redraw(lambda: ParametricFunction(
            lambda s: np.array([x0 + sx * s, c[1] + R * np.sin(th.get_value() - s), 0]),
            t_range=[0, max(min(th.get_value(), 13.5), 0.01)], color=PHYS, stroke_width=4))
        link = always_redraw(lambda: DashedLine(tip(), np.array([x0, tip()[1], 0]),
                                                color=GREY_B, stroke_width=1.5))
        formula = MathTex("e^{i\\theta}", "=", "\\cos\\theta", "+", "i\\,\\sin\\theta", font_size=56)
        formula[0].set_color(MATH); formula[4].set_color(PHYS)
        formula.to_edge(UP, buff=0.9).shift(RIGHT * 1.5)
        self.play(Create(axes), Create(circle), FadeIn(lab1), FadeIn(labi))
        self.play(GrowArrow(vec.copy()), run_time=0.6)
        self.add(vec, dot, arc, wave, link)
        self.play(Write(formula))
        self.say("Multiply by i and you rotate. Spin steadily and a wave is born.")
        self.play(th.animate.set_value(4 * PI), run_time=7, rate_func=linear)
        self.play(th.animate.set_value(5 * PI), run_time=2.2, rate_func=smooth)
        m1 = MathTex("-1", color=PHYS, font_size=40).next_to(c + LEFT * R, LEFT, 0.15)
        self.play(Flash(c + LEFT * R, color=PHYS), FadeIn(m1))
        euler = MathTex("e^{i\\pi}", "+", "1", "=", "0", font_size=110).shift(RIGHT * 2.4 + DOWN * 0.1)
        euler[0].set_color(MATH)
        self.play(FadeOut(wave), FadeOut(link), TransformFromCopy(formula, euler), run_time=1.6)
        self.say("At θ = π: Euler's identity. e, i, π, 1 and 0 — in one line.", wait=1.0)
        notes = VGroup(*[T(s, 20, GREY_B) for s in
                         ["growth", "rotation", "circles", "unity", "nothing"]])
        for n, part in zip(notes, [euler[0][0], euler[0][1], euler[0][2], euler[2], euler[4]]):
            n.next_to(part, DOWN if part not in (euler[0][1], euler[0][2]) else UP, buff=0.45)
        notes[1].shift(LEFT * 0.35); notes[2].shift(RIGHT * 0.35)
        self.play(LaggedStart(*[FadeIn(n, shift=0.1 * UP) for n in notes], lag_ratio=0.25))
        self.wait(2.0)
        self.clear_all()

    def fourier_pi(self):
        glyph = MathTex("\\pi").family_members_with_points()[0]
        N = 1024
        ts = np.linspace(0, 1, N, endpoint=False)
        pts = np.array([glyph.point_from_proportion(t) for t in ts])
        pts -= pts.mean(axis=0)
        pts *= 5.2 / (pts[:, 1].max() - pts[:, 1].min())
        z = pts[:, 0] + 1j * pts[:, 1]
        K = 50
        ns = np.arange(-K, K + 1)
        coef = np.array([np.mean(z * np.exp(-2j * PI * n * ts)) for n in ns])
        order = [i for i in np.argsort(-np.abs(coef)) if ns[i] != 0]
        origin = LEFT * 0.2 + DOWN * 0.3
        c0 = origin + np.array([coef[K].real, coef[K].imag, 0])
        tau = ValueTracker(0)

        def chain():
            g = VGroup()
            p = c0.copy()
            t = tau.get_value()
            for idx in order:
                w = coef[idx] * np.exp(2j * PI * ns[idx] * t)
                q = p + np.array([w.real, w.imag, 0])
                r = abs(coef[idx])
                if r > 0.01:
                    g.add(Circle(r, stroke_width=1, stroke_opacity=0.35, color=MATH).move_to(p))
                    g.add(Line(p, q, stroke_width=2, color=WHITE, stroke_opacity=0.85))
                p = q
            return g

        def pen():
            w = coef[order] * np.exp(2j * PI * ns[order] * tau.get_value())
            s = w.sum()
            return c0 + np.array([s.real, s.imag, 0])

        arms = always_redraw(chain)
        trace = TracedPath(pen, stroke_color=PHYS, stroke_width=5)
        formula = MathTex("f(t)=\\sum_{n=-\\infty}^{\\infty} c_n\\, e^{2\\pi i n t}", font_size=44,
                          color=MATH).to_corner(UR, buff=0.8)
        self.add(arms, trace)
        self.play(Write(formula))
        self.say("Fourier, 1807: any shape is a sum of spinning circles.")
        self.play(tau.animate.set_value(1), run_time=12, rate_func=linear)
        trace.clear_updaters()
        self.play(FadeOut(arms), trace.animate.set_stroke(width=7), run_time=1)
        self.say("100 circles, each turning at its own frequency, draw a π.", wait=1.8)
        self.clear_all()

    def square_wave(self):
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[-1.5, 1.5, 1], x_length=11, y_length=3.6,
                  axis_config={"color": GREY_D, "include_ticks": False}).shift(UP * 0.2)

        def partial(N):
            return ax.plot(lambda x: sum(4 / (PI * k) * np.sin(k * x) for k in range(1, N + 1, 2)),
                           x_range=[0, 4 * PI, 0.01], color=PHYS, stroke_width=4)

        target = ax.plot(lambda x: np.sign(np.sin(x)) * 1.0, x_range=[0.001, 4 * PI - 0.001, 0.002],
                         color=GREY_C, stroke_width=2, use_smoothing=False)
        label = MathTex("\\text{terms: }1", font_size=40).to_edge(UP, buff=1.0)
        self.play(Create(ax), Create(DashedVMobject(target, num_dashes=120)))
        cur = partial(1)
        self.play(Create(cur), FadeIn(label))
        self.say("Stack sine waves, and even a sharp square wave appears.")
        for N in [3, 5, 9, 17, 41, 101]:
            new_label = MathTex("\\text{terms: }" + str((N + 1) // 2), font_size=40).move_to(label)
            self.play(Transform(cur, partial(N)), Transform(label, new_label), run_time=0.9)
        self.say("Splitting signals into frequencies: that's how MP3, JPEG and Wi-Fi work.",
                 color=CODE, wait=2.2)
        self.clear_all()
