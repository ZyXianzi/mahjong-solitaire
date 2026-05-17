from __future__ import annotations

import random
from collections.abc import Sequence

from .core import Board, Coord, Level, Tile


FacePair = tuple[tuple[str, str], tuple[str, str]]


def generate_board(
    level: Level, seed: int | None = None, max_attempts: int = 50
) -> tuple[Board, list[tuple[int, int]]]:
    rng = random.Random(seed)
    for _ in range(max_attempts):
        coords = list(level.coords)
        rng.shuffle(coords)
        ordered_coords = sorted(coords, key=lambda coord: (coord.z, coord.y, coord.x))
        blank = Board(
            [
                Tile(
                    id=index,
                    face="",
                    match_group="",
                    coord=coord,
                )
                for index, coord in enumerate(ordered_coords)
            ]
        )
        solution = build_open_pair_sequence(blank)
        if len(solution) * 2 != len(ordered_coords):
            continue

        pairs = build_face_pairs()
        rng.shuffle(pairs)
        if len(solution) > len(pairs):
            raise ValueError("Not enough Mahjong tile faces for this layout.")

        board = blank.clone()
        for (first_id, second_id), pair_faces in zip(
            solution, pairs[: len(solution)], strict=True
        ):
            (first_face, first_group), (second_face, second_group) = pair_faces
            board.tile(first_id).face = first_face
            board.tile(first_id).match_group = first_group
            board.tile(second_id).face = second_face
            board.tile(second_id).match_group = second_group

        if validate_solution_path(board, solution):
            return board, solution

    raise RuntimeError(f"Could not generate a solvable {level.name} board.")


def build_open_pair_sequence(board: Board) -> list[tuple[int, int]]:
    work = board.clone()
    sequence: list[tuple[int, int]] = []
    while work.remaining_count() > 0:
        selectable = sorted(
            work.selectable_tiles(),
            key=lambda tile: (-tile.coord.z, tile.coord.y, tile.coord.x),
        )
        if len(selectable) < 2:
            return []
        first = selectable[0]
        second = selectable[1]
        first.removed = True
        second.removed = True
        sequence.append((first.id, second.id))
    return sequence


def validate_solution_path(board: Board, solution: Sequence[tuple[int, int]]) -> bool:
    work = board.clone()
    try:
        for first_id, second_id in solution:
            work.remove_pair(first_id, second_id)
    except ValueError:
        return False
    return work.is_complete()


def build_face_pairs() -> list[FacePair]:
    pairs: list[FacePair] = []
    suits = (("M", "characters"), ("B", "bamboo"), ("D", "dots"))
    for suffix, group in suits:
        for number in range(1, 10):
            face = f"{number}{suffix}"
            pairs.extend([((face, group), (face, group)) for _ in range(2)])

    for face in ("East", "South", "West", "North"):
        pairs.extend([((face, "wind"), (face, "wind")) for _ in range(2)])

    for face in ("Red", "Green", "White"):
        pairs.extend([((face, "dragon"), (face, "dragon")) for _ in range(2)])

    flowers = ("Plum", "Orch", "Chry", "Bamb")
    seasons = ("Spr", "Sum", "Aut", "Win")
    pairs.extend(group_pairs(flowers, "flower"))
    pairs.extend(group_pairs(seasons, "season"))
    return pairs


def group_pairs(faces: tuple[str, ...], group: str) -> list[FacePair]:
    return [
        ((faces[0], group), (faces[1], group)),
        ((faces[2], group), (faces[3], group)),
    ]
