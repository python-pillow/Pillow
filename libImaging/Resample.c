/*
 * The Python Imaging Library
 * $Id$
 *
 * Pillow image resamling support
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

static inline float lanczos_filter(float x)
{
    /* truncated sinc */
    if (-3.0 <= x && x < 3.0)
        return sinc_filter(x) * sinc_filter(x/3);
    return 0.0;
}

static struct filter LANCZOS = { lanczos_filter, 3.0 };

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


/* This is work around bug in GCC prior 4.9 in 64 bit mode.
   GCC generates code with partial dependency which 3 times slower.
   See: http://stackoverflow.com/a/26588074/253146 */
#if defined(__x86_64__) && defined(__SSE__) &&  ! defined(__NO_INLINE__) && \
    ! defined(__clang__) && defined(GCC_VERSION) && (GCC_VERSION < 40900)
static float __attribute__((always_inline)) i2f(int v) {
    float x;
    __asm__("xorps %0, %0; cvtsi2ss %1, %0" : "=X"(x) : "r"(v) );
    return x;
}
#else
static float inline i2f(int v) { return (float) v; }
#endif


Imaging
ImagingResampleHorizontal(Imaging imIn, int xsize, int filter)
{
    ImagingSectionCookie cookie;
    Imaging imOut;
    struct filter *filterp;
    float support, scale, filterscale;
    float center, ww, ss, ss0, ss1, ss2, ss3;
    int xx, yy, x, kmax, xmin, xmax;
    int *xbounds;
    float *k, *kk;

    /* check filter */
    switch (filter) {
    case IMAGING_TRANSFORM_LANCZOS:
        filterp = &LANCZOS;
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
    filterscale = scale = (float) imIn->xsize / xsize;

    /* determine support size (length of resampling filter) */
    support = filterp->support;

    if (filterscale < 1.0) {
        filterscale = 1.0;
    }

    support = support * filterscale;

    /* maximum number of coofs */
    kmax = (int) ceil(support) * 2 + 1;

    /* coefficient buffer */
    kk = malloc(xsize * kmax * sizeof(float));
    if ( ! kk)
        return (Imaging) ImagingError_MemoryError();

    xbounds = malloc(xsize * 2 * sizeof(int));
    if ( ! xbounds) {
        free(kk);
        return (Imaging) ImagingError_MemoryError();
    }

    for (xx = 0; xx < xsize; xx++) {
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

    imOut = ImagingNew(imIn->mode, xsize, imIn->ysize);
    if ( ! imOut) {
        free(kk);
        free(xbounds);
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    /* horizontal stretch */
    for (yy = 0; yy < imOut->ysize; yy++) {
        if (imIn->image8) {
            /* 8-bit grayscale */
            for (xx = 0; xx < xsize; xx++) {
                xmin = xbounds[xx * 2 + 0];
                xmax = xbounds[xx * 2 + 1];
                k = &kk[xx * kmax];
                ss = 0.5;
                for (x = xmin; x < xmax; x++)
                    ss += i2f(imIn->image8[yy][x]) * k[x - xmin];
                imOut->image8[yy][xx] = clip8(ss);
            }
        } else {
            switch(imIn->type) {
            case IMAGING_TYPE_UINT8:
                /* n-bit grayscale */
                if (imIn->bands == 2) {
                    for (xx = 0; xx < xsize; xx++) {
                        xmin = xbounds[xx * 2 + 0];
                        xmax = xbounds[xx * 2 + 1];
                        k = &kk[xx * kmax];
                        ss0 = ss1 = 0.5;
                        for (x = xmin; x < xmax; x++) {
                            ss0 += i2f((UINT8) imIn->image[yy][x*4 + 0]) * k[x - xmin];
                            ss1 += i2f((UINT8) imIn->image[yy][x*4 + 3]) * k[x - xmin];
                        }
                        imOut->image[yy][xx*4 + 0] = clip8(ss0);
                        imOut->image[yy][xx*4 + 3] = clip8(ss1);
                    }
                } else if (imIn->bands == 3) {
                    for (xx = 0; xx < xsize; xx++) {
                        xmin = xbounds[xx * 2 + 0];
                        xmax = xbounds[xx * 2 + 1];
                        k = &kk[xx * kmax];
                        ss0 = ss1 = ss2 = 0.5;
                        for (x = xmin; x < xmax; x++) {
                            ss0 += i2f((UINT8) imIn->image[yy][x*4 + 0]) * k[x - xmin];
                            ss1 += i2f((UINT8) imIn->image[yy][x*4 + 1]) * k[x - xmin];
                            ss2 += i2f((UINT8) imIn->image[yy][x*4 + 2]) * k[x - xmin];
                        }
                        imOut->image[yy][xx*4 + 0] = clip8(ss0);
                        imOut->image[yy][xx*4 + 1] = clip8(ss1);
                        imOut->image[yy][xx*4 + 2] = clip8(ss2);
                    }
                } else {
                    for (xx = 0; xx < xsize; xx++) {
                        xmin = xbounds[xx * 2 + 0];
                        xmax = xbounds[xx * 2 + 1];
                        k = &kk[xx * kmax];
                        ss0 = ss1 = ss2 = ss3 = 0.5;
                        for (x = xmin; x < xmax; x++) {
                            ss0 += i2f((UINT8) imIn->image[yy][x*4 + 0]) * k[x - xmin];
                            ss1 += i2f((UINT8) imIn->image[yy][x*4 + 1]) * k[x - xmin];
                            ss2 += i2f((UINT8) imIn->image[yy][x*4 + 2]) * k[x - xmin];
                            ss3 += i2f((UINT8) imIn->image[yy][x*4 + 3]) * k[x - xmin];
                        }
                        imOut->image[yy][xx*4 + 0] = clip8(ss0);
                        imOut->image[yy][xx*4 + 1] = clip8(ss1);
                        imOut->image[yy][xx*4 + 2] = clip8(ss2);
                        imOut->image[yy][xx*4 + 3] = clip8(ss3);
                    }
                }
                break;
            case IMAGING_TYPE_INT32:
                /* 32-bit integer */
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss = 0.0;
                    for (x = xmin; x < xmax; x++)
                        ss += i2f(IMAGING_PIXEL_I(imIn, x, yy)) * k[x - xmin];
                    IMAGING_PIXEL_I(imOut, xx, yy) = (int) ss;
                }
                break;
            case IMAGING_TYPE_FLOAT32:
                /* 32-bit float */
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss = 0.0;
                    for (x = xmin; x < xmax; x++)
                        ss += IMAGING_PIXEL_F(imIn, x, yy) * k[x - xmin];
                    IMAGING_PIXEL_F(imOut, xx, yy) = ss;
                }
                break;
            }
        }
    }
    ImagingSectionLeave(&cookie);
    free(kk);
    free(xbounds);
    return imOut;
}


Imaging
ImagingResample(Imaging imIn, int xsize, int ysize, int filter)
{
    Imaging imTemp1, imTemp2, imTemp3;
    Imaging imOut;

    if (strcmp(imIn->mode, "P") == 0 || strcmp(imIn->mode, "1") == 0)
        return (Imaging) ImagingError_ModeError();

    if (imIn->type == IMAGING_TYPE_SPECIAL)
        return (Imaging) ImagingError_ModeError();

    /* two-pass resize, first pass */
    imTemp1 = ImagingResampleHorizontal(imIn, xsize, filter);
    if ( ! imTemp1)
        return NULL;

    /* transpose image once */
    imTemp2 = ImagingTransposeToNew(imTemp1);
    ImagingDelete(imTemp1);
    if ( ! imTemp2)
        return NULL;

    /* second pass */
    imTemp3 = ImagingResampleHorizontal(imTemp2, ysize, filter);
    ImagingDelete(imTemp2);
    if ( ! imTemp3)
        return NULL;

    /* transpose result */
    imOut = ImagingTransposeToNew(imTemp3);
    ImagingDelete(imTemp3);
    if ( ! imOut)
        return NULL;

    return imOut;
}
