from style import *

# =============================================================================
#  ACT 2  --  02 MINIMIZATION   (30 s)
#  One ball keeps rolling downhill while the world around it changes discipline:
#  A physics (cyan)  -> B maths (gold) -> C computer science (magenta)
#  -> D physics again (light, least time) -> E the frontier (rugged landscape, P vs NP)
# =============================================================================


def P3(x, y):
    return np.array([x, y, 0.0])


def sm(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def smooth_curve(pts, color=None, width=None):
    m = VMobject()
    m.set_points_smoothly([np.array([p[0], p[1], 0.0]) for p in pts])
    m.set_fill(opacity=0)
    return m


def corners(pts):
    m = VMobject()
    m.set_points_as_corners([np.array([p[0], p[1], 0.0]) for p in pts])
    m.set_fill(opacity=0)
    return m


def col(c):
    return ManimColor(c)


# ---- image helpers (from v1 act 4) -----------------------------------------
def smoothstep(x):
    return sm(x)


def soft_mask(h, w, frac=0.07):
    yy = np.minimum(np.arange(h), h - 1 - np.arange(h)) / (h * frac)
    xx = np.minimum(np.arange(w), w - 1 - np.arange(w)) / (w * frac)
    return smoothstep(yy)[:, None] * smoothstep(xx)[None, :]


def set_img(m, rgba):
    m.pixel_array = rgba
    m.orig_alpha_pixel_array = rgba[:, :, 3].copy()


def ramp(v, stops, cols):
    v = np.clip(v, 0, 1)
    cols = np.array(cols, float)
    return np.stack([np.interp(v, stops, cols[:, c]) for c in range(3)], -1)


# ---- B: valley y = x^2 ------------------------------------------------------
def V(u):
    """Valley point for maths coordinate u (y = u^2), mapped to the screen."""
    return P3(-1.2 + 1.5 * u, -2.0 + 0.8 * u * u)


def roll_u(t):
    """Damped roll from u=2 to the bottom, gently brought to rest at u=0."""
    b = 1 - sm((t - 3.5) / 0.9)
    return 2.0 * np.exp(-0.72 * t) * np.cos(1.25 * t) * b


# ---- C: loss landscape -------------------------------------------------------
LS_W, LS_H = 7.6, 4.3
LC = np.array([1.6, 0.3, 0.0])


def loss_f(x, y):
    return (0.06 * (x - 1.4) ** 2 + 0.35 * ((y + 0.6) - 0.45 * np.sin(0.8 * x)) ** 2
            + 0.10 * np.cos(2.2 * x + 1) * np.cos(2.4 * y))


def loss_grad(p, h=1e-3):
    x, y = p
    return np.array([(loss_f(x + h, y) - loss_f(x - h, y)) / (2 * h),
                     (loss_f(x, y + h) - loss_f(x, y - h)) / (2 * h)])


def descent_path(start=(-3.2, 1.5), steps=170, lr=0.7, mom=0.7):
    p = np.array(start, float)
    v = np.zeros(2)
    pts = [p.copy()]
    for _ in range(steps):
        v = mom * v - lr * loss_grad(p)
        p = p + 0.5 * v
        pts.append(p.copy())
    return np.array(pts)


def loss_image(W=640, H=362):
    xs = np.linspace(-LS_W / 2, LS_W / 2, W)
    ys = np.linspace(LS_H / 2, -LS_H / 2, H)
    X, Y = np.meshgrid(xs, ys)
    L = loss_f(X, Y)
    lo, hi = L.min(), np.percentile(L, 99)
    Ln = np.clip((L - lo) / (hi - lo), 0, 1)
    rgb = ramp(Ln ** 0.8, [0, 0.16, 0.5, 0.85, 1.0],
               [(7, 10, 30), (52, 22, 112), (200, 34, 128), (240, 170, 80), (250, 220, 140)])
    fr = (Ln * 12) % 1.0
    line = np.exp(-((fr - 0.5) / 0.05) ** 2)[..., None]
    rgb = rgb * 0.8 + line * np.array([255, 255, 255]) * 0.16
    a = (soft_mask(H, W, 0.05) * 255).astype(np.uint8)
    return np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), a])


