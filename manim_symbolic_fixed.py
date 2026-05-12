from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import *

from geometric_construction import Point, build_construction, circle_line_intersections, line_intersection, other_than


AUDIO_PATH = "sourcecompile_mathspeech.mp3"
VTT_PATH = "sourcecompile_mathspeech.vtt"
AUDIO_DURATION = 275.328
FONT = "DejaVu Sans"
ANGLE_RE = re.compile(r"∠([A-Z]{3})")

INK = "#18202c"
MUTED = "#5e6e80"
BLUE = "#235bae"
GREEN = "#238c64"
ORANGE = "#d2781e"
RED = "#c8373c"
PURPLE = "#6e4baa"


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
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    cues: list[Cue] = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        start_raw, end_raw = [part.strip() for part in lines[1].split("-->")]
        cues.append(Cue(int(lines[0]), parse_time(start_raw), parse_time(end_raw), " ".join(lines[2:])))
    return cues


FORMULAS = {
    1: "ĐỀ BÀI",
    2: "ΔABC nhọn, AB < AC, AB ≠ AC",
    3: "ΔABC ngoại tiếp (I)",
    4: "(I) tiếp xúc BC, CA, AB tại D, E, F",
    5: "KI ∥ EF; BK ⊥ KI; CL ⊥ KI",
    6: "Phần 1",
    7: "Chứng minh: DK ∥ IC",
    8: "Phần 2",
    9: "Chứng minh: KF ∩ EL = J ∈ (I)",
    10: "Phần 3",
    11: "M = DK ∩ (I), N = DL ∩ (I), M,N ≠ D",
    12: "P = MN ∩ BC",
    13: "DS là đường kính của (I)",
    14: "Chứng minh: PI ⊥ AS",
    15: "HÌNH VẼ",
    16: "Dựng toàn bộ cấu hình",
    17: "A phía trên; B,C ∈ BC",
    18: "D ∈ BC, E ∈ CA, F ∈ AB",
    19: "Qua I kẻ KL ∥ EF",
    20: "BK ⊥ KL, CL ⊥ KL",
    21: "DK, DL cắt (I) tại M, N",
    22: "P = MN ∩ BC",
    23: "S đối xứng D qua I ⇒ DS là đường kính",
    24: "Mục tiêu cuối: PI ⊥ AS",
    25: "LỜI GIẢI",
    26: "Phần 1",
    27: "Chứng minh: DK ∥ IC",
    28: "EF ∥ KI ⇒ ∠KIF = ∠IFE = ∠IEF",
    29: "Suy ra",
    30: "∠KIB = ∠BIF − ∠KIF",
    31: "= ∠FED − ∠IEF",
    32: "= ∠IED",
    33: "= ∠ICD",
    34: "∠BKI = ∠BDI = 90°",
    35: "⇒ BKID nội tiếp",
    36: "∠BDK = ∠BIK = ∠ICD",
    37: "⇒ DK ∥ IC",
    38: "Phần 2",
    39: "Chứng minh: KF ∩ EL = J ∈ (I)",
    40: "∠BFI = 90° ⇒ F ∈ đường tròn đường kính BI",
    41: "⇒ B,K,F,I,D đồng viên",
    42: "J = KF ∩ (I)",
    43: "Ta có",
    44: "∠JED = 180° − ∠IFD",
    45: "= ∠KFD",
    46: "= ∠KID",
    47: "I,E,L,D,C đồng viên",
    48: "∠DEL = 180° − ∠DCL",
    49: "= ∠DIL",
    50: "Do đó",
    51: "∠JED + ∠DEL",
    52: "= ∠KID + ∠DIL",
    53: "= 180°",
    54: "⇒ J,E,L thẳng hàng",
    55: "⇒ KF và EL cắt nhau tại J ∈ (I)",
    56: "Phần 3",
    57: "Chứng minh: PI ⊥ AS",
    58: "KD ∥ IC và IC ⊥ ED",
    59: "⇒ KD ⊥ ED",
    60: "⇒ E,I,M thẳng hàng",
    61: "Tương tự: F,I,N thẳng hàng",
    62: "⇒ MNEF là hình chữ nhật",
    63: "X = AI ∩ EF, Y = AI ∩ MN",
    64: "IX = IY",
    65: "Hơn nữa",
    66: "IX · IA = IE² = IS · ID",
    67: "Suy ra",
    68: "IS / IA = IY / ID",
    69: "∠AIS = ∠DIY",
    70: "⇒ ΔAIS ∼ ΔDIY (c.g.c)",
    71: "⇒ ∠SAI = ∠IDY",
    72: "IA ⊥ MN",
    73: "∠IYP = ∠IDP = 90°",
    74: "⇒ PDYI nội tiếp đường tròn đường kính PI",
    75: "∠IPY = ∠IDY = ∠IAS",
    76: "⇒ AS ⊥ PI",
}


