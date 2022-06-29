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

class DatumaroParser(SingleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the Datumaro format."""

    glob = "annotations/*.json"

    @classmethod
    def split_file(cls, file, labels):
        """Split a Datumaro annotation file into annotation items."""
        with open(file) as fp:
            data = json.load(fp)

        labels = data.get("categories").get("label").get("labels")
        labels = [label.get("name") for label in labels]
        items = data.get("items")
        i = 0

        while i < len(items):
            if len(items[i].get("annotations")) == 0:
                items.pop(i)
            else:
                i += 1

        for item in items:
            for annotation in item.get("annotations"):
                annotation["label_id"] = labels[annotation.get("label_id")]

        return items

    @classmethod
    def parse_item(cls, item):
        """Parse a Datumaro annotation item to a usable dict format."""
        name = item.get("id").split("/")[-1]
        slices = []
        labels = set()

        for obj in item.get("annotations"):
            if obj.get("type") == "bbox":
                object_label = obj.get("label_id")
                object_bndbox = obj.get("bbox")
                labels.add(object_label)
                slices.append({
                    "xmin": round(object_bndbox[0]),
                    "ymin": round(object_bndbox[1]),
                    "xmax": round(object_bndbox[0] + object_bndbox[2]),
                    "ymax": round(object_bndbox[1] + object_bndbox[3]),
                    "label": object_label
                })

        return {"name": name, "slices": slices, "labels": labels}
