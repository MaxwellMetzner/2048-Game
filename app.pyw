import pygame
import random

# Initialize pygame
pygame.init()

# Constants
SIZE = 4
TILE_SIZE = 100
TILE_MARGIN = 10
WIDTH = SIZE * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN
HEIGHT = WIDTH
FPS = 60

# Colors
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_TILE_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}
FONT_COLOR = (119, 110, 101)
FONT = pygame.font.Font(None, 55)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

# Initialize clock
clock = pygame.time.Clock()

# Game state
board = [[0] * SIZE for _ in range(SIZE)]
score = 0

def draw_board():
    screen.fill(BACKGROUND_COLOR)
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            rect = pygame.Rect(
                col * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN,
                row * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(screen, TILE_COLORS.get(value, EMPTY_TILE_COLOR), rect)
            if value != 0:
                text = FONT.render(str(value), True, FONT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

def add_new_tile():
    empty_tiles = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if empty_tiles:
        row, col = random.choice(empty_tiles)
        board[row][col] = 2 if random.random() < 0.9 else 4

def slide_row_left(row):
    new_row = [i for i in row if i != 0]
    new_row += [0] * (SIZE - len(new_row))
    for i in range(SIZE - 1):
        if new_row[i] == new_row[i + 1] and new_row[i] != 0:
            new_row[i] *= 2
            new_row[i + 1] = 0
            global score
            score += new_row[i]
    new_row = [i for i in new_row if i != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row

def rotate_board_clockwise():
    global board
    board = [list(row) for row in zip(*board[::-1])]

def move_left():
    global board
    new_board = [slide_row_left(row) for row in board]
    if new_board != board:
        board = new_board
        add_new_tile()

def move_right():
    global board
    board = [row[::-1] for row in board]
    move_left()
    board = [row[::-1] for row in board]

def move_up():
    global board
    rotate_board_clockwise()
    rotate_board_clockwise()
    rotate_board_clockwise()
    move_left()
    rotate_board_clockwise()

def move_down():
    global board
    rotate_board_clockwise()
    move_left()
    rotate_board_clockwise()
    rotate_board_clockwise()
    rotate_board_clockwise()

# Main game loop
add_new_tile()
add_new_tile()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move_left()
            elif event.key == pygame.K_RIGHT:
                move_right()
            elif event.key == pygame.K_UP:
                move_up()
            elif event.key == pygame.K_DOWN:
                move_down()

    draw_board()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()