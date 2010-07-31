/* 
 * The Python Imaging Library
 * $Id$
 *
 * copy image
 *
 * history:
 * 95-11-26 fl   Moved from Imaging.c
 * 97-05-12 fl   Added ImagingCopy2
 * 97-08-28 fl   Allow imOut == NULL in ImagingCopy2
 *
 * Copyright (c) Fredrik Lundh 1995-97.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for details on usage and redistribution.
 */


#include "Imaging.h"


static Imaging
_copy(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int y;

    if (!imIn)
	return (Imaging) ImagingError_ValueError(NULL);

    imOut = ImagingNew2(imIn->mode, imOut, imIn);
    if (!imOut)
        return NULL;

    ImagingCopyInfo(imOut, imIn);

    ImagingSectionEnter(&cookie);
    if (imIn->block != NULL && imOut->block != NULL)
	memcpy(imOut->block, imIn->block, imIn->ysize * imIn->linesize);
    else
        for (y = 0; y < imIn->ysize; y++)
            memcpy(imOut->image[y], imIn->image[y], imIn->linesize);
    ImagingSectionLeave(&cookie);

    return imOut;
}

Imaging
ImagingCopy(Imaging imIn)
{
    return _copy(NULL, imIn);
}

Imaging
ImagingCopy2(Imaging imOut, Imaging imIn)
{
    return _copy(imOut, imIn);
}
