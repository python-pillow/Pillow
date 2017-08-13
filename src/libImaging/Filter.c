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

#include <emmintrin.h>
#include <mmintrin.h>
#include <smmintrin.h>

#if defined(__AVX2__)
    #include <immintrin.h>
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

    imOut = ImagingNewDirty(
        imIn->mode, imIn->xsize+2*xmargin, imIn->ysize+2*ymargin);
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

    ImagingCopyPalette(imOut, imIn);

    return imOut;
}


void
ImagingFilter3x3(Imaging imOut, Imaging im, const float* kernel,
                 float offset)
{
#define KERNEL1x3(in0, x, kernel, d) ( \
    _i2f((UINT8) in0[x-d])  * (kernel)[0] + \
    _i2f((UINT8) in0[x])    * (kernel)[1] + \
    _i2f((UINT8) in0[x+d])  * (kernel)[2])

#define MM_KERNEL1x3(ss, in0, x, kernel, d) \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[0]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x-d])))); \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[1]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+0])))); \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[2]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+d]))));

    int x = 0, y = 0;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    if (im->bands == 1) {
        // Add one time for rounding
        offset += 0.5;
        for (y = 1; y < im->ysize-1; y++) {
            UINT8* in_1 = (UINT8*) im->image[y-1];
            UINT8* in0 = (UINT8*) im->image[y];
            UINT8* in1 = (UINT8*) im->image[y+1];
            UINT8* out = (UINT8*) imOut->image[y];

            out[0] = in0[0];
            for (x = 1; x < im->xsize-1; x++) {
                float ss = offset;
                ss += KERNEL1x3(in1, x, &kernel[0], 1);
                ss += KERNEL1x3(in0, x, &kernel[3], 1);
                ss += KERNEL1x3(in_1, x, &kernel[6], 1);
                out[x] = clip8(ss);
             }
            out[x] = in0[x];
        }
    } else {
        for (y = 1; y < im->ysize-1; y++) {
            UINT32* in_1 = (UINT32*) im->image[y-1];
            UINT32* in0 = (UINT32*) im->image[y];
            UINT32* in1 = (UINT32*) im->image[y+1];
            UINT32* out = (UINT32*) imOut->image[y];
            __m128 pix00 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in1)[0]));
            __m128 pix01 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in1)[1]));
            __m128 pix10 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[0]));
            __m128 pix11 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[1]));
            __m128 pix20 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in_1)[0]));
            __m128 pix21 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in_1)[1]));
            __m128 pix02, pix12, pix22;

            out[0] = in0[0];
            x = 1;
            for (; x < im->xsize-3; x += 3) {
                __m128 ss;
                __m128i ssi0, ssi1, ssi2;

                ss = _mm_set1_ps(offset);
                pix02 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in1)[x+1]));
                pix12 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+1]));
                pix22 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in_1)[x+1]));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[0]), pix00));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[1]), pix01));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[2]), pix02));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[3]), pix10));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[4]), pix11));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[5]), pix12));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[6]), pix20));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[7]), pix21));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[8]), pix22));
                ssi0 = _mm_cvtps_epi32(ss);


                ss = _mm_set1_ps(offset);
                pix00 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in1)[x+2]));
                pix10 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+2]));
                pix20 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in_1)[x+2]));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[0]), pix01));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[1]), pix02));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[2]), pix00));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[3]), pix11));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[4]), pix12));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[5]), pix10));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[6]), pix21));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[7]), pix22));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[8]), pix20));
                ssi1 = _mm_cvtps_epi32(ss);

                ss = _mm_set1_ps(offset);
                pix01 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in1)[x+3]));
                pix11 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+3]));
                pix21 = _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in_1)[x+3]));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[0]), pix02));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[1]), pix00));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[2]), pix01));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[3]), pix12));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[4]), pix10));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[5]), pix11));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[6]), pix22));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[7]), pix20));
                ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps(kernel[8]), pix21));
                ssi2 = _mm_cvtps_epi32(ss);


                ssi0 = _mm_packs_epi32(ssi0, ssi1);
                ssi1 = _mm_packs_epi32(ssi2, ssi2);
                ssi0 = _mm_packus_epi16(ssi0, ssi1);
                out[x] = _mm_cvtsi128_si32(ssi0);
                _mm_storeu_si128((__m128i*) &out[x], ssi0);
            }
            for (; x < im->xsize-1; x++) {
                __m128 ss = _mm_set1_ps(offset);
                __m128i ssi;

                MM_KERNEL1x3(ss, in1, x, &kernel[0], 1);
                MM_KERNEL1x3(ss, in0, x, &kernel[3], 1);
                MM_KERNEL1x3(ss, in_1, x, &kernel[6], 1);

                ssi = _mm_cvtps_epi32(ss);
                ssi = _mm_packs_epi32(ssi, ssi);
                ssi = _mm_packus_epi16(ssi, ssi);
                out[x] = _mm_cvtsi128_si32(ssi);
            }
            out[x] = in0[x];
        }
    }
    memcpy(imOut->image[y], im->image[y], im->linesize);
}


