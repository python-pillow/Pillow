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

/**
 * Extract a single band from imIn into a newly allocated single-band image.
 * Contract: imIn is read-only and the returned image is a distinct allocation.
 */
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

    /* Shortcuts */
    if (imIn->bands == 1) {
        return ImagingCopy(imIn);
    }

    /* Special case for LXXA etc */
    if (imIn->bands == 2 && band == 1) {
        band = 3;
    }

    imOut = ImagingNewDirty(IMAGING_MODE_L, imIn->xsize, imIn->ysize);
    if (!imOut) {
        return NULL;
    }

    /* Extract band from image */
    // restrict safe: imIn is read-only, imOut is a fresh allocation.
    int xsize = imIn->xsize;
    int ysize = imIn->ysize;
    for (y = 0; y < ysize; y++) {
        UINT8 *restrict in = (UINT8 *)imIn->image[y] + band;
        UINT8 *restrict out = imOut->image8[y];
        x = 0;
        for (; x < xsize - 3; x += 4) {
            UINT32 v = MAKE_UINT32(in[0], in[4], in[8], in[12]);
            memcpy(out + x, &v, sizeof(v));
            in += 16;
        }
        for (; x < xsize; x++) {
            out[x] = *in;
            in += 4;
        }
    }

    return imOut;
}

/**
 * Split imIn into its component bands.
 * The caller must provide an array of 4 Imaging pointers,
 * which will be allocated and filled with the individual bands.
 * The number of bands returned is the number of bands in imIn.
 *
 * Contract: imIn is read-only.
 */
int
ImagingSplit(Imaging imIn, Imaging bands[4]) {
    int i, j, x, y;

    /* Check arguments */
    if (!imIn || imIn->type != IMAGING_TYPE_UINT8) {
        (void)ImagingError_ModeError();
        return 0;
    }

    /* Shortcuts */
    if (imIn->bands == 1) {
        bands[0] = ImagingCopy(imIn);
        return imIn->bands;
    }

    for (i = 0; i < imIn->bands; i++) {
        bands[i] = ImagingNewDirty(IMAGING_MODE_L, imIn->xsize, imIn->ysize);
        if (!bands[i]) {
            for (j = 0; j < i; ++j) {
                ImagingDelete(bands[j]);
            }
            return 0;
        }
    }

    /* Extract bands from image */
    // restrict safe: imIn is read-only and each band is a distinct fresh
    // allocation, so none of in/out0..out3 alias each other.
    int xsize = imIn->xsize;
    int ysize = imIn->ysize;
    if (imIn->bands == 2) {
        for (y = 0; y < ysize; y++) {
            UINT8 *restrict in = (UINT8 *)imIn->image[y];
            UINT8 *restrict out0 = bands[0]->image8[y];
            UINT8 *restrict out1 = bands[1]->image8[y];
            x = 0;
            for (; x < xsize - 3; x += 4) {
                UINT32 v = MAKE_UINT32(in[0], in[4], in[8], in[12]);
                memcpy(out0 + x, &v, sizeof(v));
                v = MAKE_UINT32(in[0 + 3], in[4 + 3], in[8 + 3], in[12 + 3]);
                memcpy(out1 + x, &v, sizeof(v));
                in += 16;
            }
            for (; x < xsize; x++) {
                out0[x] = in[0];
                out1[x] = in[3];
                in += 4;
            }
        }
    } else if (imIn->bands == 3) {
        for (y = 0; y < ysize; y++) {
            UINT8 *restrict in = (UINT8 *)imIn->image[y];
            UINT8 *restrict out0 = bands[0]->image8[y];
            UINT8 *restrict out1 = bands[1]->image8[y];
            UINT8 *restrict out2 = bands[2]->image8[y];
            x = 0;
            for (; x < xsize - 3; x += 4) {
                UINT32 v = MAKE_UINT32(in[0], in[4], in[8], in[12]);
                memcpy(out0 + x, &v, sizeof(v));
                v = MAKE_UINT32(in[0 + 1], in[4 + 1], in[8 + 1], in[12 + 1]);
                memcpy(out1 + x, &v, sizeof(v));
                v = MAKE_UINT32(in[0 + 2], in[4 + 2], in[8 + 2], in[12 + 2]);
                memcpy(out2 + x, &v, sizeof(v));
                in += 16;
            }
            for (; x < xsize; x++) {
                out0[x] = in[0];
                out1[x] = in[1];
                out2[x] = in[2];
                in += 4;
            }
        }
    } else {
        for (y = 0; y < ysize; y++) {
            UINT8 *restrict in = (UINT8 *)imIn->image[y];
            UINT8 *restrict out0 = bands[0]->image8[y];
            UINT8 *restrict out1 = bands[1]->image8[y];
            UINT8 *restrict out2 = bands[2]->image8[y];
            UINT8 *restrict out3 = bands[3]->image8[y];
            x = 0;
            for (; x < xsize - 3; x += 4) {
                UINT32 v = MAKE_UINT32(in[0], in[4], in[8], in[12]);
                memcpy(out0 + x, &v, sizeof(v));
                v = MAKE_UINT32(in[0 + 1], in[4 + 1], in[8 + 1], in[12 + 1]);
                memcpy(out1 + x, &v, sizeof(v));
                v = MAKE_UINT32(in[0 + 2], in[4 + 2], in[8 + 2], in[12 + 2]);
                memcpy(out2 + x, &v, sizeof(v));
                v = MAKE_UINT32(in[0 + 3], in[4 + 3], in[8 + 3], in[12 + 3]);
                memcpy(out3 + x, &v, sizeof(v));
                in += 16;
            }
            for (; x < xsize; x++) {
                out0[x] = in[0];
                out1[x] = in[1];
                out2[x] = in[2];
                out3[x] = in[3];
                in += 4;
            }
        }
    }

    return imIn->bands;
}

