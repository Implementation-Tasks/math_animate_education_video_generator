from __future__ import annotations

import argparse
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1280
HEIGHT = 720
FPS = 12
BG = (247, 249, 252)
INK = (26, 33, 46)
MUTED = (96, 110, 130)
BLUE = (35, 91, 174)
GREEN = (35, 140, 100)
ORANGE = (210, 120, 30)
RED = (200, 55, 60)
PURPLE = (110, 75, 170)


SCENES = [
    (
        0.00,
        0.16,
        "Đề bài",
        [
            "Tam giác ABC nhọn, không cân, AB < AC",
            "Đường tròn (I) tiếp xúc BC, CA, AB tại D, E, F",
            "K, L là chân vuông góc lên đường qua I song song EF",
        ],
        ("triangle", "incircle", "contacts"),
    ),
    (
        0.16,
        0.29,
        "Mục tiêu",
        [
            "1. Chứng minh DK song song IC",
            "2. KF và EL cắt nhau trên (I)",
            "3. Với MN cắt BC tại P, chứng minh PI vuông góc AS",
        ],
        ("triangle", "incircle", "kl", "targets"),
    ),
    (
        0.29,
        0.46,
        "Phần 1",
        [
            "Từ EF song song KI suy ra các góc tương ứng bằng nhau",
            "Tứ giác BKID nội tiếp vì có hai góc vuông",
            "Kết luận: DK song song IC",
        ],
        ("triangle", "incircle", "kl", "part1"),
    ),
    (
        0.46,
        0.68,
        "Phần 2",
        [
            "B, K, F, I, D đồng viên",
            "I, E, L, D, C đồng viên",
            "Suy ra J, E, L thẳng hàng và J nằm trên (I)",
        ],
        ("triangle", "incircle", "kl", "part2"),
    ),
    (
        0.68,
        0.88,
        "Phần 3",
        [
            "E, I, M thẳng hàng; F, I, N thẳng hàng",
            "MNEF là hình chữ nhật",
            "Dùng đồng dạng tam giác AIS và DIY",
        ],
        ("triangle", "incircle", "part3"),
    ),
    (
        0.88,
        1.01,
        "Kết luận",
        [
            "Tứ giác PDYI nội tiếp đường tròn đường kính PI",
            "Góc IPY bằng góc IAS",
            "Vậy AS vuông góc PI",
        ],
        ("triangle", "incircle", "part3", "conclusion"),
    ),
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


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


FONT_TITLE = load_font(46, bold=True)
FONT_SUBTITLE = load_font(28, bold=True)
FONT_BODY = load_font(26)
FONT_SMALL = load_font(18)


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
    segments = 26
    for i in range(segments):
        if i % 2 == 0:
            draw.line(
                [point_lerp(a, b, i / segments), point_lerp(a, b, (i + 1) / segments)],
                fill=fill,
                width=width,
            )


def draw_point(
    draw: ImageDraw.ImageDraw,
    pos: tuple[float, float],
    label: str,
    fill: tuple[int, int, int] = INK,
    label_offset: tuple[int, int] = (8, -28),
) -> None:
    x, y = pos
    r = 5
    draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)
    draw.text((x + label_offset[0], y + label_offset[1]), label, font=FONT_SMALL, fill=fill)


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    x: int,
    y: int,
    fill: tuple[int, int, int] = INK,
    line_height: int = 38,
) -> None:
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_height), line, font=FONT_BODY, fill=fill)


def scene_for(progress: float) -> tuple[float, float, str, list[str], tuple[str, ...]]:
    for scene in SCENES:
        if scene[0] <= progress < scene[1]:
            return scene
    return SCENES[-1]


