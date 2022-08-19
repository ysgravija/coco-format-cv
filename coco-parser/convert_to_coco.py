import json
import os
from shapely.geometry import Polygon
from datetime import datetime
from PIL import Image

INPUT_FOLDER = os.path.join("./input")
OUTPUT_FOLDER = os.path.join("./output")
IMAGE_DIR = os.path.join("./image")

def check_directory_exists():
  if not os.path.exists(os.path.join(OUTPUT_FOLDER)):
    os.mkdir(os.path.join(OUTPUT_FOLDER))

#### COMPUTE ####
def calculate_bbox_and_area_for_bounding_box(coordinates):
  xmin = min(coord["x"] for coord in coordinates)
  xmax = max(coord["x"] for coord in coordinates)
  ymin = min(coord["y"] for coord in coordinates)
  ymax = max(coord["y"] for coord in coordinates)
  bbox = [xmin, ymin, xmax - xmin, ymax - ymin]
  area = bbox[2] * bbox[3]
  return bbox, area

def calculate_area_for_polygon(coordinates):
  polygon_coords =[]
  for coord in coordinates:
    seg_coord = [coord["x"], coord["y"]]
    polygon_coords.append(seg_coord)
  polygon_area = Polygon(polygon_coords)
  return polygon_area.area, polygon_coords

def convert_to_segmentation_coordinates(polygon_coordinates):
  segmentation = []
  for coord in polygon_coordinates:
    segmentation.append(coord[0])
    segmentation.append(coord[1])
  return segmentation

#### GENERATE COCO MANIFEST ####
def generate_coco_info():
  now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  info = {
      "year" : 2022,
      "version" : "1.0",
      "description" : "Sample COCO Export",
      "url" : "",
      "date_created" : now
  }
  return info

def get_coco_licenses():
  licenses = [
    {
      "id": 1,
      "name": "Open source",
      "url" : "",
    }
  ]
  return licenses

def get_coco_images(filename, image_id):
  filepath = os.path.join(IMAGE_DIR, filename)
  img = Image.open(filepath).convert("RGBA")
  width, height = img.size
  date = datetime.now().strftime("%Y-%m-%d")
  image = {
    "license": 1,
    "file_name": filename,
    "coco_url": "",
    "height": height,
    "width": width,
    "date_captured": date,
    "flickr_url": "",
    "id": image_id
  }
  return image

#### PARSE CATEGORY AND ANNOTATION ####  
def get_category_dictionary(entity_types):
  category_dict = dict()
  category_id = 1
  for entity in entity_types:
    name = entity["name"]
    category = {
      "id" : category_id,
      "name" : name,
      "supercategory": name
    }
    category_dict[name] = category
    category_id += 1
  return category_dict

def get_coco_annotations(annotations, category_dict, annotation_id, image_id, coco_annotations):
  for annotation in annotations:
    category_id = category_dict[annotation["entityTypeName"]]["id"]
    if (annotation["shapeType"] == 'bounding-box'):
      bbox, area = calculate_bbox_and_area_for_bounding_box(annotation["coordinates"])
      coco_annotation = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": bbox,
        "area": area,
        "iscrowd": 0,
        "classifications": annotation["classifications"]
      }
      coco_annotations.append(coco_annotation)
    elif (annotation["shapeType"] == 'polygon'):
      bbox, area = calculate_bbox_and_area_for_bounding_box(annotation["coordinates"])
      poly_area, polygon_coordinates = calculate_area_for_polygon(annotation["coordinates"])
      segmentation = convert_to_segmentation_coordinates(polygon_coordinates)
      coco_annotation = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": bbox,
        "area": poly_area,
        "segmentation": [segmentation],
        "iscrowd": 0,
        "classifications": annotation["classifications"]
      }
      coco_annotations.append(coco_annotation);
    elif (annotation["shapeType"] == 'none'):
      coco_annotation = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "bbox": [],
        "area": 0,
        "segmentation": [[]],
        "iscrowd": 0,
        "classifications": annotation["classifications"]
      }
      coco_annotations.append(coco_annotation)
    annotation_id += 1
    
  return coco_annotations, annotation_id

def main():
  check_directory_exists()
  print("Start looking for files:")
  input_files = [f for f in os.listdir(os.path.join(INPUT_FOLDER)) if f.endswith(".json")]
  images = []
  categories = []
  coco_annotations = []
  for input_file in input_files:
    print("Parsing " + input_file + " file.")
    image_id = 1
    annotation_id = 1

    filepath = os.path.join(INPUT_FOLDER, input_file)
    with open(filepath) as json_file:
      records = json.load(json_file)  
      for record in records:
        entity_types = record["resultData"]["boxes"]["manifest"]["entityTypes"]
        
        # category
        category_dict = get_category_dictionary(entity_types)
        categories = list(category_dict.values())
        
        # images
        image_header = get_coco_images(record["assetMetadata"]["name"], image_id)
        images.append(image_header)

        # annotations
        annotations = record["resultData"]["boxes"]["entities"]
        coco_annotations, annotation_id = get_coco_annotations(annotations, category_dict, annotation_id, image_id, coco_annotations)

        # increase counter
        image_id += 1 
        
  #### OUTPUT ####
  coco_format = {
        "info": generate_coco_info(),
        "licenses" : get_coco_licenses(),
        "images" : images,
        "categories" : categories,
        "annotations" : coco_annotations
  }

  date = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")
  output_filename = "labels-" + date + ".json"
  with open(os.path.join(OUTPUT_FOLDER, output_filename), "w") as outfile:
    json.dump(coco_format, outfile)
    print("COCO Export successful. Filename: " + output_filename)

  # print(json.dumps(coco_format, indent=2))

if __name__ == "__main__":
    main()