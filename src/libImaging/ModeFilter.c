/*
 * The Python Imaging Library
 * $Id$
 *
 * mode filter
 *
 * history:
 * 2002-06-08 fl    Created (based on code from IFUNC95)
 * 2004-10-05 fl    Rewritten; use a simpler brute-force algorithm
 *
 * Copyright (c) Secret Labs AB 2002-2004.  All rights reserved.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

Imaging
ImagingModeFilter(Imaging im, int size) {
    Imaging imOut;
    int x, y, i;
    int xx, yy;
    int maxcount;
    UINT8 maxpixel;
    int histogram[256];

    if (!im || im->bands != 1 || im->type != IMAGING_TYPE_UINT8) {
        return (Imaging)ImagingError_ModeError();
    }

    imOut = ImagingNewDirty(im->mode, im->xsize, im->ysize);
    if (!imOut) {
        return NULL;
    }

    size = size / 2;

    for (y = 0; y < imOut->ysize; y++) {
        UINT8 *out = &IMAGING_PIXEL_L(imOut, 0, y);
        for (x = 0; x < imOut->xsize; x++) {
            /* calculate histogram over current area */

            /* FIXME: brute force! to improve, update the histogram
               incrementally.  may also add a "frequent list", like in
               the old implementation, but I'm not sure that's worth
               the added complexity... */

            memset(histogram, 0, sizeof(histogram));
            for (yy = y - size; yy <= y + size; yy++) {
                if (yy >= 0 && yy < imOut->ysize) {
                    UINT8 *in = &IMAGING_PIXEL_L(im, 0, yy);
                    for (xx = x - size; xx <= x + size; xx++) {
                        if (xx >= 0 && xx < imOut->xsize) {
                            histogram[in[xx]]++;
                        }
                    }
                }
            }

            /* find most frequent pixel value in this region */
            maxpixel = 0;
            maxcount = histogram[maxpixel];
            for (i = 1; i < 256; i++) {
                if (histogram[i] > maxcount) {
                    maxcount = histogram[i];
                    maxpixel = (UINT8)i;
                }
            }

            if (maxcount > 2) {
                out[x] = maxpixel;
            } else {
                out[x] = IMAGING_PIXEL_L(im, x, y);
            }
        }
    }

    ImagingCopyPalette(imOut, im);

    return imOut;
}
