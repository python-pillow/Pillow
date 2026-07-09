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
    if (!im) {
        return (Imaging)ImagingError_ValueError(NULL);
    }

    int xsize = im->xsize, ysize = im->ysize;

    Imaging imOut = ImagingNewDirty(im->mode, xsize, ysize);
    if (!imOut) {
        return NULL;
    }

    ImagingCopyPalette(imOut, im);

    if (xsize == 0 || ysize == 0) {
        return imOut;
    }

    xoffset %= xsize;
    if (xoffset < 0) {
        xoffset += xsize;
    }

    yoffset %= ysize;
    if (yoffset < 0) {
        yoffset += ysize;
    }

    int head = xoffset * im->pixelsize;
    int tail = im->linesize - head;

    // Restrict safe: im is read-only, imOut is write-only and a new allocation.
    for (int y = 0; y < ysize; y++) {
        int yi = y - yoffset;
        if (yi < 0) {
            yi += ysize;
        }
        const char *restrict in = im->image[yi];
        char *restrict out = imOut->image[y];
        memcpy(out, in + tail, head);
        memcpy(out + head, in, tail);
    }

    return imOut;
}
