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
    "easy_arena": Level(
        key="easy_arena",
        name="Easy Arena",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 0, 8),
                    (2, 0, 8),
                    (4, 0, 8),
                    (6, 0, 8),
                    (8, 0, 8),
                    (10, 0, 8),
                ],
            )
            + row_layer(1, [(2, 2, 6), (4, 2, 6), (6, 2, 6)])
            + row_layer(2, [(4, 4, 3), (6, 4, 3)])
        ),
    ),
    "easy_cross": Level(
        key="easy_cross",
        name="Easy Cross",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 8, 4),
                    (2, 6, 6),
                    (4, 2, 10),
                    (6, 0, 12),
                    (8, 2, 10),
                    (10, 6, 6),
                    (12, 8, 4),
                ],
            )
            + row_layer(1, [(4, 6, 6), (6, 4, 8), (8, 6, 6)])
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
    "medium_bridge": Level(
        key="medium_bridge",
        name="Medium Bridge",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 0, 5),
                    (0, 18, 5),
                    (2, 0, 5),
                    (2, 18, 5),
                    (4, 0, 14),
                    (6, 0, 14),
                    (8, 0, 14),
                    (10, 0, 14),
                    (12, 0, 5),
                    (12, 18, 5),
                    (14, 0, 5),
                    (14, 18, 5),
                ],
            )
            + row_layer(
                1,
                [(4, 4, 10), (6, 4, 10), (8, 4, 10), (10, 4, 10)],
            )
            + row_layer(2, [(6, 8, 4), (8, 8, 4)])
        ),
    ),
    "medium_fortress": Level(
        key="medium_fortress",
        name="Medium Fortress",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 2, 8),
                    (2, 0, 10),
                    (4, 0, 10),
                    (6, 0, 10),
                    (8, 0, 10),
                    (10, 0, 10),
                    (12, 0, 10),
                    (14, 2, 8),
                    (4, -4, 2),
                    (10, -4, 2),
                ],
            )
            + row_layer(
                1,
                [(2, 4, 8), (4, 4, 8), (6, 4, 8), (8, 4, 8), (10, 4, 8)],
            )
            + row_layer(
                2,
                [(4, 8, 5), (6, 8, 4), (8, 8, 5), (10, 10, 4)],
            )
            + row_layer(3, [(6, 10, 3), (8, 10, 3)])
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
    "hard_castle": Level(
        key="hard_castle",
        name="Hard Castle",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 0, 5),
                    (0, 18, 5),
                    (2, 2, 12),
                    (4, 0, 14),
                    (6, 0, 14),
                    (8, 0, 14),
                    (10, 0, 14),
                    (12, 2, 12),
                    (14, 0, 5),
                    (14, 18, 5),
                ],
            )
            + row_layer(
                1,
                [(2, 4, 10), (4, 4, 10), (6, 4, 10), (8, 4, 10)],
            )
            + row_layer(2, [(6, 10, 2), (8, 10, 2)])
        ),
    ),
    "hard_spider": Level(
        key="hard_spider",
        name="Hard Spider",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 4, 4),
                    (0, 22, 4),
                    (2, 8, 8),
                    (4, 4, 12),
                    (6, 0, 16),
                    (8, 0, 16),
                    (10, 4, 12),
                    (12, 8, 8),
                    (14, 4, 4),
                    (14, 22, 4),
                ],
            )
            + row_layer(
                1,
                [
                    (2, 8, 8),
                    (4, 6, 10),
                    (6, 6, 10),
                    (8, 6, 10),
                    (10, 6, 10),
                    (12, 8, 8),
                ],
            )
        ),
    ),
}
