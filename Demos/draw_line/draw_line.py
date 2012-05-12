#!/usr/bin/env python
import Image
import ImageDraw

BLACK = 0
WHITE = 255


canvas_w, canvas_h = 100, 100
im = Image.new(mode = "L", size = (canvas_w, canvas_h), color = WHITE)

draw = ImageDraw.Draw(im = im)

left_top_x, left_top_y = 10, 10
right_bottom_x, right_bottom_y = 30, 100
box = (left_top_x, left_top_y, right_bottom_x, right_bottom_y)

draw.line(xy = box, fill = BLACK, width = 1)

im.save("draw_line.bmp")
