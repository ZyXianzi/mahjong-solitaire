# Mahjong Solitaire

A playable Python/Pygame Mahjong Solitaire game managed with uv.

## Setup

The project is initialized with uv and targets Python 3.14. Use a project-local uv
cache in this workspace:

```bash
UV_CACHE_DIR=.uv-cache uv run python main.py
```

## Gameplay

- Choose Easy Bridge, Medium Fortress, or Hard Dragon from the main menu.
- Click two free matching Mahjong tiles to remove them.
- A tile is free when no tile covers it and its left or right side is open.
- Suits, winds, and dragons match identical faces.
- Flower tiles match any flower tile; season tiles match any season tile.
- `Hint` highlights one legal pair.
- `Undo` restores the previous removed pair.
- `Restart` starts the current difficulty again.
- `Menu` exits the current board.

If no legal pair remains, the game shows a `No Moves Available` modal. You can
undo the last move or exit to the menu. Clearing every tile shows the completion
modal with time, move count, and hint count.

## Version 1.0 Scope

- English UI.
- Mouse-first controls.
- One guaranteed-solvable, non-axis-symmetric board template for each difficulty.
- Board generation randomizes the removable pair sequence, so repeated games do
  not use the same mirrored face placement.
- Programmatically drawn tiles; no external image assets.
- No scoring, save/load, sound, packaged app export, or multiple layouts per
  difficulty yet.

## Tests

```bash
UV_CACHE_DIR=.uv-cache uv run python -m unittest discover -s tests
```
