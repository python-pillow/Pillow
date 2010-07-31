/*
 * The Python Imaging Library
 * $Id$
 *
 * fill image with constant pixel value
 *
 * history:
 * 95-11-26 fl	moved from Imaging.c
 * 96-05-17 fl	added radial fill, renamed wedge to linear
 * 98-06-23 fl	changed ImageFill signature
 *
 * Copyright (c) Secret Labs AB 1997-98.  All rights reserved.
 * Copyright (c) Fredrik Lundh 1995-96.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include "math.h"

Imaging
ImagingFill(Imaging im, const void* colour)
{
    int x, y;

    if (im->type == IMAGING_TYPE_SPECIAL) {
        /* use generic API */
        ImagingAccess access = ImagingAccessNew(im);
        if (access) {
            for (y = 0; y < im->ysize; y++)
                for (x = 0; x < im->xsize; x++)
                    access->put_pixel(im, x, y, colour);
            ImagingAccessDelete(im, access);
        } else {
            /* wipe the image */
            for (y = 0; y < im->ysize; y++)
                memset(im->image[y], 0, im->linesize);
        }
    } else {
        INT32 c = 0L;
        memcpy(&c, colour, im->pixelsize);
        if (im->image32 && c != 0L) {
            for (y = 0; y < im->ysize; y++)
                for (x = 0; x < im->xsize; x++)
                    im->image32[y][x] = c;
        } else {
            unsigned char cc = (unsigned char) *(UINT8*) colour;
            for (y = 0; y < im->ysize; y++)
                memset(im->image[y], cc, im->linesize);
        }
    }

    return im;
}

Imaging
ImagingFillLinearGradient(const char *mode)
{
    Imaging im;
    int y;

    if (strlen(mode) != 1)
	return (Imaging) ImagingError_ModeError();

    im = ImagingNew(mode, 256, 256);
    if (!im)
	return NULL;

    for (y = 0; y < 256; y++)
	memset(im->image8[y], (unsigned char) y, 256);

    return im;
}

Imaging
ImagingFillRadialGradient(const char *mode)
{
    Imaging im;
    int x, y;
    int d;

    if (strlen(mode) != 1)
	return (Imaging) ImagingError_ModeError();

    im = ImagingNew(mode, 256, 256);
    if (!im)
	return NULL;

    for (y = 0; y < 256; y++)
	for (x = 0; x < 256; x++) {
	    d = (int) sqrt((double) ((x-128)*(x-128) + (y-128)*(y-128)) * 2.0);
	    if (d >= 255)
		im->image8[y][x] = 255;
	    else
		im->image8[y][x] = d;
	}

    return im;
}
