import pygame
import pickle
import os
from objects.track import Track
from objects.car import Car
from objects.brain import Brain

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
track = Track("assets/tracks/track_0.json", WINDOW_WIDTH, WINDOW_HEIGHT)

# Load the trained brain
try:
    with open("model.pkl", "rb") as f:
        brain = pickle.load(f)
except FileNotFoundError:
    print("Error: model.pkl not found. Please train the model first.")
    exit(1)

# Create a single car with the trained brain
track.randomize_start_pos()
x, y = track.pixel_to_world(track.start_pos[1], track.start_pos[0])
car = Car(x, y, track, color=(0, 0, 255))  # Blue color for the car
car.brain = brain

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
        steering = brain.think(ray_distances)
        car.control(steering, 0.35)
        car.update()
    else:
        # Reset car at a new random position when it dies
        angle, start_pos = track.randomize_start_pos()
        x, y = track.pixel_to_world(start_pos[1], start_pos[0])
        car.angle = angle
        car.x = x
        car.y = y
        car.is_alive = True
        car.distance_traveled = 0
        car.frames_alive = 0
        car.laps = 0
        car._half_laps = 0
        car._last_col = None

    # Draw everything
    track.draw(screen)
    car.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Clean up
pygame.quit()
