from math import comb, log2

from style import *

# ===========================================================================
#  ACT 3 - INFORMATION   (35 s)      hand-off object: a swarm of bits / particles
#   A  0.0- 7.0  CS   / BASICS       bits, 1011 = 11, gates, half-adder
#   B  7.0-14.0  CS -> MATH / HS     twenty questions: 64 tiles halve; 1,000,000 -> 20 bits
#   C 14.0-22.0  MATH -> PHYS / UNI  tiles become gas; W and entropy rise; H vs S
#   D 22.0-29.0  CS / UNI            noisy channel, repetition code repairs flips
#   E 29.0-35.0  FRONTIER            horizon bits + surface-code lattice
# ===========================================================================

rng = np.random.default_rng(11)
PAL = "#FFE08A"


def P3(x, y):
    return np.array([x, y, 0.0])


# ---------------------------------------------------------------- helpers
def glow_text(s, color, size=96, font=MONO):
    t = Text(s, font=font, font_size=size, color=color, weight=BOLD)
    h = t.copy().set_fill(opacity=0).set_stroke(color, width=12, opacity=0.22)
    return VGroup(h, t)


def bit_txt(ch, color=MAGENTA, size=40):
    t = Text(ch, font=MONO, font_size=size, color=color, weight=BOLD)
    t.set_stroke(color, width=8, opacity=0.2, background=True)
    return t


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


def set_tex_color(m, color):
    m.set_color(color)
    return m


