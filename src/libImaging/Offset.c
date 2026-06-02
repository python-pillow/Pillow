/*
 * The Python Imaging Library
 * $Id$
 *
 * offset an image in x and y directions
 *
 * history:
 * 96-07-22 fl: Created
 * 98-11-01 cgw@pgt.com: Fixed negative-array index bug
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/**
 * Copy `im` into a newly allocated image,
 * wrapping every pixel by (xoffset, yoffset) modulo the image size.
 *
 * Contract: im is read-only.
 */
Imaging
ImagingOffset(Imaging im, int xoffset, int yoffset) {
    int x, y;
    Imaging imOut;

    if (!im) {
        return (Imaging)ImagingError_ModeError();
    }

    imOut = ImagingNewDirty(im->mode, im->xsize, im->ysize);
    if (!imOut) {
        return NULL;
    }

    ImagingCopyPalette(imOut, im);

    /* make offsets positive to avoid negative coordinates */
    xoffset %= im->xsize;
    xoffset = im->xsize - xoffset;
    if (xoffset < 0) {
        xoffset += im->xsize;
    }

    yoffset %= im->ysize;
    yoffset = im->ysize - yoffset;
    if (yoffset < 0) {
        yoffset += im->ysize;
    }

    // yi depends only on y, so compute it (and both row pointers) once per
    // row instead of redoing the modulo and pointer chase for every x.
#define OFFSET(type, image)                     \
    for (y = 0; y < im->ysize; y++) {           \
        int yi = (y + yoffset) % im->ysize;     \
        type *restrict in = im->image[yi];      \
        type *restrict out = imOut->image[y];   \
        for (x = 0; x < im->xsize; x++) {       \
            int xi = (x + xoffset) % im->xsize; \
            out[x] = in[xi];                    \
        }                                       \
    }

    if (im->image8) {
        OFFSET(UINT8, image8)
    } else {
        OFFSET(INT32, image32)
    }

    return imOut;
}
