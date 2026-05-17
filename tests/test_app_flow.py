import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from mahjong_solitaire.app import (
    LEVEL_OPTIONS,
    TILE_ASSET_DIR,
    MahjongApp,
    ScreenState,
    tile_asset_name,
)
from mahjong_solitaire.core import Board, Coord, Tile
from mahjong_solitaire.generator import build_face_pairs


class AppFlowTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_menu_and_level_select_flow(self):
        app = MahjongApp()

        self.assertEqual([button.label for button in app.menu_buttons()], ["Start Game", "Quit"])
        app.invoke_action("level_select")
        self.assertEqual(app.state, ScreenState.LEVEL_SELECT)

        tab_actions = [button.action for button in app.level_select_buttons()[:3]]
        self.assertEqual(tab_actions, ["tab:easy", "tab:medium", "tab:hard"])

        app.invoke_action("tab:hard")
        self.assertEqual(app.selected_difficulty, "hard")
        play_buttons = level_buttons(app)
        self.assertEqual(
            [button.action for button in play_buttons],
            ["level:hard", "level:hard_castle", "level:hard_spider"],
        )

        app.invoke_action("level:hard")
        self.assertEqual(app.state, ScreenState.PLAYING)
        self.assertEqual(app.current_level, "hard")
        self.assertEqual(app.board.remaining_count(), 144)

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

    def test_every_level_select_option_starts_a_board(self):
        app = MahjongApp()

        for difficulty, keys in LEVEL_OPTIONS.items():
            app.invoke_action(f"tab:{difficulty}")
            for key in keys:
                with self.subTest(level=key):
                    app.invoke_action(f"level:{key}")
                    self.assertEqual(app.state, ScreenState.PLAYING)
                    self.assertEqual(app.current_level, key)
                    self.assertIsNotNone(app.board)
                    self.assertGreater(app.board.remaining_count(), 0)

    def test_tile_art_assets_cover_all_generated_suited_and_honor_faces(self):
        for pair in build_face_pairs():
            for face, group in pair:
                tile = Tile(1, face, group, Coord(0, 0, 0))
                asset = tile_asset_name(tile)
                with self.subTest(face=face, group=group):
                    if group in {"flower", "season"}:
                        self.assertEqual(asset, "Front")
                    self.assertTrue((TILE_ASSET_DIR / f"{asset}.png").exists())

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


def level_buttons(app):
    return [
        button
        for button in app.level_select_buttons()
        if button.action.startswith("level:")
    ]


if __name__ == "__main__":
    unittest.main()
