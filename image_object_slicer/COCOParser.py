# This file is part of image-object-slicer
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

import json

from .SingleFileAnnotationParser import SingleFileAnnotationParser

class COCOParser(SingleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the MS COCO Object Detection format."""

    glob = "annotations/instances_*.json"

    @classmethod
    def split_file(cls, file):
        """Split a MS COCO Object Detection annotation file into annotation items."""
        with open(file) as fp:
            data = json.load(fp)

        labels = data.get("categories")
        labels = [label.get("name") for label in labels]
        images = data.get("images")
        images = [image.get("file_name") for image in images]
        items = [{"image": image, "annotations": []} for image in images]

        for annotation in data.get("annotations"):
            annotation["category_id"] = labels[annotation.get("category_id") - 1]
            items[annotation.get("image_id") - 1].get("annotations").append(annotation)

        return items

    @classmethod
    def parse_item(cls, item):
        """Parse a MS COCO Object Detection annotation item to a usable dict format."""
        name = item.get("image")
        slices = []
        labels = set()

        for obj in item.get("annotations"):
            if len(obj.get("segmentation")) == 0:
                object_label = obj.get("category_id")
                object_bndbox = obj.get("bbox")
                labels.add(object_label)
                slices.append({
                    "xmin": object_bndbox[0],
                    "ymin": object_bndbox[1],
                    "xmax": object_bndbox[0] + object_bndbox[2],
                    "ymax": object_bndbox[1] + object_bndbox[3],
                    "label": object_label
                })

        return {"name": name, "slices": slices, "labels": labels}
