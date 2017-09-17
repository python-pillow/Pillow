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


# --------------------------------------------------------------------
# an image animation player

class UI(tkinter.Label):

    def __init__(self, master, im):
        self.im = im
        if isinstance(self.im, list):
            # list of images
            im = self.im.pop(0)

        if im.mode == "1":
            self.image = ImageTk.BitmapImage(im, foreground="white")
        else:
            self.image = ImageTk.PhotoImage(im)

        tkinter.Label.__init__(self, master, image=self.image, bg="black", bd=0)

        self.update()

        duration = im.info.get("duration", 100)
        self.after(duration, self.next)

    def next(self):

        if isinstance(self.im, list):

            try:
                im = self.im[0]
                del self.im[0]
                self.image.paste(im)
            except IndexError:
                return  # end of list

        else:

            try:
                im = self.im
                im.seek(im.tell() + 1)
                self.image.paste(im)
            except EOFError:
                return  # end of file

        duration = im.info.get("duration", 100)
        self.after(duration, self.next)

        self.update_idletasks()


# --------------------------------------------------------------------
# script interface

if __name__ == "__main__":

    if not sys.argv[1:]:
        print("Syntax: python player.py imagefile(s)")
        sys.exit(1)

    filename = sys.argv[1]

    root = tkinter.Tk()
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
