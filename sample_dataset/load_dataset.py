from logging import error
import fiftyone as fo

DATASET_NAME = "ys-sample"
DATASET_DIR = "./"

def clean_existing_dataset():
  datasets = fo.list_datasets()
  for d in datasets:
    if (d == DATASET_NAME):
      fo.delete_dataset(d)
      print("'"+ d + "' dataset has been deleted")

def load_dataset():
  try :
    dataset = fo.Dataset.from_dir(
      dataset_dir = DATASET_DIR,
      dataset_type= fo.types.COCODetectionDataset,
      label_types=["detections", "segmentations"],
      name = DATASET_NAME
    )
    print(dataset.head())
    session = fo.launch_app(dataset)
    session.wait()
  except Exception as e:
    error(e)

if __name__ == "__main__":
  clean_existing_dataset()
  load_dataset()