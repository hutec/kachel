"""Compute a cache file given a geojson file.

A cache file is a dict mapping (x, y, z) to a boolean indicating whether
the tile is covered by the geojson file.
"""

import argparse
import json
import pickle

from kachel.utils import deg2num


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
        for (lng1, lat1), (lng2, lat2) in zip(coordinates, coordinates[1:]):
            for zoom in range(7, 15):
                x1, y1 = deg2num(lat1, lng1, zoom)
                x2, y2 = deg2num(lat2, lng2, zoom)

                visited.add((x1, y1, zoom))
                visited.add((x2, y2, zoom))
                # TODO: Add interpolation between tiles

    with open(args.cache, "wb") as f:
        pickle.dump(visited, f)


if __name__ == "__main__":
    main()
