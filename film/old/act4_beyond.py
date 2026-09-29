from style import *


# =============================================================================
#  numpy generators (all precomputed once at the top of construct)
# =============================================================================
def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def soft_mask(h, w, frac=0.07):
    """Alpha mask that fades the image borders into the background."""
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


# ---- Mandelbrot ------------------------------------------------------------
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


def make_mandel_frames(n=110, W=640, H=360):
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


# ---- mug -> donut ----------------------------------------------------------
def catmull(pts, n=400, closed=True):
    P = np.array(pts, float)
    if closed:
        P = np.vstack([P[-1], P, P[0], P[1]])
    out = []
    m = len(P) - 3
    for i in range(m):
        p0, p1, p2, p3 = P[i:i + 4]
        t = np.linspace(0, 1, 24, endpoint=False)[:, None]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.vstack(out)


def resample(curve, n):
    c = np.vstack([curve, curve[:1]])
    seg = np.linalg.norm(np.diff(c, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n, endpoint=False)
    return np.stack([np.interp(t, s, c[:, 0]), np.interp(t, s, c[:, 1])], -1)


def mug_donut_shapes(n=260):
    outer = [(-1.40, 1.24), (-1.43, 1.0), (-1.43, -0.9), (-1.40, -1.14), (-1.30, -1.26), (-1.1, -1.29),
             (0.6, -1.29), (0.80, -1.26), (0.90, -1.14), (0.93, -0.9), (0.93, -0.66),
             (1.25, -0.66), (1.7, -0.45), (1.98, 0.05), (1.9, 0.6), (1.5, 0.94), (0.93, 0.88),
             (0.93, 1.0), (0.90, 1.14), (0.80, 1.26), (0.6, 1.29), (-1.1, 1.29), (-1.30, 1.26)]
    hole = [(0.93, 0.52), (1.25, 0.56), (1.55, 0.32), (1.62, 0.02), (1.47, -0.24), (1.15, -0.32),
            (0.93, -0.28), (0.93, 0.1)]
    mo = resample(catmull(outer), n)
    mh = resample(catmull(hole), n)[::-1]          # opposite orientation -> a real hole
    # donut: same orientation as outer (CCW from top-left) and hole CW
    ang = np.radians(135) + np.linspace(0, 2 * np.pi, n, endpoint=False)
    do = np.stack([1.75 * np.cos(ang), 1.32 * np.sin(ang)], -1)
    ah = np.radians(135) - np.linspace(0, 2 * np.pi, n, endpoint=False)
    dh = np.stack([0.66 * np.cos(ah), 0.44 * np.sin(ah) + 0.05], -1)
    # align start of mug hole (reversed) with a top-left start
    k = int(np.argmin((mh[:, 0] - 0.93) ** 2 * 4 + (mh[:, 1] - 0.5) ** 2))
    mh = np.roll(mh, -k, axis=0)
    ctr = np.array([-0.28, 0.0])
    return mo - ctr, mh - ctr, do, dh


# ---- Riemann zeta ----------------------------------------------------------
ZEROS = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187, 43.3271, 48.0052, 49.7738]


# ---- general relativity ----------------------------------------------------
GR_G, GR_EPS = 0.55, 0.35


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


ELEV = np.radians(50)
GR_Y0 = 0.45


def proj(x, y, z):
    yy = y * np.sin(ELEV) + z * np.cos(ELEV)
    dd = y * np.cos(ELEV) - z * np.sin(ELEV)
    f = 1.0 / (1.0 + 0.03 * dd)
    return np.stack([x * f * 0.97, yy * f + GR_Y0, np.zeros_like(x)], -1)


# ---- double slit -----------------------------------------------------------
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


# ---- loss landscape --------------------------------------------------------
LS_W, LS_H = 7.6, 4.3


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


# ---- noise -> image --------------------------------------------------------
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
    # water reflection of the sun in the lower part
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


