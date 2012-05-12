#!/usr/bin/env python
import Image
import ImageDraw


BLACK = 0
WHITE = 255


canvas_w, canvas_h = 100, 100
im = Image.new(mode = "L", size = (canvas_w, canvas_h), color = WHITE)

draw = ImageDraw.Draw(im = im)

p1_x, p1_y = 10, 10
p2_x, p2_y = 15, 15
p3_x, p3_y = 20, 10

xy = (p1_x, p1_y)
# or
# xy = (p1_x, p1_y, p2_x, p2_y, p3_x, p3_y)


fill = "#000"

draw.point(xy, fill)

im.save("draw_points.bmp")
