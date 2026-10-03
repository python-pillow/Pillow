/*
 * The Python Imaging Library
 * $Id$
 *
 * copy image
 *
 * history:
 * 95-11-26 fl   Moved from Imaging.c
 * 97-05-12 fl   Added ImagingCopy2
 * 97-08-28 fl   Allow imOut == NULL in ImagingCopy2
 *
 * Copyright (c) Fredrik Lundh 1995-97.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

/**
 * Copy imIn into imOut.
 * This internal function requires that imOut matches imIn in mode and size.
 *
 * @param imOut Caller-owned image to copy into.
 * @param imIn Image to copy from.
 */
static void
_copy(Imaging imOut, Imaging imIn) {
    ImagingSectionCookie cookie;
    int y;

    ImagingCopyPalette(imOut, imIn);

    ImagingSectionEnter(&cookie);
    if (imIn->block != NULL && imOut->block != NULL) {
        memcpy(imOut->block, imIn->block, (size_t)imIn->ysize * imIn->linesize);
    } else {
        for (y = 0; y < imIn->ysize; y++) {
            memcpy(imOut->image[y], imIn->image[y], imIn->linesize);
        }
    }
    ImagingSectionLeave(&cookie);
}

/**
 * Create a new image by copying imIn. The caller owns the returned image.
 *
 * The new image is allocated with the current default allocation strategy.
 *
 * @param imIn Image to copy from.
 * @return A new image on success, or NULL on error with a Python exception set.
 */
Imaging
ImagingCopy(Imaging imIn) {
    if (!imIn) {
        return (Imaging)ImagingError_ValueError(NULL);
    }

    Imaging imOut = ImagingNewDirty(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut) {
        return NULL;
    }

    _copy(imOut, imIn);
    return imOut;
}

/**
 * Copy imIn into the caller-owned imOut, which must match it in mode and size.
 *
 * @param imOut Caller-owned image to copy into.
 * @param imIn Image to copy from.
 * @return imOut on success, or NULL on error with a Python exception set.
 */
Imaging
ImagingCopyInto(Imaging imOut, Imaging imIn) {
    if (!imIn || !imOut) {
        return (Imaging)ImagingError_ValueError(NULL);
    }

    if (imOut->mode != imIn->mode || imOut->xsize != imIn->xsize ||
        imOut->ysize != imIn->ysize) {
        return ImagingError_Mismatch();
    }

    _copy(imOut, imIn);
    return imOut;
}
