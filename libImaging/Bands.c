/*
 * The Python Imaging Library
 * $Id$
 *
 * stuff to extract and paste back individual bands
 *
 * history:
 * 1996-03-20 fl   Created
 * 1997-08-27 fl   Fixed putband for single band targets.
 * 2003-09-26 fl   Fixed getband/putband for 2-band images (LA, PA).
 *
 * Copyright (c) 1997-2003 by Secret Labs AB.
 * Copyright (c) 1996-1997 by Fredrik Lundh.
 *
 * See the README file for details on usage and redistribution.
 */


#include "Imaging.h"


#define CLIP(x) ((x) <= 0 ? 0 : (x) < 256 ? (x) : 255)


Imaging
ImagingGetBand(Imaging imIn, int band)
{
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imIn || imIn->type != IMAGING_TYPE_UINT8)
	return (Imaging) ImagingError_ModeError();

    if (band < 0 || band >= imIn->bands)
	return (Imaging) ImagingError_ValueError("band index out of range");

    /* Shortcuts */
    if (imIn->bands == 1)
	return ImagingCopy(imIn);

    /* Special case for LXXA etc */
    if (imIn->bands == 2 && band == 1)
        band = 3;

    imOut = ImagingNew("L", imIn->xsize, imIn->ysize);
    if (!imOut)
	return NULL;

    /* Extract band from image */
    for (y = 0; y < imIn->ysize; y++) {
	UINT8* in = (UINT8*) imIn->image[y] + band;
	UINT8* out = imOut->image8[y];
	for (x = 0; x < imIn->xsize; x++) {
	    out[x] = *in;
	    in += 4;
	}
    }

    return imOut;
}

Imaging
ImagingPutBand(Imaging imOut, Imaging imIn, int band)
{
    int x, y;

    /* Check arguments */
    if (!imIn || imIn->bands != 1 || !imOut)
	return (Imaging) ImagingError_ModeError();

    if (band < 0 || band >= imOut->bands)
	return (Imaging) ImagingError_ValueError("band index out of range");

    if (imIn->type  != imOut->type  ||
	imIn->xsize != imOut->xsize ||
	imIn->ysize != imOut->ysize)
	return (Imaging) ImagingError_Mismatch();

    /* Shortcuts */
    if (imOut->bands == 1)
	return ImagingCopy2(imOut, imIn);

    /* Special case for LXXA etc */
    if (imOut->bands == 2 && band == 1)
        band = 3;

    /* Insert band into image */
    for (y = 0; y < imIn->ysize; y++) {
	UINT8* in = imIn->image8[y];
	UINT8* out = (UINT8*) imOut->image[y] + band;
	for (x = 0; x < imIn->xsize; x++) {
	    *out = in[x];
	    out += 4;
	}
    }

    return imOut;
}

Imaging
ImagingFillBand(Imaging imOut, int band, int color)
{
    int x, y;

    /* Check arguments */
    if (!imOut || imOut->type != IMAGING_TYPE_UINT8)
	return (Imaging) ImagingError_ModeError();

    if (band < 0 || band >= imOut->bands)
	return (Imaging) ImagingError_ValueError("band index out of range");

    /* Special case for LXXA etc */
    if (imOut->bands == 2 && band == 1)
        band = 3;

    color = CLIP(color);

    /* Insert color into image */
    for (y = 0; y < imOut->ysize; y++) {
	UINT8* out = (UINT8*) imOut->image[y] + band;
	for (x = 0; x < imOut->xsize; x++) {
	    *out = (UINT8) color;
	    out += 4;
	}
    }

    return imOut;
}
