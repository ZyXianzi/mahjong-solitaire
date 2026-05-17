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
DIFFICULTIES = ("easy", "medium", "hard")
DIFFICULTY_LABELS = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
LEVEL_OPTIONS = {
    "easy": ("easy", "easy_arena", "easy_cross"),
    "medium": ("medium", "medium_bridge", "medium_fortress"),
    "hard": ("hard", "hard_castle", "hard_spider"),
}
LEVEL_SELECT_SIDEBAR = pygame.Rect(64, 154, 220, 526)
LEVEL_SELECT_CONTENT = pygame.Rect(320, 154, 896, 526)
LEVEL_CARD_SIZE = (264, 344)

BG_TOP = (11, 30, 38)
BG_BOTTOM = (28, 91, 82)
PANEL = (16, 44, 51)
PANEL_LIGHT = (25, 69, 72)
GOLD = (229, 184, 82)
GOLD_LIGHT = (246, 205, 101)
GOLD_DARK = (139, 101, 44)
TEXT = (248, 242, 226)
MUTED_TEXT = (187, 209, 201)
INK = (37, 41, 39)


class ScreenState(Enum):
    MENU = "menu"
    LEVEL_SELECT = "level_select"
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
    variant: str = "primary"


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    born: float
    lifetime: float


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
        self.selected_difficulty = "easy"
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
        self.particles: list[Particle] = []

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
        elif self.state == ScreenState.LEVEL_SELECT:
            self.handle_level_select_click(pos)
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
                    self.invoke_action(button.action)

    def handle_level_select_click(self, pos: tuple[int, int]) -> None:
        for button in self.level_select_buttons():
            if button.enabled and button.rect.collidepoint(pos):
                self.invoke_action(button.action)
                return

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
        elif action == "level_select":
            self.state = ScreenState.LEVEL_SELECT
        elif action.startswith("tab:"):
            self.selected_difficulty = action.split(":", 1)[1]
        elif action.startswith("level:"):
            self.start_game(action.split(":", 1)[1])
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
            first_rect = self.tile_rects.get(self.selected_id)
            second_rect = self.tile_rects.get(tile.id)
            move = self.board.remove_pair(self.selected_id, tile.id)
            self.history.append(move)
            if first_rect and second_rect:
                self.add_remove_burst(first_rect.center, second_rect.center)
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
        self.moves_made = max(0, self.moves_made - 1)
        self.state = ScreenState.PLAYING
        self.status("Move undone.")

    def flash(self, tile_id: int, message: str) -> None:
        self.flash_tiles[tile_id] = time.monotonic() + 0.45
        self.status(message)

    def status(self, message: str, seconds: float = 1.7) -> None:
        self.status_text = message
        self.status_until = time.monotonic() + seconds

    def add_remove_burst(
        self, first: tuple[int, int], second: tuple[int, int]
    ) -> None:
        now = time.monotonic()
        vectors = ((-36, -36), (-18, -48), (16, -44), (34, -28), (24, 10), (-26, 12))
        for center in (first, second):
            for vx, vy in vectors:
                self.particles.append(
                    Particle(
                        x=float(center[0]),
                        y=float(center[1]),
                        vx=vx,
                        vy=vy,
                        color=GOLD_LIGHT,
                        born=now,
                        lifetime=0.45,
                    )
                )

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
        self.draw_background()
        if self.state == ScreenState.MENU:
            self.draw_menu(now)
        elif self.state == ScreenState.LEVEL_SELECT:
            self.draw_level_select()
        else:
            self.draw_game(now)
            if self.state in {ScreenState.DEADLOCK, ScreenState.WON, ScreenState.ERROR}:
                self.draw_modal()

    def draw_background(self) -> None:
        height = WINDOW_SIZE[1]
        for y in range(0, height, 4):
            t = y / height
            color = tuple(
                int(BG_TOP[index] * (1 - t) + BG_BOTTOM[index] * t)
                for index in range(3)
            )
            pygame.draw.rect(self.screen, color, pygame.Rect(0, y, WINDOW_SIZE[0], 4))
        for x in range(60, WINDOW_SIZE[0], 120):
            pygame.draw.line(self.screen, (31, 103, 94), (x, 92), (x - 220, 800), 1)

    def draw_menu(self, now: float) -> None:
        glow_alpha = int(34 + 20 * math.sin(now * 1.5))
        glow = pygame.Surface((620, 190), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (235, 198, 118, glow_alpha), glow.get_rect())
        self.screen.blit(glow, glow.get_rect(center=(WINDOW_SIZE[0] // 2, 178)))

        title = self.title_font.render("Mahjong Solitaire", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(WINDOW_SIZE[0] // 2, 158)))
        subtitle = self.font.render("A quiet tile-matching table", True, MUTED_TEXT)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_SIZE[0] // 2, 222)))
        for button in self.menu_buttons():
            self.draw_button(button)

    def draw_level_select(self) -> None:
        title = self.large_font.render("Select Layout", True, TEXT)
        self.screen.blit(title, (64, 54))
        subtitle = self.font.render("Choose a difficulty tab, then start a layout.", True, MUTED_TEXT)
        self.screen.blit(subtitle, (64, 98))

        pygame.draw.rect(self.screen, PANEL, LEVEL_SELECT_SIDEBAR, border_radius=10)
        pygame.draw.rect(self.screen, (51, 112, 105), LEVEL_SELECT_SIDEBAR, width=2, border_radius=10)

        pygame.draw.rect(self.screen, (238, 231, 211), LEVEL_SELECT_CONTENT, border_radius=12)
        pygame.draw.rect(self.screen, (94, 116, 104), LEVEL_SELECT_CONTENT, width=2, border_radius=12)

        self.draw_layout_cards()
        for button in self.level_select_buttons():
            self.draw_button(button)

    def draw_layout_cards(self) -> None:
        keys = LEVEL_OPTIONS[self.selected_difficulty]
        gap = 24
        card_w, card_h = LEVEL_CARD_SIZE
        total_w = len(keys) * card_w + max(0, len(keys) - 1) * gap
        start_x = LEVEL_SELECT_CONTENT.centerx - total_w // 2
        card_y = LEVEL_SELECT_CONTENT.y + 64
        for index, level_key in enumerate(keys):
            level = LEVELS[level_key]
            card = pygame.Rect(
                start_x + index * (card_w + gap),
                card_y,
                card_w,
                card_h,
            )
            pygame.draw.rect(self.screen, (250, 246, 232), card, border_radius=10)
            pygame.draw.rect(self.screen, (152, 130, 86), card, width=2, border_radius=10)
            self.draw_level_preview(level_key, pygame.Rect(card.x + 24, card.y + 24, 216, 156))
            title = self.large_font.render(level.name.split(" ", 1)[1], True, INK)
            self.screen.blit(title, (card.x + 24, card.y + 202))
            meta = f"{len(level.coords)} tiles"
            meta_surf = self.font.render(meta, True, (88, 100, 94))
            self.screen.blit(meta_surf, (card.x + 24, card.y + 246))

    def draw_level_preview(self, level_key: str, rect: pygame.Rect) -> None:
        coords = LEVELS[level_key].coords
        min_x = min(coord.x for coord in coords)
        max_x = max(coord.x for coord in coords)
        min_y = min(coord.y for coord in coords)
        max_y = max(coord.y for coord in coords)
        span_x = max(1, max_x - min_x + 2)
        span_y = max(1, max_y - min_y + 2)
        scale = min(rect.width / span_x, rect.height / span_y)
        tile_w = max(5, int(scale * 1.75))
        tile_h = max(7, int(scale * 1.9))
        ox = rect.centerx - span_x * scale / 2
        oy = rect.centery - span_y * scale / 2
        pygame.draw.rect(self.screen, (29, 82, 76), rect, border_radius=8)
        for coord in sorted(coords, key=lambda item: (item.z, item.y, item.x)):
            x = ox + (coord.x - min_x) * scale - coord.z * 2
            y = oy + (coord.y - min_y) * scale - coord.z * 2
            mini = pygame.Rect(int(x), int(y), tile_w, tile_h)
            pygame.draw.rect(self.screen, (244, 234, 202), mini, border_radius=2)
            pygame.draw.rect(self.screen, (115, 99, 73), mini, width=1, border_radius=2)

    def draw_game(self, now: float) -> None:
        self.draw_toolbar(now)
        if self.board is None:
            return
        self.compute_tile_rects()
        for tile in sorted(self.board.active_tiles(), key=lambda item: (item.coord.z, item.coord.y, item.coord.x)):
            self.draw_tile(tile, now)
        self.draw_particles(now)
        if now < self.status_until:
            self.draw_status_bar()

    def draw_toolbar(self, now: float) -> None:
        pygame.draw.rect(self.screen, PANEL, pygame.Rect(0, 0, WINDOW_SIZE[0], 88))
        pygame.draw.line(self.screen, (51, 113, 105), (0, 87), (WINDOW_SIZE[0], 87), 2)
        title = self.large_font.render(LEVELS[self.current_level].name, True, TEXT)
        self.screen.blit(title, (34, 22))
        remaining = self.board.remaining_count() if self.board else 0
        elapsed = self.elapsed_at_end if self.state == ScreenState.WON else int(now - self.start_time)
        stats = f"Tiles: {remaining}    Moves: {self.moves_made}    Hints: {self.hints_used}    Time: {format_time(elapsed)}"
        stats_text = self.font.render(stats, True, MUTED_TEXT)
        stats_x = max(180, title.get_width() + 64)
        self.screen.blit(stats_text, (stats_x, 34))
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
        shadow = rect.move(6, 8)
        pygame.draw.rect(self.screen, (10, 24, 28), shadow, border_radius=7)
        hovered = rect.collidepoint(pygame.mouse.get_pos()) and self.board.is_selectable(tile.id)
        base = (252, 246, 225) if self.board.is_selectable(tile.id) else (199, 196, 180)
        if hovered:
            base = (255, 250, 234)
        pygame.draw.rect(self.screen, base, rect, border_radius=7)
        pygame.draw.rect(self.screen, (119, 95, 61), rect, width=2, border_radius=7)
        inner = rect.inflate(-9, -9)
        pygame.draw.rect(self.screen, (255, 252, 241), inner, border_radius=4)

        if self.selected_id == tile.id:
            pulse = int(2 + 2 * math.sin(now * 8))
            pygame.draw.rect(self.screen, GOLD_LIGHT, rect.inflate(8 + pulse, 8 + pulse), width=4, border_radius=9)
        if self.hint_pair and tile.id in self.hint_pair:
            pulse = int(3 + 2 * math.sin(now * 6))
            pygame.draw.rect(self.screen, (88, 210, 153), rect.inflate(8 + pulse, 8 + pulse), width=4, border_radius=9)
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
        pygame.draw.rect(self.screen, (250, 246, 232), rect, border_radius=10)
        pygame.draw.rect(self.screen, (69, 92, 86), rect, width=3, border_radius=10)

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
        title_surf = self.large_font.render(title, True, INK)
        body_surf = self.font.render(body, True, (70, 83, 80))
        self.screen.blit(title_surf, title_surf.get_rect(center=(rect.centerx, rect.y + 66)))
        self.screen.blit(body_surf, body_surf.get_rect(center=(rect.centerx, rect.y + 118)))
        for button in self.modal_buttons():
            self.draw_button(button)

    def draw_button(self, button: Button) -> None:
        hovered = button.enabled and button.rect.collidepoint(pygame.mouse.get_pos())
        if button.enabled:
            if button.variant == "tab":
                active = button.action.endswith(self.selected_difficulty)
                fill = GOLD if active else PANEL_LIGHT
                border = GOLD_DARK if active else (59, 128, 118)
                text_color = INK if active else TEXT
            elif button.variant == "secondary":
                fill = (238, 231, 211)
                border = (132, 116, 84)
                text_color = INK
            else:
                fill = GOLD_LIGHT if hovered else GOLD
                border = GOLD_DARK
                text_color = INK
        else:
            fill = (130, 134, 125)
            border = (78, 82, 78)
            text_color = (80, 80, 76)
        rect = button.rect.move(0, -2 if hovered else 0)
        pygame.draw.rect(self.screen, (9, 26, 29), rect.move(4, 5), border_radius=8)
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, width=2, border_radius=8)
        label = self.font.render(button.label, True, text_color)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def menu_buttons(self) -> list[Button]:
        x = WINDOW_SIZE[0] // 2 - 130
        return [
            Button("Start Game", pygame.Rect(x, 310, 260, 58), "level_select"),
            Button("Quit", pygame.Rect(x, 395, 260, 58), "quit", variant="secondary"),
        ]

    def level_select_buttons(self) -> list[Button]:
        buttons: list[Button] = []
        tab_x = LEVEL_SELECT_SIDEBAR.x + 24
        tab_y = LEVEL_SELECT_SIDEBAR.y + 34
        tab_w = LEVEL_SELECT_SIDEBAR.width - 48
        for index, key in enumerate(DIFFICULTIES):
            buttons.append(
                Button(
                    DIFFICULTY_LABELS[key],
                    pygame.Rect(tab_x, tab_y + index * 72, tab_w, 52),
                    f"tab:{key}",
                    variant="tab",
                )
            )
        keys = LEVEL_OPTIONS[self.selected_difficulty]
        gap = 24
        card_w, card_h = LEVEL_CARD_SIZE
        total_w = len(keys) * card_w + max(0, len(keys) - 1) * gap
        start_x = LEVEL_SELECT_CONTENT.centerx - total_w // 2
        card_y = LEVEL_SELECT_CONTENT.y + 64
        for index, level_key in enumerate(keys):
            card_x = start_x + index * (card_w + gap)
            buttons.append(
                Button(
                    "Play",
                    pygame.Rect(card_x + 24, card_y + card_h - 72, card_w - 48, 48),
                    f"level:{level_key}",
                )
            )
        buttons.append(
            Button(
                "Back",
                pygame.Rect(
                    tab_x,
                    LEVEL_SELECT_SIDEBAR.bottom - 72,
                    tab_w,
                    48,
                ),
                "menu",
                variant="secondary",
            )
        )
        return buttons

    def toolbar_buttons(self) -> list[Button]:
        right = WINDOW_SIZE[0] - 34
        width = 104
        gap = 12
        labels = [
            ("Hint", "hint", True),
            ("Undo", "undo", bool(self.history)),
            ("Restart", "restart", True),
            ("Menu", "level_select", True),
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
                Button(
                    "Play Again",
                    pygame.Rect(WINDOW_SIZE[0] // 2 - 190, y, 170, 46),
                    "play_again",
                ),
                Button(
                    "Menu",
                    pygame.Rect(WINDOW_SIZE[0] // 2 + 20, y, 170, 46),
                    "level_select",
                ),
            ]
        if self.state == ScreenState.ERROR:
            return [
                Button(
                    "Menu",
                    pygame.Rect(WINDOW_SIZE[0] // 2 - 85, y, 170, 46),
                    "level_select",
                )
            ]
        return [
            Button(
                "Undo Last Move",
                pygame.Rect(WINDOW_SIZE[0] // 2 - 205, y, 190, 46),
                "undo",
                bool(self.history),
            ),
            Button(
                "Exit to Menu",
                pygame.Rect(WINDOW_SIZE[0] // 2 + 15, y, 190, 46),
                "level_select",
            ),
        ]

    def draw_status_bar(self) -> None:
        rect = pygame.Rect(34, WINDOW_SIZE[1] - 58, 420, 38)
        pygame.draw.rect(self.screen, (18, 46, 50), rect, border_radius=8)
        pygame.draw.rect(self.screen, (53, 117, 109), rect, width=1, border_radius=8)
        text = self.font.render(self.status_text, True, (255, 238, 172))
        self.screen.blit(text, (rect.x + 14, rect.y + 7))

    def draw_particles(self, now: float) -> None:
        active: list[Particle] = []
        for particle in self.particles:
            age = now - particle.born
            if age >= particle.lifetime:
                continue
            t = age / particle.lifetime
            x = particle.x + particle.vx * t
            y = particle.y + particle.vy * t + 34 * t * t
            alpha = max(0, 180 - int(180 * t))
            surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*particle.color, alpha), (4, 4), 4)
            self.screen.blit(surface, (x - 4, y - 4))
            active.append(particle)
        self.particles = active


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
