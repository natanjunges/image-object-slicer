# pascalvoc-to-image, slice images using annotation files.
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
from multiprocessing import Pool, cpu_count

__version__ = "1.2.2"

def main():
    parser = argparse.ArgumentParser(description="Slice images using annotation files")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
    parser.add_argument("annotations", help="A path to the directory with the annotation files")
    parser.add_argument("images", help="A path to the directory with the input images")
    parser.add_argument("save", help="A path to the directory to save the image slices to")
    parser.add_argument("-p", "--padding", type=int, default=0, help="The amount of padding (in pixels) to add to each image slice")
    parser.add_argument("-w", "--workers", type=int, default=cpu_count(), help="The number of parallel workers to run (default is cpu count)")
    args = parser.parse_args()
    annotation_files = find_annotation_files(args.annotations)

    if len(annotation_files) > 0:
        parsed_annotation_files = parse_annotation_files(annotation_files, args.images, args.workers)

        if len(parsed_annotation_files) > 0:
            make_dir(args.save)
            create_label_dirs(parsed_annotation_files.get("labels"), args.save)
            slice_images(parsed_annotation_files.get("paths"), parsed_annotation_files.get("slice_groups"), args.padding, args.save, args.workers)
        else:
            print("Found no slices")
    else:
        print("Found no annotation file")

def find_annotation_files(path):
    """Find all annotation files from a specific path."""
    files = []

    for file in tqdm(os.listdir(path), desc="Finding annotation files"):
        if file.endswith(".xml"):
            files.append(os.path.join(path, file))

    return files

def parse_annotation_file(args):
    """Parse a specific annotation file to a usable dict format."""
    file = args[0]
    image_dir = args[1]

    try:
        xml = ElementTree.parse(file)
        img_name = xml.find("filename").text.split(".")
        img_extension = img_name[-1]
        img_name = ".".join(img_name[:-1])
        path = os.path.join(image_dir, "{}.{}".format(img_name, img_extension))
        slices = []
        labels = set()

        for obj in xml.iterfind("object"):
            object_label = obj.find("name").text
            object_bndbox = obj.find("bndbox")
            labels.add(object_label)
            slices.append({
                "xmin": float(object_bndbox.find("xmin").text),
                "xmax": float(object_bndbox.find("xmax").text),
                "ymin": float(object_bndbox.find("ymin").text),
                "ymax": float(object_bndbox.find("ymax").text),
                "label": object_label
            })

        # Sort left-to-right, top-to-bottom
        slices.sort(key=lambda slice: (int(round(slice.get("xmin"))), int(round(slice.get("ymin"))), int(round(slice.get("xmax"))), int(round(slice.get("ymax")))))

        for i, slice in enumerate(slices):
            # Number each individual slice to be able to get multiple slices from one file
            slice["name"] = "{}-{}-{}.{}".format(img_name, slice.get("label"), i, img_extension)

        return {"path": path, "slices": slices, "labels": labels}
    except Exception as e:
        # Just error if a single file can't be read
        print("Error parsing annotation file: " + str(e))

def parse_annotation_files(files, image_dir, workers):
    """Parse all annotation files."""
    paths = []
    slice_groups = []
    labels = set()

    with Pool(workers) as pool:
        for parses in tqdm(pool.imap_unordered(parse_annotation_file, [(file, image_dir) for file in files], workers), desc="Parsing annotation files", total=len(files)):
            if parses is not None and len(parses.get("slices")) > 0:
                labels = labels.union(parses.get("labels"))
                paths.append(parses.get("path"))
                slice_groups.append(parses.get("slices"))

    return {"paths": paths, "slice_groups": slice_groups, "labels": labels}

def slice_images(paths, slice_groups, padding, save_path, workers):
    """Loop through all slice groups and slice each image."""
    with Pool(workers) as pool:
        for _ in tqdm(pool.imap_unordered(slice_image, [(path, slices, padding, save_path) for path, slices in zip(paths, slice_groups)], workers), desc="Slicing images", total=len(slice_groups)):
            pass

def slice_image(args):
    """Slice an image from slices."""
    path = args[0]
    slices = args[1]
    padding = args[2]
    save_path = args[3]
    image = Image.open(path)

    for slice in slices:
        # Create the bounding box to slice from
        bndbox = (max(0, slice.get("xmin") - padding), max(0, slice.get("ymin") - padding), min(slice.get("xmax") + padding, image.width), min(slice.get("ymax") + padding, image.height))
        image_slice = image.crop(bndbox)

        try:
            image_slice.save(os.path.join(save_path, slice.get("label"), slice.get("name")))
        except Exception as  e:
            # Just error if a single image does not save
            print("Error saving image slice: " + str(e))

def create_label_dirs(labels, save_path):
    """Create all label directories."""
    for label in tqdm(labels, desc="Creating directories"):
        make_dir(save_path, label)

def make_dir(path, name=""):
    """Create a directory if it does not already exist."""
    path = os.path.abspath(os.path.join(path, name))

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            # Raise if directory can't be made, because image slices won't be saved.
            print("Error creating directory:")
            raise e
