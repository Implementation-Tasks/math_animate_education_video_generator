from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import *

from geometric_construction import build_construction, circle_line_intersections, other_than, Point


AUDIO_PATH = "sourcecompile_mathspeech.mp3"
VTT_PATH = "sourcecompile_mathspeech.vtt"
AUDIO_DURATION = 275.328


@dataclass(frozen=True)
class Cue:
    index: int
    start: float
    end: float
    text: str


def parse_time(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def parse_vtt(path: Path) -> list[Cue]:
    content = path.read_text(encoding="utf-8").strip()
    blocks = re.split(r"\n\s*\n", content)
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        start_raw, end_raw = [part.strip() for part in lines[1].split("-->")]
        cues.append(
            Cue(
                index=int(lines[0]),
                start=parse_time(start_raw),
                end=parse_time(end_raw),
                text=" ".join(lines[2:]).strip(),
            )
        )
    return cues


class TimestampSyncedGeometryAnimation(Scene):
    def construct(self) -> None:
        self.camera.background_color = "#f7f9fc"
        cues = parse_vtt(Path(VTT_PATH))
        data = build_construction()
        raw = data["points"]
        radius = float(data["radius"])

        i_raw = Point(*raw["I"])
        incircle_radius = radius
        j_raw = other_than(
            circle_line_intersections(i_raw, incircle_radius, Point(*raw["K"]), Point(*raw["F"])),
            Point(*raw["F"]),
        )
        raw["J"] = j_raw.as_tuple()

        def p(name: str) -> np.ndarray:
            x, y = raw[name]
            return np.array([x * 0.88 - 1.8, y * 0.88 - 2.52, 0.0])

        def make_line(a: str, b: str, color: str, width: int = 4, dashed: bool = False) -> VMobject:
            if dashed:
                return DashedLine(p(a), p(b), color=color, stroke_width=width)
            return Line(p(a), p(b), color=color, stroke_width=width)

        def make_dot(name: str, color: str = "#1a212e", direction=UP) -> VGroup:
            return VGroup(
                Dot(p(name), radius=0.045, color=color),
                Text(name, font="Arial", font_size=20, color=color).next_to(p(name), direction, buff=0.07),
            )

        objects: dict[str, Mobject] = {
            "triangle": VGroup(
                Polygon(p("A"), p("B"), p("C"), color="#235bae", stroke_width=4, fill_opacity=0.03),
                make_line("A", "B", "#235bae"),
                make_line("B", "C", "#235bae"),
                make_line("C", "A", "#235bae"),
                make_dot("A", direction=UP),
                make_dot("B", direction=DL),
                make_dot("C", direction=DR),
            ),
            "incircle": VGroup(
                Circle(radius=radius * 0.88, color="#238c64", stroke_width=4).move_to(p("I")),
                make_dot("I", "#238c64", RIGHT),
            ),
            "contacts": VGroup(make_dot("D", direction=DOWN), make_dot("E", direction=RIGHT), make_dot("F", direction=LEFT)),
            "ef": make_line("E", "F", "#d2781e", 4),
            "kl": VGroup(make_line("K", "L", "#d2781e", 4), make_dot("K", "#d2781e", LEFT), make_dot("L", "#d2781e", RIGHT)),
            "bkcl": VGroup(make_line("B", "K", "#607082", 3, dashed=True), make_line("C", "L", "#607082", 3, dashed=True)),
            "dk_ic": VGroup(make_line("D", "K", "#c8373c", 5), make_line("I", "C", "#c8373c", 5, dashed=True)),
            "kf_el": VGroup(make_line("K", "F", "#6e4baa", 5), make_line("E", "L", "#6e4baa", 5), make_dot("J", "#6e4baa", UR)),
            "mn": VGroup(make_line("D", "M", "#c8373c", 4), make_line("D", "N", "#c8373c", 4), make_line("M", "N", "#6e4baa", 5), make_dot("M", direction=DL), make_dot("N", direction=DR)),
            "p": VGroup(make_dot("P", direction=DOWN)),
            "ds": VGroup(make_line("D", "S", "#238c64", 4), make_dot("S", direction=UP)),
            "as_pi": VGroup(make_line("A", "S", "#c8373c", 5), make_line("P", "I", "#c8373c", 5)),
            "x_y": VGroup(make_dot("X", direction=LEFT), make_dot("Y", direction=RIGHT), make_line("M", "E", "#607082", 3, dashed=True), make_line("N", "F", "#607082", 3, dashed=True)),
        }

        title = Text("Animation đồng bộ timestamp", font="Arial", weight=BOLD, font_size=34, color="#1a212e")
        title.to_edge(UP).shift(LEFT * 3.0)
        subtitle = Text("Nguồn mốc: sourcecompile_mathspeech.vtt", font="Arial", font_size=21, color="#607082")
        subtitle.next_to(title, DOWN, aligned_edge=LEFT, buff=0.08)
        self.add(title, subtitle)

        caption_box = RoundedRectangle(width=5.7, height=1.65, corner_radius=0.08, color="#d8e1ec", fill_color=WHITE, fill_opacity=0.82)
        caption_box.to_corner(UR).shift(DOWN * 0.75 + LEFT * 0.15)
        caption = Text("", font="Arial", font_size=25, color="#1a212e", line_spacing=0.88)
        caption.move_to(caption_box.get_center())
        section_label = Text("", font="Arial", weight=BOLD, font_size=28, color="#235bae")
        section_label.next_to(caption_box, UP, aligned_edge=LEFT, buff=0.18)
        self.add(caption_box, caption, section_label)

        progress = ValueTracker(0)
        bar_bg = RoundedRectangle(width=12.2, height=0.10, corner_radius=0.04, color="#d8e1ec", fill_opacity=1)
        bar_bg.to_edge(DOWN).shift(UP * 0.28)
        bar = always_redraw(
            lambda: Rectangle(
                width=max(0.001, 12.2 * progress.get_value()),
                height=0.10,
                stroke_width=0,
                fill_opacity=1,
                color="#238c64",
            )
            .align_to(bar_bg, LEFT)
            .move_to(bar_bg.get_center(), aligned_edge=LEFT)
        )
        self.add(bar_bg, bar)

        if Path(AUDIO_PATH).exists():
            self.add_sound(AUDIO_PATH)

        visible: set[str] = set()

        def desired_keys(cue_index: int) -> list[str]:
            keys = []
            if cue_index >= 2:
                keys.append("triangle")
            if cue_index >= 3:
                keys.append("incircle")
            if cue_index >= 4:
                keys.append("contacts")
            if cue_index >= 5:
                keys.extend(["ef", "kl", "bkcl"])
            if cue_index >= 21:
                keys.append("mn")
            if cue_index >= 22:
                keys.append("p")
            if cue_index >= 23:
                keys.append("ds")
            if cue_index >= 24:
                keys.append("as_pi")
            if 28 <= cue_index <= 37:
                keys.append("dk_ic")
            if 38 <= cue_index <= 55:
                keys.append("kf_el")
            if cue_index >= 56:
                keys.extend(["dk_ic", "x_y"])
            return keys

        def section_for(cue_index: int) -> str:
            if cue_index < 15:
                return "Đề bài"
            if cue_index < 25:
                return "Dựng hình"
            if cue_index < 38:
                return "Lời giải - Phần 1"
            if cue_index < 56:
                return "Lời giải - Phần 2"
            return "Lời giải - Phần 3"

        def wrap_text(text: str, max_chars: int = 42) -> str:
            words = text.split()
            lines: list[str] = []
            current = ""
            for word in words:
                candidate = f"{current} {word}".strip()
                if current and len(candidate) > max_chars:
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            if current:
                lines.append(current)
            return "\n".join(lines[:3])

        current_time = 0.0
        for cue_pos, cue in enumerate(cues):
            if cue.start > current_time + 0.001:
                gap = cue.start - current_time
                self.play(progress.animate.set_value(cue.start / AUDIO_DURATION), run_time=gap, rate_func=linear)
                current_time = cue.start

            new_caption = Text(wrap_text(cue.text), font="Arial", font_size=25, color="#1a212e", line_spacing=0.88)
            new_caption.move_to(caption_box.get_center())
            new_section = Text(section_for(cue.index), font="Arial", weight=BOLD, font_size=28, color="#235bae")
            new_section.next_to(caption_box, UP, aligned_edge=LEFT, buff=0.18)

            self.remove(caption, section_label)
            caption = new_caption
            section_label = new_section
            self.add(caption, section_label)

            animations: list[Animation] = []
            for key in desired_keys(cue.index):
                if key not in visible:
                    visible.add(key)
                    animations.append(Create(objects[key]) if isinstance(objects[key], (Line, DashedLine, Circle, VMobject)) else FadeIn(objects[key]))

            next_start = cues[cue_pos + 1].start if cue_pos + 1 < len(cues) else AUDIO_DURATION
            segment_duration = max(0.05, next_start - cue.start)
            progress_animation = progress.animate.set_value(min(next_start / AUDIO_DURATION, 1.0))
            if animations:
                self.play(*animations, progress_animation, run_time=segment_duration, rate_func=linear)
            else:
                self.play(progress_animation, run_time=segment_duration, rate_func=linear)
            current_time = next_start

        if current_time < AUDIO_DURATION:
            self.play(progress.animate.set_value(1.0), run_time=AUDIO_DURATION - current_time, rate_func=linear)
