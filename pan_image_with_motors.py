import pygame
import sys
from adafruit_crickit import crickit
import time
import signal
import traceback
import math
import styles_and_centers
import get_tiles
from concurrent.futures import ThreadPoolExecutor
from LRUCache import LRUCache
from triangle import triangle_wave

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
screen = pygame.display.set_mode(
    (screen_width, screen_height), pygame.FULLSCREEN)
# print(f"Screen Dimension: {screen_width} x {screen_height}")
pygame.display.set_caption("Pan Large Image")
pygame.mouse.set_visible(False)


tile_width = styles_and_centers.tile_width
tile_height = styles_and_centers.tile_height

visible_tiles_x = 2 + screen_width // tile_width
visible_tiles_y = 2 + screen_height // tile_height

tiles = LRUCache(max_size=4096)

styles = styles_and_centers.styles
centers = [styles_and_centers.parse_center(
    center) for center in styles_and_centers.centers]

tile_loading_executor = ThreadPoolExecutor(max_workers=8)
tiles_in_progress = set()


def get_tile_key(style, zoom_level, x, y):
    return (style, zoom_level, x, y)


def load_tile_async(style, z, x, y):
    # print(f"load_tile_async{(style, z, x, y)}")
    tile_path = get_tiles.get_tile(style, z, x, y)
    # print(f"tile_path = {tile_path}")
    tile = pygame.image.load(tile_path)
    tiles.set((style, z, x, y), tile)


def blit_screen(screen, style, zoom, pixel_loc_x, pixel_loc_y):
    # print(f"pixel_loc: ({pixel_loc_x}, {pixel_loc_y})")
    start_x = pixel_loc_x // tile_width - 1
    start_y = pixel_loc_y // tile_height - 1

    screen_blit_coords = (
        -(pixel_loc_x % tile_width),
        -(pixel_loc_y % tile_height),
    )
    for y_i in range(visible_tiles_y):
        for x_i in range(visible_tiles_x):
            x = int(start_x) + x_i
            y = int(start_y) + y_i
            tile_key = (style, zoom, x, y)
            # print(
            #     f"Stitching tile {tile_key} at ({x * tile_width}, {y * tile_height})")
            try:
                if tile_key in tiles:
                    tile = tiles.get(tile_key)
                    screen.blit(
                        tile,
                        (
                            int(x_i * tile_width + screen_blit_coords[0]),
                            int(y_i * tile_height + screen_blit_coords[1]),
                        ),
                    )
                else:
                    # (Code for drawing a black rectangle)
                    pygame.draw.rect(screen, (0, 0, 0), (int(x_i * tile_width + screen_blit_coords[0]),
                                                         int(y_i * tile_height + screen_blit_coords[1]),
                                                         tile_width, tile_height))
                    if tile_key not in tiles_in_progress:
                        tiles_in_progress.add(tile_key)
                        tile_loading_executor.submit(
                            load_tile_async, style, zoom, x, y)
            except Exception as e:
                print(f"An error occurred: {type(e).__name__}: {e}")

# Set up the motors
pan_motor = crickit.dc_motor_1
tilt_motor = crickit.dc_motor_2
pan_motor.throttle = 0
tilt_motor.throttle = 0

clock = pygame.time.Clock()


