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
