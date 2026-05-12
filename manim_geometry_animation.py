from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import *

from geometric_construction import build_construction


AUDIO_PATH = "sourcecompile_mathspeech.mp3"
AUDIO_DURATION = 275.328
FRAME_WIDTH = 14.222
FRAME_HEIGHT = 8.0


class GeometryProofAnimation(Scene):
    def construct(self) -> None:
        self.camera.background_color = "#f7f9fc"
        data = build_construction()
        raw_points = data["points"]
        radius = float(data["radius"])

        def map_point(name: str) -> np.ndarray:
            x, y = raw_points[name]
            return np.array([x * 0.92 - 1.65, y * 0.92 - 2.55, 0.0])

        def line(name1: str, name2: str, color=WHITE, width=4) -> Line:
            return Line(map_point(name1), map_point(name2), color=color, stroke_width=width)

        def point(name: str, color="#1a212e") -> Dot:
            return Dot(map_point(name), radius=0.055, color=color)

        def label(name: str, direction=UP, color="#1a212e") -> Text:
            return Text(name, font="Arial", font_size=24, color=color).next_to(
                map_point(name), direction, buff=0.08
            )

        title = Text("Bài toán hình học", font="Arial", weight=BOLD, font_size=38, color="#1a212e")
        title.to_edge(UP).shift(LEFT * 3.35)
        subtitle = Text(
            "Dựng hình chính xác + animation Manim theo lời giải",
            font="Arial",
            font_size=23,
            color="#607082",
        ).next_to(title, DOWN, aligned_edge=LEFT, buff=0.12)

        step_title = Text("", font="Arial", weight=BOLD, font_size=31, color="#1a212e")
        step_title.to_corner(UR).shift(LEFT * 0.25 + DOWN * 0.12)
        step_body = VGroup()

        a, b, c = map_point("A"), map_point("B"), map_point("C")
        incircle = Circle(radius=radius * 0.92, color="#238c64", stroke_width=4).move_to(map_point("I"))
        triangle = VGroup(
            Polygon(a, b, c, color="#235bae", stroke_width=4, fill_opacity=0.03),
            line("A", "B", "#235bae"),
            line("B", "C", "#235bae"),
            line("C", "A", "#235bae"),
        )

        base_points = VGroup(
            *[point(name) for name in ["A", "B", "C", "I", "D", "E", "F"]],
            label("A", UP),
            label("B", DL),
            label("C", DR),
            label("I", RIGHT, "#238c64"),
            label("D", DOWN),
            label("E", RIGHT),
            label("F", LEFT),
        )

        ef = line("E", "F", "#d2781e", 4)
        ki = line("K", "L", "#d2781e", 4)
        bk = DashedLine(map_point("B"), map_point("K"), color="#607082", stroke_width=3)
        cl = DashedLine(map_point("C"), map_point("L"), color="#607082", stroke_width=3)
        kl_points = VGroup(point("K", "#d2781e"), point("L", "#d2781e"), label("K", LEFT), label("L", RIGHT))

        dk = line("D", "K", "#c8373c", 5)
        ic = line("I", "C", "#c8373c", 5)
        kf = line("K", "F", "#6e4baa", 5)
        el = line("E", "L", "#6e4baa", 5)
        dl = line("D", "L", "#c8373c", 4)
        mn = line("M", "N", "#6e4baa", 5)
        ds = line("D", "S", "#238c64", 4)
        pi = line("P", "I", "#c8373c", 5)
        ass = line("A", "S", "#c8373c", 5)
        me = DashedLine(map_point("M"), map_point("E"), color="#607082", stroke_width=3)
        nf = DashedLine(map_point("N"), map_point("F"), color="#607082", stroke_width=3)

        extra_points = VGroup(
            *[point(name) for name in ["M", "N", "P", "S", "X", "Y"]],
            label("M", DL),
            label("N", DR),
            label("P", DOWN),
            label("S", UP),
            label("X", LEFT),
            label("Y", RIGHT),
        )

        conclusion = Text("AS vuông góc PI", font="Arial", weight=BOLD, font_size=34, color="#c8373c")
        conclusion.to_corner(DR).shift(LEFT * 0.2 + UP * 0.2)

        progress = ValueTracker(0)
        bar_bg = RoundedRectangle(width=12.2, height=0.10, corner_radius=0.04, color="#dae2ec", fill_opacity=1)
        bar_bg.to_edge(DOWN).shift(UP * 0.32)
        bar = always_redraw(
            lambda: Rectangle(
                width=max(0.001, 12.2 * progress.get_value()),
                height=0.10,
                color="#238c64",
                fill_opacity=1,
                stroke_width=0,
            )
            .align_to(bar_bg, LEFT)
            .move_to(bar_bg.get_center(), aligned_edge=LEFT)
        )

        def set_step(title_text: str, lines: list[str]) -> AnimationGroup:
            nonlocal step_title, step_body
            new_title = Text(title_text, font="Arial", weight=BOLD, font_size=31, color="#1a212e")
            new_title.to_corner(UR).shift(LEFT * 0.25 + DOWN * 0.12)
            new_body = VGroup(
                *[
                    Text(line_text, font="Arial", font_size=23, color="#1a212e")
                    for line_text in lines
                ]
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.23)
            new_body.next_to(new_title, DOWN, aligned_edge=LEFT, buff=0.35)
            animation = AnimationGroup(
                FadeOut(step_title, shift=UP * 0.1),
                FadeOut(step_body, shift=UP * 0.1),
                FadeIn(new_title, shift=UP * 0.1),
                FadeIn(new_body, shift=UP * 0.1),
                lag_ratio=0.0,
            )
            step_title = new_title
            step_body = new_body
            return animation

        audio_file = Path(AUDIO_PATH)
        if audio_file.exists():
            self.add_sound(str(audio_file))

        self.add(bar_bg, bar)
        self.play(
            FadeIn(title, shift=DOWN * 0.15),
            FadeIn(subtitle, shift=DOWN * 0.15),
            progress.animate.set_value(0.03),
            run_time=5,
        )
        self.play(
            set_step(
                "Đề bài",
                [
                    "Tam giác ABC ngoại tiếp đường tròn (I)",
                    "D, E, F là các tiếp điểm",
                    "K, L là chân vuông góc trên đường qua I song song EF",
                ],
            ),
            Create(triangle),
            Create(incircle),
            FadeIn(base_points),
            progress.animate.set_value(0.16),
            run_time=39,
        )
        self.play(
            set_step(
                "Dựng đường phụ",
                [
                    "Vẽ EF và đường qua I song song EF",
                    "Hạ BK và CL vuông góc với đường này",
                    "Ba mục tiêu chứng minh được tô màu",
                ],
            ),
            Create(ef),
            Create(ki),
            Create(bk),
            Create(cl),
            FadeIn(kl_points),
            progress.animate.set_value(0.29),
            run_time=36,
        )
        self.play(
            set_step(
                "Phần 1: DK song song IC",
                [
                    "EF song song KI cho các góc tương ứng",
                    "BKID nội tiếp vì có hai góc vuông",
                    "Suy ra góc BDK bằng góc ICD",
                ],
            ),
            Create(dk),
            Create(ic),
            Indicate(dk, color="#c8373c"),
            Indicate(ic, color="#c8373c"),
            progress.animate.set_value(0.46),
            run_time=47,
        )
        self.play(
            set_step(
                "Phần 2: KF và EL",
                [
                    "B, K, F, I, D đồng viên",
                    "I, E, L, D, C đồng viên",
                    "J, E, L thẳng hàng nên giao điểm nằm trên (I)",
                ],
            ),
            Create(kf),
            Create(el),
            Circumscribe(incircle, color="#6e4baa"),
            progress.animate.set_value(0.68),
            run_time=61,
        )
        self.play(
            set_step(
                "Phần 3: M, N, P, S",
                [
                    "DK và DL cắt lại (I) tại M, N",
                    "E, I, M và F, I, N thẳng hàng",
                    "MNEF là hình chữ nhật",
                ],
            ),
            Create(dl),
            Create(mn),
            Create(me),
            Create(nf),
            FadeIn(extra_points),
            progress.animate.set_value(0.88),
            run_time=55,
        )
        self.play(
            set_step(
                "Kết luận",
                [
                    "Dùng IX · IA = IE² = IS · ID",
                    "Tam giác AIS đồng dạng tam giác DIY",
                    "PDYI nội tiếp đường tròn đường kính PI",
                ],
            ),
            Create(ds),
            Create(pi),
            Create(ass),
            FadeIn(conclusion, shift=UP * 0.2),
            progress.animate.set_value(1.0),
            run_time=32,
        )
        self.play(Circumscribe(conclusion, color="#c8373c"), run_time=3)

        elapsed = 5 + 39 + 36 + 47 + 61 + 55 + 32 + 3
        remaining = max(0, AUDIO_DURATION - elapsed)
        if remaining > 0.01:
            self.wait(remaining)
