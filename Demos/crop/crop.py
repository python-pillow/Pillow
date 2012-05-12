#!/usr/bin/env python
import os
PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

import Image

file_path = os.path.join(parent_path, "image_resources", "l_hires.jpg")

im = Image.open(fp = file_path)

left_upper_x, left_upper_y = 400, 100
right_lower_x, right_lower_y = 700, 450
box = (left_upper_x, left_upper_y, right_lower_x, right_lower_y)

region = im.crop(box)

new_filename = "x".join([str(i) for i in box]) + ".jpg"
region.save(new_filename)
