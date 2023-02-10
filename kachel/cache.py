"""Compute a cache file given a geojson file.

A cache file is a dict mapping (x, y, z) to a boolean indicating whether
the tile in zoom level 14 is covered by the geojson file.
"""

from collections import defaultdict
import argparse
import json
import pickle

from kachel.utils import deg2num, get_parent_tile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("geojson", help="GeoJSON file")
    parser.add_argument("cache", help="Cache file")
    args = parser.parse_args()

    with open(args.geojson) as f:
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

    with open(args.cache, "wb") as f:
        pickle.dump(cache, f)


if __name__ == "__main__":
    main()
