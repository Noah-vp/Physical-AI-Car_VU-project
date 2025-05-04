import pygame
import numpy as np
import os

class Democar:
    def __init__(self, x, y, color=(255, 0, 0)):
        # Initialize ray_lengths for this specific car instance
        self.ray_lengths = [0,0,0] # Start with max length (normalized)

        self.is_alive = True
        self.color = color

        self.angle = 0

        self.x = x
        self.y = y

        # Load and prepare image
        self.base_image = None # Original image, correctly oriented and scaled
        self.image = None      # Rotated image for drawing
        self.rect = None       # Rect for positioning the rotated image
        self.load_image()

    def load_image(self):
        """Loads the car image, scales it, and sets the base orientation."""
        # Construct path relative to this file (objects/car.py)
        current_dir = os.path.dirname(__file__)
        image_path = os.path.abspath(os.path.join(current_dir, "..", "assets", "images", "car.png"))
        try:
            loaded_image = pygame.image.load(image_path).convert_alpha()
            # Scale the image to exactly 20x30 pixels
            scaled_image = pygame.transform.scale(loaded_image, (20, 30))
            # Assume the loaded image points UP. Rotate it so that 0 degrees angle points RIGHT.
            self.base_image = pygame.transform.rotate(scaled_image, -90) # Rotate 90 deg clockwise
            # Initialize the image and rect
            self.update_image()
        except pygame.error as e:
            print(f"Error loading car image at {image_path}: {e}")
            # Create a placeholder rectangle if image loading fails
            self.base_image = pygame.Surface((20, 30))
            self.base_image.fill((255, 0, 0))
            self.base_image.set_colorkey((0, 0, 0))
            self.update_image()

    def control(self, steering, sensitivity):
        """Adjusts the car's angle based on left/right input flags (0 or 1)."""
        if steering >= sensitivity:
            self.angle += 2 # Turn left (positive angle change)
            return f"L,0"
        elif steering <= -sensitivity:
            self.angle -= 2 # Turn right (negative angle change)
            return f"R,0"
        else:
            return f"F,0"

    def update_image(self):
        self.angle %= 360 # Keep angle within 0-360 degrees
        """Updates the rotated image and its rect based on current angle."""
        if self.base_image:
            # Rotate the base image by the current angle
            self.image = pygame.transform.rotate(self.base_image, self.angle)
            # Get the rect of the rotated image and center it at the car's position
            self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw_rays(self, screen):
        """Draws the rays onto the screen."""
         # Draw the sensor rays in the same color as the car
        if self.is_alive and self.ray_lengths:
            ray_angles_relative = [-45, 0, 45] # Relative angles in degrees
            ray_color = (0, 255, 0) #self.color # Use the car's color for rays
            
            for i, ray_length in enumerate(self.ray_lengths):
                ray_length = ray_length * 2
                
                # Calculate the absolute angle of this specific ray
                ray_absolute_angle_deg = self.angle + ray_angles_relative[i]
                ray_absolute_angle_rad = np.radians(ray_absolute_angle_deg)
                
                # calculate the front of the car
                front_x = self.x + 30/2 * np.cos(ray_absolute_angle_rad)
                front_y = self.y - 20/2 * np.sin(ray_absolute_angle_rad)

                # Calculate the end point of the ray
                end_x = self.x + ray_length * np.cos(ray_absolute_angle_rad)
                # Remember Pygame's inverted Y-axis
                end_y = self.y - ray_length * np.sin(ray_absolute_angle_rad) 
                
                # Draw the line from car center to the ray end point
                pygame.draw.line(screen, ray_color, (front_x, front_y), (end_x, end_y), 2) # 1 pixel thickness

    def draw(self, screen):
        """Draws the car onto the screen."""
        # Update the image and rect before drawing
        self.update_image()
        
        if self.is_alive and self.image and self.rect:
            # Create a colored version of the image
            colored_image = self.image.copy()
            # Fill the image with the car's color, preserving alpha
            colored_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(colored_image, self.rect.topleft)
        
        self.draw_rays(screen)

