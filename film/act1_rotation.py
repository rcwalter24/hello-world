"""ACT 1 - ROTATION (25 s).  One rotating point is handed across the disciplines.

  A  0-5    MATHEMATICS (gold)  circle rolls out pi; a point spins            level 0
  B  5-10   gold -> cyan        height traced as a sine -> water ripples      level 1
  C  10-15  PHYSICS (cyan)      E and B waves = light; e^{i theta}, e^{i pi}   level 2
  D  15-21  gold -> magenta     epicycles build a square wave -> samples ->   level 2
                                spectrum -> keep the tallest rotations
  E  21-25  FRONTIER            zeta zeros + Langlands islands                level 3

Architecture: ONE persistent rig (circle, spokes, epicycle arms, glow dot) and ONE
persistent curve, all redrawn every frame by a single driver updater from
ValueTrackers.  The hand-offs only change trackers (hue, scale, length ...), so the
curve is never cut - it morphs and recolours.
"""
from style import *
from types import SimpleNamespace
import numpy as np

# ------------------------------------------------------------------ constants
OMEGA = 3.4                    # base spin (rad/s)
KAPPA = 0.55                   # scene units of curve per radian of history
NH = 16                        # harmonics available: n = 1,3,...,31
NS = 2.0 * np.arange(NH) + 1.0
IDX = np.arange(NH)
NARM = 8                       # epicycle arms actually drawn
NSMP = 64                      # samples across one period
STOPS = [GOLD, CYAN, GOLD, MAGENTA]
B_COL = "#7C8CFF"

X0R, YB, RR = -5.0, 0.3, 0.8                 # rolling circle
B_CX, B_CY, B_R, B_X0 = -4.75, 0.5, 1.25, -3.0
C_CX, C_CY, C_R, C_X0 = -4.75, 0.0, 1.0, -3.3
D_R, D_X0 = 1.2, -2.2
EMD = np.array([0.59, 0.34])                 # oblique direction of the B field


