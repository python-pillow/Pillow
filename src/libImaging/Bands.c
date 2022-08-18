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

Imaging
ImagingGetBand(Imaging imIn, int band) {
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imIn || imIn->type != IMAGING_TYPE_UINT8) {
        return (Imaging)ImagingError_ModeError();
    }

    if (band < 0 || band >= imIn->bands) {
        return (Imaging)ImagingError_ValueError("band index out of range");
    }

    /* Shortcut */
    if (imIn->bands == 1) {
        return ImagingCopy(imIn);
    }

    /* Allocate memory for result */
    imOut = ImagingNewDirty("L", imIn->xsize, imIn->ysize);
    if (!imOut) {
        return NULL;
    }

    /* Extract band from image */
    int pixelsize = imIn->pixelsize;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8 *in = (UINT8 *)imIn->image[y] + band;
        UINT8 *out = imOut->image8[y];
        x = 0;
        /* Copy four values at a time */
        for (; x < imIn->xsize - 3; x += 4) {
            UINT32 v = MAKE_UINT32(in[0], in[pixelsize], in[pixelsize * 2], in[pixelsize * 3]);
            memcpy(out + x, &v, sizeof(v));
            in += pixelsize * 4;
        }
        /* Copy any remaining values on this line */
        for (; x < imIn->xsize; x++) {
            out[x] = *in;
            in += pixelsize;
        }
    }

    return imOut;
}

int
ImagingSplit(Imaging imIn, Imaging *bands) {
    int i, j, band, x, y;

    /* Check arguments */
    if (!imIn || imIn->type != IMAGING_TYPE_UINT8) {
        (void)ImagingError_ModeError();
        return 0;
    }

    /* Shortcut */
    if (imIn->bands == 1) {
        bands[0] = ImagingCopy(imIn);
        return 1;
    }

    /* Allocate memory for "bands" */
    for (i = 0; i < imIn->bands; i++) {
        bands[i] = ImagingNewDirty("L", imIn->xsize, imIn->ysize);
        if (!bands[i]) {
            for (j = 0; j < i; ++j) {
                ImagingDelete(bands[j]);
            }
            return 0;
        }
    }

    /* Extract bands from image */
    int pixelsize = imIn->pixelsize;
    for (band = 0; band < imIn->bands; band++) {
        for (y = 0; y < imIn->ysize; y++) {
            UINT8 *in = (UINT8 *)imIn->image[y] + band;
            UINT8 *out = bands[band]->image8[y];
            x = 0;
            /* Copy four values at a time */
            for (; x < imIn->xsize - 3; x += 4) {
                UINT32 v = MAKE_UINT32(in[0], in[pixelsize], in[pixelsize * 2], in[pixelsize * 3]);
                memcpy(out + x, &v, sizeof(v));
                in += pixelsize * 4;
            }
            /* Copy any remaining values on this line */
            for (; x < imIn->xsize; x++) {
                out[x] = *in;
                in += pixelsize;
            }
        }
    }

    return imIn->bands;
}

Imaging
ImagingPutBand(Imaging imOut, Imaging imIn, int band) {
    int x, y;

    /* Check arguments */
    if (!imIn || imIn->bands != 1 || !imOut) {
        return (Imaging)ImagingError_ModeError();
    }

    if (band < 0 || band >= imOut->bands) {
        return (Imaging)ImagingError_ValueError("band index out of range");
    }

    if (imIn->type != imOut->type || imIn->xsize != imOut->xsize ||
        imIn->ysize != imOut->ysize) {
        return (Imaging)ImagingError_Mismatch();
    }

    /* Shortcut */
    if (imOut->bands == 1) {
        return ImagingCopy2(imOut, imIn);
    }

    /* Insert band into image */
    int pixelsize = imOut->pixelsize;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8 *in = imIn->image8[y];
        UINT8 *out = (UINT8 *)imOut->image[y] + band;
        for (x = 0; x < imIn->xsize; x++) {
            *out = in[x];
            out += pixelsize;
        }
    }

    return imOut;
}

Imaging
ImagingFillBand(Imaging imOut, int band, int color) {
    int x, y;

    /* Check arguments */
    if (!imOut || imOut->type != IMAGING_TYPE_UINT8) {
        return (Imaging)ImagingError_ModeError();
    }

    if (band < 0 || band >= imOut->bands) {
        return (Imaging)ImagingError_ValueError("band index out of range");
    }

    color = CLIP8(color);

    /* Insert color into image */
    int pixelsize = imOut->pixelsize;
    for (y = 0; y < imOut->ysize; y++) {
        UINT8 *out = (UINT8 *)imOut->image[y] + band;
        for (x = 0; x < imOut->xsize; x++) {
            *out = (UINT8)color;
            out += pixelsize;
        }
    }

    return imOut;
}

Imaging
ImagingMerge(const char *mode, Imaging *bands) {
    int i, x, y;
    int xsize, ysize;
    int bandsCount;
    Imaging imOut;
    Imaging firstBand;
    Imaging band;

    /* Check the first band. The size of this band is used as the size of the output image. */
    firstBand = bands[0];
    if (!firstBand) {
        return (Imaging)ImagingError_ValueError("wrong number of bands");
    }
    xsize = firstBand->xsize;
    ysize = firstBand->ysize;

    /* Allocate memory for the output image. This also allows us to get the number of bands this image should have. */
    imOut = ImagingNewDirty(mode, xsize, ysize);
    if (!imOut) {
        return NULL;
    }

    /* Check that the given bands have the right mode and size */
    for (bandsCount = 0; bandsCount < imOut->bands; ++bandsCount) {
        band = bands[bandsCount];
        if (!band) {
            break;
        }
        if (band->bands != 1) {
            ImagingDelete(imOut);
            return (Imaging)ImagingError_ModeError();
        }
        if (band->xsize != xsize || band->ysize != ysize) {
            ImagingDelete(imOut);
            return (Imaging)ImagingError_Mismatch();
        }
    }

    /* Check that we have enough bands for the output image */
    if (imOut->bands != bandsCount) {
        ImagingDelete(imOut);
        return (Imaging)ImagingError_ValueError("wrong number of bands");
    }

    /* TODO: Check that we weren't given too many bands? How? */

    /* Shortcut */
    if (bandsCount == 1) {
        return ImagingCopy2(imOut, firstBand);
    }

    /* Insert the bands into the image */
    int pixelsize = imOut->pixelsize;
    for (i = 0; i < bandsCount; i++) {
        band = bands[i];
        for (y = 0; y < ysize; y++) {
            UINT8 *in = band->image8[y];
            UINT8 *out = (UINT8 *)imOut->image[y] + i;
            for (x = 0; x < xsize; x++) {
                *out = in[x];
                out += pixelsize;
            }
        }
    }

    return imOut;
}
