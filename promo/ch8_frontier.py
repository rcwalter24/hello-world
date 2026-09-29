from common import *
import mpmath

CH = ("VIII", "THE FRONTIER", "MPC")


class S08a_Spacetime(Base):
    def construct(self):
        self.chapter(*CH, "where the map ends")
        plane = NumberPlane(x_range=[-9, 9, 0.6], y_range=[-5.4, 5.4, 0.6],
                            background_line_style={"stroke_color": MATH, "stroke_width": 1.2,
                                                   "stroke_opacity": 0.45},
                            axis_config={"stroke_opacity": 0}, faded_line_ratio=1)
        plane.prepare_for_nonlinear_transform(60)
        self.play(Create(plane, lag_ratio=0.02), run_time=1.5)
        self.add(self.corner)
        star = glow_dot(PHYS, 0.25, 12, 0.07, 0.08)

        def warp(p, k=0.94, s=2.4):
            r2 = (p[0] ** 2 + p[1] ** 2) / s ** 2
            return p - k * p / (r2 + 1)

        self.play(FadeIn(star, scale=0.3),
                  plane.animate.apply_function(warp), run_time=2.5)
        eq = MathTex("G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}",
                     font_size=54)
        eqg = VGroup(BackgroundRectangle(eq, color=BG, fill_opacity=0.8, buff=0.2), eq)
        eqg.to_edge(UP, buff=0.8)
        self.play(FadeIn(eqg))
        self.say("Einstein, 1915: gravity is not a force. It is the curvature of spacetime.",
                 wait=2.2)
        self.play(FadeOut(plane), FadeOut(star), FadeOut(eqg), run_time=1)

        # inspiral + gravitational waves
        Tc, Tend = 9.0, 8.85
        ts = np.linspace(0, Tend, 4000)
        r = 1.5 * (1 - ts / Tc) ** 0.25
        om = 2.2 * (1.5 / r) ** 1.5
        phi = np.concatenate([[0], np.cumsum(om[1:] * np.diff(ts))])
        emit = [np.interp(m * PI, phi, ts) for m in range(int(phi[-1] / PI))]
        tt = ValueTracker(0)
        speed = 1.6
        center = UP * 0.7

        def rings():
            t = tt.get_value()
            g = VGroup()
            for e in emit:
                if e <= t:
                    rad = 0.3 + speed * (t - e)
                    if rad < 9:
                        g.add(Circle(rad, stroke_width=2.5, color=MATH,
                                     stroke_opacity=max(0, 0.7 - rad / 12)).move_to(center))
            return g

        def holes():
            t = min(tt.get_value(), Tend)
            rr = np.interp(t, ts, r); ph = np.interp(t, ts, phi)
            d = rr * np.array([np.cos(ph), np.sin(ph) * 0.45, 0])
            return VGroup(glow_dot(WHITE, 0.14, 5, 0.04, 0.1).move_to(center + d),
                          glow_dot(WHITE, 0.14, 5, 0.04, 0.1).move_to(center - d))

        # chirp strain signal
        ax_x0, ax_x1, ax_y = -6.2, 6.2, -2.25

        def chirp():
            t = tt.get_value()
            n = max(2, int(len(ts) * min(t, Tend) / Tend))
            amp = 0.07 / np.interp(ts[:n], ts, r) ** 1.5
            h = amp * np.cos(2 * phi[:n])
            xs = ax_x0 + (ax_x1 - ax_x0) * ts[:n] / Tc
            return VMobject(stroke_color=PHYS, stroke_width=2.5).set_points_as_corners(
                [np.array([x, ax_y + y, 0]) for x, y in zip(xs, h)])

        R = always_redraw(rings); H = always_redraw(holes); C = always_redraw(chirp)
        base = Line([ax_x0, ax_y, 0], [ax_x1, ax_y, 0], stroke_width=1, color=GREY_D)
        self.add(R, H, base, C)
        self.say("Two black holes spiral together, shaking spacetime itself…")
        self.play(tt.animate.set_value(6.5), run_time=6.5, rate_func=linear)
        self.play(tt.animate.set_value(Tend), run_time=3.5, rate_func=linear)
        H.clear_updaters(); C.clear_updaters()
        merged = glow_dot(WHITE, 0.22, 10, 0.06, 0.1).move_to(center)
        self.play(FadeOut(H), FadeIn(merged, scale=2), Flash(center, color=WHITE, line_length=0.6,
                                                          flash_radius=0.5))
        self.say("2015: LIGO heard that 'chirp' — 1.3 billion years later, predicted a century before.",
                 color=PHYS)
        self.play(tt.animate.set_value(Tend + 3), run_time=3, rate_func=linear)
        R.clear_updaters()
        self.clear_all(keep_corner=False)


