#!/usr/bin/env python
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)
file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp = file_path)

left_upper_x, left_upper_y = 0, 0
right_lower_x, right_lower_y = 100, 50
box = (left_upper_x, left_upper_y, right_lower_x, right_lower_y)

region = im.crop(box)

new_filename = "x".join([str(i) for i in box]) + ".jpg"
region.save(os.path.join(PWD, new_filename))
