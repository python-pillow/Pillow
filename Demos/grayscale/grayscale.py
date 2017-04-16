#!/usr/bin/env python
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

file_path = os.path.join(parent_path, "image_resources", "captcha.jpg")

im = Image.open(fp=file_path)

# "L" (8-bit pixels, black and white)
# http://www.pythonware.com/library/pil/handbook/concepts.htm
new_im = im.convert("L")
new_file_name = os.path.splitext(os.path.basename(file_path))[0]
new_file_name = new_file_name + '-' + 'grayscale' + '.bmp'

new_im.save(os.path.join(PWD, new_file_name))

