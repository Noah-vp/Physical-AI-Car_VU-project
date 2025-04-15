import pygame
import numpy as np
import os

class Car:
    is_alive = True
    # Make MAX_RAY_LENGTH a class constant for easy access
    MAX_RAY_LENGTH = 200 
    
    # Movement parameters as class constants
    SPEED = 1  # Constant speed for all cars
    ROTATION_SPEED = 1  # Degrees per frame/update when turning


    def __init__(self, start_x, start_y, track, start_angle=0, color=(255, 0, 0)):  # Default color is red
        """Initializes the car's position, angle, and loads its image."""
        # Position and orientation
        self.x = start_x
        self.y = start_y
        self.angle = start_angle # Degrees, 0 is right, positive is counter-clockwise
        self.track = track
        self.color = color  # Store the car's color
        # self.screen = screen # Remove screen dependency from init
        
        # Initialize ray_lengths for this specific car instance
        self.ray_lengths = [1.0] * 5 # Start with max length (normalized)

        # Movement parameters
        self.speed = Car.SPEED  # Use class constant
        self.rotation_speed = Car.ROTATION_SPEED  # Use class constant

        # Performance tracking
        self.frames_alive = 0
        self.distance_traveled = 0
        self.last_position = (start_x, start_y)
        self.progress = 0  # Track progress along the track
        self.last_progress_update = 0  # Frames since last progress increase
        self.turning_penalty = 0  # Penalty for excessive turning

        # Lap tracking
        self._half_laps = 0
        self._last_col = None
        self.laps = 0

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
            # Scale the image to a reasonable size (e.g., 30x15 pixels)
            # Get original dimensions and calculate scale factor to maintain ratio
            orig_width = loaded_image.get_width()
            orig_height = loaded_image.get_height()
            scale_factor = 10 / orig_width  # Scale to 30px width
            scaled_width = 10
            scaled_height = int(orig_height * scale_factor)
            scaled_image = pygame.transform.scale(loaded_image, (scaled_width, scaled_height))
            # Assume the loaded image points UP. Rotate it so that 0 degrees angle points RIGHT.
            self.base_image = pygame.transform.rotate(scaled_image, -90) # Rotate 90 deg clockwise
        except pygame.error as e:
            print(f"Error loading car image at {image_path}: {e}")
            # Create a placeholder red rectangle if image loading fails
            self.base_image = pygame.Surface((30, 15))
            self.base_image.fill((255, 0, 0))
            self.base_image.set_colorkey((0, 0, 0))

    def control(self, steering, sensitivity):
        """Adjusts the car's angle based on left/right input flags (0 or 1)."""
        if steering >= sensitivity:
            self.angle += self.rotation_speed # Turn left (positive angle change)
            self.turning_penalty += abs(steering) * 0.1  # Small penalty for turning
        elif steering <= -sensitivity:
            self.angle -= self.rotation_speed # Turn right (negative angle change)
            self.turning_penalty += abs(steering) * 0.1
        self.angle %= 360 # Keep angle within 0-360 degrees

    def update(self):
        """Updates the car's position and checks for collisions."""
        if not self.is_alive:
            return
        # Store previous position
        old_x, old_y = self.x, self.y
        
        # Update position based on current angle and speed
        self.x += self.speed * np.cos(np.radians(self.angle))
        self.y -= self.speed * np.sin(np.radians(self.angle))  # Negative because pygame y increases downward
        
        # Calculate distance traveled this frame
        dx = self.x - old_x
        dy = self.y - old_y
        frame_distance = np.sqrt(dx*dx + dy*dy)
        self.distance_traveled += frame_distance

        # Update the image and rect for drawing
        if self.base_image:
            # Pygame rotates counter-clockwise
            self.image = pygame.transform.rotate(self.base_image, self.angle)
            self.rect = self.image.get_rect(center=(self.x, self.y))
        
        # Check for collisions
        self.check_collision()
        
        # Update ray casting
        self.ray_cast()
        
        # Update performance metrics if still alive
        if self.is_alive:
            self.frames_alive += 1
            self.check_lap()

    def draw(self, screen):
        """Draws the car onto the screen."""
        if self.is_alive and self.image and self.rect:
            # Create a colored version of the image
            colored_image = self.image.copy()
            # Fill the image with the car's color, preserving alpha
            colored_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(colored_image, self.rect.topleft)
        elif self.base_image: # Fallback: draw base image if rotated image isn't available
             # This might happen if update_image_rect hasn't been called or failed
             center_x = self.x - self.base_image.get_width() // 2
             center_y = self.y - self.base_image.get_height() // 2
             colored_image = self.base_image.copy()
             colored_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
             screen.blit(colored_image, (center_x, center_y))

        # Draw the sensor rays in the same color as the car
        if self.is_alive and self.ray_lengths:
            ray_angles_relative = [-90, -45, 0, 45, 90] # Relative angles in degrees
            ray_color = self.color # Use the car's color for rays
            
            for i, normalized_length in enumerate(self.ray_lengths):
                # Calculate the actual length in pixels
                actual_length = normalized_length * Car.MAX_RAY_LENGTH
                
                # Calculate the absolute angle of this specific ray
                ray_absolute_angle_deg = self.angle + ray_angles_relative[i]
                ray_absolute_angle_rad = np.radians(ray_absolute_angle_deg)
                
                # Calculate the end point of the ray
                end_x = self.x + actual_length * np.cos(ray_absolute_angle_rad)
                # Remember Pygame's inverted Y-axis
                end_y = self.y - actual_length * np.sin(ray_absolute_angle_rad) 
                
                # Draw the line from car center to the ray end point
                pygame.draw.line(screen, ray_color, (self.x, self.y), (end_x, end_y), 1) # 1 pixel thickness

    def check_collision(self):
        """Checks if the car has collided with the track walls."""
        if self.rect is None or self.track.layout is None:
            return False # Cannot check collision if rect or track is not ready

        # Get car dimensions from rect - use base_image for more stable dimensions
        if self.base_image:
            car_width = self.base_image.get_width()
            car_height = self.base_image.get_height()
        else:
            return False # Can't determine size

        # Calculate the four corner points of the car based on its center (self.x, self.y), 
        # dimensions, and angle.
        # This requires rotating the corner offsets.
        rad_angle = np.radians(self.angle)
        cos_a = np.cos(rad_angle)
        sin_a = np.sin(rad_angle)
        
        half_w = car_width / 2
        half_h = car_height / 2

        # Define offsets from center to corners in the car's local coordinate system
        local_corners = [
            (-half_w, -half_h), # Top-left 
            ( half_w, -half_h), # Top-right
            (-half_w,  half_h), # Bottom-left
            ( half_w,  half_h)  # Bottom-right
        ]

        corners_world = []
        for lx, ly in local_corners:
            # Rotate the local corner offset
            rotated_x = lx * cos_a - ly * sin_a
            rotated_y = lx * sin_a + ly * cos_a
            # Add the car's world position to get the corner's world position
            world_x = self.x + rotated_x
            world_y = self.y - rotated_y # Pygame's y-axis is inverted
            corners_world.append((world_x, world_y))

        # Check collision for each corner in world coordinates
        for corner_x, corner_y in corners_world:
            # Convert world pixel coordinates to track grid coordinates
            grid_col = int((corner_x - self.track.PIXEL_MARGIN) // (self.track.PIXEL_WIDTH + self.track.PIXEL_MARGIN))
            grid_row = int((corner_y - self.track.PIXEL_MARGIN) // (self.track.PIXEL_HEIGHT + self.track.PIXEL_MARGIN))

            # Check boundaries
            if not (0 <= grid_row < self.track.rows and 0 <= grid_col < self.track.cols):
                # print(f"Collision: Corner ({corner_x:.1f}, {corner_y:.1f}) -> Grid ({grid_row}, {grid_col}) is out of bounds")
                self.is_alive = False
                return True # Corner is outside the track boundaries

            # Check if the cell the corner is in is a wall (layout == 0)
            if self.track.layout[grid_row, grid_col] == 0:
                # print(f"Collision: Corner ({corner_x:.1f}, {corner_y:.1f}) -> Grid ({grid_row}, {grid_col}) is a wall")
                self.is_alive = False
                return True # Corner hit a wall
        
        return False # No collision detected

    def ray_cast(self):
        """Ray casts the car's rays and returns the length of each ray.
        
        The car casts 5 rays in different angles to detect walls:
        - Center ray points straight ahead
        - Two rays point 45 degrees left/right of center
        - Two rays point 90 degrees left/right of center
        
        Returns:
            list[float]: List of ray lengths, normalized between 0 and 1.
                        0 means the ray hit a wall immediately
                        1 means the ray reached its maximum length
        """
        # Define ray angles relative to car's heading
        ray_angles = [-90, -45, 0, 45, 90]  # degrees
        self.ray_lengths = []
        
        # Cast each ray
        for angle in ray_angles:
            # Calculate absolute angle of ray in world space
            ray_angle = self.angle + angle
            ray_rad = np.radians(ray_angle)
            
            # Ray direction unit vector
            ray_dx = np.cos(ray_rad)
            ray_dy = -np.sin(ray_rad)  # Negative because Pygame y-axis is inverted
            
            # Start ray from car's center
            ray_x = self.x
            ray_y = self.y
            
            # Maximum ray length
            MAX_RAY_LENGTH = 200  # pixels
            ray_length = 0
            step_size = 5  # pixels per step
            
            # Step ray forward until it hits a wall or reaches max length
            while ray_length < MAX_RAY_LENGTH:
                # Move ray tip forward
                ray_x += ray_dx * step_size
                ray_y += ray_dy * step_size
                ray_length += step_size
                
                # Convert ray tip position to grid coordinates
                grid_col = int((ray_x - self.track.PIXEL_MARGIN) // (self.track.PIXEL_WIDTH + self.track.PIXEL_MARGIN))
                grid_row = int((ray_y - self.track.PIXEL_MARGIN) // (self.track.PIXEL_HEIGHT + self.track.PIXEL_MARGIN))
                
                # Check if ray hit wall
                if (not (0 <= grid_row < self.track.rows and 0 <= grid_col < self.track.cols) or
                    self.track.layout[grid_row, grid_col] == 0):
                    break
            
            # Normalize ray length between 0 and 1
            normalized_length = ray_length / MAX_RAY_LENGTH
            self.ray_lengths.append(normalized_length)
        
        return self.ray_lengths

    def check_lap(self):
        """Checks if the car has completed a lap. by using the distance from the start position."""
        # Convert current position to grid coordinates
        grid_col = int((self.x - self.track.PIXEL_MARGIN) // (self.track.PIXEL_WIDTH + self.track.PIXEL_MARGIN))
        
        # Check if we've crossed the start line
        if self._last_col != grid_col and grid_col == self.track.start_pos[0]:
            self._half_laps += 1
        self.laps = self._half_laps // 2
        self._last_col = grid_col
        if self.laps > 2:
            self.is_alive = False

