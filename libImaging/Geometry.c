/*
 * The Python Imaging Library
 * $Id$
 *
 * the imaging geometry methods
 *
 * history:
 * 1995-06-15 fl  Created
 * 1996-04-15 fl  Changed origin
 * 1996-05-18 fl  Fixed rotate90/270 for rectangular images
 * 1996-05-27 fl  Added general purpose transform
 * 1996-11-22 fl  Don't crash when resizing from outside source image
 * 1997-08-09 fl  Fixed rounding error in resize
 * 1998-09-21 fl  Incorporated transformation patches (from Zircon #2)
 * 1998-09-22 fl  Added bounding box to transform engines
 * 1999-02-03 fl  Fixed bicubic filtering for RGB images
 * 1999-02-16 fl  Added fixed-point version of affine transform
 * 2001-03-28 fl  Fixed transform(EXTENT) for xoffset < 0
 * 2003-03-10 fl  Compiler tweaks
 * 2004-09-19 fl  Fixed bilinear/bicubic filtering of LA images
 *
 * Copyright (c) 1997-2003 by Secret Labs AB
 * Copyright (c) 1995-1997 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/* Undef if you don't need resampling filters */
#define WITH_FILTERS

/* For large images rotation is an inefficient operation in terms of CPU cache.
   One row in the source image affects each column in destination.
   Rotating in chunks that fit in the cache can speed up rotation
   8x on a modern CPU. A chunk size of 128 requires only 65k and is large enough
   that the overhead from the extra loops are not apparent. */
#define ROTATE_CHUNK 128

#define COORD(v) ((v) < 0.0 ? -1 : ((int)(v)))
#define FLOOR(v) ((v) < 0.0 ? ((int)floor(v)) : ((int)(v)))

/* -------------------------------------------------------------------- */
/* Transpose operations                                                 */

