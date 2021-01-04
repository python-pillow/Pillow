/*
 * The Python Imaging Library
 * $Id$
 *
 * colour and luminance matrix transforms
 *
 * history:
 * 1996-05-18 fl:   created (brute force implementation)
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#define CLIPF(v) ((v <= 0.0) ? 0 : (v >= 255.0F) ? 255 : (UINT8)v)

Imaging
ImagingConvertMatrix(Imaging im, const char *mode, float m[]) {
    Imaging imOut;
    int x, y;

    /* Assume there's enough data in the buffer */
    if (!im) {
        return (Imaging)ImagingError_ModeError();
    }

    if (strcmp(mode, "L") == 0 && im->bands == 3) {
        imOut = ImagingNewDirty("L", im->xsize, im->ysize);
        if (!imOut) {
            return NULL;
        }

        for (y = 0; y < im->ysize; y++) {
            UINT8 *in = (UINT8 *)im->image[y];
            UINT8 *out = (UINT8 *)imOut->image[y];

            for (x = 0; x < im->xsize; x++) {
                float v = m[0] * in[0] + m[1] * in[1] + m[2] * in[2] + m[3] + 0.5;
                out[x] = CLIPF(v);
                in += 4;
            }
        }

    } else if (strlen(mode) == 3 && im->bands == 3) {
        imOut = ImagingNewDirty(mode, im->xsize, im->ysize);
        if (!imOut) {
            return NULL;
        }

        for (y = 0; y < im->ysize; y++) {
            UINT8 *in = (UINT8 *)im->image[y];
            UINT8 *out = (UINT8 *)imOut->image[y];

            for (x = 0; x < im->xsize; x++) {
                float v0 = m[0] * in[0] + m[1] * in[1] + m[2] * in[2] + m[3] + 0.5;
                float v1 = m[4] * in[0] + m[5] * in[1] + m[6] * in[2] + m[7] + 0.5;
                float v2 = m[8] * in[0] + m[9] * in[1] + m[10] * in[2] + m[11] + 0.5;
                out[0] = CLIPF(v0);
                out[1] = CLIPF(v1);
                out[2] = CLIPF(v2);
                in += 4;
                out += 4;
            }
        }
    } else {
        return (Imaging)ImagingError_ModeError();
    }

    return imOut;
}
