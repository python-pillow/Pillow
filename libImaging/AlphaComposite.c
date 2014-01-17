/*
 * The Python Imaging Library
 * $Id$
 *
 * Alpha composite imSrc over imDst.
 * http://en.wikipedia.org/wiki/Alpha_compositing
 *
 * See the README file for details on usage and redistribution.
 */


#include "Imaging.h"


typedef struct
{
    UINT8 r;
    UINT8 g;
    UINT8 b;
    UINT8 a;
} rgba8;



Imaging
ImagingAlphaComposite(Imaging imDst, Imaging imSrc)
{
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imDst || !imSrc ||
        strcmp(imDst->mode, "RGBA") ||
        imDst->type != IMAGING_TYPE_UINT8 ||
        imDst->bands != 4)
        return ImagingError_ModeError();

    if (strcmp(imDst->mode, imSrc->mode) ||
        imDst->type  != imSrc->type  ||
        imDst->bands != imSrc->bands ||
        imDst->xsize != imSrc->xsize ||
        imDst->ysize != imSrc->ysize)
        return ImagingError_Mismatch();

    imOut = ImagingNew(imDst->mode, imDst->xsize, imDst->ysize);
    if (!imOut)
        return NULL;

    ImagingCopyInfo(imOut, imDst);

    for (y = 0; y < imDst->ysize; y++) {

        rgba8* dst = (rgba8*) imDst->image[y];
        rgba8* src = (rgba8*) imSrc->image[y];
        rgba8* out = (rgba8*) imOut->image[y];

        for (x = 0; x < imDst->xsize; x ++) {

            if (src->a == 0) {
                // Copy 4 bytes at once.
                *out = *dst;
            } else {
                // Integer implementation with increased precision.
                // Each variable has extra meaningful bits.
                // Divisions are rounded.

                // This code uses trick from Paste.c:
                // (a + (2 << (n-1)) - 1) / ((2 << n)-1)
                // almost equivalent to:
                // tmp = a + (2 << (n-1)), ((tmp >> n) + tmp) >> n

                UINT32 tmpr, tmpg, tmpb;
                UINT16 blend = dst->a * (255 - src->a);
                UINT16 outa255 = src->a * 255 + blend;
                // There we use 7 bits for precision.
                // We could use more, but we go beyond 32 bits.
                UINT16 coef1 = src->a * 255 * 255 * 128 / outa255;
                UINT16 coef2 = 255 * 128 - coef1;

                #define SHIFTFORDIV255(a)\
                    ((((a) >> 8) + a) >> 8)

                tmpr = src->r * coef1 + dst->r * coef2 + (0x80 << 7);
                out->r = SHIFTFORDIV255(tmpr) >> 7;
                tmpg = src->g * coef1 + dst->g * coef2 + (0x80 << 7);
                out->g = SHIFTFORDIV255(tmpg) >> 7;
                tmpb = src->b * coef1 + dst->b * coef2 + (0x80 << 7);
                out->b = SHIFTFORDIV255(tmpb) >> 7;
                out->a = SHIFTFORDIV255(outa255 + 0x80);
            }

            dst++; src++; out++;
        }

    }

    return imOut;
}
