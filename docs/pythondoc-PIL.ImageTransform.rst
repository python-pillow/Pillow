=============================
The PIL.ImageTransform Module
=============================

The PIL.ImageTransform Module
=============================

**AffineTransform** (class)
[`# <#PIL.ImageTransform.AffineTransform-class>`_]
    Define an affine image transform.

    *matrix*
        A 6-tuple (*a, b, c, d, e, f*) containing the first two rows
        from an affine transform matrix.

    For more information about this class, see `*The AffineTransform
    Class* <#PIL.ImageTransform.AffineTransform-class>`_.

**ExtentTransform** (class)
[`# <#PIL.ImageTransform.ExtentTransform-class>`_]
    Define a transform to extract a subregion from an image.

    *bbox*
        A 4-tuple (*x0, y0, x1, y1*) which specifies two points in the
        input image's coordinate system.

    For more information about this class, see `*The ExtentTransform
    Class* <#PIL.ImageTransform.ExtentTransform-class>`_.

**MeshTransform** (class)
[`# <#PIL.ImageTransform.MeshTransform-class>`_]
    Define an mesh image transform.

    *data*

    For more information about this class, see `*The MeshTransform
    Class* <#PIL.ImageTransform.MeshTransform-class>`_.

**QuadTransform** (class)
[`# <#PIL.ImageTransform.QuadTransform-class>`_]
    Define an quad image transform.

    *xy*
        An 8-tuple (*x0, y0, x1, y1, x2, y2, y3, y3*) which contain the
        upper left, lower left, lower right, and upper right corner of
        the source quadrilateral.

    For more information about this class, see `*The QuadTransform
    Class* <#PIL.ImageTransform.QuadTransform-class>`_.

The AffineTransform Class
-------------------------

**AffineTransform** (class)
[`# <#PIL.ImageTransform.AffineTransform-class>`_]
    Define an affine image transform.

    This function takes a 6-tuple (*a, b, c, d, e, f*) which contain the
    first two rows from an affine transform matrix. For each pixel (*x,
    y*) in the output image, the new value is taken from a position (a
    *x* + b *y* + c, d *x* + e *y* + f) in the input image, rounded to
    nearest pixel.

    This function can be used to scale, translate, rotate, and shear the
    original image.

    *matrix*
        A 6-tuple (*a, b, c, d, e, f*) containing the first two rows
        from an affine transform matrix.

The ExtentTransform Class
-------------------------

**ExtentTransform** (class)
[`# <#PIL.ImageTransform.ExtentTransform-class>`_]
    Define a transform to extract a subregion from an image.

    Maps a rectangle (defined by two corners) from the image to a
    rectangle of the given size. The resulting image will contain data
    sampled from between the corners, such that (*x0, y0*) in the input
    image will end up at (0,0) in the output image, and (*x1, y1*) at
    *size*.

    This method can be used to crop, stretch, shrink, or mirror an
    arbitrary rectangle in the current image. It is slightly slower than
    **crop**, but about as fast as a corresponding **resize** operation.

    *bbox*
        A 4-tuple (*x0, y0, x1, y1*) which specifies two points in the
        input image's coordinate system.

The MeshTransform Class
-----------------------

**MeshTransform** (class)
[`# <#PIL.ImageTransform.MeshTransform-class>`_]

    *data*

The QuadTransform Class
-----------------------

**QuadTransform** (class)
[`# <#PIL.ImageTransform.QuadTransform-class>`_]
    Define an quad image transform.

    Maps a quadrilateral (a region defined by four corners) from the
    image to a rectangle of the given size.

    *xy*
        An 8-tuple (*x0, y0, x1, y1, x2, y2, y3, y3*) which contain the
        upper left, lower left, lower right, and upper right corner of
        the source quadrilateral.

