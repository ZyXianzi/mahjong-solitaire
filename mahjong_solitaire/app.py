from __future__ import annotations

import math
import time
from dataclasses import dataclass
from enum import Enum

import pygame

from .core import Board, Move, Tile
from .generator import generate_board
from .levels import LEVELS


WINDOW_SIZE = (1280, 800)
FPS = 60
TILE_WIDTH = 58
TILE_HEIGHT = 74
CELL_WIDTH = TILE_WIDTH // 2
CELL_HEIGHT = TILE_HEIGHT // 2
LAYER_DX = 8
LAYER_DY = 8
BOARD_TOP = 112


class ScreenState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    DEADLOCK = "deadlock"
    WON = "won"
    ERROR = "error"


@dataclass
class Button:
    label: str
    rect: pygame.Rect
    action: str
    enabled: bool = True


class MahjongApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Mahjong Solitaire")
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("arial", 54, bold=True)
        self.large_font = pygame.font.SysFont("arial", 34, bold=True)
        self.font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 17)
        self.state = ScreenState.MENU
        self.running = True
        self.board: Board | None = None
        self.solution: list[tuple[int, int]] = []
        self.current_level = "easy"
        self.selected_id: int | None = None
        self.hint_pair: tuple[int, int] | None = None
        self.history: list[Move] = []
        self.start_time = time.monotonic()
        self.elapsed_at_end = 0
        self.moves_made = 0
        self.hints_used = 0
        self.status_text = ""
        self.status_until = 0.0
        self.flash_tiles: dict[int, float] = {}
        self.tile_rects: dict[int, pygame.Rect] = {}
        self.error_message = ""

    def run(self) -> None:
        while self.running:
            now = time.monotonic()
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw(now)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def start_game(self, level_key: str) -> None:
        self.current_level = level_key
        try:
            self.board, self.solution = generate_board(LEVELS[level_key])
        except RuntimeError as exc:
            self.error_message = str(exc)
            self.state = ScreenState.ERROR
            return
        self.selected_id = None
        self.hint_pair = None
        self.history = []
        self.start_time = time.monotonic()
        self.elapsed_at_end = 0
        self.moves_made = 0
        self.hints_used = 0
        self.status_text = "Find a matching free pair."
        self.status_until = time.monotonic() + 2.0
        self.flash_tiles = {}
        self.state = ScreenState.PLAYING

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos
        if self.state == ScreenState.MENU:
            self.handle_menu_click(pos)
        elif self.state == ScreenState.PLAYING:
            self.handle_play_click(pos)
        elif self.state in {ScreenState.DEADLOCK, ScreenState.WON, ScreenState.ERROR}:
            self.handle_modal_click(pos)

    def handle_menu_click(self, pos: tuple[int, int]) -> None:
        for button in self.menu_buttons():
            if button.rect.collidepoint(pos):
                if button.action == "quit":
                    self.running = False
                else:
                    self.start_game(button.action)

    def handle_play_click(self, pos: tuple[int, int]) -> None:
        for button in self.toolbar_buttons():
            if button.enabled and button.rect.collidepoint(pos):
                self.invoke_action(button.action)
                return
        tile = self.tile_at_pos(pos)
        if tile is None:
            return
        self.click_tile(tile)

    def handle_modal_click(self, pos: tuple[int, int]) -> None:
        for button in self.modal_buttons():
            if not button.enabled or not button.rect.collidepoint(pos):
                continue
            self.invoke_action(button.action)

    def invoke_action(self, action: str) -> None:
        if action == "hint":
            self.show_hint()
        elif action == "undo":
            self.undo()
        elif action == "restart":
            self.start_game(self.current_level)
        elif action == "menu":
            self.state = ScreenState.MENU
        elif action == "play_again":
            self.start_game(self.current_level)
        elif action == "quit":
            self.running = False

    def click_tile(self, tile: Tile) -> None:
        assert self.board is not None
        if not self.board.is_selectable(tile.id):
            self.flash(tile.id, "That tile is blocked.")
            return

        if self.selected_id is None:
            self.selected_id = tile.id
            self.hint_pair = None
            return

        if self.selected_id == tile.id:
            self.selected_id = None
            return

        if self.board.can_match(self.selected_id, tile.id):
            move = self.board.remove_pair(self.selected_id, tile.id)
            self.history.append(move)
            self.selected_id = None
            self.hint_pair = None
            self.moves_made += 1
            if self.board.is_complete():
                self.elapsed_at_end = int(time.monotonic() - self.start_time)
                self.state = ScreenState.WON
            elif self.board.is_deadlocked():
                self.status("No moves available.")
                self.state = ScreenState.DEADLOCK
            return

        old_selection = self.selected_id
        self.selected_id = tile.id
        self.flash_tiles[old_selection] = time.monotonic() + 0.35
        self.flash_tiles[tile.id] = time.monotonic() + 0.35
        self.status("Tiles do not match.")

    def show_hint(self) -> None:
        assert self.board is not None
        pairs = self.board.legal_pairs()
        if not pairs:
            self.status("No moves available.")
            self.state = ScreenState.DEADLOCK
            return
        self.hint_pair = pairs[0]
        self.selected_id = None
        self.hints_used += 1
        self.status("Hint highlighted.")

    def undo(self) -> None:
        if self.board is None or not self.history:
            self.status("Nothing to undo.")
            return
        move = self.history.pop()
        self.board.restore_pair(move)
        self.selected_id = None
        self.hint_pair = None
        self.state = ScreenState.PLAYING
        self.status("Move undone.")

    def flash(self, tile_id: int, message: str) -> None:
        self.flash_tiles[tile_id] = time.monotonic() + 0.45
        self.status(message)

    def status(self, message: str, seconds: float = 1.7) -> None:
        self.status_text = message
        self.status_until = time.monotonic() + seconds

    def tile_at_pos(self, pos: tuple[int, int]) -> Tile | None:
        if self.board is None:
            return None
        for tile in sorted(
            self.board.active_tiles(),
            key=lambda item: (item.coord.z, item.coord.y, item.coord.x),
            reverse=True,
        ):
            rect = self.tile_rects.get(tile.id)
            if rect and rect.collidepoint(pos):
                return tile
        return None

    def draw(self, now: float) -> None:
        self.screen.fill((35, 83, 80))
        if self.state == ScreenState.MENU:
            self.draw_menu()
        else:
            self.draw_game(now)
            if self.state in {ScreenState.DEADLOCK, ScreenState.WON, ScreenState.ERROR}:
                self.draw_modal()

    def draw_menu(self) -> None:
        title = self.title_font.render("Mahjong Solitaire", True, (248, 242, 226))
        self.screen.blit(title, title.get_rect(center=(WINDOW_SIZE[0] // 2, 150)))
        subtitle = self.font.render("Choose a difficulty", True, (208, 226, 218))
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_SIZE[0] // 2, 215)))
        for button in self.menu_buttons():
            self.draw_button(button)

    def draw_game(self, now: float) -> None:
        self.draw_toolbar(now)
        if self.board is None:
            return
        self.compute_tile_rects()
        for tile in sorted(self.board.active_tiles(), key=lambda item: (item.coord.z, item.coord.y, item.coord.x)):
            self.draw_tile(tile, now)
        if now < self.status_until:
            text = self.font.render(self.status_text, True, (255, 238, 172))
            self.screen.blit(text, (40, WINDOW_SIZE[1] - 44))

    def draw_toolbar(self, now: float) -> None:
        pygame.draw.rect(self.screen, (22, 47, 50), pygame.Rect(0, 0, WINDOW_SIZE[0], 88))
        title = self.large_font.render(LEVELS[self.current_level].name, True, (248, 242, 226))
        self.screen.blit(title, (34, 22))
        remaining = self.board.remaining_count() if self.board else 0
        elapsed = self.elapsed_at_end if self.state == ScreenState.WON else int(now - self.start_time)
        stats = f"Tiles: {remaining}    Moves: {self.moves_made}    Hints: {self.hints_used}    Time: {format_time(elapsed)}"
        stats_text = self.font.render(stats, True, (208, 226, 218))
        self.screen.blit(stats_text, (180, 34))
        for button in self.toolbar_buttons():
            self.draw_button(button)

    def compute_tile_rects(self) -> None:
        assert self.board is not None
        coords = [tile.coord for tile in self.board.tiles]
        min_x = min(coord.x * CELL_WIDTH - coord.z * LAYER_DX for coord in coords)
        max_x = max(coord.x * CELL_WIDTH - coord.z * LAYER_DX + TILE_WIDTH for coord in coords)
        min_y = min(coord.y * CELL_HEIGHT - coord.z * LAYER_DY for coord in coords)
        max_y = max(coord.y * CELL_HEIGHT - coord.z * LAYER_DY + TILE_HEIGHT for coord in coords)
        board_w = max_x - min_x
        board_h = max_y - min_y
        origin_x = (WINDOW_SIZE[0] - board_w) // 2 - min_x
        origin_y = BOARD_TOP + (WINDOW_SIZE[1] - BOARD_TOP - 72 - board_h) // 2 - min_y
        self.tile_rects = {}
        for tile in self.board.tiles:
            x = origin_x + tile.coord.x * CELL_WIDTH - tile.coord.z * LAYER_DX
            y = origin_y + tile.coord.y * CELL_HEIGHT - tile.coord.z * LAYER_DY
            self.tile_rects[tile.id] = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)

    def draw_tile(self, tile: Tile, now: float) -> None:
        assert self.board is not None
        rect = self.tile_rects[tile.id].copy()
        if tile.id in self.flash_tiles and now < self.flash_tiles[tile.id]:
            rect.x += int(math.sin(now * 70) * 4)
        shadow = rect.move(5, 7)
        pygame.draw.rect(self.screen, (15, 36, 37), shadow, border_radius=7)
        base = (241, 232, 205) if self.board.is_selectable(tile.id) else (193, 191, 176)
        pygame.draw.rect(self.screen, base, rect, border_radius=7)
        pygame.draw.rect(self.screen, (112, 95, 72), rect, width=2, border_radius=7)
        inner = rect.inflate(-9, -9)
        pygame.draw.rect(self.screen, (252, 248, 235), inner, border_radius=4)

        if self.selected_id == tile.id:
            pygame.draw.rect(self.screen, (245, 191, 66), rect.inflate(6, 6), width=4, border_radius=9)
        if self.hint_pair and tile.id in self.hint_pair:
            pygame.draw.rect(self.screen, (93, 198, 138), rect.inflate(7, 7), width=4, border_radius=9)
        if tile.id in self.flash_tiles and now < self.flash_tiles[tile.id]:
            pygame.draw.rect(self.screen, (222, 82, 70), rect.inflate(8, 8), width=4, border_radius=9)

        color = face_color(tile.match_group)
        label = self.small_font.render(tile.face, True, color)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_modal(self) -> None:
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 125))
        self.screen.blit(overlay, (0, 0))
        rect = pygame.Rect(0, 0, 460, 270)
        rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        pygame.draw.rect(self.screen, (248, 242, 226), rect, border_radius=8)
        pygame.draw.rect(self.screen, (42, 53, 52), rect, width=3, border_radius=8)

        if self.state == ScreenState.WON:
            title = "Board Cleared"
            elapsed = format_time(self.elapsed_at_end)
            body = f"Time: {elapsed}    Moves: {self.moves_made}    Hints: {self.hints_used}"
        elif self.state == ScreenState.ERROR:
            title = "Could Not Start"
            body = self.error_message
        else:
            title = "No Moves Available"
            body = "Undo the last move or exit to the menu."
        title_surf = self.large_font.render(title, True, (42, 53, 52))
        body_surf = self.font.render(body, True, (70, 83, 80))
        self.screen.blit(title_surf, title_surf.get_rect(center=(rect.centerx, rect.y + 66)))
        self.screen.blit(body_surf, body_surf.get_rect(center=(rect.centerx, rect.y + 118)))
        for button in self.modal_buttons():
            self.draw_button(button)

    def draw_button(self, button: Button) -> None:
        if button.enabled:
            fill = (232, 190, 88)
            border = (95, 72, 43)
            text_color = (38, 38, 34)
        else:
            fill = (130, 134, 125)
            border = (78, 82, 78)
            text_color = (80, 80, 76)
        pygame.draw.rect(self.screen, fill, button.rect, border_radius=7)
        pygame.draw.rect(self.screen, border, button.rect, width=2, border_radius=7)
        label = self.font.render(button.label, True, text_color)
        self.screen.blit(label, label.get_rect(center=button.rect.center))

    def menu_buttons(self) -> list[Button]:
        x = WINDOW_SIZE[0] // 2 - 130
        return [
            Button("Easy", pygame.Rect(x, 285, 260, 56), "easy"),
            Button("Medium", pygame.Rect(x, 365, 260, 56), "medium"),
            Button("Hard", pygame.Rect(x, 445, 260, 56), "hard"),
            Button("Quit", pygame.Rect(x, 545, 260, 56), "quit"),
        ]

    def toolbar_buttons(self) -> list[Button]:
        right = WINDOW_SIZE[0] - 34
        width = 104
        gap = 12
        labels = [
            ("Hint", "hint", True),
            ("Undo", "undo", bool(self.history)),
            ("Restart", "restart", True),
            ("Menu", "menu", True),
        ]
        buttons: list[Button] = []
        x = right - len(labels) * width - (len(labels) - 1) * gap
        for label, action, enabled in labels:
            buttons.append(Button(label, pygame.Rect(x, 24, width, 42), action, enabled))
            x += width + gap
        return buttons

    def modal_buttons(self) -> list[Button]:
        y = WINDOW_SIZE[1] // 2 + 62
        if self.state == ScreenState.WON:
            return [
                Button("Play Again", pygame.Rect(WINDOW_SIZE[0] // 2 - 190, y, 170, 46), "play_again"),
                Button("Menu", pygame.Rect(WINDOW_SIZE[0] // 2 + 20, y, 170, 46), "menu"),
            ]
        if self.state == ScreenState.ERROR:
            return [Button("Menu", pygame.Rect(WINDOW_SIZE[0] // 2 - 85, y, 170, 46), "menu")]
        return [
            Button(
                "Undo Last Move",
                pygame.Rect(WINDOW_SIZE[0] // 2 - 205, y, 190, 46),
                "undo",
                bool(self.history),
            ),
            Button("Exit to Menu", pygame.Rect(WINDOW_SIZE[0] // 2 + 15, y, 190, 46), "menu"),
        ]


def face_color(group: str) -> tuple[int, int, int]:
    if group == "characters":
        return (166, 45, 43)
    if group == "bamboo":
        return (30, 112, 73)
    if group == "dots":
        return (42, 79, 159)
    if group == "wind":
        return (54, 64, 68)
    if group == "dragon":
        return (143, 45, 86)
    return (112, 76, 35)


def format_time(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes:02d}:{secs:02d}"

