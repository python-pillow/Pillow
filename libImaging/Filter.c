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


#ifdef WORDS_BIGENDIAN
    #define MAKE_UINT32(u0, u1, u2, u3) (u3 | (u2<<8) | (u1<<16) | (u0<<24))
#else
    #define MAKE_UINT32(u0, u1, u2, u3) (u0 | (u1<<8) | (u2<<16) | (u3<<24))
#endif


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
#define KERNEL3x3(in_1, in0, in1, x, kernel, d) ( \
    (UINT8) in1[x-d]  * kernel[0] + \
    (UINT8) in1[x]    * kernel[1] + \
    (UINT8) in1[x+d]  * kernel[2] + \
    (UINT8) in0[x-d]  * kernel[3] + \
    (UINT8) in0[x]    * kernel[4] + \
    (UINT8) in0[x+d]  * kernel[5] + \
    (UINT8) in_1[x-d] * kernel[6] + \
    (UINT8) in_1[x]   * kernel[7] + \
    (UINT8) in_1[x+d] * kernel[8])

    int x = 0, y = 0;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    if (im->bands == 1) {
        for (y = 1; y < im->ysize-1; y++) {
            UINT8* in_1 = (UINT8*) im->image[y-1];
            UINT8* in0 = (UINT8*) im->image[y];
            UINT8* in1 = (UINT8*) im->image[y+1];
            UINT8* out = (UINT8*) imOut->image[y];

            out[0] = in0[0];
            for (x = 1; x < im->xsize-1; x++) {
                float ss = KERNEL3x3(in_1, in0, in1, x, kernel, 1);
                out[x] = clip8(ss + offset);
             }
            out[x] = in0[x];
        }
    } else {
        for (y = 1; y < im->ysize-1; y++) {
            UINT8* in_1 = (UINT8*) im->image[y-1];
            UINT8* in0 = (UINT8*) im->image[y];
            UINT8* in1 = (UINT8*) im->image[y+1];
            UINT32* out = (UINT32*) imOut->image[y];

            out[0] = ((UINT32*) in0)[0];
            if (im->bands == 2) {
                for (x = 1; x < im->xsize-1; x++) {
                    float ss0 = KERNEL3x3(in_1, in0, in1, x*4+0, kernel, 4);
                    float ss3 = KERNEL3x3(in_1, in0, in1, x*4+3, kernel, 4);
                    out[x] = MAKE_UINT32(
                        clip8(ss0 + offset), 0, 0, clip8(ss3 + offset));
                }
            } else if (im->bands == 3) {
                for (x = 1; x < im->xsize-1; x++) {
                    float ss0 = KERNEL3x3(in_1, in0, in1, x*4+0, kernel, 4);
                    float ss1 = KERNEL3x3(in_1, in0, in1, x*4+1, kernel, 4);
                    float ss2 = KERNEL3x3(in_1, in0, in1, x*4+2, kernel, 4);
                    out[x] = MAKE_UINT32(
                        clip8(ss0 + offset), clip8(ss1 + offset),
                        clip8(ss2 + offset), 0);
                }
            } else if (im->bands == 4) {
                for (x = 1; x < im->xsize-1; x++) {
                    float ss0 = KERNEL3x3(in_1, in0, in1, x*4+0, kernel, 4);
                    float ss1 = KERNEL3x3(in_1, in0, in1, x*4+1, kernel, 4);
                    float ss2 = KERNEL3x3(in_1, in0, in1, x*4+2, kernel, 4);
                    float ss3 = KERNEL3x3(in_1, in0, in1, x*4+3, kernel, 4);
                    out[x] = MAKE_UINT32(
                        clip8(ss0 + offset), clip8(ss1 + offset),
                        clip8(ss2 + offset), clip8(ss3 + offset));
                }
            }
            out[x] = ((UINT32*) in0)[x];
        }
    }
    memcpy(imOut->image[y], im->image[y], im->linesize);
}


