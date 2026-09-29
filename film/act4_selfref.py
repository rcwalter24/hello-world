from style import *
from manim.utils.rate_functions import ease_out_back

RED_Q = "#FF4D5A"


# =============================================================================
#  numpy helpers (precomputed once at the top of construct)
# =============================================================================
def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def soft_mask(h, w, frac=0.07):
    yy = np.minimum(np.arange(h), h - 1 - np.arange(h)) / (h * frac)
    xx = np.minimum(np.arange(w), w - 1 - np.arange(w)) / (w * frac)
    return smoothstep(yy)[:, None] * smoothstep(xx)[None, :]


def set_img(m, rgba):
    """Swap the pixels of an ImageMobject in place (keeps fades working)."""
    m.pixel_array = rgba
    m.orig_alpha_pixel_array = rgba[:, :, 3].copy()


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def ramp(v, stops, cols):
    v = np.clip(v, 0, 1)
    cols = np.array(cols, float)
    return np.stack([np.interp(v, stops, cols[:, c]) for c in range(3)], -1)


# ---- Mandelbrot -------------------------------------------------------------
MB_C = (-0.743643887037151, 0.131825904205330)


def mandel_nu(cx, cy, width, W, H, maxit):
    xs = cx + (np.arange(W) / W - 0.5) * width
    ys = cy + (0.5 - np.arange(H) / H) * width * H / W
    c = (xs[None, :] + 1j * ys[:, None]).ravel()
    z = np.zeros_like(c)
    nu = np.full(c.shape, -1.0)
    idx = np.arange(c.size)
    for it in range(maxit):
        z = z * z + c
        if it % 4 == 3:
            m = (z.real ** 2 + z.imag ** 2) > 256.0
            if m.any():
                a = np.abs(z[m])
                nu[idx[m]] = it + 1 - np.log(np.log(a)) / np.log(2)
                k = ~m
                z, c, idx = z[k], c[k], idx[k]
                if idx.size == 0:
                    break
    return nu.reshape(H, W)


def mandel_rgba(nu, mask):
    f = 0.5 - 0.5 * np.cos(2 * np.pi * nu * 0.05)
    rgb = ramp(f, [0, 0.45, 0.8, 1.0],
               [(9, 16, 48), (120, 82, 26), (245, 196, 81), (255, 250, 235)])
    rgb[nu < 0] = hex_rgb(BG)
    a = (mask * 255).astype(np.uint8)
    return np.dstack([rgb.astype(np.uint8), a])


def make_mandel_frames(n=84, W=640, H=360):
    mask = soft_mask(H, W, 0.08)
    frames = []
    for i in range(n):
        u = i / (n - 1)
        e = 0.75 * u + 0.25 * smoothstep(u)
        zoom = np.exp(np.log(1e4) * e)
        maxit = int(140 + 30 * np.log(zoom))
        cx = MB_C[0] + (-0.5 - MB_C[0]) / zoom
        cy = MB_C[1] + (0.0 - MB_C[1]) / zoom
        nu = mandel_nu(cx, cy, 3.6 / zoom, W, H, maxit)
        frames.append((mandel_rgba(nu, mask), zoom))
    return frames


# ---- logistic map -------------------------------------------------------------
BIF_R0, BIF_R1 = 2.8, 4.0
BIF_W, BIF_H = 720, 306
PLOT_X0, PLOT_X1 = -6.0, 3.4       # plot box (scene units), shared by bifurcation + time series
PLOT_Y0, PLOT_Y1 = -1.6, 2.4


