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

/**
 * Invert every byte of `im`, returning a newly allocated result.
 *
 * Contract: im is read-only.
 */
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

    // ysize and linesize are loop-invariant.
    int ysize = im->ysize, linesize = im->linesize;

    for (y = 0; y < ysize; y++) {
        // restrict safe: im is read-only, imOut is a fresh allocation.
        UINT8 *restrict in = (UINT8 *)im->image[y];
        UINT8 *restrict out = (UINT8 *)imOut->image[y];
        for (x = 0; x < linesize; x++) {
            out[x] = ~in[x];
        }
    }

    return imOut;
}
