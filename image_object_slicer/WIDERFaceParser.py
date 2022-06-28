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

from .SingleFileAnnotationParser import SingleFileAnnotationParser

class WIDERFaceParser(SingleFileAnnotationParser):
    """Class that abstracts the annotation parsing of the WIDER Face format."""

    glob = "wider_face_split/wider_face_*_bbx_gt.txt"

    @classmethod
    def split_file(cls, file):
        """Split a WIDER Face annotation file into annotation items."""
        with open(file) as fp:
            data = fp.readlines()

        items = []
        i = 0

        while i < len(data):
            try:
                item_len = int(data[i + 1])
                item = data[i:i+2+item_len]
                items.append(item)
                i += 2 + item_len
            except:
                i += 1

        return items

    @classmethod
    def parse_item(cls, item):
        """Parse a WIDER Face annotation item to a usable dict format."""
        name = item[0].split("/")[-1].strip()
        slices = []
        labels = set()

        for obj in item[2:]:
            obj_fields = obj.split()
            object_label = obj_fields[10]
            labels.add(object_label)
            xmin = float(obj_fields[0])
            ymin = float(obj_fields[1])
            slices.append({
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmin + float(obj_fields[2]),
                "ymax": ymin + float(obj_fields[3]),
                "label": object_label
            })

        return {"name": name, "slices": slices, "labels": labels}
