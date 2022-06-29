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

from .SingleFileAnnotationParser import SingleFileAnnotationParser

class CVATImagesParser(SingleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the CVAT for images format."""

    glob = "annotations.xml"

    @classmethod
    def split_file(cls, file, labels):
        """Split a CVAT for images annotation file into annotation items."""
        data = ElementTree.parse(file)
        items = data.findall("image")
        i = 0

        while i < len(items):
            if items[i].find("box") is None:
                items.pop(i)
            else:
                i += 1

        return items

    @classmethod
    def parse_item(cls, item):
        """Parse a CVAT for images annotation item to a usable dict format."""
        name = item.get("name").split("/")[-1]
        slices = []
        labels = set()

        for obj in item.iterfind("box"):
            object_label = obj.get("label")
            labels.add(object_label)
            slices.append({
                "xmin": round(float(obj.get("xtl"))),
                "ymin": round(float(obj.get("ytl"))),
                "xmax": round(float(obj.get("xbr"))),
                "ymax": round(float(obj.get("ybr"))),
                "label": object_label
            })

        return {"name": name, "slices": slices, "labels": labels}