class S08b_Qubit(Base):
    def construct(self):
        self.continue_chapter(*CH)
        Rr, el, az = 2.3, 18 * DEGREES, 35 * DEGREES
        c0 = LEFT * 3.2 + DOWN * 0.3

        def proj(x, y, z):
            X = -x * np.sin(az) + y * np.cos(az)
            Y = z * np.cos(el) - (x * np.cos(az) + y * np.sin(az)) * np.sin(el)
            return c0 + Rr * np.array([X, Y, 0])

        sphere = Circle(Rr, color=GREY_B, stroke_width=2).move_to(c0)
        sphere.set_fill(MATH, 0.06)
        eq_front = ParametricFunction(lambda t: proj(np.cos(t), np.sin(t), 0), t_range=[-PI + az, az],
                                      color=GREY_B, stroke_width=1.5)
        eq_back = DashedVMobject(ParametricFunction(lambda t: proj(np.cos(t), np.sin(t), 0),
                                                    t_range=[az, PI + az], color=GREY_D,
                                                    stroke_width=1.5), num_dashes=30)
        zax = DashedLine(proj(0, 0, -1.15), proj(0, 0, 1.15), color=GREY_C, stroke_width=1.5)
        k0 = MathTex("|0\\rangle", font_size=40).next_to(proj(0, 0, 1), UP, 0.2)
        k1 = MathTex("|1\\rangle", font_size=40).next_to(proj(0, 0, -1), DOWN, 0.2)
        th = ValueTracker(0.001); ph = ValueTracker(0)

        def tip():
            t, p = th.get_value(), ph.get_value()
            return proj(np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t))

        vec = always_redraw(lambda: Arrow(c0, tip(), buff=0, color=PHYS, stroke_width=6,
                                          max_tip_length_to_length_ratio=0.12))
        shadow = always_redraw(lambda: DashedLine(c0, proj(np.sin(th.get_value()) * np.cos(ph.get_value()),
                                                              np.sin(th.get_value()) * np.sin(ph.get_value()), 0),
                                                  color=PHYS, stroke_opacity=0.5, stroke_width=1.5))
        self.play(DrawBorderThenFill(sphere), Create(eq_front), Create(eq_back), Create(zax),
                  FadeIn(k0), FadeIn(k1), run_time=1.5)
        self.add(shadow, vec)
        psi = MathTex("|\\psi\\rangle = \\cos\\tfrac{\\theta}{2}\\,|0\\rangle + "
                      "e^{i\\varphi}\\sin\\tfrac{\\theta}{2}\\,|1\\rangle", font_size=44)
        psi.move_to(RIGHT * 3.2 + UP * 2.2)
        self.play(Write(psi))
        self.say("A bit is 0 or 1. A qubit can be any point on a sphere.")
        self.play(th.animate.set_value(PI / 2), run_time=1.8)
        self.play(ph.animate.set_value(2 * PI), run_time=3, rate_func=linear)
        self.play(th.animate.set_value(2.3), ph.animate.set_value(3 * PI), run_time=2)

        rows = VGroup()
        data = [("1 qubit", "2"), ("10 qubits", "1{,}024"), ("50 qubits", "10^{15}"),
                ("300 qubits", "> \\text{atoms in the universe}")]
        for a, b in data:
            rows.add(VGroup(T(a, 26, GREY_A), MathTex(b, font_size=38, color=MATH)).arrange(RIGHT, buff=0.4))
        head = T("numbers needed to describe the state", 22, GREY_B)
        tbl = VGroup(head, *rows).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        tbl.next_to(psi, DOWN, buff=0.7).align_to(psi, LEFT)
        self.say("n qubits hold 2ⁿ amplitudes at once — linear algebra made physical.")
        self.play(FadeIn(head))
        for rr in rows:
            self.play(FadeIn(rr, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.6)
        self.say("Shor, 1994: a quantum computer could factor huge numbers — primes again.",
                 color=PHYS, wait=2.2)
        self.clear_all(keep_corner=False)


class S08c_Riemann(Base):
    def construct(self):
        self.continue_chapter(*CH)
        z1 = MathTex("\\zeta(s)", "=", "\\sum_{n=1}^{\\infty}\\frac{1}{n^{s}}", "=",
                     "\\prod_{p\\ \\text{prime}}\\frac{1}{1-p^{-s}}", font_size=56)
        z1[4].set_color(MATH)
        z1.move_to(UP * 0.4)
        self.play(Write(z1), run_time=2)
        self.say("Euler's golden key: a sum over all numbers equals a product over all primes.")
        self.wait(1.5)
        self.play(z1.animate.scale(0.55).to_corner(UR, buff=0.3), run_time=1)

        # critical strip
        strip_ax = Axes(x_range=[-0.5, 1.5, 0.5], y_range=[0, 45, 10], x_length=2.6, y_length=5.2,
                        axis_config={"color": GREY_C, "include_ticks": False})
        strip_ax.to_edge(LEFT, buff=1.0).shift(DOWN * 0.35)
        strip = Rectangle(width=strip_ax.x_axis.unit_size, height=5.2, stroke_width=0,
                          fill_color=MATH, fill_opacity=0.12)
        strip.move_to(strip_ax.c2p(0.5, 22.5))
        crit = DashedLine(strip_ax.c2p(0.5, 0), strip_ax.c2p(0.5, 45), color=PHYS)
        lab = MathTex("\\mathrm{Re}(s)=\\tfrac12", font_size=30, color=PHYS).next_to(strip_ax.c2p(0.5, 45), UP, 0.1)
        # zeta on the critical line
        ax = Axes(x_range=[-2, 4, 1], y_range=[-2.5, 2.5, 1], x_length=6.6, y_length=5.2,
                  axis_config={"color": GREY_C, "include_ticks": False})
        ax.shift(RIGHT * 2.2 + DOWN * 0.35)
        self.play(Create(strip_ax), FadeIn(strip), Create(crit), FadeIn(lab), Create(ax))
        tmax = 42
        ts = np.linspace(0, tmax, 2400)
        vals = [complex(mpmath.zeta(mpmath.mpc(0.5, t))) for t in ts]
        pts = [ax.c2p(v.real, v.imag) for v in vals]
        zeros = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719]
        tv = ValueTracker(0)
        curve = always_redraw(lambda: VMobject(stroke_color=MATH, stroke_width=3).set_points_as_corners(
            pts[:max(2, int(tv.get_value() / tmax * (len(pts) - 1)) + 1)]))
        pen = always_redraw(lambda: Dot(pts[int(tv.get_value() / tmax * (len(pts) - 1))], color=WHITE,
                                        radius=0.06))
        climb = always_redraw(lambda: Dot(strip_ax.c2p(0.5, tv.get_value()), color=WHITE, radius=0.05))
        ttext = always_redraw(lambda: MathTex(f"\\zeta\\!\\left(\\tfrac12 + {tv.get_value():.1f}\\,i\\right)",
                                              font_size=34).move_to(ax.c2p(-0.9, 2.2)))
        self.add(curve, pen, climb, ttext)
        self.say("Walk up the critical line and trace ζ. Every time it hits 0, we find a zero.")
        last = 0
        for zt in zeros:
            self.play(tv.animate.set_value(zt), run_time=(zt - last) / 7, rate_func=linear)
            self.play(Flash(ax.c2p(0, 0), color=PHYS, line_length=0.2, flash_radius=0.15),
                      FadeIn(Dot(strip_ax.c2p(0.5, zt), color=PHYS, radius=0.08), scale=2), run_time=0.45)
            last = zt
        self.play(tv.animate.set_value(tmax), run_time=0.4, rate_func=linear)
        self.say("Riemann, 1859: are ALL nontrivial zeros on this one line?", color=PHYS, wait=1.6)
        self.say("Checked for 10 trillion zeros. Never proved. It controls how primes are spread.",
                 wait=2.4)
        self.clear_all(keep_corner=False)


