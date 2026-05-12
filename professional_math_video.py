from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1080
HEIGHT = 1920
FPS = 10

BG = (248, 250, 252)
PANEL = (255, 255, 255)
INK = (25, 32, 44)
MUTED = (91, 104, 124)
GRID = (229, 235, 244)
BLUE = (34, 84, 170)
GREEN = (26, 137, 94)
ORANGE = (214, 125, 35)
RED = (200, 55, 64)
PURPLE = (112, 78, 170)


SLIDES = [
    {
        "start": 0.0,
        "end": 52.0,
        "kicker": "ĐỀ BÀI",
        "title": "Tam giác ngoại tiếp đường tròn (I)",
        "body": [
            "Tam giác ABC nhọn, không cân, AB < AC.",
            "(I) tiếp xúc BC, CA, AB lần lượt tại D, E, F.",
            "K, L là chân vuông góc từ B, C xuống đường thẳng qua I và song song EF.",
        ],
        "math": ["1. Chứng minh DK ∥ IC", "2. KF và EL cắt nhau trên (I)", "3. Với DS là đường kính, chứng minh PI ⟂ AS"],
        "features": ("triangle", "incircle", "contacts", "kl", "targets"),
    },
    {
        "start": 52.0,
        "end": 90.9,
        "kicker": "HÌNH VẼ",
        "title": "Các điểm và đường phụ",
        "body": [
            "D, E, F là các tiếp điểm của đường tròn nội tiếp.",
            "Đường qua I song song EF nhận K, L là hình chiếu của B, C.",
            "DK, DL cắt lại (I) tại M, N; MN cắt BC tại P; DS là đường kính.",
        ],
        "math": ["M ∈ DK ∩ (I),  N ∈ DL ∩ (I)", "P = MN ∩ BC", "S đối xứng với D qua I"],
        "features": ("triangle", "incircle", "contacts", "kl", "part3"),
    },
    {
        "start": 90.9,
        "end": 133.8,
        "kicker": "PHẦN 1",
        "title": "Chứng minh DK ∥ IC",
        "body": [
            "Từ EF ∥ KI, các góc tương ứng tạo bởi tiếp tuyến bằng nhau.",
            "Vì ∠BKI = ∠BDI = 90°, tứ giác BKID nội tiếp.",
            "Suy ra hai góc so le trong bằng nhau.",
        ],
        "math": ["∠KIF = ∠IFE = ∠IEF", "∠KIB = ∠IED = ∠ICD", "∠BDK = ∠BIK = ∠ICD  ⇒  DK ∥ IC"],
        "features": ("triangle", "incircle", "contacts", "kl", "part1"),
    },
    {
        "start": 133.8,
        "end": 197.3,
        "kicker": "PHẦN 2",
        "title": "KF và EL cắt nhau trên (I)",
        "body": [
            "F thuộc đường tròn đường kính BI, nên B, K, F, I, D đồng viên.",
            "Tương tự, I, E, L, D, C đồng viên.",
            "Gọi J là giao điểm của KF với (I); chứng minh J, E, L thẳng hàng.",
        ],
        "math": ["∠JED = 180° − ∠IFD = ∠KID", "∠DEL = 180° − ∠DCL = ∠DIL", "∠JED + ∠DEL = 180°  ⇒  J, E, L thẳng hàng"],
        "features": ("triangle", "incircle", "contacts", "kl", "part2"),
    },
    {
        "start": 197.3,
        "end": 250.5,
        "kicker": "PHẦN 3",
        "title": "Đồng dạng ΔAIS và ΔDIY",
        "body": [
            "Từ KD ∥ IC và IC ⟂ ED, suy ra KD ⟂ ED.",
            "Do đó E, I, M thẳng hàng; tương tự F, I, N thẳng hàng.",
            "MNEF là hình chữ nhật, nên với X, Y trên AI ta có IX = IY.",
        ],
        "math": ["IX · IA = IE² = IS · ID", "IS / IA = IY / ID", "∠AIS = ∠DIY  ⇒  ΔAIS ∼ ΔDIY"],
        "features": ("triangle", "incircle", "contacts", "part3"),
    },
    {
        "start": 250.5,
        "end": 276.0,
        "kicker": "KẾT LUẬN",
        "title": "Suy ra AS ⟂ PI",
        "body": [
            "Từ ΔAIS ∼ ΔDIY, suy ra ∠SAI = ∠IDY.",
            "Vì IA ⟂ MN nên ∠IYP = ∠IDP = 90°.",
            "Tứ giác PDYI nội tiếp đường tròn đường kính PI.",
        ],
        "math": ["∠IPY = ∠IDY = ∠IAS", "Vậy AS ⟂ PI"],
        "features": ("triangle", "incircle", "contacts", "part3", "conclusion"),
    },
]


