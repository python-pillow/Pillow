/*
 * The Python Imaging Library
 * $Id$
 *
 * imaging storage object
 *
 * This baseline implementation is designed to efficiently handle
 * large images, provided they fit into the available memory.
 *
 * history:
 * 1995-06-15 fl   Created
 * 1995-09-12 fl   Updated API, compiles silently under ANSI C++
 * 1995-11-26 fl   Compiles silently under Borland 4.5 as well
 * 1996-05-05 fl   Correctly test status from Prologue
 * 1997-05-12 fl   Increased THRESHOLD (to speed up Tk interface)
 * 1997-05-30 fl   Added support for floating point images
 * 1997-11-17 fl   Added support for "RGBX" images
 * 1998-01-11 fl   Added support for integer images
 * 1998-03-05 fl   Exported Prologue/Epilogue functions
 * 1998-07-01 fl   Added basic "YCrCb" support
 * 1998-07-03 fl   Attach palette in prologue for "P" images
 * 1998-07-09 hk   Don't report MemoryError on zero-size images
 * 1998-07-12 fl   Change "YCrCb" to "YCbCr" (!)
 * 1998-10-26 fl   Added "I;16" and "I;16B" storage modes (experimental)
 * 1998-12-29 fl   Fixed allocation bug caused by previous fix
 * 1999-02-03 fl   Added "RGBa" and "BGR" modes (experimental)
 * 2001-04-22 fl   Fixed potential memory leak in ImagingCopyPalette
 * 2003-09-26 fl   Added "LA" and "PA" modes (experimental)
 * 2005-10-02 fl   Added image counter
 *
 * Copyright (c) 1998-2005 by Secret Labs AB
 * Copyright (c) 1995-2005 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"
#include <string.h>

/* --------------------------------------------------------------------
 * Standard image object.
 */

