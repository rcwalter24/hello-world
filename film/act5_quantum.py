from style import *

# ===========================================================================
#  ACT 5 - QUANTUM   (28 s)      the concept where the earlier acts meet
#   rotation (act 1)  -> the phase of an amplitude (a rotating arrow)
#   least action (2)  -> only the shortest path survives (arrows cancel)
#   bits (act 3)      -> qubits, whose amplitudes interfere
#
#  A   0.0 -  7.0  MATH gold -> PHYSICS cyan   arrow / add arrows / path sum
#  B   7.0 - 13.0  PHYSICS                     double slit, one particle at a time
#  C  13.0 - 20.0  cyan -> magenta             Bloch sphere, qubits, interfering bars
#  D  20.0 - 28.0  all three                   holographic disk, braid converges
# ===========================================================================

STR_COLS = [GOLD, CYAN, MAGENTA]
STR_PH = [0.0, 2 * np.pi / 3, 4 * np.pi / 3]
P_ = 3.2
K_ = 2 * np.pi / P_
AMP = 0.80
Y0 = 0.10


def mix(a, b, t):
    return ManimColor(a).interpolate(ManimColor(b), float(np.clip(t, 0, 1)))


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def set_img(m, rgba):
    """Swap the pixels of an ImageMobject in place (keeps fades working)."""
    m.pixel_array = rgba
    m.orig_alpha_pixel_array = rgba[:, :, 3].copy()


def e2(th, r=1.0):
    return r * np.array([np.cos(th), np.sin(th), 0.0])


def arrow_between(a, b, col, w=5.0, tip=0.2):
    a = np.array(a, float)
    b = np.array(b, float)
    L = np.linalg.norm(b - a)
    if L < 0.13:
        return Dot(a, radius=0.035, color=col)
    ar = Arrow(a, b, buff=0, stroke_width=w, tip_length=min(tip, 0.42 * L),
               max_tip_length_to_length_ratio=1.0, max_stroke_width_to_length_ratio=100, color=col)
    ar.set_stroke(col, w * 3.2, opacity=0.16, background=True)
    return ar


# ---- rainbow (gold -> cyan -> magenta -> gold) around a circle -----------
def ring_colour(u):
    u = (u % 1.0) * 3
    i = int(u) % 3
    return mix(STR_COLS[i], STR_COLS[(i + 1) % 3], u - int(u))


# ---- double slit ----------------------------------------------------------
DS_D, DS_A = 2.35, 0.50           # d/(lambda L), a/(lambda L)  in 1/units
DS_HALF = 2.3


def ds_intensity(y):
    return np.cos(np.pi * DS_D * y) ** 2 * np.sinc(DS_A * y) ** 2


def ds_sample(n, rng):
    out = []
    while sum(len(o) for o in out) < n:
        y = rng.uniform(-DS_HALF, DS_HALF, 4 * n)
        keep = rng.uniform(0, 1, 4 * n) < ds_intensity(y)
        out.append(y[keep])
    return np.concatenate(out)[:n]


# ---- pseudo-3D helpers (Bloch sphere) --------------------------------------
def bloch_proj(p, R, c, az=-0.55, el=0.38):
    x, y, z = p
    xp = x * np.cos(az) - y * np.sin(az)
    yp = x * np.sin(az) + y * np.cos(az)
    depth = yp * np.cos(el) - z * np.sin(el)      # > 0 : far side
    sy = yp * np.sin(el) + z * np.cos(el)
    return np.array([c[0] + R * xp, c[1] + R * sy, 0.0]), depth


def sphere_curve(fn, c, R, color, lw=1.0, n=96, dim=0.2, front=0.65):
    proj = [bloch_proj(fn(t), R, c) for t in np.linspace(0, 2 * np.pi, n + 1)]
    g = VGroup(VMobject().set_points_as_corners([p for p, _ in proj]).set_stroke(color, 1.4 * lw, dim))
    run = []
    for p, d in proj + [(None, 1.0)]:
        if d <= 0:
            run.append(p)
        else:
            if len(run) > 1:
                g.add(VMobject().set_points_as_corners(run).set_stroke(color, 2.4 * lw, front))
            run = []
    return g


def sphere_group(c, R, lw=1.0, full=True):
    out = Circle(radius=R).move_to(c)
    neon(out, CYAN, 2.6 * lw)
    out.set_fill("#0A1428", 0.85)
    g = VGroup(out, sphere_curve(lambda t: (np.cos(t), np.sin(t), 0), c, R, CYAN, lw))
    if full:
        g.add(sphere_curve(lambda t: (np.cos(t), 0, np.sin(t)), c, R, CYAN, lw, dim=0.12, front=0.35))
        g.add(sphere_curve(lambda t: (0, np.cos(t), np.sin(t)), c, R, CYAN, lw, dim=0.12, front=0.35))
        a, _ = bloch_proj((0, 0, -1.22), R, c)
        b, _ = bloch_proj((0, 0, 1.22), R, c)
        g.add(Line(a, b).set_stroke(CYAN, 1.6, 0.5))
    return g


