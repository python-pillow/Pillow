/*
 * The Python Imaging Library
 * $Id$
 *
 * interpolate between two existing images
 *
 * history:
 * 96-03-20 fl	Created
 * 96-05-18 fl	Simplified blend expression
 * 96-10-05 fl	Fixed expression bug, special case for interpolation
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for details on usage and redistribution.
 */


#include "Imaging.h"


Imaging
ImagingBlend(Imaging imIn1, Imaging imIn2, float alpha)
{
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imIn1 || !imIn2 || imIn1->type != IMAGING_TYPE_UINT8)
	return ImagingError_ModeError();
    if (imIn1->type  != imIn2->type  ||
	imIn1->bands != imIn2->bands ||
	imIn1->xsize != imIn2->xsize ||
	imIn1->ysize != imIn2->ysize)
	return ImagingError_Mismatch();

    /* Shortcuts */
    if (alpha == 0.0)
	return ImagingCopy(imIn1);
    else if (alpha == 1.0)
	return ImagingCopy(imIn2);

    imOut = ImagingNew(imIn1->mode, imIn1->xsize, imIn1->ysize);
    if (!imOut)
	return NULL;

    ImagingCopyInfo(imOut, imIn1);

    if (alpha >= 0 && alpha <= 1.0) {
	/* Interpolate between bands */
	for (y = 0; y < imIn1->ysize; y++) {
	    UINT8* in1 = (UINT8*) imIn1->image[y];
	    UINT8* in2 = (UINT8*) imIn2->image[y];
	    UINT8* out = (UINT8*) imOut->image[y];
	    for (x = 0; x < imIn1->linesize; x++)
		out[x] = (UINT8)
		    ((int) in1[x] + alpha * ((int) in2[x] - (int) in1[x]));
	}
    } else {
	/* Extrapolation; must make sure to clip resulting values */
	for (y = 0; y < imIn1->ysize; y++) {
	    UINT8* in1 = (UINT8*) imIn1->image[y];
	    UINT8* in2 = (UINT8*) imIn2->image[y];
	    UINT8* out = (UINT8*) imOut->image[y];
	    for (x = 0; x < imIn1->linesize; x++) {
		float temp = (float)
		    ((int) in1[x] + alpha * ((int) in2[x] - (int) in1[x]));
		if (temp <= 0.0)
		    out[x] = 0;
		else if (temp >= 255.0)
		    out[x] = 255;
		else
		    out[x] = (UINT8) temp;
	    }
	}
    }

    return imOut;
}
