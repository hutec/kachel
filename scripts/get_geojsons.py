"""Download geojson files."""

import argparse
import json
from typing import List

import requests


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

        # Download geojson
        print("Retrieve geojson")
        geojson = retrieve_geojson(endpoint, user_id)

        # Write geojson to file
        with open(f"data/{user_id}.geojson", "w") as f:
            json.dump(geojson, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", help="The endpoint to download from.")
    args = parser.parse_args()

    main(args.endpoint)
