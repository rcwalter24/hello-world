from style import *


class Act0(FilmScene):
    DURATION = BUDGET["act0"]

    def construct(self):
        dot = glow_dot(ORIGIN + LEFT * 3, WHITE_)
        self.caption("Everything begins with a point.", start=1.6, dur=3.6)
        self.play(FadeIn(dot, scale=0.3), run_time=1.6)          # 1.6
        self.play(Indicate(dot, scale_factor=1.6, color=WHITE_), run_time=1.0)  # 2.6
        self.wait(1.4)                                                # 4.0

        # point -> line
        line = Line(LEFT * 3, RIGHT * 3)
        neon(line, GOLD)
        self.caption("A line.  A curve.  A circle.", start=0.2, dur=5.5)
        self.play(Create(line), MoveAlongPath(dot, line), run_time=2.2)  # 6.2
        self.wait(0.3)                                                # 6.5

        # line -> circle
        circle = Circle(radius=2.2)
        neon(circle, GOLD)
        self.play(Transform(line, circle), dot.animate.move_to(circle.point_from_proportion(0)),
                  run_time=2.3, rate_func=smooth)                    # 8.8
        self.play(MoveAlongPath(dot, circle), run_time=2.4, rate_func=linear)  # 11.2

        # three colours appear: the seed of the whole film
        rings = VGroup(*[Circle(radius=2.2 + 0.0, stroke_width=3) for _ in range(3)])
        for r, c in zip(rings, [GOLD, CYAN, MAGENTA]):
            r.set_stroke(c, width=3, opacity=0.9)
        self.play(*[r.animate.scale(1.0 + 0.16 * (i + 1)).set_stroke(opacity=0.0)
                    for i, r in enumerate(rings)],
                  run_time=1.6, rate_func=rush_from)                  # 12.8
        self.add(rings)
        self.fade_all(1.2)                                           # 14.0
        self.pad_to()
