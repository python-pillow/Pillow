#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import sys

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

BLACK = "#000000"
WHITE = "#ffffff"

canvas_w, canvas_h = 250, 50
im = Image.new(mode="RGB", size=(canvas_w, canvas_h), color=WHITE)

draw = ImageDraw.Draw(im=im)

left_top_x, left_top_y = 10, 10
begin = left_top_x, left_top_y

text = u"hello world 中文"

if sys.platform == "darwin":
    filename = "/Library/Fonts/Microsoft/Times New Roman Bold.ttf"
elif sys.platform == "win32":
    filename = "timesbd.ttf"
elif sys.platform == "linux2":
    # this script required wqy truetype font,
    # install it on Debian/Ubuntu: apt-get install ttf-wqy-microhei
    filename = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
else:
    raise NotImplementedError
    
font_size = 26
font = ImageFont.truetype(filename=filename, size=font_size)

draw.text(xy=begin, text=text, fill=BLACK, font=font)

im.save(os.path.join(PWD, "draw_text.bmp"))
