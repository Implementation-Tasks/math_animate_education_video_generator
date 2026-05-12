from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import *

from geometric_construction import (
    Point,
    build_construction,
    circle_line_intersections,
    distance,
    other_than,
)


AUDIO_PATH = "sourcecompile_mathspeech.mp3"
VTT_PATH = "sourcecompile_mathspeech.vtt"
AUDIO_DURATION = 275.328

INK = "#1a212e"
MUTED = "#607082"
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
        cues.append(
            Cue(
                index=int(lines[0]),
                start=parse_time(start_raw),
                end=parse_time(end_raw),
                text=" ".join(lines[2:]).strip(),
            )
        )
    return cues


def circumcircle_raw(a: Point, b: Point, c: Point) -> tuple[Point, float]:
    d = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
    ux = (
        (a.x * a.x + a.y * a.y) * (b.y - c.y)
        + (b.x * b.x + b.y * b.y) * (c.y - a.y)
        + (c.x * c.x + c.y * c.y) * (a.y - b.y)
    ) / d
    uy = (
        (a.x * a.x + a.y * a.y) * (c.x - b.x)
        + (b.x * b.x + b.y * b.y) * (a.x - c.x)
        + (c.x * c.x + c.y * c.y) * (b.x - a.x)
    ) / d
    center = Point(ux, uy)
    return center, distance(center, a)


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
    17: "A phía trên, B,C ∈ BC",
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


