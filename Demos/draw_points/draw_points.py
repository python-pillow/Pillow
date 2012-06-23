#!/usr/bin/env python
import Image
import ImageDraw


BLACK = "#000000"
WHITE = "#ffffff"

fg_color = BLACK
bg_color = WHITE


canvas_w, canvas_h = 100, 100
im = Image.new(mode = "RGB", size = (canvas_w, canvas_h), color = bg_color)

draw = ImageDraw.Draw(im = im)

#xy = (p1_x, p1_y)
#or
#xy = (p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)

points = ((10, 10), (40, 10), (55, 35), (40,50))
for point in points:
    draw.point(xy = point, fill = fg_color)

im.save("draw_points.jpeg")
