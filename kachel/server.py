"""The actual tile server."""

import argparse
import io
import os
import pickle
from typing import Dict, Tuple

from flask import Flask, Response
from PIL import Image

app = Flask(__name__)


@app.route("/<string:user_id>/<int:z>/<int:x>/<int:y>.png")
def default_tile(user_id: str, z: int, x: int, y: int) -> Response:
    """Serving the default tile at zoom level 14.

    Args:
        user_id: The user id.
        z: the zoom level, higher is closer.
        x: the x coordinate.
        y: the y coordinate.

    Returns:
        A 256x256 png image
    """
    return tile(user_id, 14, z, x, y)


@app.route("/<string:user_id>/<int:tile_level>/<int:z>/<int:x>/<int:y>.png")
def tile(user_id: str, tile_level: int, z: int, x: int, y: int) -> Response:
    """Serve a tile at specified zoom level.

    Args:
        user_id: The user id.
        tile_level: The target zoom level of the tile.
            Options are 14, 15, 16.
        z: the zoom level, higher is closer.
        x: the x coordinate.
        y: the y coordinate.

    Returns:
        A 256x256 png image
    """

    if user_id not in app.cache:
        return Response(
            f"User id {user_id} not found.",
            status=404,
        )

    if tile_level not in app.cache[user_id]:
        return Response(
            f"Tile level {tile_level} not found. Available levels: {app.cache[user_id].keys()}",
            status=404,
        )

    tile_idx = 0
    max_square_idx = 0
    if (x, y, z) in app.cache[user_id][tile_level]:
        tile_idx = app.cache[user_id][tile_level][(x, y, z)]["tiles"]
        max_square_idx = app.cache[user_id][tile_level][(x, y, z)]["max_square"]

    tile = generate_tile(tile_idx, max_square_idx, z, tile_level)

    img_byte_arr = io.BytesIO()
    tile.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    return Response(
        img_byte_arr,
        mimetype="image/png",
    )


@app.route("/users")
def users() -> Response:
    """Return a list of endpoints for all users."""

    endpoints = [
        f"<li><code>/{user_id}/{{z}}/{{x}}/{{y}}.png</code></li>"
        for user_id in app.cache.keys()
    ]
    page = f"""
    <html>
        <body>
            <ul>
                {''.join(endpoints)}
            </ul>
        </body>
    </html>
    """
    return Response(
        page,
        mimetype="text/html",
    )


def generate_tile(
    idx: int, max_square_idx: int, zoom_level: int, tile_level: int = 16
) -> Image.Image:
    """Generate a tile image.

    Args:
        idx: Bitmask indicating which tiles are covered.
        max_square_idx: Bitmask indicating which tiles are part of a max square.
        zoom_level: The zoom level of the tile.
        tile_level: The zoom level of the tiles in the bitmask.

    Returns:
        A 256x256 PNG image.
    """
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))

    if zoom_level > tile_level:
        return image

    # Number of level target_zoom tiles in this zoom level
    n_tiles = 2 ** (tile_level - zoom_level)
    # Size of a level target_zoom tile in this zoom level
    pixels_per_tile = 256 // (2 ** (tile_level - zoom_level))
    covered_tile = Image.new(
        "RGBA", (pixels_per_tile, pixels_per_tile), (0, 0, 255, 80)
    )
    covered_max_square = Image.new(
        "RGBA", (pixels_per_tile, pixels_per_tile), (255, 0, 0, 80)
    )

    for i in range(n_tiles * n_tiles):
        if (idx & (1 << i)) != 0:
            t = covered_max_square if (max_square_idx & (1 << i)) != 0 else covered_tile

            x = i % n_tiles
            y = i // n_tiles
            image.paste(t, (x * pixels_per_tile, y * pixels_per_tile))
    return image


def _load_cache(cache_dir: str) -> Dict[str, Dict[Tuple[int, int, int], int]]:
    """Load the cache files from the cache directory.

    Args:
        cache_dir: The directory containing the cache files.

    Return:
        A dict mapping user ids to a cache.
    """
    cache: Dict[str, Dict[Tuple[int, int, int], int]] = {}
    for file_name in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, file_name)
        with open(file_path, "rb") as f:
            user_cache: Dict[Tuple[int, int, int], int] = pickle.load(f)
            user_id = file_name.split(".")[0]
            cache[user_id] = user_cache

    return cache


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cache_dir",
        help="Directory containg the cache files.",
        default="data/cache",
    )
    args = parser.parse_args()

    cache = _load_cache(args.cache_dir)
    app.cache = cache

    for user_id in cache.keys():
        print(user_id + "/{z}/{x}/{y}.png")

    app.run()


if __name__ == "__main__":
    main()
