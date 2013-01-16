#!/usr/bin/env python
import os
import sys

from PIL import Image, ImageDraw, ImageFont


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

BLACK = "#ffffff"
WHITE = "#000000"

fg_color = WHITE
bg_color = BLACK


canvas_w, canvas_h = 180, 50
im = Image.new(mode="RGB", size=(canvas_w, canvas_h), color=WHITE)

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

draw.text(xy=begin, text=text, fill=BLACK, font=font)

im.save(os.path.join(PWD, "draw_text.bmp"))
