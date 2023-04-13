import os
import requests
import mapbox_access_token
import styles_and_centers
from concurrent.futures import ThreadPoolExecutor

token = mapbox_access_token.mapbox_access_token


def get_title_dir(style, zoom_level):
    return f"tiles/{style}/{zoom_level}"


tile_loading_executor = ThreadPoolExecutor(max_workers=4)


def get_tiles(style, zoom_level, center_x, center_y, tile_range):
    min_x, max_x = center_x - tile_range, center_x + tile_range
    min_y, max_y = center_y - tile_range, center_y + tile_range
    print(
        f"Starting downloading tiles for {style} at zoom level {zoom_level}.")

    # Download the tiles
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            tile_loading_executor.submit(
                get_tile, style, zoom_level, x, y)

    print(
        f"Finished downloading tiles for {style} at zoom level {zoom_level}.")


def get_tile(style, zoom_level, x, y):
    # Set the output directory to save the downloaded tiles
    tile_dir = get_title_dir(style, zoom_level)
    os.makedirs(tile_dir, exist_ok=True)

    tile_path = os.path.join(tile_dir, f"tile_{x}_{y}.png")
    if os.path.isfile(tile_path):
        # print(f"Tile {tile_path} already exists, skipping download.")
        return tile_path

    url = f"https://api.mapbox.com/styles/v1/mapbox/{style}/tiles/{zoom_level}/{x}/{y}?access_token={token}"
    response = requests.get(url)

    if response.status_code == 200:
        with open(tile_path, "wb") as f:
            f.write(response.content)
        # print(f"Downloaded tile {tile_path}")
    else:
        print(
            f"Error downloading tile {tile_path}: {response.status_code}")
    return tile_path


if __name__ == "__main__":
    for center in styles_and_centers.centers:
        for style in styles_and_centers.styles:
            (zoom_level, center_x, center_y) = styles_and_centers.parse_center(
                center)
            get_tiles(style, zoom_level, center_x // styles_and_centers.tile_width,
                      center_y // styles_and_centers.tile_height,
                      styles_and_centers.tile_range)