def draw_geometry(
    draw: ImageDraw.ImageDraw,
    features: tuple[str, ...],
    local: float,
    elapsed: float,
) -> None:
    ax, ay = 450, 105
    bx, by = 185, 560
    cx, cy = 850, 560
    i = (445, 385)
    radius = 119
    a = (ax, ay)
    b = (bx, by)
    c = (cx, cy)
    d = tangent_point_to_line(i, b, c)
    e = tangent_point_to_line(i, c, a)
    f = tangent_point_to_line(i, a, b)
    k = (285, 382)
    l = (695, 382)
    m = (2 * i[0] - e[0], 2 * i[1] - e[1])
    n = (2 * i[0] - f[0], 2 * i[1] - f[1])
    p = (630, 560)
    s = (2 * i[0] - d[0], 2 * i[1] - d[1])

    glow = int(18 + 10 * math.sin(elapsed * 2.0))

    if "triangle" in features:
        draw.polygon([a, b, c], outline=BLUE)
        draw_line(draw, a, b, BLUE, 4)
        draw_line(draw, b, c, BLUE, 4)
        draw_line(draw, c, a, BLUE, 4)

    if "incircle" in features:
        x, y = i
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=GREEN, width=4)
        draw_point(draw, i, "I", GREEN, (8, -6))

    if "contacts" in features or "triangle" in features:
        for pos, label, offset in [
            (a, "A", (8, -32)),
            (b, "B", (-28, 8)),
            (c, "C", (10, 8)),
            (d, "D", (8, 8)),
            (e, "E", (8, -24)),
            (f, "F", (-28, -24)),
        ]:
            draw_point(draw, pos, label, INK, offset)

    if "kl" in features:
        draw_line(draw, k, l, ORANGE, 5)
        draw_line(draw, b, k, MUTED, 3, dash=True)
        draw_line(draw, c, l, MUTED, 3, dash=True)
        draw_point(draw, k, "K", ORANGE, (-28, -24))
        draw_point(draw, l, "L", ORANGE, (8, -24))

    if "targets" in features:
        draw_line(draw, d, k, RED, 5)
        draw_line(draw, i, c, RED, 5, dash=True)
        draw_line(draw, k, f, PURPLE, 4)
        draw_line(draw, e, l, PURPLE, 4)

    if "part1" in features:
        draw_line(draw, d, k, RED, 6)
        draw_line(draw, i, c, RED, 5, dash=True)
        draw.ellipse((d[0] - glow, d[1] - glow, d[0] + glow, d[1] + glow), outline=RED, width=2)

    if "part2" in features:
        draw_line(draw, k, f, PURPLE, 5)
        draw_line(draw, e, l, PURPLE, 5)
        j = point_lerp(k, f, 0.62)
        draw_point(draw, j, "J", PURPLE, (8, -28))
        draw.ellipse((j[0] - glow, j[1] - glow, j[0] + glow, j[1] + glow), outline=PURPLE, width=2)

    if "part3" in features:
        draw_line(draw, d, m, RED, 4)
        draw_line(draw, d, n, RED, 4)
        draw_line(draw, m, n, PURPLE, 5)
        draw_line(draw, d, s, GREEN, 4)
        draw_line(draw, p, i, RED, 5)
        draw_line(draw, a, s, RED, 5)
        for pos, label, offset in [
            (m, "M", (-30, -20)),
            (n, "N", (8, -22)),
            (p, "P", (8, 8)),
            (s, "S", (10, -24)),
        ]:
            draw_point(draw, pos, label, INK, offset)

    if "conclusion" in features:
        cx0, cy0 = p
        draw.arc((cx0 - 34, cy0 - 34, cx0 + 34, cy0 + 34), 205, 295, fill=RED, width=5)
        draw.text((930, 530), "AS vuông góc PI", font=FONT_SUBTITLE, fill=RED)

    dot_t = (elapsed * 0.10) % 1.0
    moving = point_lerp(a, c, dot_t)
    draw.ellipse((moving[0] - 4, moving[1] - 4, moving[0] + 4, moving[1] + 4), fill=ORANGE)


def render_frame(elapsed: float, duration: float) -> Image.Image:
    progress = min(elapsed / duration, 0.999)
    start, end, title, lines, features = scene_for(progress)
    local = (progress - start) / max(end - start, 0.001)

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    for y in range(0, HEIGHT, 24):
        shade = int(242 + 8 * math.sin((y / 80) + elapsed * 0.25))
        draw.line([(0, y), (WIDTH, y)], fill=(shade, shade + 2, 252), width=1)

    draw.rounded_rectangle((44, 42, 1236, 678), radius=8, outline=(220, 228, 238), width=2)
    draw.text((76, 64), title, font=FONT_TITLE, fill=INK)
    draw_wrapped_text(draw, lines, 76, 135)

    draw_geometry(draw, features, local, elapsed)

    bar_x, bar_y, bar_w, bar_h = 76, 642, 1128, 10
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=4, fill=(218, 226, 236))
    draw.rounded_rectangle(
        (bar_x, bar_y, bar_x + int(bar_w * progress), bar_y + bar_h),
        radius=4,
        fill=GREEN,
    )
    draw.text(
        (bar_x, bar_y + 18),
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
            frame = render_frame(elapsed, duration)
            process.stdin.write(frame.tobytes())
            if frame_index % (fps * 30) == 0:
                print(f"Rendered {frame_index}/{frame_count} frames", flush=True)
    finally:
        process.stdin.close()

    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"ffmpeg failed with exit code {return_code}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Tạo video animation khớp thời lượng audio TTS.")
    parser.add_argument("audio", nargs="?", default="sourcecompile_mathspeech.mp3")
    parser.add_argument("output", nargs="?", default="sourcecompile_mathspeech_animation.mp4")
    parser.add_argument("--fps", type=int, default=FPS)
    args = parser.parse_args()

    make_video(Path(args.audio), Path(args.output), args.fps)
    print(f"Da tao {args.output}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
