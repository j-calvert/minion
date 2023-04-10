import os
import requests
import mapbox_access_token
import styles_and_centers

# Replace with your Mapbox access token
token = mapbox_access_token.mapbox_access_token


def get_tiles(style, zoom_level, center_x, center_y, tile_range):
    min_x, max_x = center_x - tile_range, center_x + tile_range
    min_y, max_y = center_y - tile_range, center_y + tile_range

    # Set the output directory to save the downloaded tiles
    tile_dir = f"tiles/{style}/{zoom_level}"
    os.makedirs(tile_dir, exist_ok=True)

    # Download the tiles
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            url = f"https://api.mapbox.com/styles/v1/mapbox/{style}/tiles/{zoom_level}/{x}/{y}?access_token={token}"
            response = requests.get(url)

            if response.status_code == 200:
                tile_path = os.path.join(tile_dir, f"tile_{x}_{y}.png")
                with open(tile_path, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded tile {x}_{y}")
            else:
                print(
                    f"Error downloading tile {x}_{y}: {response.status_code}")

    print("Finished downloading tiles for {style} at zoom level {zoom_level}.")


if __name__ == "__main__":
    for c_i in range(0, len(styles_and_centers.centers), 4):
        for style in styles_and_centers.styles:
            (zoom_level, center_x, center_y, pix_x,
             pix_y) = styles_and_centers.parse_center(styles_and_centers.centers[c_i])
            get_tiles(style, zoom_level, center_x, center_y,
                      styles_and_centers.tile_range)
