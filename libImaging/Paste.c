/*
 * The Python Imaging Library
 * $Id$
 *
 * paste image on another image
 *
 * history:
 * 96-03-27 fl  Created
 * 96-07-16 fl  Support "1", "L" and "RGBA" masks
 * 96-08-16 fl  Merged with opaque paste
 * 97-01-17 fl  Faster blending, added support for RGBa images
 * 97-08-27 fl  Faster masking for 32-bit images
 * 98-02-02 fl  Fixed MULDIV255 macro for gcc
 * 99-02-02 fl  Added "RGBa" mask support
 * 99-02-06 fl  Rewritten.  Added support for masked fill operations.
 * 99-12-08 fl  Fixed matte fill.
 *
 * Copyright (c) Fredrik Lundh 1996-97.
 * Copyright (c) Secret Labs AB 1997-99.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"


static inline void
paste(Imaging imOut, Imaging imIn, int dx, int dy, int sx, int sy,
      int xsize, int ysize, int pixelsize)
{
    /* paste opaque region */

    int y;

    dx *= pixelsize;
    sx *= pixelsize;

    xsize *= pixelsize;

    for (y = 0; y < ysize; y++)
        memcpy(imOut->image[y+dy]+dx, imIn->image[y+sy]+sx, xsize);
}

static inline void
paste_mask_1(Imaging imOut, Imaging imIn, Imaging imMask,
             int dx, int dy, int sx, int sy,
             int xsize, int ysize, int pixelsize)
{
    /* paste with mode "1" mask */

    int x, y;

    if (imOut->image8) {

        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* in = imIn->image8[y+sy]+sx;
            UINT8* mask = imMask->image8[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                if (*mask++)
                    *out = *in;
                out++, in++;
            }
        }

    } else {

        for (y = 0; y < ysize; y++) {
            INT32* out = imOut->image32[y+dy]+dx;
            INT32* in = imIn->image32[y+sy]+sx;
            UINT8* mask = imMask->image8[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                if (*mask++)
                    *out = *in;
                out++, in++;
            }
        }
    }
}

static inline void
paste_mask_L(Imaging imOut, Imaging imIn, Imaging imMask,
             int dx, int dy, int sx, int sy,
             int xsize, int ysize, int pixelsize)
{
    /* paste with mode "L" matte */

    int x, y;
    unsigned int tmp1;

    if (imOut->image8) {

        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* in = imIn->image8[y+sy]+sx;
            UINT8* mask = imMask->image8[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                *out = BLEND(*mask, *out, *in, tmp1);
                out++, in++, mask++;
            }
        }

    } else {

        for (y = 0; y < ysize; y++) {
            UINT8* out = (UINT8*) (imOut->image32[y + dy] + dx);
            UINT8* in = (UINT8*) (imIn->image32[y + sy] + sx);
            UINT8* mask = (UINT8*) (imMask->image8[y+sy] + sx);
            for (x = 0; x < xsize; x++) {
                UINT8 a = mask[0];
                out[0] = BLEND(a, out[0], in[0], tmp1);
                out[1] = BLEND(a, out[1], in[1], tmp1);
                out[2] = BLEND(a, out[2], in[2], tmp1);
                out[3] = BLEND(a, out[3], in[3], tmp1);
                out += 4; in += 4; mask ++;
            }
        }
    }
}

static inline void
paste_mask_RGBA(Imaging imOut, Imaging imIn, Imaging imMask,
                int dx, int dy, int sx, int sy,
                int xsize, int ysize, int pixelsize)
{
    /* paste with mode "RGBA" matte */

    int x, y;
    unsigned int tmp1;

    if (imOut->image8) {

        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* in = imIn->image8[y+sy]+sx;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx*4+3;
            for (x = 0; x < xsize; x++) {
                *out = BLEND(*mask, *out, *in, tmp1);
                out++, in++, mask += 4;
            }
        }

    } else {

        for (y = 0; y < ysize; y++) {
            UINT8* out = (UINT8*) (imOut->image32[y + dy] + dx);
            UINT8* in = (UINT8*) (imIn->image32[y + sy] + sx);
            UINT8* mask = (UINT8*) (imMask->image32[y+sy] + sx);
            for (x = 0; x < xsize; x++) {
                UINT8 a = mask[3];
                out[0] = BLEND(a, out[0], in[0], tmp1);
                out[1] = BLEND(a, out[1], in[1], tmp1);
                out[2] = BLEND(a, out[2], in[2], tmp1);
                out[3] = BLEND(a, out[3], in[3], tmp1);
                out += 4; in += 4; mask += 4;
            }
        }
    }
}