class SymbolicFullGeometryAnimation(Scene):
    def construct(self) -> None:
        self.camera.background_color = "#f7f9fc"
        cues = parse_vtt(Path(VTT_PATH))
        data = build_construction()
        raw = {name: Point(*xy) for name, xy in data["points"].items()}
        radius = float(data["radius"])
        raw["J"] = other_than(
            circle_line_intersections(raw["I"], radius, raw["K"], raw["F"]),
            raw["F"],
        )

        def pos(name: str) -> np.ndarray:
            point = raw[name]
            return np.array([point.x * 0.84 - 1.8, point.y * 0.84 - 2.46, 0.0])

        def mapped(point: Point) -> np.ndarray:
            return np.array([point.x * 0.84 - 1.8, point.y * 0.84 - 2.46, 0.0])

        def line(a: str, b: str, color=INK, width=4, dashed=False) -> VMobject:
            if dashed:
                return DashedLine(pos(a), pos(b), color=color, stroke_width=width)
            return Line(pos(a), pos(b), color=color, stroke_width=width)

        def dot_label(name: str, color=INK, direction=UP) -> VGroup:
            return VGroup(
                Dot(pos(name), radius=0.045, color=color),
                Text(name, font="Arial", font_size=19, color=color).next_to(
                    pos(name), direction, buff=0.06
                ),
            )

        def angle_mark(a: str, vertex: str, b: str, color=RED, label: str | None = None) -> VGroup:
            l1 = Line(pos(vertex), pos(a))
            l2 = Line(pos(vertex), pos(b))
            angle = Angle(l1, l2, radius=0.23, color=color, stroke_width=4)
            group = VGroup(angle)
            if label:
                text = Text(label, font="Arial", font_size=18, color=color)
                text.next_to(angle, UP, buff=0.03)
                group.add(text)
            return group

        def right_angle(a: str, vertex: str, b: str, color=RED) -> RightAngle:
            return RightAngle(Line(pos(vertex), pos(a)), Line(pos(vertex), pos(b)), length=0.16, color=color)

        def raw_circle(names: tuple[str, str, str], color: str) -> Circle:
            center, raw_radius = circumcircle_raw(*(raw[name] for name in names))
            return Circle(radius=raw_radius * 0.84, color=color, stroke_width=4).move_to(mapped(center))

        triangle = VGroup(
            line("A", "B", BLUE),
            line("B", "C", BLUE),
            line("C", "A", BLUE),
            dot_label("A", direction=UP),
            dot_label("B", direction=DL),
            dot_label("C", direction=DR),
        )
        incircle = VGroup(
            Circle(radius=radius * 0.84, color=GREEN, stroke_width=4).move_to(pos("I")),
            dot_label("I", GREEN, RIGHT),
        )
        contacts = VGroup(dot_label("D", direction=DOWN), dot_label("E", direction=RIGHT), dot_label("F", direction=LEFT))
        ef = line("E", "F", ORANGE, 5)
        ki = VGroup(line("K", "L", ORANGE, 5), dot_label("K", ORANGE, LEFT), dot_label("L", ORANGE, RIGHT))
        feet = VGroup(line("B", "K", MUTED, 3, dashed=True), line("C", "L", MUTED, 3, dashed=True), right_angle("B", "K", "I", ORANGE), right_angle("C", "L", "I", ORANGE))
        dk_ic = VGroup(line("D", "K", RED, 5), line("I", "C", RED, 5, dashed=True))
        dl_ib = VGroup(line("D", "L", RED, 4), line("I", "B", RED, 4, dashed=True))
        kf_el = VGroup(line("K", "F", PURPLE, 5), line("E", "L", PURPLE, 5), dot_label("J", PURPLE, UR))
        mn_group = VGroup(line("D", "M", RED, 4), line("D", "N", RED, 4), line("M", "N", PURPLE, 5), dot_label("M", direction=DL), dot_label("N", direction=DR))
        p_group = VGroup(dot_label("P", direction=DOWN))
        ds_group = VGroup(line("D", "S", GREEN, 4), dot_label("S", direction=UP))
        as_pi = VGroup(line("A", "S", RED, 5), line("P", "I", RED, 5), right_angle("A", "I", "P", RED))
        xy_group = VGroup(dot_label("X", direction=LEFT), dot_label("Y", direction=RIGHT), line("M", "E", MUTED, 3, dashed=True), line("N", "F", MUTED, 3, dashed=True), line("A", "I", MUTED, 3, dashed=True))
        rect_mnef = VGroup(line("M", "N", PURPLE, 4), line("N", "F", PURPLE, 4), line("F", "E", PURPLE, 4), line("E", "M", PURPLE, 4))
        tri_ais = Polygon(pos("A"), pos("I"), pos("S"), color=RED, stroke_width=4, fill_opacity=0.08)
        tri_diy = Polygon(pos("D"), pos("I"), pos("Y"), color=PURPLE, stroke_width=4, fill_opacity=0.08)

        circle_bkid = raw_circle(("B", "K", "I"), ORANGE)
        circle_ieldc = raw_circle(("I", "E", "D"), PURPLE)
        circle_pdyi = raw_circle(("P", "D", "Y"), GREEN)
        circle_bi = Circle(radius=np.linalg.norm(pos("B") - pos("I")) / 2, color=ORANGE, stroke_width=4).move_to((pos("B") + pos("I")) / 2)
        circle_pi = Circle(radius=np.linalg.norm(pos("P") - pos("I")) / 2, color=GREEN, stroke_width=4).move_to((pos("P") + pos("I")) / 2)

        angles_1 = VGroup(angle_mark("K", "I", "F", RED, "∠KIF"), angle_mark("I", "F", "E", RED, "∠IFE"), angle_mark("I", "E", "F", RED, "∠IEF"))
        angle_chain_1 = VGroup(angle_mark("K", "I", "B", RED, "∠KIB"), angle_mark("B", "I", "F", PURPLE, "∠BIF"), angle_mark("F", "E", "D", ORANGE, "∠FED"), angle_mark("I", "C", "D", GREEN, "∠ICD"))
        angles_2 = VGroup(angle_mark("J", "E", "D", RED, "∠JED"), angle_mark("K", "F", "D", PURPLE, "∠KFD"), angle_mark("K", "I", "D", ORANGE, "∠KID"), angle_mark("D", "E", "L", GREEN, "∠DEL"), angle_mark("D", "I", "L", GREEN, "∠DIL"))
        angles_3 = VGroup(angle_mark("A", "I", "S", RED, "∠AIS"), angle_mark("D", "I", "Y", PURPLE, "∠DIY"), angle_mark("S", "A", "I", RED, "∠SAI"), angle_mark("I", "D", "Y", PURPLE, "∠IDY"), angle_mark("I", "P", "Y", GREEN, "∠IPY"), angle_mark("I", "A", "S", GREEN, "∠IAS"))
        right_marks = VGroup(right_angle("B", "F", "I", ORANGE), right_angle("B", "K", "I", ORANGE), right_angle("B", "D", "I", ORANGE), right_angle("I", "C", "D", RED), right_angle("K", "D", "E", RED), right_angle("I", "Y", "P", GREEN), right_angle("I", "D", "P", GREEN))

        segments_formula = VGroup(
            line("I", "X", RED, 6),
            line("I", "A", BLUE, 6),
            line("I", "E", GREEN, 6),
            line("I", "S", PURPLE, 6),
            line("I", "D", ORANGE, 6),
            line("I", "Y", RED, 6),
        )

        objects = {
            "triangle": triangle,
            "incircle": incircle,
            "contacts": contacts,
            "ef": ef,
            "ki": ki,
            "feet": feet,
            "dk_ic": dk_ic,
            "dl_ib": dl_ib,
            "kf_el": kf_el,
            "mn": mn_group,
            "p": p_group,
            "ds": ds_group,
            "as_pi": as_pi,
            "xy": xy_group,
            "rect_mnef": rect_mnef,
            "tri_sim": VGroup(tri_ais, tri_diy),
            "circle_bkid": circle_bkid,
            "circle_ieldc": circle_ieldc,
            "circle_pdyi": circle_pdyi,
            "circle_bi": circle_bi,
            "circle_pi": circle_pi,
            "angles_1": angles_1,
            "angle_chain_1": angle_chain_1,
            "angles_2": angles_2,
            "angles_3": angles_3,
            "right_marks": right_marks,
            "segments_formula": segments_formula,
        }

        base_order = {
            2: ["triangle"],
            3: ["incircle"],
            4: ["contacts"],
            5: ["ef", "ki", "feet"],
            11: ["dk_ic", "dl_ib", "mn"],
            12: ["p"],
            13: ["ds"],
            14: ["as_pi"],
            28: ["angles_1"],
            34: ["right_marks"],
            35: ["circle_bkid"],
            39: ["kf_el"],
            40: ["circle_bi"],
            47: ["circle_ieldc"],
            56: ["xy"],
            62: ["rect_mnef"],
            66: ["segments_formula"],
            70: ["tri_sim"],
            74: ["circle_pdyi", "circle_pi"],
        }

        highlight_map = {
            2: ["triangle"],
            3: ["incircle"],
            4: ["contacts"],
            5: ["ef", "ki", "feet"],
            7: ["dk_ic"],
            9: ["kf_el", "incircle"],
            11: ["dk_ic", "dl_ib", "mn"],
            12: ["mn", "p"],
            13: ["ds"],
            14: ["as_pi"],
            17: ["triangle"],
            18: ["incircle", "contacts"],
            19: ["ef", "ki"],
            20: ["feet"],
            21: ["mn"],
            22: ["p"],
            23: ["ds"],
            24: ["as_pi"],
            28: ["ef", "ki", "angles_1"],
            30: ["angle_chain_1"],
            31: ["angle_chain_1"],
            32: ["angle_chain_1"],
            33: ["angle_chain_1"],
            34: ["right_marks"],
            35: ["circle_bkid"],
            36: ["dk_ic", "angle_chain_1"],
            37: ["dk_ic"],
            39: ["kf_el"],
            40: ["circle_bi", "right_marks"],
            41: ["circle_bkid"],
            42: ["kf_el", "incircle"],
            44: ["angles_2"],
            45: ["angles_2"],
            46: ["angles_2"],
            47: ["circle_ieldc"],
            48: ["angles_2"],
            49: ["angles_2"],
            51: ["angles_2"],
            52: ["angles_2"],
            53: ["angles_2"],
            54: ["kf_el"],
            55: ["kf_el", "incircle"],
            57: ["as_pi"],
            58: ["dk_ic", "contacts"],
            59: ["right_marks", "dk_ic"],
            60: ["xy"],
            61: ["xy"],
            62: ["rect_mnef"],
            63: ["xy"],
            64: ["segments_formula"],
            66: ["segments_formula"],
            68: ["segments_formula"],
            69: ["angles_3"],
            70: ["tri_sim"],
            71: ["angles_3"],
            72: ["xy"],
            73: ["right_marks"],
            74: ["circle_pdyi", "circle_pi"],
            75: ["angles_3"],
            76: ["as_pi"],
        }

        title = Text("Chứng minh hình học bằng ký hiệu", font="Arial", weight=BOLD, font_size=32, color=INK)
        title.to_edge(UP).shift(LEFT * 2.35)
        subtitle = Text("Animation đồng bộ theo từng timestamp của audio", font="Arial", font_size=20, color=MUTED)
        subtitle.next_to(title, DOWN, aligned_edge=LEFT, buff=0.08)
        self.add(title, subtitle)

        panel = RoundedRectangle(width=5.95, height=1.75, corner_radius=0.08, color="#d8e1ec", fill_color=WHITE, fill_opacity=0.88)
        panel.to_corner(UR).shift(DOWN * 0.76 + LEFT * 0.08)
        panel.set_z_index(20)
        formula_mob = Text("", font="DejaVu Sans", font_size=28, color=INK)
        formula_mob.move_to(panel.get_center())
        formula_mob.set_z_index(22)
        section_mob = Text("", font="Arial", weight=BOLD, font_size=26, color=BLUE)
        section_mob.next_to(panel, UP, aligned_edge=LEFT, buff=0.16)
        section_mob.set_z_index(22)
        self.add(panel, formula_mob, section_mob)

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
            )
            .align_to(bar_bg, LEFT)
            .move_to(bar_bg.get_center(), aligned_edge=LEFT)
        )
        self.add(bar_bg, bar)

        for obj in objects.values():
            obj.set_z_index(5)

        if Path(AUDIO_PATH).exists():
            self.add_sound(AUDIO_PATH)

        visible: set[str] = set()
        current_time = 0.0

        def section_for(cue_index: int) -> str:
            if cue_index < 15:
                return "Đề bài"
            if cue_index < 25:
                return "Dựng hình"
            if cue_index < 38:
                return "Lời giải: phần 1"
            if cue_index < 56:
                return "Lời giải: phần 2"
            return "Lời giải: phần 3"

        def wrap_formula(text: str, max_chars: int = 32) -> str:
            tokens = text.split()
            lines: list[str] = []
            current = ""
            for token in tokens:
                candidate = f"{current} {token}".strip()
                if current and len(candidate) > max_chars:
                    lines.append(current)
                    current = token
                else:
                    current = candidate
            if current:
                lines.append(current)
            return "\n".join(lines[:3])

        for pos_index, cue in enumerate(cues):
            if cue.start > current_time + 0.001:
                self.play(
                    progress.animate.set_value(cue.start / AUDIO_DURATION),
                    run_time=cue.start - current_time,
                    rate_func=linear,
                )
                current_time = cue.start

            new_formula = Text(
                wrap_formula(FORMULAS.get(cue.index, cue.text)),
                font="DejaVu Sans",
                font_size=28,
                color=INK,
                line_spacing=0.82,
            )
            new_formula.move_to(panel.get_center())
            new_formula.set_z_index(22)
            new_section = Text(section_for(cue.index), font="Arial", weight=BOLD, font_size=26, color=BLUE)
            new_section.next_to(panel, UP, aligned_edge=LEFT, buff=0.16)
            new_section.set_z_index(22)
            self.remove(formula_mob, section_mob)
            formula_mob = new_formula
            section_mob = new_section
            self.add(formula_mob, section_mob)

            animations: list[Animation] = []
            for appear_index, keys in base_order.items():
                if cue.index >= appear_index:
                    for key in keys:
                        if key not in visible:
                            visible.add(key)
                            animations.append(FadeIn(objects[key], shift=UP * 0.05))

            for key in highlight_map.get(cue.index, []):
                if key in visible:
                    animations.append(Indicate(objects[key], color=YELLOW, scale_factor=1.03))
            animations.append(Indicate(formula_mob, color=YELLOW, scale_factor=1.03))

            next_start = cues[pos_index + 1].start if pos_index + 1 < len(cues) else AUDIO_DURATION
            duration = max(0.05, next_start - cue.start)
            animations.append(progress.animate.set_value(min(next_start / AUDIO_DURATION, 1.0)))
            self.play(*animations, run_time=duration, rate_func=linear)
            current_time = next_start

        if current_time < AUDIO_DURATION:
            self.play(progress.animate.set_value(1), run_time=AUDIO_DURATION - current_time, rate_func=linear)
