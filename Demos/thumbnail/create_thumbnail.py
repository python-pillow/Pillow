#!/usr/bin/env python
import os
PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

import Image

file_path = os.path.join(parent_path, "image_resources", 'l_hires.jpg')
im = Image.open(fp=file_path)

width, height = im.size[0], im.size[1]
new_size = (width/8, height/8)

im.thumbnail(new_size)

new_filename= "x".join([str(i) for i in new_size])
new_filename = os.path.splitext(os.path.basename(file_path))[0] + '-' + new_filename + ".jpg"
new_file_path = os.path.join(PWD, new_filename)

im.save(new_filename)
