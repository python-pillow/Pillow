/*
 * The Python Imaging Library
 * $Id$
 *
 * point (pixel) translation
 *
 * history:
 * 1995-11-27 fl   Created
 * 1996-03-31 fl   Fixed colour support
 * 1996-08-13 fl   Support 8-bit to "1" thresholding
 * 1997-05-31 fl   Added floating point transform
 * 1998-07-02 fl   Added integer point transform
 * 1998-07-17 fl   Support L to anything lookup
 * 2004-12-18 fl   Refactored; added I to L lookup
 *
 * Copyright (c) 1997-2004 by Secret Labs AB.
 * Copyright (c) 1995-2004 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

typedef struct {
    const void *table;
} im_point_context;

// Note: all point handlers must fill the entirety of `imOut`,
//       as it is allocated dirty by `ImagingPoint`.

/**
 * Contract: imIn is read-only and imOut must be a distinct image.
 */
static void
im_point_8_8(Imaging imOut, Imaging imIn, im_point_context *context) {
    /* 8-bit source, 8-bit destination */
    UINT8 *table = (UINT8 *)context->table;
    // Invariant over the loop.
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // restrict safe: imIn is read-only, imOut is a fresh allocation.
        UINT8 *restrict in = imIn->image8[y];
        UINT8 *restrict out = imOut->image8[y];
        for (int x = 0; x < xsize; x++) {
            out[x] = table[in[x]];
        }
    }
}

/**
 * Contract: imIn is read-only and imOut must be a distinct image.
 */
static void
im_point_2x8_2x8(Imaging imOut, Imaging imIn, im_point_context *context) {
    /* 2x8-bit source, 2x8-bit destination */
    UINT8 *table = (UINT8 *)context->table;
    // Invariant over the loop.
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // restrict safe: imIn is read-only, imOut is a fresh allocation.
        UINT8 *restrict in = (UINT8 *)imIn->image[y];
        UINT8 *restrict out = (UINT8 *)imOut->image[y];
        for (int x = 0; x < xsize; x++) {
            out[0] = table[in[0]];
            out[1] = 0;
            out[2] = 0;
            out[3] = table[in[3] + 256];
            in += 4;
            out += 4;
        }
    }
}

/**
 * Contract: imIn is read-only and imOut must be a distinct image.
 */
static void
im_point_3x8_3x8(Imaging imOut, Imaging imIn, im_point_context *context) {
    /* 3x8-bit source, 3x8-bit destination */
    UINT8 *table = (UINT8 *)context->table;
    // Invariant over the loop.
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // restrict safe: imIn is read-only, imOut is a fresh allocation.
        UINT8 *restrict in = (UINT8 *)imIn->image[y];
        UINT8 *restrict out = (UINT8 *)imOut->image[y];
        for (int x = 0; x < xsize; x++) {
            out[0] = table[in[0]];
            out[1] = table[in[1] + 256];
            out[2] = table[in[2] + 512];
            out[3] = 0;
            in += 4;
            out += 4;
        }
    }
}

/**
 * Contract: imIn is read-only and imOut must be a distinct image.
 */
static void
im_point_4x8_4x8(Imaging imOut, Imaging imIn, im_point_context *context) {
    /* 4x8-bit source, 4x8-bit destination */
    UINT8 *table = (UINT8 *)context->table;
    // Invariant over the loop.
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // restrict safe: imIn is read-only, imOut is a fresh allocation.
        UINT8 *restrict in = (UINT8 *)imIn->image[y];
        UINT8 *restrict out = (UINT8 *)imOut->image[y];
        for (int x = 0; x < xsize; x++) {
            out[0] = table[in[0]];
            out[1] = table[in[1] + 256];
            out[2] = table[in[2] + 512];
            out[3] = table[in[3] + 768];
            in += 4;
            out += 4;
        }
    }
}

/**
 * Contract: imIn is read-only and imOut must be a distinct image.
 */
static void
im_point_8_32(Imaging imOut, Imaging imIn, im_point_context *context) {
    /* 8-bit source, 32-bit destination */
    char *table = (char *)context->table;
    // Invariant over the loop.
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // restrict safe: imIn is read-only, imOut is a fresh allocation.
        UINT8 *restrict in = imIn->image8[y];
        INT32 *restrict out = imOut->image32[y];
        for (int x = 0; x < xsize; x++) {
            memcpy(out + x, table + in[x] * sizeof(INT32), sizeof(INT32));
        }
    }
}

/**
 * Contract: imIn is read-only and imOut must be a distinct image.
 */
static void
im_point_32_8(Imaging imOut, Imaging imIn, im_point_context *context) {
    /* 32-bit source, 8-bit destination */
    UINT8 *table = (UINT8 *)context->table;
    // Invariant over the loop.
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // restrict safe: imIn is read-only, imOut is a fresh allocation.
        INT32 *restrict in = imIn->image32[y];
        UINT8 *restrict out = imOut->image8[y];
        for (int x = 0; x < xsize; x++) {
            int v = in[x];
            if (v < 0) {
                v = 0;
            } else if (v > 65535) {
                v = 65535;
            }
            out[x] = table[v];
        }
    }
}

