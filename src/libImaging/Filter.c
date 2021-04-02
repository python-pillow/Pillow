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

static inline UINT8
clip8(float in) {
    if (in <= 0.0) {
        return 0;
    }
    if (in >= 255.0) {
        return 255;
    }
    return (UINT8)in;
}

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

void
ImagingFilter3x3(Imaging imOut, Imaging im, const float *kernel, float offset) {
#define KERNEL1x3(in0, x, kernel, d)                                             \
    (_i2f((UINT8)in0[x - d]) * (kernel)[0] + _i2f((UINT8)in0[x]) * (kernel)[1] + \
     _i2f((UINT8)in0[x + d]) * (kernel)[2])

    int x = 0, y = 0;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    if (im->bands == 1) {
        // Add one time for rounding
        offset += 0.5;
        for (y = 1; y < im->ysize - 1; y++) {
            UINT8 *in_1 = (UINT8 *)im->image[y - 1];
            UINT8 *in0 = (UINT8 *)im->image[y];
            UINT8 *in1 = (UINT8 *)im->image[y + 1];
            UINT8 *out = (UINT8 *)imOut->image[y];

            out[0] = in0[0];
            for (x = 1; x < im->xsize - 1; x++) {
                float ss = offset;
                ss += KERNEL1x3(in1, x, &kernel[0], 1);
                ss += KERNEL1x3(in0, x, &kernel[3], 1);
                ss += KERNEL1x3(in_1, x, &kernel[6], 1);
                out[x] = clip8(ss);
            }
            out[x] = in0[x];
        }
    } else {
        // Add one time for rounding
        offset += 0.5;
        for (y = 1; y < im->ysize - 1; y++) {
            UINT8 *in_1 = (UINT8 *)im->image[y - 1];
            UINT8 *in0 = (UINT8 *)im->image[y];
            UINT8 *in1 = (UINT8 *)im->image[y + 1];
            UINT8 *out = (UINT8 *)imOut->image[y];

            memcpy(out, in0, sizeof(UINT32));
            if (im->bands == 2) {
                for (x = 1; x < im->xsize - 1; x++) {
                    float ss0 = offset;
                    float ss3 = offset;
                    UINT32 v;
                    ss0 += KERNEL1x3(in1, x * 4 + 0, &kernel[0], 4);
                    ss3 += KERNEL1x3(in1, x * 4 + 3, &kernel[0], 4);
                    ss0 += KERNEL1x3(in0, x * 4 + 0, &kernel[3], 4);
                    ss3 += KERNEL1x3(in0, x * 4 + 3, &kernel[3], 4);
                    ss0 += KERNEL1x3(in_1, x * 4 + 0, &kernel[6], 4);
                    ss3 += KERNEL1x3(in_1, x * 4 + 3, &kernel[6], 4);
                    v = MAKE_UINT32(clip8(ss0), 0, 0, clip8(ss3));
                    memcpy(out + x * sizeof(v), &v, sizeof(v));
                }
            } else if (im->bands == 3) {
                for (x = 1; x < im->xsize - 1; x++) {
                    float ss0 = offset;
                    float ss1 = offset;
                    float ss2 = offset;
                    UINT32 v;
                    ss0 += KERNEL1x3(in1, x * 4 + 0, &kernel[0], 4);
                    ss1 += KERNEL1x3(in1, x * 4 + 1, &kernel[0], 4);
                    ss2 += KERNEL1x3(in1, x * 4 + 2, &kernel[0], 4);
                    ss0 += KERNEL1x3(in0, x * 4 + 0, &kernel[3], 4);
                    ss1 += KERNEL1x3(in0, x * 4 + 1, &kernel[3], 4);
                    ss2 += KERNEL1x3(in0, x * 4 + 2, &kernel[3], 4);
                    ss0 += KERNEL1x3(in_1, x * 4 + 0, &kernel[6], 4);
                    ss1 += KERNEL1x3(in_1, x * 4 + 1, &kernel[6], 4);
                    ss2 += KERNEL1x3(in_1, x * 4 + 2, &kernel[6], 4);
                    v = MAKE_UINT32(clip8(ss0), clip8(ss1), clip8(ss2), 0);
                    memcpy(out + x * sizeof(v), &v, sizeof(v));
                }
            } else if (im->bands == 4) {
                for (x = 1; x < im->xsize - 1; x++) {
                    float ss0 = offset;
                    float ss1 = offset;
                    float ss2 = offset;
                    float ss3 = offset;
                    UINT32 v;
                    ss0 += KERNEL1x3(in1, x * 4 + 0, &kernel[0], 4);
                    ss1 += KERNEL1x3(in1, x * 4 + 1, &kernel[0], 4);
                    ss2 += KERNEL1x3(in1, x * 4 + 2, &kernel[0], 4);
                    ss3 += KERNEL1x3(in1, x * 4 + 3, &kernel[0], 4);
                    ss0 += KERNEL1x3(in0, x * 4 + 0, &kernel[3], 4);
                    ss1 += KERNEL1x3(in0, x * 4 + 1, &kernel[3], 4);
                    ss2 += KERNEL1x3(in0, x * 4 + 2, &kernel[3], 4);
                    ss3 += KERNEL1x3(in0, x * 4 + 3, &kernel[3], 4);
                    ss0 += KERNEL1x3(in_1, x * 4 + 0, &kernel[6], 4);
                    ss1 += KERNEL1x3(in_1, x * 4 + 1, &kernel[6], 4);
                    ss2 += KERNEL1x3(in_1, x * 4 + 2, &kernel[6], 4);
                    ss3 += KERNEL1x3(in_1, x * 4 + 3, &kernel[6], 4);
                    v = MAKE_UINT32(clip8(ss0), clip8(ss1), clip8(ss2), clip8(ss3));
                    memcpy(out + x * sizeof(v), &v, sizeof(v));
                }
            }
            memcpy(out + x * sizeof(UINT32), in0 + x * sizeof(UINT32), sizeof(UINT32));
        }
    }
    memcpy(imOut->image[y], im->image[y], im->linesize);
}