Imaging
ImagingFlipLeftRight(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y, xr;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();
    if (imIn->xsize != imOut->xsize || imIn->ysize != imOut->ysize)
        return (Imaging) ImagingError_Mismatch();

    ImagingCopyInfo(imOut, imIn);

#define FLIP_HORIZ(image)\
    for (y = 0; y < imIn->ysize; y++) {\
        xr = imIn->xsize-1;\
        for (x = 0; x < imIn->xsize; x++, xr--)\
            imOut->image[y][x] = imIn->image[y][xr];\
    }

    ImagingSectionEnter(&cookie);

    if (imIn->image8)
        FLIP_HORIZ(image8)
    else
        FLIP_HORIZ(image32)

    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingFlipTopBottom(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int y, yr;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();
    if (imIn->xsize != imOut->xsize || imIn->ysize != imOut->ysize)
        return (Imaging) ImagingError_Mismatch();

    ImagingCopyInfo(imOut, imIn);

    ImagingSectionEnter(&cookie);

    yr = imIn->ysize-1;
    for (y = 0; y < imIn->ysize; y++, yr--)
        memcpy(imOut->image[yr], imIn->image[y], imIn->linesize);

    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingRotate90(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y, xx, yy, xr, xxsize, yysize;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();
    if (imIn->xsize != imOut->ysize || imIn->ysize != imOut->xsize)
        return (Imaging) ImagingError_Mismatch();

    ImagingCopyInfo(imOut, imIn);

#define ROTATE_90(image) \
    for (y = 0; y < imIn->ysize; y += ROTATE_CHUNK) { \
        for (x = 0; x < imIn->xsize; x += ROTATE_CHUNK) { \
            yysize = y + ROTATE_CHUNK < imIn->ysize ? y + ROTATE_CHUNK : imIn->ysize; \
            xxsize = x + ROTATE_CHUNK < imIn->xsize ? x + ROTATE_CHUNK : imIn->xsize; \
            for (yy = y; yy < yysize; yy++) { \
                xr = imIn->xsize - 1 - x; \
                for (xx = x; xx < xxsize; xx++, xr--) { \
                    imOut->image[xr][yy] = imIn->image[yy][xx]; \
                } \
            } \
        } \
    }

    ImagingSectionEnter(&cookie);

    if (imIn->image8)
        ROTATE_90(image8)
    else
        ROTATE_90(image32)

    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingTranspose(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y, xx, yy, xxsize, yysize;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();
    if (imIn->xsize != imOut->ysize || imIn->ysize != imOut->xsize)
        return (Imaging) ImagingError_Mismatch();

#define TRANSPOSE(image) \
    for (y = 0; y < imIn->ysize; y += ROTATE_CHUNK) { \
        for (x = 0; x < imIn->xsize; x += ROTATE_CHUNK) { \
            yysize = y + ROTATE_CHUNK < imIn->ysize ? y + ROTATE_CHUNK : imIn->ysize; \
            xxsize = x + ROTATE_CHUNK < imIn->xsize ? x + ROTATE_CHUNK : imIn->xsize; \
            for (yy = y; yy < yysize; yy++) { \
                for (xx = x; xx < xxsize; xx++) { \
                    imOut->image[xx][yy] = imIn->image[yy][xx]; \
                } \
            } \
        } \
    }

    ImagingCopyInfo(imOut, imIn);

    ImagingSectionEnter(&cookie);
    if (imIn->image8)
        TRANSPOSE(image8)
    else
        TRANSPOSE(image32)
    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingTransposeToNew(Imaging imIn)
{
    Imaging imTemp = ImagingNew(imIn->mode, imIn->ysize, imIn->xsize);
    if ( ! imTemp)
        return NULL;

    if ( ! ImagingTranspose(imTemp, imIn)) {
        ImagingDelete(imTemp);
        return NULL;
    }
    return imTemp;
}


Imaging
ImagingRotate180(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y, xr, yr;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();
    if (imIn->xsize != imOut->xsize || imIn->ysize != imOut->ysize)
        return (Imaging) ImagingError_Mismatch();

    ImagingCopyInfo(imOut, imIn);

    yr = imIn->ysize-1;

#define ROTATE_180(image)\
    for (y = 0; y < imIn->ysize; y++, yr--) {\
        xr = imIn->xsize-1;\
        for (x = 0; x < imIn->xsize; x++, xr--)\
            imOut->image[y][x] = imIn->image[yr][xr];\
    }

    ImagingSectionEnter(&cookie);

    if (imIn->image8)
        ROTATE_180(image8)
    else
        ROTATE_180(image32)

    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingRotate270(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y, xx, yy, yr, xxsize, yysize;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();
    if (imIn->xsize != imOut->ysize || imIn->ysize != imOut->xsize)
        return (Imaging) ImagingError_Mismatch();

    ImagingCopyInfo(imOut, imIn);

#define ROTATE_270(image) \
    for (y = 0; y < imIn->ysize; y += ROTATE_CHUNK) { \
        for (x = 0; x < imIn->xsize; x += ROTATE_CHUNK) { \
            yysize = y + ROTATE_CHUNK < imIn->ysize ? y + ROTATE_CHUNK : imIn->ysize; \
            xxsize = x + ROTATE_CHUNK < imIn->xsize ? x + ROTATE_CHUNK : imIn->xsize; \
            yr = imIn->ysize - 1 - y; \
            for (yy = y; yy < yysize; yy++, yr--) { \
                for (xx = x; xx < xxsize; xx++) { \
                    imOut->image[xx][yr] = imIn->image[yy][xx]; \
                } \
            } \
        } \
    }

    ImagingSectionEnter(&cookie);

    if (imIn->image8)
        ROTATE_270(image8)
    else
        ROTATE_270(image32)

    ImagingSectionLeave(&cookie);

    return imOut;
}


/* -------------------------------------------------------------------- */
/* Transforms                                                           */

/* transform primitives (ImagingTransformMap) */

static int
affine_transform(double* xin, double* yin, int x, int y, void* data)
{
    /* full moon tonight.  your compiler will generate bogus code
       for simple expressions, unless you reorganize the code, or
       install Service Pack 3 */

    double* a = (double*) data;
    double a0 = a[0]; double a1 = a[1]; double a2 = a[2];
    double a3 = a[3]; double a4 = a[4]; double a5 = a[5];

    xin[0] = a0 + a1*x + a2*y;
    yin[0] = a3 + a4*x + a5*y;

    return 1;
}

static int
perspective_transform(double* xin, double* yin, int x, int y, void* data)
{
    double* a = (double*) data;
    double a0 = a[0]; double a1 = a[1]; double a2 = a[2];
    double a3 = a[3]; double a4 = a[4]; double a5 = a[5];
    double a6 = a[6]; double a7 = a[7];

    xin[0] = (a0 + a1*x + a2*y) / (a6*x + a7*y + 1);
    yin[0] = (a3 + a4*x + a5*y) / (a6*x + a7*y + 1);

    return 1;
}

static int
quad_transform(double* xin, double* yin, int x, int y, void* data)
{
    /* quad warp: map quadrilateral to rectangle */

    double* a = (double*) data;
    double a0 = a[0]; double a1 = a[1]; double a2 = a[2]; double a3 = a[3];
    double a4 = a[4]; double a5 = a[5]; double a6 = a[6]; double a7 = a[7];

    xin[0] = a0 + a1*x + a2*y + a3*x*y;
    yin[0] = a4 + a5*x + a6*y + a7*x*y;

    return 1;
}

/* transform filters (ImagingTransformFilter) */

#ifdef WITH_FILTERS

static int
nearest_filter8(void* out, Imaging im, double xin, double yin, void* data)
{
    int x = COORD(xin);
    int y = COORD(yin);
    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize)
        return 0;
    ((UINT8*)out)[0] = im->image8[y][x];
    return 1;
}

static int
nearest_filter16(void* out, Imaging im, double xin, double yin, void* data)
{
    int x = COORD(xin);
    int y = COORD(yin);
    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize)
        return 0;
    ((INT16*)out)[0] = ((INT16*)(im->image8[y]))[x];
    return 1;
}

static int
nearest_filter32(void* out, Imaging im, double xin, double yin, void* data)
{
    int x = COORD(xin);
    int y = COORD(yin);
    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize)
        return 0;
    ((INT32*)out)[0] = im->image32[y][x];
    return 1;
}

#define XCLIP(im, x) ( ((x) < 0) ? 0 : ((x) < im->xsize) ? (x) : im->xsize-1 )
#define YCLIP(im, y) ( ((y) < 0) ? 0 : ((y) < im->ysize) ? (y) : im->ysize-1 )

#define BILINEAR(v, a, b, d)\
    (v = (a) + ( (b) - (a) ) * (d))

#define BILINEAR_HEAD(type)\
    int x, y;\
    int x0, x1;\
    double v1, v2;\
    double dx, dy;\
    type* in;\
    if (xin < 0.0 || xin >= im->xsize || yin < 0.0 || yin >= im->ysize)\
        return 0;\
    xin -= 0.5;\
    yin -= 0.5;\
    x = FLOOR(xin);\
    y = FLOOR(yin);\
    dx = xin - x;\
    dy = yin - y;

#define BILINEAR_BODY(type, image, step, offset) {\
    in = (type*) ((image)[YCLIP(im, y)] + offset);\
    x0 = XCLIP(im, x+0)*step;\
    x1 = XCLIP(im, x+1)*step;\
    BILINEAR(v1, in[x0], in[x1], dx);\
    if (y+1 >= 0 && y+1 < im->ysize) {\
        in = (type*) ((image)[y+1] + offset);\
        BILINEAR(v2, in[x0], in[x1], dx);\
    } else\
        v2 = v1;\
    BILINEAR(v1, v1, v2, dy);\
}

static int
bilinear_filter8(void* out, Imaging im, double xin, double yin, void* data)
{
    BILINEAR_HEAD(UINT8);
    BILINEAR_BODY(UINT8, im->image8, 1, 0);
    ((UINT8*)out)[0] = (UINT8) v1;
    return 1;
}

static int
bilinear_filter32I(void* out, Imaging im, double xin, double yin, void* data)
{
    BILINEAR_HEAD(INT32);
    BILINEAR_BODY(INT32, im->image32, 1, 0);
    ((INT32*)out)[0] = (INT32) v1;
    return 1;
}

static int
bilinear_filter32F(void* out, Imaging im, double xin, double yin, void* data)
{
    BILINEAR_HEAD(FLOAT32);
    BILINEAR_BODY(FLOAT32, im->image32, 1, 0);
    ((FLOAT32*)out)[0] = (FLOAT32) v1;
    return 1;
}

static int
bilinear_filter32LA(void* out, Imaging im, double xin, double yin, void* data)
{
    BILINEAR_HEAD(UINT8);
    BILINEAR_BODY(UINT8, im->image, 4, 0);
    ((UINT8*)out)[0] = (UINT8) v1;
    ((UINT8*)out)[1] = (UINT8) v1;
    ((UINT8*)out)[2] = (UINT8) v1;
    BILINEAR_BODY(UINT8, im->image, 4, 3);
    ((UINT8*)out)[3] = (UINT8) v1;
    return 1;
}

static int
bilinear_filter32RGB(void* out, Imaging im, double xin, double yin, void* data)
{
    int b;
    BILINEAR_HEAD(UINT8);
    for (b = 0; b < im->bands; b++) {
        BILINEAR_BODY(UINT8, im->image, 4, b);
        ((UINT8*)out)[b] = (UINT8) v1;
    }
    return 1;
}

#define BICUBIC(v, v1, v2, v3, v4, d) {\
    double p1 = v2;\
    double p2 = -v1 + v3;\
    double p3 = 2*(v1 - v2) + v3 - v4;\
    double p4 = -v1 + v2 - v3 + v4;\
    v = p1 + (d)*(p2 + (d)*(p3 + (d)*p4));\
}

