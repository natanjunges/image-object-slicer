import argparse
import os
import xml.etree.ElementTree as ET
import time

from tqdm import tqdm
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('pascalDir', metavar='pascalDir', type=str, help='A path to the directory with Pascal VOC XML files')
parser.add_argument('imageDir', metavar='imageDir', type=str, help='A path to the directory with images')
parser.add_argument('saveDir', metavar='saveDir', type=str, help='A path to the directory to save Pascal boundingbox images to')

args = parser.parse_args()

def run():
    pascal_files = get_pascal_files(args.pascalDir)
    parsed_pascal_files = parse_pascal_files(pascal_files, args.imageDir)
    make_dir(args.saveDir)
    create_label_dirs(parsed_pascal_files.get('labels'), args.saveDir)
    pascalvoc_to_images(parsed_pascal_files.get('pascal_data'), args.saveDir)

def get_pascal_files(path):
    files = []

    for file in tqdm(os.listdir(path)):
        if file.endswith('.xml'):
            files.append({ 'base': path, 'filename': file, 'path': os.path.join(path, file)}) 

    return files

def parse_pascal_file(file, image_dir):
    xml_path = file.get('path') # Path of XML file

    xml = ET.parse(xml_path) # XML root

    img_name = xml.find('filename').text # IMG name corresponding to XML
    img_path = xml.find('path').text # IMG path corresponding to XML

    items = [] 
    labels = set()

    for i, obj in enumerate(xml.iter('object')):
        object_number = i + 1
        labels.add(obj.find('name').text)
        item_name = object_number + '-' + img_name
        items.append({ 
            'path': os.path.join(image_dir, img_name), 
            'name': item_name, 
            'xmin': obj.find('bndbox').find('xmin').text,
            'xmax': obj.find('bndbox').find('xmax').text, 
            'ymin': obj.find('bndbox').find('ymin').text, 
            'ymax': obj.find('bndbox').find('ymax').text, 
            'label': obj.find('name').text
        })
    
    return { 'items': items, 'labels': labels }

def parse_pascal_files(files, image_dir):
    pascal_data = []
    labels = set()

    for file in tqdm(files, ascii=True, desc="Parsing pascal files"):
        try:
            parses = parse_pascal_file(file, image_dir)
            labels= labels.union(parses.get('labels'))
            pascal_data += parses.get('items')
        except Exception as e:
            print('Error reading file at ' + file + '.')
            print('ERROR:' + str(e))

    return { 'pascal_data': pascal_data, 'labels': labels }


def pascalvoc_to_images(pascal_data, save_path):
    for item in tqdm(pascal_data, ascii=True, desc="Creating images from pascal data"):
        pascalvoc_to_image(item, save_path)

def pascalvoc_to_image(pascal_data, save_path):
    crop = (int(pascal_data.get('xmin')), int(pascal_data.get('ymin')), int(pascal_data.get('xmax')), int(pascal_data.get('ymax')))
    image = Image.open(pascal_data.get('path'))
    image = image.crop(crop)

    try:
        image.save(os.path.join(save_path, pascal_data.get('label'), pascal_data.get('name')))
    except Exception as  e:
        print('Error saving at ' + os.path.join(save_path, pascal_data.get('label'), pascal_data.get('name')))
        print('ERROR: ' + e)


def create_label_dirs(labels, save_path):
    for label in tqdm(labels, ascii=True, desc="Creating label directories"):
        make_dir(save_path, label)

def make_dir(path, name = ''):
    path = os.path.abspath(os.path.join(path, name))

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            print('Error creating directory at ' + path + '.')
            raise e