# image-object-slicer, slice objects from images using annotation files.
# Copyright (C) 2018  Jori Regter <joriregter@gmail.com>
# Copyright (C) 2022  Natan Junges <natanajunges@gmail.com>
#
# image-object-slicer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# image-object-slicer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with image-object-slicer.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
from tqdm import tqdm
from PIL import Image
from multiprocessing import Pool, cpu_count
import pathlib

from .SingleFileAnnotationParser import SingleFileAnnotationParser
from .MultipleFileAnnotationParser import MultipleFileAnnotationParser
from .PascalVOCParser import PascalVOCParser
from .COCOParser import COCOParser
from .CVATImagesParser import CVATImagesParser
from .DatumaroParser import DatumaroParser
from .KITTIParser import KITTIParser
from .LabelMeParser import LabelMeParser

__version__ = "1.8.0"

formats = {
    # The first is always the default
    "pascalvoc": PascalVOCParser,
    "coco": COCOParser,
    "cvatimages": CVATImagesParser,
    "datumaro": DatumaroParser,
    "kitti": KITTIParser,
    "labelme": LabelMeParser
}

def main():
    parser = argparse.ArgumentParser(description="Slice objects from images using annotation files")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
    parser.add_argument("annotations", help="A path to the directory with the annotation files")
    parser.add_argument("images", help="A path to the directory with the input images")
    parser.add_argument("save", help="A path to the directory to save the image slices to")
    format_choices = list(formats.keys())
    parser.add_argument("-f", "--format", choices=format_choices, default=format_choices[0], help="The format of the annotation files (default is {})".format(format_choices[0]))
    parser.add_argument("-p", "--padding", type=int, default=0, help="The amount of padding (in pixels) to add to each image slice")
    parser.add_argument("-w", "--workers", type=int, default=cpu_count(), help="The number of parallel workers to run (default is cpu count)")
    args = parser.parse_args()
    annotation_files = find_annotation_files(formats.get(args.format), args.annotations)

    if len(annotation_files) > 0:
        parsed_annotation_files = parse_annotation_files(formats.get(args.format), annotation_files, args.workers)

        if len(parsed_annotation_files) > 0:
            make_dir(args.save)
            create_label_dirs(parsed_annotation_files.get("labels"), args.save)
            slice_images(args.images, parsed_annotation_files.get("names"), parsed_annotation_files.get("slice_groups"), args.padding, args.save, args.workers)
        else:
            print("Found no slices")
    else:
        print("Found no annotation file")

def find_annotation_files(format, path):
    """Find all annotation files from a specific path."""
    print("Finding annotation files: ", end="")
    files = list(pathlib.Path(path).glob(format.glob))

    if len(files) > 0:
        files = [str(file) for file in files]

    if issubclass(format, SingleFileAnnotationParser) and len(files) > 1:
        raise Exception("Could not find a unique annotation file: {}".format(files))

    print("{0}/{0}".format(len(files)))
    return files

def parse_annotation_file(args):
    """Parse a specific annotation file to a usable dict format."""
    format = args[0]
    file = args[1]

    try:
        parse = format.parse_file(file)
        # Sort left-to-right, top-to-bottom
        parse.get("slices").sort(key=lambda slice: (int(round(slice.get("xmin"))), int(round(slice.get("ymin"))), int(round(slice.get("xmax"))), int(round(slice.get("ymax")))))
        return parse
    except Exception as e:
        # Just error if a single file cannot be read
        print("Error parsing annotation file: " + str(e))

def parse_annotation_item(args):
    """Parse a specific annotation item to a usable dict format."""
    format = args[0]
    item = args[1]

    try:
        parse = format.parse_item(item)
        # Sort left-to-right, top-to-bottom
        parse.get("slices").sort(key=lambda slice: (int(round(slice.get("xmin"))), int(round(slice.get("ymin"))), int(round(slice.get("xmax"))), int(round(slice.get("ymax")))))
        return parse
    except Exception as e:
        # Just error if a single item cannot be read
        print("Error parsing annotation item: " + str(e))

def parse_annotation_files(format, files, workers):
    """Parse all annotation files."""
    names = []
    slice_groups = []
    labels = set()

    if issubclass(format, SingleFileAnnotationParser):
        try:
            split = format.split_file(files[0])
        except Exception as e:
            # Raise because this is the only file
            print("Error parsing annotation file:")
            raise e

        with Pool(workers) as pool:
            for parses in tqdm(pool.imap_unordered(parse_annotation_item, [(format, item) for item in split], workers), desc="Parsing annotation file", total=len(split)):
                if parses is not None and len(parses.get("slices")) > 0:
                    labels = labels.union(parses.get("labels"))
                    names.append(parses.get("name"))
                    slice_groups.append(parses.get("slices"))
    else:
        with Pool(workers) as pool:
            for parses in tqdm(pool.imap_unordered(parse_annotation_file, [(format, file) for file in files], workers), desc="Parsing annotation files", total=len(files)):
                if parses is not None and len(parses.get("slices")) > 0:
                    labels = labels.union(parses.get("labels"))
                    names.append(parses.get("name"))
                    slice_groups.append(parses.get("slices"))

    return {"names": names, "slice_groups": slice_groups, "labels": labels}

def slice_images(images_path, names, slice_groups, padding, save_path, workers):
    """Loop through all slice groups and slice each image."""
    with Pool(workers) as pool:
        for _ in tqdm(pool.imap_unordered(slice_image, [(images_path, name, slices, padding, save_path) for name, slices in zip(names, slice_groups)], workers), desc="Slicing images", total=len(slice_groups)):
            pass

def slice_image(args):
    """Slice an image from slices."""
    images_path = args[0]
    name = args[1].split(".")

    if len(name) == 1:
        name = name[0]
        files = list(pathlib.Path(images_path).glob(name + ".*"))

        if len(files) > 0:
            files = [file.name for file in files]

        if len(files) == 0:
            print("No file candidate found: {}.*".format(name))
            return
        elif len(files) == 1:
            name = files[0].split(".")
        else:
            print("Multiple file candidates found: {}".format(files))
            return

    extension = name[-1]
    name = ".".join(name[:-1])

    slices = args[2]
    padding = args[3]
    save_path = args[4]
    image = Image.open(os.path.join(images_path, "{}.{}".format(name, extension)))

    for i, slice in enumerate(slices):
        # Create the bounding box to slice from
        bndbox = (max(0, slice.get("xmin") - padding), max(0, slice.get("ymin") - padding), min(slice.get("xmax") + padding, image.width), min(slice.get("ymax") + padding, image.height))
        image_slice = image.crop(bndbox)

        try:
            image_slice.save(os.path.join(save_path, slice.get("label"), "{}-{}-{}.{}".format(name, slice.get("label"), i, extension)))
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
            # Raise if directory cannot be made, because image slices will not be saved
            print("Error creating directory:")
            raise e
