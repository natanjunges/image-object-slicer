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

from .MultipleFileAnnotationParser import MultipleFileAnnotationParser

class KITTIParser(MultipleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the KITTI format."""

    glob = "*/label_2/*.txt"

    @classmethod
    def parse_file(cls, file):
        """Parse a KITTI annotation file to a usable dict format."""
        with open(file) as fp:
            data = fp.readlines()

        name = ".".join(file.split("/")[-1].split(".")[:-1])
        slices = []
        labels = set()

        for obj in data:
            obj_fields = obj.split()
            object_label = obj_fields[0]
            labels.add(object_label)
            slices.append({
                "xmin": float(obj_fields[4]),
                "ymin": float(obj_fields[5]),
                "xmax": float(obj_fields[6]),
                "ymax": float(obj_fields[7]),
                "label": object_label
            })

        return {"name": name, "slices": slices, "labels": labels}
