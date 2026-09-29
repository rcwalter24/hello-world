from style import *
import numpy as np

E_COL = CYAN
B_COL = "#7C8CFF"
RED_Q = "#FF4D5A"


def _tp(z):
    return np.array([z.real, z.imag, 0.0])


def _smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


class Epi(VGroup):
    """Chain of rotating circles (Fourier epicycles).  coefs are in world units,
    freqs in turns per unit of t.  Arm i fades in as `n` passes i."""

    def __init__(self, freqs, coefs, base, color=GOLD, circ_op=0.35, line_op=0.8, sw=1.6):
        super().__init__()
        self.freqs = np.array(freqs, float)
        self.coefs = np.array(coefs, complex)
        self.base = complex(base[0], base[1])
        self.circ_op, self.line_op = circ_op, line_op
        self.circles = VGroup(*[Circle(radius=max(abs(c), 1e-3), stroke_width=sw, color=color)
                                for c in self.coefs])
        self.lines = VGroup(*[Line(ORIGIN, RIGHT * 0.01, stroke_width=sw + 0.8, color=color)
                              for _ in self.coefs])
        self.add(self.circles, self.lines)

    def alphas(self, n):
        return np.clip(n - np.arange(len(self.coefs)), 0, 1)

    def joints(self, t, n):
        a = self.alphas(n)
        terms = a * self.coefs * np.exp(TAU * 1j * self.freqs * t)
        return self.base + np.concatenate([[0], np.cumsum(terms)]), a

    def tips(self, ts, n):
        a = self.alphas(n)
        z = (a * self.coefs)[None, :] * np.exp(TAU * 1j * np.outer(ts, self.freqs))
        return self.base + z.sum(axis=1)

    def refresh(self, t, n, vis=1.0):
        pts, a = self.joints(t, n)
        for i in range(len(self.coefs)):
            self.circles[i].move_to(_tp(pts[i]))
            self.lines[i].set_points_as_corners([_tp(pts[i]), _tp(pts[i + 1])])
            self.circles[i].set_stroke(opacity=a[i] * vis * self.circ_op)
            self.lines[i].set_stroke(opacity=a[i] * vis * self.line_op)
        return pts[-1]


