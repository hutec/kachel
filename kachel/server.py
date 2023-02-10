"""The actual tile server."""

import argparse
import io
import pickle

from flask import Flask, Response

from kachel.utils import generate_tile

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

    idx = 0
    if (x, y, z) in app.cache:
        idx = app.cache[(x, y, z)]

    tile = generate_tile(idx, z)

    img_byte_arr = io.BytesIO()
    tile.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    return Response(
        img_byte_arr,
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


if __name__ == "__main__":
    main()
