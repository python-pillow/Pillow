/*
 * The Python Imaging Library
 * $Id$
 *
 * histogram support
 *
 * history:
 * 1995-06-15 fl   Created.
 * 1996-04-05 fl   Fixed histogram for multiband images.
 * 1997-02-23 fl   Added mask support
 * 1998-07-01 fl   Added basic 32-bit float/integer support
 *
 * Copyright (c) 1997-2003 by Secret Labs AB.
 * Copyright (c) 1995-2003 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/* HISTOGRAM */
/* --------------------------------------------------------------------
 * Take a histogram of an image. Returns a histogram object containing
 * 256 slots per band in the input image.
 */

void
ImagingHistogramDelete(ImagingHistogram h) {
    if (h) {
        if (h->histogram) {
            free(h->histogram);
        }
        free(h);
    }
}

ImagingHistogram
ImagingHistogramNew(Imaging im) {
    ImagingHistogram h;

    /* Create histogram descriptor */
    h = calloc(1, sizeof(struct ImagingHistogramInstance));
    if (!h) {
        return (ImagingHistogram)ImagingError_MemoryError();
    }

    h->mode = im->mode;
    h->bands = im->bands;

    h->histogram = calloc(im->pixelsize, 256 * sizeof(long));
    if (!h->histogram) {
        free(h);
        return (ImagingHistogram)ImagingError_MemoryError();
    }

    return h;
}

/**
 * Compute a histogram of `im`'s value distribution,
 * optionally restricted to imMask.
 *
 * Contract: Both im and imMask are read-only.
 */
ImagingHistogram
ImagingGetHistogram(Imaging im, Imaging imMask, void *minmax) {
    ImagingSectionCookie cookie;
    ImagingHistogram h;
    INT32 imin, imax;
    FLOAT32 fmin, fmax, scale;

    if (!im) {
        return ImagingError_ModeError();
    }

    int xsize = im->xsize, ysize = im->ysize;
    if (imMask) {
        /* Validate mask */
        if (xsize != imMask->xsize || ysize != imMask->ysize) {
            return ImagingError_Mismatch();
        }
        if (imMask->mode != IMAGING_MODE_1 && imMask->mode != IMAGING_MODE_L) {
            return ImagingError_ValueError("bad transparency mask");
        }
    }

    h = ImagingHistogramNew(im);
    if (!h) {
        return NULL;
    }

    // restrict safe: im and imMask are both read-only here
    //                (they may even be the same image).
    //                histogram is a fresh allocation from ImagingHistogramNew

    long *restrict histogram = h->histogram;

    if (imMask) {
        /* mask */
        if (im->image8) {
            ImagingSectionEnter(&cookie);
            for (int y = 0; y < ysize; y++) {
                UINT8 *restrict in = im->image8[y];
                UINT8 *restrict mask = imMask->image8[y];
                for (int x = 0; x < xsize; x++) {
                    if (mask[x] != 0) {
                        histogram[in[x]]++;
                    }
                }
            }
            ImagingSectionLeave(&cookie);
        } else { /* yes, we need the braces. C isn't Python! */
            if (im->type != IMAGING_TYPE_UINT8) {
                ImagingHistogramDelete(h);
                return ImagingError_ModeError();
            }
            ImagingSectionEnter(&cookie);
            for (int y = 0; y < ysize; y++) {
                UINT8 *restrict in = (UINT8 *)im->image32[y];
                UINT8 *restrict mask = imMask->image8[y];
                for (int x = 0; x < xsize; x++, in += 4) {
                    if (mask[x] != 0) {
                        histogram[*in]++;
                        if (im->bands == 2) {
                            histogram[*(in + 3) + 256]++;
                        } else {
                            histogram[*(in + 1) + 256]++;
                            histogram[*(in + 2) + 512]++;
                            histogram[*(in + 3) + 768]++;
                        }
                    }
                }
            }
            ImagingSectionLeave(&cookie);
        }
    } else {
        /* mask not given; process pixels in image */
        if (im->image8) {
            ImagingSectionEnter(&cookie);
            for (int y = 0; y < ysize; y++) {
                UINT8 *restrict in = im->image8[y];
                for (int x = 0; x < xsize; x++) {
                    histogram[in[x]]++;
                }
            }
            ImagingSectionLeave(&cookie);
        } else {
            switch (im->type) {
                case IMAGING_TYPE_UINT8:
                    ImagingSectionEnter(&cookie);
                    for (int y = 0; y < ysize; y++) {
                        UINT8 *restrict in = (UINT8 *)im->image[y];
                        for (int x = 0; x < xsize; x++, in += 4) {
                            histogram[*in]++;
                            if (im->bands == 2) {
                                histogram[*(in + 3) + 256]++;
                            } else {
                                histogram[*(in + 1) + 256]++;
                                histogram[*(in + 2) + 512]++;
                                histogram[*(in + 3) + 768]++;
                            }
                        }
                    }
                    ImagingSectionLeave(&cookie);
                    break;
                case IMAGING_TYPE_INT32:
                    if (!minmax) {
                        ImagingHistogramDelete(h);
                        return ImagingError_ValueError("min/max not given");
                    }
                    if (!xsize || !ysize) {
                        break;
                    }
                    memcpy(&imin, minmax, sizeof(imin));
                    memcpy(&imax, ((char *)minmax) + sizeof(imin), sizeof(imax));
                    if (imin >= imax) {
                        break;
                    }
                    ImagingSectionEnter(&cookie);
                    scale = 255.0F / (imax - imin);
                    for (int y = 0; y < ysize; y++) {
                        INT32 *restrict in = im->image32[y];
                        for (int x = 0; x < xsize; x++) {
                            int i = (int)(((*in++) - imin) * scale);
                            if (i >= 0 && i < 256) {
                                histogram[i]++;
                            }
                        }
                    }
                    ImagingSectionLeave(&cookie);
                    break;
                case IMAGING_TYPE_FLOAT32:
                    if (!minmax) {
                        ImagingHistogramDelete(h);
                        return ImagingError_ValueError("min/max not given");
                    }
                    if (!xsize || !ysize) {
                        break;
                    }
                    memcpy(&fmin, minmax, sizeof(fmin));
                    memcpy(&fmax, ((char *)minmax) + sizeof(fmin), sizeof(fmax));
                    if (fmin >= fmax) {
                        break;
                    }
                    ImagingSectionEnter(&cookie);
                    scale = 255.0F / (fmax - fmin);
                    for (int y = 0; y < ysize; y++) {
                        FLOAT32 *restrict in = (FLOAT32 *)im->image32[y];
                        for (int x = 0; x < xsize; x++) {
                            int i = (int)(((*in++) - fmin) * scale);
                            if (i >= 0 && i < 256) {
                                histogram[i]++;
                            }
                        }
                    }
                    ImagingSectionLeave(&cookie);
                    break;
            }
        }
    }

    return h;
}
