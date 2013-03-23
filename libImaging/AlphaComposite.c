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

        rgba8* pdst = (rgba8*) imDst->image[y];
        rgba8* psrc = (rgba8*) imSrc->image[y];
        rgba8* pout = (rgba8*) imOut->image[y];

        for (x = 0; x < imDst->xsize; x ++) {
            rgba8 src = psrc[x];

            if (src.a == 0) {
                // Copy 4 bytes at once.
                pout[x] = pdst[x];
            } else {
                rgba8 dst = pdst[x];
                rgba8* out = &pout[x];

                // Integer implementation with increased precision.
                // Each variable has extra meaningful bits.
                // Divisions are rounded.

                UINT16 blend = dst.a * (255 - src.a);  // 16 bit max
                UINT16 outa = (src.a << 4) + ((blend + 0x8) >> 4);  // 12
                UINT16 coef1 = (src.a << 16) / outa;  // 12
                UINT16 coef2 = (blend << 8) / outa;  // 12

                out->r = (src.r * coef1 + dst.r * coef2 + 0x800) >> 12;
                out->g = (src.g * coef1 + dst.g * coef2 + 0x800) >> 12;
                out->b = (src.b * coef1 + dst.b * coef2 + 0x800) >> 12;
                out->a = (outa + 0x8) >> 4;
            }

        }

    }

    return imOut;
}
