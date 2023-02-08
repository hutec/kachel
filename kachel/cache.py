"""Compute a cache file given a geojson file.

A cache file is a dict mapping (x, y, z) to a boolean indicating whether
the tile is covered by the geojson file.
"""

import argparse
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("geojson", help="GeoJSON file")
    parser.add_argument("cache", help="Cache file")
    args = parser.parse_args()

    with open(args.geojson) as f:
        geojson = json.load(f)
        print(geojson)


if __name__ == "__main__":
    main()
