#!/usr/bin/env python3

import pygame
import sys
from adafruit_crickit import crickit
import time
import signal
import os
import traceback
from profilehooks import profile


# @profile
def main():
    ...  # your code here

    # Initialize Pygame
    pygame.init()

    def signal_handler(sig, frame):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Get display information
    display_info = pygame.display.Info()

    # Get screen width and height
    screen_width = display_info.current_w
    screen_height = display_info.current_h

    # Set up the display
    # screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

    print(f"Screen Dimension: {screen_width} x {screen_height}")
    pygame.display.set_caption("Minion Map")
    pygame.mouse.set_visible(False)

    # Load the large image
    tile_dir = "tiles"

    # BROKEN Initialize the joystick
    # pygame.joystick.init()
    # joystick_count = pygame.joystick.get_count()
    # if joystick_count == 0:
    #     print("No joysticks found.")
    #     sys.exit()
    # else:
    #     # print(f"Found {joystick_count} joystick(s). Using the first one.")
    #     joystick = pygame.joystick.Joystick(0)
    #     joystick.init()

    tile_width = 512
    tile_height = 512

    tile_center_x = 10500
    tile_center_y = 22885
    tile_range = 10
    tile_min_x, tile_max_x = tile_center_x - tile_range, tile_center_x + tile_range
    tile_min_y, tile_max_y = tile_center_y - tile_range, tile_center_y + tile_range

    def load_tile(x, y):
        tile_path = os.path.join(tile_dir, f"tile_{x}_{y}.png")
        return pygame.image.load(tile_path)
        # return pygame.transform.flip(tile, False, True)

    tiles = {}
    for x in range(tile_min_x, tile_max_x + 1):
        for y in range(tile_min_y, tile_max_y + 1):
            tiles[(x, y)] = load_tile(x, y)

    # Set up the panning
    pan_speed = 10  # Set the panning speed
    pixel_loc_x = tile_center_x * tile_width  # Set initial pixel_loc_x position
    pixel_loc_y = tile_center_y * tile_height  # Set initial pixl_loc_y position
    old_pixel_loc_x = 0
    old_pixel_loc_y = 0

    # Set up the motors
    pan_motor = crickit.dc_motor_1
    tilt_motor = crickit.dc_motor_2
    pan_motor.throttle = 0
    tilt_motor.throttle = 0
    pan_motor_throttle = 0
    tilt_motor_throttle = 0

    need_stitch = True
    clock = pygame.time.Clock()
    current_tile_x = tile_center_x
    current_tile_y = tile_center_y
    visible_tiles_x = 2 + screen_width // tile_width
    visible_tiles_y = 2 + screen_height // tile_height

    def stitch_tiles(start_x, start_y, num_tiles_x, num_tiles_y):
        stitched_surface = pygame.Surface(
            (num_tiles_x * tile_width, num_tiles_y * tile_height)
        )
        # print(f"stitch_tiles({('tiles', start_x, start_y, num_tiles_x, num_tiles_y)})")

        for y in range(num_tiles_y):
            for x in range(num_tiles_x):
                tile_key = (int(start_x) + x, int(start_y) + y)
                # print(f"Stitching tile {tile_key} at ({x * tile_width}, {y * tile_height})")
                try:
                    tile = tiles[tile_key]
                    stitched_surface.blit(tile, (x * tile_width, y * tile_height))
                except Exception as e:
                    print(f"An error occurred: {type(e).__name__}: {e}")

        return stitched_surface

    large_surface = stitch_tiles(tile_min_x, tile_min_y, 2 * tile_range, 2 * tile_range)

    def blit_screen(screen, pixel_loc_x, pixel_loc_y):
        start_x = pixel_loc_x // tile_width - 1
        start_y = pixel_loc_y // tile_height - 1

        screen_blit_coords = (
            -(pixel_loc_x % tile_width),
            -(pixel_loc_y % tile_height),
        )
        for y in range(visible_tiles_y):
            for x in range(visible_tiles_x):
                tile_key = (int(start_x) + x, int(start_y) + y)
                # print(f"Stitching tile {tile_key} at ({x * tile_width}, {y * tile_height})")
                try:
                    tile = tiles[tile_key]
                    screen.blit(
                        tile,
                        (
                            x * tile_width + screen_blit_coords[0],
                            y * tile_height + screen_blit_coords[1],
                        ),
                    )
                except Exception as e:
                    print(f"An error occurred: {type(e).__name__}: {e}")

    try:
        # Main loop
        motor_update_interval = 0.1  # Time in seconds between motor updates
        last_motor_update_time = time.monotonic()
        old_pan_motor_throttle = 0
        old_tilt_motor_throttle = 0
        mode = 'a'
        pixel_loc_x_speed, pixel_loc_y_speed = 0, 0
        start_time = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pan_motor.throttle = 0
                    tilt_motor.throttle = 0
                    pygame.quit()
                    sys.exit()

            # Pan the image
            old_tile_x, old_tile_y = current_tile_x, current_tile_y

            throttle_factor = 1
            pan_factor = 10

            h_throttle_factor = .8
            v_throttle_factor = 1
            h_pan_factor = 30
            v_pan_factor = 20

            # Pan the image
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                # print("Left")
                mode = 'm'
                pixel_loc_x_speed = -1 * h_pan_factor
                pan_motor.throttle = -1 * h_throttle_factor
            elif keys[pygame.K_RIGHT]:
                # print("Right")
                mode = 'm'
                pixel_loc_x_speed = h_pan_factor
                pan_motor.throttle = h_throttle_factor
            elif mode == 'm':
                pixel_loc_x_speed = 0
                pan_motor.throttle = 0

            if keys[pygame.K_UP]:
                # print("Up")
                mode = 'm'
                pixel_loc_y_speed = -1 * v_pan_factor
                tilt_motor.throttle = -1 * v_throttle_factor
            elif keys[pygame.K_DOWN]:
                # print("Down")
                mode = 'm'
                pixel_loc_y_speed = v_pan_factor
                tilt_motor.throttle = v_throttle_factor
            elif mode == 'm':
                pixel_loc_y_speed = 0
                tilt_motor.throttle = 0


            current_time = time.monotonic()
            if (
                current_time - last_motor_update_time >= motor_update_interval
                and (pan_motor_throttle != old_pan_motor_throttle
                    or tilt_motor_throttle != old_tilt_motor_throttle)
            ):
                pan_motor.throttle = pan_motor_throttle
                tilt_motor.throttle = tilt_motor_throttle
                last_motor_update_time = current_time
                old_pan_motor_throttle = pan_motor_throttle
                old_tilt_motor_throttle = tilt_motor_throttle

            if keys[pygame.K_q]:
                raise Exception("Quit!")


            pixel_loc_x += pixel_loc_x_speed
            pixel_loc_y += pixel_loc_y_speed

            # Calculate the current x and y tile indices

            if old_pixel_loc_x != pixel_loc_x or old_pixel_loc_y != pixel_loc_y:
                screen.blit(
                    large_surface.subsurface(
                        pygame.Rect(
                            pixel_loc_x - tile_min_x * tile_width,
                            pixel_loc_y - tile_min_y * tile_height,
                            screen_width,
                            screen_height,
                        )
                    ),
                    (0, 0),
                )
                # blit_screen(
                #     screen,
                #     pixel_loc_x,
                #     pixel_loc_y,
                # )

                pygame.display.flip()

            old_pixel_loc_x = pixel_loc_x
            old_pixel_loc_y = pixel_loc_y
            clock.tick(30)  # Set the desired framerate (e.g., 60 FPS)

    except Exception as e:
        print(f"An error occurred: {type(e).__name__}: {e}")
        print("Traceback:")
        traceback.print_exc()

    finally:
        print("In finally block...")
        pan_motor.throttle = 0
        tilt_motor.throttle = 0
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
