from pathlib import Path
import numpy as np
import pandas as pd
import shutil

from padding import pad_to_tile_size
from tiling import split_into_tiles
from dataset_format import NumpyDatasetFormat
from metadata import (MetadataCreator, load_sentinel2_band_information)
from mask_processing import (one_hot_to_class_ids,calculate_cloud_coverage)


def process_subscene(image_path, mask_path, product_id, dataset_format, metadata_creator):
    image = np.load(image_path)
    mask = np.load(mask_path)

    if image.ndim != 3:
        raise ValueError(
            f"Expected image shape (height, width, bands), got {image.shape}"
        )

    if mask.ndim != 3:
        raise ValueError(
            f"Expected mask shape (height, width, classes), got {mask.shape}"
        )

    if image.shape[:2] != mask.shape[:2]:
        raise ValueError(
            f"Image and mask spatial dimensions do not match: "
            f"{image.shape[:2]} and {mask.shape[:2]}"
        )

    # Convert (H, W, 3) one-hot mask into (H, W) class IDs
    mask = one_hot_to_class_ids(mask)

    original_pixel_mask = np.ones(mask.shape, dtype=bool)

    padded_image = pad_to_tile_size(image)
    padded_mask = pad_to_tile_size(mask)
    padded_original_pixel_mask = pad_to_tile_size(original_pixel_mask) # Padded pixels: False

    # Convert once before splitting into tiles
    padded_image = np.rint(padded_image * 10_000)
    padded_image = np.clip(padded_image,0,np.iinfo(np.uint16).max).astype(np.uint16)
    padded_mask = padded_mask.astype(np.uint8)

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


def prepare_output_directory(output_directory):
    """
    Check whether the output directory already contains files.
    If it does, ask the user whether the existing output should be deleted.
    """

    output_directory = Path(output_directory)

    if not output_directory.exists():
        output_directory.mkdir(parents=True)
        return

    # Check whether the directory contains any files or folders.
    if not any(output_directory.iterdir()):
        return

    while True:
        answer = input("\nOverwrite existing output? [y/N]: ").strip().lower()

        if answer in {"y", "yes"}:
            shutil.rmtree(output_directory)
            output_directory.mkdir(parents=True)
            return

        if answer in {"", "n", "no"}:
            print("Processing cancelled.")
            raise SystemExit

        print("Please answer 'y' or 'n'.")

def main():
    project_directory = Path(__file__).resolve().parents[2]

    dataset_directory = project_directory / "DATASET"
    output_directory = project_directory / "output"
    excel_path = (
        Path(__file__).resolve().parent
        / "resources"
        / "sentinel2_spectral_response_functions.xlsx"
    )
    prepare_output_directory(output_directory)
    
    classification_table = pd.read_csv(dataset_directory / "classification_tags.csv")

    available_images = {path.stem for path in (dataset_directory / "subscenes").glob("*.npy")}
    available_masks = {path.stem for path in (dataset_directory / "masks").glob("*.npy")}
    available_scenes = available_images & available_masks

    classification_table = classification_table[classification_table["scene"].isin(available_scenes)]

    dataset_format = NumpyDatasetFormat(
        images_directory=output_directory / "images",
        masks_directory=output_directory / "masks",
    )

    metadata_creator = MetadataCreator(
        output_directory=output_directory / "metadata",
    )

    band_information = load_sentinel2_band_information(excel_path)

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
    metadata_creator.save_dataset_metadata(
        class_mapping={
            "CLEAR": 0,
            "CLOUD": 1,
            "CLOUD_SHADOW": 2,
        },
        band_information=band_information,
        spatial_resolution_m=20,
    )

if __name__ == "__main__":
    main()