Imaging
ImagingNewPrologueSubtype(const char *mode, int xsize, int ysize, int size) {
    Imaging im;

    /* linesize overflow check, roughly the current largest space req'd */
    if (xsize > (INT_MAX / 4) - 1) {
        return (Imaging)ImagingError_MemoryError();
    }

    im = (Imaging)calloc(1, size);
    if (!im) {
        return (Imaging)ImagingError_MemoryError();
    }

    /* Setup image descriptor */
    im->xsize = xsize;
    im->ysize = ysize;

    im->type = IMAGING_TYPE_UINT8;

    if (strcmp(mode, "1") == 0) {
        /* 1-bit images */
        im->bands = im->pixelsize = 1;
        im->linesize = xsize;

    } else if (strcmp(mode, "P") == 0) {
        /* 8-bit palette mapped images */
        im->bands = im->pixelsize = 1;
        im->linesize = xsize;
        im->palette = ImagingPaletteNew("RGB");

    } else if (strcmp(mode, "PA") == 0) {
        /* 8-bit palette with alpha */
        im->bands = 2;
        im->pixelsize = 4; /* store in image32 memory */
        im->linesize = xsize * 4;
        im->palette = ImagingPaletteNew("RGB");

    } else if (strcmp(mode, "L") == 0) {
        /* 8-bit grayscale (luminance) images */
        im->bands = im->pixelsize = 1;
        im->linesize = xsize;

    } else if (strcmp(mode, "LA") == 0) {
        /* 8-bit grayscale (luminance) with alpha */
        im->bands = 2;
        im->pixelsize = 4; /* store in image32 memory */
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "La") == 0) {
        /* 8-bit grayscale (luminance) with premultiplied alpha */
        im->bands = 2;
        im->pixelsize = 4; /* store in image32 memory */
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "F") == 0) {
        /* 32-bit floating point images */
        im->bands = 1;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        im->type = IMAGING_TYPE_FLOAT32;

    } else if (strcmp(mode, "I") == 0) {
        /* 32-bit integer images */
        im->bands = 1;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        im->type = IMAGING_TYPE_INT32;

    } else if (
        strcmp(mode, "I;16") == 0 || strcmp(mode, "I;16L") == 0 ||
        strcmp(mode, "I;16B") == 0 || strcmp(mode, "I;16N") == 0) {
        /* EXPERIMENTAL */
        /* 16-bit raw integer images */
        im->bands = 1;
        im->pixelsize = 2;
        im->linesize = xsize * 2;
        im->type = IMAGING_TYPE_SPECIAL;

    } else if (strcmp(mode, "RGB") == 0) {
        /* 24-bit true colour images */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "BGR;15") == 0) {
        /* EXPERIMENTAL */
        /* 15-bit reversed true colour */
        im->bands = 3;
        im->pixelsize = 2;
        im->linesize = (xsize * 2 + 3) & -4;
        im->type = IMAGING_TYPE_SPECIAL;

    } else if (strcmp(mode, "BGR;16") == 0) {
        /* EXPERIMENTAL */
        /* 16-bit reversed true colour */
        im->bands = 3;
        im->pixelsize = 2;
        im->linesize = (xsize * 2 + 3) & -4;
        im->type = IMAGING_TYPE_SPECIAL;

    } else if (strcmp(mode, "BGR;24") == 0) {
        /* EXPERIMENTAL */
        /* 24-bit reversed true colour */
        im->bands = 3;
        im->pixelsize = 3;
        im->linesize = (xsize * 3 + 3) & -4;
        im->type = IMAGING_TYPE_SPECIAL;

    } else if (strcmp(mode, "RGBX") == 0) {
        /* 32-bit true colour images with padding */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "RGBA") == 0) {
        /* 32-bit true colour images with alpha */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "RGBa") == 0) {
        /* 32-bit true colour images with premultiplied alpha */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "CMYK") == 0) {
        /* 32-bit colour separation */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "YCbCr") == 0) {
        /* 24-bit video format */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "LAB") == 0) {
        /* 24-bit color, luminance, + 2 color channels */
        /* L is uint8, a,b are int8 */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else if (strcmp(mode, "HSV") == 0) {
        /* 24-bit color, luminance, + 2 color channels */
        /* L is uint8, a,b are int8 */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;

    } else {
        free(im);
        return (Imaging)ImagingError_ValueError("unrecognized image mode");
    }

    /* Setup image descriptor */
    strcpy(im->mode, mode);

    /* Pointer array (allocate at least one line, to avoid MemoryError
       exceptions on platforms where calloc(0, x) returns NULL) */
    im->image = (char **)calloc((ysize > 0) ? ysize : 1, sizeof(void *));

    if (!im->image) {
        free(im);
        return (Imaging)ImagingError_MemoryError();
    }

    /* Initialize alias pointers to pixel data. */
    switch (im->pixelsize) {
        case 1:
        case 2:
        case 3:
            im->image8 = (UINT8 **)im->image;
            break;
        case 4:
            im->image32 = (INT32 **)im->image;
            break;
    }

    ImagingDefaultArena.stats_new_count += 1;

    return im;
}

Imaging
ImagingNewPrologue(const char *mode, int xsize, int ysize) {
    return ImagingNewPrologueSubtype(
        mode, xsize, ysize, sizeof(struct ImagingMemoryInstance));
}

void
ImagingDelete(Imaging im) {
    if (!im) {
        return;
    }

    if (im->palette) {
        ImagingPaletteDelete(im->palette);
    }

    if (im->destroy) {
        im->destroy(im);
    }

    if (im->image) {
        free(im->image);
    }

    free(im);
}

/* Array Storage Type */
/* ------------------ */
/* Allocate image as an array of line buffers. */

#define IMAGING_PAGE_SIZE (4096)

struct ImagingMemoryArena ImagingDefaultArena = {
    1,                 // alignment
    16 * 1024 * 1024,  // block_size
    0,                 // blocks_max
    0,                 // blocks_cached
    NULL,              // blocks_pool
    0,
    0,
    0,
    0,
    0  // Stats
};

int
ImagingMemorySetBlocksMax(ImagingMemoryArena arena, int blocks_max) {
    void *p;
    /* Free already cached blocks */
    ImagingMemoryClearCache(arena, blocks_max);

    if (blocks_max == 0 && arena->blocks_pool != NULL) {
        free(arena->blocks_pool);
        arena->blocks_pool = NULL;
    } else if (arena->blocks_pool != NULL) {
        p = realloc(arena->blocks_pool, sizeof(*arena->blocks_pool) * blocks_max);
        if (!p) {
            // Leave previous blocks_max value
            return 0;
        }
        arena->blocks_pool = p;
    } else {
        arena->blocks_pool = calloc(sizeof(*arena->blocks_pool), blocks_max);
        if (!arena->blocks_pool) {
            return 0;
        }
    }
    arena->blocks_max = blocks_max;

    return 1;
}