def wrap_text(text: str, max_chars: int = 34) -> str:
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


def angle_text(label: str, font_size: int, color=INK) -> VGroup:
    letters = Text(label, font=FONT, font_size=font_size, color=color)
    half_width = max(letters.width * 0.46, font_size / 85)
    height = max(letters.height * 0.28, font_size / 115)
    stroke_width = max(2, font_size / 9)
    hat = VGroup(
        Line(LEFT * half_width, UP * height, color=color, stroke_width=stroke_width),
        Line(UP * height, RIGHT * half_width, color=color, stroke_width=stroke_width),
    )
    hat.next_to(letters, UP, buff=0.01)
    return VGroup(letters, hat)


def formula_text(text: str, font_size: int, color=INK, line_spacing: float = 0.84) -> VGroup:
    lines = wrap_text(text).splitlines()
    rendered_lines = VGroup()
    for line_text in lines:
        pieces = VGroup()
        cursor = 0
        for match in ANGLE_RE.finditer(line_text):
            if match.start() > cursor:
                pieces.add(Text(line_text[cursor:match.start()], font=FONT, font_size=font_size, color=color))
            pieces.add(angle_text(match.group(1), font_size, color))
            cursor = match.end()
        if cursor < len(line_text):
            pieces.add(Text(line_text[cursor:], font=FONT, font_size=font_size, color=color))
        pieces.arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
        rendered_lines.add(pieces)
    rendered_lines.arrange(DOWN, buff=font_size / 60 * line_spacing)
    return rendered_lines


def section_for(index: int) -> str:
    if index < 15:
        return "Đề bài"
    if index < 25:
        return "Dựng hình"
    if index < 38:
        return "Lời giải: phần 1"
    if index < 56:
        return "Lời giải: phần 2"
    return "Lời giải: phần 3"


