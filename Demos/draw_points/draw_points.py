#!/usr/bin/env python
import Image
import ImageDraw

BLACK = "#ffffff"
WHITE = "#000000"

fg_color = WHITE
bg_color = BLACK


canvas_w, canvas_h = 100, 100
im = Image.new(mode = "RGB", size = (canvas_w, canvas_h), color = bg_color)

draw = ImageDraw.Draw(im = im)

#xy = (p1_x, p1_y)
#or
#xy = (p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)

y = 10
for x in range(5, 100):
    point = (x, y)
    draw.point(point, fg_color)

im.save("draw_points.png")