void
ImagingMemoryClearCache(ImagingMemoryArena arena, int new_size) {
    while (arena->blocks_cached > new_size) {
        arena->blocks_cached -= 1;
        free(arena->blocks_pool[arena->blocks_cached].ptr);
        arena->stats_freed_blocks += 1;
    }
}

ImagingMemoryBlock
memory_get_block(ImagingMemoryArena arena, int requested_size, int dirty) {
    ImagingMemoryBlock block = {NULL, 0};

    if (arena->blocks_cached > 0) {
        // Get block from cache
        arena->blocks_cached -= 1;
        block = arena->blocks_pool[arena->blocks_cached];
        // Reallocate if needed
        if (block.size != requested_size) {
            block.ptr = realloc(block.ptr, requested_size);
        }
        if (!block.ptr) {
            // Can't allocate, free previous pointer (it is still valid)
            free(arena->blocks_pool[arena->blocks_cached].ptr);
            arena->stats_freed_blocks += 1;
            return block;
        }
        if (!dirty) {
            memset(block.ptr, 0, requested_size);
        }
        arena->stats_reused_blocks += 1;
        if (block.ptr != arena->blocks_pool[arena->blocks_cached].ptr) {
            arena->stats_reallocated_blocks += 1;
        }
    } else {
        if (dirty) {
            block.ptr = malloc(requested_size);
        } else {
            block.ptr = calloc(1, requested_size);
        }
        arena->stats_allocated_blocks += 1;
    }
    block.size = requested_size;
    return block;
}

void
memory_return_block(ImagingMemoryArena arena, ImagingMemoryBlock block) {
    if (arena->blocks_cached < arena->blocks_max) {
        // Reduce block size
        if (block.size > arena->block_size) {
            block.size = arena->block_size;
            block.ptr = realloc(block.ptr, arena->block_size);
        }
        arena->blocks_pool[arena->blocks_cached] = block;
        arena->blocks_cached += 1;
    } else {
        free(block.ptr);
        arena->stats_freed_blocks += 1;
    }
}

static void
ImagingDestroyArray(Imaging im) {
    int y = 0;

    if (im->blocks) {
        while (im->blocks[y].ptr) {
            memory_return_block(&ImagingDefaultArena, im->blocks[y]);
            y += 1;
        }
        free(im->blocks);
    }
}

Imaging
ImagingAllocateArray(Imaging im, int dirty, int block_size) {
    int y, line_in_block, current_block;
    ImagingMemoryArena arena = &ImagingDefaultArena;
    ImagingMemoryBlock block = {NULL, 0};
    int aligned_linesize, lines_per_block, blocks_count;
    char *aligned_ptr = NULL;

    /* 0-width or 0-height image. No need to do anything */
    if (!im->linesize || !im->ysize) {
        return im;
    }

    aligned_linesize = (im->linesize + arena->alignment - 1) & -arena->alignment;
    lines_per_block = (block_size - (arena->alignment - 1)) / aligned_linesize;
    if (lines_per_block == 0) {
        lines_per_block = 1;
    }
    blocks_count = (im->ysize + lines_per_block - 1) / lines_per_block;
    // printf("NEW size: %dx%d, ls: %d, lpb: %d, blocks: %d\n",
    //        im->xsize, im->ysize, aligned_linesize, lines_per_block, blocks_count);

    /* One extra pointer is always NULL */
    im->blocks = calloc(sizeof(*im->blocks), blocks_count + 1);
    if (!im->blocks) {
        return (Imaging)ImagingError_MemoryError();
    }

    /* Allocate image as an array of lines */
    line_in_block = 0;
    current_block = 0;
    for (y = 0; y < im->ysize; y++) {
        if (line_in_block == 0) {
            int required;
            int lines_remaining = lines_per_block;
            if (lines_remaining > im->ysize - y) {
                lines_remaining = im->ysize - y;
            }
            required = lines_remaining * aligned_linesize + arena->alignment - 1;
            block = memory_get_block(arena, required, dirty);
            if (!block.ptr) {
                ImagingDestroyArray(im);
                return (Imaging)ImagingError_MemoryError();
            }
            im->blocks[current_block] = block;
            /* Bulletproof code from libc _int_memalign */
            aligned_ptr = (char *)(
                ((size_t) (block.ptr + arena->alignment - 1)) &
                -((Py_ssize_t) arena->alignment));
        }

        im->image[y] = aligned_ptr + aligned_linesize * line_in_block;

        line_in_block += 1;
        if (line_in_block >= lines_per_block) {
            /* Reset counter and start new block */
            line_in_block = 0;
            current_block += 1;
        }
    }

    im->destroy = ImagingDestroyArray;

    return im;
}

