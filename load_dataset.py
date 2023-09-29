import os
import io
import time
import shutil

from PIL import Image
import numpy as np
import pandas as pd
import struct

from item import Item

# directory paths
DATA_BASE_DIR = 'data/'
PHOTOS = os.path.join(DATA_BASE_DIR, 'photos/')
RAW_IMAGES_DIR = os.path.join(PHOTOS, 'solid_background/')
RATINGS_BIN_FILE = os.path.join(DATA_BASE_DIR, 'ratings.bin')
RATING_CSV = os.path.join(DATA_BASE_DIR, 'rating.csv')

parsed_items = []

def configure_folder(folder:str) -> bool:
    if not os.path.isdir(folder):
        os.makedirs(folder)
    return os.path.isdir(folder)

class Settings:
    
    def __init__(self, scale, grey):
        self.SCALE = scale
        self.GREY = grey
        self.SCALE_FOLDER = os.path.join(PHOTOS, str(scale[0]) + 'x' + str(scale[1]) + '/') 
        self.IMAGE_BIN_FILE = os.path.join(DATA_BASE_DIR, f'{str(scale[0])}_{str(scale[1])}-img.bin')
        
        configure_folder(self.SCALE_FOLDER)

        if grey:
            self.GREYSCALE_FOLDER = os.path.join(self.SCALE_FOLDER, 'greyscale/')
            configure_folder(self.GREYSCALE_FOLDER)
        
    def resize(self) -> None:  
        t1 = time.perf_counter()
        sum = 0
        for i, _ in enumerate(os.listdir(RAW_IMAGES_DIR)):
            print(f'Resizing images: {i+1}/{len(os.listdir(RAW_IMAGES_DIR))}', end='\r')
            item = os.path.join(RAW_IMAGES_DIR, str(i+1) + '.jpg')        
            
            if os.path.isfile(item): 
                if os.path.isfile(self.SCALE_FOLDER + str(i+1) + '.jpg'):
                    continue

                with Image.open(item) as image:
                    width, height = image.size
                
                if (width, height) == self.SCALE:                       
                    shutil.move(item, self.SCALE_FOLDER + str(i+1) + '.jpg')
                else:
                    with Image.open(item) as jpg:
                        jpg = jpg.resize(self.SCALE, resample=Image.BILINEAR)
                        jpg.save(os.path.join(self.SCALE_FOLDER + str(i+1) + '.jpg'))
                    sum += 1
        t2 = time.perf_counter()
        print(f'Completed resizing of {sum} images in {t2-t1:0.2f} seconds.') if sum > 0 else print(f'All images are already {self.SCALE} sized.')

    def rgb_to_greyscale(self) -> None:
        t1 = time.perf_counter()
        sum = 0
        for i, _ in enumerate(os.listdir(self.SCALE_FOLDER)):
            print(f'Converting images to greyscale: {i+1}/{len(os.listdir(self.SCALE_FOLDER))}', end='\r')
            image = os.path.join(self.SCALE_FOLDER, str(i+1) + '.jpg')
            if os.path.isfile(image):
                item = os.path.join(self.GREYSCALE_FOLDER, str(i+1) + '.jpg')
                
                if os.path.isfile(item):
                    continue

                with Image.open(image) as img:
                    grey_img = img.convert('L')
                    grey_img.save(item)
                sum += 1
        t2 = time.perf_counter()
        print(f'Completed conversion of {sum} images from rgb to greyscale in {t2-t1:0.2f} seconds.') if sum > 0 else print('All images have already been converted in greyscale.')

    def normalize(self, rgb, image):
        pixels = []
        for x in range(image.size[1]):
            row = []

            for y in range(image.size[0]):
                r, g, b = image.getpixel((y, x))
                pixel = [r/255, g/255, b/255]
                row.append(pixel)
            pixels.append(row)

        return pixels

    def jpg_to_rgb(self, id) -> np.array:
        jpg = os.path.join(self.SCALE_FOLDER, str(id) + '.jpg')
        with open(jpg, 'rb') as img: 
            data = img.read()
            image = Image.open(io.BytesIO(data))
            rgb = image.convert('RGB')
        return rgb

    def parse_row(self, row) -> Item:
        item = Item()
        item.id = int(row['id'])
        item.like = int(row['like'])

        return item

    def parse_rows(self):
        if len(parsed_items) == 0:
            data = pd.read_csv(RATING_CSV, encoding='ISO-8859-1')        
            for i, row in data.iterrows():
                print(f'Parsing data: {i}/{len(data)}', end='\r')
                item = self.parse_row(row)
                parsed_items.append(item)
            print(f'Completed parsing {len(data)} images.')
        else:
            print('Images are already parsed.')

    def create_binfiles(self):
        t1 = time.perf_counter()
        total = 0
        # fx = image bin file
        fx = open(self.IMAGE_BIN_FILE, 'wb')           
        fx.write(total.to_bytes(4, byteorder='big', signed=False))

        # fy = ratings bin file
        fy = open(RATINGS_BIN_FILE, 'wb')
        fy.write(total.to_bytes(4, byteorder='big', signed=False))

        self.parse_rows()

        count = 0
        for i, item in enumerate(parsed_items):
            print(f'Writing images to binary files: {i+1}/{len(parsed_items)}.', end='\r')
            if self.GREY:
                pass
            else:
                rgb = self.jpg_to_rgb(item.id)
                like = item.like
            if total == 0:
                fx.write((rgb.size[1]).to_bytes(4, byteorder='big', signed=False))
                fx.write((rgb.size[0]).to_bytes(4, byteorder='big', signed=False))
                fy.write(len(str(like)).to_bytes(1, byteorder='big', signed=False))

            fx.write(item.id.to_bytes(4, byteorder='big', signed=False))
            red = green = blue = []
            for y in range(rgb.size[1]):
                for x in range(rgb.size[0]):
                    r, g, b = rgb.getpixel((x, y))
                    red.append(r)
                    green.append(g)
                    blue.append(b)
            
            fx.write(bytearray(red))
            fx.write(bytearray(green))
            fx.write(bytearray(blue))

            fy.write(bytearray(like))

            count += 1
            total += 1
        t2 = time.perf_counter()

        if count > 0:
            print(f'Completed writing {count} images to binary file in {t2-t1:0.2f} seconds.')
    
        fx.seek(0)
        fx.write(total.to_bytes(4, byteorder='big', signed=False))
        fx.close()

        fy.seek(0)
        fy.write(total.to_bytes(4, byteorder='big', signed=False))
        fy.close()

    def read_binfiles(self):
        fx = open(self.IMAGE_BIN_FILE, 'rb')
        total = struct.unpack('>I', fx.read(4))[0]
        height = struct.unpack('>I', fx.read(4))[0]
        width = struct.unpack('>I', fx.read(4))[0]
        
        print(f'Retrieving {total} images of size {height}x{width}.')

        x = []
        ids = []
        for i in range(total):
            id = struct.unpack('>I', fx.read(4))[0]
            ids.append(id)
            r = g = b = np.array(bytearray(fx.read(height*width))).reshape((height, width))
            image = np.dstack((r, g, b))

            x.append(image / 255.0)
        
        fx.close()
        x = np.array(x, dtype='float32')
        ids = np.array(ids, dtype='uint32')

        return x, ids