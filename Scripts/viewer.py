#!/usr/bin/env python
#
# The Python Imaging Library
# $Id$
#

from __future__ import print_function

import sys

if sys.version_info[0] > 2:
    import tkinter
else:
    import Tkinter as tkinter

from PIL import Image, ImageTk

#
# an image viewer


class UI(tkinter.Label):

    def __init__(self, master, im):

        if im.mode == "1":
            # bitmap image
            self.image = ImageTk.BitmapImage(im, foreground="white")
            tkinter.Label.__init__(self, master, image=self.image, bd=0,
                                   bg="black")

        else:
            # photo image
            self.image = ImageTk.PhotoImage(im)
            tkinter.Label.__init__(self, master, image=self.image, bd=0)

#
# script interface

if __name__ == "__main__":

    if not sys.argv[1:]:
        print("Syntax: python viewer.py imagefile")
        sys.exit(1)

    filename = sys.argv[1]

    root = tkinter.Tk()
    root.title(filename)

    im = Image.open(filename)

    UI(root, im).pack()

    root.mainloop()
