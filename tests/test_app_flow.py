import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from mahjong_solitaire.app import MahjongApp, ScreenState
from mahjong_solitaire.core import Board, Coord, Tile


class AppFlowTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_level_start_hint_invalid_click_match_and_undo(self):
        app = MahjongApp()

        for key, expected_count in (("easy", 72), ("medium", 144), ("hard", 144)):
            with self.subTest(level=key):
                app.start_game(key)
                self.assertEqual(app.state, ScreenState.PLAYING)
                self.assertEqual(app.board.remaining_count(), expected_count)
                app.show_hint()
                self.assertIn(app.hint_pair, app.board.legal_pairs())

        app.start_game("easy")
        blocked = next(
            tile
            for tile in app.board.active_tiles()
            if not app.board.is_selectable(tile.id)
        )
        app.click_tile(blocked)
        self.assertEqual(app.status_text, "That tile is blocked.")

        first_id, second_id = app.board.legal_pairs()[0]
        app.click_tile(app.board.tile(first_id))
        app.click_tile(app.board.tile(second_id))
        self.assertEqual(app.board.remaining_count(), 70)
        self.assertEqual(len(app.history), 1)
        self.assertEqual(app.moves_made, 1)

        app.undo()
        self.assertEqual(app.board.remaining_count(), 72)
        self.assertEqual(len(app.history), 0)
        self.assertEqual(app.moves_made, 0)
        self.assertEqual(app.state, ScreenState.PLAYING)

    def test_deadlock_modal_and_win_path(self):
        app = MahjongApp()
        app.board = Board(
            [
                Tile(1, "1M", "characters", Coord(0, 0, 0)),
                Tile(2, "2M", "characters", Coord(4, 0, 0)),
            ]
        )
        app.history = []

        app.show_hint()
        self.assertEqual(app.state, ScreenState.DEADLOCK)
        self.assertFalse(app.modal_buttons()[0].enabled)

        app.start_game("easy")
        for first_id, second_id in app.solution:
            app.click_tile(app.board.tile(first_id))
            app.click_tile(app.board.tile(second_id))

        self.assertEqual(app.state, ScreenState.WON)
        self.assertEqual(app.board.remaining_count(), 0)


if __name__ == "__main__":
    unittest.main()
