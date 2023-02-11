"""Download geojson files."""

import os
import argparse
import json
from typing import List

import requests

from kachel.cache import create_cache_file


def retrieve_user_ids(endpoint: str) -> List[str]:
    url = endpoint + "/users"
    response = requests.get(url)
    users = response.json()
    return [user["id"] for user in users]


def retrieve_geojson(endpoint: str, user_id: str) -> dict:
    url = f"{endpoint}/{user_id}/geojson"
    response = requests.get(url)
    return response.json()


def main(endpoint: str) -> None:
    user_ids = retrieve_user_ids(endpoint)

    for user_id in user_ids:
        print(f"Working on user {user_id}")

        print("Retrieve geojson")
        geojson = retrieve_geojson(endpoint, user_id)
        os.makedirs("data/geojson", exist_ok=True)
        with open(f"data/geojson/{user_id}.geojson", "w") as f:
            json.dump(geojson, f)

        print("Build cache file")
        os.makedirs("data/cache", exist_ok=True)
        create_cache_file(
            f"data/geojson/{user_id}.geojson", f"data/cache/{user_id}.pkl"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", help="The endpoint to download geojson from.")
    args = parser.parse_args()

    main(args.endpoint)
