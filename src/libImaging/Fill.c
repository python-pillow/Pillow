/*
 * The Python Imaging Library
 * $Id$
 *
 * fill image with constant pixel value
 *
 * history:
 * 95-11-26 fl moved from Imaging.c
 * 96-05-17 fl added radial fill, renamed wedge to linear
 * 98-06-23 fl changed ImageFill signature
 *
 * Copyright (c) Secret Labs AB 1997-98.  All rights reserved.
 * Copyright (c) Fredrik Lundh 1995-96.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include "math.h"

/**
 * Fill an entire image with a constant colour, in place.
 */
Imaging
ImagingFill(Imaging im, const void *colour) {
    ImagingSectionCookie cookie;

    /* 0-width or 0-height image. No need to do anything */
    if (!im->linesize || !im->ysize) {
        return im;
    }

    // xsize and ysize are invariant during the loops below.
    int xsize = im->xsize;
    int ysize = im->ysize;

    if (im->type == IMAGING_TYPE_SPECIAL) {
        /* use generic API */
        ImagingAccess access = ImagingAccessNew(im);
        if (access) {
            for (int y = 0; y < ysize; y++) {
                for (int x = 0; x < xsize; x++) {
                    access->put_pixel(im, x, y, colour);
                }
            }
            ImagingAccessDelete(im, access);
        } else {
            /* wipe the image */
            for (int y = 0; y < ysize; y++) {
                memset(im->image[y], 0, im->linesize);
            }
        }
    } else {
        INT32 c = 0L;
        ImagingSectionEnter(&cookie);
        memcpy(&c, colour, im->pixelsize);
        if (im->image32 && c != 0L) {
            for (int y = 0; y < ysize; y++) {
                // Restrict safe: sole owner of image data here.
                INT32 *restrict row = im->image32[y];
                for (int x = 0; x < xsize; x++) {
                    row[x] = c;
                }
            }
        } else {
            unsigned char cc = (unsigned char)*(UINT8 *)colour;
            for (int y = 0; y < ysize; y++) {
                memset(im->image[y], cc, im->linesize);
            }
        }
        ImagingSectionLeave(&cookie);
    }

    return im;
}

Imaging
ImagingFillLinearGradient(const ModeID mode) {
    Imaging im;

    if (mode != IMAGING_MODE_1 && mode != IMAGING_MODE_F && mode != IMAGING_MODE_I &&
        mode != IMAGING_MODE_L && mode != IMAGING_MODE_P) {
        return (Imaging)ImagingError_ModeError();
    }

    im = ImagingNewDirty(mode, 256, 256);
    if (!im) {
        return NULL;
    }

    // Branch on pixel type outside the loops so the compiler can tighten them.
    // Restrict safe: sole owner of the freshly-allocated image data here.
    if (im->image8) {
        for (int y = 0; y < 256; y++) {
            memset(im->image8[y], (unsigned char)y, 256);
        }
    } else if (im->type == IMAGING_TYPE_FLOAT32) {
        for (int y = 0; y < 256; y++) {
            FLOAT32 *restrict row = (FLOAT32 *)im->image32[y];
            for (int x = 0; x < 256; x++) {
                row[x] = y;
            }
        }
    } else {
        for (int y = 0; y < 256; y++) {
            INT32 *restrict row = im->image32[y];
            for (int x = 0; x < 256; x++) {
                row[x] = y;
            }
        }
    }

    return im;
}

Imaging
ImagingFillRadialGradient(const ModeID mode) {
    Imaging im;

    if (mode != IMAGING_MODE_1 && mode != IMAGING_MODE_F && mode != IMAGING_MODE_I &&
        mode != IMAGING_MODE_L && mode != IMAGING_MODE_P) {
        return (Imaging)ImagingError_ModeError();
    }

    im = ImagingNewDirty(mode, 256, 256);
    if (!im) {
        return NULL;
    }

#define ASSIGN_ROW(row, y)                                                            \
    for (int x = 0; x < 256; x++) {                                                   \
        int d =                                                                       \
            (int)sqrt((double)((x - 128) * (x - 128) + (y - 128) * (y - 128)) * 2.0); \
        row[x] = d >= 255 ? 255 : d;                                                  \
    }

    // Branch on pixel type outside the loops so the compiler can tighten them.
    // Restrict safe: sole owner of the freshly-allocated image data here.
    if (im->image8) {
        for (int y = 0; y < 256; y++) {
            UINT8 *restrict row = im->image8[y];
            ASSIGN_ROW(row, y);
        }
    } else if (im->type == IMAGING_TYPE_FLOAT32) {
        for (int y = 0; y < 256; y++) {
            FLOAT32 *restrict row = (FLOAT32 *)im->image32[y];
            ASSIGN_ROW(row, y);
        }
    } else {
        for (int y = 0; y < 256; y++) {
            INT32 *restrict row = im->image32[y];
            ASSIGN_ROW(row, y);
        }
    }
#undef ASSIGN_ROW

    return im;
}
