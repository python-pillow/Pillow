/*
 * The Python Imaging Library
 * $Id$
 *
 * negate image
 *
 * to do:
 *      FIXME: Maybe this should be implemented using ImagingPoint()
 *
 * history:
 * 95-11-27 fl: Created
 *
 * Copyright (c) Fredrik Lundh 1995.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

Imaging
ImagingNegative(Imaging im) {
    Imaging imOut;
    int x, y;

    if (!im) {
        return (Imaging)ImagingError_ModeError();
    }

    imOut = ImagingNewDirty(im->mode, im->xsize, im->ysize);
    if (!imOut) {
        return NULL;
    }

    for (y = 0; y < im->ysize; y++) {
        for (x = 0; x < im->linesize; x++) {
            imOut->image[y][x] = ~im->image[y][x];
        }
    }

    return imOut;
}