static inline void
paste_mask_RGBa(Imaging imOut, Imaging imIn, Imaging imMask,
                int dx, int dy, int sx, int sy,
                int xsize, int ysize, int pixelsize)
{
    /* paste with mode "RGBa" matte */

    int x, y;
    unsigned int tmp1;

    if (imOut->image8) {

        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* in = imIn->image8[y+sy]+sx;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx*4+3;
            for (x = 0; x < xsize; x++) {
                *out = PREBLEND(*mask, *out, *in, tmp1);
                out++, in++, mask += 4;
            }
        }

    } else {

        for (y = 0; y < ysize; y++) {
            UINT8* out = (UINT8*) (imOut->image32[y + dy] + dx);
            UINT8* in = (UINT8*) (imIn->image32[y + sy] + sx);
            UINT8* mask = (UINT8*) (imMask->image32[y+sy] + sx);
            for (x = 0; x < xsize; x++) {
                UINT8 a = mask[3];
                out[0] = PREBLEND(a, out[0], in[0], tmp1);
                out[1] = PREBLEND(a, out[1], in[1], tmp1);
                out[2] = PREBLEND(a, out[2], in[2], tmp1);
                out[3] = PREBLEND(a, out[3], in[3], tmp1);
                out += 4; in += 4; mask += 4;
            }
        }
    }
}

int
ImagingPaste(Imaging imOut, Imaging imIn, Imaging imMask,
             int dx0, int dy0, int dx1, int dy1)
{
    int xsize, ysize;
    int pixelsize;
    int sx0, sy0;
    ImagingSectionCookie cookie;

    if (!imOut || !imIn) {
        (void) ImagingError_ModeError();
        return -1;
    }

    pixelsize = imOut->pixelsize;

    xsize = dx1 - dx0;
    ysize = dy1 - dy0;

    if (xsize != imIn->xsize || ysize != imIn->ysize ||
        pixelsize != imIn->pixelsize) {
        (void) ImagingError_Mismatch();
        return -1;
    }

    if (imMask && (xsize != imMask->xsize || ysize != imMask->ysize)) {
        (void) ImagingError_Mismatch();
        return -1;
    }

    /* Determine which region to copy */
    sx0 = sy0 = 0;
    if (dx0 < 0)
        xsize += dx0, sx0 = -dx0, dx0 = 0;
    if (dx0 + xsize > imOut->xsize)
        xsize = imOut->xsize - dx0;
    if (dy0 < 0)
        ysize += dy0, sy0 = -dy0, dy0 = 0;
    if (dy0 + ysize > imOut->ysize)
        ysize = imOut->ysize - dy0;

    if (xsize <= 0 || ysize <= 0)
        return 0;

    if (!imMask) {
        ImagingSectionEnter(&cookie);
        paste(imOut, imIn, dx0, dy0, sx0, sy0, xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "1") == 0) {
        ImagingSectionEnter(&cookie);
        paste_mask_1(imOut, imIn, imMask, dx0, dy0, sx0, sy0,
                     xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "L") == 0) {
        ImagingSectionEnter(&cookie);
        paste_mask_L(imOut, imIn, imMask, dx0, dy0, sx0, sy0,
                     xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "RGBA") == 0) {
        ImagingSectionEnter(&cookie);
        paste_mask_RGBA(imOut, imIn, imMask, dx0, dy0, sx0, sy0,
                        xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "RGBa") == 0) {
        ImagingSectionEnter(&cookie);
        paste_mask_RGBa(imOut, imIn, imMask, dx0, dy0, sx0, sy0,
                        xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else {
        (void) ImagingError_ValueError("bad transparency mask");
        return -1;
    }

    return 0;
}

static inline void
fill(Imaging imOut, const void* ink_, int dx, int dy,
     int xsize, int ysize, int pixelsize)
{
    /* fill opaque region */

    int x, y;
    UINT8 ink8 = 0;
    INT32 ink32 = 0L;

    memcpy(&ink32, ink_, pixelsize);
    memcpy(&ink8, ink_, sizeof(ink8));

    if (imOut->image8 || ink32 == 0L) {

        dx *= pixelsize;
        xsize *= pixelsize;
        for (y = 0; y < ysize; y++)
            memset(imOut->image[y+dy]+dx, ink8, xsize);

    } else {

        for (y = 0; y < ysize; y++) {
            INT32* out = imOut->image32[y+dy]+dx;
            for (x = 0; x < xsize; x++)
                out[x] = ink32;
        }

    }
}

static inline void
fill_mask_1(Imaging imOut, const void* ink_, Imaging imMask,
            int dx, int dy, int sx, int sy,
            int xsize, int ysize, int pixelsize)
{
    /* fill with mode "1" mask */

    int x, y;
    UINT8 ink8 = 0;
    INT32 ink32 = 0L;

    memcpy(&ink32, ink_, pixelsize);
    memcpy(&ink8, ink_, sizeof(ink8));

    if (imOut->image8) {

        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* mask = imMask->image8[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                if (*mask++)
                    *out = ink8;
                out++;
            }
        }

    } else {

        for (y = 0; y < ysize; y++) {
            INT32* out = imOut->image32[y+dy]+dx;
            UINT8* mask = imMask->image8[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                if (*mask++)
                    *out = ink32;
                out++;
            }
        }
    }
}

static inline void
fill_mask_L(Imaging imOut, const UINT8* ink, Imaging imMask,
            int dx, int dy, int sx, int sy,
            int xsize, int ysize, int pixelsize)
{
    /* fill with mode "L" matte */

    int x, y, i;
    unsigned int tmp1;

    if (imOut->image8) {

        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* mask = imMask->image8[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                *out = BLEND(*mask, *out, ink[0], tmp1);
                out++, mask++;
            }
        }

    } else {

        for (y = 0; y < ysize; y++) {
            UINT8* out = (UINT8*) imOut->image[y+dy]+dx*pixelsize;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                for (i = 0; i < pixelsize; i++) {
                    *out = BLEND(*mask, *out, ink[i], tmp1);
                    out++;
                }
                mask++;
            }
        }
    }
}

