from utils.support_functions import *
import pygame
import numpy as np
import sys
import json # Added json import
import os # Added os import

rows, columns = 27, 19
TSP = TSPDecoder(rows=rows, columns=columns)

# Define constants
PIXEL_WIDTH = 20
PIXEL_HEIGHT = 20 # Make pixels square for simpler wall drawing
PIXEL_MARGIN = 2
WALL_COLOR = (255, 255, 255) # Define wall color
BACKGROUND_COLOR = (0, 0, 0)
START_COLOR = (0, 255, 0) # Define start position color
TRACK_DIR = "../assets/tracks" # Directory to save tracks

# Initialise the PyGame screen according to resolution
pygame.init()
WINDOW_SIZE = [
    columns * PIXEL_WIDTH + columns * PIXEL_MARGIN + 2 * PIXEL_MARGIN,
    rows * PIXEL_HEIGHT + rows * PIXEL_MARGIN + 2 * PIXEL_MARGIN
]

def draw_track_walls(screen, grid):
    screen.fill(BACKGROUND_COLOR) # Clear screen first
    rows, cols = grid.shape
    wall_width = 1 # Thickness of the wall lines

    for r in range(rows):
        for c in range(cols):
            # Calculate screen coordinates for the corners of the current cell
            x = c * (PIXEL_WIDTH + PIXEL_MARGIN) + PIXEL_MARGIN
            y = r * (PIXEL_HEIGHT + PIXEL_MARGIN) + PIXEL_MARGIN
            cell_rect = pygame.Rect(x, y, PIXEL_WIDTH, PIXEL_HEIGHT)

            if grid[r, c] > 0: # This is a track cell
                # Check neighbor above
                if r == 0 or grid[r - 1, c] == 0:
                    pygame.draw.line(screen, WALL_COLOR, cell_rect.topleft, cell_rect.topright, wall_width)
                # Check neighbor below
                if r == rows - 1 or grid[r + 1, c] == 0:
                     pygame.draw.line(screen, WALL_COLOR, cell_rect.bottomleft, cell_rect.bottomright, wall_width)
                # Check neighbor left
                if c == 0 or grid[r, c - 1] == 0:
                    pygame.draw.line(screen, WALL_COLOR, cell_rect.topleft, cell_rect.bottomleft, wall_width)
                # Check neighbor right
                if c == cols - 1 or grid[r, c + 1] == 0:
                    pygame.draw.line(screen, WALL_COLOR, cell_rect.topright, cell_rect.bottomright, wall_width)

    # Draw start position if it exists
    if start_pos:
        r, c = start_pos
        x = c * (PIXEL_WIDTH + PIXEL_MARGIN) + PIXEL_MARGIN + PIXEL_WIDTH // 2
        y = r * (PIXEL_HEIGHT + PIXEL_MARGIN) + PIXEL_MARGIN + PIXEL_HEIGHT // 2
        pygame.draw.circle(screen, START_COLOR, (x, y), min(PIXEL_WIDTH, PIXEL_HEIGHT) // 3)

def has_neighbor(grid, r, c):
    rows, cols = grid.shape
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            # Skip the center cell itself
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            # Check boundaries
            if 0 <= nr < rows and 0 <= nc < cols:
                # Check if neighbor has been drawn (is non-zero)
                if grid[nr, nc] > 0:
                    return True
    return False

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Haptic Skin visualiser")

# Initialise the PyGame Clock for timing
clock = pygame.time.Clock()
grid = np.zeros((TSP.rows, TSP.columns))
new_grid = np.zeros((TSP.rows, TSP.columns))
start_pos = None # Initialize start position

# Ensure track directory exists
os.makedirs(TRACK_DIR, exist_ok=True)

def save_track(grid_data, start_position):
    # Find the next available track number
    track_num = 0
    while os.path.exists(os.path.join(TRACK_DIR, f"track_{track_num}.json")):
        track_num += 1
    filepath = os.path.join(TRACK_DIR, f"track_{track_num}.json")

    # Prepare data for JSON
    track_layout = grid_data.astype(int).tolist() # Convert numpy array to list
    data_to_save = {
        "layout": track_layout,
        "start_pos": start_position
    }

    # Save to JSON
    try:
        with open(filepath, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Track saved successfully to {filepath}")
        return True
    except Exception as e:
        print(f"Error saving track: {e}")
        return False

def reset_state():
    global grid, start_pos
    grid = np.zeros((TSP.rows, TSP.columns))
    start_pos = None
    print("Grid reset.")

while True:
    reset_pending = False
    # Check if the screen is closed and quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit() # Added sys.exit() for a clean exit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                if start_pos:
                    if save_track(grid, start_pos):
                        reset_pending = True # Reset after successful save
                else:
                    print("Cannot save empty track or track without start position.")
            elif event.key == pygame.K_r:
                reset_pending = True

    if reset_pending:
        reset_state()

    # Get the frame
    if TSP.frame_available:
        new_grid = TSP.readFrame()

    for row in range(rows):
        for column in range(columns):
            prev_pixel = grid[row][column]
            new_pixel = new_grid[row][column]

            if new_pixel > prev_pixel and new_pixel > 127:
                # Only update if the pixel has a neighbor or if the grid is empty
                can_draw = False
                if np.any(grid) and has_neighbor(grid, row, column):
                    can_draw = True
                elif not np.any(grid): # Allow the first pixel to be drawn anywhere
                    can_draw = True

                if can_draw:
                    grid[row][column] = new_pixel
                    # Set start position if it's the first pixel being drawn
                    if start_pos is None:
                        start_pos = (row, column)
                        print(f"Start position set to: {start_pos}")

    draw_track_walls(screen, grid)

    # Limit the framerate to 60FPS
    clock.tick(60)

    # Draw to the display
    pygame.display.flip()

