# Mahjong Solitaire

A playable Python/Pygame Mahjong Solitaire game managed with uv.

## Setup

The project is initialized with uv and targets Python 3.14. Use a project-local uv
cache in this workspace:

```bash
UV_CACHE_DIR=.uv-cache uv run python main.py
```

## Gameplay

- Click `Start Game`, then choose a difficulty tab and layout card.
- Each difficulty currently has three selectable layouts:
  Easy Pyramid, Easy Arena, Easy Cross, Medium Turtle, Medium Bridge,
  Medium Fortress, Hard Dragon, Hard Castle, and Hard Spider.
- Click two free matching Mahjong tiles to remove them.
- A tile is free when no tile covers it and its left or right side is open.
- Suits, winds, and dragons match identical faces.
- Flower tiles match any flower tile; season tiles match any season tile.
- `Hint` highlights one legal pair.
- `Undo` restores the previous removed pair.
- `Restart` starts the current difficulty again.
- `Menu` exits the current board and returns to layout selection.

If no legal pair remains, the game shows a `No Moves Available` modal. You can
undo the last move or exit to the menu. Clearing every tile shows the completion
modal with time, move count, and hint count.

## Version 1.0 Scope

- English UI.
- Mouse-first controls.
- Main menu, tabbed layout selection, and polished in-game table UI.
- Three guaranteed-solvable fixed board templates for each difficulty.
- Board generation randomizes the removable pair sequence, so repeated games do
  not use the same mirrored face placement.
- Mahjong tile PNG assets with padded face art and real flower / season tile
  images.
- Programmatically drawn buttons, previews, highlights, and effects.
- No scoring, save/load, sound, or packaged app export yet.

## Art Credits

Suited and honor tile art comes from
[FluffyStuff/riichi-mahjong-tiles](https://github.com/FluffyStuff/riichi-mahjong-tiles),
which publishes those assets in the public domain. Flower and season tile art is
cropped from Wikimedia Commons `Flowers mahjong.png` by Cangjie6 under CC
BY-SA 4.0. See `assets/tiles/ATTRIBUTION.md`.

## Tests

```bash
UV_CACHE_DIR=.uv-cache uv run python -m unittest discover -s tests
```
