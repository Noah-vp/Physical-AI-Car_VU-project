import pygame
from objects.track import Track
from objects.population import Population # Import Population class
import os
import random
# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Train Simulator")
frame_rate = 60

# Create track object
clock = pygame.time.Clock()
# loop through all track files in the assets/tracks folder
track_list = []
for file in os.listdir("assets/tracks"):
    track_file_path = os.path.join(os.path.dirname(__file__), "assets", "tracks", file)
    # if "org" in file:
    track = Track(track_file_path, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    track_list.append(track)

population = Population(size=50, track=track_list[0])
population.track_list = track_list

# Game state
running = True
font = pygame.font.Font(None, 36)

def handle_events():
    global running
    global frame_rate
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_DOWN:
                if frame_rate > 10:
                    frame_rate -= 10
            elif event.key == pygame.K_UP:
                if frame_rate < 500:
                    frame_rate += 10
            elif event.key == pygame.K_r:
                for car in population.cars:
                    car["car"].is_alive = False
            elif event.key == pygame.K_s:
                population.save_model()


def draw():
    # Clear screen
    screen.fill(population.track.BACKGROUND_COLOR) # Use background color from track
    
    # Draw track
    if population.track.layout is not None:
        population.track.draw(screen)
    
    # Draw debug information
    debug_info = [
        "ESC - Quit",
        "R - Reset Population",
        "Vertical Arrows - Change Frame Rate",
        "S - Save model",
        f"Current test position: {population.current_test_position} / {population.test_positions}",
        f"Frame Rate: {frame_rate}",
        f"Generation: {population.generation}",
        f"Cars alive: {sum(car['car'].is_alive for car in population.cars)} / {population.size}"
    ]

    for i, text in enumerate(debug_info):
        text_surface = font.render(text, True, (200, 200, 200))
        screen.blit(text_surface, (10, 10 + i * 30))
    
    # Draw population
    population.draw_population(screen)
    
    # Update display
    pygame.display.flip()

def update():
    population.update_population()

# Main game loop
while running:
    handle_events()
    draw()
    update()
    clock.tick(frame_rate)

pygame.quit()