class S08d_Questions(Base):
    def construct(self):
        self.continue_chapter(*CH)
        qs = [
            ("P = NP ?", CODE, [-4.5, 2.4, 0]),
            ("Riemann Hypothesis", MATH, [3.3, 2.5, 0]),
            ("Why is there something, not nothing?", PHYS, [-0.4, 1.35, 0]),
            ("Quantum gravity", PHYS, [4.3, 0.3, 0]),
            ("Navier–Stokes smoothness", MATH, [-3.7, 0.15, 0]),
            ("What is dark matter?", PHYS, [3.6, -1.0, 0]),
            ("Fault-tolerant quantum computers", CODE, [-3.1, -1.35, 0]),
            ("Can machines truly understand?", CODE, [1.9, -2.3, 0]),
        ]
        mobs = []
        for text, col, pos in qs:
            m = T(text, 30, col, TITLE_FONT, weight=MEDIUM).move_to(np.array(pos, float))
            mobs.append(m)
        self.say("Some of the greatest questions are still wide open:")
        self.play(LaggedStart(*[FadeIn(m, scale=0.8) for m in mobs], lag_ratio=0.35), run_time=5)
        self.wait(1.2)
        self.play(*[m.animate.set_opacity(0.18) for m in mobs], run_time=1)
        big = T("Why does mathematics describe\nthe universe at all?", 44, WHITE, TITLE_FONT,
                weight=BOLD, line_spacing=1.2)
        bb = BackgroundRectangle(big, color=BG, fill_opacity=0.85, buff=0.35, corner_radius=0.15)
        self.play(FadeIn(bb), FadeIn(big, scale=1.1), run_time=1.5)
        self.wait(2.5)
        self.clear_all(keep_corner=False)
