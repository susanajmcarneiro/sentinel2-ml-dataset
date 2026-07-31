from pathlib import Path
import numpy as np


class NumpyDatasetFormat:

    def __init__(self, images_directory, masks_directory):
        self.images_directory = Path(images_directory)
        self.masks_directory = Path(masks_directory)

        self.images_directory.mkdir(parents=True, exist_ok=True)
        self.masks_directory.mkdir(parents=True, exist_ok=True)

    def save_image(self, tile, filename):
        output_path = self.images_directory / filename
        np.save(output_path,np.ascontiguousarray(tile),allow_pickle=False)

    def save_mask(self, tile, filename):
        output_path = self.masks_directory / filename
        np.save(output_path,np.ascontiguousarray(tile),allow_pickle=False)

    def load_image(self, filename, bands=None):
        image = np.load(self.images_directory/filename,mmap_mode="r",allow_pickle=False)

        if bands is None:
            return image

        return image[..., bands]

    def load_mask(self, filename):
        return np.load(self.masks_directory / filename,mmap_mode="r",allow_pickle=False)