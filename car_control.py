import pygame
import serial
import sys
import os
from objects.car import Car
from objects.track import Track

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Car Control")

# Initialize serial communication
try:
    ser = serial.Serial('COM8', 9600, timeout=1)
    print("Connected to COM8")
except serial.SerialException:
    print("Failed to connect to COM8")
    sys.exit(1)

# Create a simple track
# First, create a track file if it doesn't exist
track_file = "simple_track.json"
if not os.path.exists(track_file):
    track_data = {
        "layout": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ],
        "start_pos": [1, 1]
    }
    with open(track_file, 'w') as f:
        import json
        json.dump(track_data, f)

# Initialize track and car
track = Track(track_file, WINDOW_WIDTH, WINDOW_HEIGHT)
start_x, start_y = track.pixel_to_world(track.start_pos[0], track.start_pos[1])
car = Car(start_x, start_y, track, start_angle=0, color=(255, 0, 0))

# Command state
current_command = None
steering_angle = 180

def send_command(command):
    """Send command to the car via serial"""
    global current_command
    if command != current_command:  # Only send if command has changed
        try:
            ser.write(f"{command}\n".encode())
            print(f"Sent command: {command}")
            current_command = command
        except serial.SerialException:
            print("Error sending command")

def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Handle movement
        steering = 0
        new_command = None

        if keys[pygame.K_LEFT]:
            steering = 1
            car.speed = Car.SPEED
            new_command = f"L,{steering_angle}"
        elif keys[pygame.K_RIGHT]:
            steering = -1
            car.speed = Car.SPEED
            new_command = f"R,{steering_angle}"
        elif keys[pygame.K_UP]:
            car.speed = Car.SPEED
            new_command = "F,0"
        else:
            car.speed = 0
            new_command = "STOP"

        # Send command if it has changed
        if new_command is not None:
            send_command(new_command)

        # Update car
        car.control(steering, 0.1)  # 0.1 is the sensitivity
        car.update()
        
        # Draw everything
        track.draw(screen)
        car.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
    
    # Clean up
    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main() 