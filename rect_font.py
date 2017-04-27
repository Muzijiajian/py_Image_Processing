#encoding=utf-8
import PIL
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import glob
import os
import random
import numpy as np
import math

DEBUG = False
DEGREE = math.pi / 180

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

def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def watermark(im, mark, position, opacity=1):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)

if __name__ == '__main__':
    if DEBUG : print 'version of PIL', PIL.__version__
    # define the global variable path
    fonts_library = '/data/FONTS/fonts_lib'     # copy from C:\Windows\Fonts
    images_library = '/data/FONTS/images_lib'
    result_path = '/data/FONTS/gen_images'
    final_path = '/data/FONTS/final_images'
    assert os.path.exists(fonts_library) and os.path.exists(images_library) and os.path.exists(result_path)

    font_types = glob.glob('{}/*.TTF'.format(fonts_library))
    image_lists = glob.glob(('{}/*.jpg'.format(images_library)))
    # check fonts file can be loaded correctly
    check_fonts_load(font_types)
    # load an image
    for img in image_lists:
        filename = img.split('/')[-1]

        logger.info('Dealing with {}'.format(filename))

        im = Image.open(img)
        shape = np.array(im).shape
        height = shape[0]
        width = shape[1]
        if DEBUG: print 'height&width of image', height, width
        # some random variables -- font's (type, size, location, width, height), color's (r,g,b)
        font_id = random.randint(0, len(font_types)-1)
        font_size = random.randint(15, 33)
        start_x = random.randint(0, height/2)
        start_y = random.randint(0, width/2)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        STRING = unicode('我是广告', 'utf-8')
        ttfont = ImageFont.truetype(font_types[font_id], font_size)
        # create same size canvas to draw text
        empty_im = Image.new('RGBA', (height, width), 'white')
        draw = ImageDraw.Draw(empty_im)
        draw.text((start_x, start_y), STRING, fill=(r, g, b), font=ttfont)
        text_size = draw.textsize(STRING, font=ttfont)      # get the rect. area of text
        if DEBUG : print start_x, start_y, text_size, font_size
        # get the bbox coordinates right
        if start_x + text_size[0] < height:
            end_x = start_x + text_size[0]
        else:
            end_x = height - 1
        if start_y + text_size[1] < width:
            end_y = start_y + text_size[1]
        else:
            end_y = width - 1
        # pts = [start_x, start_y, start_x+text_size[0], start_y, start_x+text_size[0], start_y+text_size[1], start_x, start_y+text_size[1], start_x, start_y]
        pts = [start_x, start_y, end_x, start_y, end_x, end_y, start_x, end_y, start_x, start_y]
        # draw.line(pts, fill=(0, 0, 0), width=2)
        # crop text and rotate some angle then paste it back
        rotate_angle = random.randint(-10, 10)
        if DEBUG : print 'final text position', start_x, start_y, end_x, end_y
        croppedText = empty_im.crop((start_x, start_y, end_x, end_y))
        rotatedText = croppedText.rotate(rotate_angle, expand=0)
        fff = Image.new('RGBA', rotatedText.size, (255,) * 4)
        final_Text = Image.composite(rotatedText, fff, rotatedText)
        final_Text.save('{}/text_{}'.format(result_path, filename), 'PNG')
        transPNG('{}/text_{}'.format(result_path, filename), '{}/trans_{}'.format(result_path, filename))
        # text_size = draw.textsize()
        # draw.text((40, 40), u'广告', fill=(255, 255, 255), font=ttfont)
        im.save('{}/gen_{}'.format(result_path, filename), 'JPEG')

        # use water mark method
        im = Image.open('{}/gen_{}'.format(result_path, filename))
        mark = Image.open('{}/trans_{}'.format(result_path, filename))
        merge_im = watermark(im, mark, (start_x, start_y), 1.0)
        # final_path -> result_path
        merge_im.save('{}/final_{}'.format(result_path, filename))

