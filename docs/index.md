# Overview

This project contains a simple webserver that serves veloviewer explorer tiles.
Concretely, it provides an endpoint `/<string:user_id>/<int:z>/<int:x>/<int:y>.png`
that returns a transparent blue tile, if the tile has been covered and a transparent
red tile, if the tile is part of a max square.

## Quickstart

This assumes you have a geojson file, where the filename will later be used as user id.
For example, `12345.geojson` will later be server under `/12345/{z}/{x}/{y}.png`

1. `poetry install`
1. `poetry shell`
1. `mkdir -p data/cache`
1. `python kachel/cache.py convert 12345.geojson data/cache/12345.cache`
1. `python kachel/server.py`
