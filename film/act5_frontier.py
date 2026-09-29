from style import *

# ===========================================================================
#  ACT 5 - FRONTIER   (28 s)
#  Three strands (gold / cyan / magenta) braid; every topic sits on the braid.
#  Timeline (s):
#   0.0  intro: strands drawn, then weave into a braid          (2.2)
#   2.2  1 Quantum computing   cyan x magenta                   (5.2)
#   7.4  2 AdS/CFT holography  cyan x gold                      (4.0)
#  11.4  3 Langlands           gold x gold                      (4.0)
#  15.4  4 Black holes + QEC   gold x cyan x magenta            (4.0)
#  19.4  5 Proofs/programs/physics                             (4.0)
#  23.4  strands converge on the centre, brighten              (3.9)
#  27.3  fade_all                                              (0.7)
# ===========================================================================

GOLD2 = "#FFE08A"
AMBER = "#E8A93B"

# ---- braid geometry --------------------------------------------------------
P_ = 3.2                      # braid period (x units)
K_ = 2 * np.pi / P_
AMP = 0.80
Y0 = 0.10
STR_COLS = [GOLD, CYAN, MAGENTA]
STR_PH = [0.0, 2 * np.pi / 3, 4 * np.pi / 3]
XL, XR = -11.2, 11.2          # 7 periods: shifting one period never exposes an end

BR, DM = 0.60, 0.12           # "bright" / "dim" strand weights


def build_braid():
    """Return (flat_pieces, braid_pieces): matching lists of VMobjects.
    Each strand is cut where its depth (cos theta) changes sign, so that
    'front' pieces can be drawn above 'back' pieces (over/under weaving)."""
    flat, braid = [], []
    for i, col in enumerate(STR_COLS):
        ph = STR_PH[i]
        bs = []
        n = int(np.floor((K_ * XL + ph - np.pi / 2) / np.pi)) - 1
        while True:
            x = (np.pi / 2 + n * np.pi - ph) / K_
            if x > XR:
                break
            if x > XL:
                bs.append(x)
            n += 1
        bs = [XL] + bs + [XR]
        for a, b in zip(bs[:-1], bs[1:]):
            if b - a < 1e-3:
                continue
            xs = np.linspace(a, b, 22)
            front = np.cos(K_ * (a + b) / 2 + ph) > 0
            for target, ys in ((flat, np.full_like(xs, Y0 + (i - 1) * 0.42)),
                               (braid, Y0 + AMP * np.sin(K_ * xs + ph))):
                m = VMobject()
                m.set_points_smoothly([[x, y, 0] for x, y in zip(xs, ys)])
                if target is flat:
                    neon(m, col, width=3.4)
                    m.set_stroke(col, 3.4, 0.9)
                else:
                    neon(m, col, width=4.6 if front else 2.6)
                    m.set_stroke(col, 4.6 if front else 2.6, 1.0 if front else 0.55)
                m.strand = i
                m.base = 1.0 if front else 0.55
                m.xl, m.xr = a, b
                m.set_z_index(-5 if front else -6)
                target.append(m)
    return flat, braid


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


def state_vec(p, c, R, w=5.0, r=0.06):
    tip, _ = bloch_proj(p, R, c)
    ln = Line(c, tip)
    neon(ln, MAGENTA, w)
    return VGroup(ln, glow_dot(tip, MAGENTA, r=r, layers=4), Dot(c, radius=0.03, color=WHITE_))


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
            per_layer[L].append(_geodesic(a, b))
    return per_layer, len(polys)


def multipath(arcs, centre, R):
    """One VMobject holding many polylines (arcs = lists of complex numbers)."""
    vm = VMobject()
    for arc in arcs:
        pts = [np.array([centre[0] + R * z.real, centre[1] + R * z.imag, 0.0]) for z in arc]
        vm.start_new_path(pts[0])
        vm.add_points_as_corners(pts[1:])
    return vm


def mix(a, b, t):
    return ManimColor(a).interpolate(ManimColor(b), t)


