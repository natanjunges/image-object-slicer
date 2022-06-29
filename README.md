# image-object-slicer
Slice objects from images using annotation files. Convert an object detection dataset to an image classification one. To annotate the images to be used with this tool, we recommend [openvinotoolkit/cvat](https://github.com/openvinotoolkit/cvat).

This is a fork of [gitlab.com/straighter/pascalvoc-to-image](https://gitlab.com/straighter/pascalvoc-to-image).

## Installation
Install the latest stable version from [PyPI](https://pypi.org/project/image-object-slicer/) with:
```shell
sudo pip3 install image-object-slicer
```

Or download the latest stable wheel file from the [releases page](https://github.com/natanjunges/image-object-slicer/releases) and run:
```shell
sudo pip3 install ./image_object_slicer-*-py3-none-any.whl
```

Or install the latest development version from the git repository:
```shell
git clone https://www.github.com/natanjunges/image-object-slicer.git
cd image-object-slicer
sudo pip3 install ./
```

## Usage
Different formats of annotation files are supported:

| Annotation format | Command line option |
|-------------------|---------------------|
| [MS COCO Object Detection](https://cocodataset.org/#format-data) | `coco` |
| [CVAT for images](https://openvinotoolkit.github.io/cvat/docs/manual/advanced/xml_format/#annotation) | `cvatimages` |
| [Datumaro](https://github.com/openvinotoolkit/datumaro) | `datumaro` |
| [KITTI](http://cvlibs.net/datasets/kitti/) | `kitti` |
| [LabelMe](http://labelme.csail.mit.edu/Release3.0) | `labelme` |
| [Open Images](https://storage.googleapis.com/openimages/web/index.html) | `openimages` |
| [Pascal VOC](http://host.robots.ox.ac.uk/pascal/VOC/) | `pascalvoc` |
| [WIDER Face](https://shuoyang1213.me/WIDERFACE/) | `widerface` |
| [YOLO](https://pjreddie.com/darknet/yolo/) | `yolo` |

Using the script is pretty simple, since it only has three required parameters:
```
usage: image-object-slicer [-h] [-v] [-f {pascalvoc,coco,cvatimages,datumaro,kitti,labelme,openimages,widerface,yolo}] [-p PADDING] [-w WORKERS] annotations images save

Slice objects from images using annotation files

positional arguments:
  annotations           A path to the directory with the annotation files
  images                A path to the directory with the input images
  save                  A path to the directory to save the image slices to

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -f {pascalvoc,coco,cvatimages,datumaro,kitti,labelme,openimages,widerface,yolo}, --format {pascalvoc,coco,cvatimages,datumaro,kitti,labelme,openimages,widerface,yolo}
                        The format of the annotation files (default is pascalvoc)
  -p PADDING, --padding PADDING
                        The amount of padding (in pixels) to add to each image slice
  -w WORKERS, --workers WORKERS
                        The number of parallel workers to run (default is cpu count)
```

## Building
To build the wheel file, you need `deb:python3.10-venv` and `pip:build`:
```shell
sudo apt install python3.10-venv
sudo pip3 install build
```

Build the wheel file with:
```shell
python3 -m build --wheel
```
