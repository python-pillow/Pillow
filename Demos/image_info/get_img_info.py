#!/usr/bin/env python
from __future__ import print_function
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp=file_path)
w, h = im.size[0], im.size[1]

print("format:", type(im.format), im.format)
print("info:", type(im.info), im.info)
print("mode:", type(im.mode), im.mode)
print("size:", type(im.size), im.size)
print("bands:", type(im.getbands()), im.getbands())
print("histogram:", type(im.histogram()))

data = im.getdata()
print("getdata:", type(data))
assert len(im.getdata()) == w * h
