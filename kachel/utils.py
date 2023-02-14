from itertools import product
from typing import Dict, Set, Tuple

from mercantile import Tile
from PIL import Image


def generate_tile(idx: int, zoom_level: int) -> Image:
    """Generate a tile image.

    Args:
        idx: bitmask indicating which tiles are covered.
        zoom_level: the zoom level of the tile.

    Returns:
        A 256x256 PNG image.
    """
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))

    if zoom_level > 14:
        return image

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


def compute_max_square(tiles: Set[Tile]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Compute the maximum square that contains covered tiles.

    Args:
        tiles: Set of visited tiles.

    Return:
        The top left and bottom right coordinates of the square.
    """

    coordinates = set((tile.x, tile.y) for tile in tiles)

    known_squares: Dict[Tuple[int, int], int] = {}

    def _check_square(x: int, y: int, square_size: int) -> bool:
        """Check if a square of size `square_size` starting at (x, y) is covered."""
        for dx, dy in product(range(square_size), repeat=2):
            if (x + dx, y + dy) not in coordinates:
                return False
        return True

    for x, y in coordinates:
        square_size = 1
        while _check_square(x, y, square_size + 1):
            square_size += 1
        known_squares[(x, y)] = square_size

    return max(known_squares.values())
    # return max(known_squares, key=known_squares.get)
