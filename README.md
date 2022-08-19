# coco-format-cv

Sample project to convert annotation results to COCO format and load the dataset to FiftyOne app.

# Setup
pip install --upgrade pip setuptools wheel
pip install fiftyone

More information: https://voxel51.com/docs/fiftyone/getting_started/install.html

# How to run
## coco-parser
- Require annotation record results in input folder and related images in image folder
- Run convert_to_coco.py to generate COCO format in output folder

## Sample dataset on FiftyOne
- Copy generated COCO format to root folder of sample_dataset and rename it to labels.json
- The related images must be in data folder
- Run load_dataset.py to launch FiftyOne app with the sample dataset