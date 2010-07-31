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
    const void* table;
} im_point_context;

static void
im_point_8_8(Imaging imOut, Imaging imIn, im_point_context* context)
{
    int x, y;
    /* 8-bit source, 8-bit destination */
    UINT8* table = (UINT8*) context->table;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = imIn->image8[y];
        UINT8* out = imOut->image8[y];
        for (x = 0; x < imIn->xsize; x++)
            out[x] = table[in[x]];
    }
}

static void
im_point_2x8_2x8(Imaging imOut, Imaging imIn, im_point_context* context)
{
    int x, y;
    /* 2x8-bit source, 2x8-bit destination */
    UINT8* table = (UINT8*) context->table;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = (UINT8*) imIn->image[y];
        UINT8* out = (UINT8*) imOut->image[y];
        for (x = 0; x < imIn->xsize; x++) {
            out[0] = table[in[0]];
            out[3] = table[in[3]+256];
            in += 4; out += 4;
        }
    }
}

static void
im_point_3x8_3x8(Imaging imOut, Imaging imIn, im_point_context* context)
{
    int x, y;
    /* 3x8-bit source, 3x8-bit destination */
    UINT8* table = (UINT8*) context->table;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = (UINT8*) imIn->image[y];
        UINT8* out = (UINT8*) imOut->image[y];
        for (x = 0; x < imIn->xsize; x++) {
            out[0] = table[in[0]];
            out[1] = table[in[1]+256];
            out[2] = table[in[2]+512];
            in += 4; out += 4;
        }
    }
}

static void
im_point_4x8_4x8(Imaging imOut, Imaging imIn, im_point_context* context)
{
    int x, y;
    /* 4x8-bit source, 4x8-bit destination */
    UINT8* table = (UINT8*) context->table;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = (UINT8*) imIn->image[y];
        UINT8* out = (UINT8*) imOut->image[y];
        for (x = 0; x < imIn->xsize; x++) {
            out[0] = table[in[0]];
            out[1] = table[in[1]+256];
            out[2] = table[in[2]+512];
            out[3] = table[in[3]+768];
            in += 4; out += 4;
        }
    }
}

static void
im_point_8_32(Imaging imOut, Imaging imIn, im_point_context* context)
{
    int x, y;
    /* 8-bit source, 32-bit destination */
    INT32* table = (INT32*) context->table;
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = imIn->image8[y];
        INT32* out = imOut->image32[y];
        for (x = 0; x < imIn->xsize; x++)
            out[x] = table[in[x]];
    }
}

static void
im_point_32_8(Imaging imOut, Imaging imIn, im_point_context* context)
{
    int x, y;
    /* 32-bit source, 8-bit destination */
    UINT8* table = (UINT8*) context->table;
    for (y = 0; y < imIn->ysize; y++) {
        INT32* in = imIn->image32[y];
        UINT8* out = imOut->image8[y];
        for (x = 0; x < imIn->xsize; x++) {
            int v = in[x];
            if (v < 0)
                v = 0;
            else if (v > 65535)
                v = 65535;
            out[x] = table[v];
        }
    }
}

Imaging
ImagingPoint(Imaging imIn, const char* mode, const void* table)
{
    /* lookup table transform */

    ImagingSectionCookie cookie;
    Imaging imOut;
    im_point_context context;
    void (*point)(Imaging imIn, Imaging imOut, im_point_context* context);

    if (!imIn)
	return (Imaging) ImagingError_ModeError();

    if (!mode)
        mode = imIn->mode;

    if (imIn->type != IMAGING_TYPE_UINT8) {
        if (imIn->type != IMAGING_TYPE_INT32 || strcmp(mode, "L") != 0)
            goto mode_mismatch;
    } else if (!imIn->image8 && strcmp(imIn->mode, mode) != 0)
        goto mode_mismatch;

    imOut = ImagingNew(mode, imIn->xsize, imIn->ysize);
    if (!imOut)
	return NULL;

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
        } else
            point = im_point_8_32;
    } else
        point = im_point_32_8;

    ImagingCopyInfo(imOut, imIn);

    ImagingSectionEnter(&cookie);

    context.table = table;
    point(imOut, imIn, &context);

    ImagingSectionLeave(&cookie);

    return imOut;

  mode_mismatch:
    return (Imaging) ImagingError_ValueError(
        "point operation not supported for this mode"
        );
}


Imaging
ImagingPointTransform(Imaging imIn, double scale, double offset)
{
    /* scale/offset transform */

    ImagingSectionCookie cookie;
    Imaging imOut;
    int x, y;

    if (!imIn || (strcmp(imIn->mode, "I") != 0 && 
                  strcmp(imIn->mode, "I;16") != 0 && 
                  strcmp(imIn->mode, "F") != 0))
	return (Imaging) ImagingError_ModeError();

    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut)
	return NULL;

    ImagingCopyInfo(imOut, imIn);

    switch (imIn->type) {
    case IMAGING_TYPE_INT32:
        ImagingSectionEnter(&cookie);
        for (y = 0; y < imIn->ysize; y++) {
            INT32* in  = imIn->image32[y];
            INT32* out = imOut->image32[y];
            /* FIXME: add clipping? */
            for (x = 0; x < imIn->xsize; x++)
                out[x] = in[x] * scale + offset;
        }
        ImagingSectionLeave(&cookie);
        break;
    case IMAGING_TYPE_FLOAT32:
        ImagingSectionEnter(&cookie);
        for (y = 0; y < imIn->ysize; y++) {
            FLOAT32* in  = (FLOAT32*) imIn->image32[y];
            FLOAT32* out = (FLOAT32*) imOut->image32[y];
            for (x = 0; x < imIn->xsize; x++)
                out[x] = in[x] * scale + offset;
        }
        ImagingSectionLeave(&cookie);
        break;
    case IMAGING_TYPE_SPECIAL:
        if (strcmp(imIn->mode,"I;16") == 0) {
            ImagingSectionEnter(&cookie);
            for (y = 0; y < imIn->ysize; y++) {
                UINT16* in  = (UINT16 *)imIn->image[y];
                UINT16* out = (UINT16 *)imOut->image[y];
                /* FIXME: add clipping? */
                for (x = 0; x < imIn->xsize; x++)
                    out[x] = in[x] * scale + offset;
            }
            ImagingSectionLeave(&cookie);
            break;
	}
        /* FALL THROUGH */
    default:
        ImagingDelete(imOut);
        return (Imaging) ImagingError_ValueError("internal error");
    }

    return imOut;
}