def sm(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def col_at(h):
    h = float(np.clip(h, 0, 3))
    i = min(int(h), 2)
    return interpolate_color(ManimColor(STOPS[i]), ManimColor(STOPS[i + 1]), h - i)


def trap(a=0.25, b=0.3):
    """rate function: ease in over a, cruise, ease out over b (position vs time)."""
    xs = np.linspace(0, 1, 1001)
    v = np.minimum(sm(xs / a), sm((1 - xs) / b))
    p = np.cumsum(v)
    p = (p - p[0]) / (p[-1] - p[0])
    return lambda x: float(np.interp(x, xs, p))


def tw(tracker, value, dur, rate=smooth):
    """Tween a ValueTracker to `value`.  Start value is read on the first call with a>0
    (Animation.begin() also calls interpolate(0), which must not count)."""
    st = {"v0": None}

    def f(_m, a):
        if st["v0"] is None:
            if a <= 0:
                return
            st["v0"] = tracker.get_value()
        tracker.set_value(st["v0"] + (value - st["v0"]) * a)
    return UpdateFromAlphaFunc(tracker, f, run_time=dur, rate_func=rate)


def Do(fn):
    st = {"done": False}

    def f(_m, a):
        if a > 0 and not st["done"]:
            st["done"] = True
            fn()
    return UpdateFromAlphaFunc(Mobject(), f, run_time=1 / 15, rate_func=linear)


def seg_pts(P0, P1):
    """Bezier control points for many disjoint straight segments (one VMobject)."""
    P0, P1 = np.asarray(P0, float), np.asarray(P1, float)
    d = P1 - P0
    return np.stack([P0, P0 + d / 3, P0 + 2 * d / 3, P1], axis=1).reshape(-1, 3)


def set_segs(vm, P0, P1):
    if len(P0) == 0:
        vm.set_points(seg_pts([[0, 0, 0]], [[0, 0, 0.0]]))
    else:
        vm.set_points(seg_pts(P0, P1))


class Timed(AnimationGroup):
    """AnimationGroup with explicit absolute start times (seconds from group start).
    Delayed introducers are hidden until their turn; nothing suspends updaters."""

    def __init__(self, events, total):
        anims = [a for _, a in events]
        super().__init__(*anims, lag_ratio=0, suspend_mobject_updating=False)
        awt = self.anims_with_timings
        for k, (t0, a) in enumerate(events):
            awt["start"][k] = t0
            awt["end"][k] = t0 + a.run_time
        end = max(total, float(awt["end"].max()))
        if end > total + 1e-6:
            print(f"!! Timed: an event ends at {end:.2f} > {total:.2f}")
        self.max_end_time = end
        self.run_time = end
        self._events = events

        def nosusp(an):
            an.suspend_mobject_updating = False
            for c in getattr(an, "animations", []):
                nosusp(c)
        for a in anims:
            nosusp(a)

    def begin(self):
        super().begin()

        def hide(an):
            for c in getattr(an, "animations", []):
                hide(c)
            if an.is_introducer() and not hasattr(an, "animations"):
                an.interpolate(0)
        for t0, a in self._events:
            if t0 > 1e-6:
                hide(a)


def live(m):
    """no-op updater: keeps a driver-modified mobject out of the static layer."""
    m.add_updater(lambda _m: None)
    return m


# ------------------------------------------------------------------ water field
IW, IH = 576, 288
UW, UH = 9.6, 4.8
IMG_C = np.array([0.0, 0.2, 0.0])
SRC_X = -3.7
WAVELEN = 0.9
KW = 2 * np.pi / WAVELEN
CSPD = 2.6
_xs = (np.arange(IW) + 0.5) / IW * UW - UW / 2
_ys = UH / 2 - (np.arange(IH) + 0.5) / IH * UH
_X, _Y = np.meshgrid(_xs, _ys)
_WIN = sm((UW / 2 - np.abs(_X)) / 0.9) * sm((UH / 2 - np.abs(_Y)) / 0.7)
_BGC = np.array([7, 10, 20], float)
_CY = np.array([76, 201, 240], float)
_DEEP = np.array([16, 44, 110], float)


def wave_frame(front, th, d, op):
    """RGBA water surface: two point sources, phase tied to the rotating point (th)."""
    r1 = np.hypot(_X - SRC_X, _Y - d / 2)
    r2 = np.hypot(_X - SRC_X, _Y + d / 2)

    def w(r):
        return np.cos(KW * r - th + np.pi / 2) / np.sqrt(1 + 0.4 * r) * sm((front - r) / 0.5)

    v = np.clip((w(r1) + w(r2)) / 1.5, -1, 1)
    crest, trough = np.clip(v, 0, 1), np.clip(-v, 0, 1)
    col = (_BGC + (_CY - _BGC) * (crest ** 1.5)[..., None]
           + (_DEEP - _BGC) * (0.55 * trough)[..., None])
    hi = np.clip((crest - 0.8) / 0.2, 0, 1) ** 2
    col = col + (255 - col) * (0.55 * hi)[..., None]
    col = _BGC + (col - _BGC) * (_WIN * op)[..., None]
    out = np.empty((IH, IW, 4), np.uint8)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = 255
    return out


ZEROS = [14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187, 43.3271, 48.0052, 49.7738]


class Act1(FilmScene):
    DURATION = BUDGET["act1"]

    # ------------------------------------------------------------ utilities
    def now(self):
        return self.renderer.time

    def cap(self, text, t0, t1):
        self.caption(text, start=max(0.0, t0 - self.now()), dur=t1 - t0)

    def timeline(self, t_end, events):
        """Run animations that start at absolute times; the call returns at t_end."""
        now = self.now()
        rt = t_end - now
        if rt <= 0.02:
            print(f"!! timeline overrun at {now:.2f} (wanted {t_end})")
            return
        self.play(Timed([(max(0.0, t0 - now), an) for t0, an in events], rt))

    def mark(self, s):
        print(f"[act1] {s}: t={self.now():.2f}")

    # ------------------------------------------------------------ the rig
    def build_rig(self):
        T = ValueTracker
        tr = dict(th=T(-PI / 2), spin=T(0.0), cx=T(X0R), cy=T(YB + RR), R=T(RR), vRig=T(0.0),
                  hue=T(0.0), nact=T(1.0), vCurve=T(0.0), x0=T(B_X0), sig=T(1.0), alpha=T(1.0),
                  cyc=T(B_CY), Lx=T(0.0), tap=T(1.0), vConn=T(0.0), vAxis=T(0.0), vEM=T(0.0),
                  vStems=T(0.0), vRecon=T(0.0), keep=T(16.0), vTrace=T(0.0))
        self.tr = tr
        g = lambda k: tr[k].get_value()
        P3 = lambda z: np.array([z.real, z.imag, 0.0])

        unit = Circle(radius=1.0).points.copy()
        circ = neon(Circle(radius=1.0), GOLD, 3.5)
        arms = [Circle(radius=1.0).set_stroke(GOLD, 1.6, 0.0) for _ in range(NARM - 1)]
        spokes = [VMobject().set_points_as_corners([ORIGIN, RIGHT * 0.01]) for _ in range(NARM)]
        dot = glow_dot(ORIGIN, GOLD, r=0.07, layers=7)
        dbase = [dot[k].get_fill_opacity() for k in range(len(dot) - 1)]

        def vm():
            return VMobject().set_points_as_corners([ORIGIN, RIGHT * 0.01])
        curve, bcurve, recon, axis, trace, conn = vm(), vm(), vm(), vm(), vm(), vm()
        estems, bstems, samples = vm(), vm(), vm()
        self.curve = curve

        def field(s, th, a, R, alpha, x0, sig, Lx, tapv):
            f_ = ((a / NS)[None, :] * np.sin(np.outer(th - s / KAPPA, NS))).sum(1)
            env = 1.0 - tapv * (1.0 - sm((Lx - sig * s) / 0.8))
            return alpha * R * f_ * env

        def drive(_m, dt):
            sp = g("spin")
            if sp > 0:
                tr["th"].increment_value(OMEGA * sp * dt)
            th, cx, cy, R, vr = g("th"), g("cx"), g("cy"), g("R"), g("vRig")
            col = col_at(g("hue"))
            a = np.clip(g("nact") - IDX, 0, 1)
            rad = R * a / NS
            J = (cx + 1j * cy) + np.concatenate([[0], np.cumsum(rad * np.exp(1j * NS * th))])
            # ---- rig
            circ.set_points(unit * R + np.array([cx, cy, 0.0]))
            circ.set_stroke(col, 3.5, vr)
            circ.set_stroke(col, 11.0, 0.18 * vr, background=True)
            for i in range(1, NARM):
                arms[i - 1].set_points(unit * max(rad[i], 1e-3) + P3(J[i]))
                arms[i - 1].set_stroke(col, 1.6, a[i] * vr * 0.5)
            for i in range(NARM):
                spokes[i].set_points_as_corners([P3(J[i]), P3(J[i + 1])])
                spokes[i].set_stroke(WHITE_ if i == 0 else col, 2.2 if i == 0 else 1.8,
                                     a[i] * vr * (0.6 if i == 0 else 0.85))
            tip = P3(J[-1])
            dot.move_to(tip)
            for k in range(len(dot) - 1):
                dot[k].set_fill(col, dbase[k] * vr)
            dot[-1].set_fill(WHITE_, vr)
            # ---- rolled-out trace
            vt = g("vTrace")
            if vt > 0.01 and cx - X0R > 0.02:
                trace.set_points_as_corners([[X0R, YB, 0], [cx, YB, 0]])
                trace.set_stroke(GOLD, 4.5, vt)
                trace.set_stroke(GOLD, 14.0, 0.18 * vt, background=True)
            else:
                trace.set_stroke(GOLD, 4.5, 0.0)
                trace.set_stroke(GOLD, 14.0, 0.0, background=True)
            # ---- the curve
            vc, x0, sig, alpha, cyc, Lx = g("vCurve"), g("x0"), g("sig"), g("alpha"), g("cyc"), g("Lx")
            tapv = g("tap")
            L = Lx / sig
            if vc > 0.002 and Lx > 0.05:
                N = 360
                s = np.linspace(0, L, N)
                f = field(s, th, a, R, alpha, x0, sig, Lx, tapv)
                xx, yy = x0 + sig * s, cyc + f
                pts = np.column_stack([xx, yy, np.zeros(N)])
                curve.set_points_as_corners(pts)
                curve.set_stroke(col, 4.0, vc)
                curve.set_stroke(col, 12.8, 0.18 * vc, background=True)
                vem = g("vEM")
                if vem > 0.002:
                    bp = np.column_stack([xx + EMD[0] * f, cyc + EMD[1] * f, np.zeros(N)])
                    bcurve.set_points_as_corners(bp)
                    bcurve.set_stroke(B_COL, 4.0, vem * vc)
                    bcurve.set_stroke(B_COL, 12.8, 0.18 * vem * vc, background=True)
                    ii = np.linspace(2, N - 3, 30).astype(int)
                    base = np.column_stack([xx[ii], np.full(len(ii), cyc), np.zeros(len(ii))])
                    set_segs(estems, base, np.column_stack([xx[ii], yy[ii], np.zeros(len(ii))]))
                    set_segs(bstems, base, np.column_stack([xx[ii] + EMD[0] * f[ii], cyc + EMD[1] * f[ii],
                                                            np.zeros(len(ii))]))
                    estems.set_stroke(col, 1.6, 0.32 * vem * vc)
                    bstems.set_stroke(B_COL, 1.6, 0.32 * vem * vc)
                else:
                    for m in (bcurve, estems, bstems):
                        m.set_stroke(opacity=0.0)
                        m.set_stroke(opacity=0.0, background=True)
                # ---- samples (magenta bars)
                vs = g("vStems")
                if vs > 0.002:
                    sj = L * (np.arange(NSMP) + 0.5) / NSMP
                    fj = field(sj, th, a, R, alpha, x0, sig, Lx, 0.0)
                    k = int(min(NSMP, vs * NSMP + 0.001))
                    if k > 0:
                        xj = x0 + sig * sj[:k]
                        set_segs(samples, np.column_stack([xj, np.full(k, cyc), np.zeros(k)]),
                                 np.column_stack([xj, cyc + fj[:k], np.zeros(k)]))
                        samples.set_stroke(col, 5.5, 0.95)
                    else:
                        samples.set_stroke(col, 5.5, 0.0)
                else:
                    samples.set_stroke(col, 5.5, 0.0)
                # ---- reconstruction from the `keep` tallest rotations
                vrc = g("vRecon")
                if vrc > 0.002:
                    ar = np.clip(g("keep") - IDX, 0, 1)
                    fr = field(s, th, ar, R, alpha, x0, sig, Lx, 0.0)
                    recon.set_points_as_corners(np.column_stack([xx, cyc + fr, np.zeros(N)]))
                    recon.set_stroke(WHITE_, 2.8, 0.95 * vrc)
                    recon.set_stroke(WHITE_, 8.0, 0.16 * vrc, background=True)
                else:
                    recon.set_stroke(opacity=0.0)
                    recon.set_stroke(opacity=0.0, background=True)
            else:
                for m in (curve, bcurve, estems, bstems, samples, recon):
                    m.set_stroke(opacity=0.0)
                    m.set_stroke(opacity=0.0, background=True)
            # ---- connector (dot -> start of the curve) and axis
            vcn = g("vConn")
            if vcn > 0.01:
                p0 = np.array([tip[0], tip[1], 0.0])
                p1 = np.array([x0, tip[1] - cy + cyc, 0.0])
                tt = np.linspace(0, 1, 16)[:-1]
                set_segs(conn, p0 + (p1 - p0) * tt[:, None], p0 + (p1 - p0) * (tt + 0.55 / 15)[:, None])
                conn.set_stroke(col, 2.0, 0.7 * vcn)
            else:
                conn.set_stroke(col, 2.0, 0.0)
            vax = g("vAxis")
            xs_ = cx * vr + (x0 - 0.2) * (1 - vr)
            axis.set_points_as_corners([[xs_, cyc, 0], [x0 + Lx + 0.25, cyc, 0]])
            axis.set_stroke(DIM, 1.6, 0.8 * vax)

        driver = VMobject()
        driver.add_updater(drive)
        self.driver = driver
        self.add(driver)
        order = [axis, trace, conn, estems, bstems, samples, bcurve, curve, recon, *arms, *spokes, circ, dot]
        self.rig_mobs = [driver] + order
        for m in order:
            live(m)
            self.add(m)
        for m in (axis, trace, conn, estems, bstems, samples, bcurve, curve, recon):
            m.set_stroke(opacity=0.0)
        self.dotm, self.circm = dot, circ

    def dot_pos(self):
        g = lambda k: self.tr[k].get_value()
        th, cx, cy, R = g("th"), g("cx"), g("cy"), g("R")
        u = np.array([np.cos(th), np.sin(th), 0.0])
        return np.array([cx, cy, 0.0]) + R * u, u

    # ================================================================ construct
    def construct(self):
        self.build_rig()
        self.beat_A()
        self.mark("A done")
        self.beat_B()
        self.mark("B done")
        self.beat_C()
        self.mark("C done")
        self.beat_D()
        self.mark("D done")
        self.beat_E()
        self.mark("E done")
        self.fade_all(0.7)
        self.pad_to()

    # ================================================================ A  0 - 5
    def beat_A(self):
        tr = self.tr
        self.tag("01", "ROTATION", WHITE_, start=0.2, dur=3.6)
        self.badge("MATHEMATICS", GOLD, start=0.2, dur=6.15)
        self.level(0, GOLD, start=0.2, dur=5.0)
        self.cap("Spin a point around a circle, and a wave appears.", 1.5, 5.0)

        base = Line([X0R - 0.9, YB, 0], [1.2, YB, 0]).set_stroke(DIM, width=2, opacity=0.8)
        yb2 = -0.8
        bars, dlabs = VGroup(), VGroup()
        for i in range(3):
            b = Line([X0R + 1.6 * i + 0.03, yb2, 0], [X0R + 1.6 * (i + 1) - 0.03, yb2, 0])
            neon(b, GOLD if i % 2 == 0 else "#FFE08A", 4.5)
            bars.add(b)
            dlabs.add(MathTex("d", color=GOLD).scale(0.6).move_to([X0R + 1.6 * i + 0.8, yb2 - 0.4, 0]))
        x_end = X0R + TAU * RR
        sliver = Line([X0R + 4.8 + 0.03, yb2, 0], [x_end, yb2, 0])
        neon(sliver, WHITE_, 6.0)
        eq = MathTex(r"\pi=", "3", ".", "1", "4", "1", "5", "9", r"\ldots").scale(1.3)
        eq.move_to([3.4, yb2, 0])
        eq[0].set_color(GOLD)
        for m in eq[1:]:
            m.set_color(WHITE_)
        eq_parts = eq[1:]

        def roll(_m, a):
            tr["vTrace"].set_value(1.0)
            tr["cx"].set_value(X0R + RR * TAU * a)
            tr["th"].set_value(-PI / 2 - TAU * a)

        def to_curve():
            tr["x0"].set_value(B_X0); tr["sig"].set_value(1.0); tr["alpha"].set_value(1.0)
            tr["hue"].set_value(0.0); tr["Lx"].set_value(0.0); tr["vCurve"].set_value(1.0)
            tr["tap"].set_value(1.0)

        gone = [base, bars, dlabs, sliver, eq]
        ev = [
            (0.0, FadeIn(base, run_time=0.4)),
            (0.0, tw(tr["vRig"], 1.0, 0.4)),
            (0.4, UpdateFromAlphaFunc(Mobject(), roll, run_time=1.2, rate_func=smooth)),
            (1.6, LaggedStart(*[Create(b) for b in bars], lag_ratio=0.35, run_time=0.7)),
            (1.6, LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in dlabs], lag_ratio=0.35, run_time=0.7)),
            (2.3, Create(sliver, run_time=0.25)),
            (2.3, Flash(sliver.get_center(), color=WHITE_, flash_radius=0.3, line_length=0.15, run_time=0.4)),
            (2.55, FadeIn(eq[0], run_time=0.2)),
            (2.7, LaggedStart(*[FadeIn(d, shift=UP * 0.15) for d in eq_parts], lag_ratio=0.16, run_time=0.75)),
            # hand the circle over to the wave picture
            (3.5, Do(to_curve)),
            (3.5, AnimationGroup(*[FadeOut(m, run_time=0.4) for m in gone])),
            (3.5, tw(tr["vTrace"], 0.0, 0.4)),
            (3.5, tw(tr["cx"], B_CX, 0.9)), (3.5, tw(tr["cy"], B_CY, 0.9)), (3.5, tw(tr["R"], B_R, 0.9)),
            (3.5, tw(tr["cyc"], B_CY, 0.9)),
            (3.5, tw(tr["spin"], 1.0, 0.7)),
            (3.9, tw(tr["vAxis"], 1.0, 0.5)),
            (4.1, tw(tr["vConn"], 1.0, 0.5)),
            (4.3, tw(tr["Lx"], 2.1, 0.7, linear)),
        ]
        self.timeline(5.0, ev)

    # ================================================================ B  5 - 10
    def beat_B(self):
        tr = self.tr
        self.level(1, GOLD, start=0.0, dur=1.6)
        self.level(1, CYAN, start=1.4, dur=4.0)
        self.cap("Nature is full of waves: water, sound, light.", 5.4, 10.0)
        self.badge("PHYSICS", CYAN, start=6.4 - self.now(), dur=3.9)

        self.wt = ValueTracker(0.0)
        self.wop = ValueTracker(0.0)
        wt, wop, th = self.wt, self.wop, tr["th"]

        def dsep():
            return 1.0 + 0.9 * float(sm((wt.get_value() - 1.0) / 1.6))

        img = ImageMobject(wave_frame(0.01, 0.0, 1.0, 0.0))
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        img.set(width=UW).move_to(IMG_C)
        img.set_z_index(-5)

        def img_upd(m):
            op = wop.get_value()
            if op > 0.003:
                m.pixel_array = wave_frame(CSPD * wt.get_value(), th.get_value(), dsep(), op)
        img.add_updater(img_upd)
        self.img = img

        def src_pos(sgn):
            return IMG_C + np.array([SRC_X, sgn * dsep() / 2, 0])
        s1 = glow_dot(src_pos(1), CYAN, r=0.06).add_updater(lambda m: m.move_to(src_pos(1)))
        s2 = glow_dot(src_pos(-1), CYAN, r=0.06).add_updater(lambda m: m.move_to(src_pos(-1)))
        self.srcs = [s1, s2]

        def add_img():
            self.add(img)

        ev = [
            (5.0, tw(tr["Lx"], 6.3, 1.4, linear)),
            (6.0, tw(tr["hue"], 1.0, 0.7)),                       # gold -> cyan
            (6.4, tw(tr["vRig"], 0.0, 0.5)),
            (6.4, tw(tr["vConn"], 0.0, 0.4)),
            (6.4, tw(tr["vAxis"], 0.0, 0.5)),
            # the curve compresses into a ripple cross-section
            (6.5, tw(tr["x0"], SRC_X, 0.9)),
            (6.5, tw(tr["sig"], WAVELEN / (TAU * KAPPA), 0.9)),
            (6.5, tw(tr["alpha"], 0.24, 0.9)),
            (6.5, tw(tr["cyc"], IMG_C[1], 0.9)),
            (6.5, tw(tr["Lx"], 8.4, 0.9)),
            (6.5, tw(tr["spin"], 1.0 * 6.05, 0.9)),
            # ... and the same wave spreads over a water surface
            (7.1, Do(add_img)),
            (7.1, tw(wop, 1.0, 0.6)),
            (7.1, tw(wt, 2.9, 2.9, linear)),
            (7.1, FadeIn(s1, run_time=0.5)), (7.1, FadeIn(s2, run_time=0.5)),
            (7.7, tw(tr["vCurve"], 0.0, 0.7)),
        ]
        self.timeline(10.0, ev)

    # ================================================================ C  10 - 15
    def beat_C(self):
        tr = self.tr
        self.badge("PHYSICS", CYAN, start=0.0, dur=5.1)
        self.level(2, CYAN, start=0.0, dur=5.3)
        self.cap("Electric and magnetic fields chase each other. That is light.", 10.4, 15.0)
        wt, wop, th = self.wt, self.wop, tr["th"]

        eqs = [r"\nabla\cdot\mathbf{E}=\frac{\rho}{\varepsilon_0}",
               r"\nabla\cdot\mathbf{B}=0",
               r"\nabla\times\mathbf{E}=-\frac{\partial\mathbf{B}}{\partial t}",
               r"\nabla\times\mathbf{B}=\mu_0\mathbf{J}+\mu_0\varepsilon_0\frac{\partial\mathbf{E}}{\partial t}"]
        maxw = VGroup(*[MathTex(e, color=CYAN) for e in eqs]).scale(0.85)
        maxw.arrange_in_grid(2, 2, buff=(0.9, 0.9), col_alignments="cc")
        maxw.move_to([1.3, 1.2, 0])
        maxw.set_opacity(0.13)

        legend = VGroup(
            VGroup(MathTex(r"\mathbf{E}", color=CYAN).scale(0.8),
                   Text("electric", font=FONT, font_size=20, color=CYAN)).arrange(RIGHT, buff=0.2),
            VGroup(MathTex(r"\mathbf{B}", color=B_COL).scale(0.8),
                   Text("magnetic", font=FONT, font_size=20, color=B_COL)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([5.5, 1.85, 0])

        def make_label(tex):
            m = MathTex(tex, color=WHITE_).scale(0.85)

            def upd(mm):
                p, u = self.dot_pos()
                mm.move_to(p + u * 0.62)
            m.add_updater(upd)
            upd(m)
            return m
        lab_t = make_label(r"e^{i\theta}")
        lab_p = make_label(r"e^{i\pi}")
        self.lab_p = lab_p

        eq = MathTex(r"e^{i\pi}", r"+", r"1", r"=", r"0").scale(1.7)
        eq.move_to([1.3, 1.95, 0])
        eq[0].set_color(CYAN)
        eq[1:].set_color(WHITE_)
        self.eq = eq
        eq_glow = eq.copy().set_stroke(CYAN, width=9, opacity=0.5).set_fill(CYAN, opacity=0.3)
        self.maxw, self.legend, self.lab_t = maxw, legend, lab_t

        def setup_C():
            self.remove(self.img)
            self.wop.set_value(0.0)
            tr["spin"].set_value(0.0); tr["th"].set_value(0.0)
            tr["cx"].set_value(C_CX); tr["cy"].set_value(C_CY); tr["R"].set_value(C_R)
            tr["cyc"].set_value(C_CY); tr["x0"].set_value(C_X0); tr["sig"].set_value(1.0)
            tr["alpha"].set_value(1.0); tr["hue"].set_value(1.0); tr["nact"].set_value(1.0)
            tr["Lx"].set_value(0.0); tr["vCurve"].set_value(1.0); tr["vEM"].set_value(0.0)
            tr["tap"].set_value(1.0)

        ev = [
            (10.0, tw(wt, 3.6, 0.7, linear)),
            (10.0, tw(wop, 0.0, 0.6)),
            (10.0, FadeOut(self.srcs[0], run_time=0.5)), (10.0, FadeOut(self.srcs[1], run_time=0.5)),
            (10.2, FadeIn(maxw, run_time=0.6)),
            (10.7, Do(setup_C)),
            (10.75, tw(tr["vRig"], 1.0, 0.5)),
            (10.75, tw(tr["vAxis"], 1.0, 0.5)),
            (10.75, tw(th, 3 * PI, 2.45, trap(0.22, 0.3))),
            (10.9, tw(tr["Lx"], 9.5, 1.3)),
            (10.9, tw(tr["vEM"], 1.0, 0.7)),
            (10.9, tw(tr["vConn"], 1.0, 0.5)),
            (11.1, FadeIn(legend, run_time=0.4)),
            (11.4, FadeIn(lab_t, run_time=0.3)),
            # arrives at theta = pi
            (13.2, FadeOut(lab_t, run_time=0.25)),
            (13.3, FadeIn(lab_p, run_time=0.25)),
            (13.3, Flash(np.array([C_CX - C_R, C_CY, 0.0]), color=CYAN, flash_radius=0.45,
                         line_length=0.18, run_time=0.45)),
            (13.4, FadeOut(maxw, run_time=0.5)),
            (13.4, tw(tr["vEM"], 0.25, 0.6)),
            (13.4, FadeOut(legend, run_time=0.4)),
            (13.5, tw(tr["vCurve"], 0.55, 0.6)),
            (13.7, FadeIn(eq, shift=UP * 0.2, run_time=0.6)),
            (14.3, FadeIn(eq_glow, scale=1.03, run_time=0.25)),
            (14.55, FadeOut(eq_glow, scale=1.12, run_time=0.4)),
        ]
        self.timeline(15.0, ev)

    # ================================================================ D  15 - 21
    def beat_D(self):
        tr = self.tr
        th = tr["th"]
        self.level(2, GOLD, start=0.0, dur=3.0)
        self.level(2, MAGENTA, start=2.6, dur=3.7)
        self.badge("MATHEMATICS", GOLD, start=0.15, dur=2.55)
        self.badge("COMPUTER SCIENCE", MAGENTA, start=2.75, dur=3.5)
        self.cap("Any signal is a sum of rotations. That is how we compress sound and images.", 15.3, 21.0)

        # ---- spectrum of the sampled square wave
        SPX0, SPDX, SPBASE, SPH = 1.0, 0.33, -0.3, 1.5
        specT = ValueTracker(0.0)
        barvis = ValueTracker(1.0)
        self.barvis = barvis
        keep = tr["keep"]
        bars = []
        for i in range(NH):
            b = VMobject()
            b.set_fill(MAGENTA, 0.9)
            b.set_stroke(MAGENTA, 0)
            hi = SPH / NS[i]

            def upd(m, i=i, hi=hi):
                grow = float(sm((specT.get_value() * (NH + 4) - i) / 4.0))
                h = max(hi * grow, 1e-3)
                x = SPX0 + SPDX * i
                w = 0.2
                m.set_points_as_corners([[x - w / 2, SPBASE, 0], [x + w / 2, SPBASE, 0],
                                         [x + w / 2, SPBASE + h, 0], [x - w / 2, SPBASE + h, 0],
                                         [x - w / 2, SPBASE, 0]])
                k = float(np.clip(keep.get_value() - i, 0, 1))
                m.set_fill(MAGENTA, (0.15 + 0.75 * k) * (1.0 if grow > 0.01 else 0.0) * barvis.get_value())
            b.add_updater(upd)
            upd(b)
            bars.append(b)
        spec_base = Line([SPX0 - 0.3, SPBASE, 0], [SPX0 + SPDX * (NH - 1) + 0.3, SPBASE, 0]).set_stroke(DIM, 1.6, 0.8)
        lab_s = Text("samples", font=FONT, font_size=20, color=MAGENTA).move_to([-3.6, -0.75, 0])
        lab_f = Text("spectrum: how strong is each rotation", font=FONT, font_size=20, color=DIM
                     ).move_to([3.65, -0.75, 0])
        c3 = Text("keep 3 rotations: a rough copy", font=FONT, font_size=28, color=WHITE_,
                  t2c={"3": MAGENTA}).move_to([0, -1.55, 0])
        c8 = Text("keep 8 rotations: almost the same", font=FONT, font_size=28, color=WHITE_,
                  t2c={"8": MAGENTA}).move_to([0, -1.55, 0])
        self.add(*bars)
        self.d_objs = [spec_base, lab_s, lab_f]
        self.c3, self.c8 = c3, c8

        def to_gold_stage():
            tr["nact"].set_value(1.0)

        ev = [
            # C -> D hand-off: the cyan E-field circle turns gold and becomes the first epicycle
            (15.0, FadeOut(self.eq, run_time=0.4)),
            (15.0, FadeOut(self.lab_p, run_time=0.3)),
            (15.0, tw(tr["hue"], 2.0, 0.6)),
            (15.0, tw(tr["R"], D_R, 0.6)),
            (15.0, tw(tr["x0"], D_X0, 0.6)),
            (15.0, tw(tr["Lx"], 8.5, 0.6)),
            (15.0, tw(tr["vEM"], 0.0, 0.5)),
            (15.0, tw(tr["vCurve"], 1.0, 0.5)),
            (15.0, tw(th, 5 * PI, 2.4, trap(0.25, 0.3))),
            # more and more rotations -> square wave
            (15.4, tw(tr["nact"], 8.0, 2.0, linear)),
            # gold -> magenta: the wave is sampled
            (17.4, tw(tr["nact"], 16.0, 0.6)),
            (17.5, tw(tr["hue"], 3.0, 0.6)),
            (17.5, tw(tr["vRig"], 0.0, 0.5)),
            (17.5, tw(tr["vConn"], 0.0, 0.3)),
            (17.9, tw(tr["x0"], -6.3, 0.7)),
            (17.9, tw(tr["sig"], 5.4 / (TAU * KAPPA), 0.7)),
            (17.9, tw(tr["Lx"], 5.4, 0.7)),
            (17.9, tw(tr["alpha"], 0.72, 0.7)),
            (17.9, tw(tr["cyc"], 0.5, 0.7)),
            (17.9, tw(tr["tap"], 0.0, 0.6)),
            (18.2, tw(tr["vStems"], 1.0, 0.6, linear)),
            (18.2, FadeIn(lab_s, run_time=0.4)),
            (18.7, tw(tr["vCurve"], 0.35, 0.4)),
            # the spectrum: a handful of tall bars
            (18.5, FadeIn(spec_base, run_time=0.3)),
            (18.5, tw(specT, 1.0, 0.8, linear)),
            (18.6, FadeIn(lab_f, run_time=0.4)),
            # keep only the tallest rotations
            (19.3, Do(lambda: tr["keep"].set_value(16.0))),
            (19.3, tw(tr["vRecon"], 1.0, 0.3)),
            (19.35, tw(keep, 3.0, 0.5)),
            (19.6, FadeIn(c3, run_time=0.3)),
            (20.2, FadeOut(c3, run_time=0.25)),
            (20.25, tw(keep, 8.0, 0.5)),
            (20.35, FadeIn(c8, run_time=0.3)),
        ]
        self.timeline(21.0, ev)

    # ================================================================ E  21 - 25
    def beat_E(self):
        tr = self.tr
        # ---- frontier badge (three colours)
        bg = VGroup(*[Text(t, font=FONT, font_size=18, color=c, weight=BOLD)
                      for t, c in (("MATHEMATICS", GOLD), ("PHYSICS", CYAN), ("COMPUTER SCIENCE", MAGENTA))])
        bg.arrange(RIGHT, buff=0.22).to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        self._timed(bg, 0.0, 3.8, fade=0.35, max_op=0.95)
        self.level(3, WHITE_, start=0.0, dur=3.9)
        self.cap("At the frontier, the same idea links primes, geometry and symmetry.", 21.1, 24.6)

        # ---- zeta zeros
        SX, SW, Y0, SC = -3.6, 1.5, -2.0, 0.085
        H = 52.5 * SC
        strip = Rectangle(width=SW, height=H + 0.3, stroke_width=0).set_fill(GOLD, 0.06)
        strip.move_to([SX, Y0 + (H + 0.3) / 2 - 0.15, 0])
        edges = VGroup(*[Line([SX + dx, Y0, 0], [SX + dx, Y0 + H + 0.1, 0], stroke_width=1.4,
                              stroke_color=GOLD, stroke_opacity=0.4) for dx in (-SW / 2, SW / 2)])
        zbase = Line([SX - SW / 2 - 0.2, Y0, 0], [SX + SW / 2 + 0.2, Y0, 0], stroke_width=1.4, stroke_color=DIM)
        crit = neon(DashedLine([SX, Y0, 0], [SX, Y0 + H + 0.1, 0], dash_length=0.12), GOLD, 2.4)
        crit_lab = MathTex(r"\mathrm{Re}(s)=\tfrac12", color=GOLD).scale(0.62).move_to([SX, 2.72, 0])
        zero_dots = VGroup(*[glow_dot([SX, Y0 + g * SC, 0], GOLD, r=0.065, layers=4) for g in ZEROS])
        WX0, WX1, WY = -0.8, 6.0, 0.15
        wave_axis = Line([WX0, WY, 0], [WX1, WY, 0], stroke_width=1.2, stroke_color=DIM, stroke_opacity=0.7)
        wave_lab = MathTex(r"\sum_{\gamma}\cos(\gamma\, u)", color=CYAN).scale(0.7).move_to([2.6, 1.75, 0])
        n_tr = ValueTracker(0.0)
        wvis = ValueTracker(1.0)
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
            m.set_points_as_corners(np.column_stack([xs, WY + 1.0 * y, np.zeros_like(xs)]))
            m.set_stroke([CYAN, MAGENTA], 3.4, wvis.get_value())
        wave_upd(wave)
        wave.add_updater(wave_upd)
        self.add(wave)
        z_static = VGroup(strip, edges, zbase, crit, crit_lab, wave_axis, wave_lab)

        # ---- Langlands islands
        ea, eb = 1.5, 0.95
        cN, cG, cS = np.array([-4.3, -0.5, 0]), np.array([0.0, 1.3, 0]), np.array([4.3, -0.5, 0])

        def island(c, col, name):
            ring = Ellipse(width=2 * ea, height=2 * eb).move_to(c)
            neon(ring, col, 2.2)
            ring.set_fill("#0A1020", 0.9)
            nm = Text(name, font=FONT, font_size=24, color=col, weight=BOLD).move_to(c + DOWN * 1.35)
            return ring, nm
        rN, nN = island(cN, GOLD, "NUMBERS")
        rG, nG = island(cG, CYAN, "GEOMETRY")
        rS, nS = island(cS, MAGENTA, "SYMMETRY")
        primes = [(-0.95, 0.3, "2"), (-0.4, 0.58, "3"), (0.25, 0.5, "5"), (0.9, 0.25, "7"),
                  (-0.8, -0.32, "11"), (-0.15, -0.02, "13"), (0.5, -0.22, "17"),
                  (-0.1, -0.6, "19"), (0.95, -0.5, "23")]
        numbers = VGroup(*[Text(s, font=MONO, font_size=20, color=GOLD).move_to(cN + np.array([x, y, 0]))
                           for x, y, s in primes])
        sc_, cx_ = 0.55, 0.25
        f3 = lambda x: x ** 3 - x
        u_ = np.linspace(0, np.pi, 40)
        ox = -0.5 - 0.5 * np.cos(u_)
        oy = np.sqrt(np.maximum(f3(ox), 0))
        oval = [(x, y) for x, y in zip(ox, oy)] + [(x, -y) for x, y in zip(ox[::-1], oy[::-1])]
        w_ = np.linspace(0, 1, 30)
        bx = 1 + 0.5 * w_ ** 2
        by = np.sqrt(np.maximum(f3(bx), 0))
        branch = [(x, -y) for x, y in zip(bx[::-1], by[::-1])] + [(x, y) for x, y in zip(bx, by)]
        curve_g = VGroup()
        for pts in (oval, branch):
            m = VMobject().set_points_smoothly([cG + np.array([(x - cx_) * sc_, y * sc_, 0]) for x, y in pts])
            neon(m, CYAN, 3.0)
            curve_g.add(m)
        hexr = 0.7
        hv = [cS + hexr * np.array([np.cos(np.pi / 6 + k * np.pi / 3), np.sin(np.pi / 6 + k * np.pi / 3), 0])
              for k in range(6)]
        hexa = neon(Polygon(*hv), MAGENTA, 3.0)
        diag = VGroup(*[Line(hv[k], hv[k + 3]).set_stroke(MAGENTA, 1.6, 0.7) for k in range(3)])
        sym = VGroup(diag, hexa)

        def edge_pt(c, tgt):
            v = tgt - c
            v = v / np.hypot(v[0] / ea, v[1] / eb)
            return c + v
        cen3 = (cN + cG + cS) / 3

        def bridge(c1, c2, col1, col2):
            p1, p2 = edge_pt(c1, c2), edge_pt(c2, c1)
            best = None
            for ang_ in (0.55, -0.55):
                arc = ArcBetweenPoints(p1, p2, angle=ang_)
                d = np.linalg.norm(arc.point_from_proportion(0.5) - cen3)
                if best is None or d > best[0]:
                    best = (d, arc)
            arc = best[1]
            neon(arc, col1, 3.4)
            arc.set_stroke([col1, col2], 3.4)
            arc.set_stroke([col1, col2], 11.0, 0.18, background=True)
            return arc
        b1 = bridge(cN, cG, GOLD, CYAN)
        b2 = bridge(cG, cS, CYAN, MAGENTA)
        b3 = bridge(cS, cN, MAGENTA, GOLD)
        islands = VGroup(rN, rG, rS, nN, nG, nS, numbers, curve_g, sym)
        rigmobs = self.rig_mobs

        def kill_rig():
            self.driver.clear_updaters()
            self.remove(*rigmobs)

        d_fade = [FadeOut(m, run_time=0.4) for m in self.d_objs]
        ev = [
            (21.0, AnimationGroup(*d_fade)),
            (21.0, tw(self.barvis, 0.0, 0.4)),
            (21.0, FadeOut(self.c8, run_time=0.3)),
            (21.0, tw(tr["vCurve"], 0.0, 0.4)),
            (21.0, tw(tr["vStems"], 0.0, 0.4)),
            (21.0, tw(tr["vRecon"], 0.0, 0.4)),
            (21.0, tw(tr["vAxis"], 0.0, 0.4)),
            (21.45, Do(kill_rig)),
            (21.05, FadeIn(z_static, run_time=0.5)),
            (21.5, LaggedStart(*[FadeIn(d, scale=0.2) for d in zero_dots], lag_ratio=0.25, run_time=1.0)),
            (21.5, tw(n_tr, float(len(gam)), 1.0, linear)),
            (22.75, AnimationGroup(FadeOut(z_static, run_time=0.3), FadeOut(zero_dots, run_time=0.3),
                                   tw(wvis, 0.0, 0.3))),
            (23.0, FadeIn(islands, run_time=0.4)),
            (23.4, LaggedStart(Create(b1), Create(b2), Create(b3), lag_ratio=0.3, run_time=0.75)),
            (23.75, LaggedStart(*[ShowPassingFlash(a.copy().set_stroke(WHITE_, 6, 1.0), time_width=0.7)
                                 for a in (b1, b2, b3)], lag_ratio=0.2, run_time=0.5)),
        ]
        self.timeline(24.3, ev)
