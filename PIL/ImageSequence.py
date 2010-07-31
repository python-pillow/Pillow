#
# The Python Imaging Library.
# $Id$
#
# sequence support classes
#
# history:
# 1997-02-20 fl     Created
#
# Copyright (c) 1997 by Secret Labs AB.
# Copyright (c) 1997 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

##
# This class implements an iterator object that can be used to loop
# over an image sequence.

class Iterator:

    ##
    # Create an iterator.
    #
    # @param im An image object.

    def __init__(self, im):
        if not hasattr(im, "seek"):
            raise AttributeError("im must have seek method")
        self.im = im

    def __getitem__(self, ix):
        try:
            if ix:
                self.im.seek(ix)
            return self.im
        except EOFError:
            raise IndexError # end of sequence
