import time
import math
from adafruit_crickit import crickit
import signal
import pygame
import sys
import traceback


pygame.init()
clock = pygame.time.Clock()


# Set up the motors
pan_motor = crickit.dc_motor_1
tilt_motor = crickit.dc_motor_2
pan_motor.throttle = 0
tilt_motor.throttle = 0


def signal_handler(sig, frame):
    pygame.event.post(pygame.event.Event(pygame.QUIT))


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Get display information
display_info = pygame.display.Info()

# Get screen width and height
screen_width = display_info.current_w
screen_height = display_info.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

# Set the window caption
pygame.display.set_caption('Image Display')

# Load the image
image_path = 'minion.png'
image = pygame.image.load(image_path)
image_rect = image.get_rect()

image_rect.center = (screen_width // 2, screen_height // 2)


try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pan_motor.throttle = 0
                tilt_motor.throttle = 0
                pygame.quit()
                sys.exit()

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw the image
        screen.blit(image, image_rect)

        # Update the display
        pygame.display.flip()
        # Pan the image
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            print("Left")
            pan_motor.throttle = -1
        elif keys[pygame.K_RIGHT]:
            print("Right")
            pan_motor.throttle = 1
        else:
            pan_motor.throttle = 0

        if keys[pygame.K_UP]:
            print("Up")
            tilt_motor.throttle = -1
        elif keys[pygame.K_DOWN]:
            print("Down")
            tilt_motor.throttle = 1
        else:
            tilt_motor.throttle = 0

        if keys[pygame.K_q]:    
            raise Exception("Quit!")

        clock.tick(60)  # Set the desired framerate (e.g., 60 FPS)


except Exception as e:
    # print(f"An error occurred: {type(e).__name__}: {e}")
    # print("Traceback:")
    traceback.print_exc()


finally:
    pan_motor.throttle = 0
    tilt_motor.throttle = 0
    pygame.quit()
    sys.exit()
