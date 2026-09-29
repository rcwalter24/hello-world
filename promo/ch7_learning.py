from common import *


DIGIT = [
    "01110",
    "10001",
    "00001",
    "00110",
    "00001",
    "10001",
    "01110",
]


class S07_Learning(Base):
    def construct(self):
        self.chapter("VII", "LEARNING", "MC", "teaching machines with calculus")
        self.network()
        self.descent()
        self.clear_all(keep_corner=False)

    def network(self):
        pix = VGroup()
        for r, row in enumerate(DIGIT):
            for c, ch in enumerate(row):
                pix.add(Square(0.28, stroke_width=0.5, stroke_color=GREY_D,
                               fill_color=WHITE, fill_opacity=0.95 if ch == "1" else 0.05)
                        .move_to(np.array([c * 0.28, -r * 0.28, 0])))
        pix.move_to(LEFT * 5.6 + DOWN * 0.1)
        sizes = [6, 8, 8, 4]
        xs = [-3.4, -0.9, 1.6, 4.1]
        layers = VGroup()
        for n, x in zip(sizes, xs):
            layers.add(VGroup(*[Circle(0.2, color=CODE, stroke_width=2).move_to(
                np.array([x, (n - 1) / 2 * 0.6 - i * 0.6, 0]) + DOWN * 0.35) for i in range(n)]))
        edges = VGroup()
        for a, b in zip(layers[:-1], layers[1:]):
            edges.add(VGroup(*[Line(u.get_center(), v.get_center(), stroke_width=1,
                                    color=GREY_C, stroke_opacity=0.35, buff=0.2)
                               for u in a for v in b]))
        outs = VGroup(*[T(s, 26, GREY_B).next_to(layers[-1][i], RIGHT, 0.3)
                        for i, s in enumerate(["0", "1", "2", "3"])])
        self.play(FadeIn(pix, lag_ratio=0.02), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(l, lag_ratio=0.1) for l in layers], lag_ratio=0.2),
                  LaggedStart(*[Create(e) for e in edges], lag_ratio=0.2), FadeIn(outs), run_time=2)
        formula = MathTex("a^{(\\ell+1)} = \\sigma\\!\\left(W^{(\\ell)} a^{(\\ell)} + b^{(\\ell)}\\right)",
                          font_size=46, color=CODE).to_edge(UP, buff=0.8)
        self.play(Write(formula))
        self.say("A neural network: layers of numbers, multiplied and added — linear algebra.")
        rng = np.random.default_rng(5)
        for rep in range(2):
            acts = [rng.random(n) for n in sizes]
            acts[-1] = np.array([0.05, 0.1, 0.15, 0.95]) if rep else np.array([0.3, 0.2, 0.35, 0.4])
            for li in range(len(layers)):
                anims = [layers[li][i].animate.set_fill(CODE, opacity=float(acts[li][i]))
                         for i in range(sizes[li])]
                if li > 0:
                    flashes = [ShowPassingFlash(e.copy().set_stroke(CODE, 2.5, 1), time_width=0.6)
                               for e in edges[li - 1]]
                    self.play(LaggedStart(*flashes, lag_ratio=0.004), *anims, run_time=0.8)
                else:
                    self.play(*anims, run_time=0.4)
            if rep == 0:
                self.say("At first its guesses are random. Then we measure how wrong it is…")
                self.play(*[l.animate.set_fill(opacity=0) for l in layers], run_time=0.4)
        box = SurroundingRectangle(VGroup(layers[-1][3], outs[3]), color=PHYS, buff=0.12)
        self.play(Create(box), outs[3].animate.set_color(PHYS))
        self.say("…and nudge millions of weights. After training: it reads a '3'.", color=PHYS,
                 wait=1.8)
        self.clear_all()

    def descent(self):
        def L(x, y):
            return (0.06 * (x - 3) ** 2 + 0.35 * (y + 0.8) ** 2
                    + 0.9 * np.exp(-((x + 1.0) ** 2 + (y - 0.2) ** 2) / 1.5)
                    + 0.25 * np.sin(1.3 * x) * np.cos(1.1 * y))

        fw, fh = config.frame_width, config.frame_height
        px, py = 960, 540
        X, Y = np.meshgrid(np.linspace(-fw / 2, fw / 2, px), np.linspace(fh / 2, -fh / 2, py))
        Z = L(X, Y)
        zn = (Z - Z.min()) / (Z.max() - Z.min())
        rgb = colormap(zn ** 0.7, ["#07131c", "#123447", "#1d5870", "#3f8fb0", MATH, "#d8f3ff"])
        iso = np.abs(((Z - Z.min()) * 5) % 1 - 0.5) > 0.47
        rgb[iso] = (rgb[iso] * 0.4 + 255 * 0.6 * np.array([0.5, 0.8, 0.9])).astype(np.uint8)
        rgb = (rgb * 0.75).astype(np.uint8)
        img = ImageMobject(rgba(rgb)).set(height=fh)
        self.play(FadeIn(img), run_time=1)
        self.add(self.corner)
        rule = MathTex("\\theta \\leftarrow \\theta - \\eta\\,\\nabla L(\\theta)", font_size=54)
        rb = BackgroundRectangle(rule, color=BG, fill_opacity=0.8, buff=0.25)
        rg = VGroup(rb, rule).to_corner(UR, buff=0.7)
        self.play(FadeIn(rg))
        self.say("Picture the error as a landscape. Learning = walking downhill.")

        def grad(x, y, h=1e-4):
            return np.array([(L(x + h, y) - L(x - h, y)) / (2 * h),
                             (L(x, y + h) - L(x, y - h)) / (2 * h)])

        p = np.array([-5.6, 2.6]); v = np.zeros(2)
        path = [p.copy()]
        for _ in range(260):
            v = 0.72 * v - 0.3 * grad(*p)
            p = p + v
            path.append(p.copy())
        pts = [np.array([q[0], q[1], 0]) for q in path]
        trail = VMobject(stroke_color=PHYS, stroke_width=4).set_points_smoothly(pts[:120])
        trail2 = VMobject(stroke_color=PHYS, stroke_width=4).set_points_smoothly(pts[119:])
        ball = glow_dot(PHYS, 0.13, 6, 0.04, 0.12).move_to(pts[0])
        self.play(FadeIn(ball, scale=0.5))
        self.play(MoveAlongPath(ball, trail), Create(trail), run_time=5, rate_func=linear)
        self.play(MoveAlongPath(ball, trail2), Create(trail2), run_time=3, rate_func=smooth)
        self.play(Flash(ball.get_center(), color=PHYS, line_length=0.4))
        self.say("The chain rule you learn in calculus — 'backpropagation' — trains every modern AI.",
                 wait=2.4)
        self.clear_all()