#define BICUBIC_HEAD(type)\
    int x = FLOOR(xin);\
    int y = FLOOR(yin);\
    int x0, x1, x2, x3;\
    double v1, v2, v3, v4;\
    double dx, dy;\
    type* in;\
    if (xin < 0.0 || xin >= im->xsize || yin < 0.0 || yin >= im->ysize)\
        return 0;\
    xin -= 0.5;\
    yin -= 0.5;\
    x = FLOOR(xin);\
    y = FLOOR(yin);\
    dx = xin - x;\
    dy = yin - y;\
    x--; y--;

#define BICUBIC_BODY(type, image, step, offset) {\
    in = (type*) ((image)[YCLIP(im, y)] + offset);\
    x0 = XCLIP(im, x+0)*step;\
    x1 = XCLIP(im, x+1)*step;\
    x2 = XCLIP(im, x+2)*step;\
    x3 = XCLIP(im, x+3)*step;\
    BICUBIC(v1, in[x0], in[x1], in[x2], in[x3], dx);\
    if (y+1 >= 0 && y+1 < im->ysize) {\
        in = (type*) ((image)[y+1] + offset);\
        BICUBIC(v2, in[x0], in[x1], in[x2], in[x3], dx);\
    } else\
        v2 = v1;\
    if (y+2 >= 0 && y+2 < im->ysize) {\
        in = (type*) ((image)[y+2] + offset);\
        BICUBIC(v3, in[x0], in[x1], in[x2], in[x3], dx);\
    } else\
        v3 = v2;\
    if (y+3 >= 0 && y+3 < im->ysize) {\
        in = (type*) ((image)[y+3] + offset);\
        BICUBIC(v4, in[x0], in[x1], in[x2], in[x3], dx);\
    } else\
        v4 = v3;\
    BICUBIC(v1, v1, v2, v3, v4, dy);\
}


