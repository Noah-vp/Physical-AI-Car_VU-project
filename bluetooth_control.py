import pygame
import pickle
import os
import serial
import time
from objects.track import Track
from objects.car import Car
from objects.brain import Brain

# Initialize Pygame for visualization
pygame.init()
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Physical Car Control")
clock = pygame.time.Clock()

# Load the trained brain
try:
    with open("models/model_last.pkl", "rb") as f:
        brain = pickle.load(f)
except FileNotFoundError:
    print("Error: model_last.pkl not found. Please train the model first.")
    exit(1)

# Initialize Bluetooth connection
try:
    # Adjust the port name based on your system
    bluetooth = serial.Serial('COM7', 9600, timeout=1)  # Windows
    time.sleep(2)  # Wait for connection to establish
    print("Bluetooth connection established")
    command = "S,0"
    bluetooth.write(command.encode())
except Exception as e:
    print(f"Error connecting to Bluetooth: {e}")
    exit(1)

# Create a virtual car for visualization
track = Track("assets/tracks/track_org.json", WINDOW_WIDTH, WINDOW_HEIGHT)
car = Car(0, 0, track, color=(0, 0, 255))
car.brain = brain

# Main control loop
running = True
while running:
    # Handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    try:
        # Read sensor data from Bluetooth
        if bluetooth.in_waiting > 0:
            data = bluetooth.readline().decode('utf-8').strip()
            if data:
                # split the data into a list and remove empty strings without converting to float
                data = [x for x in data.split(',') if x]
                if len(data) == 3:
                    # data[2] = 50
                    #convert to float
                    ray_distances = [float(x) for x in data]
                    
                    # Use brain to determine steering
                    steering = brain.think(ray_distances)
                    
                    # Send control command to car
                    if steering >= 0.2:
                        command = "L,0"
                    elif steering <= -0.2:
                        command = "R,0"
                    else:
                        command = "f,0"
                    print(f"ray_distances: {ray_distances}, steering: {steering}, sending command: {command}")
                    bluetooth.write(command.encode())
                    
                    # Draw visualization
                    screen.fill((150, 150, 150))
                    pygame.display.flip()
                    command = "S,0"
                    bluetooth.write(command.encode())
                    print(f"sending command: {command}")

                
    except Exception as e:
        print(f"Error in control loop: {e}")
        time.sleep(0.1)  # Wait a bit before retrying

    clock.tick(60)

# Clean up
bluetooth.close()
pygame.quit() 