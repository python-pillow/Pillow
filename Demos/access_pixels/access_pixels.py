#!/usr/bin/env python
from __future__ import print_function
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)
file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp = file_path)
im = im.draft("L", im.size)
w, h = im.size[0], im.size[1]
pixels = im.load()

print("width:", w)
print("high:", h)
print("white(255) ~ black(0):", pixels[0, 0])

def print_im(im, w=None, h=None):
    if isinstance(im, Image.Image):
        w, h = im.size[0], im.size[1]
        pixels = im.load()
    else:
        pixels = im

    for x in range(w):
        for y in range(h):

            if pixels[x, y] > 128:
                print(" ", end=' ')
            else:
                print("1", end=' ')
        print()

print_im(im, w, h)