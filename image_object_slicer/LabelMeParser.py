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

from xml.etree import ElementTree

from .MultipleFileAnnotationParser import MultipleFileAnnotationParser

class LabelMeParser(MultipleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the LabelMe format."""

    glob = "*/*.xml"

    @classmethod
    def parse_file(cls, file, labels):
        """Parse a LabelMe annotation file to a usable dict format."""
        data = ElementTree.parse(file)
        name = data.find("filename").text
        slices = []
        labels = set()

        for obj in data.iterfind("object"):
            object_type = obj.find("type")

            if object_type is not None and object_type.text == "bounding_box":
                object_label = obj.find("name").text
                object_bndbox = obj.find("polygon")
                object_points = object_bndbox.findall("pt")
                labels.add(object_label)
                slices.append({
                    "xmin": round(float(object_points[0].find("x").text)),
                    "ymin": round(float(object_points[0].find("y").text)),
                    "xmax": round(float(object_points[2].find("x").text)),
                    "ymax": round(float(object_points[2].find("y").text)),
                    "label": object_label
                })

        return {"name": name, "slices": slices, "labels": labels}
