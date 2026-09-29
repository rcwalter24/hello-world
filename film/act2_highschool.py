from style import *
from manim.utils.rate_functions import ease_out_back


def _sm(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- physics field
IW, IH = 576, 288            # image pixels
UW, UH = 9.6, 4.8            # image size in scene units
IMG_C = np.array([0.0, 0.2, 0.0])
SRC_X = -3.7                 # sources' x (image coords)
WAVELEN = 0.5
KW = 2 * np.pi / WAVELEN
CSPD = 2.6                   # wave speed (units / s)
OMEGA = KW * CSPD

_xs = (np.arange(IW) + 0.5) / IW * UW - UW / 2
_ys = UH / 2 - (np.arange(IH) + 0.5) / IH * UH
_X, _Y = np.meshgrid(_xs, _ys)
_WIN = _sm((UW / 2 - np.abs(_X)) / 0.9) * _sm((UH / 2 - np.abs(_Y)) / 0.7)
_BGC = np.array([7, 10, 20], float)
_CY = np.array([76, 201, 240], float)
_DEEP = np.array([16, 44, 110], float)


def wave_frame(t, d, op):
    """RGBA uint8 image of two ring-wave sources separated by d, at time t."""
    r1 = np.hypot(_X - SRC_X, _Y - d / 2)
    r2 = np.hypot(_X - SRC_X, _Y + d / 2)
    front = CSPD * t

    def w(r):
        return np.cos(KW * r - OMEGA * t) / np.sqrt(1 + 0.4 * r) * _sm((front - r) / 0.5)

    v = np.clip((w(r1) + w(r2)) / 1.5, -1, 1)
    crest = np.clip(v, 0, 1)
    trough = np.clip(-v, 0, 1)
    col = (_BGC + (_CY - _BGC) * (crest ** 1.5)[..., None]
           + (_DEEP - _BGC) * (0.55 * trough)[..., None])
    hi = np.clip((crest - 0.8) / 0.2, 0, 1) ** 2
    col = col + (255 - col) * (0.55 * hi)[..., None]
    col = _BGC + (col - _BGC) * (_WIN * op)[..., None]
    out = np.empty((IH, IW, 4), np.uint8)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = 255
    return out


class Act2(FilmScene):
    DURATION = BUDGET["act2"]

    # =============================================================== MATH 1
    def math_circle(self):
        cx, cy, R = -4.4, 0.55, 1.25
        x0, K = -2.5, 0.8
        th = ValueTracker(0.0)

        def P():
            t = th.get_value()
            return np.array([cx + R * np.cos(t), cy + R * np.sin(t), 0])

        def Q():
            t = th.get_value()
            return np.array([x0 + K * t, cy + R * np.sin(t), 0])

        circle = neon(Circle(radius=R).move_to([cx, cy, 0]), GOLD, 3.0)
        h_axis = Line([cx - R - 0.35, cy, 0], [x0 + K * 3 * PI + 0.25, cy, 0],
                      stroke_color=DIM, stroke_width=2)
        v_axis = Line([x0, cy - R - 0.3, 0], [x0, cy + R + 0.3, 0],
                      stroke_color=DIM, stroke_width=2)
        c_axis = Line([cx, cy - R - 0.2, 0], [cx, cy + R + 0.2, 0],
                      stroke_color=DIM, stroke_width=1.5)

        def curve():
            t = max(th.get_value(), 1e-3)
            n = max(3, int(t * 28))
            a = np.linspace(0, t, n)
            pts = np.stack([x0 + K * a, cy + R * np.sin(a), np.zeros(n)], 1)
            m = VMobject()
            m.set_points_as_corners(pts)
            return neon(m, GOLD, 4.0)

        trace = always_redraw(curve)
        radius = always_redraw(lambda: Line([cx, cy, 0], P(), color=WHITE_, stroke_width=2))
        sin_seg = always_redraw(lambda: Line([P()[0], cy, 0], P(), color=GOLD, stroke_width=5))
        cos_seg = always_redraw(lambda: Line([cx, cy, 0], [P()[0], cy, 0], color=WHITE_, stroke_width=5))
        conn = always_redraw(lambda: DashedLine(P(), Q(), color=GOLD, stroke_width=2.5,
                                                dash_length=0.07).set_stroke(opacity=0.85))
        dotP = glow_dot(P(), GOLD).add_updater(lambda m: m.move_to(P()))
        dotQ = glow_dot(Q(), GOLD).add_updater(lambda m: m.move_to(Q()))
        cos_dot = Dot(radius=0.06, color=WHITE_).add_updater(
            lambda m: m.move_to([P()[0], cy, 0]))
        sin_lab = MathTex(r"\sin\theta", color=GOLD).scale(0.95).move_to([x0 + K * PI / 2 + 0.1, cy + R + 0.5, 0])
        cos_lab = MathTex(r"\cos\theta", color=WHITE_).scale(0.95).move_to([cx, cy - R - 0.5, 0])

        static = [circle, h_axis, v_axis, c_axis, sin_lab, cos_lab]
        live = [trace, radius, sin_seg, cos_seg, conn, dotP, dotQ, cos_dot]
        self.play(*[FadeIn(m) for m in static + live], run_time=0.6)              # +0.6
        self.play(th.animate.set_value(3 * PI), run_time=4.4, rate_func=linear)   # +4.4
        for m in live:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in static + live], run_time=0.5)             # +0.5 = 5.5

    # =============================================================== MATH 2
    def math_tangent(self):
        cfg = dict(axis_config={"color": DIM, "stroke_width": 2,
                                "include_ticks": False, "include_tip": False})
        axL = Axes(x_range=[-2.2, 2.2, 1], y_range=[0, 5, 1], x_length=5.4, y_length=4.0, **cfg)
        axL.move_to([-3.6, 0.6, 0])
        axR = Axes(x_range=[-2.2, 2.2, 1], y_range=[-5, 5, 1], x_length=5.4, y_length=4.0, **cfg)
        axR.move_to([3.6, 0.6, 0])
        parab = neon(axL.plot(lambda x: x * x, x_range=[-2.1, 2.1]), GOLD, 4.0)
        labL = MathTex(r"y=x^2", color=GOLD).scale(0.95).move_to(axL.c2p(0.0, 3.3))
        labR = MathTex(r"y'=2x", color=GOLD).scale(0.95).move_to(axR.c2p(-1.45, 4.0))

        a = ValueTracker(-1.6)
        A = a.get_value
        hw, hr = 0.65, 0.6

        tan = always_redraw(lambda: neon(Line(
            axL.c2p(A() - hw, A() ** 2 - 2 * A() * hw),
            axL.c2p(A() + hw, A() ** 2 + 2 * A() * hw)), WHITE_, 3.0))
        tri = always_redraw(lambda: Polygon(
            axL.c2p(A(), A() ** 2), axL.c2p(A() + hr, A() ** 2),
            axL.c2p(A() + hr, A() ** 2 + 2 * A() * hr),
            stroke_color=GOLD, stroke_width=2, fill_color=GOLD, fill_opacity=0.3))
        dropL = always_redraw(lambda: DashedLine(axL.c2p(A(), A() ** 2), axL.c2p(A(), 0),
                                                 color=GOLD, stroke_width=2, dash_length=0.07))
        dotL = glow_dot(axL.c2p(A(), A() ** 2), GOLD).add_updater(
            lambda m: m.move_to(axL.c2p(A(), A() ** 2)))

        def rline():
            e = max(A(), -1.595)
            return neon(Line(axR.c2p(-1.6, -3.2), axR.c2p(e, 2 * e)), GOLD, 4.0)

        lineR = always_redraw(rline)
        dropR = always_redraw(lambda: DashedLine(axR.c2p(A(), 0), axR.c2p(A(), 2 * A()),
                                                 color=GOLD, stroke_width=2, dash_length=0.07))
        dotR = glow_dot(axR.c2p(A(), 2 * A()), GOLD).add_updater(
            lambda m: m.move_to(axR.c2p(A(), 2 * A())))

        slope_lab = label("slope", WHITE_, 30).move_to([-4.6, -2.0, 0])
        slope_num = DecimalNumber(2 * A(), num_decimal_places=2, include_sign=True,
                                  font_size=44, color=GOLD)
        slope_num.next_to(slope_lab, RIGHT, buff=0.3)
        slope_num.add_updater(lambda m: (m.set_value(2 * A()), m.next_to(slope_lab, RIGHT, buff=0.3)))

        static = [axL, axR, labL, labR, slope_lab]
        live = [tan, tri, dropL, dotL, lineR, dropR, dotR, slope_num]
        self.play(FadeIn(axL), FadeIn(axR), Create(parab), FadeIn(labL), FadeIn(labR),
                  *[FadeIn(m) for m in live + [slope_lab]], run_time=0.9)                  # +0.9
        self.play(a.animate.set_value(1.6), run_time=3.6, rate_func=smooth)             # +3.6
        for m in live:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in static + live + [parab]], run_time=0.5)           # +0.5 = 5.0

    # =============================================================== PHYSICS
    def physics(self, T=9.5):
        u = ValueTracker(0.0)

        def params():
            x = u.get_value()
            t = x * T
            d = 1.0 + 0.9 * _sm((x - 0.42) / 0.5)
            op = float(_sm(x / 0.05) * (1 - _sm((x - 0.93) / 0.07)))
            return t, d, op

        t0, d0, o0 = params()
        img = ImageMobject(wave_frame(t0 + 0.01, d0, 1.0))
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        img.set(width=UW).move_to(IMG_C)

        def upd(m):
            t, d, op = params()
            m.pixel_array = wave_frame(t, d, op)
        img.add_updater(upd)

        def src_pos(sign):
            _, d, _ = params()
            return IMG_C + np.array([SRC_X, sign * d / 2, 0])

        s1 = glow_dot(src_pos(1), CYAN, r=0.06).add_updater(lambda m: m.move_to(src_pos(1)))
        s2 = glow_dot(src_pos(-1), CYAN, r=0.06).add_updater(lambda m: m.move_to(src_pos(-1)))

        self.add(img)
        self.play(u.animate.set_value(1.0), FadeIn(s1, run_time=0.5), FadeIn(s2, run_time=0.5),
                  AnimationGroup(Wait(T - 0.6),
                                 AnimationGroup(FadeOut(s1, run_time=0.5), FadeOut(s2, run_time=0.5)),
                                 lag_ratio=1),
                  run_time=T, rate_func=linear)                                            # +T
        img.clear_updaters()
        self.remove(img)

    # =============================================================== CS
    def binary_search(self):
        N, target = 64, 42
        pitch = 0.19
        tiles = VGroup(*[Rectangle(width=0.15, height=0.75, stroke_width=0,
                                   fill_color=MAGENTA, fill_opacity=0.8) for _ in range(N)])
        tiles.arrange(RIGHT, buff=pitch - 0.15).move_to([0, 0.9, 0])
        tiles[target].set_stroke(WHITE_, width=1.6, opacity=0.9)
        top = label("64 tiles  (standing in for a million)", DIM, 24).move_to([0, 2.0, 0])

        def box_for(lo, hi):
            l = tiles[lo].get_left()[0] - 0.07
            r = tiles[hi].get_right()[0] + 0.07
            b = Rectangle(width=r - l, height=1.05, stroke_color=MAGENTA, stroke_width=2.5,
                          fill_opacity=0)
            return b.move_to([(l + r) / 2, 0.9, 0])

        def size_lab(lo, hi):
            n = hi - lo + 1
            g = label(f"{n} left", WHITE_, 24)
            return g.move_to([(tiles[lo].get_left()[0] + tiles[hi].get_right()[0]) / 2, 0.15, 0])

        box = box_for(0, N - 1)
        lab = size_lab(0, N - 1)
        marker = glow_dot([tiles[31].get_center()[0], 1.55, 0], WHITE_, r=0.07)

        self.play(FadeIn(tiles), FadeIn(box), FadeIn(lab), FadeIn(top), run_time=0.6)        # +0.6
        self.play(FadeIn(marker), run_time=0.01)
        lo, hi = 0, N - 1
        steps = 0
        while True:
            mid = (lo + hi) // 2
            steps += 1
            self.play(marker.animate.move_to([tiles[mid].get_center()[0], 1.55, 0]),
                      tiles[mid].animate.set_fill(WHITE_, 1.0), run_time=0.2)
            if mid == target:
                break
            if target > mid:
                excl = list(range(lo, mid + 1))
                lo = mid + 1
            else:
                excl = list(range(mid, hi + 1))
                hi = mid - 1
            nb, nl = box_for(lo, hi), size_lab(lo, hi)
            self.play(VGroup(*[tiles[i] for i in excl]).animate.set_fill(MAGENTA, 0.09),
                      Transform(box, nb), ReplacementTransform(lab, nl), run_time=0.34)
            lab = nl
        # found
        nb, nl = box_for(mid, mid), size_lab(mid, mid)
        found = label("found", WHITE_, 24).move_to(nl)
        self.play(Transform(box, nb), ReplacementTransform(lab, found),
                  Flash(tiles[mid], color=MAGENTA, line_length=0.3, flash_radius=0.45),
                  run_time=0.5)
        counter = label("1,000,000 items   →   20 steps", WHITE_, 42,
                        t2c={"1,000,000": MAGENTA, "20": MAGENTA}).move_to([0, -1.2, 0])
        self.play(FadeIn(counter, shift=UP * 0.2), run_time=0.6)
        self.wait(0.3)
        self.play(*[FadeOut(m) for m in (tiles, box, found, marker, top, counter)], run_time=0.4)

    def sierpinski(self):
        s = 5.2
        h = s * np.sqrt(3) / 2
        cy = 0.3
        A = np.array([-s / 2, cy - h / 2, 0.0])
        B = np.array([s / 2, cy - h / 2, 0.0])
        C = np.array([0.0, cy + h / 2, 0.0])
        widths = [3.0, 2.6, 2.2, 1.8, 1.4, 1.1]

        def mk(tri, w):
            p = Polygon(*tri, stroke_color=MAGENTA, stroke_width=w, fill_color=MAGENTA,
                        fill_opacity=0.5)
            p.set_stroke(MAGENTA, width=w * 2.6, opacity=0.14, background=True)
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
        self.play(FadeIn(cur[0], scale=0.8), FadeIn(dl), run_time=0.35)                     # +0.35
        for d in range(1, 6):
            starts = []
            for i, p in enumerate(cur):
                for _ in range(3):
                    starts.append(p.copy())
            self.remove(*cur)
            self.add(*starts)
            new = [mk(t, widths[d]) for t in levels[d]]
            nd = dlab(d)
            self.play(*[Transform(st, nw) for st, nw in zip(starts, new)],
                      Transform(dl, nd), run_time=0.5, rate_func=ease_out_back)             # +0.5
            cur = starts

    # =============================================================== scene
    def construct(self):
        self.tag("02", "HIGH SCHOOL", WHITE_, start=0.3, dur=3.6)
        # ---- MATH (gold): 0 -> 10.5
        self.caption("Then we find waves hiding inside circles.", start=0.9, dur=4.3)
        self.math_circle()                                                                  # 5.5
        self.caption("Change, measured instant by instant.", start=0.9, dur=4.0)
        self.math_tangent()                                                                 # 10.5
        # ---- PHYSICS (cyan): 10.5 -> 20.0
        self.caption("Waves meet, and interfere.", start=1.0, dur=5.0)
        self.physics(9.5)                                                                   # 20.0
        # ---- COMPUTER SCIENCE (magenta): 20.0 -> 29.3
        self.caption("Halve the problem again and again: a million becomes twenty steps.",
                     start=0.3, dur=5.3)
        self.binary_search()
        self.caption("Recursion: a pattern made of itself.", start=0.2, dur=3.6)
        self.sierpinski()
        self.fade_all(0.7)
        self.pad_to()