static inline void
fill_mask_RGBA(Imaging imOut, const UINT8* ink, Imaging imMask,
               int dx, int dy, int sx, int sy,
               int xsize, int ysize, int pixelsize)
{
    /* fill with mode "RGBA" matte */

    int x, y, i;
    unsigned int tmp1;

    if (imOut->image8) {

        sx = sx*4+3;
        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                *out = BLEND(*mask, *out, ink[0], tmp1);
                out++, mask += 4;
            }
        }

    } else {

        dx *= pixelsize;
        sx = sx*4 + 3;
        for (y = 0; y < ysize; y++) {
            UINT8* out = (UINT8*) imOut->image[y+dy]+dx;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                for (i = 0; i < pixelsize; i++) {
                    *out = BLEND(*mask, *out, ink[i], tmp1);
                    out++;
                }
                mask += 4;
            }
        }
    }
}

static inline void
fill_mask_RGBa(Imaging imOut, const UINT8* ink, Imaging imMask,
               int dx, int dy, int sx, int sy,
               int xsize, int ysize, int pixelsize)
{
    /* fill with mode "RGBa" matte */

    int x, y, i;
    unsigned int tmp1;

    if (imOut->image8) {

        sx = sx*4 + 3;
        for (y = 0; y < ysize; y++) {
            UINT8* out = imOut->image8[y+dy]+dx;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                *out = PREBLEND(*mask, *out, ink[0], tmp1);
                out++, mask += 4;
            }
        }

    } else {

        dx *= pixelsize;
        sx = sx*4 + 3;
        for (y = 0; y < ysize; y++) {
            UINT8* out = (UINT8*) imOut->image[y+dy]+dx;
            UINT8* mask = (UINT8*) imMask->image[y+sy]+sx;
            for (x = 0; x < xsize; x++) {
                for (i = 0; i < pixelsize; i++) {
                    *out = PREBLEND(*mask, *out, ink[i], tmp1);
                    out++;
                }
                mask += 4;
            }
        }
    }
}

int
ImagingFill2(Imaging imOut, const void* ink, Imaging imMask,
             int dx0, int dy0, int dx1, int dy1)
{
    ImagingSectionCookie cookie;
    int xsize, ysize;
    int pixelsize;
    int sx0, sy0;

    if (!imOut || !ink) {
        (void) ImagingError_ModeError();
        return -1;
    }

    pixelsize = imOut->pixelsize;

    xsize = dx1 - dx0;
    ysize = dy1 - dy0;

    if (imMask && (xsize != imMask->xsize || ysize != imMask->ysize)) {
        (void) ImagingError_Mismatch();
        return -1;
    }

    /* Determine which region to fill */
    sx0 = sy0 = 0;
    if (dx0 < 0)
        xsize += dx0, sx0 = -dx0, dx0 = 0;
    if (dx0 + xsize > imOut->xsize)
        xsize = imOut->xsize - dx0;
    if (dy0 < 0)
        ysize += dy0, sy0 = -dy0, dy0 = 0;
    if (dy0 + ysize > imOut->ysize)
        ysize = imOut->ysize - dy0;

    if (xsize <= 0 || ysize <= 0)
        return 0;

    if (!imMask) {
        ImagingSectionEnter(&cookie);
        fill(imOut, ink, dx0, dy0, xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "1") == 0) {
        ImagingSectionEnter(&cookie);
        fill_mask_1(imOut, ink, imMask, dx0, dy0, sx0, sy0,
                    xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "L") == 0) {
        ImagingSectionEnter(&cookie);
        fill_mask_L(imOut, ink, imMask, dx0, dy0, sx0, sy0,
                    xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "RGBA") == 0) {
        ImagingSectionEnter(&cookie);
        fill_mask_RGBA(imOut, ink, imMask, dx0, dy0, sx0, sy0,
                       xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else if (strcmp(imMask->mode, "RGBa") == 0) {
        ImagingSectionEnter(&cookie);
        fill_mask_RGBa(imOut, ink, imMask, dx0, dy0, sx0, sy0,
                       xsize, ysize, pixelsize);
        ImagingSectionLeave(&cookie);

    } else {
        (void) ImagingError_ValueError("bad transparency mask");
        return -1;
    }

    return 0;
}