/**
 * Insert single-band imIn into `band` of imOut, in place.
 *
 * Contract: imIn and imOut MUST be distinct images and not alias.
 */
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

    /* Shortcuts */
    if (imOut->bands == 1) {
        return ImagingCopy2(imOut, imIn);
    }

    /* Special case for LXXA etc */
    if (imOut->bands == 2 && band == 1) {
        band = 3;
    }

    /* Insert band into image */
    // restrict safe: imIn is single-band (bands verified 1),
    // imOut must be multi-band or we would have shortcut out above,
    // so they're distinct images with disparate buffers.
    int xsize = imIn->xsize;
    int ysize = imIn->ysize;
    for (y = 0; y < ysize; y++) {
        UINT8 *restrict in = imIn->image8[y];
        UINT8 *restrict out = (UINT8 *)imOut->image[y] + band;
        for (x = 0; x < xsize; x++) {
            *out = in[x];
            out += 4;
        }
    }

    return imOut;
}

/**
 * Fill a single band of imOut with a constant colour, in place.
 */
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

    /* Special case for LXXA etc */
    if (imOut->bands == 2 && band == 1) {
        band = 3;
    }

    color = CLIP8(color);

    /* Insert color into image */
    int xsize = imOut->xsize;
    int ysize = imOut->ysize;
    for (y = 0; y < ysize; y++) {
        UINT8 *restrict out = (UINT8 *)imOut->image[y] + band;
        for (x = 0; x < xsize; x++) {
            *out = (UINT8)color;
            out += 4;
        }
    }

    return imOut;
}

/**
 * Merge the caller-supplied bands[] into a newly allocated multi-band image.
 *
 * Contract: the bands[] inputs are read-only, and the output is new.
 */
Imaging
ImagingMerge(const ModeID mode, Imaging bands[4]) {
    int i, x, y;
    int bandsCount = 0;
    Imaging imOut;
    Imaging firstBand;

    firstBand = bands[0];
    if (!firstBand) {
        return (Imaging)ImagingError_ValueError("wrong number of bands");
    }

    for (i = 0; i < 4; ++i) {
        if (!bands[i]) {
            break;
        }
        if (bands[i]->bands != 1) {
            return (Imaging)ImagingError_ModeError();
        }
        if (bands[i]->xsize != firstBand->xsize ||
            bands[i]->ysize != firstBand->ysize) {
            return (Imaging)ImagingError_Mismatch();
        }
    }
    bandsCount = i;

    imOut = ImagingNewDirty(mode, firstBand->xsize, firstBand->ysize);
    if (!imOut) {
        return NULL;
    }

    if (imOut->bands != bandsCount) {
        ImagingDelete(imOut);
        return (Imaging)ImagingError_ValueError("wrong number of bands");
    }

    if (imOut->bands == 1) {
        return ImagingCopy2(imOut, firstBand);
    }

    // restrict safe: the input bands are read-only and imOut is a fresh
    // allocation, so none of in0..in3/out alias each other.
    int xsize = imOut->xsize;
    int ysize = imOut->ysize;
    if (imOut->bands == 2) {
        for (y = 0; y < ysize; y++) {
            UINT8 *restrict in0 = bands[0]->image8[y];
            UINT8 *restrict in1 = bands[1]->image8[y];
            UINT32 *restrict out = (UINT32 *)imOut->image32[y];
            for (x = 0; x < xsize; x++) {
                out[x] = MAKE_UINT32(in0[x], 0, 0, in1[x]);
            }
        }
    } else if (imOut->bands == 3) {
        for (y = 0; y < ysize; y++) {
            UINT8 *restrict in0 = bands[0]->image8[y];
            UINT8 *restrict in1 = bands[1]->image8[y];
            UINT8 *restrict in2 = bands[2]->image8[y];
            UINT32 *restrict out = (UINT32 *)imOut->image32[y];
            for (x = 0; x < xsize; x++) {
                out[x] = MAKE_UINT32(in0[x], in1[x], in2[x], 0);
            }
        }
    } else if (imOut->bands == 4) {
        for (y = 0; y < ysize; y++) {
            UINT8 *restrict in0 = bands[0]->image8[y];
            UINT8 *restrict in1 = bands[1]->image8[y];
            UINT8 *restrict in2 = bands[2]->image8[y];
            UINT8 *restrict in3 = bands[3]->image8[y];
            UINT32 *restrict out = (UINT32 *)imOut->image32[y];
            for (x = 0; x < xsize; x++) {
                out[x] = MAKE_UINT32(in0[x], in1[x], in2[x], in3[x]);
            }
        }
    }

    return imOut;
}
