"""The actual tile server."""

import pickle
import argparse
from flask import Response, Flask
from PIL import Image
import os

app = Flask(__name__)


@app.route("/tile/<int:z>/<int:x>/<int:y>.png")
def tile(z: int, x: int, y: int) -> Response:
    """serve a tile.

    args:
        z: the zoom level, higher is closer.
        x: the x coordinate.
        y: the y coordinate.

    returns:
        a 256x256 png image
    """

    if (x, y, z) in app.cache:
        idx = app.cache[(x, y, z)]
    else:
        idx = 0

    file_path = f"assets/tiles/{z}/{idx}.png"

    if not os.path.exists(file_path):
        tile = generate_tile(idx, z)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        tile.save(file_path)

    return Response(
        open(file_path, "rb").read(),
        mimetype="image/png",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cache", help="Cache file")
    args = parser.parse_args()

    with open(args.cache, "rb") as f:
        cache = pickle.load(f)

    app.cache = cache
    app.run()


def generate_tile(idx: int, zoom_level: int) -> Image:
    """Generate a tile image.

    Args:
        idx: bitmask indicating which tiles are covered.
        zoom_level: the zoom level of the tile.

    Returns:
        A 256x256 PNG image.
    """
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))

    # Number of level 14 tiles in this zoom level
    n_tiles = 2 ** (14 - zoom_level)
    # Size of a level 14 tile in this zoom level
    pixels_per_tile = 256 // (2 ** (14 - zoom_level))
    covered = Image.new("RGBA", (pixels_per_tile, pixels_per_tile), (0, 0, 255, 80))

    for i in range(n_tiles * n_tiles):
        if (idx & (1 << i)) != 0:
            x = i % n_tiles
            y = i // n_tiles
            image.paste(
                covered,
                (x * pixels_per_tile, y * pixels_per_tile),
            )
    return image


if __name__ == "__main__":
    main()