void
ImagingFilter5x5(Imaging imOut, Imaging im, const float* kernel,
                 float offset)
{
#define KERNEL1x5(in0, x, kernel, d) ( \
    _i2f((UINT8) in0[x-d-d])   * (kernel)[0] + \
    _i2f((UINT8) in0[x-d])     * (kernel)[1] + \
    _i2f((UINT8) in0[x])       * (kernel)[2] + \
    _i2f((UINT8) in0[x+d])     * (kernel)[3] + \
    _i2f((UINT8) in0[x+d+d])   * (kernel)[4])

#define MM_KERNEL1x5(ss, in0, x, kernel, d) \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[0]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x-d-d])))); \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[1]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x-d])))); \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[2]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+0])))); \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[3]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+d])))); \
    ss = _mm_add_ps(ss, _mm_mul_ps(_mm_set1_ps((kernel)[4]), \
        _mm_cvtepi32_ps(_mm_cvtepu8_epi32(*(__m128i *) &(in0)[x+d+d]))));

    int x = 0, y = 0;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    memcpy(imOut->image[1], im->image[1], im->linesize);
    if (im->bands == 1) {
        // Add one time for rounding
        offset += 0.5;
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
                float ss = offset;
                ss += KERNEL1x5(in2, x, &kernel[0], 1);
                ss += KERNEL1x5(in1, x, &kernel[5], 1);
                ss += KERNEL1x5(in0, x, &kernel[10], 1);
                ss += KERNEL1x5(in_1, x, &kernel[15], 1);
                ss += KERNEL1x5(in_2, x, &kernel[20], 1);
                out[x] = clip8(ss);
            }
            out[x+0] = in0[x+0];
            out[x+1] = in0[x+1];
        }
    } else {
        for (y = 2; y < im->ysize-2; y++) {
            UINT32* in_2 = (UINT32*) im->image[y-2];
            UINT32* in_1 = (UINT32*) im->image[y-1];
            UINT32* in0 = (UINT32*) im->image[y];
            UINT32* in1 = (UINT32*) im->image[y+1];
            UINT32* in2 = (UINT32*) im->image[y+2];
            UINT32* out = (UINT32*) imOut->image[y];

            out[0] = in0[0];
            out[1] = in0[1];
            for (x = 2; x < im->xsize-2; x++) {
                __m128 ss = _mm_set1_ps(offset);
                __m128i ssi;

                MM_KERNEL1x5(ss, in2, x, &kernel[0], 1);
                MM_KERNEL1x5(ss, in1, x, &kernel[5], 1);
                MM_KERNEL1x5(ss, in0, x, &kernel[10], 1);
                MM_KERNEL1x5(ss, in_1, x, &kernel[15], 1);
                MM_KERNEL1x5(ss, in_2, x, &kernel[20], 1);

                ssi = _mm_cvtps_epi32(ss);
                ssi = _mm_packs_epi32(ssi, ssi);
                ssi = _mm_packus_epi16(ssi, ssi);
                out[x] = _mm_cvtsi128_si32(ssi);
            }
            out[x] = in0[x];
            out[x+1] = in0[x+1];
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

    imOut = ImagingNewDirty(im->mode, im->xsize, im->ysize);
    if (!imOut)
        return NULL;

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