def clean_scene(n=96):
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
    hor = 0.62
    sky = ramp((yy / hor) ** 1.3, [0, 0.55, 1.0], [(10, 14, 46), (200, 36, 130), (250, 190, 90)])
    d = np.hypot(xx - 0.5, (yy - 0.5) * 1.0)
    sun = np.exp(-(d / 0.11) ** 8)[..., None]
    glow = np.exp(-(d / 0.30) ** 2)[..., None] * 0.55
    img = sky + glow * np.array([255, 170, 90]) * 0.5
    img = img * (1 - sun) + sun * np.array([255, 245, 220])
    ridge = 0.60 - 0.09 * np.abs(np.sin(xx * 5.5 + 0.6)) - 0.05 * np.sin(xx * 13 + 1.0) * 0.5 \
        - 0.10 * np.exp(-((xx - 0.18) / 0.16) ** 2) - 0.06 * np.exp(-((xx - 0.85) / 0.14) ** 2)
    land = (yy > ridge)[..., None]
    rim = np.exp(-((yy - ridge) / 0.012) ** 2)[..., None] * (yy > ridge - 0.02)[..., None]
    ground = ramp((yy - ridge) * 3, [0, 1], [(14, 18, 44), (5, 7, 18)])
    refl = np.exp(-((xx - 0.5) / (0.05 + 0.25 * (yy - hor))) ** 2) * (yy > hor) * 0.9
    ground = ground + refl[..., None] * np.array([245, 190, 90]) * (0.5 + 0.5 * np.sin(yy * 150)[..., None] ** 2)
    img = np.where(land, ground, img)
    img = img + rim * np.array([76, 201, 240]) * 0.9
    return np.clip(img, 0, 255) / 255.0


def denoise_frames(steps=20, n=96, seed=7):
    rng = np.random.default_rng(seed)
    x0 = clean_scene(n)
    eps = rng.normal(0, 1, x0.shape)
    frames = []
    for i in range(steps + 1):
        ab = smoothstep(i / steps) ** 1.15
        x = 0.5 + np.sqrt(ab) * (x0 - 0.5) + np.sqrt(1 - ab) * 0.30 * eps
        rgb = (np.clip(x, 0, 1) * 255).astype(np.uint8)
        frames.append(np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)]))
    return frames


# ---- D: Fermat + general relativity -------------------------------------------
FA, FB = P3(-3.7, 1.8), P3(3.7, -1.6)
V1, V2 = 1.0, 0.6


def fermat_time(x):
    return (np.hypot(x - FA[0], FA[1]) / V1 + np.hypot(FB[0] - x, FB[1]) / V2)


GR_G, GR_EPS = 0.55, 0.35
ELEV = np.radians(50)
GR_Y0 = 0.45


def gr_trace(theta, sx=-6.0, ox=5.8, ds=0.05):
    p = np.array([sx, 0.0])
    u = np.array([np.cos(theta), np.sin(theta)])
    pts = [p.copy()]
    for _ in range(900):
        r2 = p @ p + GR_EPS
        a = -GR_G * p / r2 ** 1.5
        a = a - (a @ u) * u
        u = u + a * ds
        u /= np.linalg.norm(u)
        p = p + u * ds
        pts.append(p.copy())
        if p[0] >= ox:
            break
    return np.array(pts)


def gr_solve_theta():
    lo, hi = 0.30, 0.42
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if gr_trace(mid)[-1, 1] > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def well_z(x, y, k):
    return -k / np.sqrt(x * x + y * y + 0.55)


def proj(x, y, z):
    yy = y * np.sin(ELEV) + z * np.cos(ELEV)
    dd = y * np.cos(ELEV) - z * np.sin(ELEV)
    f = 1.0 / (1.0 + 0.03 * dd)
    return np.stack([x * f * 0.97, yy * f + GR_Y0, np.zeros_like(x)], -1)


# ---- E: rugged landscape -----------------------------------------------------
def rug_h(x):
    return 1.1 * (0.45 * np.sin(1.5 * x + 0.9) + 0.30 * np.sin(3.7 * x + 1.3)
                  + 0.16 * np.sin(8.1 * x + 2.0) - 0.10 * x)


def rug_dh(x, e=1e-4):
    return (rug_h(x + e) - rug_h(x - e)) / (2 * e)


RUG_Y0 = -0.35
RUG_X0 = -3.0


def rug_pt(x):
    return P3(x, RUG_Y0 + rug_h(x))


def rug_roll(x0=RUG_X0, g=30.0, c=3.0, T=1.8, dt=0.0005, n=90):
    x, v, t = x0, 0.0, 0.0
    xs = [x0]
    nxt = 0
    per = T / n
    while t < T:
        s = rug_dh(x)
        v += (-g * s / (1 + s * s) - c * v) * dt
        x += v * dt
        t += dt
        if t >= per * (len(xs)):
            xs.append(x)
    xs = np.array(xs[:n + 1])
    # settle exactly on the local minimum
    lo, hi = xs[-1] - 0.3, xs[-1] + 0.3
    grid = np.linspace(lo, hi, 4001)
    xm = grid[np.argmin(rug_h(grid))]
    tail = xs[-1] + (xm - xs[-1]) * sm(np.linspace(0, 1, 14))
    return np.concatenate([xs, tail[1:]]), xm


