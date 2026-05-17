from __future__ import annotations

from .core import Coord, Level


def row_layer(z: int, rows: list[tuple[int, int, int]]) -> list[Coord]:
    """Build a layer from `(y, x_start, count)` row specs."""
    return [
        Coord(x=x_start + col * 2, y=y, z=z)
        for y, x_start, count in rows
        for col in range(count)
    ]


LEVELS: dict[str, Level] = {
    "easy": Level(
        key="easy",
        name="Easy Pyramid",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 8, 2),
                    (2, 6, 4),
                    (4, 4, 6),
                    (6, 2, 8),
                    (8, 0, 10),
                    (10, 2, 8),
                    (12, 4, 6),
                    (14, 6, 4),
                    (16, 8, 2),
                ],
            )
            + row_layer(
                1,
                [(4, 8, 2), (6, 6, 4), (8, 4, 6), (10, 6, 4), (12, 8, 2)],
            )
            + row_layer(2, [(8, 6, 4)])
        ),
    ),
    "medium": Level(
        key="medium",
        name="Medium Turtle",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 8, 6),
                    (2, 4, 10),
                    (4, 2, 12),
                    (6, 0, 14),
                    (8, 2, 12),
                    (10, 4, 10),
                    (12, 8, 6),
                    (6, -4, 2),
                    (6, 28, 2),
                ],
            )
            + row_layer(
                1,
                [
                    (2, 8, 6),
                    (4, 6, 8),
                    (6, 4, 10),
                    (8, 6, 8),
                    (10, 8, 6),
                ],
            )
            + row_layer(2, [(4, 10, 4), (6, 8, 6), (8, 8, 6), (10, 10, 4)])
            + row_layer(3, [(6, 10, 4), (8, 10, 4)])
            + row_layer(4, [(6, 12, 4)])
        ),
    ),
    "hard": Level(
        key="hard",
        name="Hard Dragon",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 8, 8),
                    (2, 4, 12),
                    (4, 0, 14),
                    (6, 2, 13),
                    (8, 6, 12),
                    (10, 4, 14),
                    (12, 2, 12),
                    (14, 6, 10),
                ],
            )
            + row_layer(
                1,
                [
                    (2, 8, 5),
                    (4, 4, 7),
                    (6, 6, 8),
                    (8, 10, 6),
                    (10, 8, 5),
                ],
            )
            + row_layer(2, [(4, 8, 4), (6, 10, 4), (8, 12, 4), (10, 14, 2)])
            + row_layer(3, [(6, 10, 2), (8, 12, 2)])
        ),
    ),
}
