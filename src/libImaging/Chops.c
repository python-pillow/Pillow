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

#define CHOP(operation)                                 \
    int x, y;                                           \
    Imaging imOut;                                      \
    imOut = create(imIn1, imIn2, IMAGING_MODE_UNKNOWN); \
    if (!imOut) {                                       \
        return NULL;                                    \
    }                                                   \
    for (y = 0; y < imOut->ysize; y++) {                \
        UINT8 *out = (UINT8 *)imOut->image[y];          \
        UINT8 *in1 = (UINT8 *)imIn1->image[y];          \
        UINT8 *in2 = (UINT8 *)imIn2->image[y];          \
        for (x = 0; x < imOut->linesize; x++) {         \
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

#define CHOP2(operation, mode)                  \
    int x, y;                                   \
    Imaging imOut;                              \
    imOut = create(imIn1, imIn2, mode);         \
    if (!imOut) {                               \
        return NULL;                            \
    }                                           \
    for (y = 0; y < imOut->ysize; y++) {        \
        UINT8 *out = (UINT8 *)imOut->image[y];  \
        UINT8 *in1 = (UINT8 *)imIn1->image[y];  \
        UINT8 *in2 = (UINT8 *)imIn2->image[y];  \
        for (x = 0; x < imOut->linesize; x++) { \
            out[x] = operation;                 \
        }                                       \
    }                                           \
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

Imaging
ImagingChopLighter(Imaging imIn1, Imaging imIn2) {
    CHOP((in1[x] > in2[x]) ? in1[x] : in2[x]);
}

Imaging
ImagingChopDarker(Imaging imIn1, Imaging imIn2) {
    CHOP((in1[x] < in2[x]) ? in1[x] : in2[x]);
}

Imaging
ImagingChopDifference(Imaging imIn1, Imaging imIn2) {
    CHOP(abs((int)in1[x] - (int)in2[x]));
}

Imaging
ImagingChopMultiply(Imaging imIn1, Imaging imIn2) {
    CHOP((int)in1[x] * (int)in2[x] / 255);
}

Imaging
ImagingChopScreen(Imaging imIn1, Imaging imIn2) {
    CHOP(255 - ((int)(255 - in1[x]) * (int)(255 - in2[x])) / 255);
}

Imaging
ImagingChopAdd(Imaging imIn1, Imaging imIn2, float scale, int offset) {
    CHOP(((int)in1[x] + (int)in2[x]) / scale + offset);
}

Imaging
ImagingChopSubtract(Imaging imIn1, Imaging imIn2, float scale, int offset) {
    CHOP(((int)in1[x] - (int)in2[x]) / scale + offset);
}

Imaging
ImagingChopAnd(Imaging imIn1, Imaging imIn2) {
    CHOP2((in1[x] && in2[x]) ? 255 : 0, IMAGING_MODE_1);
}

Imaging
ImagingChopOr(Imaging imIn1, Imaging imIn2) {
    CHOP2((in1[x] || in2[x]) ? 255 : 0, IMAGING_MODE_1);
}

Imaging
ImagingChopXor(Imaging imIn1, Imaging imIn2) {
    CHOP2(((in1[x] != 0) ^ (in2[x] != 0)) ? 255 : 0, IMAGING_MODE_1);
}

Imaging
ImagingChopAddModulo(Imaging imIn1, Imaging imIn2) {
    CHOP2(in1[x] + in2[x], IMAGING_MODE_UNKNOWN);
}

Imaging
ImagingChopSubtractModulo(Imaging imIn1, Imaging imIn2) {
    CHOP2(in1[x] - in2[x], IMAGING_MODE_UNKNOWN);
}

Imaging
ImagingChopSoftLight(Imaging imIn1, Imaging imIn2) {
    CHOP2(
        (((255 - in1[x]) * (in1[x] * in2[x])) / 65536) +
            (in1[x] * (255 - ((255 - in1[x]) * (255 - in2[x]) / 255))) / 255,
        IMAGING_MODE_UNKNOWN
    );
}

Imaging
ImagingChopHardLight(Imaging imIn1, Imaging imIn2) {
    CHOP2(
        (in2[x] < 128) ? ((in1[x] * in2[x]) / 127)
                       : 255 - (((255 - in2[x]) * (255 - in1[x])) / 127),
        IMAGING_MODE_UNKNOWN
    );
}

Imaging
ImagingOverlay(Imaging imIn1, Imaging imIn2) {
    CHOP2(
        (in1[x] < 128) ? ((in1[x] * in2[x]) / 127)
                       : 255 - (((255 - in1[x]) * (255 - in2[x])) / 127),
        IMAGING_MODE_UNKNOWN
    );
}
