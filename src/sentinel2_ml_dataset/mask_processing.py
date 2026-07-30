import numpy as np


def one_hot_to_class_ids(mask):
    """Convert a one-hot mask from (height, width, classes) to (height, width)"""

    return np.argmax(mask, axis=-1)

def calculate_cloud_coverage(mask_tile, original_pixel_tile):

    # Not counting padded pixels for the cloud coverage calculation: class 1 (CLOUD)
    cloud_pixels = np.sum((mask_tile == 1) & original_pixel_tile)
    total_valid_pixels = np.sum(original_pixel_tile)

    return cloud_pixels / total_valid_pixels * 100