#!/usr/bin/env python
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)
file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp=file_path)

#new_im = im.transpose(Image.FLIP_LEFT_RIGHT)
#new_filename = os.path.splitext(filepath)[0] + "flip_left_right" + ".jpg"

new_im = im.transpose(Image.FLIP_TOP_BOTTOM)
new_filename = os.path.splitext(os.path.basename(file_path))[0] + '-' + "flip_top_bottom" + ".jpg"

new_im.save(os.path.join(PWD, new_filename))
