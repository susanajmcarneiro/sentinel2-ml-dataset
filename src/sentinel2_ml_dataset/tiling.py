def split_into_tiles(array, tile_size=512):
    """Split height and width into tiles of size tile_size"""

    tiles = []

    height, width = array.shape[:2]

    for row_start in range(0, height, tile_size):
        for col_start in range(0, width, tile_size):
            tile = array[
                row_start:row_start + tile_size,
                col_start:col_start + tile_size,
                ...
            ]
            tiles.append((tile, row_start, col_start))

    return tiles