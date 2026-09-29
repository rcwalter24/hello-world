from common import *


class S01_Number(Base):
    def construct(self):
        self.chapter("I", "NUMBER", "MC", "where it all starts: counting")
        self.gauss()
        self.binary()
        self.primes()
        self.clear_all(keep_corner=False)

    # 1 + 2 + ... + n, seen as half a rectangle
    def gauss(self):
        n, s = 6, 0.62
        origin = LEFT * 1.8 + UP * 1.2
        blue = VGroup()
        for r in range(n):
            blue.add(VGroup(*[Dot(origin + s * (c * RIGHT + r * DOWN), radius=0.17, color=MATH)
                              for c in range(r + 1)]))
        q = MathTex("1+2+3+4+5+6", "=", "\\,?", font_size=52).to_edge(UP, buff=1.1)
        q.shift(RIGHT * 0.2)
        blue_flat = VGroup(*[d for row in blue for d in row])
        self.play(Write(q[0]), run_time=1.0)
        self.play(LaggedStart(*[LaggedStart(*[GrowFromCenter(d) for d in row], lag_ratio=0.1)
                                for row in blue], lag_ratio=0.3), run_time=2.0)
        self.play(Write(q[1:]), run_time=0.5)
        self.say("Add the numbers one to six. Or... just look.", wait=1.0)

        center = origin + s * (n / 2 * RIGHT + (n - 1) / 2 * DOWN)
        orange = blue_flat.copy()
        self.add(orange)
        self.play(orange.animate.set_color(PHYS), run_time=0.6)
        self.play(Rotate(orange, PI, about_point=center), run_time=1.8)
        rect = SurroundingRectangle(VGroup(blue_flat, orange), color=GREY_B, buff=0.2,
                                    corner_radius=0.1)
        b1 = Brace(rect, DOWN, color=GREY_B)
        b2 = Brace(rect, LEFT, color=GREY_B)
        l1 = b1.get_tex("7").set_color(GREY_A)
        l2 = b2.get_tex("6").set_color(GREY_A)
        self.play(Create(rect), GrowFromCenter(b1), GrowFromCenter(b2), FadeIn(l1), FadeIn(l2))
        ans = MathTex("1+2+3+4+5+6", "=", "\\frac{6 \\times 7}{2}", "=21", font_size=52)
        ans.move_to(q)
        self.play(TransformMatchingTex(q, ans), run_time=1.2)
        self.say("Two copies make a rectangle. Half of 6 × 7 is 21.", wait=1.2)
        gen = MathTex("1+2+\\cdots+n=\\frac{n(n+1)}{2}", font_size=58, color=MATH).move_to(ans)
        self.play(ReplacementTransform(ans, gen), run_time=1.2)
        self.say("A proof you can see — the young Gauss's famous trick.", wait=1.6)
        self.clear_all()

    # counting the way a computer does
    def binary(self):
        bits = 5
        vals = [2 ** (bits - 1 - i) for i in range(bits)]
        bulbs = VGroup(*[Circle(0.5, color=CODE, stroke_width=4) for _ in range(bits)])
        bulbs.arrange(RIGHT, buff=0.45).shift(UP * 0.3)
        places = VGroup(*[T(str(v), 26, GREY_B).next_to(b, UP, 0.3) for v, b in zip(vals, bulbs)])
        digits = VGroup(*[T("0", 40, WHITE, MONO_FONT).move_to(b) for b in bulbs])
        dec = T("0", 80, WHITE, TITLE_FONT, weight=BOLD).next_to(bulbs, DOWN, buff=0.8)
        self.play(LaggedStart(*[Create(b) for b in bulbs], lag_ratio=0.15),
                  FadeIn(places), FadeIn(digits), FadeIn(dec))
        self.say("To a computer, every number is a row of switches: off or on.")

        def show(k):
            for i in range(bits):
                on = (k >> (bits - 1 - i)) & 1
                bulbs[i].set_fill(CODE, opacity=0.85 if on else 0)
                digits[i].become(T(str(on), 40, BG if on else GREY_B, MONO_FONT).move_to(bulbs[i]))
            dec.become(T(str(k), 80, WHITE, TITLE_FONT, weight=BOLD).move_to(dec))

        for k in range(0, 32):
            show(k)
            self.wait(0.2 if k < 8 else 0.1)
        self.wait(0.6)
        show(21)
        expr = MathTex("21", "=", "16", "+", "4", "+", "1", "=", "10101_2", font_size=48)
        expr.next_to(bulbs, DOWN, buff=0.8)
        self.play(ReplacementTransform(dec, expr), run_time=1.0)
        self.say("Our friend 21 again: 10101. Same number, a language machines speak.", wait=1.6)
        self.clear_all()

    # the sieve of Eratosthenes
    def primes(self):
        cells = VGroup()
        for k in range(1, 101):
            sq = Square(0.56, stroke_width=1, stroke_color=GREY_D)
            lab = T(str(k), 20, GREY_A)
            cells.add(VGroup(sq, lab))
        cells.arrange_in_grid(10, 10, buff=0.04).shift(UP * 0.35 + LEFT * 2.2)
        for c in cells:
            c[1].move_to(c[0])
        self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.01), run_time=1.5)
        self.say("Sieve of Eratosthenes, ~240 BC: cross out the multiples.")
        self.play(cells[0].animate.set_opacity(0.12), run_time=0.4)
        cols = {2: MATH, 3: PHYS, 5: CODE, 7: "#C39BD3"}
        for p, col in cols.items():
            self.play(cells[p - 1][0].animate.set_fill(col, 0.9),
                      cells[p - 1][1].animate.set_color(BG), run_time=0.4)
            mult = [cells[m - 1] for m in range(p * p, 101, p)]
            self.play(LaggedStart(*[m.animate.set_opacity(0.12) for m in mult], lag_ratio=0.03),
                      run_time=1.0)
        primes = [k for k in range(2, 101) if all(k % d for d in range(2, int(k ** 0.5) + 1))]
        self.play(*[cells[k - 1][0].animate.set_fill(MATH, 0.9) for k in primes],
                  *[cells[k - 1][1].animate.set_color(BG) for k in primes], run_time=1.0)
        side = VGroup(
            T("PRIMES", 40, MATH, TITLE_FONT, weight=BOLD),
            T("the atoms of arithmetic", 26, GREY_A),
            MathTex("12 = 2^2\\times 3", font_size=44),
            MathTex("2026 = 2\\times 1013", font_size=44),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(cells, RIGHT, buff=0.8)
        self.play(FadeIn(side, shift=LEFT * 0.3, lag_ratio=0.2), run_time=1.5)
        self.say("Euclid proved they never end. But their exact pattern is still a mystery…",
                 wait=2.2)
        self.clear_all()
