import pygame

# Initialize Pygame
pygame.init()

# Get display information
display_info = pygame.display.Info()

# Get screen width and height
screen_width = display_info.current_w
screen_height = display_info.current_h

print(f"Screen width: {screen_width}, Screen height: {screen_height}")
