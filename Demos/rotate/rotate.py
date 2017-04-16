#!/usr/bin/env python
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp=file_path)
degress = 90
new_im = im.rotate(degress)

new_filename = os.path.splitext(os.path.basename(file_path))[0] + "-rotate-" + str(degress) + ".jpg"
new_im.save(os.path.join(PWD, new_filename))
