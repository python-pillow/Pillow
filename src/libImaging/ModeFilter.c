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
    ImagingSectionCookie cookie;
    Imaging imOut;
    int x, y, i;
    int xx, yy;
    int x0, x1, y0, y1;
    int maxcount;
    UINT8 maxpixel;
    int histogram[256];

    if (!im) {
        return (Imaging)ImagingError_ModeError(NULL);
    }
    if (im->bands != 1) {
        return (Imaging)ImagingError_ModeError("image must have exactly 1 band");
    }
    if (im->type != IMAGING_TYPE_UINT8) {
        return (Imaging)ImagingError_NotSupportedError("only 8-bit images supported");
    }

    imOut = ImagingNewDirty(im->mode, im->xsize, im->ysize);
    if (!imOut) {
        return NULL;
    }

    size = size / 2;

    ImagingSectionEnter(&cookie);

    for (y = 0; y < imOut->ysize; y++) {
        UINT8 *out = &IMAGING_PIXEL_L(imOut, 0, y);
        y0 = size > y ? 0 : y - size;
        y1 = size >= imOut->ysize - 1 - y ? imOut->ysize - 1 : y + size;
        for (x = 0; x < imOut->xsize; x++) {
            x0 = size > x ? 0 : x - size;
            x1 = size >= imOut->xsize - 1 - x ? imOut->xsize - 1 : x + size;

            /* calculate histogram over current area */

            /* FIXME: brute force! to improve, update the histogram
               incrementally.  may also add a "frequent list", like in
               the old implementation, but I'm not sure that's worth
               the added complexity... */

            memset(histogram, 0, sizeof(histogram));
            for (yy = y0; yy <= y1; yy++) {
                UINT8 *in = &IMAGING_PIXEL_L(im, 0, yy);
                for (xx = x0; xx <= x1; xx++) {
                    histogram[in[xx]]++;
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

    ImagingSectionLeave(&cookie);

    ImagingCopyPalette(imOut, im);

    return imOut;
}