# =============================================================================
class Act4(FilmScene):
    DURATION = BUDGET["act4"]

    def sec_out(self, *mobs, t=0.4):
        self.play(*[FadeOut(m) for m in mobs], run_time=t)

    def construct(self):
        # ------------------------------------------------------------ precompute
        mb_frames = make_mandel_frames()
        mo, mh, do, dh = mug_donut_shapes()
        rng = np.random.default_rng(11)
        ds_hits = ds_sample(2400, rng)
        ds_x = rng.uniform(0, 1, 2400)
        ds_slit = rng.integers(0, 2, 2400)
        theta_star = gr_solve_theta()
        loss_rgba = loss_image()
        gd_path = descent_path()
        dn_frames = denoise_frames()

        self.tag("04", "BEYOND", WHITE_, start=0.1, dur=3.6)

        # =====================================================================
        #  MATH (gold)                                              t = 0 .. 12.0
        # =====================================================================
        # ---- (a) Mandelbrot zoom ------------------------------------------- 5.5 s
        self.caption("Simple rules. Infinite complexity.", start=0.6, dur=4.6)
        mb = ImageMobject(mb_frames[0][0])
        mb.height = 4.6
        mb.move_to([-0.6, 0.35, 0])
        mb.set_resampling_algorithm(RESAMPLING_ALGORITHMS["cubic"])
        mb_T = ValueTracker(0.0)          # 0..1 zoom progress

        def mb_upd(m):
            i = int(np.clip(mb_T.get_value(), 0, 1) * (len(mb_frames) - 1) + 0.5)
            set_img(m, mb_frames[i][0])
        mb.add_updater(mb_upd)

        frame_box = Rectangle(width=mb.width, height=mb.height, stroke_width=1.2, stroke_color=GOLD,
                              stroke_opacity=0.25).move_to(mb)
        formula = MathTex(r"z \mapsto z^{2}+c", color=GOLD).scale(1.05).move_to([5.3, 1.3, 0])
        zoom_txt = Text("x 1", font=MONO, font_size=22, color=GOLD).move_to([5.3, 0.5, 0])

        def zt_upd(m):
            i = int(np.clip(mb_T.get_value(), 0, 1) * (len(mb_frames) - 1) + 0.5)
            z = mb_frames[i][1]
            new = Text(f"x {z:,.0f}", font=MONO, font_size=22, color=GOLD)
            new.move_to([5.3, 0.5, 0])
            m.become(new)
        mb_grp = Group(mb, frame_box, formula, zoom_txt)
        self.play(FadeIn(mb_grp), run_time=0.5)                                   # 0.5
        zoom_txt.add_updater(zt_upd)
        self.play(mb_T.animate.set_value(1.0), run_time=4.6, rate_func=linear)    # 5.1
        self.sec_out(mb_grp, t=0.4)                                               # 5.5

        # ---- (b) mug -> donut ---------------------------------------------- 3.2 s
        self.caption("To a topologist, a mug is a donut.", start=0.3, dur=2.7)
        MUG_S, MUG_C = 1.45, np.array([-0.4, 0.35, 0])
        morph = ValueTracker(0.0)
        body = VMobject()
        hole_line = VMobject()

        def to_scene(a):
            return np.column_stack([a[:, 0] * MUG_S, a[:, 1] * MUG_S, np.zeros(len(a))]) + MUG_C

        def shape_upd(_=None):
            m = smoothstep(morph.get_value())
            m = smoothstep(m)
            o = to_scene((1 - m) * mo + m * do)
            h = to_scene((1 - m) * mh + m * dh)
            body.clear_points()
            body.set_points_as_corners(np.vstack([o, o[:1]]))
            body.start_new_path(h[0])
            body.add_points_as_corners(np.vstack([h[1:], h[:1]]))
            hole_line.clear_points()
            hole_line.set_points_as_corners(np.vstack([h, h[:1]]))
        shape_upd()
        body.set_fill(GOLD, opacity=0.14)
        neon(body, GOLD, 4.0)
        hole_line.set_stroke(WHITE_, width=3, opacity=0.9)
        body.add_updater(shape_upd)
        chi = MathTex(r"\chi = 0", color=GOLD).scale(1.0).move_to([5.0, 1.2, 0])
        g1 = MathTex(r"\text{one hole}", color=WHITE_).scale(0.7).next_to(chi, DOWN, buff=0.3)
        mug_grp = VGroup(body, hole_line, chi, g1)
        self.play(FadeIn(mug_grp), run_time=0.5)                                   # 0.5
        self.wait(0.4)                                                            # 0.9
        self.play(morph.animate.set_value(1.0), run_time=1.5, rate_func=linear)   # 2.4
        self.wait(0.4)                                                            # 2.8
        self.sec_out(mug_grp, t=0.4)                                              # 3.2
        body.clear_updaters()

        # ---- (c) Riemann zeta ---------------------------------------------- 3.3 s
        self.caption("The primes hide in the zeros of one function.", start=0.3, dur=3.0)
        SX, SW, Y0, SC = -3.2, 1.7, -2.0, 0.09
        strip = Rectangle(width=SW, height=52.5 * SC + 0.3, stroke_width=0)
        strip.set_fill(GOLD, opacity=0.06)
        strip.move_to([SX, Y0 + (52.5 * SC + 0.3) / 2 - 0.15, 0])
        edges = VGroup(*[Line([SX + dx, Y0, 0], [SX + dx, Y0 + 52.5 * SC + 0.15, 0], stroke_width=1.4,
                              stroke_color=GOLD, stroke_opacity=0.4) for dx in (-SW / 2, SW / 2)])
        base = Line([SX - SW / 2 - 0.2, Y0, 0], [SX + SW / 2 + 0.2, Y0, 0], stroke_width=1.4,
                    stroke_color=DIM)
        crit = DashedLine([SX, Y0, 0], [SX, Y0 + 52.5 * SC + 0.15, 0], dash_length=0.12, stroke_width=2.4,
                          stroke_color=GOLD)
        neon(crit, GOLD, 2.4)
        crit_lab = MathTex(r"\mathrm{Re}(s)=\tfrac12", color=GOLD).scale(0.62).move_to([SX, 3.05, 0])
        zero_dots = VGroup(*[glow_dot([SX, Y0 + g * SC, 0], GOLD, r=0.065, layers=4) for g in ZEROS])
        val_labs = VGroup(*[Text(f"{g:.2f}", font=MONO, font_size=18, color=GOLD).move_to(
            [SX - SW / 2 - 0.5, Y0 + g * SC, 0]) for g in ZEROS[:3]])
        # waveform panel
        WX0, WX1, WY = -0.4, 6.3, 0.35
        wave_axis = Line([WX0, WY, 0], [WX1, WY, 0], stroke_width=1.2, stroke_color=DIM, stroke_opacity=0.7)
        wave_lab = MathTex(r"\sum_{\gamma}\cos(\gamma\, u)", color=CYAN).scale(0.7).move_to([2.95, 2.3, 0])
        n_tr = ValueTracker(0.0)
        wave = VMobject()
        uu = np.linspace(0.25, 4.65, 460)
        gam = np.array(ZEROS)

        def wave_upd(m):
            n = n_tr.get_value()
            w = np.clip(n - np.arange(len(gam)), 0, 1)
            y = (w[None, :] * np.cos(gam[None, :] * uu[:, None])).sum(1)
            y = y / np.sqrt(w.sum() + 0.6) * 0.95
            y = 1.15 * np.tanh(y / 1.15)
            xs = WX0 + (WX1 - WX0) * (uu - uu[0]) / (uu[-1] - uu[0])
            m.clear_points()
            m.set_points_as_corners(np.column_stack([xs, WY + 1.05 * y, np.zeros_like(xs)]))
        wave_upd(wave)
        neon(wave, CYAN, 3.0)
        wave.add_updater(wave_upd)
        z_static = VGroup(strip, edges, base, crit, crit_lab, wave_axis, wave_lab, val_labs)
        self.play(FadeIn(z_static), run_time=0.5)                                    # 0.5
        self.add(wave, zero_dots)
        self.play(LaggedStart(*[FadeIn(d, scale=0.2) for d in zero_dots], lag_ratio=0.28),
                  n_tr.animate.set_value(float(len(gam))), run_time=1.9, rate_func=linear)   # 2.4
        self.wait(0.4)                                                                # 2.8
        self.sec_out(z_static, zero_dots, wave, t=0.4)                                # 3.3
        wave.clear_updaters()

        # =====================================================================
        #  PHYSICS (cyan)                                          t = 12.0 .. 23.6
        # =====================================================================
        # ---- (a) general relativity ---------------------------------------- 5.6 s
        self.caption("Mass tells space how to curve. Space tells light how to move.", start=0.5, dur=5.0)
        kt = ValueTracker(0.0)
        xl = np.linspace(-6.4, 6.4, 72)
        yl = np.linspace(-3.0, 3.0, 56)
        lines = []
        for y in np.linspace(-3.0, 3.0, 13):
            lines.append(("x", y))
        for x in np.linspace(-6.0, 6.0, 25):
            lines.append(("y", x))
        grid = VGroup(*[VMobject() for _ in lines])

        def grid_upd(g):
            k = kt.get_value()
            for m, (kind, c) in zip(g, lines):
                if kind == "x":
                    X, Y = xl, np.full_like(xl, c)
                else:
                    X, Y = np.full_like(yl, c), yl
                m.clear_points()
                m.set_points_as_corners(proj(X, Y, well_z(X, Y, k)))
        grid_upd(grid)
        for m, (kind, c) in zip(grid, lines):
            m.set_stroke(CYAN, width=1.6, opacity=0.6)
        grid.add_updater(grid_upd)

        mass = glow_dot(ORIGIN, WHITE_, r=0.16, layers=7)
        mass_pos = lambda: proj(np.array([0.0]), np.array([0.0]), np.array([well_z(0.0, 0.0, kt.get_value())]))[0]
        mass.move_to(mass_pos())
        mass.add_updater(lambda m: m.move_to(mass_pos()))
        K_FINAL = 1.75
        star = glow_dot(proj(np.array([-6.0]), np.array([0.0]), np.array([well_z(-6.0, 0.0, K_FINAL)]))[0],
                        GOLD, r=0.1, layers=6)
        obs_p = proj(np.array([5.8]), np.array([0.0]), np.array([well_z(5.8, 0.0, K_FINAL)]))[0]
        observer = Circle(radius=0.16, stroke_color=WHITE_, stroke_width=2.4).move_to(obs_p)
        observer.add(Dot(radius=0.05, color=WHITE_).move_to(obs_p))

        rays, photons = [], []
        for mult in (1.0, 0.86):
            for sgn in (1, -1):
                pts = gr_trace(sgn * theta_star * mult)
                X, Y = pts[:, 0], pts[:, 1]
                P = proj(X, Y, well_z(X, Y, K_FINAL) + 0.04)
                r = VMobject()
                r.set_points_as_corners(P)
                r.set_stroke(WHITE_, width=2.4, opacity=0.95)
                r.set_stroke(CYAN, width=7, opacity=0.25, background=True)
                rays.append(r)
                photons.append(glow_dot(P[0], WHITE_, r=0.05, layers=4))

        self.play(FadeIn(grid), FadeIn(star), FadeIn(observer), run_time=0.6)        # 0.6
        self.play(FadeIn(mass), run_time=0.3)                                        # 0.9
        self.play(kt.animate.set_value(K_FINAL), run_time=1.2, rate_func=smooth)     # 2.1
        self.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.12), run_time=1.4)   # 3.5
        self.add(*photons)
        self.play(*[MoveAlongPath(p, r, rate_func=linear) for p, r in zip(photons, rays)],
                  run_time=1.3)                                                      # 4.8
        self.wait(0.3)                                                              # 5.1
        gr_grp = Group(grid, star, observer, mass, *rays, *photons)
        self.sec_out(gr_grp, t=0.4)                                                  # 5.6
        grid.clear_updaters()
        mass.clear_updaters()

        # ---- (b) double slit ------------------------------------------------ 6.0 s
        self.caption("One particle at a time, an interference pattern emerges.", start=0.3, dur=5.4)
        BX, SRC = -2.6, np.array([-5.8, 0.25, 0])
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
        source = glow_dot(SRC, CYAN, r=0.11, layers=6)
        src_beam = DashedLine(SRC, [BX, PCY, 0], dash_length=0.1, stroke_width=1.4, stroke_color=CYAN,
                              stroke_opacity=0.35)
        plate_top, plate_bot = PCY + DS_HALF, PCY - DS_HALF
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
            return 5.0 * np.exp((t - 1.5) * np.log(2400 / 5.0) / (T_END - 1.5))

        def plate_upd(m):
            n = min(int(count(ds_T.get_value())), 2400)
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

        # histogram (gold: probability) --------------------------------------
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

        # ripples from the two slits -----------------------------------------
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

        ds_static = Group(barrier, source, src_beam, plate_frame, hist_axis)
        self.play(FadeIn(ds_static), run_time=0.6)                                   # 0.6
        self.add(rip, plate, hist, flyer)
        self.play(ds_T.animate.set_value(T_END), Succession(Wait(T_END - 1.0), Create(theory, run_time=1.0)),
                  run_time=T_END, rate_func=linear)                                   # 5.1
        self.wait(0.5)                                                              # 5.6
        ds_grp = Group(ds_static, rip, plate, hist, flyer, theory)
        self.sec_out(ds_grp, t=0.4)                                                  # 6.0
        plate.clear_updaters()
        hist.clear_updaters()

        # =====================================================================
        #  COMPUTER SCIENCE (magenta)                             t = 23.6 .. 34.0
        # =====================================================================
        # ---- neural network ------------------------------------------------- 3.0 s
        layers = [3, 5, 5, 2]
        lx = [-4.2, -1.4, 1.4, 4.2]
        cy = 0.35
        node_pos = []
        for L, x in zip(layers, lx):
            ys_ = (np.arange(L) - (L - 1) / 2) * 0.95 + cy
            node_pos.append([np.array([x, y, 0]) for y in ys_])
        edges_l = []
        edge_layers = []
        for a in range(3):
            row = []
            for pa in node_pos[a]:
                for pb in node_pos[a + 1]:
                    e = Line(pa, pb, stroke_width=1.5, stroke_color=MAGENTA, stroke_opacity=0.34)
                    row.append(e)
            edge_layers.append(row)
            edges_l += row
        node_cols = [CYAN, MAGENTA, MAGENTA, GOLD]
        nodes, halos = [], []
        for li, col in enumerate(node_cols):
            for p in node_pos[li]:
                halos.append(Circle(radius=0.38, stroke_width=0, fill_color=col, fill_opacity=0.10).move_to(p))
                nodes.append(Circle(radius=0.22, stroke_width=3, stroke_color=col, fill_color=BG,
                                    fill_opacity=1).move_to(p))
        net = VGroup(VGroup(*edges_l), VGroup(*halos), VGroup(*nodes))

        self.play(FadeIn(net), run_time=0.6)                                         # 0.6

        def pulse_anims(row, col, rev=False):
            out = []
            for e in row:
                c = e.copy().set_stroke(col, width=4.5, opacity=1)
                if rev:
                    c.rotate(PI, about_point=c.get_center())
                out.append(ShowPassingFlash(c, time_width=0.6))
            return out
        # forward pass: cyan -> magenta -> gold
        for row, col in zip(edge_layers, [CYAN, WHITE_, GOLD]):
            self.play(*pulse_anims(row, col), run_time=0.36)
        # (3 * 0.36 = 1.08)                                                            # 1.68
        # backward pass in magenta
        for row in reversed(edge_layers):
            self.play(*pulse_anims(row, MAGENTA, rev=True), run_time=0.3)
        # (3 * 0.3 = 0.9)                                                              # 2.58

        # ---- loss landscape -------------------------------------------------- 3.9 s
        self.caption("A machine learns by rolling downhill.", start=0.2, dur=3.7)
        LC = np.array([1.6, 0.3, 0])
        land = ImageMobject(loss_rgba)
        land.height = LS_H
        land.move_to(LC)
        land.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
        lab_L = MathTex(r"L(\theta)", color=MAGENTA).scale(0.9).move_to([-5.05, -0.25, 0])
        self.play(net.animate.scale(0.29).move_to([-5.0, 1.45, 0]),
                  Succession(Wait(0.35), AnimationGroup(FadeIn(land), FadeIn(lab_L), run_time=0.45)),
                  run_time=0.8)                                                      # 0.8
        P = np.column_stack([gd_path[:, 0], gd_path[:, 1], np.zeros(len(gd_path))]) + LC
        prog = ValueTracker(0.0)
        trail = VMobject()
        ball = glow_dot(P[0], WHITE_, r=0.1, layers=6)

        def ball_upd(m):
            i = prog.get_value() * (len(P) - 1)
            i0 = int(i)
            f = i - i0
            i1 = min(i0 + 1, len(P) - 1)
            m.move_to(P[i0] * (1 - f) + P[i1] * f)
            pts = np.vstack([P[:i0 + 1], m.get_center()[None, :]])
            trail.clear_points()
            if len(pts) > 1:
                trail.set_points_as_corners(pts)
        trail.set_stroke(CYAN, width=3.4)
        trail.set_stroke(CYAN, width=10, opacity=0.25, background=True)
        ball.add_updater(ball_upd)
        trail.add_updater(lambda m: None)   # keep trail out of the cached static layer
        start_marker = Circle(radius=0.16, stroke_color=WHITE_, stroke_width=1.6, stroke_opacity=0.7).move_to(P[0])
        self.add(trail, ball)
        self.add(start_marker)
        self.play(prog.animate.set_value(1.0), run_time=2.2, rate_func=smooth)   # 3.0
        ring = Circle(radius=0.12, stroke_color=WHITE_, stroke_width=3).move_to(P[-1])
        self.play(ring.animate.scale(4.5).set_stroke(opacity=0), run_time=0.4)     # 3.4
        ls_grp = Group(net, land, lab_L, trail, ball, start_marker, ring)
        self.sec_out(ls_grp, t=0.4)                                                  # 3.8
        ball.clear_updaters()

        # ---- noise -> image ------------------------------------------------- 3.7 s
        dn = ImageMobject(dn_frames[0])
        dn.height = 3.9
        dn.move_to([0, 0.45, 0])
        dn.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        dn_T = ValueTracker(0.0)

        def dn_upd(m):
            i = min(len(dn_frames) - 1, int(dn_T.get_value() * len(dn_frames)))
            set_img(m, dn_frames[i])
        dn.add_updater(dn_upd)
        dn_frame = Rectangle(width=dn.width + 0.12, height=dn.height + 0.12, stroke_width=2,
                             stroke_color=MAGENTA, stroke_opacity=0.8).move_to(dn)
        dn_frame.set_stroke(MAGENTA, width=8, opacity=0.18, background=True)
        step_txt = Text("noise   t = 1.00   image", font=MONO, font_size=22, color=MAGENTA).move_to([0, -1.85, 0])

        def st_upd(m):
            i = min(len(dn_frames) - 1, int(dn_T.get_value() * len(dn_frames)))
            new = Text(f"noise   t = {1 - i / (len(dn_frames) - 1):.2f}   image", font=MONO, font_size=22,
                       color=MAGENTA)
            new.move_to([0, -1.85, 0])
            m.become(new)
        dn_grp = Group(dn, dn_frame, step_txt)
        self.play(FadeIn(dn_grp), run_time=0.4)                                      # 0.4
        step_txt.add_updater(st_upd)
        self.play(dn_T.animate.set_value(1.0), run_time=3.0, rate_func=smooth)     # 3.4
        self.wait(0.3)                                                              # 3.7
        # total CS = 2.6 + 3.8 + 3.9 = 10.3  -> final fade_all below
        self.fade_all(0.7)
        self.pad_to()