def state_vec(p, c, R, w=5.0, r=0.06, col=MAGENTA):
    tip, _ = bloch_proj(p, R, c)
    ln = Line(c, tip)
    neon(ln, col, w)
    return VGroup(ln, glow_dot(tip, col, r=r, layers=4), Dot(c, radius=0.03, color=WHITE_))


# ---- hyperbolic tiling -----------------------------------------------------
def _reflect(z, a, b):
    A = np.array([[a.real, a.imag], [b.real, b.imag]])
    if abs(np.linalg.det(A)) < 1e-9:                    # geodesic is a diameter
        u = a / abs(a)
        return u * u * np.conj(z)
    rhs = np.array([(abs(a) ** 2 + 1) / 2, (abs(b) ** 2 + 1) / 2])
    c = complex(*np.linalg.solve(A, rhs))               # centre of the circle orthogonal to |z|=1
    r2 = abs(c) ** 2 - 1
    return c + r2 / np.conj(z - c)


def _geodesic(a, b, n=14):
    A = np.array([[a.real, a.imag], [b.real, b.imag]])
    if abs(np.linalg.det(A)) < 1e-9:
        return [a + (b - a) * t for t in np.linspace(0, 1, n)]
    c = complex(*np.linalg.solve(A, np.array([(abs(a) ** 2 + 1) / 2, (abs(b) ** 2 + 1) / 2])))
    r = np.sqrt(abs(c) ** 2 - 1)
    a0, a1 = np.angle(a - c), np.angle(b - c)
    d = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi
    return [c + r * np.exp(1j * (a0 + d * t)) for t in np.linspace(0, 1, n)]


def hyperbolic_tiling(p=7, q=3, layers=4):
    """{p,q} tiling of the Poincare disk; returns list (per layer) of geodesic edges."""
    rv = np.sqrt(np.cos(np.pi / p + np.pi / q) / np.cos(np.pi / p - np.pi / q))
    V = [rv * np.exp(1j * (2 * np.pi * k / p + np.pi / p)) for k in range(p)]
    polys, cents, lay = [V], [np.mean(V)], [0]
    frontier = [0]
    for L in range(1, layers + 1):
        new = []
        for i in frontier:
            V = polys[i]
            for k in range(p):
                nv = [_reflect(z, V[k], V[(k + 1) % p]) for z in V]
                cc = np.mean(nv)
                if any(abs(cc - x) < 1e-7 for x in cents):
                    continue
                polys.append(nv); cents.append(cc); lay.append(L); new.append(len(polys) - 1)
        frontier = new
    seen, per_layer = set(), [[] for _ in range(layers + 1)]
    for poly, L in zip(polys, lay):
        for k in range(p):
            a, b = poly[k], poly[(k + 1) % p]
            key = frozenset([(round(a.real, 5), round(a.imag, 5)), (round(b.real, 5), round(b.imag, 5))])
            if key in seen:
                continue
            seen.add(key)
            per_layer[L].append(_geodesic(a, b, n=max(5, 14 - 3 * L)))
    return per_layer, len(polys)


def multipaths(arcs, centre, R, chunk=110):
    """Polylines (arcs = lists of complex numbers) packed into a few VMobjects (<~1500 pts each)."""
    out = []
    for i in range(0, len(arcs), chunk):
        vm = VMobject()
        for arc in arcs[i:i + chunk]:
            pts = [np.array([centre[0] + R * z.real, centre[1] + R * z.imag, 0.0]) for z in arc]
            vm.start_new_path(pts[0])
            vm.add_points_as_corners(pts[1:])
        out.append(vm)
    return out


