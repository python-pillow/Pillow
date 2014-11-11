#
# The Python Imaging Library.
# $Id$
#
# transform wrappers
#
# History:
# 2002-04-08 fl   Created
#
# Copyright (c) 2002 by Secret Labs AB
# Copyright (c) 2002 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

from PIL import Image


class Transform(Image.ImageTransformHandler):
    def __init__(self, data):
        self.data = data

    def getdata(self):
        return self.method, self.data

    def transform(self, size, image, **options):
        # can be overridden
        method, data = self.getdata()
        return image.transform(size, method, data, **options)


##
# Define an affine image transform.
# <p>
# This function takes a 6-tuple (<i>a, b, c, d, e, f</i>) which
# contain the first two rows from an affine transform matrix. For
# each pixel (<i>x, y</i>) in the output image, the new value is
# taken from a position (a <i>x</i> + b <i>y</i> + c,
# d <i>x</i> + e <i>y</i> + f) in the input image, rounded to
# nearest pixel.
# <p>
# This function can be used to scale, translate, rotate, and shear the
# original image.
#
# @def AffineTransform(matrix)
# @param matrix A 6-tuple (<i>a, b, c, d, e, f</i>) containing
#    the first two rows from an affine transform matrix.
# @see Image#Image.transform


class AffineTransform(Transform):
    method = Image.AFFINE


##
# Define a transform to extract a subregion from an image.
# <p>
# Maps a rectangle (defined by two corners) from the image to a
# rectangle of the given size.  The resulting image will contain
# data sampled from between the corners, such that (<i>x0, y0</i>)
# in the input image will end up at (0,0) in the output image,
# and (<i>x1, y1</i>) at <i>size</i>.
# <p>
# This method can be used to crop, stretch, shrink, or mirror an
# arbitrary rectangle in the current image. It is slightly slower than
# <b>crop</b>, but about as fast as a corresponding <b>resize</b>
# operation.
#
# @def ExtentTransform(bbox)
# @param bbox A 4-tuple (<i>x0, y0, x1, y1</i>) which specifies
#    two points in the input image's coordinate system.
# @see Image#Image.transform

class ExtentTransform(Transform):
    method = Image.EXTENT


##
# Define an quad image transform.
# <p>
# Maps a quadrilateral (a region defined by four corners) from the
# image to a rectangle of the given size.
#
# @def QuadTransform(xy)
# @param xy An 8-tuple (<i>x0, y0, x1, y1, x2, y2, y3, y3</i>) which
#   contain the upper left, lower left, lower right, and upper right
#   corner of the source quadrilateral.
# @see Image#Image.transform

class QuadTransform(Transform):
    method = Image.QUAD


##
# Define an mesh image transform.  A mesh transform consists of one
# or more individual quad transforms.
#
# @def MeshTransform(data)
# @param data A list of (bbox, quad) tuples.
# @see Image#Image.transform

class MeshTransform(Transform):
    method = Image.MESH
