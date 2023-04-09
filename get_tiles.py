import os
import requests

# Replace with your Mapbox access token
mapbox_access_token = "sk.eyJ1Ijoiai1jYWx2ZXJ0IiwiYSI6ImNsZzdhd3lrdTBscHQzZm84dDVya3diYW0ifQ.bLGHPHH-nYFf-3jK71V-CQ"

# Set the tile settings
zoom_level = 16
center_x = 10500
center_y =  22885
tile_range = 10
min_x, max_x = center_x - tile_range, center_x + tile_range
min_y, max_y = center_y - tile_range, center_y + tile_range

# Set the output directory to save the downloaded tiles
tile_dir = "tiles"
os.makedirs(tile_dir, exist_ok=True)

# Define the Mapbox Static Tiles API URL template
url_template = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token={token}"

# Download the tiles
for x in range(min_x, max_x + 1):
    for y in range(min_y, max_y + 1):
        url = url_template.format(z=zoom_level, x=x, y=y, token=mapbox_access_token)
        response = requests.get(url)

        if response.status_code == 200:
            tile_path = os.path.join(tile_dir, f"tile_{x}_{y}.png")
            with open(tile_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded tile {x}_{y}")
        else:
            print(f"Error downloading tile {x}_{y}: {response.status_code}")

print("Finished downloading tiles.")