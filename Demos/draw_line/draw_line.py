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

left_top_x, left_top_y = 10, 10
right_bottom_x, right_bottom_y = 30, 100
box = (left_top_x, left_top_y, right_bottom_x, right_bottom_y)

draw.line(xy = box, fill = fg_color, width = 1)

im.save("draw_line.jpeg")