static int
bicubic_filter8(void* out, Imaging im, double xin, double yin, void* data)
{
    BICUBIC_HEAD(UINT8);
    BICUBIC_BODY(UINT8, im->image8, 1, 0);
    if (v1 <= 0.0)
        ((UINT8*)out)[0] = 0;
    else if (v1 >= 255.0)
        ((UINT8*)out)[0] = 255;
    else
        ((UINT8*)out)[0] = (UINT8) v1;
    return 1;
}

static int
bicubic_filter32I(void* out, Imaging im, double xin, double yin, void* data)
{
    BICUBIC_HEAD(INT32);
    BICUBIC_BODY(INT32, im->image32, 1, 0);
    ((INT32*)out)[0] = (INT32) v1;
    return 1;
}

static int
bicubic_filter32F(void* out, Imaging im, double xin, double yin, void* data)
{
    BICUBIC_HEAD(FLOAT32);
    BICUBIC_BODY(FLOAT32, im->image32, 1, 0);
    ((FLOAT32*)out)[0] = (FLOAT32) v1;
    return 1;
}

static int
bicubic_filter32LA(void* out, Imaging im, double xin, double yin, void* data)
{
    BICUBIC_HEAD(UINT8);
    BICUBIC_BODY(UINT8, im->image, 4, 0);
    if (v1 <= 0.0) {
        ((UINT8*)out)[0] = 0;
        ((UINT8*)out)[1] = 0;
        ((UINT8*)out)[2] = 0;
    } else if (v1 >= 255.0) {
        ((UINT8*)out)[0] = 255;
        ((UINT8*)out)[1] = 255;
        ((UINT8*)out)[2] = 255;
    } else {
        ((UINT8*)out)[0] = (UINT8) v1;
        ((UINT8*)out)[1] = (UINT8) v1;
        ((UINT8*)out)[2] = (UINT8) v1;
    }
    BICUBIC_BODY(UINT8, im->image, 4, 3);
    if (v1 <= 0.0)
        ((UINT8*)out)[3] = 0;
    else if (v1 >= 255.0)
        ((UINT8*)out)[3] = 255;
    else
        ((UINT8*)out)[3] = (UINT8) v1;
    return 1;
}

