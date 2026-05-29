import random
import tkinter as tk
from tkinter import font as tkfont

SIZE = 4
TILE_SIZE = 100
TILE_MARGIN = 10
WIDTH = SIZE * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN
HEIGHT = WIDTH
ANIMATION_STEPS = 8
ANIMATION_DELAY_MS = 2


def color_to_hex(red, green, blue):
    return f"#{red:02x}{green:02x}{blue:02x}"

BACKGROUND_COLOR = color_to_hex(187, 173, 160)
EMPTY_TILE_COLOR = color_to_hex(205, 193, 180)
TILE_COLORS = {
    2: color_to_hex(238, 228, 218),
    4: color_to_hex(237, 224, 200),
    8: color_to_hex(242, 177, 121),
    16: color_to_hex(245, 149, 99),
    32: color_to_hex(246, 124, 95),
    64: color_to_hex(246, 94, 59),
    128: color_to_hex(237, 207, 114),
    256: color_to_hex(237, 204, 97),
    512: color_to_hex(237, 200, 80),
    1024: color_to_hex(237, 197, 63),
    2048: color_to_hex(237, 194, 46),
}
DARK_FONT_COLOR = color_to_hex(119, 110, 101)
LIGHT_FONT_COLOR = color_to_hex(249, 246, 242)
OVERLAY_COLOR = color_to_hex(238, 228, 218)
OVERLAY_PANEL_COLOR = color_to_hex(250, 248, 239)
BUTTON_COLOR = color_to_hex(143, 122, 102)
BUTTON_TEXT_COLOR = color_to_hex(249, 246, 242)
PREFERRED_TILE_FONT_FAMILIES = (
    "Clear Sans",
    "Arial",
    "Helvetica",
)
TILE_FONT_SIZES = {
    1: -46,
    2: -46,
    3: -38,
    4: -30,
    5: -24,
}