def main():
    style_idx, center_idx = 1, 4
    pixel_loc_x = centers[center_idx][1]
    pixel_loc_y = centers[center_idx][2]
    mode = 'm'

    # Pan/Tilt slop
    latest = {}
    latest[pygame.K_LEFT] = time.time() - 1 # Prevents initial movement
    latest[pygame.K_RIGHT] = 0
    latest[pygame.K_UP] = 0
    latest[pygame.K_DOWN] = 0

    # Pan/Tilt slop
    slop = {}
    slop[pygame.K_LEFT] = 0.125
    slop[pygame.K_RIGHT] = 0.25
    slop[pygame.K_UP] = 0.3
    slop[pygame.K_DOWN] = 0.3

    # Automation mode
    auto = {}
    auto[pygame.K_LEFT] = False
    auto[pygame.K_RIGHT] = False
    auto[pygame.K_UP] = False
    auto[pygame.K_DOWN] = False
    h_throttle_factor = 1
    v_throttle_factor = 1
    pan_motor_auto_baseline = 0.025
    tilt_motor_auto_baseline = 0.0125
    h_pan_factor = 33
    v_pan_factor = 14
    #  Should be a whole multiple of the periods below so multiole cycles of auto return to original position.
    time_before_auto_start = 24 
    x_period = 8
    y_period = 12

    pre_auto_pixel_loc = None

    config_enabled = True



    try:
        # Main loop
        start_time = time.time()
        while True:
            keys = pygame.key.get_pressed()
            shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pan_motor.throttle = 0
                    tilt_motor.throttle = 0
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_q and shift:
                        raise Exception("Quit!")
                    if event.key == pygame.K_b and shift:
                        config_enabled = not config_enabled
                        if config_enabled:
                            style_idx = (style_idx + 1) % len(styles)
                        else:
                            pixel_loc_x = centers[center_idx][1]
                            pixel_loc_y = centers[center_idx][2]
                        print(f"Config Enabled set to {config_enabled}")
                    if event.key == pygame.K_c:
                        pixel_loc_x = centers[center_idx][1]
                        pixel_loc_y = centers[center_idx][2]
                    if event.key == pygame.K_a:
                        mode = 'a'
                        print(f"Starting autocyle at pixel_loc: ({pixel_loc_x}, {pixel_loc_y})")
                        style_idx_auto_start = style_idx
                        start_time = time.time()
                    if event.key == pygame.K_p:
                        print(f"pan_motor_auto_baseline = {pan_motor_auto_baseline}")
                        print(f"tilt_motor_auto_baseline = {tilt_motor_auto_baseline}")
                        print(f"h_pan_factor = {h_pan_factor}")
                        print(f"v_pan_factor = {v_pan_factor}")
                    if config_enabled:
                        if event.key == pygame.K_j:
                            h_pan_factor -= 1
                            print(f"h_pan_factor now: {h_pan_factor}")
                        if event.key == pygame.K_l:
                            h_pan_factor += 1
                            print(f"h_pan_factor now: {h_pan_factor}")
                        if event.key == pygame.K_i:
                            v_pan_factor += 1
                            print(f"v_pan_factor now: {v_pan_factor}")
                        if event.key == pygame.K_k:
                            v_pan_factor -= 1
                            print(f"v_pan_factor now: {v_pan_factor}")
                        if event.key == pygame.K_h:
                            pan_motor_auto_baseline -= 0.0025
                            print(f"pan_motor_auto_baseline now: {pan_motor_auto_baseline}")
                        if event.key == pygame.K_f:
                            pan_motor_auto_baseline += 0.0025
                            print(f"pan_motor_auto_baseline now: {pan_motor_auto_baseline}")
                        if event.key == pygame.K_t:
                            tilt_motor_auto_baseline += 0.0025
                            print(f"tilt_motor_auto_baseline now: {tilt_motor_auto_baseline}")
                        if event.key == pygame.K_g:
                            tilt_motor_auto_baseline -= 0.0025
                            print(f"tilt_motor_auto_baseline now: {tilt_motor_auto_baseline}")
                    if event.key == pygame.K_s:
                        style_idx = (
                            style_idx + (1 if shift else -1)) % len(styles)
                        print(f"Style now: {styles[style_idx]}")
                    if event.key == pygame.K_z or event.key == pygame.K_x:
                        out = event.key == pygame.K_x
                        if (center_idx == 0 and not out) or center_idx == len(centers) - 1 and out:
                            print(
                                f"Ignoring zoom request, already at {'max' if out else 'min'} zoom level")
                        else:
                            center_idx = (
                                center_idx + (1 if out else -1)) % len(centers)
                            pixel_loc_x = pixel_loc_x // 2 if out else pixel_loc_x * 2
                            pixel_loc_y = pixel_loc_y // 2 if out else pixel_loc_y * 2
                            print(
                                f"Zoom level now: {centers[center_idx][0]}, and pixel_loc: ({pixel_loc_x}, {pixel_loc_y})")

            now = time.time()
            if keys[pygame.K_LEFT] or auto[pygame.K_LEFT]:
                if keys[pygame.K_LEFT]:
                    mode = 'm'
                if shift:
                    pan_motor.throttle = h_throttle_factor
                    pixel_loc_x_speed = 0
                else:
                    pan_motor.throttle = -h_throttle_factor
                    pixel_loc_x_speed = -1 *  h_pan_factor
                    latest[pygame.K_LEFT] = now
            elif keys[pygame.K_RIGHT] or auto[pygame.K_RIGHT]:
                if keys[pygame.K_RIGHT]:
                    mode = 'm'
                if shift: 
                    pan_motor.throttle = -h_throttle_factor
                else:
                    pan_motor.throttle = h_throttle_factor
                    pixel_loc_x_speed = 1 * h_pan_factor
                    latest[pygame.K_RIGHT] = now
            else:
                pixel_loc_x_speed = 0
                pan_motor.throttle = 0
                if now - latest[pygame.K_RIGHT] < slop[pygame.K_RIGHT]:
                    pixel_loc_x_speed = h_pan_factor * \
                        (1 - (now - latest[pygame.K_RIGHT]
                              ) / slop[pygame.K_RIGHT])
                elif now - latest[pygame.K_LEFT] < slop[pygame.K_LEFT]:
                    pixel_loc_x_speed = -1 * h_pan_factor * \
                        (1 - (now - latest[pygame.K_LEFT]) /
                         slop[pygame.K_LEFT])

            if keys[pygame.K_UP] or auto[pygame.K_UP]:
                # print("Up")
                if keys[pygame.K_UP]:
                    mode = 'm'
                if shift:
                    tilt_motor.throttle = v_throttle_factor
                else:
                    tilt_motor.throttle = -1 * v_throttle_factor
                    pixel_loc_y_speed = -1 * v_pan_factor
                    latest[pygame.K_UP] = now
            elif keys[pygame.K_DOWN] or auto[pygame.K_DOWN]:
                # print("Down")
                if keys[pygame.K_DOWN]:
                    mode = 'm'
                if shift:
                    tilt_motor.throttle = -1 * v_throttle_factor
                else:
                    tilt_motor.throttle = v_throttle_factor
                    pixel_loc_y_speed = v_pan_factor
                    latest[pygame.K_DOWN] = now
            else:
                pixel_loc_y_speed = 0
                tilt_motor.throttle = 0
                if now - latest[pygame.K_UP] < slop[pygame.K_UP]:
                    pixel_loc_y_speed = -1 * v_pan_factor * \
                        (1 - (now - latest[pygame.K_UP]) / slop[pygame.K_UP])
                elif now - latest[pygame.K_DOWN] < slop[pygame.K_DOWN]:
                    pixel_loc_y_speed = v_pan_factor * \
                        (1 - (now - latest[pygame.K_DOWN]) /
                         slop[pygame.K_DOWN])
                    
            if now - max(latest.values()) > time_before_auto_start:
                start_time = time.time()
                style_idx = (style_idx + 1) % len(styles)
                pre_auto_pixel_loc = (pixel_loc_x, pixel_loc_y)
                print(f"Starting autocyle, with style now: {styles[style_idx]} at pixel_loc: ({pixel_loc_x}, {pixel_loc_y})")
                mode = 'a'

            overall_scale = 1
            if mode == 'a':
                current_time = time.time() - start_time
                # style_idx = int((style_idx_auto_start + (current_time // (x_period * y_period))) % len(styles))
                # x_speed = 0
                x_speed = overall_scale * triangle_wave(current_time, x_period)
                auto[pygame.K_LEFT] = x_speed < pan_motor_auto_baseline - .5
                auto[pygame.K_RIGHT] = x_speed > pan_motor_auto_baseline + .5
                y_speed = overall_scale * triangle_wave(current_time, y_period)
                # y_speed = 0
                auto[pygame.K_UP] = y_speed < tilt_motor_auto_baseline - .5
                auto[pygame.K_DOWN] = y_speed > tilt_motor_auto_baseline + .5
                # if current_time >= x_period * y_period:
                #     mode = 'm'
                if now - start_time > time_before_auto_start:
                    print(f"Ending autocyle at pixel_loc: ({pixel_loc_x}, {pixel_loc_y})")
                    if pre_auto_pixel_loc:
                        pixel_loc_x = pre_auto_pixel_loc[0]
                        pixel_loc_y = pre_auto_pixel_loc[1]
                        pre_auto_pixel_loc = None                    
                        print(f"adjusted to: ({pixel_loc_x}, {pixel_loc_y})")
                    mode = 'm'
            else:
                auto[pygame.K_LEFT] = False
                auto[pygame.K_RIGHT] = False
                auto[pygame.K_UP] = False
                auto[pygame.K_DOWN] = False

            pixel_loc_x += pixel_loc_x_speed
            pixel_loc_y += pixel_loc_y_speed

            # if old_pixel_loc_x != pixel_loc_x or old_pixel_loc_y != pixel_loc_y:
            blit_screen(
                screen,
                styles[style_idx],
                centers[center_idx][0],
                pixel_loc_x,
                pixel_loc_y,
            )

            pygame.display.flip()

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


if __name__ == "__main__":
    main()
