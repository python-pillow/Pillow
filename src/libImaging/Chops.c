/*
 * The Python Imaging Library
 * $Id$
 *
 * basic channel operations
 *
 * history:
 * 1996-03-28 fl   Created
 * 1996-08-13 fl   Added and/or/xor for "1" images
 * 1996-12-14 fl   Added add_modulo, sub_modulo
 * 2005-09-10 fl   Fixed output values from and/or/xor
 *
 * Copyright (c) 1996 by Fredrik Lundh.
 * Copyright (c) 1997 by Secret Labs AB.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

// restrict safety: imIn1/imIn2 are read-only, and imOut is always freshly allocated
#define CHOP(operation)                                 \
    int x, y;                                           \
    Imaging imOut;                                      \
    imOut = create(imIn1, imIn2, IMAGING_MODE_UNKNOWN); \
    if (!imOut) {                                       \
        return NULL;                                    \
    }                                                   \
    int ysize = imOut->ysize;                           \
    int linesize = imOut->linesize;                     \
    for (y = 0; y < ysize; y++) {                       \
        UINT8 *restrict out = (UINT8 *)imOut->image[y]; \
        UINT8 *restrict in1 = (UINT8 *)imIn1->image[y]; \
        UINT8 *restrict in2 = (UINT8 *)imIn2->image[y]; \
        for (x = 0; x < linesize; x++) {                \
            int temp = operation;                       \
            if (temp <= 0) {                            \
                out[x] = 0;                             \
            } else if (temp >= 255) {                   \
                out[x] = 255;                           \
            } else {                                    \
                out[x] = temp;                          \
            }                                           \
        }                                               \
    }                                                   \
    return imOut;

// restrict safety: imIn1/imIn2 are read-only, and imOut is always freshly allocated
#define CHOP2(operation, mode)                          \
    int x, y;                                           \
    Imaging imOut;                                      \
    imOut = create(imIn1, imIn2, mode);                 \
    if (!imOut) {                                       \
        return NULL;                                    \
    }                                                   \
    int ysize = imOut->ysize;                           \
    int linesize = imOut->linesize;                     \
    for (y = 0; y < ysize; y++) {                       \
        UINT8 *restrict out = (UINT8 *)imOut->image[y]; \
        UINT8 *restrict in1 = (UINT8 *)imIn1->image[y]; \
        UINT8 *restrict in2 = (UINT8 *)imIn2->image[y]; \
        for (x = 0; x < linesize; x++) {                \
            out[x] = operation;                         \
        }                                               \
    }                                                   \
    return imOut;

static Imaging
create(Imaging im1, Imaging im2, const ModeID mode) {
    int xsize, ysize;

    if (!im1 || !im2 || im1->type != IMAGING_TYPE_UINT8 ||
        (mode != IMAGING_MODE_UNKNOWN &&
         (im1->mode != IMAGING_MODE_1 || im2->mode != IMAGING_MODE_1))) {
        return (Imaging)ImagingError_ModeError();
    }
    if (im1->type != im2->type || im1->bands != im2->bands) {
        return (Imaging)ImagingError_Mismatch();
    }

    xsize = (im1->xsize < im2->xsize) ? im1->xsize : im2->xsize;
    ysize = (im1->ysize < im2->ysize) ? im1->ysize : im2->ysize;

    return ImagingNewDirty(im1->mode, xsize, ysize);
}

/**
 * Return a newly allocated image containing the lighter pixels of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopLighter(Imaging imIn1, Imaging imIn2) {
    CHOP((in1[x] > in2[x]) ? in1[x] : in2[x]);
}

/**
 * Return a newly allocated image containing the darker pixels of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopDarker(Imaging imIn1, Imaging imIn2) {
    CHOP((in1[x] < in2[x]) ? in1[x] : in2[x]);
}

/**
 * Return a newly allocated image containing the absolute per-pixel difference of the
 * two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopDifference(Imaging imIn1, Imaging imIn2) {
    CHOP(abs((int)in1[x] - (int)in2[x]));
}

/**
 * Return a newly allocated image containing the per-pixel product (scaled to 0-255) of
 * the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopMultiply(Imaging imIn1, Imaging imIn2) {
    CHOP((int)in1[x] * (int)in2[x] / 255);
}

/**
 * Return a newly allocated image containing the screen blend of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopScreen(Imaging imIn1, Imaging imIn2) {
    CHOP(255 - ((int)(255 - in1[x]) * (int)(255 - in2[x])) / 255);
}

/**
 * Return a newly allocated image containing the per-pixel sum, divided by `scale` and
 * shifted by `offset`, clipped to 0-255.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopAdd(Imaging imIn1, Imaging imIn2, float scale, int offset) {
    CHOP(((int)in1[x] + (int)in2[x]) / scale + offset);
}

/**
 * Return a newly allocated image containing the per-pixel difference, divided by
 * `scale` and shifted by `offset`, clipped to 0-255.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopSubtract(Imaging imIn1, Imaging imIn2, float scale, int offset) {
    CHOP(((int)in1[x] - (int)in2[x]) / scale + offset);
}

/**
 * Return a newly allocated "1" image that is the logical AND of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopAnd(Imaging imIn1, Imaging imIn2) {
    CHOP2((in1[x] && in2[x]) ? 255 : 0, IMAGING_MODE_1);
}

/**
 * Return a newly allocated "1" image that is the logical OR of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopOr(Imaging imIn1, Imaging imIn2) {
    CHOP2((in1[x] || in2[x]) ? 255 : 0, IMAGING_MODE_1);
}

/**
 * Return a newly allocated "1" image that is the logical XOR of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopXor(Imaging imIn1, Imaging imIn2) {
    CHOP2(((in1[x] != 0) ^ (in2[x] != 0)) ? 255 : 0, IMAGING_MODE_1);
}

/**
 * Return a newly allocated image containing the per-pixel sum of the two images,
 * wrapping on overflow (no clipping).
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopAddModulo(Imaging imIn1, Imaging imIn2) {
    CHOP2(in1[x] + in2[x], IMAGING_MODE_UNKNOWN);
}

/**
 * Return a newly allocated image containing the per-pixel difference of the two images,
 * wrapping on underflow (no clipping).
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopSubtractModulo(Imaging imIn1, Imaging imIn2) {
    CHOP2(in1[x] - in2[x], IMAGING_MODE_UNKNOWN);
}

/**
 * Return a newly allocated image containing the soft-light blend of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopSoftLight(Imaging imIn1, Imaging imIn2) {
    CHOP2(
        (((255 - in1[x]) * (in1[x] * in2[x])) / 65536) +
            (in1[x] * (255 - ((255 - in1[x]) * (255 - in2[x]) / 255))) / 255,
        IMAGING_MODE_UNKNOWN
    );
}

/**
 * Return a newly allocated image containing the hard-light blend of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingChopHardLight(Imaging imIn1, Imaging imIn2) {
    CHOP2(
        (in2[x] < 128) ? ((in1[x] * in2[x]) / 127)
                       : 255 - (((255 - in2[x]) * (255 - in1[x])) / 127),
        IMAGING_MODE_UNKNOWN
    );
}

/**
 * Return a newly allocated image containing the overlay blend of the two images.
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingOverlay(Imaging imIn1, Imaging imIn2) {
    CHOP2(
        (in1[x] < 128) ? ((in1[x] * in2[x]) / 127)
                       : 255 - (((255 - in1[x]) * (255 - in2[x])) / 127),
        IMAGING_MODE_UNKNOWN
    );
}
