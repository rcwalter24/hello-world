from style import *


class Cover(FilmScene):
    def construct(self):
        rng = np.random.default_rng(3)
        # star dust
        dust = VGroup(*[Dot([rng.uniform(-7.2, 7.2), rng.uniform(-4, 4), 0],
                            radius=rng.uniform(0.008, 0.028), color=WHITE_,
                            fill_opacity=rng.uniform(0.15, 0.6)) for _ in range(140)])
        self.add(dust)
        # faint formulas: one per discipline colour
        eqs = [(r"e^{i\pi}+1=0", GOLD, [-5.0, 2.7]), (r"\nabla\times E=-\partial_t B", CYAN, [4.8, 2.9]),
               (r"S=k_B\log W", CYAN, [-5.4, -0.95]), (r"z_{n+1}=z_n^2+c", GOLD, [5.3, -1.0]),
               (r"P\overset{?}{=}NP", MAGENTA, [-5.4, 1.5]), (r"|\psi\rangle=\alpha|0\rangle+\beta|1\rangle", MAGENTA, [4.7, 1.6])]
        for tex, c, p in eqs:
            self.add(MathTex(tex, color=c, font_size=32).move_to([p[0], p[1], 0]).set_opacity(0.42))
        # concentric rings behind the core
        for r, c in zip([1.0, 1.55, 2.1], [GOLD, CYAN, MAGENTA]):
            ring = Circle(radius=r).stretch(0.62, 1)
            neon(ring, c, 2.0); ring.set_stroke(opacity=0.35)
            self.add(ring)
        # three braided strands, pinching to the centre
        cols = [GOLD, CYAN, MAGENTA]
        for k, c in enumerate(cols):
            ph = TAU * k / 3
            f = lambda x, ph=ph: np.array([x, (1.35 * (1 - np.exp(-(x / 1.7) ** 2)) * np.exp(-(x / 6.0) ** 2) + 0.03)
                                           * np.sin(2.0 * x + ph), 0])
            curve = ParametricFunction(f, t_range=[-7.1, 7.1, 0.02])
            neon(curve, c, 5.0)
            self.add(curve)
        self.add(glow_dot(ORIGIN, WHITE_, r=0.16, layers=9))
        # title
        title = Text("THE SOURCE CODE", font=FONT, font_size=74, weight=LIGHT, color=WHITE_)
        title2 = Text("OF EVERYTHING", font=FONT, font_size=74, weight=LIGHT, color=WHITE_)
        VGroup(title, title2).arrange(DOWN, buff=0.12).move_to(DOWN * 2.3)
        for t in (title, title2): t.set_stroke(BG, width=8, background=True)
        sub = VGroup(Text("MATHEMATICS", font=FONT, font_size=24, color=GOLD, weight=BOLD),
                     Text("PHYSICS", font=FONT, font_size=24, color=CYAN, weight=BOLD),
                     Text("COMPUTER SCIENCE", font=FONT, font_size=24, color=MAGENTA, weight=BOLD))
        sub.arrange(RIGHT, buff=0.7).next_to(title2, DOWN, buff=0.35)
        sub.set_stroke(BG, width=6, background=True)
        self.add(title, title2, sub)
