from style import *


# ---------------------------------------------------------------- helpers
def glow_text(s, color, size=96, font=MONO):
    t = Text(s, font=font, font_size=size, color=color, weight=BOLD)
    h = t.copy().set_fill(opacity=0).set_stroke(color, width=12, opacity=0.22)
    return VGroup(h, t)


def P3(x, y):
    return np.array([x, y, 0.0])


def rigid_move(mob, R, R2, ang, run_time):
    """Rigid motion of a polygon: rotate by ang about R while R travels to R2."""
    start = mob.copy()

    def f(m, a):
        m.become(start.copy().rotate(ang * a, about_point=R).shift((R2 - R) * a))
    return UpdateFromAlphaFunc(mob, f, run_time=run_time, rate_func=smooth)


def rls(tri):
    """(right-angle vertex, end of the length-4 leg, end of the length-3 leg)."""
    for i in range(3):
        R = tri[i]
        a, b = tri[(i + 1) % 3], tri[(i + 2) % 3]
        da, db = np.linalg.norm(a - R), np.linalg.norm(b - R)
        if abs(da - 4) < 1e-6 and abs(db - 3) < 1e-6:
            return R, a, b
        if abs(db - 4) < 1e-6 and abs(da - 3) < 1e-6:
            return R, b, a
    raise ValueError("not a 3-4-5 triangle")


# ---- logic gate symbols (unit size, centred on origin) ---------------------
def _neon_parts(parts, color=MAGENTA, w=3.5):
    g = VGroup(*parts)
    for m in g:
        neon(m, color, w)
    return g


def and_gate():
    return _neon_parts([
        Line(P3(-0.6, 0.55), P3(0, 0.55)),
        Arc(radius=0.55, start_angle=PI / 2, angle=-PI, arc_center=ORIGIN),
        Line(P3(0, -0.55), P3(-0.6, -0.55)),
        Line(P3(-0.6, -0.55), P3(-0.6, 0.55)),
    ])


def _or_parts():
    return [
        CubicBezier(P3(-0.6, 0.55), P3(-0.25, 0.2), P3(-0.25, -0.2), P3(-0.6, -0.55)),
        CubicBezier(P3(-0.6, 0.55), P3(0, 0.55), P3(0.4, 0.3), P3(0.65, 0)),
        CubicBezier(P3(-0.6, -0.55), P3(0, -0.55), P3(0.4, -0.3), P3(0.65, 0)),
    ]


def or_gate():
    return _neon_parts(_or_parts())


def xor_gate():
    extra = CubicBezier(P3(-0.8, 0.55), P3(-0.45, 0.2), P3(-0.45, -0.2), P3(-0.8, -0.55))
    return _neon_parts(_or_parts() + [extra])


def not_gate():
    tri = Polygon(P3(-0.5, 0.5), P3(-0.5, -0.5), P3(0.5, 0))
    bub = Circle(radius=0.1).move_to(P3(0.6, 0))
    return _neon_parts([tri, bub])


def wire(pts, lit=False):
    m = VMobject()
    m.set_points_as_corners([np.array([p[0], p[1], 0.0]) for p in pts])
    if lit:
        neon(m, MAGENTA, 3.5)
    else:
        m.set_stroke(DIM, width=2.5, opacity=0.9)
    return m


