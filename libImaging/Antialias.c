/*
 * The Python Imaging Library
 * $Id$
 *
 * pilopen antialiasing support
 *
 * history:
 * 2002-03-09 fl  Created (for PIL 1.1.3)
 * 2002-03-10 fl  Added support for mode "F"
 *
 * Copyright (c) 1997-2002 by Secret Labs AB
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include <math.h>

/* resampling filters (from antialias.py) */

struct filter {
    float (*filter)(float x);
    float support;
};

static inline float sinc_filter(float x)
{
    if (x == 0.0)
        return 1.0;
    x = x * M_PI;
    return sin(x) / x;
}

static inline float antialias_filter(float x)
{
    /* lanczos (truncated sinc) */
    if (-3.0 <= x && x < 3.0)
        return sinc_filter(x) * sinc_filter(x/3);
    return 0.0;
}

static struct filter ANTIALIAS = { antialias_filter, 3.0 };

static inline float nearest_filter(float x)
{
    if (-0.5 <= x && x < 0.5)
        return 1.0;
    return 0.0;
}

static struct filter NEAREST = { nearest_filter, 0.5 };

static inline float bilinear_filter(float x)
{
    if (x < 0.0)
        x = -x;
    if (x < 1.0)
        return 1.0-x;
    return 0.0;
}

static struct filter BILINEAR = { bilinear_filter, 1.0 };

static inline float bicubic_filter(float x)
{
    /* http://en.wikipedia.org/wiki/Bicubic_interpolation#Bicubic_convolution_algorithm */
#define a -0.5
    if (x < 0.0)
        x = -x;
    if (x < 1.0)
        return ((a + 2.0) * x - (a + 3.0)) * x*x + 1;
    if (x < 2.0)
        return (((x - 5) * x + 8) * x - 4) * a;
    return 0.0;
#undef a
}

static struct filter BICUBIC = { bicubic_filter, 2.0 };


static inline UINT8 clip8(float in)
{
    int out = (int) in;
    if (out >= 255)
       return 255;
    if (out <= 0)
        return 0;
    return (UINT8) out;
}


