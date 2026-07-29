/*
 * The Python Imaging Library
 *
 * See Convert.c and Palette.c for legacy history of this file.
 *
 * Copyright (c) 1997-2005 by Secret Labs AB.
 * Copyright (c) 1995-1997 by Fredrik Lundh.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

/*
 * The coarse colour mapping is loosely based on the corresponding code in
 * the IJG JPEG library by Thomas G. Lane.  Original algorithms by
 * Paul Heckbert and Spencer W. Thomas.
 */

#define DIST(a, b, s) (a - b) * (a - b) * s

#define RSCALE 1
#define GSCALE 1
#define BSCALE 1

#define RDIST(a, b) DIST(a, b, RSCALE *RSCALE)
#define GDIST(a, b) DIST(a, b, GSCALE *GSCALE)
#define BDIST(a, b) DIST(a, b, BSCALE *BSCALE)

#define RSTEP (4 * RSCALE)
#define GSTEP (4 * GSCALE)
#define BSTEP (4 * BSCALE)

#define BOX 8
#define BOXVOLUME (BOX * BOX * BOX)

static INT16 *
palette_cache(ImagingPalette palette, int r, int g, int b) {
    return &palette->cache[(r >> 2) + (g >> 2) * 64 + (b >> 2) * 64 * 64];
}

static void
palette_cache_update(ImagingPalette palette, int r, int g, int b) {
    int i, j;
    unsigned int dmin[IMAGING_PALETTE_MAX_ENTRIES], dmax;
    int r0, g0, b0;
    int r1, g1, b1;
    int rc, gc, bc;
    unsigned int d[BOXVOLUME];
    UINT8 c[BOXVOLUME];

    /* Get box boundaries for the given (r,g,b)-triplet.  Each box
       covers eight cache slots (32 colour values, that is). */

    r0 = r & 0xe0;
    r1 = r0 + 0x1f;
    rc = (r0 + r1) / 2;
    g0 = g & 0xe0;
    g1 = g0 + 0x1f;
    gc = (g0 + g1) / 2;
    b0 = b & 0xe0;
    b1 = b0 + 0x1f;
    bc = (b0 + b1) / 2;

    /* Step 1 -- Select relevant palette entries (after Heckbert) */

    /* For each palette entry, calculate the min and max distances to
     * any position in the box given by the colour we're looking for. */

    dmax = (unsigned int)~0;

    for (i = 0; i < palette->size; i++) {
        int r, g, b;
        unsigned int tmin, tmax;

        /* Find min and max distances to any point in the box */
        r = palette->palette[i * 4 + 0];
        tmin = (r < r0) ? RDIST(r, r0) : (r > r1) ? RDIST(r, r1) : 0;
        tmax = (r <= rc) ? RDIST(r, r1) : RDIST(r, r0);

        g = palette->palette[i * 4 + 1];
        tmin += (g < g0) ? GDIST(g, g0) : (g > g1) ? GDIST(g, g1) : 0;
        tmax += (g <= gc) ? GDIST(g, g1) : GDIST(g, g0);

        b = palette->palette[i * 4 + 2];
        tmin += (b < b0) ? BDIST(b, b0) : (b > b1) ? BDIST(b, b1) : 0;
        tmax += (b <= bc) ? BDIST(b, b1) : BDIST(b, b0);

        dmin[i] = tmin;
        if (tmax < dmax) {
            dmax = tmax; /* keep the smallest max distance only */
        }
    }

    /* Step 2 -- Incrementally update cache slot (after Thomas) */

    /* Find the box containing the nearest palette entry, and update
     * all slots in that box.  We only check boxes for which the min
     * distance is less than or equal the smallest max distance */

    for (i = 0; i < BOXVOLUME; i++) {
        d[i] = (unsigned int)~0;
    }

    for (i = 0; i < palette->size; i++) {
        if (dmin[i] <= dmax) {
            int rd, gd, bd;
            int ri, gi, bi;
            int rx, gx, bx;

            ri = (r0 - palette->palette[i * 4 + 0]) * RSCALE;
            gi = (g0 - palette->palette[i * 4 + 1]) * GSCALE;
            bi = (b0 - palette->palette[i * 4 + 2]) * BSCALE;

            rd = ri * ri + gi * gi + bi * bi;

            ri = ri * (2 * RSTEP) + RSTEP * RSTEP;
            gi = gi * (2 * GSTEP) + GSTEP * GSTEP;
            bi = bi * (2 * BSTEP) + BSTEP * BSTEP;

            rx = ri;
            for (r = j = 0; r < BOX; r++) {
                gd = rd;
                gx = gi;
                for (g = 0; g < BOX; g++) {
                    bd = gd;
                    bx = bi;
                    for (b = 0; b < BOX; b++) {
                        if ((unsigned int)bd < d[j]) {
                            d[j] = bd;
                            c[j] = (UINT8)i;
                        }
                        bd += bx;
                        bx += 2 * BSTEP * BSTEP;
                        j++;
                    }
                    gd += gx;
                    gx += 2 * GSTEP * GSTEP;
                }
                rd += rx;
                rx += 2 * RSTEP * RSTEP;
            }
        }
    }

    /* Step 3 -- Update cache */

    /* The c array now contains the closest match for each
     * cache slot in the box.  Update the cache. */

    j = 0;
    for (r = r0; r < r1; r += 4) {
        for (g = g0; g < g1; g += 4) {
            for (b = b0; b < b1; b += 4) {
                *palette_cache(palette, r, g, b) = c[j++];
            }
        }
    }
}

static int
palette_cache_prepare(ImagingPalette palette) {
    int entries = 64 * 64 * 64;

    if (palette->cache == NULL) {
        /* malloc check ok, small constant allocation */
        palette->cache = (INT16 *)malloc(entries * sizeof(INT16));
        if (!palette->cache) {
            (void)ImagingError_MemoryError();
            return -1;
        }

        /* Mark all entries as empty */
        for (int i = 0; i < entries; i++) {
            palette->cache[i] = 0x100;
        }
    }

    return 0;
}

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
                INT16 *cache = palette_cache(palette, r, g, b);
                if (cache[0] == 0x100) {
                    palette_cache_update(palette, r, g, b);
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
                INT16 *cache = palette_cache(palette, r, g, b);
                if (cache[0] == 0x100) {
                    palette_cache_update(palette, r, g, b);
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

        if (palette_cache_prepare(palette) < 0) {
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
