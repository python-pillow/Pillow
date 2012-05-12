#!/usr/bin/env python
import os
PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

import Image

file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp = file_path)
im = im.draft("L", im.size)
w, h = im.size[0], im.size[1]
pixsels = im.load()

print "width:", w
print "high:", h
print "white(255) ~ black(0):", pixsels[0, 0]

def print_im(im, w = None, h = None):
    if isinstance(im, Image.Image):
        w, h = im.size[0], im.size[1]
        pixsels = im.load()
    else:
        pixsels = im

    for x in xrange(w):
        for y in xrange(h):

            if pixsels[x, y] > 128:
                print " ",
            else:
                print "1",
        print

print_im(im, w, h)