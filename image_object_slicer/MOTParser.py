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

class MOTParser(SingleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the MOT format."""

    glob = "gt/gt.txt"
    labels = "gt/labels.txt"

    @classmethod
    def parse_labels(cls, file):
        with open(file) as fp:
            labels = fp.readlines()

        return [label.strip() for label in labels]

    @classmethod
    def split_file(cls, file, labels):
        """Split a MOT annotation file into annotation items."""
        with open(file, newline="") as fp:
            data = DictReader(fp, ["frame_id", "track_id", "x", "y", "w", "h", "not_ignored", "class_id", "visibility", "skipped"])
            items = {}

            for item in data:
                item["class_id"] = labels[int(item.get("class_id")) - 1]
                items[item.get("frame_id")] = items.get(item.get("frame_id"), {"image": item.get("frame_id"), "annotations": []})
                items[item.get("frame_id")].get("annotations").append(item)

            return list(items.values())

    @classmethod
    def parse_item(cls, item):
        """Parse a MOT annotation item to a usable dict format."""
        name = item.get("image")
        slices = []
        labels = set()

        for obj in item.get("annotations"):
            object_label = obj.get("class_id")
            labels.add(object_label)
            xmin = float(obj.get("x"))
            ymin = float(obj.get("y"))
            slices.append({
                "xmin": round(xmin),
                "ymin": round(ymin),
                "xmax": round(xmin + float(obj.get("w"))),
                "ymax": round(ymin + float(obj.get("h"))),
                "label": object_label
            })

        return {"name": name, "slices": slices, "labels": labels}
