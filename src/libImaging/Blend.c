/*
 * The Python Imaging Library
 * $Id$
 *
 * interpolate between two existing images
 *
 * history:
 * 96-03-20 fl Created
 * 96-05-18 fl Simplified blend expression
 * 96-10-05 fl Fixed expression bug, special case for interpolation
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

/**
 * Interpolate (or, for alpha outside [0, 1], extrapolate) between imIn1 and
 * imIn2 by `alpha`, returning a newly allocated result.
 *
 * Contract: imIn1 and imIn2 are read-only and may alias each other.
 */
Imaging
ImagingBlend(Imaging imIn1, Imaging imIn2, float alpha) {
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imIn1 || !imIn2) {
        return ImagingError_ValueError(NULL);
    }
    if (imIn1->type != IMAGING_TYPE_UINT8 && imIn1->type != IMAGING_TYPE_I16) {
        return ImagingError_NotSupportedError("only 8-bit and I;16 images supported");
    }
    if (imIn1->palette || imIn1->mode == IMAGING_MODE_1) {
        return ImagingError_NotSupportedError("modes P, PA and 1 not supported");
    }

    if (imIn1->mode != imIn2->mode || imIn1->xsize != imIn2->xsize ||
        imIn1->ysize != imIn2->ysize) {
        return ImagingError_Mismatch("images must have the same mode and size");
    }

    /* Shortcuts */
    if (imIn1 == imIn2 || alpha == 0.0) {
        return ImagingCopy(imIn1);
    } else if (alpha == 1.0) {
        return ImagingCopy(imIn2);
    }

    imOut = ImagingNewDirty(imIn1->mode, imIn1->xsize, imIn1->ysize);
    if (!imOut) {
        return NULL;
    }

    int ysize = imIn1->ysize;
    if (imIn1->type == IMAGING_TYPE_UINT8) {
        int linesize = imIn1->linesize;
        if (alpha >= 0 && alpha <= 1.0) {
            /* Interpolate between bands */
            for (y = 0; y < ysize; y++) {
                // restrict safe: imIn1 and imIn2 are read-only; imOut is a new
                // allocation
                UINT8 *restrict in1 = (UINT8 *)imIn1->image[y];
                UINT8 *restrict in2 = (UINT8 *)imIn2->image[y];
                UINT8 *restrict out = (UINT8 *)imOut->image[y];
                for (x = 0; x < linesize; x++) {
                    out[x] = (UINT8)roundf(
                        (int)in1[x] + alpha * ((int)in2[x] - (int)in1[x])
                    );
                }
            }
        } else {
            /* Extrapolation; must make sure to clip resulting values */
            for (y = 0; y < ysize; y++) {
                // restrict safe: imIn1 and imIn2 are read-only; imOut is a new
                // allocation
                UINT8 *restrict in1 = (UINT8 *)imIn1->image[y];
                UINT8 *restrict in2 = (UINT8 *)imIn2->image[y];
                UINT8 *restrict out = (UINT8 *)imOut->image[y];
                for (x = 0; x < linesize; x++) {
                    out[x] = (UINT8)CLIP8(
                        roundf((int)in1[x] + alpha * ((int)in2[x] - (int)in1[x]))
                    );
                }
            }
        }
    } else if (imIn1->type == IMAGING_TYPE_I16) {
        int xsize = imIn1->xsize;
        int bigendian = isImageI16BigEndian(imIn1);

        if (alpha >= 0 && alpha <= 1.0) {
            for (y = 0; y < ysize; y++) {
                UINT8 *restrict in1 = (UINT8 *)imIn1->image[y];
                UINT8 *restrict in2 = (UINT8 *)imIn2->image[y];
                UINT8 *restrict out = (UINT8 *)imOut->image[y];
                for (x = 0; x < xsize; x++) {
                    float v1 = (int)in1[x * 2 + (bigendian ? 1 : 0)] +
                               ((int)in1[x * 2 + (bigendian ? 0 : 1)] << 8);
                    float v2 = (int)in2[x * 2 + (bigendian ? 1 : 0)] +
                               ((int)in2[x * 2 + (bigendian ? 0 : 1)] << 8);
                    UINT16 v = roundf(v1 + alpha * (v2 - v1));
                    out[x * 2 + (bigendian ? 1 : 0)] = (UINT8)(v & 0xff);
                    out[x * 2 + (bigendian ? 0 : 1)] = (UINT8)(v >> 8);
                }
            }
        } else {
            /* Extrapolation; must make sure to clip resulting values */
            for (y = 0; y < ysize; y++) {
                UINT8 *restrict in1 = (UINT8 *)imIn1->image[y];
                UINT8 *restrict in2 = (UINT8 *)imIn2->image[y];
                UINT8 *restrict out = (UINT8 *)imOut->image[y];
                for (x = 0; x < xsize; x++) {
                    float v1 = (int)in1[x * 2 + (bigendian ? 1 : 0)] +
                               ((int)in1[x * 2 + (bigendian ? 0 : 1)] << 8);
                    float v2 = (int)in2[x * 2 + (bigendian ? 1 : 0)] +
                               ((int)in2[x * 2 + (bigendian ? 0 : 1)] << 8);
                    UINT16 v = CLIP16(roundf(v1 + alpha * (v2 - v1)));
                    out[x * 2 + (bigendian ? 1 : 0)] = (UINT8)(v & 0xff);
                    out[x * 2 + (bigendian ? 0 : 1)] = (UINT8)(v >> 8);
                }
            }
        }
    }

    return imOut;
}
