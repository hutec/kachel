from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Set, Tuple

from mercantile import Tile
from PIL import Image


def generate_tile(idx: int, max_square_idx: int, zoom_level: int) -> Image:
    """Generate a tile image.

    Args:
        idx: bitmask indicating which tiles are covered.
        max_square_idx: bitmask indicating which tiles are part of a max square.
        zoom_level: the zoom level of the tile.
        max_square: Whether to highlight the maximum square.

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
    covered_tile = Image.new(
        "RGBA", (pixels_per_tile, pixels_per_tile), (0, 0, 255, 80)
    )
    covered_max_square = Image.new(
        "RGBA", (pixels_per_tile, pixels_per_tile), (255, 0, 0, 80)
    )

    for i in range(n_tiles * n_tiles):
        if (idx & (1 << i)) != 0:
            t = covered_max_square if (max_square_idx & (1 << i)) != 0 else covered_tile

            x = i % n_tiles
            y = i // n_tiles
            image.paste(t, (x * pixels_per_tile, y * pixels_per_tile))
    return image


@dataclass
class MaxSquare:
    top_left: Tuple[int, int]
    size: int

    @property
    def bottom_right(self) -> Tuple[int, int]:
        return (self.top_left[0] + self.size, self.top_left[1] + self.size)


def compute_max_squares(tiles: Set[Tile]) -> List[MaxSquare]:
    """Compute max squares that contains covered tiles.

    Args:
        tiles: Set of visited tiles.

    Return:
        List of max squares each consisting of a top left coordinate and a size.
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

    max_square_size = max(known_squares.values())
    max_squares = []
    for (x, y), square_size in known_squares.items():
        if square_size == max_square_size:
            max_squares.append(MaxSquare((x, y), square_size))
    return max_squares
