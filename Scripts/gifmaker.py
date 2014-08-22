#!/usr/bin/env python
#
# The Python Imaging Library
# $Id$
#
# convert sequence format to GIF animation
#
# history:
#       97-01-03 fl     created
#
# Copyright (c) Secret Labs AB 1997.  All rights reserved.
# Copyright (c) Fredrik Lundh 1997.
#
# See the README file for information on usage and redistribution.
#

#
# For special purposes, you can import this module and call
# the makedelta or compress functions yourself.  For example,
# if you have an application that generates a sequence of
# images, you can convert it to a GIF animation using some-
# thing like the following code:
#
#       import Image
#       import gifmaker
#
#       sequence = []
#
#       # generate sequence
#       for i in range(100):
#           im = <generate image i>
#           sequence.append(im)
#
#       # write GIF animation
#       fp = open("out.gif", "wb")
#       gifmaker.makedelta(fp, sequence)
#       fp.close()
#
# Alternatively, use an iterator to generate the sequence, and
# write data directly to a socket.  Or something...
#

from __future__ import print_function

from PIL import Image, ImageChops

from PIL.GifImagePlugin import getheader, getdata

# --------------------------------------------------------------------
# sequence iterator

class image_sequence:
    def __init__(self, im):
        self.im = im
    def __getitem__(self, ix):
        try:
            if ix:
                self.im.seek(ix)
            return self.im
        except EOFError:
            raise IndexError # end of sequence

# --------------------------------------------------------------------
# straightforward delta encoding

def makedelta(fp, sequence):
    """Convert list of image frames to a GIF animation file"""

    frames = 0

    previous = None

    for im in sequence:

        #
        # FIXME: write graphics control block before each frame

        if not previous:

            # global header
            for s in getheader(im) + getdata(im):
                fp.write(s)

        else:

            # delta frame
            delta = ImageChops.subtract_modulo(im, previous)

            bbox = delta.getbbox()

            if bbox:

                # compress difference
                for s in getdata(im.crop(bbox), offset = bbox[:2]):
                    fp.write(s)

            else:
                # FIXME: what should we do in this case?
                pass

        previous = im.copy()

        frames += 1

    fp.write(";")

    return frames

# --------------------------------------------------------------------
# main hack

def compress(infile, outfile):

    # open input image, and force loading of first frame
    im = Image.open(infile)
    im.load()

    # open output file
    fp = open(outfile, "wb")

    seq = image_sequence(im)

    makedelta(fp, seq)

    fp.close()


if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:
        print("GIFMAKER -- create GIF animations")
        print("Usage: gifmaker infile outfile")
        sys.exit(1)

    compress(sys.argv[1], sys.argv[2])