def bif_data():
    """Bifurcation density image (gold) + per-column orbit samples."""
    W, H, S = BIF_W, BIF_H, 3
    r = np.linspace(BIF_R0, BIF_R1, W * S)
    col = np.arange(W * S) // S
    x = np.full(W * S, 0.5)
    for _ in range(300):
        x = r * x * (1 - x)
    acc = np.zeros((H, W))
    for _ in range(360):
        x = r * x * (1 - x)
        row = np.clip(((1 - x) * (H - 1)).astype(int), 0, H - 1)
        np.add.at(acc, (row, col), 1)
    pad = np.pad(acc, 1)
    acc = acc + 0.7 * (pad[:-2, 1:-1] + pad[2:, 1:-1]) + 0.35 * (pad[1:-1, :-2] + pad[1:-1, 2:])
    v = 1 - np.exp(-acc * 0.06)
    v = np.clip(v * 1.05, 0, 1)
    rgb = np.zeros((H, W, 3))
    rgb[:] = hex_rgb(GOLD)
    white = np.clip(v - 0.75, 0, 1) / 0.25
    rgb = rgb + (255 - rgb) * (0.6 * white[..., None])
    alpha = (v ** 0.85 * 255).astype(np.uint8)
    rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), alpha])
    # orbit samples per column (for the hopping dot)
    rr = np.linspace(BIF_R0, BIF_R1, W)
    xx = np.full(W, 0.5)
    for _ in range(300):
        xx = rr * xx * (1 - xx)
    seq = []
    for _ in range(64):
        xx = rr * xx * (1 - xx)
        seq.append(xx.copy())
    return rgba, np.array(seq).T          # (H,W,4), (W,64)


def logistic_orbit(x0, r, n):
    xs = [x0]
    for _ in range(n):
        xs.append(r * xs[-1] * (1 - xs[-1]))
    return np.array(xs)


