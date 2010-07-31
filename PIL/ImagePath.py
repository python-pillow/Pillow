#
# The Python Imaging Library
# $Id$
#
# path interface
#
# History:
# 1996-11-04 fl   Created
# 2002-04-14 fl   Added documentation stub class
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#

import Image

##
# Path wrapper.

class Path:

    ##
    # Creates a path object.
    #
    # @param xy Sequence.  The sequence can contain 2-tuples [(x, y), ...]
    #     or a flat list of numbers [x, y, ...].

    def __init__(self, xy):
        pass

    ##
    # Compacts the path, by removing points that are close to each
    # other.  This method modifies the path in place.

    def compact(self, distance=2):
        pass

    ##
    # Gets the bounding box.

    def getbbox(self):
        pass

    ##
    # Maps the path through a function.

    def map(self, function):
        pass

    ##
    # Converts the path to Python list.
    #
    # @param flat By default, this function returns a list of 2-tuples
    #     [(x, y), ...].  If this argument is true, it returns a flat
    #     list [x, y, ...] instead.
    # @return A list of coordinates.

    def tolist(self, flat=0):
        pass

    ##
    # Transforms the path.

    def transform(self, matrix):
        pass


# override with C implementation
Path = Image.core.path