static int
bicubic_filter32RGB(void* out, Imaging im, double xin, double yin, void* data)
{
    int b;
    BICUBIC_HEAD(UINT8);
    for (b = 0; b < im->bands; b++) {
        BICUBIC_BODY(UINT8, im->image, 4, b);
        if (v1 <= 0.0)
            ((UINT8*)out)[b] = 0;
        else if (v1 >= 255.0)
            ((UINT8*)out)[b] = 255;
        else
            ((UINT8*)out)[b] = (UINT8) v1;
    }
    return 1;
}

static ImagingTransformFilter
getfilter(Imaging im, int filterid)
{
    switch (filterid) {
    case IMAGING_TRANSFORM_NEAREST:
        if (im->image8)
            switch (im->type) {
            case IMAGING_TYPE_UINT8:
                return (ImagingTransformFilter) nearest_filter8;
            case IMAGING_TYPE_SPECIAL:
                switch (im->pixelsize) {
                case 1:
                    return (ImagingTransformFilter) nearest_filter8;
                case 2:
                    return (ImagingTransformFilter) nearest_filter16;
                case 4:
                    return (ImagingTransformFilter) nearest_filter32;
                }
            }
        else
            return (ImagingTransformFilter) nearest_filter32;
        break;
    case IMAGING_TRANSFORM_BILINEAR:
        if (im->image8)
            return (ImagingTransformFilter) bilinear_filter8;
        else if (im->image32) {
            switch (im->type) {
            case IMAGING_TYPE_UINT8:
                if (im->bands == 2)
                    return (ImagingTransformFilter) bilinear_filter32LA;
                else
                    return (ImagingTransformFilter) bilinear_filter32RGB;
            case IMAGING_TYPE_INT32:
                return (ImagingTransformFilter) bilinear_filter32I;
            case IMAGING_TYPE_FLOAT32:
                return (ImagingTransformFilter) bilinear_filter32F;
            }
        }
        break;
    case IMAGING_TRANSFORM_BICUBIC:
        if (im->image8)
            return (ImagingTransformFilter) bicubic_filter8;
        else if (im->image32) {
            switch (im->type) {
            case IMAGING_TYPE_UINT8:
                if (im->bands == 2)
                    return (ImagingTransformFilter) bicubic_filter32LA;
                else
                    return (ImagingTransformFilter) bicubic_filter32RGB;
            case IMAGING_TYPE_INT32:
                return (ImagingTransformFilter) bicubic_filter32I;
            case IMAGING_TYPE_FLOAT32:
                return (ImagingTransformFilter) bicubic_filter32F;
            }
        }
        break;
    }
    /* no such filter */
    return NULL;
}

