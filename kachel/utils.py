import math
from typing import Tuple
from Pillow import Image

LatLng = Tuple[float, float]


def num2deg(xtile: int, ytile: int, zoom: int) -> LatLng:
    """Converts tile coordinates to latitude and longitude.

    Taken from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python

    Args:
        xtile: The x coordinate of the tile.
        ytile: The y coordinate of the tile.
        zoom: The zoom level of the tile.

    Returns:
        A tuple of latitude and longitude marking the NW corner of the tile.
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


def get_parent_tile(x: int, y: int, z: int) -> Tuple[int, int]:
    """Get the parent tile of a given zoom 14 tile.

    Args:
        x: The x coordinate of the tile at zoom 14.
        y: The y coordinate of the tile at zoom 14.
        z: The zoom level of the parent tile.
            Must be smaller than 14.

    Returns:
        The x and y coordinates of the parent tile at given zoom.
    """
    # Get the NW corner of the tile at zoom 14
    latlng = num2deg(x, y, 14)

    # Convert the NW corner to the parent zoom level
    return deg2num(*latlng, z)


def generate_tile(idx: int, zoom_level: int) -> Image:
    """Generate a tile image.

    Args:
        idx: bitmask indicating which tiles are covered.
        zoom_level: the zoom level of the tile.

    Returns:
        A 256x256 PNG image.
    """
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))

    # Number of level 14 tiles in this zoom level
    n_tiles = 2 ** (14 - zoom_level)
    # Size of a level 14 tile in this zoom level
    pixels_per_tile = 256 // (2 ** (14 - zoom_level))
    covered = Image.new("RGBA", (pixels_per_tile, pixels_per_tile), (0, 0, 255, 80))

    for i in range(n_tiles * n_tiles):
        if (idx & (1 << i)) != 0:
            x = i % n_tiles
            y = i // n_tiles
            image.paste(
                covered,
                (x * pixels_per_tile, y * pixels_per_tile),
            )
    return image
