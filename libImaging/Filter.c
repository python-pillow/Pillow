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

Imaging
ImagingExpand(Imaging imIn, int xmargin, int ymargin, int mode)
{
    Imaging imOut;
    int x, y;

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

    if (imIn->image8) {
	EXPAND(UINT8, image8);
    } else {
	EXPAND(INT32, image32);
    }

    ImagingCopyInfo(imOut, imIn);

    return imOut;
}

Imaging
ImagingFilter(Imaging im, int xsize, int ysize, const FLOAT32* kernel,
              FLOAT32 offset, FLOAT32 divisor)
{
    Imaging imOut;
    int x, y;
    FLOAT32 sum;

    if (!im || strcmp(im->mode, "L") != 0)
	return (Imaging) ImagingError_ModeError();

    if (im->xsize < xsize || im->ysize < ysize)
        return ImagingCopy(im);

    if ((xsize != 3 && xsize != 5) || xsize != ysize)
	return (Imaging) ImagingError_ValueError("bad kernel size");

    imOut = ImagingNew(im->mode, im->xsize, im->ysize);
    if (!imOut)
	return NULL;

    /* brute force kernel implementations */
#define	KERNEL3x3(image, kernel, d) ( \
    (int) image[y+1][x-d] * kernel[0] + \
    (int) image[y+1][x]   * kernel[1] + \
    (int) image[y+1][x+d] * kernel[2] + \
    (int) image[y][x-d]   * kernel[3] + \
    (int) image[y][x]     * kernel[4] + \
    (int) image[y][x+d]   * kernel[5] + \
    (int) image[y-1][x-d] * kernel[6] + \
    (int) image[y-1][x]   * kernel[7] + \
    (int) image[y-1][x+d] * kernel[8])

#define	KERNEL5x5(image, kernel, d) ( \
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

    if (xsize == 3) {
	/* 3x3 kernel. */
	for (x = 0; x < im->xsize; x++)
	    imOut->image[0][x] = im->image8[0][x];
	for (y = 1; y < im->ysize-1; y++) {
	    imOut->image[y][0] = im->image8[y][0];
	    for (x = 1; x < im->xsize-1; x++) {
		sum = KERNEL3x3(im->image8, kernel, 1) / divisor + offset;
		if (sum <= 0)
		    imOut->image8[y][x] = 0;
		else if (sum >= 255)
		    imOut->image8[y][x] = 255;
		else
		    imOut->image8[y][x] = (UINT8) sum;
	     }
	    imOut->image8[y][x] = im->image8[y][x];
	}
	for (x = 0; x < im->xsize; x++)
	    imOut->image8[y][x] = im->image8[y][x];
    } else {
	/* 5x5 kernel. */
	for (y = 0; y < 2; y++)
	    for (x = 0; x < im->xsize; x++)
		imOut->image8[y][x] = im->image8[y][x];
	for (; y < im->ysize-2; y++) {
	    for (x = 0; x < 2; x++)
		imOut->image8[y][x] = im->image8[y][x];
	    for (; x < im->xsize-2; x++) {
		sum = KERNEL5x5(im->image8, kernel, 1) / divisor + offset;
		if (sum <= 0)
		    imOut->image8[y][x] = 0;
		else if (sum >= 255)
		    imOut->image8[y][x] = 255;
		else
		    imOut->image8[y][x] = (UINT8) sum;
	    }
	    for (; x < im->xsize; x++)
		imOut->image8[y][x] = im->image8[y][x];
	}
	for (; y < im->ysize; y++)
	    for (x = 0; x < im->xsize; x++)
		imOut->image8[y][x] = im->image8[y][x];
    }
    return imOut;
}

