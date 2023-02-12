"""Compute a cache file given a geojson file.

A cache file is a dict mapping (x, y, z) to a boolean indicating whether
the tile in zoom level 14 is covered by the geojson file.
"""

import argparse
import json
import os
import pickle
from collections import defaultdict
from typing import List

import requests

from kachel.utils import deg2num, get_parent_tile


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
    visited = set()
    for route in routes:
        coordinates = route["geometry"]["coordinates"]
        # TODO: Properly handle interpolation between tiles
        #  For now, we assume the coordinates are close enough
        for lng, lat in coordinates:
            zoom = 14
            x, y = deg2num(lat, lng, zoom)
            visited.add((x, y, zoom))

    cache = defaultdict(int)
    for zoom in range(14, 8, -1):
        for x, y, z in visited:
            parent_x, parent_y = get_parent_tile(x, y, zoom)

            n_tiles = 2 ** (14 - zoom)  # Number of level 14 tiles in this zoom level
            # The x and y coordinates of the parent tile in level 14
            parent_x_l14 = parent_x * n_tiles
            parent_y_l14 = parent_y * n_tiles

            idx = (y - parent_y_l14) * n_tiles + (x - parent_x_l14)
            cache[(parent_x, parent_y, zoom)] |= 1 << idx

    with open(cache_file, "wb") as f:
        pickle.dump(cache, f)


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