#else
#define getfilter(im, id) NULL
#endif

/* transformation engines */

Imaging
ImagingTransform(
    Imaging imOut, Imaging imIn, int x0, int y0, int x1, int y1,
    ImagingTransformMap transform, void* transform_data,
    ImagingTransformFilter filter, void* filter_data,
    int fill)
{
    /* slow generic transformation.  use ImagingTransformAffine or
       ImagingScaleAffine where possible. */

    ImagingSectionCookie cookie;
    int x, y;
    char *out;
    double xx, yy;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();

    ImagingCopyInfo(imOut, imIn);

    ImagingSectionEnter(&cookie);

    if (x0 < 0)
        x0 = 0;
    if (y0 < 0)
        y0 = 0;
    if (x1 > imOut->xsize)
        x1 = imOut->xsize;
    if (y1 > imOut->ysize)
        y1 = imOut->ysize;

    for (y = y0; y < y1; y++) {
        out = imOut->image[y] + x0*imOut->pixelsize;
        for (x = x0; x < x1; x++) {
            if (!transform(&xx, &yy, x-x0, y-y0, transform_data) ||
                !filter(out, imIn, xx, yy, filter_data)) {
                if (fill)
                    memset(out, 0, imOut->pixelsize);
            }
            out += imOut->pixelsize;
        }
    }

    ImagingSectionLeave(&cookie);

    return imOut;
}

static Imaging
ImagingScaleAffine(Imaging imOut, Imaging imIn,
                   int x0, int y0, int x1, int y1,
                   double a[6], int fill)
{
    /* scale, nearest neighbour resampling */

    ImagingSectionCookie cookie;
    int x, y;
    int xin;
    double xo, yo;
    int xmin, xmax;
    int *xintab;

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();

    ImagingCopyInfo(imOut, imIn);

    if (x0 < 0)
        x0 = 0;
    if (y0 < 0)
        y0 = 0;
    if (x1 > imOut->xsize)
        x1 = imOut->xsize;
    if (y1 > imOut->ysize)
        y1 = imOut->ysize;

    xintab = (int*) malloc(imOut->xsize * sizeof(int));
    if (!xintab) {
        ImagingDelete(imOut);
        return (Imaging) ImagingError_MemoryError();
    }

    xo = a[0];
    yo = a[3];

    xmin = x1;
    xmax = x0;

    /* Pretabulate horizontal pixel positions */
    for (x = x0; x < x1; x++) {
        xin = COORD(xo);
        if (xin >= 0 && xin < (int) imIn->xsize) {
            xmax = x+1;
            if (x < xmin)
                xmin = x;
            xintab[x] = xin;
        }
        xo += a[1];
    }

#define AFFINE_SCALE(pixel, image)\
    for (y = y0; y < y1; y++) {\
        int yi = COORD(yo);\
        pixel *in, *out;\
        out = imOut->image[y];\
        if (fill && x1 > x0)\
            memset(out+x0, 0, (x1-x0)*sizeof(pixel));\
        if (yi >= 0 && yi < imIn->ysize) {\
            in = imIn->image[yi];\
            for (x = xmin; x < xmax; x++)\
                out[x] = in[xintab[x]];\
        }\
        yo += a[5];\
    }

    ImagingSectionEnter(&cookie);

    if (imIn->image8) {
        AFFINE_SCALE(UINT8, image8);
    } else {
        AFFINE_SCALE(INT32, image32);
    }

    ImagingSectionLeave(&cookie);

    free(xintab);

    return imOut;
}

