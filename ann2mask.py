#encoding=utf-8
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import *
import glob
import os
import random
import cv2
import numpy as np

from joblib import Parallel, delayed
from python_utils import converters     # deal with weird error in image_6089, still remains

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)#, filename='./logs/ann2mask.txt')
logger = logging.getLogger(__name__)

DEBUG = False

def make_rec_mask(txtfile):
    """
    read annotation textfile and return its rec. masked image
    :param txtfile: txtfile: <x1>,<y1>,<x2>,<y2>,<x3>,<y3>,<x4>,<y4>,<difficult>,"<transcript>";
    """
    img_file = txtfile.replace('.txt', '.jpg')
    img_name = img_file.split('/')[-1]
    bgr_im = cv2.imread(img_file)  # opencv loads img in BGR order
    mask_img = np.zeros_like(bgr_im, dtype=np.int16)
    # mask_img = np.mean(mask_img, axis=-1)
    if DEBUG : print bgr_im.shape, mask_img.shape
    with open(txtfile, 'r') as fread:
        lines = fread.readlines()
        for line in lines:
            line = line.rstrip('\n')
            if DEBUG : print line
            line_components = line.split(',')
            diff = int(float(line_components[8]))  # skip difficult annotaions
            if diff == 0:
                x = y = width = height = 0
                x1 = converters.to_int(line_components[0])
                y1 = converters.to_int(line_components[1])
                x2 = converters.to_int(line_components[2])
                y2 = converters.to_int(line_components[3])
                x3 = converters.to_int(line_components[4])
                y3 = converters.to_int(line_components[5])
                x4 = converters.to_int(line_components[6])
                y4 = converters.to_int(line_components[7])
                # check annotaion file is not exceed image boundary e.g. image_1187, image_1664, image_1868 (y, x)
                if x1 <= 0: x1 = 0
                if y1 <= 0: y1 = 0
                if x2 >= bgr_im.shape[1] : x2 = bgr_im.shape[1]
                if y2 >= bgr_im.shape[0] : y2 = bgr_im.shape[0]
                if x3 >= bgr_im.shape[1] : x3 = bgr_im.shape[1]
                if y3 >= bgr_im.shape[0] : y3 = bgr_im.shape[0]
                if x4 >= bgr_im.shape[1] : x4 = bgr_im.shape[1]
                if y4 >= bgr_im.shape[0] : y4 = bgr_im.shape[0]
                # check coordinates to got rect.
                if x1 >= x4:
                    x = x1
                else:
                    x = x4
                if y1 >= y2:
                    y = y1
                else:
                    y = y2
                # cal rect. width & height
                width = x3 - x
                height = y4 - y
                # draw mask
                if DEBUG : print x, y, width, height
                for i in xrange(y, y+height):
                    for j in xrange(x, x+width):
                        mask_img[i, j, :] = 1
    logger.info('processed {}'.format(img_name))
    # save mask image into local file
    # if np.sum(mask_img) > 0:
    cv2.imwrite('{}/{}'.format(mask_images_path, img_name), mask_img*255)

def make_skew_mask(txtfile):
    """
    read annotation textfile and return its skew masked image
    :param txtfile: txtfile: <x1>,<y1>,<x2>,<y2>,<x3>,<y3>,<x4>,<y4>,<difficult>,"<transcript>";
    """
    img_file = txtfile.replace('.txt', '.jpg')
    img_name = img_file.split('/')[-1]
    bgr_im = cv2.imread(img_file)  # opencv loads img in BGR order
    mask_img = np.zeros_like(bgr_im, dtype=np.int16)

    bbox_points = []
    with open(txtfile, 'r') as fread:
        lines = fread.readlines()
        for line in lines:
            line = line.rstrip('\n')
            line_components = line.split(',')
            diff = int(float(line_components[8]))  # skip difficult annotaions
            if diff not in [0, 1]: print txtfile
            if diff == 0:
                x1 = converters.to_int(line_components[0])
                y1 = converters.to_int(line_components[1])
                x2 = converters.to_int(line_components[2])
                y2 = converters.to_int(line_components[3])
                x3 = converters.to_int(line_components[4])
                y3 = converters.to_int(line_components[5])
                x4 = converters.to_int(line_components[6])
                y4 = converters.to_int(line_components[7])
                pts = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], np.int32)
                cv2.fillPoly(mask_img, [pts], (255, 255, 255))

    # logger.info('processed {}'.format(img_name))
    if np.sum(mask_img) > 0:
        # make label 0 or 255 based
        mask_img = np.where(mask_img < 255, 0, 1)
        cv2.imwrite('{}/{}'.format(mask_images_path, img_name), mask_img)
    else:
        logger.info('{} file has no mask'.format(img_name))

if __name__ == '__main__':
    # sample_txtfile = icdar_dir_train + 'image_1868.txt'
    # make_rec_mask(sample_txtfile)

    # make_skew_mask(sample_txtfile)

    # set seed to replicate
    random.seed(0)
    all_txtfiles = glob.glob("{}*.txt".format(icdar_dir_train))

    # for txtfile in all_txtfiles:
    #     make_rec_mask(txtfile)
    # 4*8 cpus doing jobs
    # Parallel(n_jobs=num_thread*4)(delayed(make_rec_mask)(txtfile) for txtfile in all_txtfiles)
    Parallel(n_jobs=num_thread * 4)(delayed(make_skew_mask)(txtfile) for txtfile in all_txtfiles)
