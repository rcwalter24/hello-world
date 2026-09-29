from common import *
from ch0_opening import trinity


class S09_Finale(Base):
    def construct(self):
        dots, edges, labels = trinity()
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.3), run_time=1.5)
        self.play(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(labels), run_time=0.8)
        tri = VGroup(dots, edges, labels)
        self.play(tri.animate.scale(0.5).to_edge(UP, buff=0.7), run_time=1.2)

        lines = VGroup(
            T("Mathematics is the language.", 44, MATH, TITLE_FONT, weight=BOLD),
            T("Physics is the story.", 44, PHYS, TITLE_FONT, weight=BOLD),
            T("Computation is the pen.", 44, CODE, TITLE_FONT, weight=BOLD),
        ).arrange(DOWN, buff=0.45).shift(DOWN * 0.95)
        for l, d in zip(lines, dots):
            self.play(FadeIn(l, shift=UP * 0.2), Indicate(d, color=WHITE, scale_factor=1.6), run_time=1.1)
            self.wait(0.7)
        self.wait(1.0)
        self.play(FadeOut(lines, shift=UP * 0.2), run_time=0.9)

        a = T("The next chapter is unwritten.", 46, WHITE, TITLE_FONT, weight=MEDIUM).shift(DOWN * 0.3)
        b = T("Come write it.", 62, WHITE, TITLE_FONT, weight=BOLD).next_to(a, DOWN, buff=0.6)
        b.set_color_by_gradient(MATH, PHYS, CODE)
        self.play(Write(a), run_time=1.6)
        self.wait(0.8)
        self.play(FadeIn(b, scale=1.15), run_time=1.4)
        self.wait(2.2)
        self.play(FadeOut(VGroup(a, b)), tri.animate.move_to(UP * 0.9).scale(1.3), run_time=1.5)
        title = T("THE UNREASONABLE BEAUTY", 54, WHITE, TITLE_FONT, weight=BOLD).shift(DOWN * 1.4)
        sub = T("Mathematics  ·  Physics  ·  Computation", 28, GREY_B).next_to(title, DOWN, buff=0.35)
        self.play(FadeIn(title, shift=UP * 0.2), FadeIn(sub), run_time=1.5)
        self.wait(3.0)
        self.play(FadeOut(VGroup(tri, title, sub)), run_time=2.0)
        self.wait(0.8)
