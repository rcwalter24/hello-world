from common import *
from fractal import mandel

CH = ("VI", "COMPUTATION", "MPC")


def mandel_rgb(nu):
    stops = ["#0B0E14", "#123447", MATH, "#E6F8FF", PHYS, "#7A3B00", "#0B0E14"]
    v = (np.sqrt(np.maximum(nu, 0)) * 0.11) % 1.0
    rgb = colormap(v, stops)
    rgb[nu < 0] = (5, 7, 10)
    return rgba(rgb)


class S06a_Turing(Base):
    def construct(self):
        self.chapter(CH[0], CH[1], CH[2], "what can be computed — and what cannot?")
        self.turing()
        self.sorting()
        self.clear_all(keep_corner=False)

    def turing(self):
        tape_syms = ["_", "_", "1", "0", "1", "1", "_", "_"]
        cells = VGroup(*[Square(0.9, color=GREY_B, stroke_width=2) for _ in tape_syms])
        cells.arrange(RIGHT, buff=0).shift(DOWN * 0.3)
        syms = VGroup(*[T(s if s != "_" else "", 44, WHITE, MONO_FONT).move_to(c)
                        for s, c in zip(tape_syms, cells)])
        head = Triangle(color=CODE, fill_opacity=1).scale(0.22).rotate(PI)
        state = T("state: carry", 26, CODE, MONO_FONT)
        pos = 5

        def head_at(i):
            return cells[i].get_top() + UP * 0.35

        head.move_to(head_at(pos))
        state.next_to(head, UP, buff=0.2)
        rules = VGroup(
            T("(carry, 1)  →  write 0, move ←", 24, GREY_A, MONO_FONT),
            T("(carry, 0)  →  write 1, HALT", 24, GREY_A, MONO_FONT),
            T("(carry, _)  →  write 1, HALT", 24, GREY_A, MONO_FONT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_edge(UP, buff=1.0)
        num = MathTex("1011_2 = 11", font_size=48).next_to(cells, DOWN, buff=0.8)
        self.play(Create(cells), FadeIn(syms), run_time=1.2)
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(state), FadeIn(rules), Write(num))
        self.say("Alan Turing, 1936: a tape, a head, and a table of rules. Here: add one.")
        writes = [(5, "0", 0), (4, "0", 0), (3, "1", 1)]
        for i, sym, rule in writes:
            box = SurroundingRectangle(rules[rule], color=CODE, buff=0.08)
            self.play(Create(box), cells[i].animate.set_fill(CODE, 0.25), run_time=0.5)
            new = T(sym, 44, CODE, MONO_FONT).move_to(cells[i])
            self.play(Transform(syms[i], new), run_time=0.5)
            if rule == 0:
                self.play(head.animate.move_to(head_at(i - 1)),
                          state.animate.next_to(head_at(i - 1), UP, buff=0.45),
                          cells[i].animate.set_fill(opacity=0), FadeOut(box), run_time=0.6)
            else:
                self.play(Transform(state, T("state: HALT", 26, PHYS, MONO_FONT).move_to(state)),
                          FadeOut(box), run_time=0.6)
        res = MathTex("1100_2 = 12", font_size=48, color=CODE).move_to(num)
        self.play(Transform(num, res))
        self.say("Every app, every game, every AI reduces to steps this simple.", wait=1.8)
        self.say("Turing also proved some questions no machine can ever answer.", color=PHYS,
                 wait=1.8)
        self.clear_all()

    def sorting(self):
        rng = np.random.default_rng(3)
        vals = list(rng.permutation(40) + 1)
        W = 0.26
        bars = VGroup(*[Rectangle(width=W * 0.8, height=0.11 * v, stroke_width=0,
                                  fill_color=interpolate_color(ManimColor(MATH), ManimColor(CODE), v / 40),
                                  fill_opacity=1) for v in vals])
        base = DOWN * 2.3
        for i, b in enumerate(bars):
            b.move_to(base + RIGHT * (i - 19.5) * W, aligned_edge=DOWN)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.02), run_time=1.2)
        self.say("An algorithm is a recipe. Quicksort: pick a pivot, split, repeat.")

        order = list(range(len(vals)))  # order[slot] = bar index
        swaps = []
        a = vals[:]

        def qs(lo, hi):
            if lo >= hi:
                return
            p = a[hi]
            i = lo
            for j in range(lo, hi):
                if a[j] < p:
                    a[i], a[j] = a[j], a[i]
                    swaps.append((i, j, hi))
                    i += 1
            a[i], a[hi] = a[hi], a[i]
            swaps.append((i, hi, hi))
            qs(lo, i - 1)
            qs(i + 1, hi)

        qs(0, len(a) - 1)
        for (i, j, piv) in swaps:
            if i == j:
                continue
            bi, bj = bars[order[i]], bars[order[j]]
            xi, xj = bi.get_x(), bj.get_x()
            self.play(bi.animate.set_x(xj), bj.animate.set_x(xi), run_time=0.07, rate_func=linear)
            order[i], order[j] = order[j], order[i]
        self.play(LaggedStart(*[bars[k].animate.set_fill(CODE) for k in order], lag_ratio=0.03),
                  run_time=1.2)
        self.say("n·log n steps instead of n²: for a billion items, seconds instead of decades.",
                 color=CODE, wait=2.0)
        self.clear_all()


