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
        name="Easy Bridge",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 2, 5),
                    (2, 0, 6),
                    (4, 2, 4),
                    (6, 0, 5),
                    (8, 4, 4),
                ],
            )
            + row_layer(1, [(2, 4, 3), (4, 6, 2), (6, 2, 3)])
            + row_layer(2, [(3, 5, 2), (5, 7, 2)])
        ),
    ),
    "medium": Level(
        key="medium",
        name="Medium Fortress",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 2, 7),
                    (2, 0, 8),
                    (4, 0, 8),
                    (6, 2, 7),
                    (8, 0, 8),
                    (10, 4, 5),
                    (12, 6, 5),
                ],
            )
            + row_layer(
                1,
                [
                    (2, 4, 4),
                    (4, 3, 4),
                    (6, 6, 3),
                    (8, 5, 3),
                    (10, 8, 2),
                ],
            )
            + row_layer(2, [(3, 5, 2), (5, 9, 2), (7, 7, 2)])
            + row_layer(3, [(6, 8, 2)])
        ),
    ),
    "hard": Level(
        key="hard",
        name="Hard Dragon",
        coords=tuple(
            row_layer(
                0,
                [
                    (0, 2, 9),
                    (2, 0, 11),
                    (4, 4, 10),
                    (6, 2, 10),
                    (8, 0, 11),
                    (10, 4, 9),
                    (12, 2, 10),
                    (14, 6, 10),
                ],
            )
            + row_layer(
                1,
                [
                    (2, 4, 7),
                    (4, 6, 8),
                    (6, 3, 9),
                    (8, 5, 8),
                    (10, 7, 8),
                ],
            )
            + row_layer(2, [(3, 7, 5), (5, 5, 4), (7, 9, 5), (9, 7, 4)])
            + row_layer(3, [(5, 8, 2), (7, 10, 2)])
            + row_layer(4, [(6, 9, 2)])
        ),
    ),
}