/* Block Storage Type */
/* ------------------ */
/* Allocate image as a single block. */

static void
ImagingDestroyBlock(Imaging im) {
    if (im->block) {
        free(im->block);
    }
}

Imaging
ImagingAllocateBlock(Imaging im) {
    Py_ssize_t y, i;

    /* overflow check for malloc */
    if (im->linesize && im->ysize > INT_MAX / im->linesize) {
        return (Imaging)ImagingError_MemoryError();
    }

    if (im->ysize * im->linesize <= 0) {
        /* some platforms return NULL for malloc(0); this fix
           prevents MemoryError on zero-sized images on such
           platforms */
        im->block = (char *)malloc(1);
    } else {
        /* malloc check ok, overflow check above */
        im->block = (char *)calloc(im->ysize, im->linesize);
    }

    if (!im->block) {
        return (Imaging)ImagingError_MemoryError();
    }

    for (y = i = 0; y < im->ysize; y++) {
        im->image[y] = im->block + i;
        i += im->linesize;
    }

    im->destroy = ImagingDestroyBlock;

    return im;
}

/* --------------------------------------------------------------------
 * Create a new, internally allocated, image.
 */

Imaging
ImagingNewInternal(const char *mode, int xsize, int ysize, int dirty) {
    Imaging im;

    if (xsize < 0 || ysize < 0) {
        return (Imaging)ImagingError_ValueError("bad image size");
    }

    im = ImagingNewPrologue(mode, xsize, ysize);
    if (!im) {
        return NULL;
    }

    if (ImagingAllocateArray(im, dirty, ImagingDefaultArena.block_size)) {
        return im;
    }

    ImagingError_Clear();

    // Try to allocate the image once more with smallest possible block size
    if (ImagingAllocateArray(im, dirty, IMAGING_PAGE_SIZE)) {
        return im;
    }

    ImagingDelete(im);
    return NULL;
}

Imaging
ImagingNew(const char *mode, int xsize, int ysize) {
    return ImagingNewInternal(mode, xsize, ysize, 0);
}

Imaging
ImagingNewDirty(const char *mode, int xsize, int ysize) {
    return ImagingNewInternal(mode, xsize, ysize, 1);
}

Imaging
ImagingNewBlock(const char *mode, int xsize, int ysize) {
    Imaging im;

    if (xsize < 0 || ysize < 0) {
        return (Imaging)ImagingError_ValueError("bad image size");
    }

    im = ImagingNewPrologue(mode, xsize, ysize);
    if (!im) {
        return NULL;
    }

    if (ImagingAllocateBlock(im)) {
        return im;
    }

    ImagingDelete(im);
    return NULL;
}

Imaging
ImagingNew2Dirty(const char *mode, Imaging imOut, Imaging imIn) {
    /* allocate or validate output image */

    if (imOut) {
        /* make sure images match */
        if (strcmp(imOut->mode, mode) != 0 || imOut->xsize != imIn->xsize ||
            imOut->ysize != imIn->ysize) {
            return ImagingError_Mismatch();
        }
    } else {
        /* create new image */
        imOut = ImagingNewDirty(mode, imIn->xsize, imIn->ysize);
        if (!imOut) {
            return NULL;
        }
    }

    return imOut;
}

void
ImagingCopyPalette(Imaging destination, Imaging source) {
    if (source->palette) {
        if (destination->palette) {
            ImagingPaletteDelete(destination->palette);
        }
        destination->palette = ImagingPaletteDuplicate(source->palette);
    }
}