def run(args: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def audio_duration(audio_path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture=True,
    )
    return float(result.stdout.strip())


def parse_vtt_time(value: str) -> float:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def polish_cue_text(text: str) -> str:
    text = re.sub(r"góc ([A-Z]) ([A-Z]) ([A-Z])", r"∠\1\2\3", text)
    text = re.sub(r"tam giác ([A-Z]) ([A-Z]) ([A-Z])", r"Δ\1\2\3", text, flags=re.IGNORECASE)
    replacements = [
        ("một trăm tám mươi độ", "180°"),
        ("chín mươi độ", "90°"),
        ("bình phương", "²"),
        ("nhỏ hơn", "<"),
        ("song song E F", "∥ EF"),
        ("song song với", "∥"),
        ("vuông góc với", "⟂"),
        ("đường tròn I", "đường tròn (I)"),
        ("A B C", "ABC"),
        ("A B", "AB"),
        ("A C", "AC"),
        ("B C", "BC"),
        ("C A", "CA"),
        ("D K", "DK"),
        ("K D", "KD"),
        ("D L", "DL"),
        ("K F", "KF"),
        ("E L", "EL"),
        ("M N", "MN"),
        ("D S", "DS"),
        ("E D", "ED"),
        ("B I", "BI"),
        ("B K", "BK"),
        ("B D", "BD"),
        ("K I D", "KID"),
        ("D I L", "DIL"),
        ("P I", "PI"),
        ("A S", "AS"),
        ("E F", "EF"),
        ("K I", "KI"),
        ("I C", "IC"),
        ("I D", "ID"),
        ("I E", "IE"),
        ("I S", "IS"),
        ("I A", "IA"),
        ("I X", "IX"),
        ("I Y", "IY"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"(∠[A-Z]{3}|[A-Z]{2}) bằng", r"\1 =", text)
    text = re.sub(r"trừ (∠[A-Z]{3}|[A-Z]{2})", r"− \1", text)
    text = re.sub(r"cộng (∠[A-Z]{3}|[A-Z]{2})", r"+ \1", text)
    text = re.sub(r"([A-Z]{2}) nhân ([A-Z]{2})", r"\1 · \2", text)
    text = re.sub(r"([A-Z]{2}) chia ([A-Z]{2})", r"\1 / \2", text)
    return text


def load_vtt_cues(path: Path) -> list[dict[str, float | str]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    cues: list[dict[str, float | str]] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if "-->" not in line:
            index += 1
            continue
        start_raw, end_raw = [part.strip() for part in line.split("-->")]
        index += 1
        text_lines: list[str] = []
        while index < len(lines) and lines[index].strip():
            text_lines.append(lines[index].strip())
            index += 1
        raw_text = " ".join(text_lines)
        cues.append(
            {
                "start": parse_vtt_time(start_raw),
                "end": parse_vtt_time(end_raw),
                "text": polish_cue_text(raw_text),
                "raw_text": raw_text,
            }
        )
        index += 1
    return cues


_CUES: list[dict[str, float | str]] | None = None


def cues() -> list[dict[str, float | str]]:
    global _CUES
    if _CUES is None:
        _CUES = load_vtt_cues(Path("sourcecompile_mathspeech_timestamp.vtt"))
    return _CUES


def cue_index_for(elapsed: float, cue_list: list[dict[str, float | str]]) -> int:
    if not cue_list:
        return -1
    for index, cue in enumerate(cue_list):
        if float(cue["start"]) <= elapsed < float(cue["end"]):
            return index
    if elapsed < float(cue_list[0]["start"]):
        return 0
    return len(cue_list) - 1


def features_for_elapsed(elapsed: float) -> tuple[str, ...]:
    if elapsed < 9.725:
        return ("triangle",)
    if elapsed < 16.087:
        return ("triangle", "incircle", "contacts")
    if elapsed < 22.950:
        return ("triangle", "incircle", "contacts", "kl")
    if elapsed < 35.887:
        return ("triangle", "incircle", "contacts", "kl", "targets")
    if elapsed < 52.025:
        return ("triangle", "incircle", "contacts", "kl", "targets", "part3")
    if elapsed < 61.350:
        return ("triangle", "contacts")
    if elapsed < 67.775:
        return ("triangle", "incircle", "contacts")
    if elapsed < 75.850:
        return ("triangle", "incircle", "contacts", "kl")
    if elapsed < 90.862:
        return ("triangle", "incircle", "contacts", "kl", "part3")
    if elapsed < 133.787:
        return ("triangle", "incircle", "contacts", "kl", "part1")
    if elapsed < 197.237:
        return ("triangle", "incircle", "contacts", "kl", "part2")
    if elapsed < 250.487:
        return ("triangle", "incircle", "contacts", "part3")
    return ("triangle", "incircle", "contacts", "part3", "conclusion")


def formulas_for_elapsed(elapsed: float) -> list[str]:
    if elapsed < 52.025:
        return ["DK ∥ IC", "KF ∩ EL = J ∈ (I)", "PI ⟂ AS"]
    if elapsed < 90.862:
        return ["K, L là hình chiếu trên đường qua I ∥ EF", "M ∈ DK ∩ (I), N ∈ DL ∩ (I)", "P = MN ∩ BC, DS là đường kính"]
    if elapsed < 133.787:
        return ["∠KIF = ∠IFE = ∠IEF", "∠KIB = ∠IED = ∠ICD", "∠BDK = ∠BIK = ∠ICD ⇒ DK ∥ IC"]
    if elapsed < 197.237:
        return ["B, K, F, I, D đồng viên", "I, E, L, D, C đồng viên", "∠JED + ∠DEL = 180° ⇒ J, E, L thẳng hàng"]
    if elapsed < 250.487:
        return ["E, I, M thẳng hàng; F, I, N thẳng hàng", "IX · IA = IE² = IS · ID", "ΔAIS ∼ ΔDIY"]
    return ["PDYI nội tiếp đường tròn đường kính PI", "∠IPY = ∠IDY = ∠IAS", "Vậy AS ⟂ PI"]


def load_font(size: int, bold: bool = False, math_font: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if math_font:
        candidates.extend([Path("C:/Windows/Fonts/cambria.ttc"), Path("C:/Windows/Fonts/cambriab.ttf")])
    candidates.extend(
        [
            Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT_KICKER = load_font(30, True)
FONT_TITLE = load_font(58, True, math_font=True)
FONT_BODY = load_font(34, math_font=True)
FONT_BODY_BOLD = load_font(34, True, math_font=True)
FONT_MATH = load_font(38, math_font=True)
FONT_LABEL = load_font(24, True)
FONT_SMALL = load_font(22, math_font=True)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    width: int,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    line_height: int,
) -> int:
    for line in wrap_text(draw, text, font, width):
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def point_lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def tangent_point_to_line(
    p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
) -> tuple[float, float]:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    return (ax + t * dx, ay + t * dy)


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def add(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: tuple[float, float], b: tuple[float, float]) -> tuple[float, float]:
    return (a[0] - b[0], a[1] - b[1])


def mul(a: tuple[float, float], k: float) -> tuple[float, float]:
    return (a[0] * k, a[1] * k)


def dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross(a: tuple[float, float], b: tuple[float, float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def project_point_to_line(
    p: tuple[float, float], a: tuple[float, float], direction: tuple[float, float]
) -> tuple[float, float]:
    t = dot(sub(p, a), direction) / dot(direction, direction)
    return add(a, mul(direction, t))


def line_intersection(
    a: tuple[float, float],
    direction_a: tuple[float, float],
    b: tuple[float, float],
    direction_b: tuple[float, float],
) -> tuple[float, float]:
    denominator = cross(direction_a, direction_b)
    if abs(denominator) < 1e-9:
        return a
    t = cross(sub(b, a), direction_b) / denominator
    return add(a, mul(direction_a, t))


def second_circle_intersection(
    known: tuple[float, float],
    through: tuple[float, float],
    center: tuple[float, float],
) -> tuple[float, float]:
    direction = sub(through, known)
    numerator = -2 * dot(sub(known, center), direction)
    denominator = dot(direction, direction)
    t = numerator / denominator
    return add(known, mul(direction, t))


def circumcircle(
    a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]
) -> tuple[tuple[float, float], float] | None:
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        return None
    ux = (
        (ax * ax + ay * ay) * (by - cy)
        + (bx * bx + by * by) * (cy - ay)
        + (cx * cx + cy * cy) * (ay - by)
    ) / d
    uy = (
        (ax * ax + ay * ay) * (cx - bx)
        + (bx * bx + by * by) * (ax - cx)
        + (cx * cx + cy * cy) * (bx - ax)
    ) / d
    center = (ux, uy)
    return center, dist(center, a)


def draw_line(
    draw: ImageDraw.ImageDraw,
    a: tuple[float, float],
    b: tuple[float, float],
    fill: tuple[int, int, int],
    width: int = 4,
    dash: bool = False,
) -> None:
    if not dash:
        draw.line([a, b], fill=fill, width=width)
        return
    for i in range(28):
        if i % 2 == 0:
            draw.line([point_lerp(a, b, i / 28), point_lerp(a, b, (i + 1) / 28)], fill=fill, width=width)


def draw_point(
    draw: ImageDraw.ImageDraw,
    pos: tuple[float, float],
    label: str,
    fill: tuple[int, int, int] = INK,
    offset: tuple[int, int] = (10, -34),
) -> None:
    x, y = pos
    r = 7
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    draw.text((x + offset[0], y + offset[1]), label, font=FONT_LABEL, fill=fill)


def draw_circle(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    radius: float,
    fill: tuple[int, int, int],
    width: int = 4,
) -> None:
    x, y = center
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=fill, width=width)


def draw_right_angle(
    draw: ImageDraw.ImageDraw,
    vertex: tuple[float, float],
    toward_a: tuple[float, float],
    toward_b: tuple[float, float],
    size: float = 24,
    fill: tuple[int, int, int] = MUTED,
) -> None:
    va = sub(toward_a, vertex)
    vb = sub(toward_b, vertex)
    la = math.hypot(*va)
    lb = math.hypot(*vb)
    if la < 1e-6 or lb < 1e-6:
        return
    ua = mul(va, size / la)
    ub = mul(vb, size / lb)
    p1 = add(vertex, ua)
    p2 = add(p1, ub)
    p3 = add(vertex, ub)
    draw.line([p1, p2, p3], fill=fill, width=3)


def draw_extended_line(
    draw: ImageDraw.ImageDraw,
    a: tuple[float, float],
    b: tuple[float, float],
    fill: tuple[int, int, int],
    width: int = 4,
    dash: bool = False,
    scale: float = 1.35,
) -> None:
    mid = point_lerp(a, b, 0.5)
    half = mul(sub(b, a), scale / 2)
    draw_line(draw, sub(mid, half), add(mid, half), fill, width, dash)


def geometry_points() -> tuple[dict[str, tuple[float, float]], float]:
    model_a = (0.0, 4.5)
    model_b = (-2.5, 0.0)
    model_c = (6.0, 0.0)

    side_a = dist(model_b, model_c)
    side_b = dist(model_c, model_a)
    side_c = dist(model_a, model_b)
    perimeter = side_a + side_b + side_c
    model_i = (
        (side_a * model_a[0] + side_b * model_b[0] + side_c * model_c[0]) / perimeter,
        (side_a * model_a[1] + side_b * model_b[1] + side_c * model_c[1]) / perimeter,
    )
    model_d = tangent_point_to_line(model_i, model_b, model_c)
    model_e = tangent_point_to_line(model_i, model_c, model_a)
    model_f = tangent_point_to_line(model_i, model_a, model_b)
    direction_ef = sub(model_f, model_e)
    model_k = project_point_to_line(model_b, model_i, direction_ef)
    model_l = project_point_to_line(model_c, model_i, direction_ef)
    model_m = second_circle_intersection(model_d, model_k, model_i)
    model_n = second_circle_intersection(model_d, model_l, model_i)
    model_p = line_intersection(model_m, sub(model_n, model_m), model_b, sub(model_c, model_b))
    model_s = add(model_i, sub(model_i, model_d))
    model_j = second_circle_intersection(model_f, model_k, model_i)
    model_x = line_intersection(model_a, sub(model_i, model_a), model_e, sub(model_f, model_e))
    model_y = line_intersection(model_a, sub(model_i, model_a), model_m, sub(model_n, model_m))

    scale = 100.0
    origin_x = 410.0
    origin_y = 1610.0

    def screen(point: tuple[float, float]) -> tuple[float, float]:
        return (origin_x + point[0] * scale, origin_y - point[1] * scale)

    model_points = {
        "A": model_a,
        "B": model_b,
        "C": model_c,
        "I": model_i,
        "D": model_d,
        "E": model_e,
        "F": model_f,
        "K": model_k,
        "L": model_l,
        "M": model_m,
        "N": model_n,
        "P": model_p,
        "S": model_s,
        "J": model_j,
        "X": model_x,
        "Y": model_y,
    }
    radius = dist(model_i, model_d) * scale
    return {key: screen(value) for key, value in model_points.items()}, radius


def draw_geometry(draw: ImageDraw.ImageDraw, features: tuple[str, ...], elapsed: float) -> None:
    pts, radius = geometry_points()
    a, b, c, i, d, e, f = (pts[key] for key in ("A", "B", "C", "I", "D", "E", "F"))
    k, l, m, n, p, s = (pts[key] for key in ("K", "L", "M", "N", "P", "S"))
    j, x_point, y_point = (pts[key] for key in ("J", "X", "Y"))
    glow = int(22 + 9 * math.sin(elapsed * 2.2))

    draw.rounded_rectangle((44, 900, 1036, 1816), radius=18, fill=PANEL, outline=GRID, width=2)
    draw.text((74, 928), "Dựng hình", font=FONT_BODY_BOLD, fill=INK)

    if "triangle" in features:
        draw_line(draw, a, b, BLUE, 6)
        draw_line(draw, b, c, BLUE, 6)
        draw_line(draw, c, a, BLUE, 6)

    if "incircle" in features:
        draw_circle(draw, i, radius, GREEN, 6)
        draw_point(draw, i, "I", GREEN, (12, -8))

    if "contacts" in features or "triangle" in features:
        for key, offset in {
            "A": (10, -42),
            "B": (-42, 12),
            "C": (14, 12),
            "D": (10, 12),
            "E": (10, -34),
            "F": (-42, -34),
        }.items():
            draw_point(draw, pts[key], key, INK, offset)

    if "kl" in features:
        draw_line(draw, e, f, MUTED, 4, True)
        draw_line(draw, k, l, ORANGE, 7)
        draw_line(draw, b, k, MUTED, 4, True)
        draw_line(draw, c, l, MUTED, 4, True)
        draw_point(draw, k, "K", ORANGE, (-42, -34))
        draw_point(draw, l, "L", ORANGE, (12, -34))
        draw_right_angle(draw, k, b, l, 22, ORANGE)
        draw_right_angle(draw, l, c, k, 22, ORANGE)

    if "targets" in features:
        draw_line(draw, d, k, RED, 7)
        draw_line(draw, i, c, RED, 5, True)
        draw_line(draw, k, f, PURPLE, 5)
        draw_line(draw, e, l, PURPLE, 5)

    if "part1" in features:
        draw_line(draw, e, f, MUTED, 4, True)
        draw_line(draw, k, l, ORANGE, 6)
        draw_line(draw, d, k, RED, 8)
        draw_line(draw, i, c, RED, 6, True)
        draw_right_angle(draw, k, b, i, 22, RED)
        draw_right_angle(draw, d, b, i, 22, RED)
        draw.ellipse((d[0] - glow, d[1] - glow, d[0] + glow, d[1] + glow), outline=RED, width=3)

    if "part2" in features:
        circle_bkfid = circumcircle(b, k, f)
        circle_ieldc = circumcircle(i, e, l)
        if circle_bkfid:
            draw_circle(draw, circle_bkfid[0], circle_bkfid[1], (210, 196, 238), 3)
        if circle_ieldc:
            draw_circle(draw, circle_ieldc[0], circle_ieldc[1], (204, 226, 216), 3)
        draw_extended_line(draw, k, f, PURPLE, 7)
        draw_extended_line(draw, e, l, PURPLE, 7)
        draw_point(draw, j, "J", PURPLE, (12, -38))
        draw.ellipse((j[0] - glow, j[1] - glow, j[0] + glow, j[1] + glow), outline=PURPLE, width=3)

    if "part3" in features:
        draw_line(draw, e, f, MUTED, 4, True)
        draw_line(draw, e, m, MUTED, 4, True)
        draw_line(draw, f, n, MUTED, 4, True)
        draw_line(draw, a, i, MUTED, 4, True)
        draw_line(draw, d, m, RED, 5)
        draw_line(draw, d, n, RED, 5)
        draw_line(draw, m, n, PURPLE, 7)
        draw_line(draw, d, s, GREEN, 5)
        draw_line(draw, p, i, RED, 7)
        draw_line(draw, a, s, RED, 7)
        draw_point(draw, x_point, "X", MUTED, (10, -32))
        draw_point(draw, y_point, "Y", MUTED, (10, -32))
        for key, offset in {"M": (-46, -28), "N": (12, -34), "P": (12, 12), "S": (12, -36)}.items():
            draw_point(draw, pts[key], key, INK, offset)

    if "conclusion" in features:
        draw.rounded_rectangle((590, 940, 1000, 1014), radius=10, fill=(255, 241, 241), outline=(245, 190, 194), width=2)
        draw.text((615, 958), "AS ⟂ PI", font=FONT_MATH, fill=RED)


def slide_for(elapsed: float) -> dict:
    for slide in SLIDES:
        if slide["start"] <= elapsed < slide["end"]:
            return slide
    return SLIDES[-1]


def render_frame(elapsed: float, duration: float) -> Image.Image:
    slide = slide_for(elapsed)
    cue_list = cues()
    cue_index = cue_index_for(elapsed, cue_list)
    active_cue = cue_list[cue_index] if cue_index >= 0 else {"text": "", "start": 0.0, "end": 0.0}
    previous_cue = cue_list[cue_index - 1] if cue_index > 0 else None
    next_cue = cue_list[cue_index + 1] if 0 <= cue_index < len(cue_list) - 1 else None
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    for y in range(0, HEIGHT, 32):
        shade = int(244 + 5 * math.sin(y / 90 + elapsed * 0.2))
        draw.line([(0, y), (WIDTH, y)], fill=(shade, shade + 2, 252), width=1)

    draw.rounded_rectangle((44, 46, 1036, 852), radius=18, fill=PANEL, outline=GRID, width=2)
    draw.text((74, 78), slide["kicker"], font=FONT_KICKER, fill=GREEN)
    y = draw_wrapped(draw, slide["title"], 74, 126, 920, FONT_TITLE, INK, 68)
    y += 12

    cue_start = float(active_cue["start"])
    cue_end = float(active_cue["end"])
    cue_progress = 0.0 if cue_end <= cue_start else min(max((elapsed - cue_start) / (cue_end - cue_start), 0.0), 1.0)
    draw.rounded_rectangle((74, y, 1006, y + 220), radius=12, fill=(244, 248, 255), outline=(204, 218, 242), width=2)
    draw.text((104, y + 18), "Đang phát theo timestamp", font=FONT_SMALL, fill=MUTED)
    draw_wrapped(draw, str(active_cue["text"]), 104, y + 52, 860, FONT_BODY_BOLD, INK, 43)
    draw.rounded_rectangle((104, y + 190, 976, y + 200), radius=5, fill=(214, 224, 238))
    draw.rounded_rectangle((104, y + 190, 104 + int(872 * cue_progress), y + 200), radius=5, fill=BLUE)
    y += 240

    if previous_cue:
        draw_wrapped(draw, f"Trước: {previous_cue['text']}", 84, y, 900, FONT_SMALL, MUTED, 29)
        y += 34
    if next_cue:
        draw_wrapped(draw, f"Tiếp: {next_cue['text']}", 84, y, 900, FONT_SMALL, MUTED, 29)
        y += 42

    formulas = formulas_for_elapsed(elapsed)
    draw.rounded_rectangle((74, y, 1006, min(y + 205, 812)), radius=12, fill=(250, 252, 255), outline=(216, 226, 244), width=2)
    my = y + 18
    for formula in formulas:
        color = RED if "⇒" in formula or "Vậy" in formula or "⟂" in formula else BLUE
        my = draw_wrapped(draw, formula, 104, my, 860, FONT_MATH, color, 45) + 4

    draw_geometry(draw, features_for_elapsed(elapsed), elapsed)

    progress = min(elapsed / duration, 1.0)
    bar_x, bar_y, bar_w, bar_h = 74, 1850, 932, 14
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=7, fill=(216, 225, 236))
    draw.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + bar_h), radius=7, fill=GREEN)
    draw.text(
        (bar_x, bar_y + 24),
        f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d} / {int(duration // 60):02d}:{int(duration % 60):02d}",
        font=FONT_SMALL,
        fill=MUTED,
    )
    return img


def make_video(audio_path: Path, output_path: Path, fps: int) -> None:
    duration = audio_duration(audio_path)
    frame_count = math.ceil(duration * fps)
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        str(output_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    try:
        for frame_index in range(frame_count):
            elapsed = frame_index / fps
            process.stdin.write(render_frame(elapsed, duration).tobytes())
            if frame_index % (fps * 30) == 0:
                print(f"Rendered {frame_index}/{frame_count} frames", flush=True)
    finally:
        process.stdin.close()

    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {return_code}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a professional math video from translated Markdown/LaTeX content.")
    parser.add_argument("audio", nargs="?", default="sourcecompile_mathspeech.mp3")
    parser.add_argument("output", nargs="?", default="source_math_professional_vertical.mp4")
    parser.add_argument("--fps", type=int, default=FPS)
    args = parser.parse_args()
    make_video(Path(args.audio), Path(args.output), args.fps)
    print(f"Da tao {args.output}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
