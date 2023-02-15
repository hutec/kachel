"""Compute a cache file given a geojson file.

A cache file is a dict mapping (x, y, z) to a boolean indicating whether
the tile in zoom level 14 is covered by the geojson file.
"""

import argparse
import json
import math
import os
import pickle
from collections import defaultdict
from typing import List

import requests
from mercantile import Tile, parent
from mercantile import tile as tile_from_coordinates

from kachel.utils import MaxSquare, compute_max_square


def main():
    parser = argparse.ArgumentParser()
    # Add two subparsers for the two different modes
    # One for just converting geojson to cache file
    # One for downloading geojson files and converting them to cache files

    subparsers = parser.add_subparsers(dest="mode")
    subparsers.required = True
    convert_parser = subparsers.add_parser(
        "convert", description="Convert geojson to cache file"
    )
    download_parser = subparsers.add_parser(
        "download", description="Download geojson files and convert them to cache files"
    )

    convert_parser.add_argument("geojson", help="Source GeoJSON file or directory")
    convert_parser.add_argument("cache", help="Target cache file or directory")

    download_parser.add_argument(
        "endpoint", help="The endpoint to download geojson from."
    )
    args = parser.parse_args()

    if args.mode == "download":
        user_ids = retrieve_user_ids(args.endpoint)

        for user_id in user_ids:
            print(f"Working on user {user_id}")

            print("Retrieve geojson")
            geojson = retrieve_geojson(args.endpoint, user_id)
            os.makedirs("data/geojson", exist_ok=True)
            with open(f"data/geojson/{user_id}.geojson", "w") as f:
                json.dump(geojson, f)

            print("Build cache file")
            os.makedirs("data/cache", exist_ok=True)
            create_cache_file(
                f"data/geojson/{user_id}.geojson", f"data/cache/{user_id}.pkl"
            )
    elif args.mode == "convert":
        if os.path.isdir(args.geojson):
            for filename in os.listdir(args.geojson):
                if not filename.endswith(".geojson"):
                    continue
                geojson_file = os.path.join(args.geojson, filename)
                cache_file = os.path.join(
                    args.cache, filename.replace(".geojson", ".pkl")
                )
                create_cache_file(geojson_file, cache_file)
        else:
            create_cache_file(args.geojson, args.cache)


def create_cache_file(geojson_file: str, cache_file: str) -> None:
    """Generate a cache file from a geojson file."""
    with open(geojson_file) as f:
        geojson = json.load(f)

    routes = geojson["features"]
    cache = defaultdict(lambda: defaultdict(int))
    processed_tiles = set()
    for route in routes:
        coordinates = route["geometry"]["coordinates"]
        # TODO: Properly handle interpolation between tiles
        #  For now, we assume the coordinates are close enough
        for lng, lat in coordinates:
            tile: Tile = tile_from_coordinates(lng, lat, 14)
            processed_tiles.add(tile)

    max_squares = compute_max_square(processed_tiles)

    for tile in processed_tiles:
        _is_max_square = is_in_max_squares(tile, max_squares)

        for zoom in range(8, 15):
            if zoom == 14:
                cache[(tile.x, tile.y, zoom)]["tiles"] = 1
                if _is_max_square:
                    cache[(tile.x, tile.y, zoom)]["max_square"] = 1
                continue

            parent_tile: Tile = parent(tile, zoom=zoom)

            # Number of level 14 tiles in this zoom level
            n_tiles = int(math.pow(2, 14 - zoom))
            # Compute the top left level 14 tile in the parent tile, that's index 0
            top_left_tile = Tile(parent_tile.x * n_tiles, parent_tile.y * n_tiles, 14)

            # Compute the index of the level 14 tile in the parent tile
            idx = (tile.y - top_left_tile.y) * n_tiles + (tile.x - top_left_tile.x)
            cache[(parent_tile.x, parent_tile.y, zoom)]["tiles"] |= 1 << idx
            if _is_max_square:
                cache[(parent_tile.x, parent_tile.y, zoom)]["max_square"] |= 1 << idx

    with open(cache_file, "wb") as f:
        pickle.dump(dict(cache), f)


def is_in_max_square(tile: Tile, max_square: MaxSquare) -> bool:
    """Check if a tile is in the max square."""
    _x = max_square.top_left[0] <= tile.x < max_square.bottom_right[0]
    _y = max_square.top_left[1] <= tile.y < max_square.bottom_right[1]
    return _x and _y


def is_in_max_squares(tile: Tile, max_squares: List[MaxSquare]) -> bool:
    """Check if a tile is in any of the max squares."""
    for max_square in max_squares:
        if is_in_max_square(tile, max_square):
            return True
    return False


def retrieve_user_ids(endpoint: str) -> List[str]:
    url = endpoint + "/users"
    response = requests.get(url)
    users = response.json()
    return [user["id"] for user in users]


def retrieve_geojson(endpoint: str, user_id: str) -> dict:
    url = f"{endpoint}/{user_id}/geojson"
    response = requests.get(url)
    return response.json()


if __name__ == "__main__":
    main()
