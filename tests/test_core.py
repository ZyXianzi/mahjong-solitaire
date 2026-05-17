import unittest

from mahjong_solitaire.core import Board, Coord, Tile
from mahjong_solitaire.generator import generate_board, validate_solution_path
from mahjong_solitaire.levels import LEVELS


def tile(tile_id, face, group, x, y, z=0):
    return Tile(tile_id, face, group, Coord(x, y, z))


class BoardRuleTests(unittest.TestCase):
    def test_side_blocking_and_open_side_selection(self):
        board = Board(
            [
                tile(1, "1M", "characters", 0, 0),
                tile(2, "2M", "characters", 2, 0),
                tile(3, "3M", "characters", 4, 0),
            ]
        )

        self.assertTrue(board.is_selectable(1))
        self.assertFalse(board.is_selectable(2))
        self.assertTrue(board.is_selectable(3))

    def test_top_coverage_blocks_selection(self):
        board = Board(
            [
                tile(1, "1M", "characters", 0, 0, 0),
                tile(2, "2M", "characters", 0, 0, 1),
            ]
        )

        self.assertFalse(board.is_selectable(1))
        self.assertTrue(board.is_selectable(2))

    def test_classic_matching_rules(self):
        board = Board(
            [
                tile(1, "1M", "characters", 0, 0),
                tile(2, "1M", "characters", 4, 0),
                tile(3, "Plum", "flower", 0, 4),
                tile(4, "Orch", "flower", 4, 4),
                tile(5, "Spr", "season", 0, 8),
                tile(6, "Sum", "season", 4, 8),
                tile(7, "2M", "characters", 8, 0),
            ]
        )

        self.assertTrue(board.can_match(1, 2))
        self.assertTrue(board.can_match(3, 4))
        self.assertTrue(board.can_match(5, 6))
        self.assertFalse(board.can_match(1, 7))
        self.assertFalse(board.can_match(3, 5))

    def test_legal_pairs_deadlock_and_undo(self):
        board = Board(
            [
                tile(1, "1M", "characters", 0, 0),
                tile(2, "1M", "characters", 4, 0),
                tile(3, "2M", "characters", 0, 4),
                tile(4, "3M", "characters", 4, 4),
            ]
        )

        self.assertEqual(board.legal_pairs(), [(1, 2)])
        move = board.remove_pair(1, 2)
        self.assertTrue(board.is_deadlocked())
        board.restore_pair(move)
        self.assertEqual(board.remaining_count(), 4)
        self.assertFalse(board.is_deadlocked())


class GeneratorTests(unittest.TestCase):
    def test_all_levels_generate_valid_solution_paths(self):
        for key, level in LEVELS.items():
            with self.subTest(level=key):
                board, solution = generate_board(level, seed=7)
                self.assertEqual(board.remaining_count(), len(level.coords))
                self.assertEqual(len(solution) * 2, len(level.coords))
                self.assertTrue(validate_solution_path(board, solution))

    def test_level_sizes_match_prd_scale(self):
        self.assertEqual(len(LEVELS["easy"].coords), 36)
        self.assertEqual(len(LEVELS["medium"].coords), 72)
        self.assertEqual(len(LEVELS["hard"].coords), 144)


if __name__ == "__main__":
    unittest.main()