class Act3(FilmScene):
    DURATION = BUDGET["act3"]

    def mark(self, s):
        print(f"[act3] {s}: t={self.renderer.time:.2f}")

    # =====================================================================
    # MATH  (gold)
    # =====================================================================
    def math(self):
        self.tag("03", "UNIVERSITY", WHITE_, start=0.3, dur=3.6)
        self.caption("Any motion is a sum of simple rotations.", start=0.9, dur=6.3)

        # ---- (a) square wave from 6 circles --------------------------------
        base = (-4.2, 0.3)
        x0 = -1.9
        ns = np.array([1, 3, 5, 7, 9, 11])
        sq = Epi(ns, 1.4 / ns, base, GOLD, circ_op=0.55, line_op=0.95, sw=2.0)
        th = ValueTracker(0.0)
        nact = ValueTracker(1.0)
        vis = ValueTracker(0.0)

        axis = Line([x0, base[1], 0], [6.4, base[1], 0], stroke_width=1.5, color=DIM)
        conn = DashedLine(ORIGIN, RIGHT, stroke_width=1.6, color=GOLD, dash_length=0.08)
        wave = VMobject()
        neon(wave, GOLD, 4.0)
        tipdot = glow_dot(ORIGIN, GOLD, r=0.07)

        def upd_sq(_m):
            v = vis.get_value()
            thv = th.get_value()
            tip = sq.refresh(thv / TAU, nact.get_value(), v)
            tipdot.move_to(_tp(tip))
            if thv > 0.05:
                tau = np.linspace(0, thv, 260)
                z = sq.tips(tau / TAU, nact.get_value())
                xs = x0 + (thv - tau) * 0.55
                wave.set_points_as_corners(np.stack([xs, z.imag, np.zeros_like(xs)], axis=1))
            wave.set_stroke(opacity=v, background=False)
            wave.set_stroke(opacity=0.18 * v, background=True)
            conn.put_start_and_end_on(_tp(tip), np.array([x0, tip.imag, 0]))
            conn.set_stroke(opacity=0.55 * v)
            axis.set_stroke(opacity=v)

        driver = VMobject()
        driver.add_updater(upd_sq)
        self.add(driver, axis, sq, conn, wave, tipdot)
        upd_sq(None)
        self.play(vis.animate.set_value(1), FadeIn(tipdot), run_time=0.3)              # 0.3
        self.play(th.animate.set_value(4 * PI), nact.animate.set_value(6.99),
                  run_time=2.5, rate_func=linear)                                       # 2.8
        self.play(vis.animate.set_value(0), FadeOut(tipdot), run_time=0.4)              # 3.2
        driver.clear_updaters()
        self.remove(driver, sq, conn, wave, axis)

        # ---- (b) heart with 40 arms via FFT --------------------------------
        N = 256
        s = np.linspace(0, TAU, N, endpoint=False)
        path = 16 * np.sin(s) ** 3 + 1j * (13 * np.cos(s) - 5 * np.cos(2 * s)
                                            - 2 * np.cos(3 * s) - np.cos(4 * s))
        cf = np.fft.fft(path) / N
        fr = np.fft.fftfreq(N, 1.0 / N).astype(int)
        keep = [i for i in range(N) if fr[i] != 0 and abs(fr[i]) <= 20]
        keep.sort(key=lambda i: (abs(fr[i]), -fr[i]))       # low frequency first
        sc = 0.155
        heart = Epi([fr[i] for i in keep], [cf[i] * sc for i in keep], (0.0, 0.45),
                    GOLD, circ_op=0.42, line_op=0.8, sw=1.5)
        t2 = ValueTracker(-0.15)
        n2 = ValueTracker(1.0)
        v2 = ValueTracker(0.0)
        trail = VMobject()
        neon(trail, GOLD, 4.5)
        htip = glow_dot(ORIGIN, GOLD, r=0.08)
        Ppts = heart.tips(np.linspace(0, 1, 361), 99)

        def upd_h(_m):
            tip = heart.refresh(t2.get_value(), n2.get_value(), v2.get_value())
            htip.move_to(_tp(tip))
            k = int(max(t2.get_value(), 0) * 360) + 1
            if k > 2:
                trail.set_points_as_corners(
                    np.stack([Ppts.real[:k], Ppts.imag[:k], np.zeros(k)], axis=1))

        driver2 = VMobject()
        driver2.add_updater(upd_h)
        self.add(driver2, heart, trail, htip)
        upd_h(None)
        self.play(v2.animate.set_value(1), FadeIn(htip), run_time=0.2)                  # 3.4
        self.play(n2.animate.set_value(40), t2.animate.set_value(0.0),
                  run_time=0.9, rate_func=linear)                                       # 4.3
        self.play(t2.animate.set_value(1.0), run_time=3.0, rate_func=linear)            # 7.3
        self.play(v2.animate.set_value(0), FadeOut(htip), run_time=0.4)                 # 7.7
        driver2.clear_updaters()
        self.remove(driver2, heart)
        self.mark("heart done")

        # ---- (c) Euler's identity ------------------------------------------
        self.caption("Five constants. One equation.", start=0.2, dur=3.6)
        cols = ["#F5C451", "#FF9F43", "#FFD98A", "#FFF3C4", "#E9A23B"]
        syms = [r"e", r"i", r"\pi", r"1", r"0"]
        consts = VGroup(*[MathTex(sy, color=c).scale(2.6) for sy, c in zip(syms, cols)])
        for m, x in zip(consts, [-4.4, -2.2, 0, 2.2, 4.4]):
            m.move_to([x, 0.5, 0])
        self.play(FadeOut(trail),
                  LaggedStart(*[FadeIn(m, shift=UP * 0.3, scale=0.8) for m in consts],
                              lag_ratio=0.6, run_time=1.4))                             # 9.1

        eq = MathTex(r"{{e}}^{ {{i}} {{\pi}} } {{+}} {{1}} {{=}} {{0}}").scale(2.4)
        eq.move_to([0, 0.5, 0])
        for idx, c in zip([0, 2, 4, 8, 12], cols):
            eq[idx].set_color(c)
        for idx in (6, 10):
            eq[idx].set_color(WHITE_)
        pieces = [eq[0], eq[2], eq[4], eq[8], eq[12]]
        self.play(*[ReplacementTransform(consts[k], pieces[k]) for k in range(5)],
                  FadeIn(eq[6], shift=UP * 0.2), FadeIn(eq[10], shift=UP * 0.2),
                  run_time=0.9, rate_func=smooth)                                       # 10.0
        glow = eq.copy()
        glow.set_stroke(GOLD, width=9, opacity=0.5)
        glow.set_fill(GOLD, opacity=0.35)
        self.add(glow)
        self.play(FadeIn(glow, scale=1.03), run_time=0.3)                              # 10.3
        self.play(FadeOut(glow, scale=1.12), run_time=0.5)                             # 10.8
        self.wait(0.3)                                                                  # 11.1
        self.remove(glow)
        self.mark("math done")
        return eq

    # =====================================================================
    # PHYSICS  (cyan)
    # =====================================================================
    def physics(self, eq):
        self.caption("Electric and magnetic fields chase each other. That is light.",
                     start=0.8, dur=8.1)
        eqs = [r"\nabla\cdot\mathbf{E}=\frac{\rho}{\varepsilon_0}",
               r"\nabla\cdot\mathbf{B}=0",
               r"\nabla\times\mathbf{E}=-\frac{\partial\mathbf{B}}{\partial t}",
               r"\nabla\times\mathbf{B}=\mu_0\mathbf{J}+\mu_0\varepsilon_0\frac{\partial\mathbf{E}}{\partial t}"]
        maxw = VGroup(*[MathTex(e, color=CYAN) for e in eqs]).scale(0.95)
        maxw.arrange_in_grid(2, 2, buff=(0.9, 1.1), col_alignments="cc")
        maxw.move_to([0, 0.05, 0])
        maxw.set_opacity(0.14)

        yb = -0.05
        X0, X1 = -5.6, 5.8
        xs = np.linspace(X0, X1, 220)
        sx = np.linspace(X0 + 0.15, X1 - 0.15, 36)
        lam, spd, A = 3.1, 1.7, 1.25
        kk = TAU / lam
        D = np.array([0.62, 0.36, 0.0]) * 0.95
        WT = ValueTracker(0.0)
        vis = ValueTracker(0.0)

        def field(x, t):
            env = _smooth((x - X0) / 1.4) * _smooth((X1 - x) / 1.4)
            grow = _smooth(t / 1.6)
            return A * grow * env * np.sin(kk * x - kk * spd * t)

        axis = Arrow([-6.3, yb, 0], [6.6, yb, 0], buff=0, stroke_width=2, color=DIM,
                     max_tip_length_to_length_ratio=0.03, tip_length=0.18)
        depth = Line([X0 - 0.4, yb, 0], np.array([X0 - 0.4, yb, 0]) + D * 1.6,
                     stroke_width=1.5, color=DIM)
        Ec = VMobject()
        Bc = VMobject()
        neon(Ec, E_COL, 4.0)
        neon(Bc, B_COL, 4.0)
        Es = VGroup(*[Line(ORIGIN, RIGHT * 0.01, stroke_width=1.6, color=E_COL) for _ in sx])
        Bs = VGroup(*[Line(ORIGIN, RIGHT * 0.01, stroke_width=1.6, color=B_COL) for _ in sx])
        lblE = MathTex(r"\mathbf{E}", color=E_COL).scale(0.9).move_to([-6.2, 1.3, 0])
        lblB = MathTex(r"\mathbf{B}", color=B_COL).scale(0.9).move_to([-5.15, 0.8, 0])
        wave = VGroup(Es, Bs, Ec, Bc)

        def upd_w(_m):
            t = WT.get_value()
            v = vis.get_value()
            f = field(xs, t)
            Ec.set_points_as_corners(np.stack([xs, yb + f, np.zeros_like(xs)], axis=1))
            Bc.set_points_as_corners(np.stack([xs + D[0] * f, yb + D[1] * f, np.zeros_like(xs)], axis=1))
            fs = field(sx, t)
            for j in range(len(sx)):
                p0 = np.array([sx[j], yb, 0])
                Es[j].set_points_as_corners([p0, p0 + np.array([0, fs[j], 0])])
                Bs[j].set_points_as_corners([p0, p0 + D * fs[j]])
            for m in (Ec, Bc):
                m.set_stroke(opacity=v, background=False)
                m.set_stroke(opacity=0.18 * v, background=True)
            Es.set_stroke(opacity=0.32 * v)
            Bs.set_stroke(opacity=0.32 * v)

        driver = VMobject()
        driver.add_updater(upd_w)
        self.add(driver, wave)
        upd_w(None)

        self.play(FadeOut(eq), FadeIn(maxw), Create(axis), FadeIn(depth),
                  vis.animate.set_value(1), run_time=0.8)                                # 0.8
        self.play(FadeIn(lblE), FadeIn(lblB), WT.animate.set_value(0.5),
                  run_time=0.5, rate_func=linear)
        self.play(WT.animate.set_value(5.2), run_time=4.7, rate_func=linear)             # 6.0
        cl = MathTex(r"c", color=WHITE_).scale(3.2)
        cv = MathTex(r"=\,299\,792\,458\ \mathrm{m/s}", color=CYAN).scale(1.0)
        cg = VGroup(cl, cv).arrange(RIGHT, buff=0.3, aligned_edge=DOWN).move_to([0.6, 2.6, 0])
        cglow = cl.copy().set_stroke(CYAN, width=10, opacity=0.5).set_fill(CYAN, opacity=0.4)
        self.play(WT.animate.set_value(7.4), FadeIn(cg, shift=UP * 0.2), FadeIn(cglow),
                  run_time=1.3, rate_func=linear)                                        # 7.3
        self.play(WT.animate.set_value(9.5), FadeOut(cglow), run_time=2.1, rate_func=linear)   # 9.4
        self.mark("physics done")
        return [driver, wave, axis, depth, maxw, lblE, lblB, cg], driver

    # =====================================================================
    # COMPUTER SCIENCE  (magenta)
    # =====================================================================
    def cs(self, phys):
        objs, driver = phys
        # ---- Turing machine ------------------------------------------------
        self.caption("A machine that reads and writes symbols can compute anything computable.",
                     start=0.3, dur=3.5)
        n, cs_, y = 11, 0.85, 0.4
        cells = VGroup(*[Square(cs_, stroke_width=2.4, color=MAGENTA) for _ in range(n)])
        cells.arrange(RIGHT, buff=0).move_to([0, y, 0])
        for c in cells:
            c.set_stroke(MAGENTA, width=2.4, opacity=0.7)
            c.set_stroke(MAGENTA, width=7.5, opacity=0.14, background=True)
        init = ["", "1", "0", "1", "1", "0", "", "", "", "", ""]
        write = ["", "0", "1", "0", "0", "1", "", "", "", "", ""]
        symt = {}
        for i, sy in enumerate(init):
            if sy:
                symt[i] = Text(sy, font=MONO, font_size=40, color=WHITE_).move_to(cells[i])
        tri = Triangle(color=MAGENTA, fill_opacity=1).scale(0.16).rotate(PI)
        box = RoundedRectangle(width=1.0, height=0.55, corner_radius=0.13, color=MAGENTA,
                               stroke_width=2.5)
        state = Text("q0", font=MONO, font_size=24, color=WHITE_)
        head = VGroup(box, tri, state)
        tri.next_to(cells[1], UP, buff=0.06)
        box.next_to(tri, UP, buff=0.05)
        state.move_to(box)
        hint = label("read  ·  write  ·  move", DIM, 24).move_to([0, -0.85, 0])

        self.play(FadeOut(VGroup(*objs)),
                  LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.06, run_time=0.8),
                  FadeIn(VGroup(*symt.values())), FadeIn(head), FadeIn(hint),
                  run_time=0.8)                                                          # 0.8
        self.remove(*objs)
        driver.clear_updaters()
        names = ["q0", "q1"]
        for k in range(1, 6):
            new = Text(write[k], font=MONO, font_size=40, color=MAGENTA).move_to(cells[k])
            ns_ = Text(names[k % 2], font=MONO, font_size=24, color=WHITE_).move_to(state)
            self.play(Transform(symt[k], new), Transform(state, ns_),
                      cells[k].animate.set_fill(MAGENTA, 0.22), run_time=0.22)
            self.play(head.animate.shift(RIGHT * cs_), run_time=0.28, rate_func=smooth)
        halt = Text("HALT", font=MONO, font_size=22, color=WHITE_).move_to(state)
        self.play(Transform(state, halt), run_time=0.3)
        self.mark("tape done")                                                          # ~3.9
        self.wait(0.1)

        # ---- halting problem ----------------------------------------------
        self.caption("Yet some questions no machine can answer.", start=0.2, dur=3.2)
        Hb = RoundedRectangle(width=1.7, height=1.1, corner_radius=0.16, color=MAGENTA,
                              stroke_width=4)
        Hb.set_stroke(MAGENTA, width=12, opacity=0.18, background=True)
        Hb.set_fill(MAGENTA, 0.1)
        Hb.move_to([0, -0.55, 0])
        Ht = Text("H", font=FONT, font_size=52, color=WHITE_, weight=BOLD).move_to(Hb)
        Hq = label("halts?", MAGENTA, 24).next_to(Hb, DOWN, buff=0.2)
        prog = Text("program", font=FONT, font_size=22, color=DIM).move_to([-4.2, -0.35, 0])
        pin = Arrow([-3.2, -0.55, 0], Hb.get_left() + LEFT * 0.05, buff=0, color=WHITE_,
                    stroke_width=3, tip_length=0.22, max_tip_length_to_length_ratio=0.3)
        self.play(FadeOut(cells), FadeOut(VGroup(*symt.values())), FadeOut(head), FadeOut(hint),
                  FadeIn(Hb), FadeIn(Ht), FadeIn(Hq), FadeIn(prog), Create(pin), run_time=0.5)  # 0.5
        loop = ArcBetweenPoints(Hb.get_right() + RIGHT * 0.02, Hb.get_left() + LEFT * 0.04,
                                angle=1.5 * PI)
        loop.set_stroke(MAGENTA, width=4)
        loop.set_stroke(MAGENTA, width=13, opacity=0.18, background=True)
        loop.add_tip(tip_length=0.28)
        self.play(Create(loop), FadeOut(prog), FadeOut(pin), run_time=1.1)             # 1.6
        runner = glow_dot(loop.point_from_proportion(0), MAGENTA, r=0.08)
        selfl = label("H runs on its own code", MAGENTA, 24).next_to(loop, UP, buff=0.18)
        q = Text("?", font=FONT, font_size=110, color=RED_Q, weight=BOLD)
        q.move_to(loop.get_center() + UP * 0.1)
        qg = q.copy().set_stroke(RED_Q, width=10, opacity=0.3)
        self.play(FadeIn(runner), FadeIn(selfl), run_time=0.2)                          # 1.8
        self.play(MoveAlongPath(runner, loop), run_time=0.9, rate_func=linear)          # 2.7
        self.play(FadeIn(q, scale=0.5), FadeIn(qg, scale=0.5), run_time=0.4)           # 3.1
        self.play(Indicate(q, scale_factor=1.15, color=RED_Q), run_time=0.5)           # 3.6
        self.mark("halting done")

        # ---- P vs NP -------------------------------------------------------
        self.caption("Easy to check. Hard to find?", start=0.2, dur=5.0)
        rng = np.random.RandomState(7)
        W, H_ = 4.2, 3.0
        layers = [1, 3, 4, 4, 3, 1]
        L = len(layers)
        pos = {}
        for l, cnt in enumerate(layers):
            ys = np.linspace(H_ / 2, -H_ / 2, cnt) if cnt > 1 else [0.0]
            for j in range(cnt):
                pos[(l, j)] = np.array([-W / 2 + l * W / (L - 1), ys[j], 0.0])
        sol = [(0, 0)] + [(l, int(rng.randint(layers[l]))) for l in range(1, L - 1)] + [(L - 1, 0)]
        edges = set(zip(sol[:-1], sol[1:]))
        for l in range(1, L - 1):
            for j in range(layers[l]):
                if (l, j) in sol:
                    continue
                nonsol = [(l + 1, jj) for jj in range(layers[l + 1]) if (l + 1, jj) not in sol]
                if l + 1 == L - 1 or not nonsol:
                    continue
                for tgt in rng.permutation(len(nonsol))[:1 + rng.randint(2)]:
                    edges.add(((l, j), nonsol[tgt]))
        for j in range(layers[1]):
            edges.add(((0, 0), (1, j)))
        # sol nodes also branch into dead ends
        for l in range(1, L - 2):
            nonsol = [(l + 1, jj) for jj in range(layers[l + 1]) if (l + 1, jj) not in sol]
            if nonsol:
                edges.add((sol[l], nonsol[rng.randint(len(nonsol))]))
        adj = {}
        for a, b in edges:
            adj.setdefault(a, []).append(b)
        # DFS order (solution child last) -> the order in which the slow search probes edges
        order = []

        def dfs(u):
            kids = sorted(adj.get(u, []), key=lambda v: (v in sol, rng.rand()))
            for v in kids:
                order.append((u, v))
                dfs(v)
        dfs((0, 0))

        def build(cx):
            off = np.array([cx, 0.35, 0])
            es = {e: Line(pos[e[0]] + off, pos[e[1]] + off, stroke_width=1.8, color=DIM)
                  for e in edges}
            for e in es.values():
                e.set_stroke(opacity=0.55)
            ns = VGroup(*[Dot(pos[k] + off, radius=0.1, color=DIM) for k in pos])
            ns[0].set_color(WHITE_)
            return es, ns, off

        esL, nsL, offL = build(-3.9)
        esR, nsR, offR = build(3.9)
        gL = VGroup(*esL.values(), nsL)
        gR = VGroup(*esR.values(), nsR)
        goalL = Circle(radius=0.22, color=WHITE_, stroke_width=2.5).move_to(pos[(L - 1, 0)] + offL)
        goalR = Circle(radius=0.22, color=WHITE_, stroke_width=2.5).move_to(pos[(L - 1, 0)] + offR)
        pnp = MathTex(r"\mathrm{P}\;\overset{?}{=}\;\mathrm{NP}", color=MAGENTA).scale(1.15)
        pnp.move_to([0, 0.35, 0])
        findL = VGroup(label("find", WHITE_, 34), label("slow", MAGENTA, 24)).arrange(DOWN, buff=0.12)
        findL.move_to([-3.9, -1.85, 0])
        chkR = VGroup(label("check", WHITE_, 34), label("fast", MAGENTA, 24)).arrange(DOWN, buff=0.12)
        chkR.move_to([3.9, -1.85, 0])

        self.play(FadeOut(VGroup(Hb, Ht, Hq, loop, runner, selfl, q, qg)),
                  FadeIn(gL), FadeIn(gR), FadeIn(goalL), FadeIn(goalR),
                  FadeIn(findL), FadeIn(chkR), FadeIn(pnp), run_time=0.6)               # 0.6
        flashes = []
        for e in order:
            f = esL[e].copy().set_stroke(MAGENTA, width=6, opacity=1.0)
            flashes.append(ShowPassingFlash(f, time_width=1.0))
        search = LaggedStart(*flashes, lag_ratio=0.07, run_time=2.7)
        solR = [esR[e] .copy().set_stroke(MAGENTA, width=6, opacity=1.0)
                for e in zip(sol[:-1], sol[1:])]
        for m in solR:
            neon(m, MAGENTA, 6.0)
        chk = MathTex(r"\checkmark", color=WHITE_).scale(1.1).next_to(goalR, RIGHT, buff=0.2)
        chk.shift(UP * 0.0)
        check = Succession(LaggedStart(*[Create(m) for m in solR], lag_ratio=0.5, run_time=0.7),
                           FadeIn(chk, run_time=0.25))
        self.play(AnimationGroup(search, check), run_time=2.7)                         # 3.3
        solL = [esL[e].copy() for e in zip(sol[:-1], sol[1:])]
        for m in solL:
            neon(m, MAGENTA, 6.0)
        self.play(LaggedStart(*[Create(m) for m in solL], lag_ratio=0.5, run_time=0.6),
                  goalL.animate.set_color(MAGENTA), run_time=0.6)                       # 3.9
        self.wait(1.1)
        self.mark("pnp done")

    # =====================================================================
    def construct(self):
        eq = self.math()          # ~11.1
        phys = self.physics(eq)   # ~ +8.5 (fade-out of eq overlaps)
        self.cs(phys)
        self.fade_all(0.7)
        self.pad_to()
