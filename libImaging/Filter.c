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


static inline UINT8 clip8(float in)
{
    if (in <= 0.0)
        return 0;
    if (in >= 255.0)
        return 255;
    return (UINT8) in;
}

Imaging
ImagingExpand(Imaging imIn, int xmargin, int ymargin, int mode)
{
    Imaging imOut;
    int x, y;
    ImagingSectionCookie cookie;

    if (xmargin < 0 && ymargin < 0)
        return (Imaging) ImagingError_ValueError("bad kernel size");

    imOut = ImagingNew(
        imIn->mode, imIn->xsize+2*xmargin, imIn->ysize+2*ymargin
        );
    if (!imOut)
        return NULL;

#define EXPAND_LINE(type, image, yin, yout) {\
    for (x = 0; x < xmargin; x++)\
        imOut->image[yout][x] = imIn->image[yin][0];\
    for (x = 0; x < imIn->xsize; x++)\
        imOut->image[yout][x+xmargin] = imIn->image[yin][x];\
    for (x = 0; x < xmargin; x++)\
        imOut->image[yout][xmargin+imIn->xsize+x] =\
            imIn->image[yin][imIn->xsize-1];\
    }

#define EXPAND(type, image) {\
    for (y = 0; y < ymargin; y++)\
        EXPAND_LINE(type, image, 0, y);\
    for (y = 0; y < imIn->ysize; y++)\
        EXPAND_LINE(type, image, y, y+ymargin);\
    for (y = 0; y < ymargin; y++)\
        EXPAND_LINE(type, image, imIn->ysize-1, ymargin+imIn->ysize+y);\
    }

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {
        EXPAND(UINT8, image8);
    } else {
        EXPAND(INT32, image32);
    }
    ImagingSectionLeave(&cookie);

    ImagingCopyInfo(imOut, imIn);

    return imOut;
}


void
ImagingFilter3x3(Imaging imOut, Imaging im, const float* kernel,
                 float offset)
{
#define KERNEL3x3(in_1, in, in1, kernel, d) ( \
    (UINT8) in1[x-d]  * kernel[0] + \
    (UINT8) in1[x]    * kernel[1] + \
    (UINT8) in1[x+d]  * kernel[2] + \
    (UINT8) in0[x-d]  * kernel[3] + \
    (UINT8) in0[x]    * kernel[4] + \
    (UINT8) in0[x+d]  * kernel[5] + \
    (UINT8) in_1[x-d] * kernel[6] + \
    (UINT8) in_1[x]   * kernel[7] + \
    (UINT8) in_1[x+d] * kernel[8])

    int x, y;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    for (y = 1; y < im->ysize-1; y++) {
        UINT8* in_1 = (UINT8*) im->image[y-1];
        UINT8* in0 = (UINT8*) im->image[y];
        UINT8* in1 = (UINT8*) im->image[y+1];
        UINT8* out = (UINT8*) imOut->image[y];

        out[0] = in0[0];
        for (x = 1; x < im->xsize-1; x++) {
            float sum = KERNEL3x3(in_1, in, in1, kernel, 1) + offset;
            out[x] = clip8(sum);
         }
        out[x] = in0[x];
    }
    memcpy(imOut->image[y], im->image[y], im->linesize);
}

Imaging
ImagingFilter(Imaging im, int xsize, int ysize, const FLOAT32* kernel,
              FLOAT32 offset)
{
    Imaging imOut;
    int x, y;
    ImagingSectionCookie cookie;

    if (!im || strcmp(im->mode, "L") != 0)
        return (Imaging) ImagingError_ModeError();

    if (im->xsize < xsize || im->ysize < ysize)
        return ImagingCopy(im);

    if ((xsize != 3 && xsize != 5) || xsize != ysize)
        return (Imaging) ImagingError_ValueError("bad kernel size");

    imOut = ImagingNew(im->mode, im->xsize, im->ysize);
    if (!imOut)
        return NULL;

    // Add one time for rounding
    offset += 0.5;

#define KERNEL5x5(image, kernel, d) ( \
    (int) image[y+2][x-d-d] * kernel[0] + \
    (int) image[y+2][x-d]   * kernel[1] + \
    (int) image[y+2][x]     * kernel[2] + \
    (int) image[y+2][x+d]   * kernel[3] + \
    (int) image[y+2][x+d+d] * kernel[4] + \
    (int) image[y+1][x-d-d] * kernel[5] + \
    (int) image[y+1][x-d]   * kernel[6] + \
    (int) image[y+1][x]     * kernel[7] + \
    (int) image[y+1][x+d]   * kernel[8] + \
    (int) image[y+1][x+d+d] * kernel[9] + \
    (int) image[y][x-d-d]   * kernel[10] + \
    (int) image[y][x-d]     * kernel[11] + \
    (int) image[y][x]       * kernel[12] + \
    (int) image[y][x+d]     * kernel[13] + \
    (int) image[y][x+d+d]   * kernel[14] + \
    (int) image[y-1][x-d-d] * kernel[15] + \
    (int) image[y-1][x-d]   * kernel[16] + \
    (int) image[y-1][x]     * kernel[17] + \
    (int) image[y-1][x+d]   * kernel[18] + \
    (int) image[y-1][x+d+d] * kernel[19] + \
    (int) image[y-2][x-d-d] * kernel[20] + \
    (int) image[y-2][x-d]   * kernel[21] + \
    (int) image[y-2][x]     * kernel[22] + \
    (int) image[y-2][x+d]   * kernel[23] + \
    (int) image[y-2][x+d+d] * kernel[24])

    ImagingSectionEnter(&cookie);
    if (xsize == 3) {
        /* 3x3 kernel. */
        ImagingFilter3x3(imOut, im, kernel, offset);
    } else {
        /* 5x5 kernel. */
        memcpy(imOut->image[0], im->image[0], im->linesize);
        memcpy(imOut->image[1], im->image[1], im->linesize);
        for (y = 2; y < im->ysize-2; y++) {
            for (x = 0; x < 2; x++)
                imOut->image8[y][x] = im->image8[y][x];
            for (; x < im->xsize-2; x++) {
                float sum = KERNEL5x5(im->image8, kernel, 1) + offset;
                imOut->image8[y][x] = clip8(sum);
            }
            for (; x < im->xsize; x++)
                imOut->image8[y][x] = im->image8[y][x];
        }
        memcpy(imOut->image[y], im->image[y], im->linesize);
        memcpy(imOut->image[y+1], im->image[y+1], im->linesize);
    }
    ImagingSectionLeave(&cookie);
    return imOut;
}

