import math
from typing import Tuple

LatLong = Tuple[float, float]


def num2deg(xtile: int, ytile: int, zoom: int) -> LatLong:
    """Converts tile coordinates to latitude and longitude.

    Taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python

    Args:
        xtile: The x coordinate of the tile.
        ytile: The y coordinate of the tile.
        zoom: The zoom level of the tile.

    Returns:
        A tuple of latitude and longitude.
    """
    n = 2.0**zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    """Converts latitude and longitude to tile coordinates.

    Taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python

    Args:
        lat_deg: The latitude in degrees.
        lon_deg: The longitude in degrees.
        zoom: The zoom level of the tile.

    Returns:
        A tuple of x and y coordinates.
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0**zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)
