/*
 * The Python Imaging Library
 * $Id$
 *
 * cut region from image
 *
 * history:
 * 95-11-27 fl Created
 * 98-07-10 fl Fixed "null result" error
 * 99-02-05 fl Rewritten to use Paste primitive
 *
 * Copyright (c) Secret Labs AB 1997-99.
 * Copyright (c) Fredrik Lundh 1995.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

Imaging
ImagingCrop(Imaging imIn, int sx0, int sy0, int sx1, int sy1) {
    Imaging imOut;
    int xsize, ysize;
    int dx0, dy0, dx1, dy1;
    INT32 zero = 0;

    if (!imIn) {
        return (Imaging)ImagingError_ModeError();
    }

    xsize = sx1 - sx0;
    if (xsize < 0) {
        xsize = 0;
    }
    ysize = sy1 - sy0;
    if (ysize < 0) {
        ysize = 0;
    }

    imOut = ImagingNewDirty(imIn->mode, xsize, ysize);
    if (!imOut) {
        return NULL;
    }

    ImagingCopyPalette(imOut, imIn);

    if (sx0 < 0 || sy0 < 0 || sx1 > imIn->xsize || sy1 > imIn->ysize) {
        (void)ImagingFill(imOut, &zero);
    }

    dx0 = -sx0;
    dy0 = -sy0;
    dx1 = imIn->xsize - sx0;
    dy1 = imIn->ysize - sy0;

    /* paste the source image on top of the output image!!! */
    if (ImagingPaste(imOut, imIn, NULL, dx0, dy0, dx1, dy1) < 0) {
        ImagingDelete(imOut);
        return NULL;
    }

    return imOut;
}
