# Sentinel-2 ML Dataset Builder

This project converts the Sentinel-2 Cloud Mask Catalogue into a tiled dataset suitable for machine-learning applications.

The original Sentinel-2 subscenes and cloud masks are padded, divided into `512 × 512` tiles, converted to appropriate data types, and saved together with tile-level and dataset-level metadata.

## Features

The processing pipeline:

- reads Sentinel-2 subscenes and their corresponding cloud masks;
- converts one-hot encoded masks into class-ID masks;
- pads arrays so their dimensions are divisible by 512;
- divides images and masks into `512 × 512` tiles;
- saves image tiles as `uint16`;
- saves mask tiles as `uint8`;
- calculates cloud coverage while excluding padded pixels;
- creates tile-level metadata in CSV format;
- creates dataset-level metadata in JSON format;
- supports loading selected Sentinel-2 bands.

## Project Structure

After downloading and extracting the project ZIP file, the folder structure should be:

```text
sentinel2-ml-dataset/
├── DATASET/
│   ├── classification_tags.csv
│   ├── subscenes/
│   │   └── <scene_id>.npy
│   └── masks/
│       └── <scene_id>.npy
├── output/
├── pyproject.toml
├── README.md
└── src/
    └── sentinel2_ml_dataset/
        ├── __init__.py
        ├── dataset_format.py
        ├── mask_processing.py
        ├── metadata.py
        ├── padding.py
        ├── process_s2_catalogue.py
        ├── tiling.py
        └── resources/
            └── sentinel2_spectral_response_functions.xlsx
```

The `output` directory may initially be empty. The required subdirectories are created automatically when the processing script runs.

## Input data

### Sentinel-2 images

Each input image is stored as a NumPy array with shape:

```text
(height, width, number_of_bands)
```

The supplied catalogue contains 13 Sentinel-2 bands in the following order:

```text
B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B10, B11, B12
```

The image values are reflectances obtained by dividing the original Sentinel-2 L1C integer values by `10,000`.

Some reflectance values may be greater than 1.

### Cloud masks

Each input mask is a boolean one-hot encoded NumPy array with shape:

```text
(height, width, number_of_classes)
```

The mask classes are:

```text
CLEAR
CLOUD
CLOUD_SHADOW
```

During processing, the one-hot encoded mask is converted into a two-dimensional class-ID mask:

```text
0 = CLEAR
1 = CLOUD
2 = CLOUD_SHADOW
```

## Architecture

The project is divided into small modules so that individual parts of the processing pipeline can be reused or replaced.

### `padding.py`

Pads the bottom and right sides of an array until its spatial dimensions are divisible by the requested tile size.

### `tiling.py`

Divides padded arrays into tiles and returns the row and column coordinates of each tile.

### `mask_processing.py`

Contains functions for:

- converting one-hot encoded masks to class IDs;
- calculating cloud coverage;
- excluding padded pixels from cloud-coverage calculations.

### `dataset_format.py`

Defines the `NumpyDatasetFormat` class.

This class is responsible for:

- saving image tiles;
- saving mask tiles;
- loading image tiles;
- loading selected image bands;
- loading mask tiles.

### `metadata.py`

Contains:

- the `MetadataCreator` class;
- the function used to read official Sentinel-2 band information.

Tile metadata are saved as CSV, while dataset metadata are saved as JSON.

### `process_s2_catalogue.py`

Runs the complete processing pipeline for every scene listed in `classification_tags.csv`.

## Installation

Python 3.10 or newer is recommended.

Open a terminal in the main project directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the project and its dependencies:

```bash
pip install -e .
```

The dependencies are:

- NumPy;
- pandas;
- openpyxl.

## Running the processing pipeline

The paths used by the script are based on the fixed project structure shown above.

From the main project directory, run:

```bash
python src/sentinel2_ml_dataset/process_s2_catalogue.py
```

The script reads the input data from:

```text
DATASET/
```

and writes the processed dataset to:

```text
output/
```

## Demonstration notebook

The repository includes a Jupyter notebook demonstrating the complete preprocessing workflow:

```text
notebooks/cloudsen12_preprocessing_walkthrough.ipynb
```

The notebook walks through the main processing steps using a Sentinel-2 subscene, including:

