# 2048 in Python (Pygame)

A small desktop clone of 2048 built with Pygame. The game runs in a single window, uses the classic 4x4 board, and keeps the core rules simple: slide tiles with the arrow keys, merge matching values, and try to reach 2048 before the board fills up.

## Gameplay
- The board is a 4x4 grid of numbered tiles.
- Use the arrow keys to move every tile in one direction at once.
- Matching tiles merge into a single tile with double the value.
- After each valid move, a new tile spawns as a 2 or 4.

## What the app includes
- Real-time keyboard input with Pygame.
- Random tile generation after successful moves.
- Color-coded tiles for higher values.
- Lightweight single-file implementation that is easy to read and extend.

## Requirements
- Python 3
- Pygame

## Install
```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python app.pyw
```