class Act3(FilmScene):
    DURATION = BUDGET["act3"]

    # ------------------------------------------------------------ utilities
    def until(self, t):
        """Wait until absolute scene time t (no-op if already past)."""
        remain = t - self.renderer.time
        if remain > 0.02:
            self.wait(remain)
        elif remain < -0.25:
            print(f"!! Act3 behind schedule by {-remain:.2f}s at target {t}")

    def overlays(self):
        # concept tag
        self.tag("03", "INFORMATION", WHITE_, start=0.2, dur=3.5)
        # discipline badges (each starts 0.35 before the previous ends -> cross-fade)
        self.badge("COMPUTER SCIENCE", MAGENTA, 0.2, 7.0)        # A      0.2 - 7.2
        self.badge("COMPUTER SCIENCE", MAGENTA, 6.85, 4.4)       # B1     6.85 - 11.25
        self.badge("MATHEMATICS", GOLD, 10.9, 4.85)              # B2+C1 10.9 - 15.75
        self.badge("PHYSICS", CYAN, 15.4, 6.95)                  # C2    15.4 - 22.35
        self.badge("COMPUTER SCIENCE", MAGENTA, 22.0, 7.35)      # D     22.0 - 29.35
        tri = VGroup(Text("MATHEMATICS", font=FONT, font_size=18, color=GOLD, weight=BOLD),
                     Text("PHYSICS", font=FONT, font_size=18, color=CYAN, weight=BOLD),
                     Text("COMPUTER SCIENCE", font=FONT, font_size=18, color=MAGENTA, weight=BOLD))
        tri.arrange(RIGHT, buff=0.3).to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        self._timed(tri, 29.0, 5.9, fade=0.35, max_op=0.95)      # E     29.0 - 34.9
        # ladder
        self.level(0, MAGENTA, 0.2, 7.0)
        self.level(1, MAGENTA, 6.85, 4.4)
        self.level(1, GOLD, 10.9, 3.45)
        self.level(2, GOLD, 14.0, 1.75)
        self.level(2, CYAN, 15.4, 6.95)
        self.level(2, MAGENTA, 22.0, 7.35)
        self.level(3, WHITE_, 29.0, 5.9)
        # narration: one caption per beat
        self.caption("Two symbols, 0 and 1, are enough to compute.", 0.6, 5.8)
        self.caption("Each yes-or-no answer is one bit. A million things need only twenty.", 7.4, 6.2)
        self.caption("Disorder is missing information. Entropy counts the bits you don't know.",
                     14.3, 7.4)
        self.caption("Add a little redundancy, and errors can be repaired.", 22.4, 6.4)
        self.caption("Black holes, error-correcting codes, spacetime: one puzzle?", 29.3, 5.0)

    # =====================================================================
    # A  0 - 7   BITS -> GATES -> HALF ADDER  (magenta)
    # =====================================================================
    def beat_A(self):
        b0 = glow_text("0", MAGENTA, 110).move_to(P3(-1.3, 0.7))
        b1 = glow_text("1", MAGENTA, 110).move_to(P3(1.3, 0.7))
        off = label("off", DIM, 22).move_to(P3(-1.3, -0.35))
        on = label("on", DIM, 22).move_to(P3(1.3, -0.35))
        self.play(FadeIn(b0, scale=0.6), FadeIn(b1, scale=0.6), FadeIn(off), FadeIn(on),
                  run_time=0.6)                                                  # 0.6

        xs = [-3.0, -1.8, -0.6, 0.6]
        row_y = 0.7
        n1 = glow_text("1", MAGENTA, 110).move_to(P3(xs[2], row_y))
        n2 = glow_text("1", MAGENTA, 110).move_to(P3(xs[3], row_y))
        self.play(b1.animate.move_to(P3(xs[0], row_y)), b0.animate.move_to(P3(xs[1], row_y)),
                  TransformFromCopy(b1, n1), TransformFromCopy(b1, n2),
                  FadeOut(off), FadeOut(on), run_time=0.7)                       # 1.3
        vals = VGroup(*[label(v, WHITE_ if v != "4" else DIM, 26).move_to(P3(x, -0.3))
                        for v, x in zip(["8", "4", "2", "1"], xs)])
        eq = MathTex(r"=\,11", color=WHITE_).scale(1.7).move_to(P3(2.6, row_y))
        self.play(FadeIn(vals, shift=UP * 0.1), Write(eq), run_time=0.6)         # 1.9
        self.wait(0.15)                                                          # 2.05
        bits = VGroup(b0, b1, n1, n2, vals, eq)

        # ---- four gates: AND, OR, NOT, XOR   (inputs A=1, B=0) -----------
        gy = 0.5
        specs = [(-4.8, "and", and_gate, "AND", (1, 0), 0),
                 (-1.6, "or", or_gate, "OR", (1, 0), 1),
                 (1.6, "not", not_gate, "NOT", (0,), 1),
                 (4.8, "xor", xor_gate, "XOR", (1, 0), 1)]
        gates, names, dimw, litw = [], [], [], []
        for gx, kind, mk, nm, ins, out in specs:
            gates.append(mk().shift(P3(gx, gy)))
            names.append(label(nm, WHITE_, 22).move_to(P3(gx, gy - 1.0)))
            if kind == "not":
                in_pts = [[(gx - 1.4, gy), (gx - 0.5, gy)]]
                out_pts = [(gx + 0.7, gy), (gx + 1.4, gy)]
            else:
                xi = gx - (0.6 if kind == "and" else 0.5)
                in_pts = [[(gx - 1.4, gy + .28), (xi, gy + .28)], [(gx - 1.4, gy - .28), (xi, gy - .28)]]
                xo = gx + (0.55 if kind == "and" else 0.65)
                out_pts = [(xo, gy), (gx + 1.4, gy)]
            for pts, v in zip(in_pts, ins):
                (litw if v else dimw).append(wire(pts, bool(v)))
            (litw if out else dimw).append(wire(out_pts, bool(out)))
        dimw_g = VGroup(*[wire_ for wire_ in dimw])
        gate_grp = VGroup(*gates, *names)
        self.play(FadeOut(bits, run_time=0.3),
                  LaggedStart(FadeIn(dimw_g), FadeIn(gate_grp), lag_ratio=0.15, run_time=0.6))  # 2.65
        self.play(LaggedStart(*[Create(w) for w in litw], lag_ratio=0.08), run_time=0.7)           # 3.35
        self.wait(0.1)
        self.play(FadeOut(VGroup(dimw_g, *litw, gate_grp)), run_time=0.3)                          # 3.75

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
        dimh = VGroup(*[wire(p) for p in [railA, railB, dropA, dropB, outS, outC]])
        litw_in = [wire(railA, True), wire(railB, True), wire(dropA, True), wire(dropB, True)]
        litw_c = wire(outC, True)
        srcA = glow_text("1", MAGENTA, 46).move_to(P3(-5.3, yA))
        srcB = glow_text("1", MAGENTA, 46).move_to(P3(-5.3, yB))
        lA = label("A", DIM, 22).move_to(P3(-6.0, yA))
        lB = label("B", DIM, 22).move_to(P3(-6.0, yB))
        jd = VGroup(Dot(P3(jA, yA), radius=0.05, color=MAGENTA), Dot(P3(jB, yB), radius=0.05, color=MAGENTA))
        self.play(FadeIn(dimh), FadeIn(xor), FadeIn(andg), FadeIn(xor_nm), FadeIn(and_nm),
                  FadeIn(srcA), FadeIn(srcB), FadeIn(lA), FadeIn(lB), run_time=0.5)               # 4.25
        self.play(LaggedStart(*[Create(m) for m in litw_in], lag_ratio=0.12), FadeIn(jd),
                  run_time=0.45)                                                                  # 4.7
        dark = interpolate_color(ManimColor(MAGENTA), ManimColor(BG), 0.6)
        sumb = glow_text("0", dark, 46).move_to(P3(3.3, yx))
        carb = glow_text("1", MAGENTA, 46).move_to(P3(3.3, ya))
        sl = label("sum", DIM, 20).move_to(P3(3.3, yx - 0.55))
        cl = label("carry", DIM, 20).move_to(P3(3.3, ya - 0.55))
        self.play(Create(litw_c), FadeIn(sumb, scale=0.7), FadeIn(sl), run_time=0.4)              # 5.1
        self.play(FadeIn(carb, scale=0.7), FadeIn(cl), run_time=0.25)                             # 5.35
        res = MathTex(r"1+1=", r"10_2").scale(0.95).move_to(P3(5.35, 0.25))
        res[1].set_color(MAGENTA)
        self.play(Write(res), run_time=0.6)                                                       # 5.95
        self.until(6.2)                                                                           # 6.2
        self.A_left = VGroup(dimh, xor, andg, xor_nm, and_nm, srcA, srcB, lA, lB, jd, *litw_in,
                             litw_c, sumb, carb, sl, cl, res)

    # =====================================================================
    # B  7 - 14   TWENTY QUESTIONS: a million things -> 20 bits
    # =====================================================================
    def beat_B(self):
        N, target = 64, 42
        pitch = 0.19
        TY = 1.2                      # tile row y
        tiles = VGroup(*[Rectangle(width=0.15, height=0.75, stroke_width=0,
                                   fill_color=MAGENTA, fill_opacity=0.8) for _ in range(N)])
        tiles.arrange(RIGHT, buff=pitch - 0.15).move_to([0, TY, 0])
        tiles[target].set_stroke(WHITE_, width=1.6, opacity=0.9)
        top = label("64 tiles  (standing in for a million)", DIM, 24).move_to([0, 2.3, 0])

        def box_for(lo, hi):
            l = tiles[lo].get_left()[0] - 0.07
            r = tiles[hi].get_right()[0] + 0.07
            b = Rectangle(width=r - l, height=1.05, stroke_color=MAGENTA, stroke_width=2.5,
                          fill_opacity=0)
            return b.move_to([(l + r) / 2, TY, 0])

        def size_lab(lo, hi):
            n = hi - lo + 1
            g = label(f"{n} left", WHITE_, 24)
            return g.move_to([(tiles[lo].get_left()[0] + tiles[hi].get_right()[0]) / 2, TY - 0.75, 0])

        box = box_for(0, N - 1)
        lab = size_lab(0, N - 1)
        reg_y = -0.55
        reg_lab = label("answers", DIM, 24).move_to(P3(-3.1, reg_y))
        slots = [P3(-1.5 + 0.6 * k, reg_y) for k in range(6)]
        coin = label("each answer: a fair coin flip, probability 1/2  =  1 bit", DIM, 22).move_to(P3(0, -1.2))

        # hand-off A -> B: half-adder dissolves, the row of tiles appears in its place
        self.play(FadeOut(self.A_left), run_time=0.4)                                   # 6.6
        self.play(FadeIn(tiles), FadeIn(box), FadeIn(lab), FadeIn(top),
                  FadeIn(reg_lab), run_time=0.6)                                        # 7.2
        lo, hi = 0, N - 1
        bits = []
        for k in range(6):
            half = (hi - lo + 1) // 2
            mid = lo + half                       # first index of the right half
            bx = (tiles[mid - 1].get_right()[0] + tiles[mid].get_left()[0]) / 2
            div = DashedLine([bx, TY - 0.6, 0], [bx, TY + 1.0, 0], color=WHITE_, stroke_width=2.5,
                             dash_length=0.08)
            self.play(FadeIn(div), run_time=0.2)
            ans = 1 if target >= mid else 0
            if ans:
                excl = list(range(lo, mid)); lo = mid
            else:
                excl = list(range(mid, hi + 1)); hi = mid - 1
            bit = glow_text(str(ans), MAGENTA, 40).move_to(slots[k])
            bits.append(bit)
            nb, nl = box_for(lo, hi), size_lab(lo, hi)
            anims = [VGroup(*[tiles[i] for i in excl]).animate.set_fill(MAGENTA, 0.09),
                     Transform(box, nb), ReplacementTransform(lab, nl),
                     FadeIn(bit, scale=0.6), FadeOut(div)]
            if k == 1:
                anims.append(FadeIn(coin))
            self.play(*anims, run_time=0.45)                                             # +0.65 each
            lab = nl
        bits = VGroup(*bits)                                                             # 11.1
        found = label("found", WHITE_, 24).move_to(lab)
        eq42 = label("= 42", WHITE_, 30).next_to(bits, RIGHT, buff=0.35)
        self.play(ReplacementTransform(lab, found), FadeIn(eq42),
                  Flash(tiles[target], color=MAGENTA, line_length=0.3, flash_radius=0.45),
                  run_time=0.45)                                                         # 11.55

        # magenta -> gold: the counting turns into mathematics
        counter = label("1,000,000 things   →   20 bits", WHITE_, 44,
                        t2c={"1,000,000": GOLD, "20": GOLD}).move_to(P3(0, -1.85))
        formula = MathTex(r"2^{20}\approx 1{,}000{,}000", color=GOLD).scale(0.85).move_to(P3(0, -2.5))
        self.play(tiles.animate.set_fill(GOLD, 0.85), bits.animate.set_color(GOLD),
                  FadeOut(box), FadeOut(found), FadeOut(eq42), FadeOut(coin), FadeOut(top),
                  FadeIn(counter, shift=UP * 0.2), FadeIn(formula, shift=UP * 0.1),
                  run_time=0.9)                                                          # 12.45
        self.until(13.0)                                                                 # 13.0
        self.B_extra = VGroup(counter, formula, bits, reg_lab)
        self.tiles = tiles

    # =====================================================================
    # C  14 - 22   THE SAME TILES BECOME A GAS;  W, entropy, H vs S
    # =====================================================================
    def beat_C(self):
        tiles = self.tiles
        NP = 64
        X0, X1, Y0, Y1 = -6.1, -0.7, -1.4, 2.0
        XM = (X0 + X1) / 2
        # ordered start: 8 x 8 lattice in the left half
        gx = np.linspace(-5.85, -3.65, 8)
        gy = np.linspace(1.7, -1.1, 8)
        slots = np.array([[gx[i // 8], gy[i % 8]] for i in range(NP)])

        def style_dot(d, col):
            d.set_fill(col, 1.0)
            d.set_stroke(col, width=8, opacity=0.25, background=True)

        targets = []
        for i in range(NP):
            d = Dot(radius=0.07, color=GOLD).move_to([slots[i, 0], slots[i, 1], 0])
            style_dot(d, GOLD)
            targets.append(d)

        box = Rectangle(width=X1 - X0, height=Y1 - Y0).move_to([(X0 + X1) / 2, (Y0 + Y1) / 2, 0])
        neon(box, GOLD, 3.5)
        box.add_updater(lambda m: None)
        part = DashedLine([XM, Y0, 0], [XM, Y1, 0], color=WHITE_, stroke_width=2.5,
                          dash_length=0.1).set_stroke(opacity=0.7)

        # readouts
        anchor1 = P3(X0, -1.85)
        anchor2 = P3(X0, -2.3)

        def mk_txt(s, anchor):
            t = Text(s, font=MONO, font_size=22, color=WHITE_)
            t.move_to(anchor).align_to(anchor, LEFT)
            t.add_updater(lambda m: None)
            return t

        wtxt = mk_txt("W = 1", anchor1)
        btxt = mk_txt("log2 W = 0 bits missing", anchor2)
        bar = Rectangle(width=0.02, height=0.09, stroke_width=0, fill_color=CYAN, fill_opacity=0.9)
        bar.move_to(P3(X0 + 0.01, -2.58)).add_updater(lambda m: None)
        BAR_MAX = X1 - X0

        # hand-off B -> C: the same 64 tiles fly into the box as particles
        anims = [Transform(t, d) for t, d in zip(tiles, targets)]
        self.play(AnimationGroup(*anims, lag_ratio=0.01, run_time=1.4),
                  FadeOut(self.B_extra, run_time=0.5),
                  FadeIn(box, run_time=0.8), FadeIn(part, run_time=0.8),
                  FadeIn(wtxt, run_time=0.8), FadeIn(btxt, run_time=0.8),
                  FadeIn(bar, run_time=0.8))                                             # 14.4
        # the animation group swallowed `tiles` into a throw-away Group: rebuild a scene-level swarm
        self.remove(*list(tiles))
        tiles = VGroup(*list(tiles))
        self.add(tiles)

        # ---- physics of the gas -------------------------------------------
        st = {"go": False, "rel": False, "t": 0.0, "ct": 0.0, "acc": 0.0, "nl": float(NP),
              "shown": (-1, -1)}
        P = slots.copy()
        ang = rng.uniform(0, TAU, NP)
        spd = rng.uniform(0.7, 1.7, NP)
        V = np.stack([np.cos(ang) * spd, np.sin(ang) * spd], 1)
        C_GOLD, C_CYAN = ManimColor(GOLD), ManimColor(CYAN)

        def sim(m, dt):
            if not st["go"]:
                return
            dt = min(dt, 0.05)
            st["t"] += dt
            P[:] += V * dt
            xmax = (X1 if st["rel"] else XM) - 0.07
            xmin, ymin, ymax = X0 + 0.07, Y0 + 0.07, Y1 - 0.07
            hit = P[:, 0] > xmax
            P[hit, 0] = 2 * xmax - P[hit, 0]; V[hit, 0] *= -1
            hit = P[:, 0] < xmin
            P[hit, 0] = 2 * xmin - P[hit, 0]; V[hit, 0] *= -1
            hit = P[:, 1] > ymax
            P[hit, 1] = 2 * ymax - P[hit, 1]; V[hit, 1] *= -1
            hit = P[:, 1] < ymin
            P[hit, 1] = 2 * ymin - P[hit, 1]; V[hit, 1] *= -1
            for d, p in zip(m, P):
                d.move_to([p[0], p[1], 0])
            # colour: gold -> cyan once released
            if st["rel"] and st["ct"] < 1.0:
                st["ct"] = min(1.0, st["ct"] + dt / 1.6)
                col = C_GOLD.interpolate(C_CYAN, st["ct"])
                for d in m:
                    style_dot(d, col)
                box.set_stroke(col, width=3.5)
                box.set_stroke(col, width=11.2, opacity=0.18, background=True)
            # readouts (throttled)
            st["acc"] += dt
            if st["acc"] >= 0.1:
                st["acc"] = 0.0
                nl = float((P[:, 0] < XM).sum())
                st["nl"] += (nl - st["nl"]) * 0.35
                n = int(round(st["nl"]))
                W = comb(NP, n)
                bits_ = int(round(log2(W)))
                if (n, bits_) != st["shown"]:
                    st["shown"] = (n, bits_)
                    for t_, s_, anc in ((wtxt, f"W = {W:,}", anchor1),
                                        (btxt, f"log2 W = {bits_} bits missing", anchor2)):
                        new = Text(s_, font=MONO, font_size=22, color=WHITE_)
                        new.move_to(anc).align_to(anc, LEFT)
                        t_.become(new)
                    w = max(0.02, BAR_MAX * log2(W) / NP)
                    bar.stretch_to_fit_width(w)
                    bar.align_to(P3(X0, 0), LEFT)

        tiles.add_updater(sim)
        self.until(14.9)                                                                 # 14.9
        st["go"] = True
        st["rel"] = True
        self.play(FadeOut(part), run_time=0.4)                                           # 15.3

        # ---- Shannon vs Boltzmann, same shape ------------------------------
        PX = 3.6
        lab1 = label("information  ·  Shannon", GOLD, 20).move_to(P3(PX, 2.7))
        Hf = MathTex("H", "=", r"-\sum_i", "p_i", r"\log", "p_i", color=GOLD).scale(1.1).move_to(P3(PX, 1.85))
        Hf[4].set_color(WHITE_)
        brg = MathTex(r"p_i=\tfrac{1}{W}", r"\;\Rightarrow\;", "H", "=", r"\log", "W", color=GOLD)
        brg.scale(0.95).move_to(P3(PX, 0.85))
        brg[1].set_color(DIM)
        brg[4].set_color(WHITE_); brg[5].set_color(WHITE_)
        lab2 = label("physics  ·  Boltzmann", CYAN, 20).move_to(P3(PX, -0.1))
        Sf = MathTex("S", "=", "k_B", r"\log", "W", color=CYAN).scale(1.1).move_to(P3(PX, -0.65))
        Sf[3].set_color(WHITE_); Sf[4].set_color(WHITE_)
        note = label("k_B only converts bits into joules per kelvin", DIM, 18).move_to(P3(PX, -1.5))
        self.until(15.6)
        self.play(FadeIn(lab1), Write(Hf), run_time=0.9)                                  # 16.5
        self.until(16.8)
        self.play(FadeIn(brg, shift=UP * 0.1), run_time=0.9)                              # 17.7
        self.until(18.0)
        self.play(FadeIn(lab2), Write(Sf), run_time=0.9)                                  # 18.9
        self.until(19.1)
        r1 = SurroundingRectangle(brg[4:6], color=WHITE_, buff=0.08, stroke_width=2)
        r2 = SurroundingRectangle(Sf[3:5], color=WHITE_, buff=0.08, stroke_width=2)
        self.play(Create(r1), Create(r2), FadeIn(note), run_time=0.7)                     # 19.8
        self.play(Indicate(r1, color=WHITE_, scale_factor=1.15),
                  Indicate(r2, color=WHITE_, scale_factor=1.15), run_time=0.7)            # 20.5
        self.until(21.2)

        # hand-off C -> D: four particles become the message bits, the rest fade
        self.C_stuff = VGroup(box, wtxt, btxt, bar, lab1, Hf, brg, lab2, Sf, note, r1, r2)
        self.C_tiles = tiles
        self.C_st = st
        self.C_sim = sim

    # =====================================================================
    # D  22 - 29   NOISY CHANNEL + REPETITION CODE   (magenta)
    # =====================================================================
    def beat_D(self):
        tiles = self.C_tiles
        tiles.clear_updaters()
        for m in (self.C_stuff[0], self.C_stuff[1], self.C_stuff[2], self.C_stuff[3]):
            m.clear_updaters()

        msg = [1, 0, 1, 1]
        offs = [-0.93, -0.31, 0.31, 0.93]
        SX, RX = -4.6, 4.6
        Y_PLAIN, Y_CODE, Y_DEC = 1.8, 0.2, -1.4
        sent_p = [bit_txt(str(b), MAGENTA, 40).move_to(P3(SX + o, Y_PLAIN)) for b, o in zip(msg, offs)]

        # which dots turn into the message bits (the nearest to each slot); others fade
        pick = []
        for g in sent_p:
            pos = np.array([d.get_center() for d in tiles])
            j = int(np.argmin(np.linalg.norm(pos - g.get_center(), axis=1)))
            while j in pick:
                pos[j] = 1e3
                j = int(np.argmin(np.linalg.norm(pos - g.get_center(), axis=1)))
            pick.append(j)
        others = [tiles[j] for j in range(len(tiles)) if j not in pick]

        # channel band
        band = Rectangle(width=4.2, height=4.7).move_to(P3(0, 0.15))
        band.set_stroke(MAGENTA, width=2, opacity=0.45)
        band = DashedVMobject(band, num_dashes=60)

        def noisy(y, seed):
            r = np.random.default_rng(seed)
            xs = np.linspace(-2.1, 2.1, 90)
            ys = y + 0.05 * np.sin(9 * xs) + r.normal(0, 0.035, xs.size)
            m = VMobject()
            m.set_points_as_corners(np.stack([xs, ys, np.zeros_like(xs)], 1))
            return m.set_stroke(MAGENTA, width=2, opacity=0.4)

        wires = VGroup(noisy(Y_PLAIN, 1), noisy(Y_CODE, 2))
        ch_lab = label("noisy channel", MAGENTA, 22).move_to(P3(0, 2.75))
        l_from = label("message", DIM, 20).move_to(P3(SX, 2.5))
        l_to = label("received", DIM, 20).move_to(P3(RX, 2.5))

        self.C_stuff_fade = [m for m in self.C_stuff]
        anims = [FadeTransform(tiles[j], g) for j, g in zip(pick, sent_p)]
        self.play(*anims, *[FadeOut(m) for m in others], *[FadeOut(m) for m in self.C_stuff],
                  run_time=0.8)                                                          # 22.0 (start of D)
        self.until(22.0)
        self.play(FadeIn(band), FadeIn(wires), FadeIn(ch_lab), FadeIn(l_from), FadeIn(l_to),
                  run_time=0.7)                                                          # 22.7

        # ---- 1. plain transmission: one flip goes unnoticed --------------
        recv_x = [RX + o for o in offs]
        recv_p = self.transmit(sent_p, recv_x, {2: "0"}, 40)                             # 23.85
        ring = Circle(radius=0.32, color=WHITE_, stroke_width=2.5).move_to(recv_p[2])
        bad = Text("one flip: undetected", font=FONT, font_size=22,
                   color=DIM).move_to(P3(RX, Y_PLAIN - 0.75))
        self.play(Create(ring), FadeIn(bad), run_time=0.4)                               # 24.25
        self.until(24.4)

        # ---- 2. add redundancy: every bit is sent three times -------------
        old_row = VGroup(*sent_p, *recv_p, ring, bad)
        centres = [-1.65, -0.55, 0.55, 1.65]
        sent_c, blocks = [], []
        for b, c in zip(msg, centres):
            blk = [bit_txt(str(b), MAGENTA, 30).move_to(P3(SX + c + d, Y_CODE)) for d in (-0.31, 0, 0.31)]
            blocks.append(blk)
            sent_c += blk
        rep = label("repeat each bit three times", DIM, 20).move_to(P3(SX, Y_CODE + 0.75))
        copy_anims = []
        for i, blk in enumerate(blocks):
            for g in blk:
                copy_anims.append(TransformFromCopy(sent_p[i], g))
        self.play(old_row.animate.set_opacity(0.25), *copy_anims, FadeIn(rep), run_time=0.7)   # 25.1

        # ---- 3. coded transmission with two flips, then majority vote -----
        recv_cx = [RX + c + d for c in centres for d in (-0.31, 0, 0.31)]
        flips = {1: "0", 8: "0"}
        recv_c = self.transmit(sent_c, recv_cx, flips, 30)                               # 26.25
        rings = VGroup(*[Circle(radius=0.26, color=WHITE_, stroke_width=2.5).move_to(recv_c[i])
                         for i in flips])
        unders = VGroup(*[Line(P3(RX + c - 0.5, Y_CODE - 0.4), P3(RX + c + 0.5, Y_CODE - 0.4))
                          .set_stroke(DIM, 2) for c in centres])
        arrows = VGroup(*[Arrow(P3(RX + c, Y_CODE - 0.45), P3(RX + c, Y_DEC + 0.45), buff=0, color=DIM,
                                stroke_width=2.5, max_tip_length_to_length_ratio=0.3)
                          for c in centres])
        dec = [bit_txt(str(b), MAGENTA, 40).move_to(P3(RX + c, Y_DEC)) for b, c in zip(msg, centres)]
        vote = label("majority vote", DIM, 22).next_to(P3(RX + centres[0], Y_DEC), LEFT, buff=0.55)
        ok = Text("✓  repaired", font=FONT, font_size=26, color=WHITE_).move_to(P3(RX, Y_DEC - 0.75))
        self.play(Create(rings), run_time=0.3)                                           # 26.55
        self.play(LaggedStart(Create(unders), FadeIn(vote), lag_ratio=0.1),
                  LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(d, scale=0.6) for d in dec], lag_ratio=0.1),
                  run_time=0.8)                                                          # 27.35
        self.play(FadeIn(ok, shift=UP * 0.1), run_time=0.4)                              # 27.75
        self.until(28.3)
        self.D_all = VGroup(band, wires, ch_lab, l_from, l_to, old_row, rep, rings, unders, arrows, vote,
                            ok, *sent_c, *recv_c, *dec)

    def transmit(self, sent, dest_xs, flips, size):
        """Send copies of `sent` glyphs to dest_xs; indices in `flips` (idx -> new char)
        are corrupted in the middle of the channel."""
        copies = [g.copy() for g in sent]
        self.add(*copies)
        a1 = []
        for i, c in enumerate(copies):
            y = c.get_center()[1]
            tx = (c.get_center()[0] + dest_xs[i]) / 2 if i in flips else dest_xs[i]
            a1.append(c.animate.move_to(P3(tx, y)))
        self.play(*a1, run_time=0.55, rate_func=smooth)
        news = {}
        a2, fl = [], []
        for i, ch in flips.items():
            c = copies[i]
            n = bit_txt(ch, WHITE_, size).move_to(c.get_center())
            news[i] = n
            a2 += [FadeTransform(c, n), Flash(n.get_center(), color=WHITE_, flash_radius=0.4,
                                              line_length=0.15)]
        self.play(*a2, run_time=0.25)
        a3 = [news[i].animate.move_to(P3(dest_xs[i], news[i].get_center()[1])) for i in flips]
        self.play(*a3, run_time=0.35)
        return [news.get(i, copies[i]) for i in range(len(copies))]

    # =====================================================================
    # E  29 - 35   FRONTIER: horizon bits + surface-code lattice
    # =====================================================================
    def beat_E(self):
        HC, HR = np.array([-0.9, 0.1, 0.0]), 1.12
        halo = VGroup(*[Circle(radius=HR + 0.1 + 0.16 * i).move_to(HC).set_stroke(width=0).set_fill(CYAN, 0.05)
                        for i in range(4)])
        bh = Circle(radius=HR).move_to(HC)
        bh.set_fill("#000000", 1.0)
        neon(bh, CYAN, 3.4)
        NB = 40
        bang = TAU * np.arange(NB) / NB
        bits = VGroup(*[Dot(radius=0.07, color=MAGENTA) for _ in range(NB)])
        bph, bw = rng.uniform(0, TAU, NB), rng.uniform(1.6, 4.2, NB)
        clk = {"t": 0.0}

        def bit_upd(m, dt):
            clk["t"] += dt
            t = clk["t"]
            ramp = min(1.0, t / 0.9)
            for j, d in enumerate(bits):
                a = bang[j] + 0.35 * t
                d.move_to(HC + 1.36 * np.array([np.cos(a), np.sin(a), 0]))
                on = np.sin(bw[j] * t + bph[j]) > 0.25
                d.set_fill(MAGENTA, ramp * (1.0 if on else 0.18))

        bit_upd(bits, 0.0)

        SP = 0.62
        gxr, gyr = range(-7, 8), range(-4, 5)
        pos = lambda i, j: HC + np.array([i * SP, j * SP, 0.0])
        keep = {(i, j) for i in gxr for j in gyr
                if np.hypot(i * SP, j * SP) > 1.82}
        lat_edges = VMobject()
        for i, j in keep:
            for di, dj in ((1, 0), (0, 1)):
                if (i + di, j + dj) in keep:
                    lat_edges.start_new_path(pos(i, j))
                    lat_edges.add_line_to(pos(i + di, j + dj))
        lat_edges.set_stroke(MAGENTA, 1.6, 0.55)
        nodes = VGroup(*[Dot(pos(i, j), radius=0.05, color=MAGENTA) for i, j in sorted(keep)])
        plaq, pinfo = VGroup(), []
        for i in list(gxr)[:-1]:
            for j in list(gyr)[:-1]:
                if all(c in keep for c in ((i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1))):
                    sq = Square(side_length=SP).move_to(pos(i, j) + np.array([SP / 2, SP / 2, 0]))
                    sq.set_stroke(width=0)
                    col = GOLD if (i + j) % 2 == 0 else CYAN
                    sq.set_fill(col, 0.0)
                    plaq.add(sq)
                    pinfo.append((col, rng.uniform(1.2, 3.2), rng.uniform(0, 6.3)))
        clk2 = {"t": 0.0}

        def plaq_upd(m, dt):
            clk2["t"] += dt
            t = clk2["t"]
            ramp = min(1.0, t / 0.9)
            for sq, (col, w, ph) in zip(plaq, pinfo):
                s = np.sin(w * t + ph)
                sq.set_fill(col, ramp * 0.34 * max(0.0, s) ** 3)

        halo.set_z_index(0); bh.set_z_index(3); bits.set_z_index(4)
        plaq.set_z_index(-1)
        static = VGroup(halo, lat_edges, nodes, bh)
        bits.add_updater(bit_upd)
        plaq.add_updater(plaq_upd)
        self.add(bits, plaq)
        # hand-off D -> E: the channel fades, the horizon and its code fade in
        self.play(FadeOut(self.D_all, run_time=0.35), FadeIn(static, run_time=0.7))                     # 29.0

        # horizon entropy ~ area
        NX = 5.3
        S = MathTex(r"S\;\propto\;A", color=CYAN).scale(1.2).move_to(P3(NX, 1.2))
        n1 = label("horizon entropy", DIM, 19).move_to(P3(NX, 0.45))
        n2 = label("scales with its area", DIM, 19).move_to(P3(NX, 0.1))
        area = Circle(radius=HR + 0.05).move_to(HC).set_stroke(CYAN, width=4, opacity=0.9)
        self.play(FadeIn(S, shift=UP * 0.1), FadeIn(n1), FadeIn(n2),
                  ShowPassingFlash(area, time_width=0.9), run_time=1.0)             # 30.0
        self.remove(area)
        # information ripples out through the code
        def ripple(delay):
            ring = Circle(radius=HR + 0.1).move_to(HC).set_stroke(CYAN, width=0, opacity=0)

            def f(m, a):
                a2 = min(1.0, max(0.0, (a - delay) / (1 - delay)))
                if a2 <= 0:
                    return
                m.become(Circle(radius=HR + 0.1 + 2.6 * a2).move_to(HC)
                         .set_stroke(CYAN, width=4, opacity=0.9 * (1 - a2) ** 1.2))
            return UpdateFromAlphaFunc(ring, f, run_time=2.6, rate_func=linear)
        self.play(ripple(0.0), ripple(0.35), run_time=2.6)                                # 32.6
        self.until(34.3)
        bits.clear_updaters()
        plaq.clear_updaters()
        self.fade_all(0.7)                                                                # 35.0

    # ------------------------------------------------------------ scene
    def construct(self):
        self.overlays()
        self.beat_A()
        self.beat_B()
        self.beat_C()
        self.beat_D()
        self.beat_E()
        self.pad_to()
