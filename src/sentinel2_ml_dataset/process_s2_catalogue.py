from pathlib import Path
import numpy as np
import pandas as pd

from padding import pad_to_tile_size
from tiling import split_into_tiles
from dataset_format import NumpyDatasetFormat
from metadata import MetadataCreator
from mask_processing import (one_hot_to_class_ids,calculate_cloud_coverage)


def process_subscene(image_path, mask_path, product_id, dataset_format, metadata_creator):
    image = np.load(image_path)
    mask = np.load(mask_path)

    # Convert (H, W, 3) one-hot mask into (H, W) class IDs
    mask = one_hot_to_class_ids(mask)

    original_pixel_mask = np.ones(mask.shape, dtype=bool)

    padded_image = pad_to_tile_size(image)
    padded_mask = pad_to_tile_size(mask)
    padded_original_pixel_mask = pad_to_tile_size(original_pixel_mask) # Padded pixels: False

    image_tiles = split_into_tiles(padded_image)
    mask_tiles = split_into_tiles(padded_mask)
    original_pixel_tiles = split_into_tiles(padded_original_pixel_mask)

    for image_data, mask_data, original_pixel_data in zip(image_tiles, mask_tiles, original_pixel_tiles):

        image_tile, row_start, col_start = image_data
        mask_tile, mask_row_start, mask_col_start = mask_data
        original_pixel_tile, _, _ = original_pixel_data

        tile_id = f"{product_id}_r{row_start}_c{col_start}"
        filename = f"{tile_id}.npy"

        cloud_coverage = calculate_cloud_coverage(mask_tile, original_pixel_tile)

        dataset_format.save_image(image_tile, filename)
        dataset_format.save_mask(mask_tile, filename)

        metadata_creator.add_tile_record(
            tile_id=tile_id,
            image_filename=filename,
            mask_filename=filename,
            product_id=product_id,
            row_start=row_start,
            column_start=col_start,
            cloud_coverage=cloud_coverage,
        )


def main():
    dataset_directory = Path("path/to/DATASET")
    output_directory = Path("path/to/output")

    classification_table = pd.read_csv(dataset_directory / "classification_tags.csv",index_col="index")

    dataset_format = NumpyDatasetFormat(
        images_directory=output_directory / "images",
        masks_directory=output_directory / "masks",
    )

    metadata_creator = MetadataCreator(
        output_directory=output_directory / "metadata",
    )

    for _, row in classification_table.iterrows():

        product_id = row["scene"]

        image_path = (dataset_directory/"subscenes"/f"{product_id}.npy")
        mask_path = (dataset_directory/"masks"/f"{product_id}.npy")

        if not image_path.exists():
            raise FileNotFoundError(
                f"Subscene not found: {image_path}"
            )

        if not mask_path.exists():
            raise FileNotFoundError(
                f"Mask not found: {mask_path}"
            )

        process_subscene(
            image_path=image_path,
            mask_path=mask_path,
            product_id=product_id,
            dataset_format=dataset_format,
            metadata_creator=metadata_creator,
        )

    metadata_creator.save_tile_metadata()


if __name__ == "__main__":
    main()