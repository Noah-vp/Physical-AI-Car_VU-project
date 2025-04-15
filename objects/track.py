import pygame
import json
import numpy as np
import os
import random

class Track:
    # Define constants for drawing
    PIXEL_WIDTH = 20
    PIXEL_HEIGHT = 20
    PIXEL_MARGIN = 2
    WALL_COLOR = (0,0,0) # Black walls
    START_COLOR = (0, 255, 0) # Green start
    BACKGROUND_COLOR = (150, 150, 150) # Light gray background
    WALL_WIDTH = 1 # Thickness of the wall lines

    def __init__(self, filepath, width, height):
        """Initializes the Track object by loading layout from a JSON file."""
        self.filepath = filepath
        self.layout = None
        self.start_pos = None
        self.rows = 0
        self.cols = 0
        self.load_track()
        self.scale_track(width, height)

    def scale_track(self, width, height):
        """Scales the track to the provided width and height."""
        self.PIXEL_WIDTH = width // self.cols
        self.PIXEL_HEIGHT = height // self.rows

    def load_track(self):
        """Loads the track layout and start position from the JSON file."""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            self.layout = np.array(data['layout']) # Convert layout to NumPy array
            self.start_pos = tuple(data['start_pos']) # Ensure start_pos is a tuple
            self.rows, self.cols = self.layout.shape
            print(f"Track loaded successfully from {self.filepath}")
            print(f"Layout dimensions: {self.rows}x{self.cols}, Start position: {self.start_pos}")
        except FileNotFoundError:
            print(f"Error: Track file not found at {self.filepath}")
            self.layout = None
            self.start_pos = None
        except Exception as e:
            print(f"Error loading track from {self.filepath}: {e}")
            self.layout = None
            self.start_pos = None

    def randomize_start_pos(self):
        """Randomizes the start position of the track to a random valid position and also returns a start angle"""
        # Keep trying until we find a valid position
        while True:
            valid_positions = np.where(self.layout > 0)
            random_idx = np.random.randint(0, len(valid_positions[0]))
            start_pos = (valid_positions[0][random_idx], valid_positions[1][random_idx])

            # Calculate the angle of the start position by making sure there are two track cells in the direction of the start angle
            r, c = start_pos
            self.start_pos = start_pos
            # Check bounds before accessing cells
            if (c + 2 < self.cols and self.layout[r, c + 1] > 0 and self.layout[r, c + 2] > 0): # Cell to the right is a track cell
                return 0, start_pos    
            elif (c - 2 >= 0 and self.layout[r, c - 1] > 0 and self.layout[r, c - 2] > 0): # Cell to the left is a track cell
                return 180, start_pos
            # If neither direction is valid, continue the loop to try a new random position

    def draw(self, screen):
        """Draws the track walls and start position onto the provided screen surface."""
        if self.layout is None:
            print("Cannot draw track: Layout not loaded.")
            return

        screen.fill(self.BACKGROUND_COLOR) # Clear screen first

        for r in range(self.rows):
            for c in range(self.cols):
                # Calculate screen coordinates for the corners of the current cell
                x = c * (self.PIXEL_WIDTH + self.PIXEL_MARGIN) + self.PIXEL_MARGIN
                y = r * (self.PIXEL_HEIGHT + self.PIXEL_MARGIN) + self.PIXEL_MARGIN
                cell_rect = pygame.Rect(x, y, self.PIXEL_WIDTH, self.PIXEL_HEIGHT)

                if self.layout[r, c] > 0: # This is a track cell
                    # Draw walls based on neighbors
                    # Check neighbor above
                    if r == 0 or self.layout[r - 1, c] == 0:
                        pygame.draw.line(screen, self.WALL_COLOR, cell_rect.topleft, cell_rect.topright, self.WALL_WIDTH)
                    # Check neighbor below
                    if r == self.rows - 1 or self.layout[r + 1, c] == 0:
                         pygame.draw.line(screen, self.WALL_COLOR, cell_rect.bottomleft, cell_rect.bottomright, self.WALL_WIDTH)
                    # Check neighbor left
                    if c == 0 or self.layout[r, c - 1] == 0:
                        pygame.draw.line(screen, self.WALL_COLOR, cell_rect.topleft, cell_rect.bottomleft, self.WALL_WIDTH)
                    # Check neighbor right
                    if c == self.cols - 1 or self.layout[r, c + 1] == 0:
                        pygame.draw.line(screen, self.WALL_COLOR, cell_rect.topright, cell_rect.bottomright, self.WALL_WIDTH)

        # Draw start position if it exists
        if self.start_pos:
            r, c = self.start_pos
            # Ensure start_pos is within bounds
            if 0 <= r < self.rows and 0 <= c < self.cols:
                # Center the circle within the cell
                center_x = c * (self.PIXEL_WIDTH + self.PIXEL_MARGIN) + self.PIXEL_MARGIN + self.PIXEL_WIDTH // 2
                center_y = r * (self.PIXEL_HEIGHT + self.PIXEL_MARGIN) + self.PIXEL_MARGIN + self.PIXEL_HEIGHT // 2
                radius = min(self.PIXEL_WIDTH, self.PIXEL_HEIGHT) // 3
                pygame.draw.circle(screen, self.START_COLOR, (center_x, center_y), radius)
            else:
                print(f"Warning: Start position {self.start_pos} is outside the grid dimensions.")

    def pixel_to_world(self, x, y):
        """Converts pixel coordinates to world coordinates."""
        center_x = x * (self.PIXEL_WIDTH + self.PIXEL_MARGIN) + self.PIXEL_MARGIN + self.PIXEL_WIDTH // 2
        center_y = y * (self.PIXEL_HEIGHT + self.PIXEL_MARGIN) + self.PIXEL_MARGIN + self.PIXEL_HEIGHT // 2
        return center_x, center_y

