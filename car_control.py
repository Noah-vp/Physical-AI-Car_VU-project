import pygame
import serial
import sys
import numpy as np
import time
from objects.democar import Democar

# Initialize Pygame
pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Car Visualization")

# Set up the clock for controlling frame rate
clock = pygame.time.Clock()

running = True
ser = None
current_command = None
model_output = 0
stop = False

def read_raycast():
    if ser and ser.is_open:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:  # Only process non-empty lines
                try:
                    # split the data into a list and remove empty strings
                    data = [float(x) for x in data.split(',') if x]
                    if len(data) == 3:  # Ensure we have exactly 3 values
                        return data
                except ValueError:
                    print(f"Invalid data received: {data}")
        except serial.SerialException:
            print("Error reading from serial port")
    return None

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

try:
    # Add a small delay before connecting to allow the port to reset
    time.sleep(1)
    ser = serial.Serial('COM7', 9600, timeout=0.1)  # Reduced timeout
    print("Connected to COM7")

    # Initialize the car
    car = Democar(x=WINDOW_WIDTH/2, y=WINDOW_HEIGHT/2)

    while running:
        # Handle events
        command = ""
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
            car.speed = 1
            new_command = f"L,{0}"
        elif keys[pygame.K_RIGHT]:
            steering = -1
            car.speed = 1
            new_command = f"R,{0}"
        elif keys[pygame.K_UP]:
            new_command = "F,0"
        else:
            car.speed = 0
            new_command = "STOP"

        # Clear the screen
        screen.fill((255, 255, 255))

        # Read raycast data
        raycast = read_raycast()
        if raycast:
            car.ray_lengths = raycast
        
        # Update car control
        send_command(command)
        current_command = command
        # Draw the car
        car.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(60)

except serial.SerialException as e:
    print(f"Error while connecting to COM7: {str(e)}")
    sys.exit(1)

finally:
    # Ensure the serial port is properly closed
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed")