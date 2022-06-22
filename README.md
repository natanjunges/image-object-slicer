# pascalvoc-to-image

Tool to cut objects from bounding boxes in PascalVOC XML files. It will:

-   Read the directory containing the XMLs
-   Parse the XMLs to a readable format
-   Create images for all created bounding boxes in a separate folder

## Usage

Using the script is pretty simple, since it only has three parameters.


```
usage: pascalvoc-to-image [-h] pascal images save

Tool to cut objects from bounding boxes in PascalVOC XML files

positional arguments:
  pascal      A path to the directory with the PascalVOC XML files
  images      A path to the directory with the input images
  save        A path to the directory to save the object bounding box images to

options:
  -h, --help  show this help message and exit
```

## Installation

```
$ git clone https://www.github.com/natanjunges/pascalvoc-to-image.git
$ cd pascalvoc-to-image
$ sudo pip3 install .
```
