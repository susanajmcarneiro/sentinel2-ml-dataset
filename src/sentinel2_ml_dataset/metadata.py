from pathlib import Path
import csv
import json
import pandas as pd


def load_sentinel2_band_information(excel_path):
    """
    Load Sentinel-2 band metadata from the ESA spectral response functions.
    """

    excel_path = Path(excel_path)

    band_table = pd.read_excel(
        excel_path,
        sheet_name="Overview",
        usecols="A:E",
        skiprows=10,
        nrows=13,
        header=None,
        names=[
            "band_prefix",
            "band_suffix",
            "center_wavelength_nm",
            "bandwidth_nm",
            "native_gsd_m",
        ],
        engine="openpyxl",
    )

    band_suffix = (
        band_table["band_suffix"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )

    band_table["band_name"] = (
        band_table["band_prefix"].astype(str).str.strip()
        + band_suffix
    ).str.upper()

    band_table.insert(
        0,
        "band_id",
        range(len(band_table)),
    )

    columns_to_keep = [
        "band_id",
        "band_name",
        "center_wavelength_nm",
        "bandwidth_nm",
        "native_gsd_m",
    ]

    return band_table[columns_to_keep].to_dict(orient="records")


class MetadataCreator:

    def __init__(self, output_directory):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

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

    def save_dataset_metadata(
        self,
        class_mapping,
        band_information,
        processed_gsd_m,
        filename="dataset.json",
    ):
        metadata = {
            "processed_gsd_m": processed_gsd_m,
            "class_mapping": class_mapping,
            "bands": band_information,
        }

        output_path = self.output_directory / filename

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)