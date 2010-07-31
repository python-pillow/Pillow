#
# The Python Imaging Library
# $Id$
#

from Tkinter import *
from PIL import Image, ImageTk

#
# an image viewer

class UI(Label):

    def __init__(self, master, im):

        if im.mode == "1":
            # bitmap image
            self.image = ImageTk.BitmapImage(im, foreground="white")
            Label.__init__(self, master, image=self.image, bg="black", bd=0)

        else:
            # photo image
            self.image = ImageTk.PhotoImage(im)
            Label.__init__(self, master, image=self.image, bd=0)

#
# script interface

if __name__ == "__main__":

    import sys

    if not sys.argv[1:]:
        print "Syntax: python viewer.py imagefile"
        sys.exit(1)

    filename = sys.argv[1]

    root = Tk()
    root.title(filename)

    im = Image.open(filename)

    UI(root, im).pack()

    root.mainloop()
