from pathlib import Path
import csv
import json


class MetadataCreator:

    def __init__(self, output_directory):
        """
        Create a metadata manager.

        Parameters
        ----------
        output_directory : str or Path
            Directory where the metadata files will be saved.
        """

        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Each entry will represent one image-mask tile pair.
        self.tile_records = []

    def add_tile_record(
        self,
        tile_id,
        image_filename,
        mask_filename,
        product_id,
        row_start,
        column_start,
        cloud_coverage,
    ):
        """
        Add the metadata associated with one tile.
        """

        record = {
            "tile_id": tile_id,
            "image_filename": image_filename,
            "mask_filename": mask_filename,
            "product_id": product_id,
            "row_start": row_start,
            "column_start": column_start,
            "cloud_coverage_percent": cloud_coverage,
        }

        self.tile_records.append(record)

    def save_tile_metadata(self, filename="tiles.csv"):
        """
        Save all tile-level metadata as a CSV file.
        """

        output_path = self.output_directory / filename

        fieldnames = [
            "tile_id",
            "image_filename",
            "mask_filename",
            "product_id",
            "row_start",
            "column_start",
            "cloud_coverage_percent",
        ]

        with output_path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self.tile_records)

    def save_dataset_metadata(self,class_mapping,band_information,filename="dataset.json"):
        """
        Save dataset-level metadata as a JSON file.
        """

        metadata = {
            "class_mapping": class_mapping,
            "bands": band_information,
        }

        output_path = self.output_directory / filename

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)