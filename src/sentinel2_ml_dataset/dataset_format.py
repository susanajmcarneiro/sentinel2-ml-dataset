from pathlib import Path
import numpy as np


class NumpyDatasetFormat:

    def __init__(self, images_directory, masks_directory):
        self.images_directory = Path(images_directory)
        self.masks_directory = Path(masks_directory)

        self.images_directory.mkdir(parents=True, exist_ok=True)
        self.masks_directory.mkdir(parents=True, exist_ok=True)


    def save_image(self, tile, filename):
        tile = tile.astype(np.uint16)

        output_path = self.images_directory / filename
        np.save(output_path, tile)

    def save_mask(self, tile, filename):
        tile = tile.astype(np.uint8)

        output_path = self.masks_directory / filename
        np.save(output_path, tile)