class Act1(FilmScene):
    DURATION = BUDGET["act1"]

    def construct(self):
        self.tag("01", "BASICS", WHITE_, start=0.3, dur=3.6)
        self.math_part()
        self.physics_part()
        self.cs_part()
        self.fade_all(0.7)
        self.pad_to()

    # =====================================================================
    # MATHEMATICS  (gold)
    # =====================================================================
    def math_part(self):
        self.caption("First, we learn to count, and to measure.", start=0.4, dur=1.9)

        # ---- pi : the circle rolls out into a line --------------------
        r, yb, x0 = 0.8, 0.3, -5.0
        Cc = TAU * r
        base = Line(P3(-5.9, yb), P3(1.2, yb)).set_stroke(DIM, width=2, opacity=0.8)
        circ = Circle(radius=r).move_to(P3(x0, yb + r))
        neon(circ, GOLD, 3.5)
        center0 = P3(x0, yb + r)
        spoke = Line(center0 + DOWN * r, center0 + UP * r).set_stroke(WHITE_, width=2.5, opacity=0.7)
        rim = glow_dot(center0 + DOWN * r, GOLD, r=0.06)
        trace = Line(P3(x0, yb), P3(x0 + 0.001, yb))
        neon(trace, GOLD, 4.5)
        roll_grp = VGroup(circ, spoke, rim, trace)

        self.play(FadeIn(base), FadeIn(circ), FadeIn(spoke), FadeIn(rim), run_time=0.4)  # 0.4

        def roll(m, a):
            th = TAU * a
            c = center0 + RIGHT * r * th
            ang = -PI / 2 - th
            v = r * np.array([np.cos(ang), np.sin(ang), 0])
            circ.move_to(c)
            spoke.put_start_and_end_on(c + v, c - v)
            rim.move_to(c + v)
            trace.put_start_and_end_on(P3(x0, yb), P3(x0 + max(r * th, 0.001), yb))

        self.play(UpdateFromAlphaFunc(roll_grp, roll, run_time=1.4, rate_func=smooth))

        # three diameters ... and a bit
        self.caption("A circle's edge is always π times its width.", start=2.3 - self.renderer.time, dur=2.3)
        yb2 = -0.65
        bars, dlabs = VGroup(), VGroup()
        for i in range(3):
            b = Line(P3(x0 + 1.6 * i + 0.03, yb2), P3(x0 + 1.6 * (i + 1) - 0.03, yb2))
            neon(b, GOLD if i % 2 == 0 else "#FFE08A", 4.5)
            bars.add(b)
            dl = MathTex("d", color=GOLD).scale(0.6).move_to(P3(x0 + 1.6 * i + 0.8, yb2 - 0.4))
            dlabs.add(dl)
        sliver = Line(P3(x0 + 4.8 + 0.03, yb2), P3(x0 + Cc, yb2))
        neon(sliver, WHITE_, 6.0)
        self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.35),
                  LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in dlabs], lag_ratio=0.35),
                  run_time=0.8)                                                # 3.2
        sl_c = sliver.get_center()
        self.play(Create(sliver), Flash(sl_c, color=WHITE_, flash_radius=0.3, line_length=0.15, run_time=0.4),
                  run_time=0.3)                                                # 3.6

        eq = MathTex(r"\pi=", "3", ".", "1", "4", "1", "5", "9", r"\ldots").scale(1.3)
        eq.move_to(P3(2.9, yb2))
        eq[0].set_color(GOLD)
        for m in eq[1:]:
            m.set_color(WHITE_)
        eq[0].set_opacity(0)
        digs = list(eq[1:])
        for d in digs:
            d.save_state()
            d.move_to(sl_c).scale(0.2).set_opacity(0)
        self.add(eq)
        self.play(eq[0].animate.set_opacity(1), run_time=0.2)                  # 3.9
        self.play(LaggedStart(*[Restore(d, path_arc=-0.6) for d in digs], lag_ratio=0.22),
                  run_time=1.1)                                                # 5.2
        pi_all = VGroup(base, circ, spoke, rim, trace, bars, dlabs, sliver, eq)
        self.play(FadeOut(pi_all), run_time=0.3)                                # 5.8

        # ---- Pythagoras: moving-pieces proof --------------------------
        self.caption("Squares on the sides of a right triangle add up.", start=0.1, dur=4.0)
        k = 0.5
        BL = P3(-2.6 - 3.5 * k, 0.6 - 3.5 * k)

        def sc(p):
            return BL + k * np.array([p[0], p[1], 0.0])

        def poly(pts, col, fo, sw=3.0, z=0):
            pg = Polygon(*[sc(p) for p in pts])
            pg.set_fill(col, fo)
            pg.set_stroke(col, width=sw, opacity=1)
            pg.set_z_index(z)
            return pg

        PALE = "#FFE9A8"
        frame = Polygon(*[sc(p) for p in [P3(0, 0), P3(7, 0), P3(7, 7), P3(0, 7)]])
        frame.set_stroke(WHITE_, width=1.5, opacity=0.45)
        starts = [[P3(0, 0), P3(4, 0), P3(0, 3)], [P3(7, 0), P3(7, 4), P3(4, 0)],
                  [P3(7, 7), P3(3, 7), P3(7, 4)], [P3(0, 7), P3(0, 3), P3(3, 7)]]
        targets = [[P3(0, 0), P3(3, 0), P3(3, 4)], [P3(3, 4), P3(3, 7), P3(7, 4)],
                   [P3(7, 7), P3(3, 7), P3(7, 4)], [P3(0, 0), P3(0, 4), P3(3, 4)]]
        tris = [poly(t, GOLD, 0.42, 3.0, 2) for t in starts]
        c2 = poly([P3(4, 0), P3(7, 4), P3(3, 7), P3(0, 3)], WHITE_, 0.16, 2.5, 1)
        c2lab = MathTex("c^2", color=WHITE_).scale(1.1).move_to(sc(P3(3.5, 3.5)))
        l4 = MathTex("4", color=WHITE_).scale(0.6).move_to(sc(P3(2.0, 0.45)))
        l3 = MathTex("3", color=WHITE_).scale(0.6).move_to(sc(P3(0.45, 1.5)))
        l5 = MathTex("5", color=WHITE_).scale(0.6).move_to(sc(P3(2.35, 1.95)))
        legs = VGroup(l3, l4, l5)

        self.play(FadeIn(frame), LaggedStart(*[FadeIn(t) for t in tris], lag_ratio=0.2), run_time=0.6)
        self.play(FadeIn(c2), FadeIn(c2lab), FadeIn(legs), run_time=0.5)                                   # +1.3
        self.wait(0.2)

        a2 = poly([P3(0, 4), P3(3, 4), P3(3, 7), P3(0, 7)], GOLD, 0.3, 2.5, 0)
        b2 = poly([P3(3, 0), P3(7, 0), P3(7, 4), P3(3, 4)], PALE, 0.3, 2.5, 0)
        a2lab = MathTex("a^2", color=GOLD).scale(1.0).move_to(sc(P3(1.5, 5.5)))
        b2lab = MathTex("b^2", color=PALE).scale(1.1).move_to(sc(P3(5.0, 2.0)))

        moves = []
        for t, s, g in zip(tris, starts, targets):
            R, L, S = rls(s)
            R2, L2, S2 = rls(g)
            ang = np.arctan2(*(L2 - R2)[[1, 0]]) - np.arctan2(*(L - R)[[1, 0]])
            # sanity: chirality must match so the piece maps rigidly
            assert np.allclose(
                R2 + np.array([[np.cos(ang), -np.sin(ang), 0], [np.sin(ang), np.cos(ang), 0], [0, 0, 1]]) @ (S - R),
                S2, atol=1e-6), "chirality mismatch"
            moves.append(rigid_move(t, sc(R), sc(R2), ang, 1.4))
        self.play(*moves,
                  FadeOut(c2, run_time=0.5), FadeOut(c2lab, run_time=0.5), FadeOut(legs, run_time=0.5),
                  Succession(Wait(0.8), AnimationGroup(FadeIn(a2, run_time=0.6), FadeIn(b2, run_time=0.6),
                                                       FadeIn(a2lab, run_time=0.6), FadeIn(b2lab, run_time=0.6))))  # +3.1

        e1 = MathTex("a^2", "+", "b^2", "=", "c^2").scale(1.5).move_to(P3(3.6, 0.9))
        e1[0].set_color(GOLD)
        e1[2].set_color(PALE)
        e1[4].set_color(WHITE_)
        e2 = MathTex("9", "+", "16", "=", "25").scale(1.15).move_to(P3(3.6, -0.3))
        e2[0].set_color(GOLD)
        e2[2].set_color(PALE)
        e2[4].set_color(WHITE_)
        self.play(FadeIn(e1, shift=UP * 0.15), run_time=0.5)                                              # +3.7
        self.play(FadeIn(e2, shift=UP * 0.15), run_time=0.4)
        self.wait(0.2)
        self.play(*[FadeOut(m) for m in [frame, a2, b2, a2lab, b2lab, e1, e2, *tris]], run_time=0.3)  # +4.9

    # =====================================================================
    # PHYSICS  (cyan)
    # =====================================================================
    def physics_part(self):
        self.caption("Throw a ball: a parabola. Throw it fast enough: an orbit.", start=0.1, dur=6.6)

        # ---- stroboscopic parabola ------------------------------------
        H = 3.2

        def par(t):
            return P3(-5.2 + 10.4 * t, -1.7 + 4 * H * t * (1 - t))

        ground = Line(P3(-6.2, -1.7), P3(6.2, -1.7)).set_stroke(DIM, width=2, opacity=0.8)
        trace = ParametricFunction(lambda t: par(t), t_range=[0, 1, 0.01])
        trace = DashedVMobject(trace.set_stroke(CYAN, width=2.5, opacity=0.7), num_dashes=46)
        n = 10
        T = 1.8
        ghosts = [glow_dot(par(i / n), CYAN, r=0.07) for i in range(n + 1)]
        ball = glow_dot(par(0), WHITE_, r=0.09)
        self.play(FadeIn(ground), run_time=0.3)                                                            # 0.3
        anims = [UpdateFromAlphaFunc(ball, lambda m, a: m.move_to(par(a)), run_time=T, rate_func=linear),
                 Create(trace, run_time=T, rate_func=linear)]
        for i, g in enumerate(ghosts):
            fi = FadeIn(g, scale=0.5, run_time=0.3)
            anims.append(fi if i == 0 else Succession(Wait(T * i / n), fi))
        self.add(ball)
        self.play(AnimationGroup(*anims))                                                                  # 2.6
        self.play(FadeOut(VGroup(ground, trace, ball, *ghosts)), run_time=0.3)                             # 3.0

        # ---- Newton's cannon + the Moon --------------------------------
        c = P3(0, 0.05)
        R = 1.1
        earth = Circle(radius=R).move_to(c)
        earth.set_fill("#0C2B48", 1)
        neon(earth, CYAN, 3.5)
        halo = Circle(radius=R + 0.14).move_to(c).set_stroke(CYAN, width=6, opacity=0.12)
        lat = VGroup(Ellipse(width=2 * R, height=0.7).move_to(c), Ellipse(width=1.2, height=2 * R).move_to(c))
        lat.set_stroke(CYAN, width=1.5, opacity=0.3)
        S = c + UP * (R + 0.35)
        tower = Line(c + UP * R, S).set_stroke(WHITE_, width=3)
        planet = VGroup(halo, earth, lat, tower)
        self.play(FadeIn(planet, scale=0.8), run_time=0.4)                                                 # 3.5

        def rad(deg):
            return np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg)), 0])

        def shot(end_deg, ext):
            E = c + R * rad(end_deg)
            p = CubicBezier(S, S + RIGHT * ext, E + rad(end_deg) * ext * (0.3 if ext < 1 else 0.9), E)
            return neon(p, CYAN, 2.5)

        p1, p2 = shot(55, 0.6), shot(-5, 1.4)
        b1 = glow_dot(S, WHITE_, r=0.07)
        self.add(b1)
        self.play(MoveAlongPath(b1, p1, run_time=0.55), Create(p1, run_time=0.55))                          # 4.05
        b2 = glow_dot(S, WHITE_, r=0.07)
        self.add(b2)
        self.play(FadeOut(b1, run_time=0.2), MoveAlongPath(b2, p2, run_time=0.75), Create(p2, run_time=0.75))  # 4.8

        ro = R + 0.35

        def ring(t, rr=ro, ph=0.0):
            return c + rr * P3(np.sin(TAU * t + ph), np.cos(TAU * t + ph))

        orbit = ParametricFunction(lambda t: ring(t), t_range=[0, 1, 0.01])
        neon(orbit, CYAN, 3.0)
        b3 = glow_dot(S, WHITE_, r=0.07)
        self.add(b3)
        moon_orb = DashedVMobject(Circle(radius=2.5).move_to(c).set_stroke(CYAN, width=2.5, opacity=0.6),
                                  num_dashes=64)
        moon = glow_dot(ring(0, 2.5, 0.9), "#DDE7FF", r=0.11)
        self.play(FadeOut(b2, run_time=0.2), FadeIn(moon_orb, run_time=0.5), FadeIn(moon, run_time=0.5),
                  MoveAlongPath(b3, orbit, run_time=1.6, rate_func=linear), Create(orbit, run_time=1.6, rate_func=linear),
                  UpdateFromAlphaFunc(moon, lambda m, a: m.move_to(ring(0, 2.5, 0.9 + 2.2 * a)),
                                      run_time=1.8, rate_func=linear))                                       # 6.6
        self.wait(0.1)
        everything = [planet, p1, p2, orbit, b3, moon_orb, moon]
        self.play(*[FadeOut(m) for m in everything], run_time=0.3)                                          # 7.3

    # =====================================================================
    # COMPUTER SCIENCE  (magenta)
    # =====================================================================
    def cs_part(self):
        self.caption("Two symbols, 0 and 1, are enough to compute.", start=0.1, dur=7.2)

        # ---- two bits -> 1011 = 11 ------------------------------------
        b0 = glow_text("0", MAGENTA, 110).move_to(P3(-1.3, 0.7))
        b1 = glow_text("1", MAGENTA, 110).move_to(P3(1.3, 0.7))
        off = label("off", DIM, 22).move_to(P3(-1.3, -0.35))
        on = label("on", DIM, 22).move_to(P3(1.3, -0.35))
        self.play(FadeIn(b0, scale=0.6), FadeIn(b1, scale=0.6), FadeIn(off), FadeIn(on), run_time=0.7)      # 0.7

        xs = [-3.0, -1.8, -0.6, 0.6]
        row_y = 0.7
        n1 = glow_text("1", MAGENTA, 110).move_to(P3(xs[2], row_y))
        n2 = glow_text("1", MAGENTA, 110).move_to(P3(xs[3], row_y))
        self.play(b1.animate.move_to(P3(xs[0], row_y)), b0.animate.move_to(P3(xs[1], row_y)),
                  TransformFromCopy(b1, n1), TransformFromCopy(b1, n2),
                  FadeOut(off), FadeOut(on), run_time=0.8)                                                  # 1.5
        vals = VGroup(*[label(v, WHITE_ if v != "4" else DIM, 26).move_to(P3(x, -0.3))
                        for v, x in zip(["8", "4", "2", "1"], xs)])
        eq = MathTex(r"=\,11", color=WHITE_).scale(1.7).move_to(P3(2.6, row_y))
        self.play(FadeIn(vals, shift=UP * 0.1), Write(eq), run_time=0.7)                                    # 2.2
        self.wait(0.2)
        bits = VGroup(b0, b1, n1, n2, vals, eq)

        # ---- gates AND / OR / NOT ------------------------------------
        gy = 0.6
        gates = []
        for gx, mk, name in [(-4.2, and_gate, "AND"), (0.0, or_gate, "OR"), (4.2, not_gate, "NOT")]:
            g = mk().shift(P3(gx, gy))
            nm = label(name, WHITE_, 22).move_to(P3(gx, gy - 1.0))
            gates.append((g, nm))
        # wires (dim) and lit copies
        def w(pts, lit=False):
            return wire(pts, lit)
        and_in = [[(-5.6, gy + .28), (-4.8, gy + .28)], [(-5.6, gy - .28), (-4.8, gy - .28)]]
        and_out = [(-3.65, gy), (-2.9, gy)]
        or_in = [[(-1.4, gy + .28), (-0.55, gy + .28)], [(-1.4, gy - .28), (-0.55, gy - .28)]]
        or_out = [(0.65, gy), (1.3, gy)]
        not_in = [(2.9, gy), (3.7, gy)]
        not_out = [(4.9 + 0.0, gy), (5.7, gy)]
        dim_wires = VGroup(*[w(p) for p in and_in + [and_out] + or_in + [or_out] + [not_in, not_out]])
        lit_in = VGroup(w(and_in[0], True), w(and_in[1], True), w(or_in[0], True))
        lit_out = VGroup(w(and_out, True), w(or_out, True), w(not_out, True))
        gate_grp = VGroup(*[g for g, _ in gates], *[nm for _, nm in gates])
        self.play(FadeOut(bits, run_time=0.3),
                  LaggedStart(*[FadeIn(m) for m in [dim_wires, *[g for g, _ in gates], *[nm for _, nm in gates]]],
                              lag_ratio=0.08, run_time=0.7))                                                # 3.4
        self.play(LaggedStart(*[Create(m) for m in lit_in], lag_ratio=0.1, run_time=0.4))                   # 3.9
        self.play(LaggedStart(*[Create(m) for m in lit_out], lag_ratio=0.15, run_time=0.45))                 # 4.5
        self.wait(0.2)
        self.play(FadeOut(VGroup(dim_wires, lit_in, lit_out, gate_grp)), run_time=0.3)                      # 5.2

        # ---- half adder: 1 + 1 = 10 -----------------------------------
        s = 1.4
        xg, yx, ya = 0.6, 1.3, -0.8
        xor = xor_gate().scale(s, about_point=ORIGIN).shift(P3(xg, yx))
        andg = and_gate().scale(s, about_point=ORIGIN).shift(P3(xg, ya))
        xor_nm = label("XOR", WHITE_, 20).move_to(P3(xg, yx + 1.0))
        and_nm = label("AND", WHITE_, 20).move_to(P3(xg, ya - 1.0))
        xi = -0.25
        yA, yB = yx + 0.39, yx - 0.39
        aA, aB = ya + 0.39, ya - 0.39
        x_src = -4.7
        jA, jB = -3.2, -2.3
        railA = [(x_src, yA), (xi, yA)]
        railB = [(x_src, yB), (xi, yB)]
        dropA = [(jA, yA), (jA, aA), (xi, aA)]
        dropB = [(jB, yB), (jB, aB), (xi, aB)]
        x_out = xg + 0.77
        outS = [(xg + 0.91, yx), (2.8, yx)]
        outC = [(x_out, ya), (2.8, ya)]
        dimw = VGroup(*[w(p) for p in [railA, railB, dropA, dropB, outS, outC]])
        litw_in = [w(railA, True), w(railB, True), w(dropA, True), w(dropB, True)]
        litw_c = w(outC, True)
        srcA = glow_text("1", MAGENTA, 46).move_to(P3(-5.3, yA))
        srcB = glow_text("1", MAGENTA, 46).move_to(P3(-5.3, yB))
        lA = label("A", DIM, 22).move_to(P3(-6.0, yA))
        lB = label("B", DIM, 22).move_to(P3(-6.0, yB))
        jd = VGroup(Dot(P3(jA, yA), radius=0.05, color=MAGENTA), Dot(P3(jB, yB), radius=0.05, color=MAGENTA))
        self.play(FadeIn(dimw), FadeIn(xor), FadeIn(andg), FadeIn(xor_nm), FadeIn(and_nm),
                  FadeIn(srcA), FadeIn(srcB), FadeIn(lA), FadeIn(lB), run_time=0.6)                         # 5.9
        self.play(LaggedStart(*[Create(m) for m in litw_in], lag_ratio=0.15), FadeIn(jd), run_time=0.5)      # 6.6
        dark = interpolate_color(ManimColor(MAGENTA), ManimColor(BG), 0.6)
        sumb = glow_text("0", dark, 46).move_to(P3(3.3, yx))
        carb = glow_text("1", MAGENTA, 46).move_to(P3(3.3, ya))
        sl = label("sum", DIM, 20).move_to(P3(3.3, yx - 0.55))
        cl = label("carry", DIM, 20).move_to(P3(3.3, ya - 0.55))
        self.play(Create(litw_c), FadeIn(sumb, scale=0.7), FadeIn(sl), run_time=0.4)                         # 7.1
        self.play(FadeIn(carb, scale=0.7), FadeIn(cl), run_time=0.25)                                         # 7.4
        res = MathTex(r"1+1=", r"10_2").scale(0.95).move_to(P3(5.35, 0.25))
        res[1].set_color(MAGENTA)
        self.play(Write(res), run_time=0.7)
        self.wait(1.4)                                                                  # 8.1
