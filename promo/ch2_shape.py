from common import *


class S02_Shape(Base):
    def construct(self):
        self.chapter("II", "SHAPE", "MP", "geometry: the first science")
        self.pythagoras()
        self.rolling_pi()
        self.clear_all(keep_corner=False)

    def pythagoras(self):
        a, b = 1.5, 2.0
        o = LEFT * 1.0 + DOWN * 0.3
        A, B, C = o, o + RIGHT * b, o + UP * a
        tri = Polygon(A, B, C, color=WHITE, fill_color=GREY_E, fill_opacity=1, stroke_width=3)
        sq_b = Polygon(A, B, B + DOWN * b, A + DOWN * b, color=PHYS, fill_opacity=0.35)
        sq_a = Polygon(A, C, C + LEFT * a, A + LEFT * a, color=CODE, fill_opacity=0.35)
        n = np.array([a, b, 0])
        sq_c = Polygon(B, C, C + n, B + n, color=MATH, fill_opacity=0.35)
        la = MathTex("a^2", color=CODE).move_to(sq_a)
        lb = MathTex("b^2", color=PHYS).move_to(sq_b)
        lc = MathTex("c^2", color=MATH).move_to(sq_c)
        fig = VGroup(sq_a, sq_b, sq_c, tri, la, lb, lc).move_to(LEFT * 3.2 + DOWN * 0.1)
        self.play(DrawBorderThenFill(tri))
        self.play(LaggedStart(*[DrawBorderThenFill(s) for s in (sq_a, sq_b, sq_c)], lag_ratio=0.3),
                  run_time=1.8)
        self.play(FadeIn(la), FadeIn(lb), FadeIn(lc))
        eq = MathTex("a^2", "+", "b^2", "=", "c^2", font_size=80).shift(RIGHT * 3.4 + UP * 0.2)
        eq[0].set_color(CODE); eq[2].set_color(PHYS); eq[4].set_color(MATH)
        self.play(Write(eq))
        self.say("Pythagoras: true for every right triangle, forever. But why?", wait=1.5)
        self.play(FadeOut(fig), eq.animate.scale(0.6).to_corner(UR, buff=0.5), run_time=1)

        # proof by rearrangement inside a square of side a + b
        a, b = 1.3, 2.2
        s = a + b
        org = np.array([-s / 2, -s / 2 + 0.2, 0])
        P = lambda x, y: org + np.array([x, y, 0])
        config1 = [
            [P(0, 0), P(a, 0), P(0, b)],
            [P(s, 0), P(s, a), P(a, 0)],
            [P(s, s), P(b, s), P(s, a)],
            [P(0, s), P(0, b), P(b, s)],
        ]
        config2 = [
            [P(s, 0), P(s, a), P(a, 0)],
            [P(a, a), P(a, 0), P(s, a)],
            [P(0, s), P(0, a), P(a, s)],
            [P(a, a), P(a, s), P(0, a)],
        ]
        frame = Square(s, color=GREY_B).move_to(P(s / 2, s / 2))
        tris = VGroup(*[Polygon(*v, color=WHITE, stroke_width=2, fill_color=GREY_D,
                                fill_opacity=1) for v in config1])
        hole_c = Polygon(P(a, 0), P(s, a), P(b, s), P(0, b), color=MATH, fill_opacity=0.35,
                         stroke_width=0)
        lab_c = MathTex("c^2", color=MATH, font_size=60).move_to(hole_c)
        self.play(Create(frame))
        self.play(FadeIn(hole_c), LaggedStart(*[FadeIn(t, scale=0.8) for t in tris], lag_ratio=0.2))
        self.play(Write(lab_c))
        self.say("Four copies of the triangle in a square. The empty space is c².", wait=1.2)
        hole_a = Square(a, color=CODE, fill_opacity=0.35, stroke_width=0).move_to(P(a / 2, a / 2))
        hole_b = Square(b, color=PHYS, fill_opacity=0.35, stroke_width=0).move_to(P(a + b / 2, a + b / 2))
        lab_a = MathTex("a^2", color=CODE, font_size=52).move_to(hole_a)
        lab_b = MathTex("b^2", color=PHYS, font_size=60).move_to(hole_b)
        self.play(FadeOut(hole_c), FadeOut(lab_c), run_time=0.5)
        self.play(*[Transform(tris[i], Polygon(*config2[i], color=WHITE, stroke_width=2,
                                                 fill_color=GREY_D, fill_opacity=1))
                    for i in range(4)], run_time=2.2)
        self.play(FadeIn(hole_a), FadeIn(hole_b), Write(lab_a), Write(lab_b))
        self.say("Slide them around. Same triangles, same empty space: a² + b² = c².", wait=1.2)
        self.play(Indicate(eq, color=WHITE, scale_factor=1.2))
        self.wait(0.8)
        self.clear_all()

    def rolling_pi(self):
        nl = NumberLine(x_range=[0, 4, 1], length=10, include_numbers=True,
                        font_size=36, color=GREY_B).shift(DOWN * 1.2)
        u = nl.unit_size
        r = u / 2  # diameter = 1
        t = ValueTracker(0)

        def center():
            return nl.n2p(t.get_value()) + UP * r

        wheel = always_redraw(lambda: Circle(r, color=MATH, stroke_width=4).move_to(center()))
        spoke_pt = lambda: center() + r * np.array([
            np.cos(-PI / 2 - t.get_value() * u / r), np.sin(-PI / 2 - t.get_value() * u / r), 0])
        spoke = always_redraw(lambda: Line(center(), spoke_pt(), color=MATH, stroke_width=2))
        pen = always_redraw(lambda: Dot(spoke_pt(), color=PHYS, radius=0.09))
        path = TracedPath(spoke_pt, stroke_color=PHYS, stroke_width=4)
        unrolled = always_redraw(lambda: Line(nl.n2p(0), nl.n2p(t.get_value()), color=MATH,
                                              stroke_width=7))
        d = MathTex("d = 1", color=MATH).next_to(nl.n2p(0) + UP * 2 * r, UP)
        self.play(Create(nl), Create(wheel), FadeIn(spoke), FadeIn(pen), FadeIn(d))
        self.add(path, unrolled, pen)
        self.say("Roll a circle of diameter 1 through one full turn…")
        self.play(t.animate.set_value(PI), run_time=5, rate_func=smooth)
        pi_lab = MathTex("\\pi = 3.14159\\,26535\\,89793\\ldots", font_size=60, color=WHITE)
        pi_lab.to_edge(UP, buff=1.0)
        arrow = Arrow(pi_lab.get_bottom(), nl.n2p(PI) + UP * 0.1, color=GREY_B, buff=0.2)
        self.play(Write(pi_lab), GrowArrow(arrow))
        self.say("…and it lands on π. A number that never ends and never repeats.", wait=1.5)
        path.clear_updaters()
        self.play(path.animate.set_stroke(width=7), run_time=0.6)
        self.say("The point on the rim draws a cycloid — the fastest slide under gravity.",
                 color=PHYS, wait=2.0)
        self.clear_all()

        quote = T("“The book of nature is written\nin the language of mathematics.”",
                  46, WHITE, TITLE_FONT, weight=MEDIUM, line_spacing=1.2)
        who = T("— Galileo Galilei, 1623", 28, PHYS).next_to(quote, DOWN, buff=0.6)
        self.play(FadeIn(quote, shift=UP * 0.2), run_time=1.5)
        self.play(FadeIn(who), run_time=0.8)
        self.wait(2.5)
        self.clear_all()
