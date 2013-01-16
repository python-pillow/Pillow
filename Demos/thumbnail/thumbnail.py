#!/usr/bin/env python
import os
from PIL import Image


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

file_path = os.path.join(parent_path, "image_resources", 'captcha.jpg')
im = Image.open(fp=file_path)

width, height = im.size[0], im.size[1]
new_size = (width/4, height/4)

im.thumbnail(new_size)

new_filename= "x".join([str(i) for i in new_size])
new_filename = os.path.splitext(os.path.basename(file_path))[0] + '-' + new_filename + ".jpg"
new_file_path = os.path.join(PWD, new_filename)

im.save(os.path.join(PWD, new_filename))
