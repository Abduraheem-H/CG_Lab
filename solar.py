import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import time

GRID_WIDTH = 30
GRID_HEIGHT = 20
TILE_SIZE = 20

WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

SNAKE_INITIAL_LENGTH = 3
DIFFICULTY_LEVELS = {"1": ("EASY", 0.20), "2": ("MEDIUM", 0.15), "3": ("HARD", 0.10)}
# Default to Medium if selection fails
current_difficulty_name = "MEDIUM"
SNAKE_UPDATE_INTERVAL = DIFFICULTY_LEVELS["2"][1]  # Default to medium interval

snake = []
food_pos = None
current_direction = "RIGHT"
score = 0
game_over = False
game_over_printed = False
last_update_time = 0.0

COLOR_SNAKE_HEAD = (0.0, 0.8, 0.0)
COLOR_SNAKE_BODY = (0.0, 0.6, 0.0)
COLOR_FOOD = (1.0, 0.0, 0.0)
COLOR_BACKGROUND = (0.0, 0.0, 0.1)
COLOR_GRID_LINES = (0.1, 0.1, 0.2)


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def key_callback(window, key, scancode, action, mods):
    global current_direction, game_over

    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif game_over:
            if key == glfw.KEY_R:
                reset_game()
        else:
            if key == glfw.KEY_UP and current_direction != "DOWN":
                current_direction = "UP"
            elif key == glfw.KEY_DOWN and current_direction != "UP":
                current_direction = "DOWN"
            elif key == glfw.KEY_LEFT and current_direction != "RIGHT":
                current_direction = "LEFT"
            elif key == glfw.KEY_RIGHT and current_direction != "LEFT":
                current_direction = "RIGHT"


def reset_game():
    global snake, food_pos, current_direction, score, game_over, last_update_time, game_over_printed
    snake = []
    head_x = GRID_WIDTH // 2
    head_y = GRID_HEIGHT // 2
    for i in range(SNAKE_INITIAL_LENGTH):
        snake.append((head_x - i, head_y))
    current_direction = "RIGHT"
    score = 0
    game_over = False
    game_over_printed = False
    last_update_time = glfw.get_time()
    generate_food()
    print("Game Reset! Score: 0")


def generate_food():
    global food_pos
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in snake:
            food_pos = (x, y)
            break


def update_game():
    global snake, food_pos, score, game_over, last_update_time, game_over_printed

    if game_over:
        if not game_over_printed:
            print("\n--- GAME OVER ---")
            print(f"Final Score: {score}")
            print("Press 'R' to Restart or 'ESC' to Quit")
            game_over_printed = True
        return

    current_time = glfw.get_time()
    if current_time - last_update_time < SNAKE_UPDATE_INTERVAL:
        return

    last_update_time = current_time

    head_x, head_y = snake[0]
    if current_direction == "UP":
        new_head = (head_x, head_y + 1)
    elif current_direction == "DOWN":
        new_head = (head_x, head_y - 1)
    elif current_direction == "LEFT":
        new_head = (head_x - 1, head_y)
    elif current_direction == "RIGHT":
        new_head = (head_x + 1, head_y)
    else:
        return

    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
        game_over = True
        return

    if new_head in snake[1:]:
        game_over = True
        return

    snake.insert(0, new_head)

    if new_head == food_pos:
        score += 1
        generate_food()
        print(f"Score: {score}")
    else:
        snake.pop()


def draw_rectangle(grid_x, grid_y, color):
    x = grid_x * TILE_SIZE
    y = grid_y * TILE_SIZE

    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + TILE_SIZE, y)
    glVertex2f(x + TILE_SIZE, y + TILE_SIZE)
    glVertex2f(x, y + TILE_SIZE)
    glEnd()


def draw_grid_lines():
    glColor3f(*COLOR_GRID_LINES)
    glBegin(GL_LINES)
    for x in range(GRID_WIDTH + 1):
        glVertex2f(x * TILE_SIZE, 0)
        glVertex2f(x * TILE_SIZE, WINDOW_HEIGHT)
    for y in range(GRID_HEIGHT + 1):
        glVertex2f(0, y * TILE_SIZE)
        glVertex2f(WINDOW_WIDTH, y * TILE_SIZE)
    glEnd()


def render(window):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    glColor3f(*COLOR_BACKGROUND)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()

    draw_grid_lines()

    if snake:
        draw_rectangle(snake[0][0], snake[0][1], COLOR_SNAKE_HEAD)
        for segment in snake[1:]:
            draw_rectangle(segment[0], segment[1], COLOR_SNAKE_BODY)

    if food_pos:
        draw_rectangle(food_pos[0], food_pos[1], COLOR_FOOD)

    glfw.swap_buffers(window)


def main():
    global SNAKE_UPDATE_INTERVAL, current_difficulty_name

    # --- Difficulty Selection Menu ---
    print("Welcome to the Snake Game!")
    print("Please choose your difficulty:")
    for key, (name, interval) in DIFFICULTY_LEVELS.items():
        print(f"  {key}: {name} (Speed: {1/interval:.1f} squares/sec)")

    selected_option = ""
    while selected_option not in DIFFICULTY_LEVELS:
        selected_option = input("Enter your choice (1, 2, or 3): ").strip()
        if selected_option not in DIFFICULTY_LEVELS:
            print("Invalid choice. Please enter 1, 2, or 3.")

    current_difficulty_name, SNAKE_UPDATE_INTERVAL = DIFFICULTY_LEVELS[selected_option]
    print(f"Starting game on {current_difficulty_name} difficulty...")
    time.sleep(1)  # Give a moment to read the message

    # --- OpenGL and Game Initialization ---
    if not glfw.init():
        return

    window = glfw.create_window(
        WINDOW_WIDTH, WINDOW_HEIGHT, "OpenGL Snake Game", None, None
    )
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)

    glClearColor(0.0, 0.0, 0.0, 1.0)

    framebuffer_size_callback(window, WINDOW_WIDTH, WINDOW_HEIGHT)

    reset_game()  # This will use the selected SNAKE_UPDATE_INTERVAL

    while not glfw.window_should_close(window):
        update_game()
        render(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