# ---- small builders --------------------------------------------------------
def topic_title(text, cols):
    t = Text(text, font=FONT, font_size=24, weight=BOLD)
    t.set_color_by_gradient(*cols)
    a = glow_dot(ORIGIN, cols[0], r=0.045, layers=3)
    b = glow_dot(ORIGIN, cols[-1], r=0.045, layers=3)
    g = VGroup(a, t, b).arrange(RIGHT, buff=0.3)
    return g.move_to(UP * 3.3)


def two_tone_link(p, q, cols, w=3.0):
    ln = Line(p, q)
    ln.set_stroke(cols, width=w)
    ln.set_stroke(cols, width=w * 3.2, opacity=0.2, background=True)
    return ln


def equals_link(centre, cols, half=0.24, gap=0.1):
    c = np.array(centre, dtype=float)
    return VGroup(two_tone_link(c + UP * gap + LEFT * half, c + UP * gap + RIGHT * half, cols),
                  two_tone_link(c + DOWN * gap + LEFT * half, c + DOWN * gap + RIGHT * half, cols))


class Act5(FilmScene):
    DURATION = BUDGET["act5"]

    # ------------------------------------------------------------------
    def construct(self):
        L = ValueTracker(1.0)                       # global braid level
        W = [ValueTracker(1.0) for _ in range(3)]   # per-strand weights
        SPD = ValueTracker(0.0)                     # extra drift speed (camera slide)
        st = {"off": 0.0}

        flat, target = build_braid()
        braid = VGroup(*flat)

        def levels():
            lv = L.get_value()
            for p in flat:
                f = W[p.strand].get_value() * lv
                p.set_stroke(opacity=p.base * f)
                p.set_stroke(opacity=0.18 * p.base * f, background=True)

        def drift(m, dt):
            d = (0.22 + SPD.get_value()) * dt
            st["off"] += d
            m.shift(LEFT * d)
            if st["off"] >= P_:
                m.shift(RIGHT * P_)
                st["off"] -= P_
            levels()

        def slide(old, new, weights, old_title=None, new_title=None, rt=0.8, extra=()):
            """Camera-slide: old content leaves left, new enters from the right,
            the braid speeds up and the strand weights re-tune to the new topic.
            Titles cross-fade in place (old out first, then new in)."""
            anims = [SPD.animate(rate_func=there_and_back).set_value(1.7)]
            anims += [w.animate.set_value(x) for w, x in zip(W, weights)]
            if old is not None:
                anims.append(Succession(FadeOut(old, shift=LEFT * 1.8, run_time=0.55), Wait(0.25)))
            if new is not None:
                anims.append(Succession(Wait(0.25), FadeIn(new, shift=LEFT * 1.8, run_time=0.55)))
            seq = []
            if old_title is not None:
                seq.append(FadeOut(old_title, run_time=0.3))
            if new_title is not None:
                seq.append(FadeIn(new_title, run_time=0.4))
            if seq:
                anims.append(Succession(*seq))
            self.play(*anims, *extra, run_time=rt)

        # =====================================================================
        # INTRO 0.0 - 2.2 : three strands are drawn, then weave into a braid
        # =====================================================================
        self.tag("05", "FRONTIER", WHITE_, start=0.3, dur=3.6)
        vis = sorted([p for p in flat if p.xr > -7.6 and p.xl < 7.6], key=lambda p: p.xl)
        self.add(*[p for p in flat if p not in vis])
        self.play(AnimationGroup(*[
            Succession(*[Create(p, run_time=1.0 / sum(1 for q in vis if q.strand == i), rate_func=linear)
                         for p in vis if p.strand == i]) for i in range(3)]), run_time=1.0)   # 1.0
        self.play(AnimationGroup(*[Transform(f, b) for f, b in zip(flat, target)]),
                  run_time=1.2)                                                            # 2.2
        for f_, b_ in zip(flat, target):
            f_.base = b_.base
            f_.set_z_index(b_.z_index)
        self.add(braid)
        braid.add_updater(drift)

        # =====================================================================
        # 1. QUANTUM COMPUTING (cyan x magenta)   2.2 - 7.4   (5.2 s)
        # =====================================================================
        self.caption("Qubits: superposition and interference, put to work.", start=0.5, dur=4.5)
        title1 = topic_title("QUANTUM COMPUTING", [CYAN, MAGENTA])
        BC, BRAD = np.array([0.0, 0.15, 0.0]), 1.6
        bloch = sphere_group(BC, BRAD)
        lbl0 = MathTex(r"|0\rangle", font_size=34, color=CYAN).move_to(bloch_proj((0, 0, 1.22), BRAD, BC)[0] + UP * 0.3)
        lbl1 = MathTex(r"|1\rangle", font_size=34, color=CYAN).move_to(bloch_proj((0, 0, -1.22), BRAD, BC)[0] + DOWN * 0.3)
        TH = 0.95
        lat = sphere_curve(lambda t: (np.sin(TH) * np.cos(t), np.sin(TH) * np.sin(t), np.cos(TH)),
                           BC, BRAD, MAGENTA, 1.0, dim=0.18, front=0.35)
        phi = ValueTracker(0.0)

        def vec_at(ph):
            return state_vec((np.sin(TH) * np.cos(ph), np.sin(TH) * np.sin(ph), np.cos(TH)), BC, BRAD)

        vec = vec_at(0.0)
        big = VGroup(bloch, lat, lbl0, lbl1, vec)
        slide(None, big, [DM, BR, BR], None, title1)                                     # 3.0
        vec.add_updater(lambda m: m.become(vec_at(phi.get_value())))
        self.play(phi.animate.set_value(2.35 * np.pi), run_time=1.4, rate_func=linear)     # 4.4
        vec.clear_updaters()

        # -- row of qubits in superposition -> amplitude chart
        QX, QY = [-5.6, -4.4, -3.2], 0.45
        qubits = VGroup()
        for x in QX:
            c = np.array([x, QY, 0.0])
            qubits.add(VGroup(sphere_group(c, 0.42, 0.6, full=False),
                              state_vec((1, 0, 0), c, 0.42, 3.5, 0.04)))
        ket = VGroup(*[MathTex(r"|+\rangle", font_size=28, color=CYAN).move_to([x, QY - 0.85, 0]) for x in QX])
        fact = MathTex(r"15 = 3 \times 5", font_size=34, color=WHITE_).move_to([-4.4, -1.15, 0])

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
        v1 = [a0] * 8; v1[MARK] = -a0                                   # oracle marks the answer
        m1 = np.mean(v1); v2 = [2 * m1 - x for x in v1]                 # inversion about the mean
        v3 = list(v2); v3[MARK] = -v3[MARK]
        m3 = np.mean(v3); v4 = [2 * m3 - x for x in v3]                 # 2nd round: answer ~ 0.97

        bars = bars_poly([0.0] * 8)
        self.play(FadeOut(big, target_position=qubits[0].get_center(), scale=0.25),
                  FadeIn(qubits, shift=RIGHT * 0.3), FadeIn(ket), FadeIn(fact),
                  FadeIn(base_line), FadeIn(xlabels), FadeIn(step_lbl),
                  run_time=0.7)                                                            # 5.1
        self.add(bars)
        self.play(Transform(bars, bars_poly(v0)), run_time=0.4)                            # 5.5
        lbl_i = Text("interference", font=FONT, font_size=22, color=MAGENTA).move_to(step_lbl)
        self.play(Transform(bars, bars_poly(v1)), FadeOut(step_lbl), FadeIn(lbl_i), run_time=0.4)   # 5.9
        self.play(Transform(bars, bars_poly(v2)), run_time=0.4)                            # 6.3
        self.play(Transform(bars, bars_poly(v3)), run_time=0.4)                            # 6.7
        self.play(Transform(bars, bars_poly(v4)), run_time=0.4)                            # 7.1
        tipx = X0 + MARK * PITCH
        ans = glow_dot([tipx, YB + v4[MARK] * HS, 0], MAGENTA, r=0.07, layers=4)
        ans_t = Text("answer", font=FONT, font_size=20, color=MAGENTA).move_to([tipx, YB + v4[MARK] * HS + 0.3, 0])
        self.play(FadeIn(ans), FadeIn(ans_t), run_time=0.3)                                # 7.4
        t1 = VGroup(qubits, ket, fact, base_line, xlabels, lbl_i, bars, ans, ans_t)

        # =====================================================================
        # 2. AdS/CFT HOLOGRAPHY (cyan x gold)   7.4 - 11.4   (4.0 s)
        # =====================================================================
        self.caption("A universe inside a disk, described entirely by its boundary.", start=0.5, dur=3.3)
        title2 = topic_title("HOLOGRAPHY  ·  AdS / CFT", [CYAN, GOLD])
        DC, RD = np.array([0.0, 0.1, 0.0]), 2.3
        disk = Circle(radius=RD).move_to(DC)
        disk.set_fill("#0B1226", 1.0)
        neon(disk, CYAN, 3.0)
        rng = np.random.default_rng(7)
        NT = 60
        ang = 2 * np.pi * np.arange(NT) / NT
        tw, tph = rng.uniform(1.5, 4.0, NT), rng.uniform(0, 2 * np.pi, NT)
        ticks = VGroup(*[Line(ORIGIN, RIGHT * 0.1) for _ in range(NT)])
        clk = {"t": 0.0}

        def tick_upd(m, dt):
            clk["t"] += dt
            for j, ln in enumerate(ticks):
                f = 0.5 + 0.5 * np.sin(tw[j] * clk["t"] + tph[j])
                u = np.array([np.cos(ang[j]), np.sin(ang[j]), 0.0])
                ln.put_start_and_end_on(DC + u * (RD + 0.07), DC + u * (RD + 0.07 + 0.08 + 0.24 * f))
                ln.set_stroke(CYAN, 3.0, 0.35 + 0.65 * f)

        tick_upd(ticks, 0.0)
        lab_b = VGroup(Text("boundary theory", font=FONT, font_size=22, color=CYAN).move_to([-5.3, 1.2, 0]),
                       Line([-4.2, 1.15, 0], DC + RD * np.array([np.cos(2.6), np.sin(2.6), 0]) * 1.06)
                       .set_stroke(CYAN, 1.2, 0.6))
        lab_c = VGroup(Text("curved bulk", font=FONT, font_size=22, color=GOLD).move_to([5.0, 1.2, 0]),
                       Line([3.9, 1.15, 0], DC + np.array([1.05, 0.55, 0]))
                       .set_stroke(GOLD, 1.2, 0.6),
                       Dot(DC + np.array([1.05, 0.55, 0]), radius=0.035, color=GOLD))
        pulse_ang = 2 * np.pi * np.arange(12) / 12 + 0.13
        pdots, plines, pends = VGroup(), VGroup(), []
        for j, a in enumerate(pulse_ang):
            u = np.array([np.cos(a), np.sin(a), 0.0])
            depth = [0.28, 0.5, 0.36, 0.62][j % 4]
            s, e = DC + u * RD, DC + u * RD * depth
            pdots.add(glow_dot(s, WHITE_, r=0.045, layers=3))
            plines.add(Line(s, e).set_stroke(CYAN, 1.8, 0.55))
            pends.append(e)
        static2 = VGroup(disk, ticks, lab_b, lab_c, pdots)
        slide(t1, static2, [BR, DM, BR], title1, title2)                                                   # 8.2   (T1 out)
        ticks.add_updater(tick_upd)
        per_layer, npoly = hyperbolic_tiling(7, 3, 4)
        tiles = VGroup()
        for L_, arcs in enumerate(per_layer):
            vm = multipath(arcs, DC, RD)
            vm.set_stroke(mix(GOLD, CYAN, L_ / 5.5), width=2.4 - 0.35 * L_)
            vm.set_stroke(mix(GOLD, CYAN, L_ / 5.5), width=(2.4 - 0.35 * L_) * 3, opacity=0.14,
                          background=True)
            tiles.add(vm)
        tiles.set_z_index(1)
        plines.set_z_index(2)
        pdots.set_z_index(3)
        self.play(LaggedStart(*[Create(t) for t in tiles], lag_ratio=0.5), run_time=0.9)   # 9.1
        self.play(LaggedStart(*[AnimationGroup(Create(ln), d.animate.move_to(e))
                                for ln, d, e in zip(plines, pdots, pends)], lag_ratio=0.12),
                  run_time=1.6)                                                            # 10.7
        self.wait(0.7)                                                                     # 11.4
        ticks.clear_updaters()
        t2 = VGroup(disk, ticks, lab_b, lab_c, pdots, tiles, plines)

        # =====================================================================
        # 3. LANGLANDS (gold x gold)   11.4 - 15.4   (4.0 s)
        # =====================================================================
        self.caption("Langlands: bridges between numbers, geometry and symmetry.", start=0.5, dur=3.3)
        title3 = topic_title("THE LANGLANDS PROGRAMME", [GOLD, GOLD2])
        ea, eb = 1.55, 1.0
        cN, cG, cS = np.array([-4.2, -0.55, 0]), np.array([0.0, 1.5, 0]), np.array([4.2, -0.55, 0])

        def island(c, col, name, label_pos):
            ring = Ellipse(width=2 * ea, height=2 * eb).move_to(c)
            neon(ring, col, 2.2)
            ring.set_fill("#0A1020", 0.9)
            nm = Text(name, font=FONT, font_size=26, color=col, weight=BOLD).move_to(label_pos)
            return ring, nm

        rN, nN = island(cN, GOLD, "NUMBERS", cN + DOWN * 1.4)
        rG, nG = island(cG, GOLD2, "GEOMETRY", cG + DOWN * 1.4)
        rS, nS = island(cS, AMBER, "SYMMETRY", cS + DOWN * 1.4)

        primes = [(-0.95, 0.3, "2"), (-0.4, 0.58, "3"), (0.25, 0.5, "5"), (0.9, 0.25, "7"),
                  (-0.8, -0.32, "11"), (-0.15, -0.02, "13"), (0.5, -0.22, "17"),
                  (-0.1, -0.62, "19"), (0.95, -0.5, "23")]
        numbers = VGroup(*[Text(s, font=MONO, font_size=22, color=GOLD).move_to(cN + np.array([x, y, 0]))
                           for x, y, s in primes])

        sc, cx = 0.58, 0.25
        f = lambda x: x ** 3 - x
        u = np.linspace(0, np.pi, 40)
        ox = -0.5 - 0.5 * np.cos(u)
        oy = np.sqrt(np.maximum(f(ox), 0))
        oval = [(x, y) for x, y in zip(ox, oy)] + [(x, -y) for x, y in zip(ox[::-1], oy[::-1])]
        w_ = np.linspace(0, 1, 30)
        bx = 1 + 0.5 * w_ ** 2
        by = np.sqrt(np.maximum(f(bx), 0))
        branch = [(x, -y) for x, y in zip(bx[::-1], by[::-1])] + [(x, y) for x, y in zip(bx, by)]
        curve = VGroup()
        for pts in (oval, branch):
            m = VMobject().set_points_smoothly([cG + np.array([(x - cx) * sc, y * sc, 0]) for x, y in pts])
            neon(m, GOLD2, 3.2)
            curve.add(m)

        hexr = 0.72
        hv = [cS + hexr * np.array([np.cos(np.pi / 6 + k * np.pi / 3), np.sin(np.pi / 6 + k * np.pi / 3), 0]) for k in range(6)]
        hexa = Polygon(*hv)
        neon(hexa, AMBER, 3.0)
        diag = VGroup(*[Line(hv[k], hv[k + 3]).set_stroke(AMBER, 1.6, 0.7) for k in range(3)])
        mirrors = VGroup(*[DashedLine(cS + 0.9 * np.array([np.cos(k * np.pi / 3), np.sin(k * np.pi / 3), 0]),
                                      cS - 0.9 * np.array([np.cos(k * np.pi / 3), np.sin(k * np.pi / 3), 0]),
                                      dash_length=0.08).set_stroke(AMBER, 1.3, 0.45) for k in range(3)])
        sym = VGroup(mirrors, diag, hexa)

        def edge_pt(c, tgt):
            v = (tgt - c)
            v = v / np.hypot(v[0] / ea, v[1] / eb)
            return c + v

        cen3 = (cN + cG + cS) / 3

        def bridge(c1, c2, col):
            p1, p2 = edge_pt(c1, c2), edge_pt(c2, c1)
            best = None
            for ang_ in (0.55, -0.55):
                a = ArcBetweenPoints(p1, p2, angle=ang_)
                d = np.linalg.norm(a.point_from_proportion(0.5) - cen3)
                if best is None or d > best[0]:
                    best = (d, a)
            arc = best[1]
            neon(arc, col, 3.4)
            return arc, p1, p2

        b1, p1a, p1b = bridge(cN, cG, GOLD)
        b2, p2a, p2b = bridge(cG, cS, GOLD2)
        b3, p3a, p3b = bridge(cS, cN, AMBER)
        ports = VGroup(*[glow_dot(p, WHITE_, r=0.05, layers=3) for p in (p1a, p1b, p2a, p2b, p3a, p3b)])
        static3 = VGroup(rN, rG, rS, nN, nG, nS, numbers, curve, sym, ports)
        slide(t2, static3, [BR, DM, DM], title2, title3)                                  # 12.2  (T2 out)
        # math x math: only the gold strand stays lit
        pulses = []
        for arc, col in ((b1, GOLD), (b2, GOLD2), (b3, AMBER)):
            pl = glow_dot(arc.get_start(), WHITE_, r=0.08, layers=5)
            pulses.append(pl)
            self.add(pl)
            self.play(Create(arc), MoveAlongPath(pl, arc), run_time=0.8, rate_func=smooth)
        self.play(*[FadeOut(pl) for pl in pulses],
                  LaggedStart(*[ShowPassingFlash(a.copy().set_stroke(WHITE_, 6, 1.0), time_width=0.7)
                                for a in (b1, b2, b3)], lag_ratio=0.25),
                  run_time=0.8)                                                            # 15.4
        t3 = VGroup(static3, b1, b2, b3)

        # =====================================================================
        # 4. BLACK HOLES x ERROR CORRECTION (all three)   15.4 - 19.4   (4.0 s)
        # =====================================================================
        self.caption("Black holes, error-correcting codes, spacetime: one puzzle?", start=0.5, dur=3.3)
        title4 = topic_title("BLACK HOLES  ·  ERROR-CORRECTING CODES", [CYAN, GOLD, MAGENTA])
        HC, HR = np.array([0.0, 0.1, 0.0]), 1.12
        halo = VGroup(*[Circle(radius=HR + 0.1 + 0.16 * i).move_to(HC).set_stroke(width=0).set_fill(CYAN, 0.05)
                        for i in range(4)])
        bh = Circle(radius=HR).move_to(HC)
        bh.set_fill("#000000", 1.0)
        neon(bh, CYAN, 3.4)
        NB = 40
        bang = 2 * np.pi * np.arange(NB) / NB
        bits = VGroup(*[Dot(radius=0.07, color=MAGENTA) for _ in range(NB)])
        bph, bw = rng.uniform(0, 2 * np.pi, NB), rng.uniform(1.6, 4.2, NB)
        clk4 = {"t": 0.0}

        def bit_upd(m, dt):
            clk4["t"] += dt
            t = clk4["t"]
            for j, d in enumerate(bits):
                a = bang[j] + 0.35 * t
                d.move_to(HC + 1.36 * np.array([np.cos(a), np.sin(a), 0]))
                on = np.sin(bw[j] * t + bph[j]) > 0.25
                d.set_fill(MAGENTA, 1.0 if on else 0.18)

        bit_upd(bits, 0.0)
        # small surface-code patch with a hole (a defect)
        SP = 0.62
        gx, gy = range(-7, 8), range(-4, 5)
        keep = {(i, j) for i in gx for j in gy
                if np.hypot(i * SP - HC[0], j * SP + 0.1 - HC[1]) > 1.82}
        pos = lambda i, j: np.array([i * SP, j * SP + 0.1, 0.0])
        lat_edges = VMobject()
        for i, j in keep:
            for di, dj in ((1, 0), (0, 1)):
                if (i + di, j + dj) in keep:
                    lat_edges.start_new_path(pos(i, j))
                    lat_edges.add_line_to(pos(i + di, j + dj))
        lat_edges.set_stroke(MAGENTA, 1.6, 0.55)
        nodes = VGroup(*[Dot(pos(i, j), radius=0.05, color=MAGENTA) for i, j in sorted(keep)])
        plaq, pinfo = VGroup(), []
        for i in list(gx)[:-1]:
            for j in list(gy)[:-1]:
                if all(c in keep for c in ((i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1))):
                    sq = Square(side_length=SP).move_to(pos(i, j) + np.array([SP / 2, SP / 2, 0]))
                    sq.set_stroke(width=0)
                    sq.set_fill(GOLD if (i + j) % 2 == 0 else CYAN, 0.0)
                    plaq.add(sq)
                    pinfo.append((GOLD if (i + j) % 2 == 0 else CYAN, rng.uniform(1.2, 3.2), rng.uniform(0, 6.3)))
        clk4b = {"t": 0.0}

        def plaq_upd(m, dt):
            clk4b["t"] += dt
            t = clk4b["t"]
            ramp = min(1.0, t / 0.6)
            for sq, (col, w, ph) in zip(plaq, pinfo):
                s = np.sin(w * t + ph)
                sq.set_fill(col, ramp * 0.34 * max(0.0, s) ** 3)

        static4 = VGroup(halo, lat_edges, nodes, bh, bits)
        halo.set_z_index(0); bh.set_z_index(3); bits.set_z_index(4)
        slide(t3, static4, [BR, BR, BR], title3, title4)                                                   # 16.2  (T3 out)
        bits.add_updater(bit_upd)
        plaq.add_updater(plaq_upd)
        plaq.set_z_index(-1)
        self.add(plaq)
        self.wait(3.2)                                                                     # 19.4
        bits.clear_updaters(); plaq.clear_updaters()
        t4 = VGroup(static4, plaq)

        # =====================================================================
        # 5. PROOFS = PROGRAMS = PHYSICS   19.4 - 23.4   (4.0 s)
        # =====================================================================
        self.caption("A proof is a program.", start=0.5, dur=3.3)
        title5 = topic_title("PROOFS  ·  PROGRAMS  ·  PHYSICS", [GOLD, MAGENTA, CYAN])
        BXY, BWD, BHT = 0.15, 3.4, 2.3
        cols5 = [GOLD, MAGENTA, CYAN]
        xs5 = [-4.3, 0.0, 4.3]
        boxes, names = VGroup(), VGroup()
        for x, col, nm in zip(xs5, cols5, ["logic", "code", "physics"]):
            bx_ = RoundedRectangle(width=BWD, height=BHT, corner_radius=0.22).move_to([x, BXY, 0])
            neon(bx_, col, 3.0)
            bx_.set_fill("#0A1020", 0.9)
            boxes.add(bx_)
            names.add(Text(nm, font=FONT, font_size=24, color=col).move_to([x, BXY - 0.82, 0]))
        f_logic = MathTex(r"A \Rightarrow B", font_size=66, color=GOLD).move_to([xs5[0], BXY + 0.2, 0])
        f_code = MathTex(r"f : A \to B", font_size=66, color=MAGENTA).move_to([xs5[1], BXY + 0.2, 0])
        f_phys = MathTex(r"A \rightsquigarrow B", font_size=66, color=CYAN).move_to([xs5[2], BXY + 0.2, 0])
        eq1 = equals_link([-2.15, BXY, 0], [GOLD, MAGENTA])
        eq2 = equals_link([2.15, BXY, 0], [MAGENTA, CYAN])
        top_arc = ArcBetweenPoints([xs5[0], BXY + BHT / 2, 0], [xs5[2], BXY + BHT / 2, 0], angle=-0.6)
        top_arc.set_stroke([GOLD, MAGENTA, CYAN], width=2.4)
        top_arc.set_stroke([GOLD, MAGENTA, CYAN], width=7.5, opacity=0.16, background=True)
        eq3 = equals_link(top_arc.point_from_proportion(0.5), [MAGENTA, MAGENTA], half=0.3, gap=0.1)
        eq3.set_z_index(2)
        eq3_bg = Circle(radius=0.3).move_to(top_arc.point_from_proportion(0.5)).set_fill(BG, 1.0).set_stroke(width=0)
        eq3_bg.set_z_index(1)
        static5 = VGroup(boxes, names)
        slide(t4, static5, [BR, BR, BR], title4, title5)                                                   # 20.2  (T4 out)
        self.play(LaggedStart(Write(f_logic), Write(f_code), Write(f_phys), lag_ratio=0.35),
                  run_time=1.0)                                                            # 21.2
        self.play(FadeIn(eq1, scale=1.3), FadeIn(eq2, scale=1.3), Create(top_arc), FadeIn(eq3), FadeIn(eq3_bg),
                  run_time=0.5)                                                            # 21.7
        self.play(ShowPassingFlash(top_arc.copy().set_stroke(WHITE_, 7, 1.0), time_width=0.5),
                  Indicate(eq1, scale_factor=1.15, color=WHITE_), Indicate(eq2, scale_factor=1.15, color=WHITE_),
                  run_time=1.0)                                                            # 22.7
        self.wait(0.7)                                                                     # 23.4
        t5 = VGroup(static5, f_logic, f_code, f_phys, eq1, eq2, eq3, eq3_bg, top_arc)

        # =====================================================================
        # FINALE: strands converge on the centre, brightening   23.4 - 27.3
        # =====================================================================
        C = ValueTracker(0.0)
        PHT = ValueTracker(st["off"])
        B = ValueTracker(0.0)

        def make_strands():
            cv, ph, bv = C.get_value(), PHT.get_value(), B.get_value()
            xs = np.linspace(-7.5, 7.5, 160)
            g = VGroup()
            for i, col in enumerate(STR_COLS):
                env = 1 - cv * (1 - np.minimum(1.0, np.abs(xs) / 5.5) ** 1.1)
                ys = Y0 * (1 - cv) + AMP * (1 - 0.2 * cv) * env * np.sin(K_ * (xs + ph) + STR_PH[i])
                m = VMobject().set_points_smoothly([[x, y, 0] for x, y in zip(xs, ys)])
                wd = 3.5 + 3.5 * bv
                m.set_stroke(col, wd, opacity=min(1.0, bv * 1.15))
                m.set_stroke(col, wd * 3.2, opacity=0.2 * bv, background=True)
                g.add(m)
            return g

        strands = always_redraw(make_strands)
        strands.set_z_index(-4)
        off0 = st["off"]
        self.add(strands)
        self.play(FadeOut(t5, shift=LEFT * 1.8), FadeOut(title5),
                  L.animate.set_value(0.0), B.animate.set_value(0.5),
                  PHT.animate(rate_func=linear).set_value(off0 + 0.22 * 0.8),
                  *[w.animate.set_value(1.0) for w in W],
                  run_time=0.8)                                                            # 24.2
        braid.clear_updaters()
        self.remove(braid)
        self.play(C.animate(rate_func=smooth).set_value(1.0),
                  B.animate(rate_func=smooth).set_value(1.0),
                  PHT.animate(rate_func=linear).set_value(off0 + 0.22 * 0.8 + 0.5 * 2.8),
                  run_time=2.8)                                                            # 27.0
        centre = glow_dot(ORIGIN, WHITE_, r=0.12, layers=6)
        self.play(FadeIn(centre, scale=0.4), run_time=0.3)                                 # 27.3
        strands.clear_updaters()
        self.remove(L, C, PHT, B, SPD, *W)
        self.fade_all(0.7)                                                                 # 28.0
        self.pad_to()
