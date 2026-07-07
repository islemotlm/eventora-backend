from manim import *


class RedBlueScene(Scene):
    def construct(self):
        title = Text("Red Circle and Blue Square", font_size=36, color=WHITE)
        title.to_edge(UP)

        circle = Circle(radius=1.0, color=RED, fill_opacity=0.8)
        square = Square(side_length=1.8, color=BLUE, fill_opacity=0.8)

        circle.move_to(LEFT * 2.5)
        square.move_to(RIGHT * 2.5)

        self.play(FadeIn(title, shift=UP * 0.3), run_time=0.8)
        self.play(FadeIn(circle), FadeIn(square), run_time=1.0)
        self.play(
            circle.animate.scale(1.15).shift(UP * 0.4),
            square.animate.scale(0.9).shift(DOWN * 0.4),
            run_time=1.2,
        )
        self.play(
            circle.animate.move_to(LEFT * 0.5),
            square.animate.move_to(RIGHT * 0.5),
            run_time=1.0,
        )
        self.wait(0.6)