class Game2048App:
    def __init__(self):
        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.is_animating = False
        self.animation_progress = 0.0
        self.animation_tiles = []
        self.pending_board = None
        self.pending_score_gain = 0
        self.animation_after_id = None
        self.game_over = False
        self.restart_button_bounds = None

        self.root = tk.Tk()
        self.root.title("2048")
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND_COLOR)

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH,
            height=HEIGHT,
            bg=BACKGROUND_COLOR,
            bd=0,
            highlightthickness=0,
            relief="flat",
        )
        self.canvas.pack()
        self.canvas.focus_set()
        self.canvas.bind("<Button-1>", self.handle_canvas_click)
        self.canvas.bind("<Motion>", self.handle_canvas_motion)

        available_families = set(tkfont.families(self.root))
        tile_font_family = self.get_preferred_font_family(available_families)

        self.tile_fonts = {
            digits: tkfont.Font(family=tile_font_family, size=size, weight="bold")
            for digits, size in TILE_FONT_SIZES.items()
        }
        self.overlay_title_font = tkfont.Font(family=tile_font_family, size=-34, weight="bold")
        self.overlay_text_font = tkfont.Font(family=tile_font_family, size=-18, weight="bold")
        self.button_font = tkfont.Font(family=tile_font_family, size=-20, weight="bold")

        bindings = {
            "<Left>": self.move_left,
            "<Right>": self.move_right,
            "<Up>": self.move_up,
            "<Down>": self.move_down,
        }
        for key, handler in bindings.items():
            self.root.bind(key, lambda event, handler=handler: self.handle_move(handler))

        self.start_new_game()

    def start_new_game(self, event=None):
        if self.animation_after_id is not None:
            self.root.after_cancel(self.animation_after_id)
            self.animation_after_id = None

        self.board = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.is_animating = False
        self.animation_progress = 0.0
        self.animation_tiles = []
        self.pending_board = None
        self.pending_score_gain = 0
        self.game_over = False
        self.restart_button_bounds = None

        self.add_new_tile()
        self.add_new_tile()
        self.draw_board()

    def get_tile_font(self, value):
        digits = min(len(str(value)), max(self.tile_fonts))
        return self.tile_fonts[digits]

    def get_preferred_font_family(self, available_families):
        for family in PREFERRED_TILE_FONT_FAMILIES:
            if family in available_families:
                return family
        return "TkDefaultFont"

    def get_tile_fill_color(self, value):
        if value >= 2048:
            return TILE_COLORS[2048]
        return TILE_COLORS.get(value, EMPTY_TILE_COLOR)

    def get_tile_text_color(self, value):
        if value >= 8:
            return LIGHT_FONT_COLOR
        return DARK_FONT_COLOR

    def get_tile_bounds(self, row, col):
        x0 = col * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN
        y0 = row * (TILE_SIZE + TILE_MARGIN) + TILE_MARGIN
        x1 = x0 + TILE_SIZE
        y1 = y0 + TILE_SIZE
        return x0, y0, x1, y1

    def get_tile_center(self, row, col):
        x0, y0, x1, y1 = self.get_tile_bounds(row, col)
        return (x0 + x1) / 2, (y0 + y1) / 2

    def draw_background(self):
        self.canvas.delete("all")

        for row in range(SIZE):
            for col in range(SIZE):
                x0, y0, x1, y1 = self.get_tile_bounds(row, col)
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=EMPTY_TILE_COLOR,
                    outline=EMPTY_TILE_COLOR,
                )

    def draw_tile(self, value, center_x, center_y):
        x0 = center_x - TILE_SIZE / 2
        y0 = center_y - TILE_SIZE / 2
        x1 = x0 + TILE_SIZE
        y1 = y0 + TILE_SIZE
        fill_color = self.get_tile_fill_color(value)

        self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill_color, outline=fill_color)
        self.canvas.create_text(
            center_x,
            center_y,
            text=str(value),
            fill=self.get_tile_text_color(value),
            font=self.get_tile_font(value),
        )

    def draw_board(self):
        self.draw_background()

        if self.is_animating:
            for movement in self.animation_tiles:
                start_x, start_y = self.get_tile_center(*movement["from"])
                end_x, end_y = self.get_tile_center(*movement["to"])
                current_x = start_x + (end_x - start_x) * self.animation_progress
                current_y = start_y + (end_y - start_y) * self.animation_progress
                self.draw_tile(movement["value"], current_x, current_y)
        else:
            for row in range(SIZE):
                for col in range(SIZE):
                    value = self.board[row][col]
                    if value != 0:
                        center_x, center_y = self.get_tile_center(row, col)
                        self.draw_tile(value, center_x, center_y)

        if self.game_over:
            self.draw_game_over_overlay()

    def draw_game_over_overlay(self):
        panel_width = WIDTH - 80
        panel_height = 170
        panel_x0 = (WIDTH - panel_width) / 2
        panel_y0 = (HEIGHT - panel_height) / 2
        panel_x1 = panel_x0 + panel_width
        panel_y1 = panel_y0 + panel_height

        self.canvas.create_rectangle(
            0,
            0,
            WIDTH,
            HEIGHT,
            fill=OVERLAY_COLOR,
            outline="",
            stipple="gray50",
        )
        self.canvas.create_rectangle(
            panel_x0,
            panel_y0,
            panel_x1,
            panel_y1,
            fill=OVERLAY_PANEL_COLOR,
            outline=BACKGROUND_COLOR,
            width=2,
        )
        self.canvas.create_text(
            WIDTH / 2,
            panel_y0 + 42,
            text="Game Over",
            fill=DARK_FONT_COLOR,
            font=self.overlay_title_font,
        )
        self.canvas.create_text(
            WIDTH / 2,
            panel_y0 + 78,
            text="No more moves left.",
            fill=DARK_FONT_COLOR,
            font=self.overlay_text_font,
        )

        button_width = 170
        button_height = 46
        button_x0 = (WIDTH - button_width) / 2
        button_y0 = panel_y1 - 62
        button_x1 = button_x0 + button_width
        button_y1 = button_y0 + button_height
        self.restart_button_bounds = (button_x0, button_y0, button_x1, button_y1)

        self.canvas.create_rectangle(
            button_x0,
            button_y0,
            button_x1,
            button_y1,
            fill=BUTTON_COLOR,
            outline=BUTTON_COLOR,
        )
        self.canvas.create_text(
            WIDTH / 2,
            button_y0 + (button_height / 2),
            text="New Game",
            fill=BUTTON_TEXT_COLOR,
            font=self.button_font,
        )

    def handle_canvas_motion(self, event):
        if self.game_over and self.is_within_restart_button(event.x, event.y):
            self.canvas.config(cursor="hand2")
            return
        self.canvas.config(cursor="")

    def handle_canvas_click(self, event):
        self.canvas.focus_set()
        if self.game_over and self.is_within_restart_button(event.x, event.y):
            self.start_new_game()

    def is_within_restart_button(self, x_pos, y_pos):
        if self.restart_button_bounds is None:
            return False
        x0, y0, x1, y1 = self.restart_button_bounds
        return x0 <= x_pos <= x1 and y0 <= y_pos <= y1

    def add_new_tile(self, target_board=None):
        board = self.board if target_board is None else target_board
        empty_tiles = [
            (row_index, col_index)
            for row_index in range(SIZE)
            for col_index in range(SIZE)
            if board[row_index][col_index] == 0
        ]
        if empty_tiles:
            row_index, col_index = random.choice(empty_tiles)
            board[row_index][col_index] = 2 if random.random() < 0.9 else 4

    def slide_row_left(self, row_index, row):
        non_zero_tiles = [
            {"source_col": col_index, "value": value}
            for col_index, value in enumerate(row)
            if value != 0
        ]
        new_row = [0] * SIZE
        movements = []
        score_gain = 0
        target_col = 0
        tile_index = 0

        while tile_index < len(non_zero_tiles):
            current_tile = non_zero_tiles[tile_index]
            next_index = tile_index + 1

            if next_index < len(non_zero_tiles) and non_zero_tiles[next_index]["value"] == current_tile["value"]:
                next_tile = non_zero_tiles[next_index]
                merged_value = current_tile["value"] * 2
                new_row[target_col] = merged_value
                score_gain += merged_value
                movements.append(
                    {
                        "value": current_tile["value"],
                        "from": (row_index, current_tile["source_col"]),
                        "to": (row_index, target_col),
                    }
                )
                movements.append(
                    {
                        "value": next_tile["value"],
                        "from": (row_index, next_tile["source_col"]),
                        "to": (row_index, target_col),
                    }
                )
                tile_index += 2
            else:
                new_row[target_col] = current_tile["value"]
                movements.append(
                    {
                        "value": current_tile["value"],
                        "from": (row_index, current_tile["source_col"]),
                        "to": (row_index, target_col),
                    }
                )
                tile_index += 1

            target_col += 1

        return new_row, score_gain, movements

    def to_left_space(self, row, col, direction):
        if direction == "left":
            return row, col
        if direction == "right":
            return row, SIZE - 1 - col
        if direction == "up":
            return col, row
        return col, SIZE - 1 - row

    def from_left_space(self, row, col, direction):
        if direction == "left":
            return row, col
        if direction == "right":
            return row, SIZE - 1 - col
        if direction == "up":
            return col, row
        return SIZE - 1 - col, row

    def get_transformed_board(self, direction):
        transformed_board = [[0] * SIZE for _ in range(SIZE)]
        for row in range(SIZE):
            for col in range(SIZE):
                transformed_row, transformed_col = self.to_left_space(row, col, direction)
                transformed_board[transformed_row][transformed_col] = self.board[row][col]
        return transformed_board

    def restore_transformed_board(self, transformed_board, direction):
        restored_board = [[0] * SIZE for _ in range(SIZE)]
        for row in range(SIZE):
            for col in range(SIZE):
                original_row, original_col = self.from_left_space(row, col, direction)
                restored_board[original_row][original_col] = transformed_board[row][col]
        return restored_board

    def build_move(self, direction):
        transformed_board = self.get_transformed_board(direction)
        next_transformed_board = []
        transformed_movements = []
        score_gain = 0

        for row_index, row in enumerate(transformed_board):
            new_row, row_score_gain, row_movements = self.slide_row_left(row_index, row)
            next_transformed_board.append(new_row)
            transformed_movements.extend(row_movements)
            score_gain += row_score_gain

        next_board = self.restore_transformed_board(next_transformed_board, direction)
        if next_board == self.board:
            return None

        movements = []
        for movement in transformed_movements:
            from_position = movement["from"]
            to_position = movement["to"]
            from_row, from_col = self.from_left_space(from_position[0], from_position[1], direction)
            to_row, to_col = self.from_left_space(to_position[0], to_position[1], direction)
            movements.append(
                {
                    "value": movement["value"],
                    "from": (from_row, from_col),
                    "to": (to_row, to_col),
                }
            )

        return {
            "board": next_board,
            "movements": movements,
            "score_gain": score_gain,
        }

    def has_available_moves(self):
        for row in range(SIZE):
            for col in range(SIZE):
                value = self.board[row][col]
                if value == 0:
                    return True
                if row + 1 < SIZE and self.board[row + 1][col] == value:
                    return True
                if col + 1 < SIZE and self.board[row][col + 1] == value:
                    return True
        return False

    def move_left(self):
        return self.build_move("left")

    def move_right(self):
        return self.build_move("right")

    def move_up(self):
        return self.build_move("up")

    def move_down(self):
        return self.build_move("down")

    def start_animation(self, move_result):
        self.is_animating = True
        self.animation_progress = 0.0
        self.animation_tiles = move_result["movements"]
        self.pending_board = move_result["board"]
        self.pending_score_gain = move_result["score_gain"]
        self.animate_step(0)

    def animate_step(self, step_index):
        self.animation_progress = step_index / ANIMATION_STEPS
        self.draw_board()

        if step_index < ANIMATION_STEPS:
            self.animation_after_id = self.root.after(
                ANIMATION_DELAY_MS,
                lambda: self.animate_step(step_index + 1),
            )
            return

        self.finish_animation()

    def finish_animation(self):
        self.animation_after_id = None
        self.is_animating = False
        if self.pending_board is None:
            self.animation_tiles = []
            self.pending_score_gain = 0
            self.draw_board()
            return

        self.board = [row[:] for row in self.pending_board]
        self.score += self.pending_score_gain
        self.add_new_tile()
        self.animation_tiles = []
        self.pending_board = None
        self.pending_score_gain = 0
        self.game_over = not self.has_available_moves()
        self.draw_board()

    def handle_move(self, move_handler):
        if self.is_animating or self.game_over:
            return

        move_result = move_handler()
        if move_result is not None:
            self.start_animation(move_result)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Game2048App().run()