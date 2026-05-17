from __future__ import annotations

from .core import Coord, Level


def rectangle_layer(cols: int, rows: int, z: int, x0: int, y0: int) -> list[Coord]:
    return [
        Coord(x=x0 + col * 2, y=y0 + row * 2, z=z)
        for row in range(rows)
        for col in range(cols)
    ]


LEVELS: dict[str, Level] = {
    "easy": Level(
        key="easy",
        name="Easy",
        coords=tuple(
            rectangle_layer(cols=6, rows=4, z=0, x0=0, y0=0)
            + rectangle_layer(cols=4, rows=2, z=1, x0=2, y0=2)
            + rectangle_layer(cols=2, rows=1, z=2, x0=4, y0=3)
            + rectangle_layer(cols=2, rows=1, z=3, x0=4, y0=3)
        ),
    ),
    "medium": Level(
        key="medium",
        name="Medium",
        coords=tuple(
            rectangle_layer(cols=8, rows=6, z=0, x0=0, y0=0)
            + rectangle_layer(cols=6, rows=3, z=1, x0=2, y0=3)
            + rectangle_layer(cols=4, rows=1, z=2, x0=4, y0=5)
            + rectangle_layer(cols=2, rows=1, z=3, x0=6, y0=5)
        ),
    ),
    "hard": Level(
        key="hard",
        name="Hard",
        coords=tuple(
            rectangle_layer(cols=10, rows=8, z=0, x0=0, y0=0)
            + rectangle_layer(cols=8, rows=5, z=1, x0=2, y0=3)
            + rectangle_layer(cols=6, rows=3, z=2, x0=4, y0=5)
            + rectangle_layer(cols=4, rows=1, z=3, x0=6, y0=7)
            + rectangle_layer(cols=2, rows=1, z=4, x0=8, y0=7)
        ),
    ),
}