Imaging
ImagingPoint(Imaging imIn, ModeID mode, const void *table) {
    /* lookup table transform */

    ImagingSectionCookie cookie;
    Imaging imOut;
    im_point_context context;
    void (*point)(Imaging imIn, Imaging imOut, im_point_context *context);

    if (!imIn) {
        return (Imaging)ImagingError_ModeError();
    }

    if (mode == IMAGING_MODE_UNKNOWN) {
        mode = imIn->mode;
    }

    if (imIn->type != IMAGING_TYPE_UINT8) {
        if (imIn->type != IMAGING_TYPE_INT32 || mode != IMAGING_MODE_L) {
            goto mode_mismatch;
        }
    } else if (!imIn->image8 && imIn->mode != mode) {
        goto mode_mismatch;
    }

    imOut = ImagingNewDirty(mode, imIn->xsize, imIn->ysize);
    if (!imOut) {
        return NULL;
    }

    /* find appropriate handler */
    if (imIn->type == IMAGING_TYPE_UINT8) {
        if (imIn->bands == imOut->bands && imIn->type == imOut->type) {
            switch (imIn->bands) {
                case 1:
                    point = im_point_8_8;
                    break;
                case 2:
                    point = im_point_2x8_2x8;
                    break;
                case 3:
                    point = im_point_3x8_3x8;
                    break;
                case 4:
                    point = im_point_4x8_4x8;
                    break;
                default:
                    /* this cannot really happen */
                    point = im_point_8_8;
                    break;
            }
        } else {
            point = im_point_8_32;
        }
    } else {
        point = im_point_32_8;
    }

    ImagingCopyPalette(imOut, imIn);

    ImagingSectionEnter(&cookie);

    context.table = table;
    point(imOut, imIn, &context);

    ImagingSectionLeave(&cookie);

    return imOut;

mode_mismatch:
    return (Imaging)ImagingError_ValueError(
        "point operation not supported for this mode"
    );
}

/**
 * Apply an affine (scale/offset) transform to every pixel of imIn,
 * returning a newly allocated result.
 *
 * Contract: imIn is read-only.
 */
Imaging
ImagingPointTransform(Imaging imIn, double scale, double offset) {
    /* scale/offset transform */

    ImagingSectionCookie cookie;
    Imaging imOut;

    if (!imIn || (imIn->mode != IMAGING_MODE_I && imIn->mode != IMAGING_MODE_I_16 &&
                  imIn->mode != IMAGING_MODE_F)) {
        return (Imaging)ImagingError_ModeError();
    }

    // Invariant over the loops.
    int xsize = imIn->xsize, ysize = imIn->ysize;

    imOut = ImagingNewDirty(imIn->mode, xsize, ysize);
    if (!imOut) {
        return NULL;
    }

    switch (imIn->type) {
        case IMAGING_TYPE_INT32:
            ImagingSectionEnter(&cookie);
            for (int y = 0; y < ysize; y++) {
                // restrict safe: imIn is read-only, imOut is a fresh allocation.
                INT32 *restrict in = imIn->image32[y];
                INT32 *restrict out = imOut->image32[y];
                /* FIXME: add clipping? */
                for (int x = 0; x < xsize; x++) {
                    out[x] = in[x] * scale + offset;
                }
            }
            ImagingSectionLeave(&cookie);
            break;
        case IMAGING_TYPE_FLOAT32:
            ImagingSectionEnter(&cookie);
            for (int y = 0; y < ysize; y++) {
                // restrict safe: imIn is read-only, imOut is a fresh allocation.
                FLOAT32 *restrict in = (FLOAT32 *)imIn->image32[y];
                FLOAT32 *restrict out = (FLOAT32 *)imOut->image32[y];
                for (int x = 0; x < xsize; x++) {
                    out[x] = in[x] * scale + offset;
                }
            }
            ImagingSectionLeave(&cookie);
            break;
        case IMAGING_TYPE_SPECIAL:
            if (imIn->mode == IMAGING_MODE_I_16) {
                ImagingSectionEnter(&cookie);
                for (int y = 0; y < ysize; y++) {
                    // restrict safe: imIn is read-only, imOut is a fresh allocation.
                    char *restrict in = imIn->image[y];
                    char *restrict out = imOut->image[y];
                    /* FIXME: add clipping? */
                    for (int x = 0; x < xsize; x++) {
                        UINT16 v;
                        memcpy(&v, in + x * sizeof(v), sizeof(v));
                        v = v * scale + offset;
                        memcpy(out + x * sizeof(UINT16), &v, sizeof(v));
                    }
                }
                ImagingSectionLeave(&cookie);
                break;
            }
            /* FALL THROUGH */
        default:
            ImagingDelete(imOut);
            return (Imaging)ImagingError_ValueError("internal error");
    }

    return imOut;
}
