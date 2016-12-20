#!/usr/bin/env python
#
# The Python Imaging Library
# $Id$
#
# this demo script creates four windows containing an image and a slider.
# drag the slider to modify the image.
#

import sys

if sys.version_info[0] > 2:
    import tkinter
else:
    import Tkinter as tkinter

from PIL import Image, ImageTk, ImageEnhance

#
# enhancer widget


class Enhance(tkinter.Frame):
    def __init__(self, master, image, name, enhancer, lo, hi):
        tkinter.Frame.__init__(self, master)

        # set up the image
        self.tkim = ImageTk.PhotoImage(image.mode, image.size)
        self.enhancer = enhancer(image)
        self.update("1.0")  # normalize

        # image window
        tkinter.Label(self, image=self.tkim).pack()

        # scale
        s = tkinter.Scale(self, label=name, orient=tkinter.HORIZONTAL,
                  from_=lo, to=hi, resolution=0.01,
                  command=self.update)
        s.set(self.value)
        s.pack()

    def update(self, value):
        self.value = float(value)
        self.tkim.paste(self.enhancer.enhance(self.value))

#
# main

if len(sys.argv) != 2:
    print("Usage: enhancer file")
    sys.exit(1)

root = tkinter.Tk()

im = Image.open(sys.argv[1])

im.thumbnail((200, 200))

Enhance(root, im, "Color", ImageEnhance.Color, 0.0, 4.0).pack()
Enhance(tkinter.Toplevel(), im, "Sharpness", ImageEnhance.Sharpness, -2.0, 2.0).pack()
Enhance(tkinter.Toplevel(), im, "Brightness", ImageEnhance.Brightness, -1.0, 3.0).pack()
Enhance(tkinter.Toplevel(), im, "Contrast", ImageEnhance.Contrast, -1.0, 3.0).pack()

root.mainloop()
