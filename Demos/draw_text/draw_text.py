#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageFont
import sys

BLACK = "#ffffff"
WHITE = "#000000"

fg_color = WHITE
bg_color = BLACK


canvas_w, canvas_h = 180, 50
im = Image.new(mode="RGB", size=(canvas_w, canvas_h), color=bg_color)

draw = ImageDraw.Draw(im=im)

left_top_x, left_top_y = 10, 10
begin = left_top_x, left_top_y

text = "hello world"

if sys.platform == "darwin":
    filename = "/Library/Fonts/Microsoft/Times New Roman Bold.ttf"
elif sys.platform == "win32":
    #filename = "C:/Windows/Fonts/timesbd.ttf"
    filename = "timesbd.ttf"
else:
    raise Exception
font_size = 26
font = ImageFont.truetype(filename=filename, size=font_size)

draw.text(xy=begin, text=text, fill=fg_color, font=font)

im.save("draw_text.bmp")