class S06b_Life(Base):
    def construct(self):
        self.continue_chapter(*CH)
        GH, GW = 90, 150
        VH, VW = 50, 88
        grid = np.zeros((GH, GW), np.uint8)
        gun = [(0, 4), (0, 5), (1, 4), (1, 5), (10, 4), (10, 5), (10, 6), (11, 3), (11, 7), (12, 2),
               (12, 8), (13, 2), (13, 8), (14, 5), (15, 3), (15, 7), (16, 4), (16, 5), (16, 6),
               (17, 5), (20, 2), (20, 3), (20, 4), (21, 2), (21, 3), (21, 4), (22, 1), (22, 5),
               (24, 0), (24, 1), (24, 5), (24, 6), (34, 2), (34, 3), (35, 2), (35, 3)]
        for x, y in gun:
            grid[y + 3, x + 3] = 1
        rng = np.random.default_rng(1)
        grid[20:46, 55:85] = (rng.random((26, 30)) < 0.35)

        def step(g):
            n = sum(np.roll(np.roll(g, dy, 0), dx, 1)
                    for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0))
            return ((n == 3) | ((g == 1) & (n == 2))).astype(np.uint8)

        cell = 12
        age = np.zeros_like(grid, np.float64)

        def render(g, age):
            v = g[:VH, :VW]
            a = age[:VH, :VW]
            rgb = np.zeros((VH, VW, 3), np.uint8)
            rgb[:] = (14, 18, 26)
            fresh = np.array([255, 255, 255]); c = np.array([0x7B, 0xED, 0x9F])
            t = np.clip(a / 6, 0, 1)[..., None]
            alive = (fresh * (1 - t) + c * t).astype(np.uint8)
            rgb[v == 1] = alive[v == 1]
            big = np.kron(rgb, np.ones((cell, cell, 1), np.uint8))
            big[::cell, :, :] = (8, 10, 15)
            big[:, ::cell, :] = (8, 10, 15)
            return rgba(big)

        img = ImageMobject(render(grid, age)).scale_to_fit_height(6.0).shift(DOWN * 0.15)
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        rules = VGroup(
            T("CONWAY'S GAME OF LIFE", 30, CODE, TITLE_FONT, weight=BOLD),
            T("born with exactly 3 neighbours", 22, GREY_A),
            T("survives with 2 or 3", 22, GREY_A),
            T("otherwise dies", 22, GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        self.play(FadeIn(img), run_time=1.0)
        rules.move_to(img.get_corner(UR) + DL * 0.2, aligned_edge=UR)
        bg = BackgroundRectangle(rules, color=BG, fill_opacity=0.85, buff=0.2)
        self.play(FadeIn(bg), FadeIn(rules))
        self.say("Three rules. No designer. Yet 'life' emerges: gliders, guns, chaos.")
        state = {"g": grid, "age": age}

        def gens(n, dt_per_gen=1 / 12):
            for _ in range(n):
                g2 = step(state["g"])
                state["age"] = np.where(g2 == 1, state["age"] + 1, 0)
                state["g"] = g2
                img.pixel_array = render(state["g"], state["age"])
                self.wait(dt_per_gen)

        gens(70)
        self.say("This glider gun fires forever. Life can even simulate a whole computer.",
                 color=CODE)
        gens(80)
        self.clear_all(keep_corner=False)


class S06c_Mandelbrot(Base):
    def construct(self):
        self.continue_chapter(*CH)
        px, py = 1280, 720
        target = complex(-0.743643887037151, 0.131825904205330)
        start = complex(-0.6, 0.0)
        w0, w1 = 3.6, 3.6e-5
        k = ValueTracker(0)

        def frame(u):
            w = w0 * (w1 / w0) ** u
            c = target + (start - target) * (w / w0)
            maxit = int(250 + 220 * np.log10(w0 / w))
            return mandel_rgb(mandel(c.real, c.imag, w, px, py, maxit))

        img = ImageMobject(frame(0)).set(height=config.frame_height)
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        self.bring_to_front(self.corner)
        eq = MathTex("z_{n+1} = z_n^2 + c", font_size=64)
        box = BackgroundRectangle(eq, color=BG, fill_opacity=0.7, buff=0.3)
        eqg = VGroup(box, eq).to_edge(UP, buff=0.8)
        self.play(FadeIn(img), run_time=1.2)
        self.add(self.corner)
        self.play(FadeIn(eqg))
        self.say("The Mandelbrot set: one line of arithmetic, repeated.")
        img.add_updater(lambda m: setattr(m, "pixel_array", frame(k.get_value())))
        self.play(k.animate.set_value(0.35), run_time=5, rate_func=rate_functions.ease_in_sine)
        self.say("Zoom in 100,000 times. The detail never ends.")
        self.play(k.animate.set_value(1), run_time=9, rate_func=linear)
        img.clear_updaters()
        self.say("Infinite complexity from a simple rule — only a computer lets us see it.",
                 wait=2.0)
        self.clear_all(keep_corner=False)
