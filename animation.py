from manim import *
import numpy as np


class MathSpeechAnimation(Scene):
    def construct(self):
        audio_duration = 275.328
        self.add_sound("sourcecompile_mathspeech.mp3")

        # === CẢNH 1: Tiêu đề ===
        title = Text("Các Tính Chất Đường Thẳng", font_size=48, color=WHITE)
        title.move_to(ORIGIN)

        self.play(FadeIn(title))
        self.wait(2)
        self.play(FadeOut(title))

        # === CẢNH 2: Cắt nhau ===
        intersect_line1 = Line(LEFT * 3 + DOWN, RIGHT * 3 + UP, color=BLUE)
        intersect_line2 = Line(LEFT * 3 + UP, RIGHT * 3 + DOWN, color=YELLOW)

        intersection_point = line_intersection(
            [
                intersect_line1.get_start(),
                intersect_line1.get_end(),
            ],
            [
                intersect_line2.get_start(),
                intersect_line2.get_end(),
            ],
        )
        dot = Dot(intersection_point, color=RED)
        intersect_label = Text("d₁ ∩ d₂ = {M}", color=WHITE, font_size=36)
        intersect_label.move_to(DOWN * 2.5)

        self.play(Create(intersect_line1))
        self.play(Create(intersect_line2))
        self.play(GrowFromCenter(dot))
        self.play(Write(intersect_label))
        self.wait(3)
        self.play(FadeOut(intersect_line1, intersect_line2, dot, intersect_label))

        # === CẢNH 3: Vuông góc ===
        line1 = Line(LEFT * 3, RIGHT * 3, color=BLUE)
        line2 = Line(DOWN * 2.5, UP * 2.5, color=GREEN)
        right_angle = RightAngle(line1, line2, length=0.3, color=WHITE)
        perp_label = Text("d₁ ⟂ d₂", color=WHITE, font_size=40)
        perp_label.move_to(UP * 3)

        self.play(Create(line1))
        self.play(Create(line2))
        self.play(Create(right_angle))
        self.play(Write(perp_label))
        self.wait(3)
        self.play(FadeOut(line1, line2, right_angle, perp_label))

        # === CẢNH 4: Góc mũ ===
        ray1 = Line(ORIGIN, RIGHT * 3, color=ORANGE)
        ray2 = Line(ORIGIN, rotate_vector(RIGHT * 3, 60 * DEGREES), color=PURPLE)
        angle_arc = Angle(ray1, ray2, radius=0.8, color=YELLOW)
        angle_label = Text("AOB̂ = 60°", color=WHITE, font_size=36)
        angle_label.next_to(angle_arc, RIGHT + UP * 0.3)
        note = Text("Â là ký hiệu góc tại đỉnh A", color=GRAY, font_size=28)
        note.to_edge(DOWN)

        self.play(Create(ray1))
        self.play(Create(ray2))
        self.play(Create(angle_arc))
        self.play(Write(angle_label))
        self.play(FadeIn(note))
        self.wait(4)

        # === CẢNH 5: Kết thúc ===
        remaining_time = audio_duration - self.time - 2
        if remaining_time > 0:
            self.wait(remaining_time)
        self.play(FadeOut(*self.mobjects))
        self.wait(1)
