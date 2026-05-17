# AGENTS.md

This file gives future agents the project context needed to work on this repo
without rediscovering the basics.

## Project Overview

This is a Python 3.14 Mahjong Solitaire desktop game managed with uv. The game
uses `pygame-ce` and imports it as `pygame`.

Current 1.0 scope:

- English UI.
- Mouse-first desktop play.
- Easy Pyramid, Medium Turtle, and Hard Dragon difficulties.
- One fixed classic coordinate template per difficulty.
- Guaranteed-solvable generated boards.
- Hint, undo, invalid-click feedback, deadlock modal, and win modal.
- Programmatically drawn tile art; no external image assets.

Out of scope for 1.0:

- Scoring, save/load, sound, packaged app export.
- Multiple layouts per difficulty.
- External image assets.

## Commands

Use a project-local uv cache. The default user-level uv cache may be blocked in
sandboxed sessions.

Run the game:

```bash
UV_CACHE_DIR=.uv-cache uv run python main.py
```

Run tests:

```bash
UV_CACHE_DIR=.uv-cache uv run python -m unittest discover -s tests
```

Headless Pygame smoke check:

```bash
UV_CACHE_DIR=.uv-cache SDL_VIDEODRIVER=dummy uv run python -c "from mahjong_solitaire.app import MahjongApp; import time, pygame; app=MahjongApp(); [app.start_game(k) or app.draw(time.monotonic()) for k in ('easy','medium','hard')]; print('pygame smoke ok', app.board.remaining_count()); pygame.quit()"
```

## Code Map

- `main.py`: Root entrypoint. Starts `MahjongApp`.
- `mahjong_solitaire/core.py`: Testable game rules and data objects:
  `Coord`, `Tile`, `Move`, `Level`, `Board`.
- `mahjong_solitaire/levels.py`: Fixed Easy/Medium/Hard coordinate templates.
- `mahjong_solitaire/generator.py`: Board generation, face assignment, and
  solution validation.
- `mahjong_solitaire/app.py`: Pygame UI, input handling, rendering, modals, and
  game state transitions.
- `tests/test_core.py`: Unit coverage for selection rules, matching, deadlock,
  undo, and generated board solvability.

## Core Rules

Tile coordinates use `(x, y, z)`. Each tile occupies a 2x2 logical footprint.

A tile is selectable only when:

- It is not removed.
- No active tile on a higher `z` overlaps its footprint.
- At least one horizontal side is open: no same-layer neighbor directly touching
  its left side or right side with vertical overlap.

Matching rules:

- Suits, winds, and dragons match only identical face plus group.
- Flowers match any other flower.
- Seasons match any other season.

Deadlock is defined as remaining tiles > 0 and no legal selectable matching pair.

## Generation Contract

`generate_board(level)` must return a board that has at least one known solution
path. It currently builds a randomized open-pair removal sequence from the blank
layout, assigns Mahjong faces to that sequence, then validates the solution path
before returning. Different seeds should produce different pair coordinates and
face placement.

Do not weaken this contract. If level templates change, keep the generator tests
passing for all difficulties.

Current layout sizes:

- Easy Pyramid: 72 tiles.
- Medium Turtle: 144 tiles.
- Hard Dragon: 144 tiles.

## UI Notes

The Pygame app uses a fixed `1280x800` window. Rendering is intentionally
programmatic: rounded tiles, shadows, face labels, selection outlines, hint
outlines, and invalid-click flash feedback are all drawn in code.

The player-facing text is English. Keep future UI text English unless the user
explicitly asks to localize it.

## Development Guidance

- Keep rule logic independent from Pygame where practical; add unit tests for
  rule or generator changes.
- Prefer small, direct modules over extra framework structure.
- Keep `main.py` as the root run target.
- Use uv for dependency changes and commit the updated `uv.lock`.
- `.uv-cache/` and `.venv/` are local artifacts and should stay ignored.
- Before handing off substantial changes, run the unittest command above.

## Git Guidance

The user has allowed local Git commits at appropriate milestones. Use concise
semantic commit messages, for example:

- `feat: implement playable mahjong solitaire`
- `test: add board generation coverage`
- `docs: document agent handoff context`

Before committing, inspect `git status --short` and avoid including unrelated
user changes.