# =============================================================================
class Act2(FilmScene):
    DURATION = BUDGET["act2"]

    # ---- the hand-off object ---------------------------------------------
    def make_ball(self, pos, color):
        self.ball = glow_dot(pos, color, r=0.1, layers=6)
        self.ball_col = color
        self.ball.set_z_index(10)
        self.pos_fn = None
        self.ball.add_updater(lambda m: m.move_to(self.pos_fn()) if self.pos_fn else None)
        return self.ball

    def hop(self, target, lift=0.9, run_time=0.8, col_to=None, rate_func=smooth):
        """Ball leaps to a new place (and optionally changes colour): the hand-off."""
        self.pos_fn = None
        start = self.ball.get_center().copy()
        tgt = np.array(target, float)
        c0 = self.ball_col
        if col_to:
            self.ball_col = col_to

        def f(m, a):
            p = (1 - a) * start + a * tgt + UP * lift * np.sin(PI * a)
            m.move_to(p)
            if col_to:
                cc = interpolate_color(col(c0), col(col_to), a)
                for s in m[:-1]:
                    s.set_fill(cc)
        return UpdateFromAlphaFunc(self.ball, f, run_time=run_time, rate_func=rate_func)

    def recolor(self, col_to, run_time=0.5):
        c0 = self.ball_col
        self.ball_col = col_to

        def f(m, a):
            cc = interpolate_color(col(c0), col(col_to), a)
            for s in m[:-1]:
                s.set_fill(cc)
        return UpdateFromAlphaFunc(self.ball, f, run_time=run_time, rate_func=smooth)

    # =========================================================================
    def construct(self):
        # ---- precompute once ----------------------------------------------
        self.loss_rgba = loss_image()
        self.gd_path = descent_path()
        self.dn_frames = denoise_frames()
        self.theta_star = gr_solve_theta()

        # ---- overlays (non-blocking, absolute times) -----------------------
        self.tag("02", "MINIMIZATION", WHITE_, start=0.2, dur=3.6)
        # A  0-6  physics / basics
        self.badge("PHYSICS", CYAN, start=0.0, dur=6.5)
        self.level(0, CYAN, start=0.0, dur=6.5)
        self.caption("Nature always finds the easiest path.", start=0.5, dur=5.3)
        # B  6-12  physics -> mathematics / high school
        self.badge("PHYSICS", CYAN, start=6.0, dur=2.4)
        self.badge("MATHEMATICS", GOLD, start=8.4, dur=5.3)
        self.level(1, GOLD, start=6.0, dur=6.2)
        self.caption("At the lowest point, the slope is zero.", start=7.0, dur=4.8)
        # C  12-19  mathematics -> computer science / university
        self.badge("COMPUTER SCIENCE", MAGENTA, start=13.75, dur=5.25)
        self.level(2, MAGENTA, start=12.0, dur=7.3)
        self.caption("A machine learns by rolling downhill.", start=12.6, dur=5.9)
        # D  19-25  physics / university -> frontier
        self.badge("PHYSICS", CYAN, start=19.05, dur=5.85)
        self.level(2, CYAN, start=19.0, dur=3.3)
        self.level(3, CYAN, start=22.0, dur=3.3)
        self.caption("Light takes the quickest path — even through curved spacetime.",
                     start=19.4, dur=5.4)
        # E  25-30  computer science / frontier
        self.badge("COMPUTER SCIENCE", MAGENTA, start=24.95, dur=4.95)
        self.level(3, MAGENTA, start=25.0, dur=4.9)
        self.caption("Some landscapes have too many valleys to search. P vs NP?",
                     start=25.2, dur=4.6)

        self.beat_a()
        print(f'[t] beat a end {self.renderer.time:.2f}')
        self.beat_b()
        print(f'[t] beat b end {self.renderer.time:.2f}')
        self.beat_c()
        print(f'[t] beat c end {self.renderer.time:.2f}')
        self.beat_d()
        print(f'[t] beat d end {self.renderer.time:.2f}')
        self.beat_e()
        print(f'[t] beat e end {self.renderer.time:.2f}')
        self.fade_all(0.7)        # 30.0
        self.pad_to()

    # =========================================================================
    # A  0 - 5.4   the ball, a parabola, and every other path it could have taken
    # =========================================================================
    def beat_a(self):
        GY = -1.9
        S, E = P3(-4.3, GY), P3(4.18, GY)
        H = 2.8
        ground = ParametricFunction(lambda s: P3(4.6 * s, GY), t_range=[-1, 1, 0.02])
        ground.set_stroke(DIM, width=2.5, opacity=0.9)
        self.ground = ground

        def path(a=1.0, b=0.0, k=2, n=90):
            t = np.linspace(0, 1, n)
            x = S[0] + (E[0] - S[0]) * t
            y = GY + 4 * H * a * t * (1 - t) + b * np.sin(k * np.pi * t)
            return np.column_stack([x, y])

        specs = [(0.25, 0, 2), (0.5, 0, 2), (0.78, 0, 2), (1.3, 0, 2), (1.62, 0, 2),
                 (1.0, 0.9, 2), (1.0, -0.7, 2), (0.95, 0.55, 3), (1.05, -0.5, 4)]
        alts = VGroup(*[smooth_curve(path(a, b, k)).set_stroke(CYAN, width=2.0, opacity=0.42)
                        for a, b, k in specs])
        true = smooth_curve(path(1.0, 0, 2))
        neon(true, CYAN, 4.5)

        start_ring = Circle(radius=0.2, stroke_color=WHITE_, stroke_width=1.6, stroke_opacity=0.6).move_to(S)
        end_ring = DashedVMobject(Circle(radius=0.2, stroke_color=CYAN, stroke_width=1.6,
                                         stroke_opacity=0.6).move_to(E), num_dashes=12)
        ball = self.make_ball(S, CYAN)

        self.play(FadeIn(ground), FadeIn(start_ring), FadeIn(end_ring), FadeIn(ball, scale=0.4),
                  run_time=0.7)                                                         # 0.7
        self.play(LaggedStart(*[Create(p) for p in alts], lag_ratio=0.16, run_time=1.7))  # 2.4

        fl = ValueTracker(0.0)
        self.pos_fn = lambda: P3(S[0] + (E[0] - S[0]) * fl.get_value(),
                                 GY + 4 * H * fl.get_value() * (1 - fl.get_value()))
        self.play(UpdateFromAlphaFunc(fl, lambda m, a: m.set_value(a), run_time=2.0, rate_func=linear),
                  Create(true, run_time=2.0, rate_func=linear),
                  alts.animate(run_time=2.0).set_stroke(opacity=0.12))                  # 4.4
        self.pos_fn = None
        self.play(Flash(E, color=CYAN, flash_radius=0.45, line_length=0.15, run_time=0.5),
                  FadeOut(alts, run_time=0.5))                                          # 4.9
        self.wait(0.5)                                                                  # 5.4
        self.A_true = true
        self.A_marks = VGroup(start_ring, end_ring)

    # =========================================================================
    # B  5.4 - 11.7   the ground bends into a valley; slope of the tangent
    # =========================================================================
    def beat_b(self):
        ground, ball = self.ground, self.ball
        valley = ParametricFunction(lambda s: V(2.2 * s), t_range=[-1, 1, 0.02])
        neon(valley, CYAN, 4.0)
        G_s0 = P3(4.6 * (2.0 / 2.2), -1.9)
        V_s0 = V(2.0)

        def ride(m, a):
            m.move_to((1 - a) * G_s0 + a * V_s0)

        self.play(Transform(ground, valley, run_time=1.4),
                  UpdateFromAlphaFunc(ball, ride, run_time=1.4),
                  FadeOut(self.A_true, run_time=0.6), FadeOut(self.A_marks, run_time=0.6))   # 6.8

        tau = ValueTracker(0.0)
        u = lambda: roll_u(tau.get_value())
        self.pos_fn = lambda: V(u())

        fade_f = ValueTracker(0.0)

        def tangent():
            uu = u()
            d = np.array([1.5, 1.6 * uu, 0.0])
            d = d / np.linalg.norm(d) * 1.15
            p = V(uu)
            ln = Line(p - d, p + d)
            f = fade_f.get_value()
            ln.set_stroke(WHITE_, width=3.0, opacity=f)
            ln.set_stroke(WHITE_, width=9.6, opacity=0.18 * f, background=True)
            ln.set_z_index(5)
            return ln

        tan = always_redraw(tangent)
        lab = label("slope", WHITE_, 30).move_to(P3(3.9, 0.9))
        num = DecimalNumber(4.0, num_decimal_places=2, include_sign=True, font_size=46, color=GOLD)
        num.next_to(lab, RIGHT, buff=0.3)

        def num_upd(m):
            val = 2 * u()
            m.set_value(val)
            m.set_color(WHITE_ if abs(val) < 0.06 else GOLD)
            m.next_to(lab, RIGHT, buff=0.3)
            m.set_opacity(fade_f.get_value())
        num.add_updater(num_upd)
        lab.add_updater(lambda m: m.set_opacity(fade_f.get_value()))
        ylab = MathTex(r"y=x^{2}", color=GOLD).scale(1.0).move_to(P3(-1.2, 1.3))
        readout = VGroup(lab, num)

        def valley_gold(m, a):
            neon(m, interpolate_color(col(CYAN), col(GOLD), a), 4.0)

        reveal = AnimationGroup(UpdateFromAlphaFunc(fade_f, lambda m, a: m.set_value(a), run_time=0.5),
                                FadeIn(ylab, run_time=0.5),
                                UpdateFromAlphaFunc(ground, valley_gold, run_time=0.6),
                                self.recolor(GOLD, 0.6))
        self.add(tan, readout)
        self.play(UpdateFromAlphaFunc(tau, lambda m, a: m.set_value(4.4 * a), run_time=4.4, rate_func=linear),
                  Succession(Wait(1.5), reveal))                                        # 11.2
        self.pos_fn = None
        ring = Circle(radius=0.14, stroke_color=WHITE_, stroke_width=3).move_to(V(0))
        self.play(ring.animate(run_time=0.4).scale(4.0).set_stroke(opacity=0),
                  Indicate(num, scale_factor=1.25, color=WHITE_, run_time=0.4))          # 11.6
        self.remove(ring)
        tan.clear_updaters(); num.clear_updaters(); lab.clear_updaters()
        self.B_grp = Group(ground, tan, readout, ylab)
        self.tau_B = tau

    # =========================================================================
    # C  11.6 - 18.8   valley -> 2D loss landscape; gradient descent; denoising
    # =========================================================================
    def beat_c(self):
        ball = self.ball
        P = np.column_stack([self.gd_path[:, 0], self.gd_path[:, 1], np.zeros(len(self.gd_path))]) + LC

        land = ImageMobject(self.loss_rgba)
        land.height = LS_H
        land.move_to(LC)
        land.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
        lab_L = MathTex(r"L(\theta)", color=MAGENTA).scale(0.9).move_to(P3(-4.9, -0.2))

        # a small neural network on the left
        layers = [3, 5, 5, 2]
        lx = np.linspace(-6.2, -3.6, 4)
        node_pos = []
        for L, x in zip(layers, lx):
            ys_ = (np.arange(L) - (L - 1) / 2) * 0.36 + 1.15
            node_pos.append([P3(x, y) for y in ys_])
        edge_layers = []
        for a in range(3):
            row = []
            for pa in node_pos[a]:
                for pb in node_pos[a + 1]:
                    row.append(Line(pa, pb, stroke_width=1.2, stroke_color=MAGENTA, stroke_opacity=0.3))
            edge_layers.append(row)
        edges = VGroup(*[VGroup(*r) for r in edge_layers])
        nodes = VGroup()
        for li, cc in enumerate([CYAN, MAGENTA, MAGENTA, GOLD]):
            for p in node_pos[li]:
                nodes.add(Circle(radius=0.1, stroke_width=2.2, stroke_color=cc, fill_color=BG,
                                 fill_opacity=1).move_to(p))
        net = VGroup(edges, nodes)

        prog = ValueTracker(0.0)

        def pos_at(pr):
            i = pr * (len(P) - 1)
            i0 = int(min(i, len(P) - 1))
            f = i - i0
            i1 = min(i0 + 1, len(P) - 1)
            return P[i0] * (1 - f) + P[i1] * f, i0

        def net_upd(_m):
            pr = prog.get_value()
            for li, row in enumerate(edge_layers):
                w = 0.5 + 0.5 * np.sin(TAU * (pr * 3.5 + (2 - li) / 3.0))
                for e in row:
                    e.set_stroke(opacity=0.18 + 0.62 * w ** 3)
        edges.add_updater(net_upd)

        trail = VMobject()
        trail.set_stroke(WHITE_, width=3.0)
        trail.set_stroke(MAGENTA, width=10, opacity=0.35, background=True)
        trail.set_z_index(5)

        def trail_upd(m):
            p, i0 = pos_at(prog.get_value())
            pts = np.vstack([P[:i0 + 1], p[None, :]])
            m.clear_points()
            if len(pts) > 1:
                m.set_points_as_corners(pts)
        trail.add_updater(trail_upd)
        start_marker = Circle(radius=0.16, stroke_color=WHITE_, stroke_width=1.6,
                              stroke_opacity=0.7).move_to(P[0])

        # hand-off: valley dissolves into a landscape; the ball leaps to the top of it
        self.play(FadeOut(self.B_grp, run_time=0.5),
                  FadeIn(land, run_time=0.7), FadeIn(net, run_time=0.7), FadeIn(lab_L, run_time=0.7),
                  FadeIn(start_marker, run_time=0.7),
                  self.hop(P[0], lift=0.9, run_time=0.8, col_to=MAGENTA))              # 12.4
        self.add(trail)
        self.pos_fn = lambda: pos_at(prog.get_value())[0]
        self.play(UpdateFromAlphaFunc(prog, lambda m, a: m.set_value(a), run_time=2.4, rate_func=smooth))  # 14.8
        self.pos_fn = None
        edges.clear_updaters()
        trail.clear_updaters()
        ring = Circle(radius=0.12, stroke_color=WHITE_, stroke_width=3).move_to(P[-1])
        self.play(ring.animate(run_time=0.4).scale(4.5).set_stroke(opacity=0))          # 15.2
        self.remove(ring)

        # noise -> image : a trained model paints from noise
        dn_frames = self.dn_frames
        dn = ImageMobject(dn_frames[0])
        dn.height = 3.9
        dn.move_to(P3(-0.8, 0.45))
        dn.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        dn_T = ValueTracker(0.0)

        def dn_upd(m):
            i = min(len(dn_frames) - 1, int(dn_T.get_value() * len(dn_frames)))
            set_img(m, dn_frames[i])
        dn.add_updater(dn_upd)
        dn_frame = Rectangle(width=dn.width + 0.12, height=dn.height + 0.12, stroke_width=2,
                             stroke_color=MAGENTA, stroke_opacity=0.8).move_to(dn)
        dn_frame.set_stroke(MAGENTA, width=8, opacity=0.18, background=True)
        step_txt = Text("noise   t = 1.00   image", font=MONO, font_size=22, color=MAGENTA).move_to(P3(-0.8, -1.85))
        st = {"i": -1}

        def st_upd(m):
            i = min(len(dn_frames) - 1, int(dn_T.get_value() * len(dn_frames)))
            if i != st["i"]:
                st["i"] = i
                new = Text(f"noise   t = {1 - i / (len(dn_frames) - 1):.2f}   image", font=MONO,
                           font_size=22, color=MAGENTA)
                new.move_to(P3(-0.8, -1.85))
                m.become(new)
        step_txt.add_updater(st_upd)
        dn_grp = Group(dn, dn_frame, step_txt)
        gone = Group(land, net, lab_L, trail, start_marker)
        self.play(FadeOut(gone, run_time=0.5), FadeIn(dn_grp, run_time=0.5))            # 15.7
        self.play(UpdateFromAlphaFunc(dn_T, lambda m, a: m.set_value(a), run_time=2.6, rate_func=smooth),
                  Succession(Wait(1.0), Indicate(ball, scale_factor=1.5, color=WHITE_, run_time=0.8)))  # 18.3
        dn.clear_updaters()
        step_txt.clear_updaters()
        self.C_grp = dn_grp

    # =========================================================================
    # D  18.3 - 24.5   light takes the quickest path: refraction, then curved spacetime
    # =========================================================================
    def beat_d(self):
        ball = self.ball
        xs = np.linspace(-4.0, 4.0, 8001)
        xstar = xs[np.argmin(fermat_time(xs))]
        X = P3(xstar, 0.0)

        # --- Fermat / refraction picture
        medium = Rectangle(width=11.6, height=2.75, stroke_width=0, fill_color=CYAN, fill_opacity=0.09)
        medium.move_to(P3(0, -1.375))
        bound = Line(P3(-5.8, 0), P3(5.8, 0)).set_stroke(WHITE_, width=1.8, opacity=0.55)
        fast = label("fast", DIM, 22).move_to(P3(5.0, 0.4))
        slow = label("slow", DIM, 22).move_to(P3(5.0, -0.4))
        A_dot = Circle(radius=0.15, stroke_color=WHITE_, stroke_width=1.8, stroke_opacity=0.7).move_to(FA)
        B_dot = Circle(radius=0.15, stroke_color=WHITE_, stroke_width=1.8, stroke_opacity=0.7).move_to(FB)
        straight = DashedLine(FA, FB, dash_length=0.12, stroke_width=1.6, stroke_color=WHITE_,
                              stroke_opacity=0.35)
        d1_static = VGroup(medium, bound, fast, slow, A_dot, B_dot, straight)
        cands = VGroup(*[corners([FA, P3(cx, 0), FB]).set_stroke(CYAN, width=2.0, opacity=0.4)
                         for cx in np.linspace(-1.6, 3.6, 9)])
        true = corners([FA, X, FB])
        neon(true, CYAN, 4.5)

        self.play(FadeOut(self.C_grp, run_time=0.5), FadeIn(d1_static, run_time=0.5),
                  self.hop(FA, lift=1.0, run_time=0.6, col_to=CYAN))                     # 18.9
        self.play(LaggedStart(*[Create(p) for p in cands], lag_ratio=0.12, run_time=0.7))  # 19.6
        self.play(Create(true, run_time=0.4), cands.animate(run_time=0.4).set_stroke(opacity=0.1))  # 20.0

        L1 = float(np.linalg.norm(X - FA))
        L2 = float(np.linalg.norm(FB - X))
        T1, T2 = L1 / V1, L2 / V2
        fl = ValueTracker(0.0)

        def phot():
            t = fl.get_value() * (T1 + T2)
            if t <= T1:
                return FA + (X - FA) * (t / T1)
            return X + (FB - X) * ((t - T1) / T2)
        self.pos_fn = phot
        self.play(UpdateFromAlphaFunc(fl, lambda m, a: m.set_value(a), run_time=0.9, rate_func=linear))  # 20.9
        self.pos_fn = None
        self.wait(0.2)                                                                   # 21.1

        # --- curved spacetime: light bends around a mass
        kt = ValueTracker(0.0)
        xl = np.linspace(-6.4, 6.4, 72)
        yl = np.linspace(-3.0, 3.0, 56)
        lines = [("x", y) for y in np.linspace(-3.0, 3.0, 13)] + [("y", x) for x in np.linspace(-6.0, 6.0, 25)]
        grid = VGroup(*[VMobject() for _ in lines])

        def grid_upd(g):
            k = kt.get_value()
            for m, (kind, c) in zip(g, lines):
                if kind == "x":
                    Xg, Yg = xl, np.full_like(xl, c)
                else:
                    Xg, Yg = np.full_like(yl, c), yl
                m.clear_points()
                m.set_points_as_corners(proj(Xg, Yg, well_z(Xg, Yg, k)))
        grid_upd(grid)
        for m in grid:
            m.set_stroke(CYAN, width=1.6, opacity=0.6)
        grid.add_updater(grid_upd)

        mass = glow_dot(ORIGIN, WHITE_, r=0.16, layers=7)
        mass_pos = lambda: proj(np.array([0.0]), np.array([0.0]), np.array([well_z(0.0, 0.0, kt.get_value())]))[0]
        mass.move_to(mass_pos())
        mass.add_updater(lambda m: m.move_to(mass_pos()))
        K_FINAL = 1.75

        def mirror(pts):      # light travels right -> left
            q = pts.copy()
            q[:, 0] *= -1
            return q

        star_p = mirror(proj(np.array([-6.0]), np.array([0.0]), np.array([well_z(-6.0, 0.0, K_FINAL)])))[0]
        obs_p = mirror(proj(np.array([5.8]), np.array([0.0]), np.array([well_z(5.8, 0.0, K_FINAL)])))[0]
        star_ring = Circle(radius=0.2, stroke_color=CYAN, stroke_width=1.8, stroke_opacity=0.8).move_to(star_p)
        observer = Circle(radius=0.16, stroke_color=WHITE_, stroke_width=2.4).move_to(obs_p)
        observer.add(Dot(radius=0.05, color=WHITE_).move_to(obs_p))

        rays, paths = [], []
        for sgn in (1, -1):
            pts = gr_trace(sgn * self.theta_star)
            Xr, Yr = pts[:, 0], pts[:, 1]
            Pp = mirror(proj(Xr, Yr, well_z(Xr, Yr, K_FINAL) + 0.04))
            r = VMobject()
            r.set_points_as_corners(Pp)
            r.set_stroke(WHITE_, width=2.4, opacity=0.95)
            r.set_stroke(CYAN, width=7, opacity=0.25, background=True)
            rays.append(r)
            paths.append(Pp)
        photon2 = glow_dot(paths[1][0], WHITE_, r=0.05, layers=4)

        self.play(FadeOut(VGroup(d1_static, cands, true), run_time=0.4),
                  FadeIn(grid, run_time=0.5), FadeIn(observer, run_time=0.5),
                  FadeIn(star_ring, run_time=0.5),
                  self.hop(paths[0][0], lift=0.6, run_time=0.5))                        # 21.6
        self.play(FadeIn(mass, run_time=0.3),
                  UpdateFromAlphaFunc(kt, lambda m, a: m.set_value(K_FINAL * a), run_time=0.9))   # 22.5
        grid.clear_updaters()
        mass.clear_updaters()

        fp = ValueTracker(0.0)

        def along(Pp, a):
            i = a * (len(Pp) - 1)
            i0 = int(min(i, len(Pp) - 1))
            i1 = min(i0 + 1, len(Pp) - 1)
            return Pp[i0] * (1 - (i - i0)) + Pp[i1] * (i - i0)
        self.pos_fn = lambda: along(paths[0], fp.get_value())
        photon2.add_updater(lambda m: m.move_to(along(paths[1], fp.get_value())))
        self.add(photon2)
        self.play(UpdateFromAlphaFunc(fp, lambda m, a: m.set_value(a), run_time=1.3, rate_func=linear),
                  *[Create(r, run_time=1.3, rate_func=linear) for r in rays])           # 23.8
        self.pos_fn = None
        photon2.clear_updaters()
        self.wait(0.2)                                                                   # 24.0
        self.D_grp = Group(grid, mass, observer, star_ring, *rays, photon2)

    # =========================================================================
    # E  24.0 - 29.3   countless valleys, and a search that is hard to do but easy to check
    # =========================================================================
    def beat_e(self):
        ball = self.ball
        xs = np.linspace(-5.6, 5.6, 300)
        curve = smooth_curve([rug_pt(x)[:2] for x in xs])
        neon(curve, MAGENTA, 4.0)
        # minima of the rugged curve
        hh = rug_h(np.linspace(-5.6, 5.6, 4000))
        gx = np.linspace(-5.6, 5.6, 4000)
        mins = [gx[i] for i in range(1, 3999) if hh[i] < hh[i - 1] and hh[i] < hh[i + 1]]
        gmin = gx[np.argmin(hh)]
        glints = []
        for mx in mins:
            c = CYAN if abs(mx - gmin) < 1e-6 else GOLD
            glints.append(glow_dot(rug_pt(mx), c, r=0.07, layers=4))

        traj, xm = rug_roll()
        traj_pts = np.array([rug_pt(x) for x in traj])

        # hand-off: photon becomes a ball again, on a rugged landscape
        self.play(FadeOut(self.D_grp, run_time=0.4), FadeIn(curve, run_time=0.5),
                  self.hop(rug_pt(RUG_X0), lift=0.7, run_time=0.6, col_to=MAGENTA))     # 24.6

        fr = ValueTracker(0.0)

        def roll_pos():
            i = fr.get_value() * (len(traj_pts) - 1)
            i0 = int(min(i, len(traj_pts) - 1))
            i1 = min(i0 + 1, len(traj_pts) - 1)
            return traj_pts[i0] * (1 - (i - i0)) + traj_pts[i1] * (i - i0)
        self.pos_fn = roll_pos
        self.play(UpdateFromAlphaFunc(fr, lambda m, a: m.set_value(a), run_time=1.3, rate_func=rush_from))  # 25.9
        self.pos_fn = None
        # countless valleys
        self.play(LaggedStart(*[FadeIn(g, scale=0.3) for g in glints], lag_ratio=0.12, run_time=0.75))   # 26.65
        gring = Circle(radius=0.12, stroke_color=CYAN, stroke_width=2.5).move_to(rug_pt(gmin))
        self.play(gring.animate(run_time=0.35).scale(3.2).set_stroke(opacity=0))          # 27.25
        self.remove(gring)

        # find is hard, check is instant
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
        for l in range(1, L - 2):
            nonsol = [(l + 1, jj) for jj in range(layers[l + 1]) if (l + 1, jj) not in sol]
            if nonsol:
                edges.add((sol[l], nonsol[rng.randint(len(nonsol))]))
        adj = {}
        for a, b in edges:
            adj.setdefault(a, []).append(b)
        order = []

        def dfs(u):
            kids = sorted(adj.get(u, []), key=lambda v: (v in sol, rng.rand()))
            for v in kids:
                order.append((u, v))
                dfs(v)
        dfs((0, 0))

        def build(cx):
            off = np.array([cx, 0.35, 0])
            es = {e: Line(pos[e[0]] + off, pos[e[1]] + off, stroke_width=1.8, color=DIM) for e in edges}
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
        pnp = MathTex(r"\mathrm{P}\;\overset{?}{=}\;\mathrm{NP}", color=MAGENTA).scale(1.15).move_to(P3(0, 0.35))
        findL = VGroup(label("find", WHITE_, 34), label("slow", MAGENTA, 24)).arrange(DOWN, buff=0.12)
        findL.move_to(P3(-3.9, -1.85))
        chkR = VGroup(label("check", WHITE_, 34), label("fast", MAGENTA, 24)).arrange(DOWN, buff=0.12)
        chkR.move_to(P3(3.9, -1.85))

        root = pos[(0, 0)] + offL
        self.play(FadeOut(VGroup(curve, *glints), run_time=0.3),
                  FadeIn(gL, run_time=0.5), FadeIn(gR, run_time=0.5), FadeIn(goalL, run_time=0.5),
                  FadeIn(goalR, run_time=0.5), FadeIn(findL, run_time=0.5), FadeIn(chkR, run_time=0.5),
                  FadeIn(pnp, run_time=0.5),
                  self.hop(root, lift=0.6, run_time=0.5))                                # 27.75

        flashes = []
        for e in order:
            f = esL[e].copy().set_stroke(MAGENTA, width=6, opacity=1.0)
            flashes.append(ShowPassingFlash(f, time_width=1.0))
        search = LaggedStart(*flashes, lag_ratio=0.07, run_time=1.4)
        solR = [esR[e].copy() for e in zip(sol[:-1], sol[1:])]
        for m in solR:
            neon(m, MAGENTA, 6.0)
        chk = MathTex(r"\checkmark", color=GOLD).scale(1.1).next_to(goalR, RIGHT, buff=0.2)
        check = Succession(LaggedStart(*[Create(m) for m in solR], lag_ratio=0.5, run_time=0.5),
                           FadeIn(chk, run_time=0.2))
        self.play(AnimationGroup(search, check))                                         # 29.15
        solL = [esL[e].copy() for e in zip(sol[:-1], sol[1:])]
        for m in solL:
            neon(m, MAGENTA, 6.0)
        self.play(LaggedStart(*[Create(m) for m in solL], lag_ratio=0.5, run_time=0.35),
                  goalL.animate(run_time=0.35).set_color(GOLD))                          # 29.5
