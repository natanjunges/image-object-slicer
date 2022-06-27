# This file is part of image-object-slicer
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

from xml.etree import ElementTree

from .MultipleFileAnnotationParser import MultipleFileAnnotationParser

class PascalVOCParser(MultipleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the Pascal VOC format."""

    glob = "Annotations/*.xml"

    @classmethod
    def parse_file(cls, file):
        """Parse a Pascal VOC annotation file to a usable dict format."""
        xml = ElementTree.parse(file)
        name = xml.find("filename").text
        slices = []
        labels = set()

        for obj in xml.iterfind("object"):
            object_label = obj.find("name").text
            object_bndbox = obj.find("bndbox")
            labels.add(object_label)
            slices.append({
                "xmin": float(object_bndbox.find("xmin").text),
                "ymin": float(object_bndbox.find("ymin").text),
                "xmax": float(object_bndbox.find("xmax").text),
                "ymax": float(object_bndbox.find("ymax").text),
                "label": object_label
            })

        return {"name": name, "slices": slices, "labels": labels}
