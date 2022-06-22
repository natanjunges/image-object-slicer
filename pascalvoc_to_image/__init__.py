import argparse
import os
import xml.etree.ElementTree as ET
import time
from tqdm import tqdm
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description="Tool to cut objects from bounding boxes in PascalVOC XML files")
    parser.add_argument("pascal", help="A path to the directory with the PascalVOC XML files")
    parser.add_argument("images", help="A path to the directory with the input images")
    parser.add_argument("save", help="A path to the directory to save the object bounding box images to")
    args = parser.parse_args()
    pascal_files = get_pascal_files(args.pascal)
    parsed_pascal_files = parse_pascal_files(pascal_files, args.images)
    make_dir(args.save)
    create_label_dirs(parsed_pascal_files.get("labels"), args.save)
    pascalvoc_to_images(parsed_pascal_files.get("objects"), args.save)

def get_pascal_files(path):
    """Get all PascalVOC XML files from a specific path."""
    files = []

    for file in tqdm(os.listdir(path)):
        if file.endswith(".xml"):
            files.append(os.path.join(path, file))

    return files

def parse_pascal_file(file, image_dir):
    """Parse a specific PascalVOC file to a usable dict format."""
    xml = ET.parse(file)
    img_name = xml.find("filename").text.split(".")
    img_extension = img_name[-1]
    img_name = ".".join(img_name[:-1])
    objects = []
    labels = set()

    for i, obj in enumerate(xml.iter("object")):
        object_label = obj.find("name").text
        # Number each individual object to be able to get multiple objects from one file
        object_name = "{}-{}-{}.{}".format(img_name, object_label, i, img_extension)
        object_bndbox = obj.find("bndbox")
        labels.add(object_label)
        objects.append({
            "path": os.path.join(image_dir, "{}.{}".format(img_name, img_extension)),
            "name": object_name,
            "xmin": int(float(object_bndbox.find("xmin").text)),
            "xmax": int(float(object_bndbox.find("xmax").text)),
            "ymin": int(float(object_bndbox.find("ymin").text)),
            "ymax": int(float(object_bndbox.find("ymax").text)),
            "label": object_label
        })

    return {"objects": objects, "labels": labels}

def parse_pascal_files(files, image_dir):
    """Parse all PascalVOC files."""
    objects = []
    labels = set()

    for file in tqdm(files, ascii=True, desc="Parsing PascalVOC files"):
        try:
            parses = parse_pascal_file(file, image_dir)
            labels = labels.union(parses.get("labels"))
            objects += parses.get("objects")
        except Exception as e:
            # Just error if a single file can't be read
            print("Error parsing PascalVOC file: " + str(e))

    return {"objects": objects, "labels": labels}

def pascalvoc_to_images(objects, save_path):
    """Loop through all PascalVOC objects and cut an image from each."""
    for object in tqdm(objects, ascii=True, desc="Creating images from PascalVOC objects"):
        pascalvoc_to_image(object, save_path)

def pascalvoc_to_image(object, save_path):
    """Cut an image from a PascalVOC object."""
    # Create the bounding box to cut from
    bndbox = (object.get("xmin"), object.get("ymin"), object.get("xmax"), object.get("ymax"))
    image = Image.open(object.get("path"))
    image = image.crop(bndbox)

    try:
        image.save(os.path.join(save_path, object.get("label"), object.get("name")))
    except Exception as  e:
        # Just error if a single image does not save
        print("Error saving cut image: " + str(e))

def create_label_dirs(labels, save_path):
    """Function to create all label directories."""
    for label in tqdm(labels, ascii=True, desc="Creating label directories"):
        make_dir(save_path, label)

def make_dir(path, name=""):
    """Helper function to create a directory if it does not already exist."""
    path = os.path.abspath(os.path.join(path, name))

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            # Raise if directory can't be made, because image cuts won't be saved.
            print("Error creating directory:")
            raise e
