from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path


EPS = 1e-8


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scale: float) -> "Point":
        return Point(self.x * scale, self.y * scale)

    def dot(self, other: "Point") -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Point") -> float:
        return self.x * other.y - self.y * other.x

    def norm(self) -> float:
        return math.hypot(self.x, self.y)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


def distance(a: Point, b: Point) -> float:
    return (a - b).norm()


def foot_point(p: Point, a: Point, b: Point) -> Point:
    direction = b - a
    t = (p - a).dot(direction) / direction.dot(direction)
    return a + direction * t


def line_intersection(a: Point, b: Point, c: Point, d: Point) -> Point:
    r = b - a
    s = d - c
    denom = r.cross(s)
    if abs(denom) < EPS:
        raise ValueError("Hai duong thang song song hoac trung nhau.")
    t = (c - a).cross(s) / denom
    return a + r * t


def circle_line_intersections(center: Point, radius: float, a: Point, b: Point) -> list[Point]:
    direction = b - a
    offset = a - center
    aa = direction.dot(direction)
    bb = 2 * offset.dot(direction)
    cc = offset.dot(offset) - radius * radius
    disc = bb * bb - 4 * aa * cc
    if disc < -EPS:
        return []
    disc = max(0.0, disc)
    root = math.sqrt(disc)
    return [
        a + direction * ((-bb - root) / (2 * aa)),
        a + direction * ((-bb + root) / (2 * aa)),
    ]


def incenter(a: Point, b: Point, c: Point) -> Point:
    side_a = distance(b, c)
    side_b = distance(c, a)
    side_c = distance(a, b)
    total = side_a + side_b + side_c
    return Point(
        (side_a * a.x + side_b * b.x + side_c * c.x) / total,
        (side_a * a.y + side_b * b.y + side_c * c.y) / total,
    )


def other_than(points: list[Point], reference: Point) -> Point:
    points = sorted(points, key=lambda point: distance(point, reference), reverse=True)
    return points[0]


def build_construction() -> dict[str, object]:
    # Same triangle as the original TikZ source, but all dependent points are computed.
    a = Point(0.0, 4.5)
    b = Point(-2.5, 0.0)
    c = Point(6.0, 0.0)

    i = incenter(a, b, c)
    d = foot_point(i, b, c)
    e = foot_point(i, c, a)
    f = foot_point(i, a, b)
    radius = distance(i, d)

    ef_dir = e - f
    line_start = i
    line_end = i + ef_dir
    k = foot_point(b, line_start, line_end)
    l = foot_point(c, line_start, line_end)

    m = other_than(circle_line_intersections(i, radius, d, k), d)
    n = other_than(circle_line_intersections(i, radius, d, l), d)
    p = line_intersection(m, n, b, c)
    s = i * 2 - d
    x = line_intersection(a, i, e, f)
    y = line_intersection(a, i, m, n)

    points = {
        "A": a,
        "B": b,
        "C": c,
        "I": i,
        "D": d,
        "E": e,
        "F": f,
        "K": k,
        "L": l,
        "M": m,
        "N": n,
        "P": p,
        "S": s,
        "X": x,
        "Y": y,
    }
    validations = validate(points, radius)

    return {
        "radius": radius,
        "points": {name: point.as_tuple() for name, point in points.items()},
        "validations": validations,
    }


def parallel_error(a: Point, b: Point, c: Point, d: Point) -> float:
    return abs((b - a).cross(d - c))


def perpendicular_error(a: Point, b: Point, c: Point, d: Point) -> float:
    return abs((b - a).dot(d - c))


def circle_error(center: Point, radius: float, point: Point) -> float:
    return abs(distance(center, point) - radius)


def validate(points: dict[str, Point], radius: float) -> dict[str, float]:
    a = points["A"]
    b = points["B"]
    c = points["C"]
    i = points["I"]
    d = points["D"]
    e = points["E"]
    f = points["F"]
    k = points["K"]
    l = points["L"]
    m = points["M"]
    n = points["N"]
    p = points["P"]
    s = points["S"]
    return {
        "D_on_BC": perpendicular_error(i, d, b, c),
        "E_on_CA": perpendicular_error(i, e, c, a),
        "F_on_AB": perpendicular_error(i, f, a, b),
        "KI_parallel_EF": parallel_error(k, i, e, f),
        "BK_perpendicular_KI": perpendicular_error(b, k, k, i),
        "CL_perpendicular_KI": perpendicular_error(c, l, k, i),
        "M_on_circle": circle_error(i, radius, m),
        "N_on_circle": circle_error(i, radius, n),
        "DK_parallel_IC": parallel_error(d, k, i, c),
        "DL_parallel_IB": parallel_error(d, l, i, b),
        "P_on_BC": abs((p - b).cross(c - b)),
        "P_on_MN": abs((p - m).cross(n - m)),
        "DS_is_diameter": distance(d, s) - 2 * radius,
        "AS_perpendicular_PI": perpendicular_error(a, s, p, i),
    }


def main() -> None:
    data = build_construction()
    output = Path("geometric_construction.json")
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Da tao {output}")
    for key, value in data["validations"].items():
        print(f"{key}: {value:.3e}")


if __name__ == "__main__":
    main()
