from sensor import Sensor, DesignatedRouter
from multiprocessing import Queue, Array
from Receiver_and_Sender import Receiver, Sender, Transmitter, Result

import sys
import cv2
from os.path import splitext
from argparse import ArgumentParser
import numpy as np
from pathlib import Path

from helpers import (random_pos, random_vel, random_width, random_angle,
                     reflect_vector, cross, get_x, get_y, normalize, real_attr,
                     make_shared_arr, modify_shared_arr, array_from_shared,
                     shared_from_array, shared_from_double, double_from_shared)
from communication import (Connection, HelloMessage, AskEnergyMessage, RespondEnergyMessage,
                           StartCorrectionMessage, StopCorrectionMessage)

from matplotlib import pyplot as plt

from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
import multiprocessing as mp
import ctypes

from time import time, sleep
import os


def getImages(f_in, format_in, num):
    """Read images in directory.
    @param f_in Input derictory with files(images).
    """
    p = Path(f_in)
    nameIn = '*.' + format_in
    imgs = []
    for f in p.glob(nameIn):
        if int(f.stem) <= num - 1:
            imgs.append(cv2.imread(str(f)))
    return imgs


if __name__ == "__main__":
    #arg_parser = ArgumentParser()
    #arg_parser.add_argument("input", type=str, help="Input derictory with files(images)")
    #arg_parser.add_argument("-o", "--output", default="/results/", type=str, help="Output derictory")
    #arg_parser.add_argument("-n", "--number", default=2, type=int, help="Number of images")
    #args = arg_parser.parse_args()

    #imgs = getImages(args.input, 'jpg', args.number)
    numImgs = 10
    numCamers = 4
    imgs = getImages('D:\\University\\Diplom\\datasets\\sequence_01\\images', 'jpg', numImgs * numCamers)
    router = DesignatedRouter(numCamers, numImgs, imgs)
    #router.run_analyze()
    print("Done")