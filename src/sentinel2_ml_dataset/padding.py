import numpy as np


def pad_to_tile_size(array, tile_size=512):
    """Pad the first two dimensions with zeros until divisible by tile_size"""

    height, width = array.shape[:2]

    pad_height = (-height) % tile_size
    pad_width = (-width) % tile_size

    padding = [
        (0, pad_height),
        (0, pad_width),
    ]

    # Padding just the first two dimensions
    padding.extend([(0, 0)] * (array.ndim - 2))

    return np.pad(array, padding, mode="constant", constant_values=0)