class SymbolicFixedGeometryAnimation(Scene):
    def construct(self) -> None:
        self.camera.background_color = "#f7f9fc"
        cues = parse_vtt(Path(VTT_PATH))
        data = build_construction()
        raw = {name: Point(*xy) for name, xy in data["points"].items()}
        radius = float(data["radius"])
        raw["J"] = other_than(circle_line_intersections(raw["I"], radius, raw["K"], raw["F"]), raw["F"])

        def pos(name: str) -> np.ndarray:
            p = raw[name]
            return np.array([p.x * 0.82 - 2.0, p.y * 0.82 - 2.35, 0.0])

        def line(a: str, b: str, color=INK, width=3.5, dashed=False) -> VMobject:
            cls = DashedLine if dashed else Line
            return cls(pos(a), pos(b), color=color, stroke_width=width)

        def dot_label(name: str, color=INK, direction=UP) -> VGroup:
            dot = Dot(pos(name), radius=0.045, color=color)
            label = Text(name, font=FONT, font_size=18, color=color).next_to(pos(name), direction, buff=0.055)
            return VGroup(dot, label)

        def angle_label(text: str, where: np.ndarray, color=RED) -> VGroup:
            match = ANGLE_RE.fullmatch(text)
            label = angle_text(match.group(1), 17, color) if match else Text(text, font=FONT, font_size=17, color=color)
            return label.move_to(where)

        def right_angle_at(line_1_a: str, line_1_b: str, line_2_a: str, line_2_b: str, color=RED) -> VGroup:
            cross = line_intersection(raw[line_1_a], raw[line_1_b], raw[line_2_a], raw[line_2_b])
            cross_pos = np.array([cross.x * 0.82 - 2.0, cross.y * 0.82 - 2.35, 0.0])
            first = Line(cross_pos, cross_pos + normalize(pos(line_1_a) - cross_pos), color=color)
            second = Line(cross_pos, cross_pos + normalize(pos(line_2_a) - cross_pos), color=color)
            return VGroup(
                Dot(cross_pos, radius=0.045, color=color),
                RightAngle(first, second, length=0.22, color=color, stroke_width=4),
            )

        triangle = VGroup(
            line("A", "B", BLUE, 4),
            line("B", "C", BLUE, 4),
            line("C", "A", BLUE, 4),
            dot_label("A", BLUE, UP),
            dot_label("B", BLUE, DL),
            dot_label("C", BLUE, DR),
        )
        incircle = VGroup(Circle(radius=radius * 0.82, color=GREEN, stroke_width=4).move_to(pos("I")), dot_label("I", GREEN, RIGHT))
        contacts = VGroup(dot_label("D", ORANGE, DOWN), dot_label("E", ORANGE, RIGHT), dot_label("F", ORANGE, LEFT))
        base_lines = VGroup(line("E", "F", ORANGE, 5), line("K", "L", ORANGE, 5), dot_label("K", ORANGE, LEFT), dot_label("L", ORANGE, RIGHT))
        perpendiculars = VGroup(
            line("B", "K", MUTED, 3, True),
            line("C", "L", MUTED, 3, True),
            RightAngle(Line(pos("K"), pos("B")), Line(pos("K"), pos("I")), length=0.15, color=ORANGE),
            RightAngle(Line(pos("L"), pos("C")), Line(pos("L"), pos("I")), length=0.15, color=ORANGE),
        )
        proof_1 = VGroup(line("D", "K", RED, 5), line("I", "C", RED, 4, True))
        proof_2 = VGroup(line("K", "F", PURPLE, 5), line("E", "L", PURPLE, 5), dot_label("J", PURPLE, UR))
        mn = VGroup(line("D", "M", RED, 4), line("D", "N", RED, 4), line("M", "N", PURPLE, 5), dot_label("M", PURPLE, DL), dot_label("N", PURPLE, DR))
        p_ds = VGroup(dot_label("P", GREEN, DOWN), line("D", "S", GREEN, 4), dot_label("S", GREEN, UP))
        final_lines = VGroup(line("A", "S", RED, 5), line("P", "I", RED, 5), right_angle_at("A", "S", "P", "I", RED))
        xy = VGroup(dot_label("X", PURPLE, LEFT), dot_label("Y", PURPLE, RIGHT), line("A", "I", MUTED, 3, True), line("M", "E", MUTED, 3, True), line("N", "F", MUTED, 3, True))
        rect = VGroup(line("M", "N", PURPLE, 4), line("N", "F", PURPLE, 4), line("F", "E", PURPLE, 4), line("E", "M", PURPLE, 4))
        angles = VGroup(
            angle_label("∠KIF", pos("I") + UP * 0.35, RED),
            angle_label("∠IFE", pos("F") + LEFT * 0.35, RED),
            angle_label("∠IEF", pos("E") + RIGHT * 0.35, RED),
            angle_label("∠ICD", pos("C") + UP * 0.28, GREEN),
            angle_label("∠KID", pos("I") + LEFT * 0.45, ORANGE),
            angle_label("∠IDY", pos("D") + UP * 0.35, PURPLE),
            angle_label("∠IPY", pos("P") + DOWN * 0.35, GREEN),
        )
        circles = VGroup(
            Circle(radius=np.linalg.norm(pos("B") - pos("I")) / 2, color=ORANGE, stroke_width=3).move_to((pos("B") + pos("I")) / 2),
            Circle(radius=np.linalg.norm(pos("P") - pos("I")) / 2, color=GREEN, stroke_width=3).move_to((pos("P") + pos("I")) / 2),
        )

        objects = {
            "triangle": triangle,
            "incircle": incircle,
            "contacts": contacts,
            "base_lines": base_lines,
            "perpendiculars": perpendiculars,
            "proof_1": proof_1,
            "proof_2": proof_2,
            "mn": mn,
            "p_ds": p_ds,
            "final_lines": final_lines,
            "xy": xy,
            "rect": rect,
            "angles": angles,
            "circles": circles,
        }
        for obj in objects.values():
            obj.set_z_index(5)

        show_at = {
            2: ["triangle"],
            3: ["incircle"],
            4: ["contacts"],
            5: ["base_lines", "perpendiculars"],
            7: ["proof_1"],
            9: ["proof_2"],
            11: ["mn"],
            13: ["p_ds"],
            14: ["final_lines"],
            28: ["angles"],
            40: ["circles"],
            56: ["xy"],
            62: ["rect"],
        }
        highlights = {
            5: ["base_lines", "perpendiculars"],
            7: ["proof_1"],
            9: ["proof_2"],
            11: ["mn"],
            14: ["final_lines"],
            28: ["base_lines", "angles"],
            37: ["proof_1"],
            55: ["proof_2"],
            62: ["rect"],
            66: ["xy"],
            74: ["circles"],
            76: ["final_lines"],
        }

        title = Text("Chứng minh hình học bằng ký hiệu", font=FONT, weight=BOLD, font_size=32, color=INK)
        title.to_edge(UP).shift(LEFT * 2.35)
        subtitle = Text("Animation đồng bộ theo từng timestamp của audio", font=FONT, font_size=20, color=MUTED)
        subtitle.next_to(title, DOWN, aligned_edge=LEFT, buff=0.08)
        self.add(title, subtitle)

        panel = RoundedRectangle(width=5.95, height=1.75, corner_radius=0.08, color="#d8e1ec", fill_color=WHITE, fill_opacity=0.9)
        panel.to_corner(UR).shift(DOWN * 1.05 + LEFT * 0.08)
        panel.set_z_index(20)
        formula_mob = Text("", font=FONT, font_size=27, color=INK)
        section_mob = Text("", font=FONT, weight=BOLD, font_size=25, color=BLUE)
        self.add(panel)

        progress = ValueTracker(0)
        bar_bg = RoundedRectangle(width=12.2, height=0.10, corner_radius=0.04, color="#d8e1ec", fill_opacity=1)
        bar_bg.to_edge(DOWN).shift(UP * 0.25)
        bar = always_redraw(
            lambda: Rectangle(
                width=max(0.001, 12.2 * progress.get_value()),
                height=0.10,
                stroke_width=0,
                fill_opacity=1,
                color=GREEN,
            ).align_to(bar_bg, LEFT).move_to(bar_bg.get_center(), aligned_edge=LEFT)
        )
        self.add(bar_bg, bar)

        if Path(AUDIO_PATH).exists():
            self.add_sound(AUDIO_PATH)

        visible: set[str] = set()
        current_time = 0.0
        for i, cue in enumerate(cues):
            if cue.start > current_time + 0.001:
                self.play(progress.animate.set_value(cue.start / AUDIO_DURATION), run_time=cue.start - current_time, rate_func=linear)
                current_time = cue.start

            self.remove(formula_mob, section_mob)
            formula_mob = formula_text(FORMULAS.get(cue.index, cue.text), font_size=27, color=INK, line_spacing=0.84)
            formula_mob.move_to(panel.get_center() + DOWN * 0.16).set_z_index(22)
            section_mob = Text(section_for(cue.index), font=FONT, weight=BOLD, font_size=25, color=BLUE)
            section_mob.align_to(panel, LEFT).shift(RIGHT * 0.18)
            section_mob.move_to([section_mob.get_center()[0], panel.get_top()[1] - 0.23, 0])
            section_mob.set_z_index(22)
            self.add(formula_mob, section_mob)

            animations: list[Animation] = []
            for index, keys in show_at.items():
                if cue.index >= index:
                    for key in keys:
                        if key not in visible:
                            visible.add(key)
                            self.add(objects[key])
                            animations.append(Circumscribe(objects[key], color=YELLOW, buff=0.04))
            for key in highlights.get(cue.index, []):
                if key in visible:
                    animations.append(Circumscribe(objects[key], color=YELLOW, buff=0.04))
            animations.append(Indicate(formula_mob, color=YELLOW, scale_factor=1.02))

            next_start = cues[i + 1].start if i + 1 < len(cues) else AUDIO_DURATION
            duration = max(0.05, next_start - cue.start)
            animations.append(progress.animate.set_value(min(next_start / AUDIO_DURATION, 1.0)))
            self.play(*animations, run_time=duration, rate_func=linear)
            current_time = next_start

        if current_time < AUDIO_DURATION:
            self.play(progress.animate.set_value(1), run_time=AUDIO_DURATION - current_time, rate_func=linear)