# =============================================================================
class Act4(FilmScene):
    DURATION = BUDGET["act4"]
    DEBUG = False

    # snap run_times to whole frames (30 fps) so the running clock matches the comments
    @staticmethod
    def _snap(t):
        return max(1, round(t * 30)) / 30 - 0.001

    def play(self, *a, **kw):
        if kw.get("run_time") is not None:
            kw["run_time"] = self._snap(kw["run_time"])
        super().play(*a, **kw)

    def wait(self, duration=1.0, **kw):
        super().wait(self._snap(duration), **kw)

    def mark(self, s):
        if self.DEBUG:
            print(f"[t={self.renderer.time:6.2f}] {s}")

    # ------------------------------------------------------------ overlays
    def three_badge(self, start, dur):
        parts = [Text(t, font=FONT, font_size=18, color=c, weight=BOLD)
                 for t, c in (("MATHEMATICS", GOLD), ("PHYSICS", CYAN), ("COMPUTER SCIENCE", MAGENTA))]
        g = VGroup(*parts).arrange(RIGHT, buff=0.25)
        g.to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        return self._timed(g, start, dur, fade=0.35, max_op=0.95)

    # =====================================================================
    #  A  0 - 7  MATHEMATICS  recursion / Sierpinski
    # =====================================================================
    def beat_a(self):
        s = 5.0
        h = s * np.sqrt(3) / 2
        cy = 0.25
        A = np.array([-s / 2, cy - h / 2, 0.0])
        B = np.array([s / 2, cy - h / 2, 0.0])
        C = np.array([0.0, cy + h / 2, 0.0])
        widths = [3.0, 2.6, 2.2, 1.8, 1.4, 1.1]

        def mk(tri, w):
            p = Polygon(*tri, stroke_color=GOLD, stroke_width=w, fill_color=GOLD, fill_opacity=0.42)
            p.set_stroke(GOLD, width=w * 2.6, opacity=0.14, background=True)
            return p

        def kids(tri):
            a, b, c = tri
            ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
            return [(a, ab, ca), (ab, b, bc), (ca, bc, c)]

        levels = [[(A, B, C)]]
        for _ in range(5):
            levels.append([k for t in levels[-1] for k in kids(t)])

        def dlab(d):
            g = VGroup(label(f"depth {d}", WHITE_, 34),
                       label(f"{3 ** d} triangle" + ("" if d == 0 else "s"), DIM, 24))
            return g.arrange(DOWN, buff=0.2).move_to([4.7, 0.3, 0])

        cur = [mk(levels[0][0], widths[0])]
        dl = dlab(0)
        self.play(FadeIn(cur[0], scale=0.8), FadeIn(dl), run_time=0.6)                       # 0.6
        for d in range(1, 6):
            starts = []
            for p in cur:
                for _ in range(3):
                    starts.append(p.copy())
            self.remove(*cur)
            self.add(*starts)
            new = [mk(t, widths[d]) for t in levels[d]]
            self.play(*[Transform(st, nw) for st, nw in zip(starts, new)],
                      Transform(dl, dlab(d)), run_time=0.95, rate_func=ease_out_back)        # 5.35
            cur = starts
        self.wait(0.25)                                                                       # 5.6
        # the hand-off object: a single point, about to be iterated
        self.dot = glow_dot(C, GOLD, r=0.09)
        self.play(FadeIn(self.dot, scale=0.4), run_time=0.3)                                  # 5.9
        self.tri_grp = Group(*cur, dl)

    # =====================================================================
    #  B  7 - 14  MATHEMATICS  Mandelbrot: orbit, bounded vs escaping, deep zoom
    # =====================================================================
    def beat_b(self):
        mb, k = self.mb, self.mb_k
        frames = self.mb_frames
        cx0, cy0 = self.mb_c

        def P(z):
            return np.array([cx0 + (z.real + 0.5) * k, cy0 + z.imag * k, 0.0])

        formula = MathTex(r"z_{n+1}=z_n^{2}+c", color=GOLD).scale(0.85).move_to([5.3, 1.75, 0])
        frame_box = Rectangle(width=mb.width, height=mb.height, stroke_width=1.2, stroke_color=GOLD,
                              stroke_opacity=0.25).move_to(mb)
        dot = self.dot
        # ---- hand-off: triangle dissolves, the point drops onto z = 0 of the complex plane
        self.play(FadeOut(self.tri_grp), dot.animate.move_to(P(0j)),
                  FadeIn(mb), FadeIn(frame_box), FadeIn(formula), run_time=1.1)              # 7.0
        self.mark("B plane in")

        def orbit(c, n, hop, col, status, scol, tail=0.3):
            marker = Circle(radius=0.1, stroke_color=GOLD, stroke_width=3).move_to(P(c))
            marker.set_stroke(GOLD, width=9, opacity=0.25, background=True)
            clab = MathTex("c", color=GOLD).scale(0.75).next_to(marker, UP, buff=0.08)
            st = label(status, scol, 24).move_to([5.3, 0.85, 0])
            self.play(FadeIn(marker), FadeIn(clab), FadeIn(st), run_time=0.25)
            segs = VGroup()
            z = 0j
            for i in range(n):
                zn = z * z + c
                seg = Line(P(z), P(zn), stroke_width=2.4, stroke_color=col)
                seg.set_stroke(col, width=2.4, opacity=0.9)
                segs.add(seg)
                self.play(dot.animate.move_to(P(zn)), Create(seg), run_time=hop, rate_func=linear)
                z = zn
            return marker, clab, st, segs

        # bounded: centre of the period-3 "rabbit" bulb, the orbit cycles for ever
        c1 = complex(-0.1226, 0.7449)
        m, cl, st, segs = orbit(c1, 6, 0.1667, WHITE_, "stays bounded", GOLD)                   # 8.36
        self.play(FadeOut(m), FadeOut(cl), FadeOut(st), FadeOut(segs), run_time=0.3)          # 8.66
        # escaping
        c2 = complex(-0.72, 0.5)
        m, cl, st, segs = orbit(c2, 7, 0.1667, WHITE_, "escapes to infinity", WHITE_)           # 10.11
        self.play(FadeOut(dot), Flash(P(2.11 - 1.16j), color=WHITE_, line_length=0.25, flash_radius=0.4),
                  FadeOut(m), FadeOut(cl), FadeOut(st), FadeOut(segs), run_time=0.3)           # 10.41
        self.mark("B orbits done")

        # ---- deep zoom
        zoom_txt = Text("x 1", font=MONO, font_size=22, color=GOLD).move_to([5.3, 0.85, 0])
        mb_T = self.mb_T = ValueTracker(0.0)

        def mb_upd(m_):
            i = int(np.clip(mb_T.get_value(), 0, 1) * (len(frames) - 1) + 0.5)
            set_img(m_, frames[i][0])
        mb.add_updater(mb_upd)

        def zt_upd(m_):
            i = int(np.clip(mb_T.get_value(), 0, 1) * (len(frames) - 1) + 0.5)
            new = Text(f"x {frames[i][1]:,.0f}", font=MONO, font_size=22, color=GOLD)
            new.move_to([5.3, 0.85, 0])
            m_.become(new)
        self.play(FadeIn(zoom_txt), run_time=0.2)                                             # 10.61
        zoom_txt.add_updater(zt_upd)
        self.play(mb_T.animate.set_value(1.0), run_time=3.16, rate_func=linear)                # 13.6
        mb.clear_updaters()
        zoom_txt.clear_updaters()
        self.play(FadeOut(mb), FadeOut(frame_box), FadeOut(formula), FadeOut(zoom_txt), run_time=0.4)   # 14.0
        self.mark("B done")

    # =====================================================================
    #  C  14 - 21  gold -> cyan  bifurcation, then sensitive dependence
    # =====================================================================
    def beat_c(self):
        Wu, Hu = PLOT_X1 - PLOT_X0, PLOT_Y1 - PLOT_Y0

        def T(x, y):                      # unit box -> scene
            return np.array([PLOT_X0 + Wu * x, PLOT_Y0 + Hu * y, 0.0])

        def tick(txt, pos, col=DIM, size=18):
            return Text(txt, font=FONT, font_size=size, color=col).move_to(pos)

        def axes():
            xa = Line(T(0, 0), T(1, 0) + RIGHT * 0.15, stroke_width=1.6, stroke_color=DIM)
            ya = Line(T(0, 0), T(0, 1) + UP * 0.15, stroke_width=1.6, stroke_color=DIM)
            y0 = tick("0", T(0, 0) + LEFT * 0.25)
            y1 = tick("1", T(0, 1) + LEFT * 0.25)
            xl = tick("x", T(0, 1) + RIGHT * 0.3, WHITE_, 22)
            return VGroup(xa, ya, y0, y1, xl)

        # ---- bifurcation (gold) --------------------------------------------
        ax1 = axes()
        rt = VGroup(*[tick(f"{v:g}", T((v - BIF_R0) / (BIF_R1 - BIF_R0), 0) + DOWN * 0.28)
                      for v in (3.0, 3.5, 4.0)],
                    tick("r", T(1, 0) + RIGHT * 0.15 + DOWN * 0.28, WHITE_, 22))
        formula = MathTex(r"x_{n+1}=r\,x_n(1-x_n)", color=GOLD).scale(0.6).move_to([5.2, 1.75, 0])
        bif = ImageMobject(self.bif_rgba)
        bif.set(width=Wu, height=Hu).move_to(T(0.5, 0.5))
        bif.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
        ft = self.ft = ValueTracker(0.0)
        base_alpha = self.bif_rgba[:, :, 3].copy()
        colidx = np.arange(BIF_W)[None, :]

        def bif_upd(m):
            f = ft.get_value()
            rgba = self.bif_rgba.copy()
            rgba[:, :, 3] = np.where(colidx <= f * (BIF_W - 1), base_alpha, 0)
            set_img(m, rgba)
        bif.add_updater(bif_upd)
        front = Line(T(0, 0), T(0, 1), stroke_width=1.4, stroke_color=GOLD, stroke_opacity=0.5)
        front.add_updater(lambda m: m.put_start_and_end_on(T(ft.get_value(), 0), T(ft.get_value(), 1)))
        rtxt = Text("r = 2.80", font=MONO, font_size=22, color=GOLD).move_to([5.2, 0.85, 0])

        def rt_upd(m):
            v = BIF_R0 + (BIF_R1 - BIF_R0) * ft.get_value()
            new = Text(f"r = {v:.2f}", font=MONO, font_size=22, color=GOLD).move_to([5.2, 0.85, 0])
            m.become(new)

        dot = self.dot = glow_dot(T(0, 0.5), GOLD, r=0.09)
        st = {"k": 0.0}
        orb = self.bif_orb

        def dot_upd(m, dt):
            st["k"] += dt * 13
            j = int(np.clip(ft.get_value(), 0, 1) * (BIF_W - 1))
            y = orb[j][int(st["k"]) % 64]
            m.move_to(T(ft.get_value(), y))

        self.play(FadeIn(ax1), FadeIn(rt), FadeIn(formula), FadeIn(rtxt), FadeIn(dot, scale=0.4),
                  run_time=0.5)                                                              # 14.5
        self.add(bif, front)
        rtxt.add_updater(rt_upd)
        dot.add_updater(dot_upd)
        self.play(ft.animate.set_value(1.0), run_time=3.0, rate_func=linear)                  # 17.5
        dot.clear_updaters()
        rtxt.clear_updaters()
        bif.clear_updaters()
        front.clear_updaters()
        self.mark("C bif done")

        # ---- hand-off: same point, now a physical trajectory (cyan) ----------
        NP = 40
        ta = logistic_orbit(0.400000, 4.0, NP)
        tb = logistic_orbit(0.400001, 4.0, NP)
        ax2 = axes()
        nt = VGroup(*[tick(str(v), T(v / NP, 0) + DOWN * 0.28) for v in (0, 10, 20, 30, 40)],
                    tick("n", T(1, 0) + RIGHT * 0.15 + DOWN * 0.28, WHITE_, 22))
        formula2 = MathTex(r"x_{n+1}=4\,x_n(1-x_n)", color=CYAN).scale(0.6).move_to([5.2, 1.75, 0])
        legA = VGroup(Line(LEFT * 0.22, RIGHT * 0.22, stroke_width=3.5, stroke_color=CYAN),
                      Text("x0 = 0.400000", font=MONO, font_size=20, color=CYAN)).arrange(RIGHT, buff=0.15)
        legB = VGroup(Line(LEFT * 0.22, RIGHT * 0.22, stroke_width=3.5, stroke_color=WHITE_),
                      Text("x0 = 0.400001", font=MONO, font_size=20, color=WHITE_)).arrange(RIGHT, buff=0.15)
        leg = VGroup(legA, legB).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([5.2, -0.2, 0])
        nT = self.nT = ValueTracker(0.0)

        def trace_pts(vals):
            n = nT.get_value()
            i = int(n)
            pts = [T(j / NP, vals[j]) for j in range(min(i, NP) + 1)]
            if i < NP:
                f = n - i
                pts.append(T((i + f) / NP, vals[i] * (1 - f) + vals[i + 1] * f))
            return np.array(pts)

        def mk_trace(vals, col):
            m = VMobject()
            m.set_points_as_corners(np.array([T(0, vals[0]), T(0, vals[0]) + RIGHT * 1e-3]))
            neon(m, col, 3.4)
            m.add_updater(lambda mm: (mm.clear_points(), mm.set_points_as_corners(trace_pts(vals))))
            return m
        trA, trB = mk_trace(ta, CYAN), mk_trace(tb, WHITE_)
        trB.set_stroke(opacity=0.9)

        cyan_dot = glow_dot(dot.get_center(), CYAN, r=0.09)
        self.play(FadeOut(bif), FadeOut(front), FadeOut(ax1), FadeOut(rt), FadeOut(rtxt),
                  FadeOut(formula), Transform(dot, cyan_dot),
                  FadeIn(ax2), FadeIn(nt), FadeIn(formula2), FadeIn(leg),
                  dot.animate.move_to(T(0, ta[0])),
                  run_time=0.5)                                                               # 18.0
        self.add(trB, trA)
        dot.add_updater(lambda m: m.move_to(trace_pts(ta)[-1]))
        self.play(nT.animate.set_value(float(NP)), run_time=2.8, rate_func=linear)           # 20.8
        self.wait(0.2)                                                                        # 21.0
        dot.clear_updaters()
        trA.clear_updaters()
        trB.clear_updaters()
        self.c_stuff = [trA, trB, ax2, nt, formula2, leg]
        self.mark("C done")

    # =====================================================================
    #  D  21 - 29  cyan -> magenta  orbit -> bits -> Turing tape -> halting paradox
    # =====================================================================
    def beat_d(self):
        dot = self.dot
        NB = 8
        xs = logistic_orbit(0.4, 4.0, NB - 1)
        bits = [0 if v < 0.5 else 1 for v in xs]
        flip = [1 - b for b in bits]
        NY, NX0, NX1 = 1.75, -3.5, 3.5

        def p(x):
            return np.array([NX0 + (NX1 - NX0) * x, NY, 0.0])

        nl = Line(p(0), p(1), stroke_width=2.4, stroke_color=CYAN)
        neon(nl, CYAN, 2.4)
        mid = DashedLine(p(0.5) + DOWN * 0.22, p(0.5) + UP * 0.22, dash_length=0.06, stroke_width=2,
                         stroke_color=WHITE_)
        t0 = Text("0", font=FONT, font_size=18, color=DIM).move_to(p(0) + DOWN * 0.3)
        t1 = Text("1", font=FONT, font_size=18, color=DIM).move_to(p(1) + DOWN * 0.3)
        thr = VGroup(MathTex(r"x<\tfrac12", color=CYAN).scale(0.6).move_to(p(0.25) + UP * 0.75),
                     MathTex(r"\to\ 0", color=CYAN).scale(0.6).move_to(p(0.25) + UP * 0.75 + RIGHT * 0.0),
                     ).arrange(RIGHT, buff=0.15).move_to(p(0.25) + UP * 0.75)
        thr2 = VGroup(MathTex(r"x\geq\tfrac12", color=CYAN).scale(0.6),
                      MathTex(r"\to\ 1", color=CYAN).scale(0.6)).arrange(RIGHT, buff=0.15).move_to(
            p(0.75) + UP * 0.75)
        nline = VGroup(nl, mid, t0, t1, thr, thr2)

        # tape
        n_c, cs_, ty = 11, 0.75, -0.55
        cells = VGroup(*[Square(cs_, stroke_width=2.6, stroke_color=CYAN, stroke_opacity=0.7) for _ in range(n_c)])
        cells.arrange(RIGHT, buff=0).move_to([0, ty, 0])
        cellx = lambda i: cells[i].get_center()

        self.play(FadeOut(VGroup(*self.c_stuff)), FadeIn(nline), FadeIn(cells),
                  dot.animate.move_to(p(xs[0])), run_time=0.6)                                # 21.6
        self.mark("D numberline in")

        # the orbit hops; every hop drops one bit onto the tape
        digits = []
        pending = None
        hop = 0.14
        for k in range(NB):
            anims = [dot.animate.move_to(p(xs[k]))]
            if pending is not None:
                idx = k - 1
                anims.append(pending.animate.move_to(cellx(1 + idx)).set_color(WHITE_))
            self.play(*anims, run_time=hop, rate_func=linear)
            if pending is not None:
                digits.append(pending)
            pending = Text(str(bits[k]), font=MONO, font_size=36, color=CYAN).move_to(p(xs[k]) + UP * 0.38)
            self.add(pending)
        self.play(pending.animate.move_to(cellx(NB)).set_color(WHITE_), run_time=hop, rate_func=linear)
        digits.append(pending)                                                                # 22.88
        syms = {1 + i: d for i, d in enumerate(digits)}

        # ---- physics -> computer science: the tape wakes up as a Turing machine
        tri = Triangle(color=MAGENTA, fill_opacity=1).scale(0.16).rotate(PI)
        box = RoundedRectangle(width=1.0, height=0.55, corner_radius=0.13, color=MAGENTA, stroke_width=2.5)
        state = Text("q0", font=MONO, font_size=24, color=WHITE_)
        head = VGroup(box, tri, state)
        tri.next_to(cells[1], UP, buff=0.06)
        box.next_to(tri, UP, buff=0.05)
        state.move_to(box)
        hint = label("read  ·  write  ·  move", DIM, 24).move_to([0, -1.6, 0])
        self.play(FadeOut(dot), FadeOut(nline), cells.animate.set_stroke(MAGENTA, opacity=0.85),
                  FadeIn(head), FadeIn(hint), run_time=0.5)                                   # 23.38
        self.mark("D tape ready")
        for k in range(1, NB + 1):
            new = Text(str(flip[k - 1]), font=MONO, font_size=36, color=MAGENTA).move_to(cells[k])
            self.play(AnimationGroup(Transform(syms[k], new),
                                     cells[k].animate.set_fill(MAGENTA, 0.22),
                                     head.animate.shift(RIGHT * cs_),
                                     lag_ratio=0.35), run_time=0.24)
        halt = Text("HALT", font=MONO, font_size=22, color=WHITE_).move_to(state)
        self.play(Transform(state, halt), run_time=0.2)                                        # 25.5
        self.mark("D tape done")

        # ---- the halting paradox
        Hb = RoundedRectangle(width=1.7, height=1.1, corner_radius=0.16, color=MAGENTA, stroke_width=4)
        Hb.set_stroke(MAGENTA, width=12, opacity=0.18, background=True)
        Hb.set_fill(MAGENTA, 0.1)
        Hb.move_to([0, -0.85, 0])
        Ht = Text("H", font=FONT, font_size=52, color=WHITE_, weight=BOLD).move_to(Hb)
        Hq = label("halts?", MAGENTA, 24).next_to(Hb, DOWN, buff=0.2)
        prog = Text("program", font=FONT, font_size=22, color=DIM).move_to([-4.2, -0.65, 0])
        pin = Arrow([-3.2, -0.85, 0], Hb.get_left() + LEFT * 0.05, buff=0, color=WHITE_,
                    stroke_width=3, tip_length=0.22, max_tip_length_to_length_ratio=0.3)
        tape_all = Group(cells, head, hint, *digits)
        self.play(AnimationGroup(AnimationGroup(FadeOut(tape_all)),
                                 AnimationGroup(FadeIn(Hb), FadeIn(Ht), FadeIn(Hq), FadeIn(prog), Create(pin)),
                                 lag_ratio=0.45), run_time=0.5)                                                               # 26.0
        loop = ArcBetweenPoints(Hb.get_right() + RIGHT * 0.02, Hb.get_left() + LEFT * 0.04, angle=1.5 * PI)
        loop.set_stroke(MAGENTA, width=4)
        loop.set_stroke(MAGENTA, width=13, opacity=0.18, background=True)
        loop.add_tip(tip_length=0.28)
        self.play(Create(loop), FadeOut(prog), FadeOut(pin), run_time=0.9)                   # 26.9
        runner = glow_dot(loop.point_from_proportion(0), MAGENTA, r=0.08)
        selfl = label("H runs on its own code", MAGENTA, 24).next_to(loop, UP, buff=0.18)
        q = Text("?", font=FONT, font_size=110, color=RED_Q, weight=BOLD)
        q.move_to(loop.get_center() + UP * 0.1)
        qg = q.copy().set_stroke(RED_Q, width=10, opacity=0.3)
        self.play(FadeIn(runner), FadeIn(selfl), run_time=0.2)                                # 27.1
        self.play(MoveAlongPath(runner, loop), run_time=0.7, rate_func=linear)               # 27.8
        self.play(FadeIn(q, scale=0.5), FadeIn(qg, scale=0.5), run_time=0.4)                 # 28.2
        self.play(Indicate(q, scale_factor=1.15, color=RED_Q), run_time=0.5)                 # 28.7
        self.wait(0.43)                                                                       # 29.0
        self.d_stuff = [Hb, Ht, Hq, loop, runner, selfl, q, qg]
        self.mark("D done")

    # =====================================================================
    #  E  29 - 35  FRONTIER  a proof is a program (Curry-Howard)
    # =====================================================================
    def beat_e(self):
        BXY, BWD, BHT = 0.3, 3.0, 2.1
        xs5 = [-4.3, 0.0, 4.3]
        cols5 = [GOLD, MAGENTA, CYAN]
        boxes, names = [], VGroup()
        for x, col, nm in zip(xs5, cols5, ["logic", "code", "physics"]):
            bx_ = RoundedRectangle(width=BWD, height=BHT, corner_radius=0.22).move_to([x, BXY, 0])
            neon(bx_, col, 3.0)
            bx_.set_fill("#0A1020", 0.9)
            boxes.append(bx_)
            names.add(Text(nm, font=FONT, font_size=24, color=col).move_to([x, BXY - 0.72, 0]))
        f_logic = MathTex(r"A \Rightarrow B", font_size=60, color=GOLD).move_to([xs5[0], BXY + 0.2, 0])
        f_code = MathTex(r"f : A \to B", font_size=60, color=MAGENTA).move_to([xs5[1], BXY + 0.2, 0])
        f_phys = MathTex(r"A \rightsquigarrow B", font_size=60, color=CYAN).move_to([xs5[2], BXY + 0.2, 0])

        def link(a, b, c1, c2):
            m = Line(a, b)
            m.set_stroke([c1, c2], width=3.4)
            m.set_stroke([c1, c2], width=11, opacity=0.2, background=True)
            return m
        half = BWD / 2
        L1 = link([xs5[0] + half, BXY, 0], [xs5[1] - half, BXY, 0], GOLD, MAGENTA)
        L2 = link([xs5[1] + half, BXY, 0], [xs5[2] - half, BXY, 0], MAGENTA, CYAN)
        L3 = ArcBetweenPoints([xs5[2], BXY + BHT / 2, 0], [xs5[0], BXY + BHT / 2, 0], angle=0.6)
        L3.set_stroke([CYAN, GOLD], width=3.4)
        L3.set_stroke([CYAN, GOLD], width=11, opacity=0.2, background=True)

        old = [m for m in self.d_stuff]
        self.play(*[FadeOut(m, run_time=0.5) for m in old],
                  *[FadeIn(b) for b in boxes], FadeIn(names),
                  LaggedStart(Write(f_logic), Write(f_code), Write(f_phys), lag_ratio=0.3),
                  run_time=1.4)                                                               # 30.4
        self.mark("E boxes")
        self.play(*[Create(l) for l in (L1, L2, L3)], run_time=0.5)                            # 30.9
        pulse = glow_dot(L1.get_start(), WHITE_, r=0.09, layers=8)
        self.add(pulse)
        self.play(FadeIn(pulse, scale=0.5), run_time=0.1)                                     # 31.0

        def seg(link_, box, col, t):
            self.play(MoveAlongPath(pulse, link_, rate_func=linear),
                      Flash(box.get_center(), color=col, line_length=0.3, flash_radius=1.35,
                            num_lines=12, run_time=t),
                      run_time=t)
        seg(L1, boxes[0], GOLD, 0.5)
        seg(L2, boxes[1], MAGENTA, 0.5)
        seg(L3, boxes[2], CYAN, 0.6)                                                          # 32.6
        seg(L1, boxes[0], GOLD, 0.4)
        seg(L2, boxes[1], MAGENTA, 0.4)
        seg(L3, boxes[2], CYAN, 0.5)                                                          # 33.9
        self.mark("E pulses")

    # =====================================================================
    def construct(self):
        # ---------------------------------------------------------------- precompute
        self.mb_frames = make_mandel_frames()
        self.bif_rgba, self.bif_orb = bif_data()
        mb = ImageMobject(self.mb_frames[0][0])
        mb.height = 4.6
        mb.move_to([-0.6, 0.35, 0])
        mb.set_resampling_algorithm(RESAMPLING_ALGORITHMS["cubic"])
        self.mb = mb
        self.mb_k = mb.width / 3.6
        self.mb_c = (-0.6, 0.35)

        # ---------------------------------------------------------------- overlays (absolute times)
        self.tag("04", "SELF-REFERENCE", WHITE_, start=0.2, dur=3.6)
        self.caption("A rule that feeds on its own output.", start=0.5, dur=5.6)
        self.caption("Simple rules. Infinite complexity.", start=7.6, dur=5.6)
        self.caption("In a chaotic world, tiny differences grow without limit.", start=14.4, dur=6.2)
        self.caption("A machine can compute anything computable.\nYet some questions no machine can answer.",
                     start=21.2, dur=7.4)
        self.caption("A proof is a program.", start=30.2, dur=4.2)
        # badges: one per discipline; hand-offs cross-fade
        self.badge("MATHEMATICS", GOLD, start=0.3, dur=17.6)          # A, B, C-bifurcation
        self.badge("PHYSICS", CYAN, start=17.55, dur=5.5)             # C-trajectories, D-orbit bits
        self.badge("COMPUTER SCIENCE", MAGENTA, start=22.7, dur=6.65) # D-Turing, halting
        self.three_badge(start=29.0, dur=6.0)                         # E: all three
        # ladder: 0 -> 1 -> 2 (B..D) -> 3
        self.level(0, GOLD, start=0.0, dur=3.6)
        self.level(1, GOLD, start=3.25, dur=3.75)
        self.level(2, WHITE_, start=6.65, dur=22.45)
        self.level(3, WHITE_, start=28.75, dur=6.25)

        self.beat_a()          # 7.0 (hand-off inside)
        self.beat_b()          # 14.0
        self.beat_c()          # 21.0
        self.beat_d()          # 29.0
        self.beat_e()          # 33.9
        self.fade_all(0.7)     # 34.6
        self.pad_to()