- inspecting the original image and cloud mask;
- converting one-hot masks to class IDs;
- padding images and masks;
- splitting arrays into `512 × 512` tiles;
- calculating cloud coverage;
- inspecting the processed image and mask tiles;
- loading processed tiles with the `NumpyDatasetFormat` class;
- exploring the generated metadata.

The notebook is intended as an interactive demonstration of the implemented pipeline and is not required to run the processing script.

## Output structure

After processing, the output directory will contain:

```text
output/
├── images/
│   └── <tile_id>.npy
├── masks/
│   └── <tile_id>.npy
└── metadata/
    ├── tiles.csv
    └── dataset.json
```

Each image tile and its corresponding mask use the same filename.

A tile filename contains:

- the original Sentinel-2 product ID;
- the starting row of the tile;
- the starting column of the tile.

For example:

```text
<product_id>_r0_c512.npy
```

## Image tiles

The output image tiles have shape:

```text
(512, 512, number_of_bands)
```

They are saved as:

```text
uint16
```

Before saving, the reflectance values are multiplied by `10,000` and rounded.

Reflectance values can be recovered using:

```python
reflectance = image.astype(float) / 10_000
```

## Mask tiles

The output mask tiles have shape:

```text
(512, 512)
```

They are saved as:

```text
uint8
```

The class mapping is:

```text
0 = CLEAR
1 = CLOUD
2 = CLOUD_SHADOW
```

## Padding

Padding is added only to the bottom and right sides of each array.

For example, an input array with shape:

```text
(1022, 1022)
```

is padded to:

```text
(1024, 1024)
```

The padded array can then be divided into four `512 × 512` tiles.

Padded pixels are excluded from cloud-coverage calculations.

## Tile metadata

The file:

```text
output/metadata/tiles.csv
```

contains one row for each generated tile.

The stored fields include:

- tile ID;
- image filename;
- mask filename;
- original product ID;
- starting row;
- starting column;
- cloud coverage percentage.

## Dataset metadata

The file:

```text
output/metadata/dataset.json
```

contains information that applies to the complete dataset, including:

- the cloud-mask class mapping;
- the processed ground sampling distance (GSD);
- Sentinel-2 band IDs;
- Sentinel-2 band names;
- centre wavelengths;
- bandwidths;
- the native GSD of each band.

## Loading the processed dataset

The `NumpyDatasetFormat` class can be used to load processed tiles.

```python
from sentinel2_ml_dataset.dataset_format import NumpyDatasetFormat

dataset = NumpyDatasetFormat(
    images_directory="output/images",
    masks_directory="output/masks",
)
```

Load all bands from an image tile:

```python
image = dataset.load_image("tile_filename.npy")
```

Load the corresponding mask:

```python
mask = dataset.load_mask("tile_filename.npy")
```

Load only selected bands:

```python
selected_bands = dataset.load_image(
    "tile_filename.npy",
    bands=[3, 2, 1],
)
```

The example above loads:

```text
B4, B3, B2
```

which correspond to the red, green, and blue bands.

Band positions use zero-based Python indexing:

```text
0  = B1
1  = B2
2  = B3
3  = B4
4  = B5
5  = B6
6  = B7
7  = B8
8  = B8A
9  = B9
10 = B10
11 = B11
12 = B12
```

## Sentinel-2 band metadata

Official Sentinel-2 band information is read from the Spectral Response Functions workbook stored at:

```text
src/sentinel2_ml_dataset/resources/sentinel2_spectral_response_functions.xlsx
```

The `Overview` sheet contains the following information for each band:

- band name;
- centre wavelength;
- spectral width;
- native ground sampling distance (GSD).

The catalogue images were resampled to a common spatial resolution of 20 metres. The original resolution of each Sentinel-2 band is also retained in the metadata.

## Notes

- Image and mask tiles always use identical filenames.
- Image and mask spatial dimensions are checked before processing.
- Reflectance values may be greater than 1.
- The number of image bands is not hard-coded by the processing functions.
- The mask conversion supports any number of one-hot encoded classes.
- Padding does not contribute to cloud-coverage percentages.
- Output directories are created automatically.

## References

Sentinel-2 band metadata are obtained from the official Copernicus Sentinel-2 Spectral Response Functions workbook:

```text
Sentinel-2 Spectral Response Functions
Document code: COPE-GSEG-EOPG-TN-15-0007
Version: 4.0