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

from csv import DictReader

from .SingleFileAnnotationParser import SingleFileAnnotationParser

class OpenImagesParser(SingleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the Open Images format."""

    glob = "annotations/*-annotations-bbox.csv"

    @classmethod
    def split_file(cls, file):
        """Split an Open Images annotation file into annotation items."""
        with open(file, newline="") as fp:
            data = DictReader(fp)
            items = {}

            for item in data:
                items[item.get("ImageID")] = items.get(item.get("ImageID"), {"image": item.get("ImageID"), "annotations": []})
                items[item.get("ImageID")].get("annotations").append(item)

            return list(items.values())

    @classmethod
    def parse_item(cls, item):
        """Parse an Open Images annotation item to a usable dict format."""
        name = item.get("image")
        slices = []
        labels = set()

        for obj in item.get("annotations"):
            object_label = obj.get("LabelName")
            labels.add(object_label)
            slices.append({
                "xmin": float(obj.get("XMin")),
                "ymin": float(obj.get("YMin")),
                "xmax": float(obj.get("XMax")),
                "ymax": float(obj.get("YMax")),
                "label": object_label
            })

        return {"name": name, "slices": slices, "labels": labels}
