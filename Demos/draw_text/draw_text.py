#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageFont
import sys

BLACK = 0
WHITE = 255

canvas_w, canvas_h = 100, 100
im = Image.new(mode = "L", size = (canvas_w, canvas_h), color = WHITE)

draw = ImageDraw.Draw(im = im)

left_top_x, left_top_y = 10, 10
begin = left_top_x, left_top_y

text = "hello world"
fill = "#000"

if sys.platform == "darwin":
    filename = "/Library/Fonts/Microsoft/Times New Roman Bold.ttf"
elif sys.platform == "win32":
    #filename = "C:/Windows/Fonts/timesbd.ttf"
    filename = "timesbd.ttf"
else:
    raise Exception
font_size = 14
font = ImageFont.truetype(filename = filename, size = font_size)

draw.text(xy = begin, text = text, fill = fill, font = font)

im.save("draw_text.bmp")
