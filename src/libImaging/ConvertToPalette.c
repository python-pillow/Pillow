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

#if defined(_MSC_VER)
#pragma optimize("", off)
#endif

/**
 * Internal function to convert a grayscale image to a palette image.
 * The palette is assumed to be the grayscale ramp, so we can just copy the data as is.
 * imOut and imIn MUST be different images.
 */
static void
topalette_grayscale(Imaging imOut, Imaging imIn) {
    int alpha = imOut->mode == IMAGING_MODE_PA;
    /* Grayscale palette: copy data as is */
    ImagingSectionCookie cookie;
    ImagingSectionEnter(&cookie);
    int xsize = imIn->xsize, ysize = imIn->ysize;
    if (alpha) {
        for (int y = 0; y < ysize; y++) {
            // Restrict safe: we know imOut and imIn to be different images
            UINT8 *restrict in = (UINT8 *)imIn->image[y];
            UINT8 *restrict out = (UINT8 *)imOut->image[y];
            for (int x = 0; x < xsize; x++) {
                UINT8 v = *in++;
                *out++ = v;
                *out++ = v;
                *out++ = v;
                *out++ = 255;
            }
        }
    } else {
        for (int y = 0; y < imIn->ysize; y++) {
            memcpy(imOut->image[y], imIn->image[y], imIn->linesize);
        }
    }
    ImagingSectionLeave(&cookie);
}

/**
 * Internal function to convert a colour image to a palette image using
 * the Floyd-Steinberg dithering algorithm.
 * imOut and imIn MUST be different images.
 * @return 0 on success, 1 on memory allocation failure (PyErr is set).
 */
static int
topalette_colour_floyd_steinberg(Imaging imOut, Imaging imIn, ImagingPalette palette) {
    int alpha = imOut->mode == IMAGING_MODE_PA;
    int *errors = calloc(imIn->xsize + 1, sizeof(int) * 3);
    if (!errors) {
        ImagingError_MemoryError();  // Sets the exception
        return 1;
    }

    /* Map each pixel to the nearest palette entry */

    ImagingSectionCookie cookie;
    ImagingSectionEnter(&cookie);
    for (int y = 0; y < imIn->ysize; y++) {
        int r, r0, r1, r2;
        int g, g0, g1, g2;
        int b, b0, b1, b2;
        UINT8 *in = (UINT8 *)imIn->image[y];
        UINT8 *out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];
        int *e = errors;

        r = r0 = r1 = 0;
        g = g0 = g1 = 0;
        b = b0 = b1 = b2 = 0;

        for (int x = 0; x < imIn->xsize; x++, in += 4) {
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
    return 0;
}

/**
 * Internal function to convert a colour image to a palette image using the closest
 * colour. imOut and imIn MUST be different images.
 */
static void
topalette_colour_closest(Imaging imOut, Imaging imIn, ImagingPalette palette) {
    int alpha = imOut->mode == IMAGING_MODE_PA;
    ImagingSectionCookie cookie;
    ImagingSectionEnter(&cookie);
    for (int y = 0; y < imIn->ysize; y++) {
        int r, g, b;
        UINT8 *in = (UINT8 *)imIn->image[y];
        UINT8 *out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];

        for (int x = 0; x < imIn->xsize; x++, in += 4) {
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

Imaging
topalette(
    Imaging imOut, Imaging imIn, const ModeID mode, ImagingPalette inpalette, int dither
) {
    ImagingPalette palette = inpalette;

    /* Map L or RGB/RGBX/RGBA/RGBa to palette image */
    if (imIn->mode != IMAGING_MODE_L && imIn->mode != IMAGING_MODE_RGB &&
        imIn->mode != IMAGING_MODE_RGBX && imIn->mode != IMAGING_MODE_RGBA &&
        imIn->mode != IMAGING_MODE_RGBa) {
        return (Imaging)ImagingError_ValueError("conversion not supported");
    }

    if (palette == NULL) {
        /* FIXME: make user configurable */
        if (imIn->bands == 1) {
            palette = ImagingPaletteNew(IMAGING_MODE_RGB);
            if (!palette) {  // Exception has been set by ImagingPaletteNew
                return NULL;
            }

            palette->size = 256;
            for (int i = 0; i < 256; i++) {
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
    if (!imOut->palette) {  // Exception has been set by ImagingPaletteDuplicate
        goto done;
    }

    if (imIn->bands == 1) {
        topalette_grayscale(imOut, imIn);
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
            if (topalette_colour_floyd_steinberg(imOut, imIn, palette) != 0) {
                // Exception will have been set by the work function
                ImagingDelete(imOut);
                return NULL;
            }
        } else {
            topalette_colour_closest(imOut, imIn, palette);
        }
        if (inpalette != palette) {
            // If we created a temporary palette, delete the cache to free memory
            ImagingPaletteCacheDelete(palette);
        }
    }

    if (inpalette != palette) {
        // If we created a temporary palette, delete it to free memory
        ImagingPaletteDelete(palette);
    }

    return imOut;
}

#if defined(_MSC_VER)
#pragma optimize("", on)
#endif
