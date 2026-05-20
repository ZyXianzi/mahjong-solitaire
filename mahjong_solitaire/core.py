"""Core game rules that can be tested without opening a Pygame window."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


TILE_SPAN = 2


@dataclass(frozen=True)
class Coord:
    """Tile position in the layout grid.

    The `z` value is the layer height. Higher layers can cover lower tiles.
    """

    x: int
    y: int
    z: int


@dataclass
class Tile:
    """A single Mahjong tile on the board."""

    id: int
    face: str
    match_group: str
    coord: Coord
    removed: bool = False

    @property
    def x(self) -> int:
        return self.coord.x

    @property
    def y(self) -> int:
        return self.coord.y

    @property
    def z(self) -> int:
        return self.coord.z


@dataclass(frozen=True)
class Move:
    """One removed pair, stored so undo can restore it."""

    first_id: int
    second_id: int


@dataclass(frozen=True)
class Level:
    """A named layout template made from fixed tile coordinates."""

    key: str
    name: str
    coords: tuple[Coord, ...]


class Board:
    """Rules engine for selecting, matching, removing, and restoring tiles."""

    def __init__(self, tiles: list[Tile]):
        self.tiles = tiles
        self._by_id = {tile.id: tile for tile in tiles}

    def clone(self) -> Board:
        """Return an independent copy used by tests and board generation."""
        return Board(
            [
                Tile(
                    id=tile.id,
                    face=tile.face,
                    match_group=tile.match_group,
                    coord=tile.coord,
                    removed=tile.removed,
                )
                for tile in self.tiles
            ]
        )

    def tile(self, tile_id: int) -> Tile:
        return self._by_id[tile_id]

    def active_tiles(self) -> list[Tile]:
        return [tile for tile in self.tiles if not tile.removed]

    def remaining_count(self) -> int:
        return sum(not tile.removed for tile in self.tiles)

    def is_complete(self) -> bool:
        return self.remaining_count() == 0

    def is_selectable(self, tile_id: int) -> bool:
        """A tile is free when it is uncovered and has one open side."""
        tile = self.tile(tile_id)
        if tile.removed or self.is_covered(tile):
            return False
        return self.is_left_open(tile) or self.is_right_open(tile)

    def selectable_tiles(self) -> list[Tile]:
        return [tile for tile in self.active_tiles() if self.is_selectable(tile.id)]

    def is_covered(self, tile: Tile) -> bool:
        """Check whether any higher tile overlaps this tile's 2x2 footprint."""
        return any(
            other.z > tile.z and rects_overlap(tile.coord, other.coord)
            for other in self.active_tiles()
            if other.id != tile.id
        )

    def is_left_open(self, tile: Tile) -> bool:
        return not any(
            other.z == tile.z
            and other.x + TILE_SPAN == tile.x
            and vertical_overlap(other.coord, tile.coord)
            for other in self.active_tiles()
            if other.id != tile.id
        )

    def is_right_open(self, tile: Tile) -> bool:
        return not any(
            other.z == tile.z
            and tile.x + TILE_SPAN == other.x
            and vertical_overlap(other.coord, tile.coord)
            for other in self.active_tiles()
            if other.id != tile.id
        )

    def can_match(self, first_id: int, second_id: int) -> bool:
        """Apply classic Mahjong Solitaire matching rules."""
        if first_id == second_id:
            return False
        first = self.tile(first_id)
        second = self.tile(second_id)
        if first.removed or second.removed:
            return False
        if first.match_group in {"flower", "season"}:
            return first.match_group == second.match_group
        return first.face == second.face and first.match_group == second.match_group

    def legal_pairs(self) -> list[tuple[int, int]]:
        selectable = self.selectable_tiles()
        return [
            (first.id, second.id)
            for first, second in combinations(selectable, 2)
            if self.can_match(first.id, second.id)
        ]

    def remove_pair(self, first_id: int, second_id: int) -> Move:
        """Remove a legal pair and return a Move object for undo."""
        if not self.is_selectable(first_id) or not self.is_selectable(second_id):
            raise ValueError("Both tiles must be selectable before removal.")
        if not self.can_match(first_id, second_id):
            raise ValueError("Tiles do not match.")
        self.tile(first_id).removed = True
        self.tile(second_id).removed = True
        return Move(first_id=first_id, second_id=second_id)

    def restore_pair(self, move: Move) -> None:
        self.tile(move.first_id).removed = False
        self.tile(move.second_id).removed = False

    def has_legal_pair(self) -> bool:
        return bool(self.legal_pairs())

    def is_deadlocked(self) -> bool:
        """Deadlock means tiles remain but no legal matching pair exists."""
        return self.remaining_count() > 0 and not self.has_legal_pair()


def rects_overlap(first: Coord, second: Coord) -> bool:
    """Return True when two tile footprints overlap in x/y space."""
    return (
        first.x < second.x + TILE_SPAN
        and first.x + TILE_SPAN > second.x
        and first.y < second.y + TILE_SPAN
        and first.y + TILE_SPAN > second.y
    )


def vertical_overlap(first: Coord, second: Coord) -> bool:
    """Side blocking only matters when neighboring tiles overlap vertically."""
    return first.y < second.y + TILE_SPAN and first.y + TILE_SPAN > second.y
