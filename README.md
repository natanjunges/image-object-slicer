# pascalvoc-to-image
This is a fork of [gitlab.com/straighter/pascalvoc-to-image](https://gitlab.com/straighter/pascalvoc-to-image).

Tool to cut objects from bounding boxes in PascalVOC XML files. It will:
-   Read the directory containing the XMLs
-   Parse the XMLs to a readable format
-   Create images for all created bounding boxes in a separate folder

## Usage
Using the script is pretty simple, since it only has three required parameters:


```
usage: pascalvoc-to-image [-h] [-v] [-p PADDING] [-w WORKERS] annotations images save

Slice images using annotation files

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
Download the latest stable wheel file from the [releases page](https://github.com/natanjunges/pascalvoc-to-image/releases) and run:
```shell
sudo pip3 install ./pascalvoc_to_image-*-py3-none-any.whl
```

Or install the latest development version from the git repository:
```shell
git clone https://www.github.com/natanjunges/pascalvoc-to-image.git
cd pascalvoc-to-image
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
