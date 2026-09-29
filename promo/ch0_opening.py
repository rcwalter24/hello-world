from common import *


def trinity(scale=1.0):
    pos = [UP * 1.7, DOWN * 1.2 + LEFT * 2.6, DOWN * 1.2 + RIGHT * 2.6]
    cols = [MATH, PHYS, CODE]
    names = ["MATHEMATICS", "PHYSICS", "COMPUTATION"]
    dots = VGroup(*[glow_dot(c, 0.13, 8, 0.04, 0.08).move_to(p) for c, p in zip(cols, pos)])
    edges = VGroup(*[Line(pos[i], pos[(i + 1) % 3], stroke_width=2.5)
                     .set_color([cols[i], cols[(i + 1) % 3]]) for i in range(3)])
    labels = VGroup(
        T(names[0], 24, MATH, TITLE_FONT, weight=BOLD).next_to(dots[0], UP, 0.3),
        T(names[1], 24, PHYS, TITLE_FONT, weight=BOLD).next_to(dots[1], DOWN, 0.3),
        T(names[2], 24, CODE, TITLE_FONT, weight=BOLD).next_to(dots[2], DOWN, 0.3),
    )
    return dots, edges, labels


class S00_Opening(Base):
    def construct(self):
        seed = glow_dot(WHITE, 0.07, 10, 0.05, 0.06)
        self.play(FadeIn(seed, scale=0.1), run_time=1.6)
        line = T("Every idea begins as a single point.", 36, GREY_A).shift(DOWN * 1.4)
        self.play(Write(line), run_time=1.6)
        self.wait(1.2)
        self.play(FadeOut(line), run_time=0.6)

        dots, edges, labels = trinity()
        starts = VGroup(*[seed.copy() for _ in range(3)])
        self.remove(seed)
        self.add(starts)
        self.play(*[Transform(starts[i], dots[i]) for i in range(3)], run_time=1.8,
                  rate_func=smooth)
        self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.3), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(l, shift=0.1 * UP) for l in labels], lag_ratio=0.4),
                  run_time=1.6)
        self.wait(0.8)

        triad = VGroup(starts, edges, labels)
        self.play(triad.animate.scale(0.55).shift(UP * 1.3), run_time=1.3)
        title = T("THE UNREASONABLE BEAUTY", 54, WHITE, TITLE_FONT, weight=BOLD)
        title.next_to(triad, DOWN, buff=0.7)
        sub = T("a journey from counting to the edge of knowledge", 28, GREY_B)
        sub.next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=UP * 0.2, scale=1.05), run_time=1.5)
        self.play(FadeIn(sub), run_time=1.0)
        self.wait(2.2)
        self.play(FadeOut(VGroup(triad, title, sub)), run_time=1.2)