static inline int
check_fixed(double a[6], int x, int y)
{
    return (fabs(a[0] + x*a[1] + y*a[2]) < 32768.0 &&
            fabs(a[3] + x*a[4] + y*a[5]) < 32768.0);
}

static inline Imaging
affine_fixed(Imaging imOut, Imaging imIn,
             int x0, int y0, int x1, int y1,
             double a[6], int filterid, int fill)
{
    /* affine transform, nearest neighbour resampling, fixed point
       arithmetics */

    int x, y;
    int xin, yin;
    int xsize, ysize;
    int xx, yy;
    int a0, a1, a2, a3, a4, a5;

    ImagingCopyInfo(imOut, imIn);

    xsize = (int) imIn->xsize;
    ysize = (int) imIn->ysize;

/* use 16.16 fixed point arithmetics */
#define FIX(v) FLOOR((v)*65536.0 + 0.5)

    a0 = FIX(a[0]); a1 = FIX(a[1]); a2 = FIX(a[2]);
    a3 = FIX(a[3]); a4 = FIX(a[4]); a5 = FIX(a[5]);

#define AFFINE_TRANSFORM_FIXED(pixel, image)\
    for (y = y0; y < y1; y++) {\
        pixel *out;\
        xx = a0;\
        yy = a3;\
        out = imOut->image[y];\
        if (fill && x1 > x0)\
            memset(out+x0, 0, (x1-x0)*sizeof(pixel));\
        for (x = x0; x < x1; x++, out++) {\
            xin = xx >> 16;\
            if (xin >= 0 && xin < xsize) {\
                yin = yy >> 16;\
                if (yin >= 0 && yin < ysize)\
                    *out = imIn->image[yin][xin];\
            }\
            xx += a1;\
            yy += a4;\
        }\
        a0 += a2;\
        a3 += a5;\
    }

    if (imIn->image8)
        AFFINE_TRANSFORM_FIXED(UINT8, image8)
    else
        AFFINE_TRANSFORM_FIXED(INT32, image32)

    return imOut;
}

