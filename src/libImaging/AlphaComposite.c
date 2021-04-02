/*
 * The Python Imaging Library
 * $Id$
 *
 * Alpha composite imSrc over imDst.
 * https://en.wikipedia.org/wiki/Alpha_compositing
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

#define PRECISION_BITS 7

typedef struct {
    UINT8 r;
    UINT8 g;
    UINT8 b;
    UINT8 a;
} rgba8;

Imaging
ImagingAlphaComposite(Imaging imDst, Imaging imSrc) {
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imDst || !imSrc || strcmp(imDst->mode, "RGBA") ||
        imDst->type != IMAGING_TYPE_UINT8 || imDst->bands != 4) {
        return ImagingError_ModeError();
    }

    if (strcmp(imDst->mode, imSrc->mode) || imDst->type != imSrc->type ||
        imDst->bands != imSrc->bands || imDst->xsize != imSrc->xsize ||
        imDst->ysize != imSrc->ysize) {
        return ImagingError_Mismatch();
    }

    imOut = ImagingNewDirty(imDst->mode, imDst->xsize, imDst->ysize);
    if (!imOut) {
        return NULL;
    }

    for (y = 0; y < imDst->ysize; y++) {
        rgba8 *dst = (rgba8 *)imDst->image[y];
        rgba8 *src = (rgba8 *)imSrc->image[y];
        rgba8 *out = (rgba8 *)imOut->image[y];

        for (x = 0; x < imDst->xsize; x++) {
            if (src->a == 0) {
                // Copy 4 bytes at once.
                *out = *dst;
            } else {
                // Integer implementation with increased precision.
                // Each variable has extra meaningful bits.
                // Divisions are rounded.

                UINT32 tmpr, tmpg, tmpb;
                UINT32 blend = dst->a * (255 - src->a);
                UINT32 outa255 = src->a * 255 + blend;
                // There we use 7 bits for precision.
                // We could use more, but we go beyond 32 bits.
                UINT32 coef1 = src->a * 255 * 255 * (1 << PRECISION_BITS) / outa255;
                UINT32 coef2 = 255 * (1 << PRECISION_BITS) - coef1;

                tmpr = src->r * coef1 + dst->r * coef2;
                tmpg = src->g * coef1 + dst->g * coef2;
                tmpb = src->b * coef1 + dst->b * coef2;
                out->r =
                    SHIFTFORDIV255(tmpr + (0x80 << PRECISION_BITS)) >> PRECISION_BITS;
                out->g =
                    SHIFTFORDIV255(tmpg + (0x80 << PRECISION_BITS)) >> PRECISION_BITS;
                out->b =
                    SHIFTFORDIV255(tmpb + (0x80 << PRECISION_BITS)) >> PRECISION_BITS;
                out->a = SHIFTFORDIV255(outa255 + 0x80);
            }

            dst++;
            src++;
            out++;
        }
    }

    return imOut;
}
