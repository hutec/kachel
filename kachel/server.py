"""The actual tile server."""

import argparse
import io
import os
import pickle
from typing import Dict, Tuple

from flask import Flask, Response

from kachel.utils import generate_tile

app = Flask(__name__)


@app.route("/<string:user_id>/<int:z>/<int:x>/<int:y>.png")
def tile(user_id: str, z: int, x: int, y: int) -> Response:
    """serve a tile.

    Args:
        user_id: The user id.
        z: the zoom level, higher is closer.
        x: the x coordinate.
        y: the y coordinate.

    Returns:
        a 256x256 png image
    """

    if user_id not in app.cache:
        return Response(
            f"User id {user_id} not found",
            status=404,
        )

    tile_idx = 0
    max_square_idx = 0
    if (x, y, z) in app.cache[user_id]:
        tile_idx = app.cache[user_id][(x, y, z)]["tiles"]
        max_square_idx = app.cache[user_id][(x, y, z)]["max_square"]

    tile = generate_tile(tile_idx, max_square_idx, z)

    img_byte_arr = io.BytesIO()
    tile.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    return Response(
        img_byte_arr,
        mimetype="image/png",
    )


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
