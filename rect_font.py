#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import PIL
from PIL import Image, ImageDraw, ImageFont
import glob
import os
import random
import numpy as np

DEBUG = True

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def check_fonts_load(font_file_lists):
    for font_file in font_file_lists:
        flag = ImageFont.truetype(font_file, 7)
    logger.info('Loading fonts are ok...')


def transPNG(srcImageName, dstImageName):
    img = Image.open(srcImageName)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = list()
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(dstImageName, "PNG")

if __name__ == '__main__':
    if DEBUG : print 'version of PIL', PIL.__version__
    # define the global variable path
    fonts_library = '/data/FONTS/fonts_lib'     # copy from C:\Windows\Fonts
    images_library = '/data/FONTS/images_lib'
    result_path = '/data/FONTS/gen_images'
    textes_path = '/data/FONTS/gen_bboxes'
    assert os.path.exists(fonts_library) and os.path.exists(images_library) and os.path.exists(result_path)

    font_types = glob.glob('{}/*.TTF'.format(fonts_library))
    image_lists = glob.glob(('{}/*.jpg'.format(images_library)))
    # check fonts file can be loaded correctly
    check_fonts_load(font_types)
    # load an image
    for img in image_lists:
        filename = img.split('/')[-1]
        im = Image.open(img)
        draw = ImageDraw.Draw(im)
        height, width, _ = np.array(im).shape
        if DEBUG: print 'height&width of image', height, width
        # some random variables -- font's (type, size, location, width, height), color's (r,g,b)
        font_id = random.randint(0, len(font_types)-1)
        font_size = random.randint(15, 33)
        start_x = random.randint(0, height-1)
        start_y = random.randint(0, width-1)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        STRING = unicode('我是广告', 'utf-8')
        ttfont = ImageFont.truetype(font_types[font_id], font_size)
        # create same size canvas to draw text
        draw.text((start_x, start_y), STRING, fill=(r, g, b), font=ttfont)
        text_size = draw.textsize(STRING, font=ttfont)      # get the rect. area of text
        if DEBUG : print start_x, start_y, text_size, font_size
        # get the bbox coordinates right
        if start_x + text_size[0] < width:
            end_x = start_x + text_size[0]
        else:
            end_x = width - 1
        if start_y + text_size[1] < height:
            end_y = start_y + text_size[1]
        else:
            end_y = height - 1
        # pts = [start_x, start_y, start_x+text_size[0], start_y, start_x+text_size[0], start_y+text_size[1], start_x, start_y+text_size[1], start_x, start_y]
        pts = [start_x, start_y, end_x, start_y, end_x, end_y, start_x, end_y, start_x, start_y]
        # draw.line(pts, fill=(0, 0, 0), width=2)
        # text_size = draw.textsize()
        # draw.text((40, 40), u'广告', fill=(255, 255, 255), font=ttfont)
        im.save('{}/gen_{}'.format(result_path, filename), 'JPEG')
        # save bbox in a textfile
        textname = filename.replace('.jpg', '.txt')
        textfile_path = '{}/{}'.format(textes_path, textname)
        with open(textfile_path, 'wb') as fwrite:
            one_line = str(start_x) + ' ' + str(start_y) + ' ' + str(end_x) + ' ' + str(end_y) + ' ' + STRING.encode('gbk')
            fwrite.write(one_line)
