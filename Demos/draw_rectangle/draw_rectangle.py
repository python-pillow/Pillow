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

left_top_x, left_top_y = 10, 10
right_bottom_x, right_bottom_y = 30, 100
box = (left_top_x, left_top_y, right_bottom_x, right_bottom_y)

draw.rectangle(xy = box, fill = fg_color, outline = None)

im.save("draw_rectangle.bmp")