void
ImagingFilter5x5(Imaging imOut, Imaging im, const float* kernel,
                 float offset)
{
#define KERNEL5x5(in_2, in_1, in0, in1, in2, x, kernel, d) ( \
    (UINT8) in2[x-d-d]   * kernel[0] + \
    (UINT8) in2[x-d]     * kernel[1] + \
    (UINT8) in2[x]       * kernel[2] + \
    (UINT8) in2[x+d]     * kernel[3] + \
    (UINT8) in2[x+d+d]   * kernel[4] + \
    (UINT8) in1[x-d-d]   * kernel[5] + \
    (UINT8) in1[x-d]     * kernel[6] + \
    (UINT8) in1[x]       * kernel[7] + \
    (UINT8) in1[x+d]     * kernel[8] + \
    (UINT8) in1[x+d+d]   * kernel[9] + \
    (UINT8) in0[x-d-d]   * kernel[10] + \
    (UINT8) in0[x-d]     * kernel[11] + \
    (UINT8) in0[x]       * kernel[12] + \
    (UINT8) in0[x+d]     * kernel[13] + \
    (UINT8) in0[x+d+d]   * kernel[14] + \
    (UINT8) in_1[x-d-d]  * kernel[15] + \
    (UINT8) in_1[x-d]    * kernel[16] + \
    (UINT8) in_1[x]      * kernel[17] + \
    (UINT8) in_1[x+d]    * kernel[18] + \
    (UINT8) in_1[x+d+d]  * kernel[19] + \
    (UINT8) in_2[x-d-d]  * kernel[20] + \
    (UINT8) in_2[x-d]    * kernel[21] + \
    (UINT8) in_2[x]      * kernel[22] + \
    (UINT8) in_2[x+d]    * kernel[23] + \
    (UINT8) in_2[x+d+d]  * kernel[24])

    int x = 0, y = 0;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    memcpy(imOut->image[1], im->image[1], im->linesize);
    if (im->bands == 1) {
        for (y = 2; y < im->ysize-2; y++) {
            UINT8* in_2 = (UINT8*) im->image[y-2];
            UINT8* in_1 = (UINT8*) im->image[y-1];
            UINT8* in0 = (UINT8*) im->image[y];
            UINT8* in1 = (UINT8*) im->image[y+1];
            UINT8* in2 = (UINT8*) im->image[y+2];
            UINT8* out = (UINT8*) imOut->image[y];

            out[0] = in0[0];
            out[1] = in0[1];
            for (x = 2; x < im->xsize-2; x++) {
                float ss = KERNEL5x5(in_2, in_1, in0, in1, in2, x, kernel, 1);
                out[x] = clip8(ss + offset);
            }
            out[x+0] = in0[x+0];
            out[x+1] = in0[x+1];
        }
    } else {
        for (y = 2; y < im->ysize-2; y++) {
            UINT8* in_2 = (UINT8*) im->image[y-2];
            UINT8* in_1 = (UINT8*) im->image[y-1];
            UINT8* in0 = (UINT8*) im->image[y];
            UINT8* in1 = (UINT8*) im->image[y+1];
            UINT8* in2 = (UINT8*) im->image[y+2];
            UINT32* out = (UINT32*) imOut->image[y];

            out[0] = ((UINT32*) in0)[0];
            out[1] = ((UINT32*) in0)[1];
            if (im->bands == 2) {
                for (x = 2; x < im->xsize-2; x++) {
                    float ss0 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+0, kernel, 4);
                    float ss3 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+3, kernel, 4);
                    out[x] = MAKE_UINT32(
                        clip8(ss0 + offset), 0, 0, clip8(ss3 + offset));
                }
            } else if (im->bands == 3) {
                for (x = 2; x < im->xsize-2; x++) {
                    float ss0 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+0, kernel, 4);
                    float ss1 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+1, kernel, 4);
                    float ss2 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+2, kernel, 4);
                    out[x] = MAKE_UINT32(
                        clip8(ss0 + offset), clip8(ss1 + offset),
                        clip8(ss2 + offset), 0);
                }
            } else if (im->bands == 4) {
                for (x = 2; x < im->xsize-2; x++) {
                    float ss0 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+0, kernel, 4);
                    float ss1 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+1, kernel, 4);
                    float ss2 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+2, kernel, 4);
                    float ss3 = KERNEL5x5(in_2, in_1, in0, in1, in2, x*4+3, kernel, 4);
                    out[x] = MAKE_UINT32(
                        clip8(ss0 + offset), clip8(ss1 + offset),
                        clip8(ss2 + offset), clip8(ss3 + offset));
                }
            }
            out[x] = ((UINT32*) in0)[x];
            out[x+1] = ((UINT32*) in0)[x+1];
        }
    }
    memcpy(imOut->image[y], im->image[y], im->linesize);
    memcpy(imOut->image[y+1], im->image[y+1], im->linesize);
}

Imaging
ImagingFilter(Imaging im, int xsize, int ysize, const FLOAT32* kernel,
              FLOAT32 offset)
{
    Imaging imOut;
    ImagingSectionCookie cookie;

    if ( ! im || im->type != IMAGING_TYPE_UINT8)
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

    ImagingSectionEnter(&cookie);
    if (xsize == 3) {
        /* 3x3 kernel. */
        ImagingFilter3x3(imOut, im, kernel, offset);
    } else {
        /* 5x5 kernel. */
        ImagingFilter5x5(imOut, im, kernel, offset);
    }
    ImagingSectionLeave(&cookie);
    return imOut;
}