Imaging
ImagingStretchHorizaontal(Imaging imOut, Imaging imIn, int filter)
{
    /* FIXME: this is a quick and straightforward translation from a
       python prototype.  might need some further C-ification... */

    ImagingSectionCookie cookie;
    struct filter *filterp;
    float support, scale, filterscale;
    float center, ww, ss;
    int xx, yy, x, b, kmax, xmin, xmax;
    int *xbounds;
    float *k, *kk;

    /* check modes */
    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();

    if (imOut->ysize != imIn->ysize)
        return (Imaging) ImagingError_ValueError(
            "ImagingStretchHorizaontal requires equal heights"
        );

    /* check filter */
    switch (filter) {
    case IMAGING_TRANSFORM_NEAREST:
        filterp = &NEAREST;
        break;
    case IMAGING_TRANSFORM_ANTIALIAS:
        filterp = &ANTIALIAS;
        break;
    case IMAGING_TRANSFORM_BILINEAR:
        filterp = &BILINEAR;
        break;
    case IMAGING_TRANSFORM_BICUBIC:
        filterp = &BICUBIC;
        break;
    default:
        return (Imaging) ImagingError_ValueError(
            "unsupported resampling filter"
            );
    }

    /* prepare for horizontal stretch */
    filterscale = scale = (float) imIn->xsize / imOut->xsize;

    /* determine support size (length of resampling filter) */
    support = filterp->support;

    if (filterscale < 1.0) {
        filterscale = 1.0;
    }

    support = support * filterscale;

    /* maximum number of coofs */
    kmax = (int) ceil(support) * 2 + 1;

    /* coefficient buffer (with rounding safety margin) */
    kk = malloc(imOut->xsize * kmax * sizeof(float));
    if ( ! kk)
        return (Imaging) ImagingError_MemoryError();

    xbounds = malloc(imOut->xsize * 2 * sizeof(int));
    if ( ! xbounds) {
        free(kk);
        return (Imaging) ImagingError_MemoryError();
    }

    for (xx = 0; xx < imOut->xsize; xx++) {
        k = &kk[xx * kmax];
        center = (xx + 0.5) * scale;
        ww = 0.0;
        ss = 1.0 / filterscale;
        xmin = (int) floor(center - support);
        if (xmin < 0)
            xmin = 0;
        xmax = (int) ceil(center + support);
        if (xmax > imIn->xsize)
            xmax = imIn->xsize;
        for (x = xmin; x < xmax; x++) {
            float w = filterp->filter((x - center + 0.5) * ss) * ss;
            k[x - xmin] = w;
            ww += w;
        }
        for (x = 0; x < xmax - xmin; x++) {
            if (ww != 0.0)
                k[x] /= ww;
        }
        xbounds[xx * 2 + 0] = xmin;
        xbounds[xx * 2 + 1] = xmax;
    }

    ImagingSectionEnter(&cookie);
    /* horizontal stretch */
    for (yy = 0; yy < imOut->ysize; yy++) {
        if (imIn->image8) {
            /* 8-bit grayscale */
            for (xx = 0; xx < imOut->xsize; xx++) {
                xmin = xbounds[xx * 2 + 0];
                xmax = xbounds[xx * 2 + 1];
                k = &kk[xx * kmax];
                ss = 0.5;
                for (x = xmin; x < xmax; x++)
                    ss = ss + imIn->image8[yy][x] * k[x - xmin];
                imOut->image8[yy][xx] = clip8(ss);
            }
        } else
            switch(imIn->type) {
            case IMAGING_TYPE_UINT8:
                /* n-bit grayscale */
                for (xx = 0; xx < imOut->xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    for (b = 0; b < imIn->bands; b++) {
                        if (imIn->bands == 2 && b)
                            b = 3; /* hack to deal with LA images */
                        ss = 0.5;
                        for (x = xmin; x < xmax; x++)
                            ss = ss + (UINT8) imIn->image[yy][x*4+b] * k[x - xmin];
                        imOut->image[yy][xx*4+b] = clip8(ss);
                    }
                }
                break;
            case IMAGING_TYPE_INT32:
                /* 32-bit integer */
                for (xx = 0; xx < imOut->xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss = 0.0;
                    for (x = xmin; x < xmax; x++)
                        ss = ss + IMAGING_PIXEL_I(imIn, x, yy) * k[x - xmin];
                    IMAGING_PIXEL_I(imOut, xx, yy) = (int) ss;
                }
                break;
            case IMAGING_TYPE_FLOAT32:
                /* 32-bit float */
                for (xx = 0; xx < imOut->xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss = 0.0;
                    for (x = xmin; x < xmax; x++)
                        ss = ss + IMAGING_PIXEL_F(imIn, x, yy) * k[x - xmin];
                    IMAGING_PIXEL_F(imOut, xx, yy) = ss;
                }
                break;
            default:
                ImagingSectionLeave(&cookie);
                return (Imaging) ImagingError_ModeError();
            }
    }
    ImagingSectionLeave(&cookie);

    free(kk);
    free(xbounds);

    return imOut;
}


Imaging
ImagingStretch(Imaging imOut, Imaging imIn, int filter)
{
    Imaging imTemp1, imTemp2, imTemp3;
    int xsize = imOut->xsize;
    int ysize = imOut->ysize;

    if (strcmp(imIn->mode, "P") == 0 || strcmp(imIn->mode, "1") == 0)
        return (Imaging) ImagingError_ModeError();

    /* two-pass resize */
    imTemp1 = ImagingNew(imIn->mode, xsize, imIn->ysize);
    if ( ! imTemp1)
        return NULL;

    /* first pass */
    if ( ! ImagingStretchHorizaontal(imTemp1, imIn, filter)) {
        ImagingDelete(imTemp1);
        return NULL;
    }

    imTemp2 = ImagingNew(imIn->mode, imIn->ysize, xsize);
    if ( ! imTemp2) {
        ImagingDelete(imTemp1);
        return NULL;
    }

    /* transpose image once */
    if ( ! ImagingTranspose(imTemp2, imTemp1)) {
        ImagingDelete(imTemp1);
        ImagingDelete(imTemp2);
        return NULL;
    }
    ImagingDelete(imTemp1);

    imTemp3 = ImagingNew(imIn->mode, ysize, xsize);
    if ( ! imTemp3) {
        ImagingDelete(imTemp2);
        return NULL;
    }

    /* second pass */
    if ( ! ImagingStretchHorizaontal(imTemp3, imTemp2, filter)) {
        ImagingDelete(imTemp2);
        ImagingDelete(imTemp3);
        return NULL;
    }
    ImagingDelete(imTemp2);

    /* transpose result */
    if ( ! ImagingTranspose(imOut, imTemp3)) {
        ImagingDelete(imTemp3);
        return NULL;
    }
    ImagingDelete(imTemp3);

    return imOut;
}
