#!/usr/bin/env python
#
# The Python Imaging Library
# $Id$
#

from __future__ import print_function

try:
    from tkinter import *
except ImportError:
    from Tkinter import *

from PIL import Image, ImageTk
import sys


Image.DEBUG = 0


# --------------------------------------------------------------------
# an image animation player

class UI(Label):

    def __init__(self, master, im):
        if isinstance(im, list):
            # list of images
            self.im = im[1:]
            im = self.im[0]
        else:
            # sequence
            self.im = im

        if im.mode == "1":
            self.image = ImageTk.BitmapImage(im, foreground="white")
        else:
            self.image = ImageTk.PhotoImage(im)

        Label.__init__(self, master, image=self.image, bg="black", bd=0)

        self.update()

        try:
            duration = im.info["duration"]
        except KeyError:
            duration = 100
        self.after(duration, self.next)

    def next(self):

        if isinstance(self.im, list):

            try:
                im = self.im[0]
                del self.im[0]
                self.image.paste(im)
            except IndexError:
                return # end of list

        else:

            try:
                im = self.im
                im.seek(im.tell() + 1)
                self.image.paste(im)
            except EOFError:
                return # end of file

        try:
            duration = im.info["duration"]
        except KeyError:
            duration = 100
        self.after(duration, self.next)

        self.update_idletasks()


# --------------------------------------------------------------------
# script interface

if __name__ == "__main__":

    if not sys.argv[1:]:
        print("Syntax: python player.py imagefile(s)")
        sys.exit(1)

    filename = sys.argv[1]

    root = Tk()
    root.title(filename)

    if len(sys.argv) > 2:
        # list of images
        print("loading...")
        im = []
        for filename in sys.argv[1:]:
            im.append(Image.open(filename))
    else:
        # sequence
        im = Image.open(filename)

    UI(root, im).pack()

    root.mainloop()
