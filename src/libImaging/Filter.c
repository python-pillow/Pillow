/*
 * The Python Imaging Library
 * $Id$
 *
 * apply convolution kernel to image
 *
 * history:
 * 1995-11-26 fl   Created, supports 3x3 kernels
 * 1995-11-27 fl   Added 5x5 kernels, copy border
 * 1999-07-26 fl   Eliminated a few compiler warnings
 * 2002-06-09 fl   Moved kernel definitions to Python
 * 2002-06-11 fl   Support floating point kernels
 * 2003-09-15 fl   Added ImagingExpand helper
 *
 * Copyright (c) Secret Labs AB 1997-2002.  All rights reserved.
 * Copyright (c) Fredrik Lundh 1995.
 *
 * See the README file for information on usage and redistribution.
 */

/*
 * FIXME: Support RGB and RGBA/CMYK modes as well
 * FIXME: Expand image border (current version leaves border as is)
 * FIXME: Implement image processing gradient filters
 */

#include "Imaging.h"


/* 5 is number of bits enought to account all kernel coefficients (1<<5 > 25).
   8 is number of bits in result.
   Any coefficients delta smaller than this precision will have no effect. */
#define PRECISION_BITS (8 + 5)
/* 16 is number of bis required for kernel storage.
   1 bit is reserver for sign.
   Largest possible kernel coefficient is  */
#define LARGEST_KERNEL (1 << (16 - 1 - PRECISION_BITS))

#include "FilterSIMD_3x3f_u8.c"
#include "FilterSIMD_3x3f_4u8.c"
#include "FilterSIMD_3x3i_4u8.c"
#include "FilterSIMD_5x5f_u8.c"
#include "FilterSIMD_5x5f_4u8.c"
#include "FilterSIMD_5x5i_4u8.c"


Imaging
ImagingExpand(Imaging imIn, int xmargin, int ymargin, int mode) {
    Imaging imOut;
    int x, y;
    ImagingSectionCookie cookie;

    if (xmargin < 0 && ymargin < 0) {
        return (Imaging)ImagingError_ValueError("bad kernel size");
    }

    imOut = ImagingNewDirty(
        imIn->mode, imIn->xsize + 2 * xmargin, imIn->ysize + 2 * ymargin);
    if (!imOut) {
        return NULL;
    }

#define EXPAND_LINE(type, image, yin, yout)                        \
    {                                                              \
        for (x = 0; x < xmargin; x++) {                            \
            imOut->image[yout][x] = imIn->image[yin][0];           \
        }                                                          \
        for (x = 0; x < imIn->xsize; x++) {                        \
            imOut->image[yout][x + xmargin] = imIn->image[yin][x]; \
        }                                                          \
        for (x = 0; x < xmargin; x++) {                            \
            imOut->image[yout][xmargin + imIn->xsize + x] =        \
                imIn->image[yin][imIn->xsize - 1];                 \
        }                                                          \
    }

#define EXPAND(type, image)                                                       \
    {                                                                             \
        for (y = 0; y < ymargin; y++) {                                           \
            EXPAND_LINE(type, image, 0, y);                                       \
        }                                                                         \
        for (y = 0; y < imIn->ysize; y++) {                                       \
            EXPAND_LINE(type, image, y, y + ymargin);                             \
        }                                                                         \
        for (y = 0; y < ymargin; y++) {                                           \
            EXPAND_LINE(type, image, imIn->ysize - 1, ymargin + imIn->ysize + y); \
        }                                                                         \
    }

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {
        EXPAND(UINT8, image8);
    } else {
        EXPAND(INT32, image32);
    }
    ImagingSectionLeave(&cookie);

    ImagingCopyPalette(imOut, imIn);

    return imOut;
}

Imaging
ImagingFilter(Imaging im, int xsize, int ysize, const FLOAT32* kernel,
              FLOAT32 offset)
{
    ImagingSectionCookie cookie;
    Imaging imOut;
    int i, fast_path = 1;
    FLOAT32 tmp;
    INT16 norm_kernel[25];
    INT32 norm_offset;

    if (!im || im->type != IMAGING_TYPE_UINT8) {
        return (Imaging)ImagingError_ModeError();
    }

    if (im->xsize < xsize || im->ysize < ysize) {
        return ImagingCopy(im);
    }

    if ((xsize != 3 && xsize != 5) || xsize != ysize) {
        return (Imaging)ImagingError_ValueError("bad kernel size");
    }

    imOut = ImagingNewDirty(im->mode, im->xsize, im->ysize);
    if (!imOut) {
        return NULL;
    }

    for (i = 0; i < xsize * ysize; i++) {
        tmp = kernel[i] * (1 << PRECISION_BITS);
        tmp += (tmp >= 0) ? 0.5 : -0.5;
        if (tmp >= 32768 || tmp <= -32769) {
            fast_path = 0;
            break;
        }
        norm_kernel[i] = tmp;
    }
    tmp = offset * (1 << PRECISION_BITS);
    tmp += (tmp >= 0) ? 0.5 : -0.5;
    if (tmp >= 1 << 30) {
        norm_offset = 1 << 30;
    } else if (tmp <= -1 << 30) {
        norm_offset = -1 << 30;
    } else {
        norm_offset = tmp;
    }

    ImagingSectionEnter(&cookie);
    if (xsize == 3) {
        /* 3x3 kernel. */
        if (im->image8) {
            ImagingFilter3x3f_u8(imOut, im, kernel, offset);
        } else {
            if (fast_path) {
                ImagingFilter3x3i_4u8(imOut, im, norm_kernel, norm_offset);
            } else {
                ImagingFilter3x3f_4u8(imOut, im, kernel, offset);
            }
        }
    } else {
        /* 5x5 kernel. */
        if (im->image8) {
            ImagingFilter5x5f_u8(imOut, im, kernel, offset);
        } else {
            if (fast_path) {
                ImagingFilter5x5i_4u8(imOut, im, norm_kernel, norm_offset);
            } else {
                ImagingFilter5x5f_4u8(imOut, im, kernel, offset);
            }
        }
    }
    ImagingSectionLeave(&cookie);
    return imOut;
}
