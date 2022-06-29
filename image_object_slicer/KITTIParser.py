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

class KITTIParser(MultipleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the KITTI format."""

    glob = "*/label_2/*.txt"

    @classmethod
    def parse_file(cls, file, labels):
        """Parse a KITTI annotation file to a usable dict format."""
        with open(file, newline="") as fp:
            data = DictReader(fp, ["type", "truncated", "occluded", "alpha", "bbox_left", "bbox_top", "bbox_right", "bbox_bottom", "dimensions_height", "dimensions_width", "dimensions_length", "location_x", "location_y", "location_z", "rotation_y", "score"], delimiter=" ")
            name = ".".join(file.split("/")[-1].split(".")[:-1])
            slices = []
            labels = set()

            for obj in data:
                object_label = obj.get("type")
                labels.add(object_label)
                slices.append({
                    "xmin": round(float(obj.get("bbox_left"))),
                    "ymin": round(float(obj.get("bbox_top"))),
                    "xmax": round(float(obj.get("bbox_right"))),
                    "ymax": round(float(obj.get("bbox_bottom"))),
                    "label": object_label
                })

            return {"name": name, "slices": slices, "labels": labels}
