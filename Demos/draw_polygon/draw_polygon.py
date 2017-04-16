#!/usr/bin/env python
import os
from PIL import Image
from PIL import ImageDraw


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

BLACK = "#000000"
WHITE = "#ffffff"
RED = "#ff0000"

canvas_w, canvas_h = 100, 100
im = Image.new(mode="RGB", size=(canvas_w, canvas_h), color=WHITE)

draw = ImageDraw.Draw(im=im)

#xy = (p1_x, p1_y)
#or
#xy = (p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)

xy = ((10, 10), (40, 10), (55, 35), (40,50))
draw.polygon(xy=xy, fill=RED, outline=BLACK)
im.save(os.path.join(PWD, "draw_polygon.jpg"))
