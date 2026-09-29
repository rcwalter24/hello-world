from common import *

CH = ("V", "LIGHT & QUANTA", "MP")


class S05a_Maxwell(Base):
    def construct(self):
        self.chapter(*CH, "four equations, and then the strangest idea in science")
        eqs = VGroup(
            MathTex("\\nabla\\cdot\\mathbf{E}=\\frac{\\rho}{\\varepsilon_0}"),
            MathTex("\\nabla\\cdot\\mathbf{B}=0"),
            MathTex("\\nabla\\times\\mathbf{E}=-\\frac{\\partial\\mathbf{B}}{\\partial t}"),
            MathTex("\\nabla\\times\\mathbf{B}=\\mu_0\\mathbf{J}+\\mu_0\\varepsilon_0"
                    "\\frac{\\partial\\mathbf{E}}{\\partial t}"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).scale(0.95).to_edge(UP, buff=0.8).shift(LEFT * 2.2)
        notes = VGroup(*[T(s, 22, GREY_B) for s in [
            "charges create electric fields",
            "there are no magnetic charges",
            "changing magnetism makes electricity",
            "changing electricity makes magnetism",
        ]])
        for n, e in zip(notes, eqs):
            n.next_to(e, RIGHT, buff=0.6).align_to(eqs[3].get_right() + RIGHT * 0.6, LEFT)
        for e in eqs:
            e.set_color_by_gradient(MATH, "#9ad9ef")
        self.say("James Clerk Maxwell, 1865: all of electricity and magnetism.")
        for e, n in zip(eqs, notes):
            self.play(Write(e), FadeIn(n, shift=LEFT * 0.2), run_time=1.1)
        self.wait(1.0)
        self.say("The last two feed each other — a self-sustaining wave that travels at…")
        speed = MathTex("c=\\frac{1}{\\sqrt{\\mu_0\\varepsilon_0}}", "\\approx 299\\,792\\,458\\ \\text{m/s}",
                        font_size=60, color=PHYS)
        speed.to_edge(DOWN, buff=1.25)
        self.play(eqs[2:].animate.set_color(PHYS), run_time=0.6)
        self.play(Write(speed), run_time=1.8)
        self.say("…the speed of light. Light IS an electromagnetic wave.", color=PHYS, wait=2.2)
        self.clear_all(keep_corner=False)


class S05b_EMWave(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=68 * DEGREES, theta=-50 * DEGREES, zoom=0.85)
        corner = make_corner(*CH)
        self.add_fixed_in_frame_mobjects(corner)
        axis = Line3D(LEFT * 6.5, RIGHT * 6.5, color=GREY_C, thickness=0.01)
        ph = ValueTracker(0)
        k, A = 1.1, 1.6
        xs = np.linspace(-6, 6, 49)

        def field(direction, color):
            def build():
                g = VGroup()
                p = ph.get_value()
                for x in xs:
                    amp = A * np.sin(k * x - p)
                    g.add(Line(np.array([x, 0, 0]), np.array([x, 0, 0]) + amp * direction,
                               color=color, stroke_width=2, stroke_opacity=0.8))
                curve = ParametricFunction(lambda x: np.array([x, 0, 0]) +
                                           A * np.sin(k * x - p) * direction,
                                           t_range=[-6, 6], color=color, stroke_width=4)
                g.add(curve)
                return g
            return always_redraw(build)

        E = field(OUT, PHYS)          # electric field (vertical in 3D view)
        B = field(UP, MATH)           # magnetic field (horizontal, perpendicular)
        lE = T("E  electric field", 26, PHYS)
        lB = T("B  magnetic field", 26, MATH)
        legend = VGroup(lE, lB).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6)
        cap = T("Each field creates the other. Forever. At the speed of light.", 30, GREY_A)
        cap.to_edge(DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(legend, cap)
        self.remove(legend, cap)
        self.play(Create(axis), run_time=0.8)
        self.add(E, B)
        self.play(FadeIn(legend), FadeIn(cap), ph.animate.set_value(3), run_time=3, rate_func=linear)
        self.begin_ambient_camera_rotation(rate=0.12)
        self.play(ph.animate.set_value(14), run_time=9, rate_func=linear)
        self.stop_ambient_camera_rotation()
        cap2 = T("Radio, Wi-Fi, X-rays, rainbows: one equation, different wavelengths.", 30, GREY_A)
        cap2.to_edge(DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(cap2)
        self.remove(cap2)
        self.play(FadeOut(cap), FadeIn(cap2), ph.animate.set_value(18), run_time=3, rate_func=linear)
        self.play(ph.animate.set_value(21), run_time=2.5, rate_func=linear)
        self.play(*[FadeOut(m) for m in (axis, E, B, legend, cap2, corner)], run_time=1)


class S05c_Quantum(Base):
    def construct(self):
        self.continue_chapter(*CH)
        shift = UP * 0.35
        W, H = 11.5, 5.4
        x_left, x_right = -6.2, 5.3
        barrier_x, screen_x = -3.6, 4.6
        d = 1.3
        slits = [np.array([barrier_x, d]), np.array([barrier_x, -d])]
        px, py = 690, 324
        X, Y = np.meshgrid(np.linspace(x_left, x_right, px), np.linspace(H / 2, -H / 2, py))
        r1 = np.hypot(X - slits[0][0], Y - slits[0][1])
        r2 = np.hypot(X - slits[1][0], Y - slits[1][1])
        k = 14.0
        stops = [BG, "#0e2530", "#1d5870", MATH, "#e6f8ff"]

        def frame(t):
            left = np.cos(k * (X - barrier_x) - t)
            right = (np.cos(k * r1 - t) / np.sqrt(r1 + 0.3) + np.cos(k * r2 - t) / np.sqrt(r2 + 0.3))
            v = np.where(X < barrier_x, 0.55 * left, 0.85 * right)
            out = rgba(colormap(0.5 + 0.5 * np.clip(v, -1, 1), stops))
            out[X > screen_x, 3] = 0
            return out

        img = ImageMobject(frame(0)).stretch_to_fit_width(x_right - x_left)
        img.stretch_to_fit_height(H).move_to(np.array([(x_left + x_right) / 2, 0, 0]) + shift)
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        t = ValueTracker(0)
        img.add_updater(lambda m: setattr(m, "pixel_array", frame(t.get_value())))

        gap = 0.18
        barrier = VGroup(
            Line([barrier_x, H / 2, 0], [barrier_x, d + gap, 0]),
            Line([barrier_x, d - gap, 0], [barrier_x, -d + gap, 0]),
            Line([barrier_x, -d - gap, 0], [barrier_x, -H / 2, 0]),
        ).set_stroke(WHITE, 6).shift(shift)
        screen = Line([screen_x, H / 2, 0], [screen_x, -H / 2, 0], color=GREY_B,
                      stroke_width=4).shift(shift)

        ys = np.linspace(-H / 2, H / 2, 800)
        a1 = np.hypot(screen_x - barrier_x, ys - d)
        a2 = np.hypot(screen_x - barrier_x, ys + d)
        amp = np.exp(1j * k * a1) / np.sqrt(a1) + np.exp(1j * k * a2) / np.sqrt(a2)
        inten = np.abs(amp) ** 2
        inten /= inten.max()
        prof = VMobject(color=PHYS, stroke_width=3).set_points_smoothly(
            [np.array([screen_x + 0.15 + 0.9 * i, y, 0]) + shift for i, y in zip(inten, ys)])

        self.play(FadeIn(img), Create(barrier), Create(screen), run_time=1.2)
        self.say("Send a wave through two slits: the ripples overlap and interfere.")
        self.play(t.animate.set_value(18), run_time=6, rate_func=linear)
        self.play(Create(prof), t.animate.set_value(24), run_time=2, rate_func=linear)
        self.say("Bright where crests meet crests, dark where crests meet troughs.")
        self.play(t.animate.set_value(34), run_time=3.5, rate_func=linear)
        img.clear_updaters()
        self.play(FadeOut(img), FadeOut(prof), run_time=1)

        self.say("Now fire single electrons, one at a time. Each lands as a single dot…")
        rng = np.random.default_rng(7)
        cdf = np.cumsum(inten); cdf /= cdf[-1]
        hits = Group()
        batches = [1, 1, 1, 1, 2, 3, 5, 8, 15, 30, 60, 120, 200, 300, 400, 500]
        for i, n in enumerate(batches):
            yy = np.interp(rng.random(n), cdf, ys)
            xx = screen_x + 0.35 + rng.random(n) * 0.9
            new = VGroup(*[Dot([x, y, 0], radius=0.022 if n > 20 else 0.04, color=CODE)
                           .shift(shift) for x, y in zip(xx, yy)])
            if n <= 3:
                src = Dot([x_left + 0.4, 0, 0], radius=0.05, color=CODE).shift(shift)
                self.play(src.animate.move_to(new[0].get_center()), run_time=0.45, rate_func=linear)
                self.remove(src)
                self.add(new)
                self.wait(0.1)
            else:
                self.play(FadeIn(new, lag_ratio=0.02), run_time=0.45)
            hits.add(new)
            if i == 9:
                self.say("…yet together, the dots paint the interference pattern.", color=CODE)
        self.wait(0.5)
        schro = MathTex("i\\hbar\\frac{\\partial}{\\partial t}\\Psi=\\hat{H}\\Psi", font_size=64,
                        color=MATH).move_to(LEFT * 0.5 + UP * 1.2)
        born = MathTex("P = |\\Psi|^2", font_size=54, color=PHYS).next_to(schro, DOWN, buff=0.6)
        self.play(Write(schro), run_time=1.5)
        self.play(Write(born))
        self.say("Each particle travels as a wave of probability. Nature, at bottom, is math.",
                 wait=2.5)
        self.clear_all(keep_corner=False)