void
ImagingFilter5x5(Imaging imOut, Imaging im, const float *kernel, float offset) {
#define KERNEL1x5(in0, x, kernel, d)                                             \
    (_i2f((UINT8)in0[x - d - d]) * (kernel)[0] +                                 \
     _i2f((UINT8)in0[x - d]) * (kernel)[1] + _i2f((UINT8)in0[x]) * (kernel)[2] + \
     _i2f((UINT8)in0[x + d]) * (kernel)[3] +                                     \
     _i2f((UINT8)in0[x + d + d]) * (kernel)[4])

    int x = 0, y = 0;

    memcpy(imOut->image[0], im->image[0], im->linesize);
    memcpy(imOut->image[1], im->image[1], im->linesize);
    if (im->bands == 1) {
        // Add one time for rounding
        offset += 0.5;
        for (y = 2; y < im->ysize - 2; y++) {
            UINT8 *in_2 = (UINT8 *)im->image[y - 2];
            UINT8 *in_1 = (UINT8 *)im->image[y - 1];
            UINT8 *in0 = (UINT8 *)im->image[y];
            UINT8 *in1 = (UINT8 *)im->image[y + 1];
            UINT8 *in2 = (UINT8 *)im->image[y + 2];
            UINT8 *out = (UINT8 *)imOut->image[y];

            out[0] = in0[0];
            out[1] = in0[1];
            for (x = 2; x < im->xsize - 2; x++) {
                float ss = offset;
                ss += KERNEL1x5(in2, x, &kernel[0], 1);
                ss += KERNEL1x5(in1, x, &kernel[5], 1);
                ss += KERNEL1x5(in0, x, &kernel[10], 1);
                ss += KERNEL1x5(in_1, x, &kernel[15], 1);
                ss += KERNEL1x5(in_2, x, &kernel[20], 1);
                out[x] = clip8(ss);
            }
            out[x + 0] = in0[x + 0];
            out[x + 1] = in0[x + 1];
        }
    } else {
        // Add one time for rounding
        offset += 0.5;
        for (y = 2; y < im->ysize - 2; y++) {
            UINT8 *in_2 = (UINT8 *)im->image[y - 2];
            UINT8 *in_1 = (UINT8 *)im->image[y - 1];
            UINT8 *in0 = (UINT8 *)im->image[y];
            UINT8 *in1 = (UINT8 *)im->image[y + 1];
            UINT8 *in2 = (UINT8 *)im->image[y + 2];
            UINT8 *out = (UINT8 *)imOut->image[y];

            memcpy(out, in0, sizeof(UINT32) * 2);
            if (im->bands == 2) {
                for (x = 2; x < im->xsize - 2; x++) {
                    float ss0 = offset;
                    float ss3 = offset;
                    UINT32 v;
                    ss0 += KERNEL1x5(in2, x * 4 + 0, &kernel[0], 4);
                    ss3 += KERNEL1x5(in2, x * 4 + 3, &kernel[0], 4);
                    ss0 += KERNEL1x5(in1, x * 4 + 0, &kernel[5], 4);
                    ss3 += KERNEL1x5(in1, x * 4 + 3, &kernel[5], 4);
                    ss0 += KERNEL1x5(in0, x * 4 + 0, &kernel[10], 4);
                    ss3 += KERNEL1x5(in0, x * 4 + 3, &kernel[10], 4);
                    ss0 += KERNEL1x5(in_1, x * 4 + 0, &kernel[15], 4);
                    ss3 += KERNEL1x5(in_1, x * 4 + 3, &kernel[15], 4);
                    ss0 += KERNEL1x5(in_2, x * 4 + 0, &kernel[20], 4);
                    ss3 += KERNEL1x5(in_2, x * 4 + 3, &kernel[20], 4);
                    v = MAKE_UINT32(clip8(ss0), 0, 0, clip8(ss3));
                    memcpy(out + x * sizeof(v), &v, sizeof(v));
                }
            } else if (im->bands == 3) {
                for (x = 2; x < im->xsize - 2; x++) {
                    float ss0 = offset;
                    float ss1 = offset;
                    float ss2 = offset;
                    UINT32 v;
                    ss0 += KERNEL1x5(in2, x * 4 + 0, &kernel[0], 4);
                    ss1 += KERNEL1x5(in2, x * 4 + 1, &kernel[0], 4);
                    ss2 += KERNEL1x5(in2, x * 4 + 2, &kernel[0], 4);
                    ss0 += KERNEL1x5(in1, x * 4 + 0, &kernel[5], 4);
                    ss1 += KERNEL1x5(in1, x * 4 + 1, &kernel[5], 4);
                    ss2 += KERNEL1x5(in1, x * 4 + 2, &kernel[5], 4);
                    ss0 += KERNEL1x5(in0, x * 4 + 0, &kernel[10], 4);
                    ss1 += KERNEL1x5(in0, x * 4 + 1, &kernel[10], 4);
                    ss2 += KERNEL1x5(in0, x * 4 + 2, &kernel[10], 4);
                    ss0 += KERNEL1x5(in_1, x * 4 + 0, &kernel[15], 4);
                    ss1 += KERNEL1x5(in_1, x * 4 + 1, &kernel[15], 4);
                    ss2 += KERNEL1x5(in_1, x * 4 + 2, &kernel[15], 4);
                    ss0 += KERNEL1x5(in_2, x * 4 + 0, &kernel[20], 4);
                    ss1 += KERNEL1x5(in_2, x * 4 + 1, &kernel[20], 4);
                    ss2 += KERNEL1x5(in_2, x * 4 + 2, &kernel[20], 4);
                    v = MAKE_UINT32(clip8(ss0), clip8(ss1), clip8(ss2), 0);
                    memcpy(out + x * sizeof(v), &v, sizeof(v));
                }
            } else if (im->bands == 4) {
                for (x = 2; x < im->xsize - 2; x++) {
                    float ss0 = offset;
                    float ss1 = offset;
                    float ss2 = offset;
                    float ss3 = offset;
                    UINT32 v;
                    ss0 += KERNEL1x5(in2, x * 4 + 0, &kernel[0], 4);
                    ss1 += KERNEL1x5(in2, x * 4 + 1, &kernel[0], 4);
                    ss2 += KERNEL1x5(in2, x * 4 + 2, &kernel[0], 4);
                    ss3 += KERNEL1x5(in2, x * 4 + 3, &kernel[0], 4);
                    ss0 += KERNEL1x5(in1, x * 4 + 0, &kernel[5], 4);
                    ss1 += KERNEL1x5(in1, x * 4 + 1, &kernel[5], 4);
                    ss2 += KERNEL1x5(in1, x * 4 + 2, &kernel[5], 4);
                    ss3 += KERNEL1x5(in1, x * 4 + 3, &kernel[5], 4);
                    ss0 += KERNEL1x5(in0, x * 4 + 0, &kernel[10], 4);
                    ss1 += KERNEL1x5(in0, x * 4 + 1, &kernel[10], 4);
                    ss2 += KERNEL1x5(in0, x * 4 + 2, &kernel[10], 4);
                    ss3 += KERNEL1x5(in0, x * 4 + 3, &kernel[10], 4);
                    ss0 += KERNEL1x5(in_1, x * 4 + 0, &kernel[15], 4);
                    ss1 += KERNEL1x5(in_1, x * 4 + 1, &kernel[15], 4);
                    ss2 += KERNEL1x5(in_1, x * 4 + 2, &kernel[15], 4);
                    ss3 += KERNEL1x5(in_1, x * 4 + 3, &kernel[15], 4);
                    ss0 += KERNEL1x5(in_2, x * 4 + 0, &kernel[20], 4);
                    ss1 += KERNEL1x5(in_2, x * 4 + 1, &kernel[20], 4);
                    ss2 += KERNEL1x5(in_2, x * 4 + 2, &kernel[20], 4);
                    ss3 += KERNEL1x5(in_2, x * 4 + 3, &kernel[20], 4);
                    v = MAKE_UINT32(clip8(ss0), clip8(ss1), clip8(ss2), clip8(ss3));
                    memcpy(out + x * sizeof(v), &v, sizeof(v));
                }
            }
            memcpy(
                out + x * sizeof(UINT32), in0 + x * sizeof(UINT32), sizeof(UINT32) * 2);
        }
    }
    memcpy(imOut->image[y], im->image[y], im->linesize);
    memcpy(imOut->image[y + 1], im->image[y + 1], im->linesize);
}

Imaging
ImagingFilter(Imaging im, int xsize, int ysize, const FLOAT32 *kernel, FLOAT32 offset) {
    Imaging imOut;
    ImagingSectionCookie cookie;

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
