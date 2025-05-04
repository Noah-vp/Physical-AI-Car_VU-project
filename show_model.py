import pygame
import pickle
import os
from objects.track import Track
from objects.car import Car
from objects.brain import Brain
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Create the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("AI Car Demo")
clock = pygame.time.Clock()

# Load the track
track_file_path = os.path.join(os.path.dirname(__file__), "assets", "tracks", "track_4.json")
track = Track(track_file_path, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

# Load the trained brain
try:
    with open("models/model_last.pkl", "rb") as f:
        brain = pickle.load(f)
except FileNotFoundError:
    print("Error: model_last.pkl not found. Please train the model first.")
    exit(1)

# Create a single car with the trained brain
start_angle, start_pos = track.randomize_start_pos()
x, y = track.pixel_to_world(start_pos[1], start_pos[0])
car = Car(x, y, track, color=(0, 0, 255))  # Blue color for the car
car.angle = start_angle
car.ROTATION_SPEED = 1
car.brain = brain  # Properly assign the loaded brain to the car

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Update car
    if car.is_alive:
        ray_distances = car.ray_cast()
        steering = car.brain.think(ray_distances)  # Use car's brain instead of global brain
        car.control(steering, 0.2)
        car.update()
        car.distance_traveled = 0
    else:
        # Reset car at a new random position when it dies
        start_angle, start_pos = track.randomize_start_pos()
        x, y = track.pixel_to_world(start_pos[1], start_pos[0])
        car.angle = start_angle
        car.x = x
        car.y = y
        car.is_alive = True
        car.distance_traveled = 0
        car.stuck_frames = 0  # Reset stuck frames instead of frames_alive

    # Draw everything
    track.draw(screen)
    car.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
