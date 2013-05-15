#!/usr/bin/env python
#
# The Python Imaging Library
# $Id$
#
# this demo script illustrates how a 1-bit BitmapImage can be used
# as a dynamically updated overlay
#

try:
    from tkinter import *
except ImportError:
    from Tkinter import *

from PIL import Image, ImageTk
import sys

#
# an image viewer

class UI(Frame):
    def __init__(self, master, im, value = 128):
        Frame.__init__(self, master)

        self.image = im
        self.value = value

        self.canvas = Canvas(self, width=im.size[0], height=im.size[1])
        self.backdrop = ImageTk.PhotoImage(im)
        self.canvas.create_image(0, 0, image=self.backdrop, anchor=NW)
        self.canvas.pack()

        scale = Scale(self, orient=HORIZONTAL, from_=0, to=255,
                      resolution=1, command=self.update, length=256)
        scale.set(value)
        scale.bind("<ButtonRelease-1>", self.redraw)
        scale.pack()

        # uncomment the following line for instant feedback (might
        # be too slow on some platforms)
        # self.redraw()

    def update(self, value):
        self.value = eval(value)

        self.redraw()

    def redraw(self, event = None):

        # create overlay (note the explicit conversion to mode "1")
        im = self.image.point(lambda v,t=self.value: v>=t, "1")
        self.overlay = ImageTk.BitmapImage(im, foreground="green")

        # update canvas
        self.canvas.delete("overlay")
        self.canvas.create_image(0, 0, image=self.overlay, anchor=NW,
                tags="overlay")

# --------------------------------------------------------------------
# main

root = Tk()

im = Image.open(sys.argv[1])

if im.mode != "L":
    im = im.convert("L")

# im.thumbnail((320,200))

UI(root, im).pack()

root.mainloop()
