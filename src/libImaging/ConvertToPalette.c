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

// The hash will always have up to 50% fill factor.
#define EXACT_COLOR_HASH_SIZE (IMAGING_PALETTE_MAX_ENTRIES * 2)

struct ExactColorHashInstance {
    UINT32 keys[EXACT_COLOR_HASH_SIZE];
    UINT8 values[EXACT_COLOR_HASH_SIZE];
};
typedef struct ExactColorHashInstance *ExactColorHash;

static UINT32
exact_color_key(int r, int g, int b) {
    UINT32 key = ((UINT32)r << 16) | ((UINT32)g << 8) | (UINT32)b;
    // Zero will mean "empty slot", so increment all keys by 1.
    return key + 1;
}

static UINT32
exact_color_hash(UINT32 key) {
    // Fibonacci hashing distributes the 25-bit keys across the 512-entry table.
    return (key * 2654435761U) >> 23;
}

static void
prepare_exact_color_hash(ImagingPalette palette, ExactColorHash ech) {
    memset(ech->keys, 0, EXACT_COLOR_HASH_SIZE * sizeof(UINT32));
    for (int i = 0; i < palette->size; i++) {
        UINT32 key = exact_color_key(
            palette->palette[i * 4],
            palette->palette[i * 4 + 1],
            palette->palette[i * 4 + 2]
        );
        UINT32 hash = exact_color_hash(key);
        // Linear probe for an empty slot.
        // Given the guarantee of at most 50% fill factor (see EXACT_COLOR_HASH_SIZE),
        // this will always terminate.
        while (ech->keys[hash] != 0 && ech->keys[hash] != key) {
            hash = (hash + 1) % EXACT_COLOR_HASH_SIZE;
        }
        if (ech->keys[hash] == 0) {
            ech->keys[hash] = key;
            ech->values[hash] = (UINT8)i;
        }
    }
}

static int
find_exact_color(const ExactColorHash ech, int r, int g, int b) {
    UINT32 key = exact_color_key(r, g, b);
    UINT32 hash = exact_color_hash(key);
    while (ech->keys[hash] != 0) {
        if (ech->keys[hash] == key) {
            return ech->values[hash];
        }
        hash = (hash + 1) % EXACT_COLOR_HASH_SIZE;
    }
    return -1;
}

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
topalette_colour_floyd_steinberg(
    Imaging imOut, Imaging imIn, ImagingPalette palette, ExactColorHash ech
) {
    int alpha = imOut->mode == IMAGING_MODE_PA;
    int xsize = imIn->xsize, ysize = imIn->ysize;
    int *errors = calloc(xsize + 1, sizeof(int) * 3);
    if (!errors) {
        ImagingError_MemoryError();  // Sets the exception
        return 1;
    }

    /* Map each pixel to the nearest palette entry */

    ImagingSectionCookie cookie;
    ImagingSectionEnter(&cookie);
    for (int y = 0; y < ysize; y++) {
        int r, r0, r1, r2;
        int g, g0, g1, g2;
        int b, b0, b1, b2;
        // Restrict safe: we know imOut and imIn to be different images
        UINT8 *restrict in = (UINT8 *)imIn->image[y];
        UINT8 *restrict out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];
        int *e = errors;

        r = r0 = r1 = 0;
        g = g0 = g1 = 0;
        b = b0 = b1 = b2 = 0;

        for (int x = 0; x < xsize; x++, in += 4) {
            int d2;

            r = CLIP8(in[0] + (r + e[3 + 0]) / 16);
            g = CLIP8(in[1] + (g + e[3 + 1]) / 16);
            b = CLIP8(in[2] + (b + e[3 + 2]) / 16);

            int palette_index = find_exact_color(ech, r, g, b);
            if (palette_index < 0) {
                /* get closest colour */
                INT16 *cache = &ImagingPaletteCache(palette, r, g, b);
                if (cache[0] == 0x100) {
                    ImagingPaletteCacheUpdate(palette, r, g, b);
                }
                palette_index = cache[0];
            }
            if (alpha) {
                UINT32 v =
                    MAKE_UINT32(palette_index, palette_index, palette_index, 255);
                memcpy(out + x * 4, &v, sizeof(v));
            } else {
                out[x] = (UINT8)palette_index;
            }

            r -= (int)palette->palette[palette_index * 4];
            g -= (int)palette->palette[palette_index * 4 + 1];
            b -= (int)palette->palette[palette_index * 4 + 2];

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
topalette_colour_closest(
    Imaging imOut, Imaging imIn, ImagingPalette palette, ExactColorHash ech
) {
    int alpha = imOut->mode == IMAGING_MODE_PA;
    ImagingSectionCookie cookie;
    ImagingSectionEnter(&cookie);
    int xsize = imIn->xsize, ysize = imIn->ysize;
    for (int y = 0; y < ysize; y++) {
        // Restrict safe: we know imOut and imIn to be different images
        UINT8 *restrict in = (UINT8 *)imIn->image[y];
        UINT8 *restrict out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];

        for (int x = 0; x < xsize; x++, in += 4) {
            int r = in[0], g = in[1], b = in[2];
            int palette_index = find_exact_color(ech, r, g, b);
            if (palette_index < 0) {
                /* get closest colour */
                INT16 *cache = &ImagingPaletteCache(palette, r, g, b);
                if (cache[0] == 0x100) {
                    ImagingPaletteCacheUpdate(palette, r, g, b);
                }
                palette_index = cache[0];
            }
            if (alpha) {
                UINT32 v =
                    MAKE_UINT32(palette_index, palette_index, palette_index, 255);
                memcpy(out + x * 4, &v, sizeof(v));
            } else {
                out[x] = (UINT8)palette_index;
            }
        }
    }
    ImagingSectionLeave(&cookie);
}

Imaging
topalette(
    Imaging imOut, Imaging imIn, const ModeID mode, ImagingPalette inpalette, int dither
) {
    int palette_is_temporary = inpalette == NULL;
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
        goto done;
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

        // An ECH instance is only about 3 KiB; should be safe to allocate on the stack.
        struct ExactColorHashInstance exact_color_hash;
        prepare_exact_color_hash(palette, &exact_color_hash);

        if (ImagingPaletteCachePrepare(palette) < 0) {
            // Failed allocation for cache
            ImagingDelete(imOut);
            imOut = NULL;
            goto done;
        }

        if (dither) {
            if (topalette_colour_floyd_steinberg(
                    imOut, imIn, palette, &exact_color_hash
                ) != 0) {
                // Exception will have been set by the work function
                ImagingDelete(imOut);
                imOut = NULL;
                goto done;
            }
        } else {
            topalette_colour_closest(imOut, imIn, palette, &exact_color_hash);
        }
    }

done:

    if (palette_is_temporary) {
        // If we created a temporary palette, delete it to free memory
        ImagingPaletteDelete(palette);
    }

    return imOut;
}

#if defined(_MSC_VER)
#pragma optimize("", on)
#endif
