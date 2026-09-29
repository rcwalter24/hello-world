from common import *


def f(x):
    return 0.15 * (x - 1) * (x - 3) * (x - 5) + 2


def df(x):
    return 0.15 * (3 * x ** 2 - 18 * x + 23)


class S03_Change(Base):
    def construct(self):
        self.chapter("III", "CHANGE", "MPC", "calculus: the mathematics of motion")
        self.derivative_and_integral()
        self.orbit()
        self.three_body()
        self.clear_all(keep_corner=False)

    def derivative_and_integral(self):
        ax = Axes(x_range=[0, 6, 1], y_range=[0, 4, 1], x_length=9, y_length=4.6,
                  axis_config={"color": GREY_C, "include_ticks": False}).shift(DOWN * 0.5)
        g = ax.plot(f, x_range=[0.2, 5.8], color=WHITE, stroke_width=4)
        self.play(Create(ax), Create(g), run_time=1.5)

        x0 = ValueTracker(0.6)
        tan = always_redraw(lambda: ax.plot(
            lambda x: f(x0.get_value()) + df(x0.get_value()) * (x - x0.get_value()),
            x_range=[x0.get_value() - 0.9, x0.get_value() + 0.9], color=MATH, stroke_width=5))
        dot = always_redraw(lambda: Dot(ax.c2p(x0.get_value(), f(x0.get_value())), color=MATH))
        slope = always_redraw(lambda: VGroup(
            T("slope", 26, GREY_B),
            DecimalNumber(df(x0.get_value()), num_decimal_places=2, color=MATH, font_size=40)
        ).arrange(RIGHT, buff=0.2).to_corner(UR, buff=1.0))
        deriv = MathTex("f'(x)=\\lim_{h\\to 0}\\frac{f(x+h)-f(x)}{h}", font_size=46, color=MATH)
        deriv.to_edge(UP, buff=0.9)
        self.play(Create(tan), FadeIn(dot), FadeIn(slope), Write(deriv))
        self.say("The derivative: how fast something is changing, at one instant.")
        self.play(x0.animate.set_value(5.4), run_time=5, rate_func=smooth)
        self.play(FadeOut(tan), FadeOut(dot), FadeOut(slope), run_time=0.6)

        integ = MathTex("\\int_a^b f(x)\\,dx", "=\\lim_{n\\to\\infty}\\sum_{k=1}^{n} f(x_k)\\,\\Delta x",
                        font_size=46, color=PHYS).move_to(deriv)
        rects = ax.get_riemann_rectangles(g, x_range=[0.5, 5.5], dx=0.5, color=[PHYS, "#FFD08A"],
                                          fill_opacity=0.7, stroke_width=1)
        self.play(ReplacementTransform(deriv, integ), Create(rects), run_time=1.5)
        self.say("The integral: add up infinitely many infinitely thin pieces.")
        for dx in (0.25, 0.1, 0.04, 0.02):
            new = ax.get_riemann_rectangles(g, x_range=[0.5, 5.5], dx=dx, color=[PHYS, "#FFD08A"],
                                            fill_opacity=0.7, stroke_width=1 if dx > 0.05 else 0)
            self.play(Transform(rects, new), run_time=1.0)
        ftc = MathTex("\\frac{d}{dx}\\int_a^x f(t)\\,dt = f(x)", font_size=50)
        ftc.set_color_by_gradient(MATH, PHYS).move_to(integ)
        self.play(ReplacementTransform(integ, ftc), run_time=1.2)
        self.say("Two ideas, secretly one: the Fundamental Theorem of Calculus.", wait=1.8)
        self.clear_all()

    def orbit(self):
        law = MathTex("F = G\\frac{Mm}{r^2}", font_size=54, color=PHYS).to_corner(UR, buff=0.9)
        law2 = MathTex("F = m a", font_size=54, color=PHYS).next_to(law, DOWN, buff=0.4)
        sun = glow_dot("#FFD166", 0.22, 10, 0.06, 0.07).move_to(LEFT * 2.6 + DOWN * 0.2)
        self.play(FadeIn(sun, scale=0.5), Write(law), Write(law2))
        self.say("Newton, 1687: one law of gravity for apples and planets alike.", wait=0.5)

        code = VGroup(*[T(l, 22, CODE, MONO_FONT) for l in [
            "for step in range(N):",
            "a  = -G*M * r / |r|³",
            "v += a * dt",
            "r += v * dt",
        ]]).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        for line in code[1:]:
            line.shift(RIGHT * 0.5)
        code.to_corner(DR, buff=0.9).shift(UP * 0.5)
        box = SurroundingRectangle(code, color=CODE, buff=0.25, corner_radius=0.1, stroke_width=1.5)

        # integrate an eccentric orbit (semi-implicit Euler, like the code on screen)
        GM, dt = 12.0, 0.002
        r = np.array([3.4, 0.0]); v = np.array([0.0, 1.35])
        pts = []
        for _ in range(12000):
            a = -GM * r / np.linalg.norm(r) ** 3
            v = v + a * dt
            r = r + v * dt
            pts.append(r.copy())
        pts = np.array(pts)
        # find one period
        ang = np.unwrap(np.arctan2(pts[:, 1], pts[:, 0]))
        per = int(np.argmax(ang > 2 * PI)) or len(pts)
        c0 = sun[1].get_center()
        P3 = lambda p: c0 + np.array([p[0], p[1], 0])

        coarse = VGroup(*[Dot(P3(pts[i]), radius=0.05, color=CODE) for i in range(0, per, per // 36)])
        self.play(FadeIn(box), LaggedStart(*[FadeIn(l) for l in code], lag_ratio=0.2))
        self.say("A computer can't solve it in one go. It takes tiny steps in time.")
        self.play(LaggedStart(*[GrowFromCenter(d) for d in coarse], lag_ratio=0.5), run_time=3.5)

        k = ValueTracker(0)
        planet = always_redraw(lambda: glow_dot(MATH, 0.1, 5, 0.04, 0.1).move_to(
            P3(pts[min(int(k.get_value()), len(pts) - 1)])))
        trail = TracedPath(lambda: planet[1].get_center(), stroke_color=MATH, stroke_width=3,
                           dissipating_time=2.5)
        self.add(trail, planet)
        self.say("Step by step, the math becomes a world: an orbit, a Kepler ellipse.")
        self.play(k.animate.set_value(2 * per - 1), run_time=7, rate_func=linear)
        self.play(FadeOut(coarse), run_time=0.5)
        self.clear_all()

    def three_body(self):
        # the Chenciner–Montgomery figure-eight solution (G = m = 1)
        x = np.array([[0.97000436, -0.24308753], [-0.97000436, 0.24308753], [0.0, 0.0]])
        v3 = np.array([-0.93240737, -0.86473146])
        v = np.array([-v3 / 2, -v3 / 2, v3])

        def acc(x):
            a = np.zeros_like(x)
            for i in range(3):
                for j in range(3):
                    if i != j:
                        d = x[j] - x[i]
                        a[i] += d / np.linalg.norm(d) ** 3
            return a

        dt, T_ = 0.002, 6.3259
        hist = []
        for _ in range(int(2 * T_ / dt)):
            # velocity Verlet
            a0 = acc(x)
            x = x + v * dt + 0.5 * a0 * dt * dt
            v = v + 0.5 * (a0 + acc(x)) * dt
            hist.append(x.copy())
        hist = np.array(hist) * 3.2
        k = ValueTracker(0)
        cols = [MATH, PHYS, CODE]
        bodies = [always_redraw(lambda i=i: glow_dot(cols[i], 0.13, 6, 0.04, 0.1).move_to(
            np.array([*hist[min(int(k.get_value()), len(hist) - 1), i], 0]) + DOWN * 0.2))
                  for i in range(3)]
        trails = [TracedPath(lambda b=b: b[1].get_center(), stroke_color=c, stroke_width=3,
                             dissipating_time=1.6) for b, c in zip(bodies, cols)]
        self.add(*trails, *bodies)
        self.say("Three bodies usually mean chaos. But there is a hidden dance…")
        self.play(k.animate.set_value(len(hist) * 0.5), run_time=5, rate_func=linear)
        self.say("…the figure-eight orbit: found by computer in 1993, proved in 2000.")
        self.play(k.animate.set_value(len(hist) - 1), run_time=5, rate_func=linear)
        self.wait(0.3)
        self.clear_all()