# =============================================================================
class Act5(FilmScene):
    DURATION = BUDGET["act5"]

    def freeze(self, *mobs):
        for m in mobs:
            m.clear_updaters()

    def tri_badge(self, start, dur):
        """MATHEMATICS . PHYSICS . COMPUTER SCIENCE, each in its own colour."""
        parts = VGroup()
        for i, (t, c) in enumerate([("MATHEMATICS", GOLD), ("PHYSICS", CYAN), ("COMPUTER SCIENCE", MAGENTA)]):
            if i:
                parts.add(Text("·", font=FONT, font_size=18, color=DIM))
            parts.add(Text(t, font=FONT, font_size=18, color=c, weight=BOLD))
        parts.arrange(RIGHT, buff=0.16)
        parts.to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        return self._timed(parts, start, dur, fade=0.35, max_op=0.95)

    # ------------------------------------------------------------------
    def construct(self):
        # ------------------------------------------------------------ precompute
        rng = np.random.default_rng(11)
        NP = 2400
        ds_hits = ds_sample(NP, rng)
        ds_x = rng.uniform(0, 1, NP)
        ds_slit = rng.integers(0, 2, NP)
        per_layer, npoly = hyperbolic_tiling(7, 3, 4)

        # ------------------------------------------------ overlays (absolute times)
        self.tag("05", "QUANTUM", WHITE_, start=0.1, dur=3.6)
        self.badge("MATHEMATICS", GOLD, start=0.0, dur=2.75)
        self.badge("PHYSICS", CYAN, start=2.5, dur=13.5)          # -> 16.0
        self.badge("COMPUTER SCIENCE", MAGENTA, start=15.7, dur=4.6)   # -> 20.3
        self.tri_badge(start=20.0, dur=7.4)                       # -> 27.4
        self.level(1, GOLD, start=0.0, dur=2.75)
        self.level(2, CYAN, start=2.5, dur=10.8)                  # -> 13.3
        self.level(3, CYAN, start=13.0, dur=3.3)                  # -> 16.3
        self.level(3, MAGENTA, start=16.0, dur=4.3)               # -> 20.3
        self.level(3, WHITE_, start=20.0, dur=7.4)                # -> 27.4
        self.caption("Nature tries every path. Only the shortest survives.", start=1.0, dur=5.9)
        self.caption("One particle at a time, an interference pattern emerges.", start=7.4, dur=5.2)
        self.caption("Qubits put that interference to work.", start=13.5, dur=5.8)
        self.caption("A universe inside a disk, described entirely by its boundary.", start=20.4, dur=3.5)

        # =====================================================================
        # A1  0.0 - 2.2   a rotating arrow = a phase (the circle-point of act 1)
        # =====================================================================
        C0 = np.array([-1.0, -0.1, 0.0])
        R1 = 1.1
        th1 = ValueTracker(0.0)
        th2 = ValueTracker(0.0)
        k1 = ValueTracker(0.0)          # gold -> cyan
        col1 = lambda: mix(GOLD, CYAN, k1.get_value())

        cross = VGroup(Line(C0 + LEFT * 1.5, C0 + RIGHT * 1.5), Line(C0 + DOWN * 1.5, C0 + UP * 1.5))
        cross.set_stroke(DIM, 1.2, 0.55)
        fade = ValueTracker(0.0)        # always_redraw objects rebuild each frame: drive their opacity by a tracker
        phase_lbl = Text("phase", font=FONT, font_size=24, color=GOLD).move_to(C0 + np.array([2.55, 0.2, 0]))
        phase_lbl.add_updater(lambda m: m.set_color(col1()))
        circ = Circle(radius=R1).move_to(C0)

        def circ_upd(m):
            neon(m, col1(), 3.2)
            m.set_stroke(opacity=fade.get_value())
            m.set_stroke(opacity=0.18 * fade.get_value(), background=True)
        circ.add_updater(circ_upd)
        arrow1 = always_redraw(lambda: arrow_between(C0, C0 + e2(th1.get_value(), R1), col1()).set_opacity(fade.get_value()))
        tipdot = always_redraw(lambda: glow_dot(C0 + e2(th1.get_value(), R1), col1(), r=0.06, layers=4)
                               .scale(max(fade.get_value(), 1e-3)))
        arc = always_redraw(lambda: (Arc(radius=0.42, start_angle=0, angle=th1.get_value() % TAU,
                                         arc_center=C0, stroke_width=2.2, stroke_color=col1(),
                                         stroke_opacity=0.7 * fade.get_value())
                                     if th1.get_value() % TAU > 0.03 else VMobject()))
        cross.set_opacity(0)
        self.add(cross, circ, arrow1, tipdot, arc)
        phase_lbl.set_opacity(0)
        self.add(phase_lbl)
        self.play(AnimationGroup(
            fade.animate(run_time=0.6, rate_func=smooth).set_value(1.0),
            cross.animate(run_time=0.6).set_opacity(0.55),
            phase_lbl.animate(run_time=0.8).set_opacity(0.9),
            th1.animate(run_time=2.2, rate_func=rush_from).set_value(TAU + 0.5)))                # 2.2

        # =====================================================================
        # A2  2.2 - 4.1   second arrow tip-to-tail: reinforce, then cancel
        # =====================================================================
        n1 = np.array([np.sin(0.5), -np.cos(0.5), 0.0])           # unit normal of arrow 1

        def a2_start():
            return C0 + e2(th1.get_value(), R1)

        def a2_tail():
            d = 0.5 * (1 - np.cos(th2.get_value() - th1.get_value()))
            return a2_start() + 0.2 * d * n1

        arrow2 = always_redraw(lambda: arrow_between(a2_tail(), a2_tail() + e2(th2.get_value(), R1), CYAN))
        resu = always_redraw(lambda: arrow_between(
            C0 - 0.3 * n1, a2_tail() + e2(th2.get_value(), R1) - 0.3 * n1, WHITE_, w=3.4))
        lab_add = Text("add up", font=FONT, font_size=26, color=CYAN).move_to(C0 + np.array([3.6, 1.1, 0]))
        lab_can = Text("cancel out", font=FONT, font_size=26, color=WHITE_).move_to(lab_add)
        th2.set_value(TAU + 0.5)
        arrow2.set_opacity(0)
        self.play(k1.animate.set_value(1.0),
                  phase_lbl.animate.set_opacity(0),
                  FadeIn(arrow2), FadeIn(resu), FadeIn(lab_add), run_time=0.6)             # 2.8
        self.wait(0.5)                                                                     # 3.3
        self.play(th2.animate(rate_func=smooth).set_value(TAU + 0.5 + PI),
                  ReplacementTransform(lab_add, lab_can), run_time=0.8)                    # 4.1
        self.freeze(circ, arrow1, tipdot, arc, arrow2, resu, phase_lbl)

        # =====================================================================
        # A3  4.1 - 7.0   every path carries an arrow; all but the shortest cancel
        # =====================================================================
        SRC = np.array([-5.8, 0.25, 0.0])
        DET = np.array([2.85, 0.25, 0.0])
        cA = 6.0
        hs = np.linspace(-1.5, 1.5, 41)
        phis = cA * hs ** 2
        paths, marks, mark_ph = [], [], []
        for j in range(0, 41, 4):
            off = hs[j] * 1.3
            s = np.linspace(0, 1, 26)
            pts = [SRC + (DET - SRC) * si + UP * off * 4 * si * (1 - si) for si in s]
            pm = VMobject().set_points_smoothly(pts)
            pm.set_stroke(CYAN, 2.2, 0.62)
            paths.append(pm)
            mid = SRC + (DET - SRC) * 0.5 + UP * off
            d = e2(phis[j], 0.17)
            marks.append(Arrow(mid - d, mid + d, buff=0, stroke_width=3.2, tip_length=0.13,
                               max_tip_length_to_length_ratio=1.0, max_stroke_width_to_length_ratio=100,
                               color=WHITE_))
        straight = paths[5]
        straight.set_stroke(WHITE_, 3.2, 1.0)
        straight.set_stroke(CYAN, 10, 0.25, background=True)
        paths = VGroup(*paths)
        marks = VGroup(*marks)

        source = glow_dot(SRC, CYAN, r=0.11, layers=6)
        det_dot = glow_dot(DET, WHITE_, r=0.08, layers=4)
        src_lbl = Text("source", font=FONT, font_size=20, color=DIM).move_to(SRC + np.array([-0.2, -0.45, 0]))
        det_lbl = Text("detector", font=FONT, font_size=20, color=DIM).move_to(DET + np.array([0.25, -0.45, 0]))

        # phasor chain (all 41 amplitudes added tip to tail)
        seg = 0.27
        P = np.zeros((42, 3))
        for j in range(41):
            P[j + 1] = P[j] + e2(phis[j], seg)
        PC = np.array([5.4, 0.55, 0.0])
        P = P + PC - (P[0] + P[-1]) / 2
        chain_l = VMobject().set_points_as_corners(P[:17]).set_stroke(CYAN, 2.4, 0.7)
        chain_c = VMobject().set_points_as_corners(P[16:26]).set_stroke(WHITE_, 4.2, 1.0)
        chain_r = VMobject().set_points_as_corners(P[25:]).set_stroke(CYAN, 2.4, 0.7)
        chain_c.set_stroke(WHITE_, 12, 0.18, background=True)
        chain_lbl = Text("all arrows, added", font=FONT, font_size=20, color=DIM).move_to([5.4, -1.45, 0])
        res_arrow = arrow_between(P[0], P[-1], WHITE_, w=3.4, tip=0.2)

        A2_out = [circ, cross, arrow1, tipdot, arc, arrow2, resu, lab_can]
        self.play(AnimationGroup(
            *[FadeOut(m, run_time=0.35) for m in A2_out],
            FadeIn(source, run_time=0.4), FadeIn(det_dot, run_time=0.4),
            FadeIn(src_lbl, run_time=0.4), FadeIn(det_lbl, run_time=0.4),
            Succession(Wait(0.25), LaggedStart(*[Create(p) for p in paths], lag_ratio=0.08, run_time=0.65)),
            Succession(Wait(0.5), FadeIn(marks, run_time=0.4))))                          # 5.0
        self.play(Create(chain_l, run_time=0.5, rate_func=linear), FadeIn(chain_lbl, run_time=0.4))   # 5.5
        self.play(Create(chain_c, run_time=0.35, rate_func=linear))                        # 5.85
        self.play(Create(chain_r, run_time=0.5, rate_func=linear))                         # 6.35
        outer = [i for i in range(11) if abs(i - 5) > 1]
        self.play(FadeIn(res_arrow),
                  *[paths[i].animate.set_stroke(opacity=0.09) for i in outer],
                  *[marks[i].animate.set_opacity(0.12) for i in outer],
                  run_time=0.55)                                                           # 6.9
        self.wait(0.1)                                                                     # 7.0
        A3_out = [paths, marks, det_dot, src_lbl, det_lbl, chain_l, chain_c, chain_r, chain_lbl, res_arrow]

        # =====================================================================
        # B  7.0 - 13.0   double slit, one particle at a time
        # =====================================================================
        BX = -2.6
        PCY = 0.25
        PLX, PLW = 2.85, 0.75
        HX0 = 3.85
        s1, s2 = PCY + 0.5, PCY - 0.5
        hw = 0.08
        barrier = VGroup(
            Line([BX, 2.75, 0], [BX, s1 + hw, 0]),
            Line([BX, s1 - hw, 0], [BX, s2 + hw, 0]),
            Line([BX, s2 - hw, 0], [BX, -2.3, 0]))
        for b in barrier:
            neon(b, WHITE_, 5.0)
            b.set_stroke(opacity=0.85)
        src_beam = DashedLine(SRC, [BX, PCY, 0], dash_length=0.1, stroke_width=1.4, stroke_color=CYAN,
                              stroke_opacity=0.35)
        plate_frame = Rectangle(width=PLW, height=2 * DS_HALF, stroke_width=1.2, stroke_color=DIM,
                                fill_color=CYAN, fill_opacity=0.03).move_to([PLX + PLW / 2, PCY, 0])
        ph, pw = int(2 * DS_HALF * 100), int(PLW * 100)
        acc = np.zeros((ph, pw))
        plate = ImageMobject(np.zeros((ph, pw, 4), np.uint8))
        plate.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
        plate.width = PLW
        plate.move_to(plate_frame)
        stamp_r = 5
        gy, gx = np.mgrid[-stamp_r:stamp_r + 1, -stamp_r:stamp_r + 1]
        stamp = np.exp(-(gx ** 2 + gy ** 2) / (2 * 1.7 ** 2))
        st = {"n": 0}
        ds_T = ValueTracker(0.0)
        T_END = 4.5

        def count(t):
            if t < 1.5:
                return 5.0 * t / 1.5
            return 5.0 * np.exp((t - 1.5) * np.log(NP / 5.0) / (T_END - 1.5))

        def plate_upd(m):
            n = min(int(count(ds_T.get_value())), NP)
            if n > st["n"]:
                for j in range(st["n"], n):
                    row = int((DS_HALF - ds_hits[j]) * 100)
                    col = int(ds_x[j] * (pw - 1))
                    r0, r1 = max(row - stamp_r, 0), min(row + stamp_r + 1, ph)
                    c0, c1 = max(col - stamp_r, 0), min(col + stamp_r + 1, pw)
                    acc[r0:r1, c0:c1] += stamp[r0 - row + stamp_r:r1 - row + stamp_r,
                                               c0 - col + stamp_r:c1 - col + stamp_r]
                st["n"] = n
                v = 1 - np.exp(-acc * 1.1)
                white = np.clip(acc - 1.2, 0, 1.5) / 1.5
                col_c = np.array([76, 201, 240.0])
                rgb = col_c[None, None, :] * (1 - white[..., None]) + 255.0 * white[..., None]
                set_img(m, np.dstack([rgb, v * 255]).astype(np.uint8))
        plate.add_updater(plate_upd)

        NB = 46
        edges_y = np.linspace(-DS_HALF, DS_HALF, NB + 1)
        cdf_bins = np.array([ds_intensity(np.linspace(edges_y[i], edges_y[i + 1], 12)).mean() for i in range(NB)])
        pmax = cdf_bins.max() / cdf_bins.sum()
        hist = VMobject()
        hist.set_fill(GOLD, opacity=0.22)
        hist.set_stroke(GOLD, width=2.2)
        H_MAX = 2.3

        def hist_upd(m):
            n = st["n"]
            cnt = np.histogram(ds_hits[:n], bins=edges_y)[0]
            L = cnt / (n * pmax + 6.0) * H_MAX
            pts = [[HX0, PCY - DS_HALF, 0]]
            for i in range(NB):
                y0 = PCY + edges_y[i]
                y1 = PCY + edges_y[i + 1]
                pts += [[HX0, y0, 0], [HX0 + L[i], y0, 0], [HX0 + L[i], y1, 0], [HX0, y1, 0]]
            m.clear_points()
            m.set_points_as_corners(np.array(pts))
        hist_upd(hist)
        hist.add_updater(hist_upd)
        hist_axis = Line([HX0, PCY - DS_HALF, 0], [HX0, PCY + DS_HALF, 0], stroke_width=1.2, stroke_color=DIM)
        ys = np.linspace(-DS_HALF, DS_HALF, 220)
        theory = VMobject()
        Ith = ds_intensity(ys) / cdf_bins.max() * (cdf_bins.max() / cdf_bins.sum()) / pmax * H_MAX \
            * (cdf_bins.sum() * pmax / cdf_bins.max())
        theory.set_points_smoothly(np.column_stack([HX0 + Ith * 0.985, PCY + ys, np.zeros_like(ys)]))
        theory.set_stroke(WHITE_, width=2.0, opacity=0.9)
        theory.set_stroke(GOLD, width=6, opacity=0.25, background=True)

        def ripples():
            g = VGroup()
            ph_ = (ds_T.get_value() * 0.45) % 1.0
            for sy in (s1, s2):
                for k in range(11):
                    r = (k + ph_) * 0.55
                    if r < 0.05:
                        continue
                    op = 0.30 * max(0.0, 1 - r / 6.2) * min(1.0, r / 0.6)
                    a = Arc(radius=r, start_angle=-0.95, angle=1.9, arc_center=[BX, sy, 0],
                            stroke_width=1.6, stroke_color=CYAN, stroke_opacity=op)
                    g.add(a)
            return g
        rip = always_redraw(ripples)

        flyer = Dot(radius=0.06, color=WHITE_)
        flyer.set_opacity(0)

        def fly_upd(m):
            t = ds_T.get_value()
            if t >= 1.62:
                m.set_opacity(0)
                return
            j = int(np.ceil(t / 0.3 - 1e-9))
            tau = j * 0.3
            f = (t - (tau - 0.3)) / 0.3
            if j < 1 or j > 5 or f < 0:
                m.set_opacity(0)
                return
            j -= 1
            sy = s1 if ds_slit[j] == 0 else s2
            hit = np.array([PLX + ds_x[j] * PLW, PCY + ds_hits[j], 0])
            slit = np.array([BX, sy, 0])
            if f < 0.45:
                p = SRC + (slit - SRC) * (f / 0.45)
            else:
                p = slit + (hit - slit) * ((f - 0.45) / 0.55)
            m.move_to(p)
            m.set_opacity(1)
        flyer.add_updater(fly_upd)

        ds_static = Group(barrier, src_beam, plate_frame, hist_axis)
        self.play(*[FadeOut(m) for m in A3_out], FadeIn(ds_static), run_time=0.5)          # 7.5
        self.add(rip, plate, hist, flyer)
        self.play(ds_T.animate.set_value(T_END), Succession(Wait(T_END - 1.0), Create(theory, run_time=1.0)),
                  run_time=T_END, rate_func=linear)                                        # 12.0
        self.wait(0.5)                                                                     # 12.5
        plate.clear_updaters()
        hist.clear_updaters()
        ds_grp = Group(ds_static, rip, plate, hist, flyer, theory, source)

        # =====================================================================
        # C  13.0 - 20.0   Bloch sphere -> qubits -> interfering amplitudes
        # =====================================================================
        BC, BRAD = np.array([0.0, 0.15, 0.0]), 1.6
        bloch = sphere_group(BC, BRAD)
        lbl0 = MathTex(r"|0\rangle", font_size=34, color=CYAN).move_to(bloch_proj((0, 0, 1.22), BRAD, BC)[0] + UP * 0.3)
        lbl1 = MathTex(r"|1\rangle", font_size=34, color=CYAN).move_to(bloch_proj((0, 0, -1.22), BRAD, BC)[0] + DOWN * 0.3)
        TH = 0.95
        lat = sphere_curve(lambda t: (np.sin(TH) * np.cos(t), np.sin(TH) * np.sin(t), np.cos(TH)),
                           BC, BRAD, MAGENTA, 1.0, dim=0.18, front=0.35)
        phi = ValueTracker(0.0)
        kc = ValueTracker(0.0)          # cyan -> magenta

        def vec_at(ph_, k):
            return state_vec((np.sin(TH) * np.cos(ph_), np.sin(TH) * np.sin(ph_), np.cos(TH)),
                             BC, BRAD, col=mix(CYAN, MAGENTA, k))

        vec = vec_at(0.0, 0.0)
        big = VGroup(bloch, lat, lbl0, lbl1, vec)
        vec.add_updater(lambda m: m.become(vec_at(phi.get_value(), kc.get_value())))
        self.play(FadeOut(ds_grp), FadeIn(big), run_time=0.5)                              # 13.0
        self.play(phi.animate(rate_func=linear).set_value(2.35 * np.pi),
                  kc.animate(rate_func=smooth).set_value(1.0), run_time=2.4)               # 15.4
        vec.clear_updaters()

        QX, QY = [-5.6, -4.4, -3.2], 0.45
        qubits = VGroup()
        for x in QX:
            c = np.array([x, QY, 0.0])
            qubits.add(VGroup(sphere_group(c, 0.42, 0.6, full=False),
                              state_vec((1, 0, 0), c, 0.42, 3.5, 0.04)))
        ket = VGroup(*[MathTex(r"|+\rangle", font_size=28, color=CYAN).move_to([x, QY - 0.85, 0]) for x in QX])
        fact = MathTex(r"15 = 3 \times ?", font_size=34, color=WHITE_).move_to([-4.4, -1.15, 0])
        fact_done = MathTex(r"15 = 3 \times 5", font_size=34, color=WHITE_).move_to(fact)
        fact_done[0][-1].set_color(MAGENTA)

        X0, PITCH, BW, YB, HS, MARK = -1.0, 0.86, 0.62, 0.45, 1.75, 5

        def bars_poly(vals):
            g = VGroup()
            for j, v in enumerate(vals):
                x = X0 + j * PITCH
                col = MAGENTA if j == MARK else CYAN
                pl = Polygon([x - BW / 2, YB, 0], [x + BW / 2, YB, 0],
                             [x + BW / 2, YB + v * HS, 0], [x - BW / 2, YB + v * HS, 0])
                neon(pl, col, 2.6)
                pl.set_fill(col, 0.30)
                g.add(pl)
            return g

        base_line = Line([X0 - 0.45, YB, 0], [X0 + 7 * PITCH + 0.45, YB, 0]).set_stroke(DIM, 1.4, 0.8)
        xlabels = VGroup(*[Text(format(j, "03b"), font=MONO, font_size=17, color=DIM)
                           .move_to([X0 + j * PITCH, -1.85, 0]) for j in range(8)])
        step_lbl = Text("superposition", font=FONT, font_size=22, color=CYAN).move_to([X0 + 3.5 * PITCH, -2.35, 0])

        a0 = 1 / np.sqrt(8)
        v0 = [a0] * 8
        v1 = [a0] * 8; v1[MARK] = -a0                                   # oracle flips the sign (phase) of the answer
        m1 = np.mean(v1); v2 = [2 * m1 - x for x in v1]                 # inversion about the mean
        v3 = list(v2); v3[MARK] = -v3[MARK]
        m3 = np.mean(v3); v4 = [2 * m3 - x for x in v3]                 # 2nd round: answer amplitude ~ 0.97

        bars = bars_poly([0.0] * 8)
        self.play(FadeOut(big, target_position=qubits[0].get_center(), scale=0.25),
                  FadeIn(qubits, shift=RIGHT * 0.3), FadeIn(ket), FadeIn(fact),
                  FadeIn(base_line), FadeIn(xlabels), FadeIn(step_lbl),
                  run_time=0.7)                                                            # 16.1
        self.add(bars)
        self.play(Transform(bars, bars_poly(v0)), run_time=0.4)                            # 16.5
        lbl_i = Text("interference", font=FONT, font_size=22, color=MAGENTA).move_to(step_lbl)
        self.play(Transform(bars, bars_poly(v1)), FadeOut(step_lbl), FadeIn(lbl_i), run_time=0.5)   # 17.0
        self.play(Transform(bars, bars_poly(v2)), run_time=0.5)                            # 17.5
        self.play(Transform(bars, bars_poly(v3)), run_time=0.5)                            # 18.0
        self.play(Transform(bars, bars_poly(v4)), run_time=0.5)                            # 18.5
        tipx = X0 + MARK * PITCH
        ans = glow_dot([tipx, YB + v4[MARK] * HS, 0], MAGENTA, r=0.07, layers=4)
        ans_t = Text("answer", font=FONT, font_size=20, color=MAGENTA).move_to([tipx, YB + v4[MARK] * HS + 0.3, 0])
        self.play(FadeIn(ans), FadeIn(ans_t), ReplacementTransform(fact, fact_done), run_time=0.5)   # 19.0
        self.wait(1.0)                                                                     # 20.0
        t1 = Group(qubits, ket, fact_done, base_line, xlabels, lbl_i, bars, ans, ans_t)

        # =====================================================================
        # D  20.0 - 28.0   holographic disk, then the three strands converge
        # =====================================================================
        DC, RD = np.array([0.0, -0.05, 0.0]), 2.3
        disk = Circle(radius=RD).move_to(DC)
        disk.set_fill("#0B1226", 1.0)
        neon(disk, CYAN, 3.0)
        NT = 60
        ang = 2 * np.pi * np.arange(NT) / NT
        tw, tph = rng.uniform(1.5, 4.0, NT), rng.uniform(0, 2 * np.pi, NT)
        tcol = [ring_colour(a / (2 * np.pi)) for a in ang]
        ticks = VGroup(*[Line(ORIGIN, RIGHT * 0.1) for _ in range(NT)])
        clk = {"t": 0.0}

        def tick_upd(m, dt):
            clk["t"] += dt
            for j, ln in enumerate(ticks):
                f = 0.5 + 0.5 * np.sin(tw[j] * clk["t"] + tph[j])
                u = np.array([np.cos(ang[j]), np.sin(ang[j]), 0.0])
                ln.put_start_and_end_on(DC + u * (RD + 0.07), DC + u * (RD + 0.07 + 0.08 + 0.24 * f))
                ln.set_stroke(tcol[j], 3.0, 0.35 + 0.65 * f)

        tick_upd(ticks, 0.0)
        lab_b = VGroup(Text("boundary", font=FONT, font_size=24, color=MAGENTA).move_to([-5.2, 1.3, 0]),
                       Line([-4.3, 1.25, 0], DC + RD * np.array([np.cos(2.6), np.sin(2.6), 0]) * 1.06)
                       .set_stroke(MAGENTA, 1.2, 0.6))
        lab_c = VGroup(Text("bulk", font=FONT, font_size=24, color=GOLD).move_to([4.6, 1.3, 0]),
                       Line([3.9, 1.25, 0], DC + np.array([1.05, 0.55, 0]))
                       .set_stroke(GOLD, 1.2, 0.6),
                       Dot(DC + np.array([1.05, 0.55, 0]), radius=0.035, color=GOLD))
        pulse_ang = 2 * np.pi * np.arange(12) / 12 + 0.13
        pdots, plines, pends = VGroup(), VGroup(), []
        for j, a in enumerate(pulse_ang):
            u = np.array([np.cos(a), np.sin(a), 0.0])
            depth = [0.28, 0.5, 0.36, 0.62][j % 4]
            s, e = DC + u * RD, DC + u * RD * depth
            c_ = ring_colour(a / (2 * np.pi))
            pdots.add(glow_dot(s, c_, r=0.045, layers=3))
            plines.add(Line(s, e).set_stroke(c_, 1.8, 0.6))
            pends.append(e)
        tiles = VGroup()
        for L_, arcs in enumerate(per_layer):
            for vm in multipaths(arcs, DC, RD):
                vm.set_stroke(mix(GOLD, CYAN, L_ / 5.5), width=2.4 - 0.35 * L_)
                vm.set_stroke(mix(GOLD, CYAN, L_ / 5.5), width=(2.4 - 0.35 * L_) * 3, opacity=0.14,
                              background=True)
                tiles.add(vm)
        tiles.set_z_index(1)
        plines.set_z_index(2)
        pdots.set_z_index(3)
        # group the tile chunks per layer for a staged reveal
        tile_groups, idx = [], 0
        for L_, arcs in enumerate(per_layer):
            n_chunks = int(np.ceil(len(arcs) / 110))
            tile_groups.append(VGroup(*tiles[idx: idx + n_chunks]))
            idx += n_chunks

        self.play(FadeOut(t1, run_time=0.3),
                  Succession(Wait(0.15), AnimationGroup(FadeIn(disk), FadeIn(ticks), FadeIn(lab_b),
                                                        FadeIn(lab_c), FadeIn(pdots), run_time=0.35)))   # 20.5
        ticks.add_updater(tick_upd)
        self.play(LaggedStart(*[Create(t) for t in tile_groups], lag_ratio=0.5), run_time=1.0)   # 21.5
        self.play(LaggedStart(*[AnimationGroup(Create(ln), d.animate.move_to(e))
                                for ln, d, e in zip(plines, pdots, pends)], lag_ratio=0.12),
                  run_time=1.5)                                                            # 23.0
        self.wait(0.9)                                                                     # 23.9
        ticks.clear_updaters()
        t2 = Group(disk, ticks, lab_b, lab_c, pdots, tiles, plines)

        # ---- the three strands braid and converge at (0,0) -------------------
        C = ValueTracker(0.0)
        PHT = ValueTracker(0.0)
        B = ValueTracker(0.0)

        def make_strands():
            cv, ph_, bv = C.get_value(), PHT.get_value(), B.get_value()
            xs = np.linspace(-7.5, 7.5, 161)
            g = VGroup()
            for i, col in enumerate(STR_COLS):
                env = 1 - cv * (1 - np.minimum(1.0, np.abs(xs) / 5.5) ** 1.1)
                ys_ = Y0 * (1 - cv) + AMP * (1 - 0.2 * cv) * env * np.sin(K_ * (xs + ph_) + STR_PH[i])
                m = VMobject().set_points_smoothly([[x, y, 0] for x, y in zip(xs, ys_)])
                wd = 3.5 + 3.5 * bv
                m.set_stroke(col, wd, opacity=min(1.0, bv * 1.15))
                m.set_stroke(col, wd * 3.2, opacity=0.2 * bv, background=True)
                g.add(m)
            return g

        strands = always_redraw(make_strands)
        strands.set_z_index(-4)
        self.add(strands)
        self.play(FadeOut(t2), B.animate.set_value(0.5),
                  PHT.animate(rate_func=linear).set_value(0.3), run_time=0.7)              # 24.6
        self.play(C.animate(rate_func=smooth).set_value(1.0),
                  B.animate(rate_func=smooth).set_value(1.0),
                  PHT.animate(rate_func=linear).set_value(0.3 + 0.5 * 2.4), run_time=2.4)  # 27.0
        centre = glow_dot(ORIGIN, WHITE_, r=0.12, layers=6)
        self.play(FadeIn(centre, scale=0.4), run_time=0.3)                                 # 27.3
        strands.clear_updaters()
        self.remove(C, PHT, B, th1, th2, k1, fade, phi, kc, ds_T)
        self.fade_all(0.7)                                                                 # 28.0
        self.pad_to()
