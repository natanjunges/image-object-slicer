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

from .MultipleFileAnnotationParser import MultipleFileAnnotationParser

class YOLOParser(MultipleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the YOLO format."""

    glob = "obj_*_data/*.txt"
    labels = "obj.names"

    @classmethod
    def parse_labels(cls, file):
        with open(file) as fp:
            labels = fp.readlines()

        return [label.strip() for label in labels]

    @classmethod
    def parse_file(cls, file, labels_list):
        """Parse a YOLO annotation file to a usable dict format."""
        with open(file, newline="") as fp:
            data = DictReader(fp, ["label_id", "cx", "cy", "rw", "rh"], delimiter=" ")
            name = ".".join(file.split("/")[-1].split(".")[:-1])
            slices = []
            labels = set()

            for obj in data:
                object_label = labels_list[int(obj.get("label_id"))]
                labels.add(object_label)
                cx = float(obj.get("cx"))
                cy = float(obj.get("cy"))
                rw = float(obj.get("rw"))
                rh = float(obj.get("rh"))
                slices.append({
                    "xmin": cx - (rw/2),
                    "ymin": cy - (rh/2),
                    "xmax": cx + (rw/2),
                    "ymax": cy + (rh/2),
                    "label": object_label
                })

            return {"name": name, "slices": slices, "labels": labels}
