/*
 * The Python Imaging Library
 * $Id$
 *
 * imaging palette object
 *
 * history:
 * 1996-05-05 fl   Added to library
 * 1996-05-27 fl   Added colour mapping stuff
 * 1997-05-12 fl   Support RGBA palettes
 * 2005-02-09 fl   Removed grayscale entries from web palette
 *
 * Copyright (c) Secret Labs AB 1997-2005.  All rights reserved.
 * Copyright (c) Fredrik Lundh 1995-1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/**
 * Create a palette object in the given mode.
 *
 * @param mode The mode of the palette (RGB/RGBA/CMYK).
 * @return A new palette object, or NULL on error with a Python exception set.
 */
ImagingPalette
ImagingPaletteNew(const ModeID mode) {
    int i;
    ImagingPalette palette;

    if (mode != IMAGING_MODE_RGB && mode != IMAGING_MODE_RGBA &&
        mode != IMAGING_MODE_CMYK) {
        return (ImagingPalette)ImagingError_ModeError();
    }

    palette = calloc(1, sizeof(struct ImagingPaletteInstance));
    if (!palette) {
        return (ImagingPalette)ImagingError_MemoryError();
    }

    palette->mode = mode;

    palette->size = 0;
    for (i = 0; i < IMAGING_PALETTE_MAX_ENTRIES; i++) {
        palette->palette[i * 4 + 3] = 255; /* opaque */
    }

    return palette;
}

/**
 * Create a standard "browser" palette object in RGB mode.
 *
 * @return A new palette object, or NULL on error with a Python exception set.
 */
ImagingPalette
ImagingPaletteNewBrowser(void) {
    int i, r, g, b;
    ImagingPalette palette;

    palette = ImagingPaletteNew(IMAGING_MODE_RGB);
    if (!palette) {
        return NULL;
    }

    /* FIXME: Add 10-level windows palette here? */

    /* Simple 6x6x6 colour cube */
    i = 10;
    for (b = 0; b < 256; b += 51) {
        for (g = 0; g < 256; g += 51) {
            for (r = 0; r < 256; r += 51) {
                palette->palette[i * 4 + 0] = r;
                palette->palette[i * 4 + 1] = g;
                palette->palette[i * 4 + 2] = b;
                i++;
            }
        }
    }
    palette->size = i;

    /* FIXME: add 30-level grayscale wedge here? */

    return palette;
}

/**
 * Duplicate a palette object.
 *
 * @param palette The palette to duplicate.
 * @return A new palette object, or NULL on error with a Python exception set.
 */
ImagingPalette
ImagingPaletteDuplicate(ImagingPalette palette) {
    ImagingPalette new_palette;

    if (!palette) {
        return NULL;
    }
    /* malloc check ok, small constant allocation */
    new_palette = malloc(sizeof(struct ImagingPaletteInstance));
    if (!new_palette) {
        return (ImagingPalette)ImagingError_MemoryError();
    }

    memcpy(new_palette, palette, sizeof(struct ImagingPaletteInstance));

    /* Don't share the cache */
    new_palette->cache = NULL;

    return new_palette;
}

/**
 * Destroy a palette object.
 *
 * @param palette The palette to destroy; may be NULL.
 * @return Void. The passed-in palette pointer is invalid after this call.
 */
void
ImagingPaletteDelete(ImagingPalette palette) {
    if (palette) {
        if (palette->cache) {
            free(palette->cache);
        }
        free(palette);
    }
}