Imaging
ImagingTransformAffine(Imaging imOut, Imaging imIn,
                       int x0, int y0, int x1, int y1,
                       double a[6], int filterid, int fill)
{
    /* affine transform, nearest neighbour resampling, floating point
       arithmetics*/

    ImagingSectionCookie cookie;
    int x, y;
    int xin, yin;
    int xsize, ysize;
    double xx, yy;
    double xo, yo;

    if (filterid || imIn->type == IMAGING_TYPE_SPECIAL) {
        /* Filtered transform */
        ImagingTransformFilter filter = getfilter(imIn, filterid);
        if (!filter)
            return (Imaging) ImagingError_ValueError("unknown filter");
        return ImagingTransform(
            imOut, imIn,
            x0, y0, x1, y1,
            affine_transform, a,
            filter, NULL, fill);
    }

    if (a[2] == 0 && a[4] == 0)
        /* Scaling */
        return ImagingScaleAffine(imOut, imIn, x0, y0, x1, y1, a, fill);

    if (!imOut || !imIn || strcmp(imIn->mode, imOut->mode) != 0)
        return (Imaging) ImagingError_ModeError();

    if (x0 < 0)
        x0 = 0;
    if (y0 < 0)
        y0 = 0;
    if (x1 > imOut->xsize)
        x1 = imOut->xsize;
    if (y1 > imOut->ysize)
        y1 = imOut->ysize;

    ImagingCopyInfo(imOut, imIn);

    /* translate all four corners to check if they are within the
       range that can be represented by the fixed point arithmetics */

    if (check_fixed(a, 0, 0) && check_fixed(a, x1-x0, y1-y0) &&
        check_fixed(a, 0, y1-y0) && check_fixed(a, x1-x0, 0))
        return affine_fixed(imOut, imIn, x0, y0, x1, y1, a, filterid, fill);

    /* FIXME: cannot really think of any reasonable case when the
       following code is used.  maybe we should fall back on the slow
       generic transform engine in this case? */

    xsize = (int) imIn->xsize;
    ysize = (int) imIn->ysize;

    xo = a[0];
    yo = a[3];

#define AFFINE_TRANSFORM(pixel, image)\
    for (y = y0; y < y1; y++) {\
        pixel *out;\
        xx = xo;\
        yy = yo;\
        out = imOut->image[y];\
        if (fill && x1 > x0)\
            memset(out+x0, 0, (x1-x0)*sizeof(pixel));\
        for (x = x0; x < x1; x++, out++) {\
            xin = COORD(xx);\
            if (xin >= 0 && xin < xsize) {\
                yin = COORD(yy);\
                if (yin >= 0 && yin < ysize)\
                    *out = imIn->image[yin][xin];\
            }\
            xx += a[1];\
            yy += a[4];\
        }\
        xo += a[2];\
        yo += a[5];\
    }

    ImagingSectionEnter(&cookie);

    if (imIn->image8)
        AFFINE_TRANSFORM(UINT8, image8)
    else
        AFFINE_TRANSFORM(INT32, image32)

    ImagingSectionLeave(&cookie);

    return imOut;
}

Imaging
ImagingTransformPerspective(Imaging imOut, Imaging imIn,
                            int x0, int y0, int x1, int y1,
                            double a[8], int filterid, int fill)
{
    ImagingTransformFilter filter = getfilter(imIn, filterid);
    if (!filter)
        return (Imaging) ImagingError_ValueError("bad filter number");

    return ImagingTransform(
        imOut, imIn,
        x0, y0, x1, y1,
        perspective_transform, a,
        filter, NULL,
        fill);
}

Imaging
ImagingTransformQuad(Imaging imOut, Imaging imIn,
                     int x0, int y0, int x1, int y1,
                     double a[8], int filterid, int fill)
{
    ImagingTransformFilter filter = getfilter(imIn, filterid);
    if (!filter)
        return (Imaging) ImagingError_ValueError("bad filter number");

    return ImagingTransform(
        imOut, imIn,
        x0, y0, x1, y1,
        quad_transform, a,
        filter, NULL,
        fill);
}

/* -------------------------------------------------------------------- */
/* Convenience functions */

Imaging
ImagingRotate(Imaging imOut, Imaging imIn, double theta, int filterid)
{
    int xsize, ysize;
    double sintheta, costheta;
    double a[6];

    /* Setup an affine transform to rotate around the image center */
    theta = -theta * M_PI / 180.0;
    sintheta = sin(theta);
    costheta = cos(theta);

    xsize = imOut->xsize;
    ysize = imOut->ysize;

    a[0] = -costheta * xsize/2 - sintheta * ysize/2 + xsize/2;
    a[1] = costheta;
    a[2] = sintheta;
    a[3] = sintheta * xsize/2 - costheta * ysize/2 + ysize/2;
    a[4] = -sintheta;
    a[5] = costheta;

    return ImagingTransformAffine(
        imOut, imIn,
        0, 0, imOut->xsize, imOut->ysize,
        a, filterid, 1);
}
