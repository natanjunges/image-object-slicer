# pascalvoc-to-image, tool to cut objects from bounding boxes in PascalVOC XML files.
# Copyright (C) 2018  Jori Regter <joriregter@gmail.com>
# Copyright (C) 2022  Natan Junges <natanajunges@gmail.com>
#
# pascalvoc-to-image is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# pascalvoc-to-image is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pascalvoc-to-image.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
from xml.etree import ElementTree
from tqdm import tqdm
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description="Tool to cut objects from bounding boxes in PascalVOC XML files")
    parser.add_argument("pascal", help="A path to the directory with the PascalVOC XML files")
    parser.add_argument("images", help="A path to the directory with the input images")
    parser.add_argument("save", help="A path to the directory to save the object bounding box images to")
    parser.add_argument("-p", "--padding", type=int, default=0, help="The amount of padding (in pixels) to add to each bounding box")
    args = parser.parse_args()
    pascal_files = get_pascal_files(args.pascal)
    parsed_pascal_files = parse_pascal_files(pascal_files, args.images)
    make_dir(args.save)
    create_label_dirs(parsed_pascal_files.get("labels"), args.save)
    pascalvoc_to_images(parsed_pascal_files.get("objects"), args.padding, args.save)

def get_pascal_files(path):
    """Get all PascalVOC XML files from a specific path."""
    files = []

    for file in tqdm(os.listdir(path), desc="Finding PascalVOC files"):
        if file.endswith(".xml"):
            files.append(os.path.join(path, file))

    return files

def parse_pascal_file(file, image_dir):
    """Parse a specific PascalVOC file to a usable dict format."""
    xml = ElementTree.parse(file)
    img_name = xml.find("filename").text.split(".")
    img_extension = img_name[-1]
    img_name = ".".join(img_name[:-1])
    objects = []
    labels = set()

    for obj in xml.iter("object"):
        object_label = obj.find("name").text
        object_bndbox = obj.find("bndbox")
        labels.add(object_label)
        objects.append({
            "path": os.path.join(image_dir, "{}.{}".format(img_name, img_extension)),
            "xmin": float(object_bndbox.find("xmin").text),
            "xmax": float(object_bndbox.find("xmax").text),
            "ymin": float(object_bndbox.find("ymin").text),
            "ymax": float(object_bndbox.find("ymax").text),
            "label": object_label
        })

    # Sort left-to-right, top-to-bottom
    objects.sort(key=lambda obj: (int(round(obj.get("xmin"))), int(round(obj.get("ymin"))), int(round(obj.get("xmax"))), int(round(obj.get("ymax")))))

    for i, obj in enumerate(objects):
        # Number each individual object to be able to get multiple objects from one file
        obj["name"] = "{}-{}-{}.{}".format(img_name, obj.get("label"), i, img_extension)

    return {"objects": objects, "labels": labels}

def parse_pascal_files(files, image_dir):
    """Parse all PascalVOC files."""
    objects = []
    labels = set()

    for file in tqdm(files, desc="Parsing PascalVOC files"):
        try:
            parses = parse_pascal_file(file, image_dir)
            labels = labels.union(parses.get("labels"))
            objects += parses.get("objects")
        except Exception as e:
            # Just error if a single file can't be read
            print("Error parsing PascalVOC file: " + str(e))

    return {"objects": objects, "labels": labels}

def pascalvoc_to_images(objects, padding, save_path):
    """Loop through all PascalVOC objects and cut an image from each."""
    for object in tqdm(objects, desc="Generating images"):
        pascalvoc_to_image(object, padding, save_path)

def pascalvoc_to_image(object, padding, save_path):
    """Cut an image from a PascalVOC object."""
    image = Image.open(object.get("path"))
    # Create the bounding box to cut from
    bndbox = (max(0, object.get("xmin") - padding), max(0, object.get("ymin") - padding), min(object.get("xmax") + padding, image.width), min(object.get("ymax") + padding, image.height))
    image = image.crop(bndbox)

    try:
        image.save(os.path.join(save_path, object.get("label"), object.get("name")))
    except Exception as  e:
        # Just error if a single image does not save
        print("Error saving cut image: " + str(e))

def create_label_dirs(labels, save_path):
    """Function to create all label directories."""
    for label in tqdm(labels, desc="Creating directories"):
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
