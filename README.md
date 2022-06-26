# image-object-slicer
Slice objects from images using annotation files. Convert an object detection dataset to an image classification one.

This is a fork of [gitlab.com/straighter/pascalvoc-to-image](https://gitlab.com/straighter/pascalvoc-to-image).

## Usage
Using the script is pretty simple, since it only has three required parameters:


```
usage: image-object-slicer [-h] [-v] [-p PADDING] [-w WORKERS] annotations images save

Slice objects from images using annotation files

positional arguments:
  annotations           A path to the directory with the annotation files
  images                A path to the directory with the input images
  save                  A path to the directory to save the image slices to

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -p PADDING, --padding PADDING
                        The amount of padding (in pixels) to add to each image slice
  -w WORKERS, --workers WORKERS
                        The number of parallel workers to run (default is cpu count)
```

## Installation
Download the latest stable wheel file from the [releases page](https://github.com/natanjunges/image-object-slicer/releases) and run:
```shell
sudo pip3 install ./image_object_slicer-*-py3-none-any.whl
```

Or install the latest development version from the git repository:
```shell
git clone https://www.github.com/natanjunges/image-object-slicer.git
cd image-object-slicer
sudo pip3 install ./
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
