/*
 * The Python Imaging Library
 *
 * See Convert.c for legacy history of this file.
 *
 * Copyright (c) 1997-2005 by Secret Labs AB.
 * Copyright (c) 1995-1997 by Fredrik Lundh.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

// TODO: copied from Convert.c, will be removed soon
static void
l2rgb(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        UINT8 v = *in++;
        *out++ = v;
        *out++ = v;
        *out++ = v;
        *out++ = 255;
    }
}

#if defined(_MSC_VER)
#pragma optimize("", off)
#endif

Imaging
topalette(
    Imaging imOut, Imaging imIn, const ModeID mode, ImagingPalette inpalette, int dither
) {
    ImagingSectionCookie cookie;
    int alpha;
    int x, y;
    ImagingPalette palette = inpalette;

    /* Map L or RGB/RGBX/RGBA/RGBa to palette image */
    if (imIn->mode != IMAGING_MODE_L && imIn->mode != IMAGING_MODE_RGB &&
        imIn->mode != IMAGING_MODE_RGBX && imIn->mode != IMAGING_MODE_RGBA &&
        imIn->mode != IMAGING_MODE_RGBa) {
        return (Imaging)ImagingError_ValueError("conversion not supported");
    }

    alpha = mode == IMAGING_MODE_PA;

    if (palette == NULL) {
        /* FIXME: make user configurable */
        if (imIn->bands == 1) {
            palette = ImagingPaletteNew(IMAGING_MODE_RGB);

            palette->size = 256;
            int i;
            for (i = 0; i < 256; i++) {
                palette->palette[i * 4] = palette->palette[i * 4 + 1] =
                    palette->palette[i * 4 + 2] = (UINT8)i;
            }
        } else {
            palette = ImagingPaletteNewBrowser(); /* Standard colour cube */
        }
    }

    if (!palette) {
        return (Imaging)ImagingError_ValueError("no palette");
    }

    imOut = ImagingNew2Dirty(mode, imOut, imIn);
    if (!imOut) {
        if (palette != inpalette) {
            ImagingPaletteDelete(palette);
        }
        return NULL;
    }

    ImagingPaletteDelete(imOut->palette);
    imOut->palette = ImagingPaletteDuplicate(palette);

    if (imIn->bands == 1) {
        /* grayscale image */

        /* Grayscale palette: copy data as is */
        ImagingSectionEnter(&cookie);
        for (y = 0; y < imIn->ysize; y++) {
            if (alpha) {
                l2rgb((UINT8 *)imOut->image[y], (UINT8 *)imIn->image[y], imIn->xsize);
            } else {
                memcpy(imOut->image[y], imIn->image[y], imIn->linesize);
            }
        }
        ImagingSectionLeave(&cookie);

    } else {
        /* colour image */

        /* Create mapping cache */
        if (ImagingPaletteCachePrepare(palette) < 0) {
            ImagingDelete(imOut);
            if (palette != inpalette) {
                ImagingPaletteDelete(palette);
            }
            return NULL;
        }

        if (dither) {
            /* floyd-steinberg dither */

            int *errors;
            errors = calloc(imIn->xsize + 1, sizeof(int) * 3);
            if (!errors) {
                ImagingDelete(imOut);
                return ImagingError_MemoryError();
            }

            /* Map each pixel to the nearest palette entry */
            ImagingSectionEnter(&cookie);
            for (y = 0; y < imIn->ysize; y++) {
                int r, r0, r1, r2;
                int g, g0, g1, g2;
                int b, b0, b1, b2;
                UINT8 *in = (UINT8 *)imIn->image[y];
                UINT8 *out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];
                int *e = errors;

                r = r0 = r1 = 0;
                g = g0 = g1 = 0;
                b = b0 = b1 = b2 = 0;

                for (x = 0; x < imIn->xsize; x++, in += 4) {
                    int d2;
                    INT16 *cache;

                    r = CLIP8(in[0] + (r + e[3 + 0]) / 16);
                    g = CLIP8(in[1] + (g + e[3 + 1]) / 16);
                    b = CLIP8(in[2] + (b + e[3 + 2]) / 16);

                    /* get closest colour */
                    cache = &ImagingPaletteCache(palette, r, g, b);
                    if (cache[0] == 0x100) {
                        ImagingPaletteCacheUpdate(palette, r, g, b);
                    }
                    if (alpha) {
                        out[x * 4] = out[x * 4 + 1] = out[x * 4 + 2] = (UINT8)cache[0];
                        out[x * 4 + 3] = 255;
                    } else {
                        out[x] = (UINT8)cache[0];
                    }

                    r -= (int)palette->palette[cache[0] * 4];
                    g -= (int)palette->palette[cache[0] * 4 + 1];
                    b -= (int)palette->palette[cache[0] * 4 + 2];

                    /* propagate errors (don't ask ;-) */
                    r2 = r;
                    d2 = r + r;
                    r += d2;
                    e[0] = r + r0;
                    r += d2;
                    r0 = r + r1;
                    r1 = r2;
                    r += d2;
                    g2 = g;
                    d2 = g + g;
                    g += d2;
                    e[1] = g + g0;
                    g += d2;
                    g0 = g + g1;
                    g1 = g2;
                    g += d2;
                    b2 = b;
                    d2 = b + b;
                    b += d2;
                    e[2] = b + b0;
                    b += d2;
                    b0 = b + b1;
                    b1 = b2;
                    b += d2;

                    e += 3;
                }

                e[0] = b0;
                e[1] = b1;
                e[2] = b2;
            }
            ImagingSectionLeave(&cookie);
            free(errors);

        } else {
            /* closest colour */
            ImagingSectionEnter(&cookie);
            for (y = 0; y < imIn->ysize; y++) {
                int r, g, b;
                UINT8 *in = (UINT8 *)imIn->image[y];
                UINT8 *out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];

                for (x = 0; x < imIn->xsize; x++, in += 4) {
                    INT16 *cache;

                    r = in[0];
                    g = in[1];
                    b = in[2];

                    /* get closest colour */
                    cache = &ImagingPaletteCache(palette, r, g, b);
                    if (cache[0] == 0x100) {
                        ImagingPaletteCacheUpdate(palette, r, g, b);
                    }
                    if (alpha) {
                        out[x * 4] = out[x * 4 + 1] = out[x * 4 + 2] = (UINT8)cache[0];
                        out[x * 4 + 3] = 255;
                    } else {
                        out[x] = (UINT8)cache[0];
                    }
                }
            }
            ImagingSectionLeave(&cookie);
        }
        if (inpalette != palette) {
            ImagingPaletteCacheDelete(palette);
        }
    }

    if (inpalette != palette) {
        ImagingPaletteDelete(palette);
    }

    return imOut;
}

#if defined(_MSC_VER)
#pragma optimize("", on)
#endif
