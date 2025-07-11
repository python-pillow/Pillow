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
    im->refcount = 1;
    im->type = IMAGING_TYPE_UINT8;
    strcpy(im->arrow_band_format, "C");

    if (strcmp(mode, "1") == 0) {
        /* 1-bit images */
        im->bands = im->pixelsize = 1;
        im->linesize = xsize;
        strcpy(im->band_names[0], "1");

    } else if (strcmp(mode, "P") == 0) {
        /* 8-bit palette mapped images */
        im->bands = im->pixelsize = 1;
        im->linesize = xsize;
        im->palette = ImagingPaletteNew("RGB");
        strcpy(im->band_names[0], "P");

    } else if (strcmp(mode, "PA") == 0) {
        /* 8-bit palette with alpha */
        im->bands = 2;
        im->pixelsize = 4; /* store in image32 memory */
        im->linesize = xsize * 4;
        im->palette = ImagingPaletteNew("RGB");
        strcpy(im->band_names[0], "P");
        strcpy(im->band_names[1], "X");
        strcpy(im->band_names[2], "X");
        strcpy(im->band_names[3], "A");

    } else if (strcmp(mode, "L") == 0) {
        /* 8-bit grayscale (luminance) images */
        im->bands = im->pixelsize = 1;
        im->linesize = xsize;
        strcpy(im->band_names[0], "L");

    } else if (strcmp(mode, "LA") == 0) {
        /* 8-bit grayscale (luminance) with alpha */
        im->bands = 2;
        im->pixelsize = 4; /* store in image32 memory */
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "L");
        strcpy(im->band_names[1], "X");
        strcpy(im->band_names[2], "X");
        strcpy(im->band_names[3], "A");

    } else if (strcmp(mode, "La") == 0) {
        /* 8-bit grayscale (luminance) with premultiplied alpha */
        im->bands = 2;
        im->pixelsize = 4; /* store in image32 memory */
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "L");
        strcpy(im->band_names[1], "X");
        strcpy(im->band_names[2], "X");
        strcpy(im->band_names[3], "a");

    } else if (strcmp(mode, "F") == 0) {
        /* 32-bit floating point images */
        im->bands = 1;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        im->type = IMAGING_TYPE_FLOAT32;
        strcpy(im->arrow_band_format, "f");
        strcpy(im->band_names[0], "F");

    } else if (strcmp(mode, "I") == 0) {
        /* 32-bit integer images */
        im->bands = 1;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        im->type = IMAGING_TYPE_INT32;
        strcpy(im->arrow_band_format, "i");
        strcpy(im->band_names[0], "I");

    } else if (strcmp(mode, "I;16") == 0 || strcmp(mode, "I;16L") == 0 ||
               strcmp(mode, "I;16B") == 0 || strcmp(mode, "I;16N") == 0) {
        /* EXPERIMENTAL */
        /* 16-bit raw integer images */
        im->bands = 1;
        im->pixelsize = 2;
        im->linesize = xsize * 2;
        im->type = IMAGING_TYPE_SPECIAL;
        strcpy(im->arrow_band_format, "s");
        strcpy(im->band_names[0], "I");

    } else if (strcmp(mode, "RGB") == 0) {
        /* 24-bit true colour images */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "R");
        strcpy(im->band_names[1], "G");
        strcpy(im->band_names[2], "B");
        strcpy(im->band_names[3], "X");

    } else if (strcmp(mode, "RGBX") == 0) {
        /* 32-bit true colour images with padding */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "R");
        strcpy(im->band_names[1], "G");
        strcpy(im->band_names[2], "B");
        strcpy(im->band_names[3], "X");

    } else if (strcmp(mode, "RGBA") == 0) {
        /* 32-bit true colour images with alpha */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "R");
        strcpy(im->band_names[1], "G");
        strcpy(im->band_names[2], "B");
        strcpy(im->band_names[3], "A");

    } else if (strcmp(mode, "RGBa") == 0) {
        /* 32-bit true colour images with premultiplied alpha */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "R");
        strcpy(im->band_names[1], "G");
        strcpy(im->band_names[2], "B");
        strcpy(im->band_names[3], "a");

    } else if (strcmp(mode, "CMYK") == 0) {
        /* 32-bit colour separation */
        im->bands = im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "C");
        strcpy(im->band_names[1], "M");
        strcpy(im->band_names[2], "Y");
        strcpy(im->band_names[3], "K");

    } else if (strcmp(mode, "YCbCr") == 0) {
        /* 24-bit video format */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "Y");
        strcpy(im->band_names[1], "Cb");
        strcpy(im->band_names[2], "Cr");
        strcpy(im->band_names[3], "X");

    } else if (strcmp(mode, "LAB") == 0) {
        /* 24-bit color, luminance, + 2 color channels */
        /* L is uint8, a,b are int8 */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "L");
        strcpy(im->band_names[1], "a");
        strcpy(im->band_names[2], "b");
        strcpy(im->band_names[3], "X");

    } else if (strcmp(mode, "HSV") == 0) {
        /* 24-bit color, luminance, + 2 color channels */
        /* L is uint8, a,b are int8 */
        im->bands = 3;
        im->pixelsize = 4;
        im->linesize = xsize * 4;
        strcpy(im->band_names[0], "H");
        strcpy(im->band_names[1], "S");
        strcpy(im->band_names[2], "V");
        strcpy(im->band_names[3], "X");

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

    // UNDONE -- not accurate for arrow
    MUTEX_LOCK(&ImagingDefaultArena.mutex);
    ImagingDefaultArena.stats_new_count += 1;
    MUTEX_UNLOCK(&ImagingDefaultArena.mutex);

    return im;
}

Imaging
ImagingNewPrologue(const char *mode, int xsize, int ysize) {
    return ImagingNewPrologueSubtype(
        mode, xsize, ysize, sizeof(struct ImagingMemoryInstance)
    );
}

void
ImagingDelete(Imaging im) {
    if (!im) {
        return;
    }

    MUTEX_LOCK(&im->mutex);
    im->refcount--;

    if (im->refcount > 0) {
        MUTEX_UNLOCK(&im->mutex);
        return;
    }
    MUTEX_UNLOCK(&im->mutex);

    if (im->palette) {
        ImagingPaletteDelete(im->palette);
        im->palette = NULL;
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
    0,  // Stats
    0,  // use_block_allocator
#ifdef Py_GIL_DISABLED
    {0},
#endif
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
ImagingMemorySetBlockAllocator(ImagingMemoryArena arena, int use_block_allocator) {
    arena->use_block_allocator = use_block_allocator;
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
        MUTEX_LOCK(&ImagingDefaultArena.mutex);
        while (im->blocks[y].ptr) {
            memory_return_block(&ImagingDefaultArena, im->blocks[y]);
            y += 1;
        }
        MUTEX_UNLOCK(&ImagingDefaultArena.mutex);
        free(im->blocks);
    }
}

Imaging
ImagingAllocateArray(Imaging im, ImagingMemoryArena arena, int dirty, int block_size) {
    int y, line_in_block, current_block;
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
    im->lines_per_block = lines_per_block;
    blocks_count = (im->ysize + lines_per_block - 1) / lines_per_block;
    // printf("NEW size: %dx%d, ls: %d, lpb: %d, blocks: %d\n",
    //        im->xsize, im->ysize, aligned_linesize, lines_per_block, blocks_count);

    /* One extra pointer is always NULL */
    im->blocks_count = blocks_count;
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
            aligned_ptr = (char *)(((size_t)(block.ptr + arena->alignment - 1)) &
                                   -((Py_ssize_t)arena->alignment));
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

/* Borrowed Arrow Storage Type */
/* --------------------------- */
/* Don't allocate the image. */

static void
ImagingDestroyArrow(Imaging im) {
    // Rely on the internal Python destructor for the array capsule.
    if (im->arrow_array_capsule) {
        Py_DECREF(im->arrow_array_capsule);
        im->arrow_array_capsule = NULL;
    }
}

Imaging
ImagingBorrowArrow(
    Imaging im,
    struct ArrowArray *external_array,
    int offset_width,
    PyObject *arrow_capsule
) {
    // offset_width is the number of char* for a single offset from arrow
    Py_ssize_t y, i;

    char *borrowed_buffer = NULL;
    struct ArrowArray *arr = external_array;

    if (arr->n_children == 1) {
        arr = arr->children[0];
    }
    if (arr->n_buffers == 2) {
        // buffer 0 is the null list
        // buffer 1 is the data
        borrowed_buffer = (char *)arr->buffers[1] + (offset_width * arr->offset);
    }

    if (!borrowed_buffer) {
        return (Imaging)ImagingError_ValueError(
            "Arrow Array, exactly 2 buffers required"
        );
    }

    for (y = i = 0; y < im->ysize; y++) {
        im->image[y] = borrowed_buffer + i;
        i += im->linesize;
    }
    im->read_only = 1;
    Py_INCREF(arrow_capsule);
    im->arrow_array_capsule = arrow_capsule;
    im->destroy = ImagingDestroyArrow;

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

    MUTEX_LOCK(&ImagingDefaultArena.mutex);
    Imaging tmp = ImagingAllocateArray(
        im, &ImagingDefaultArena, dirty, ImagingDefaultArena.block_size
    );
    MUTEX_UNLOCK(&ImagingDefaultArena.mutex);
    if (tmp) {
        return im;
    }

    PyErr_Clear();

    // Try to allocate the image once more with smallest possible block size
    MUTEX_LOCK(&ImagingDefaultArena.mutex);
    tmp = ImagingAllocateArray(im, &ImagingDefaultArena, dirty, IMAGING_PAGE_SIZE);
    MUTEX_UNLOCK(&ImagingDefaultArena.mutex);
    if (tmp) {
        return im;
    }

    ImagingDelete(im);
    return NULL;
}

Imaging
ImagingNew(const char *mode, int xsize, int ysize) {
    if (ImagingDefaultArena.use_block_allocator) {
        return ImagingNewBlock(mode, xsize, ysize);
    }
    return ImagingNewInternal(mode, xsize, ysize, 0);
}

Imaging
ImagingNewDirty(const char *mode, int xsize, int ysize) {
    if (ImagingDefaultArena.use_block_allocator) {
        return ImagingNewBlock(mode, xsize, ysize);
    }
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
ImagingNewArrow(
    const char *mode,
    int xsize,
    int ysize,
    PyObject *schema_capsule,
    PyObject *array_capsule
) {
    /* A borrowed arrow array */
    Imaging im;
    struct ArrowSchema *schema =
        (struct ArrowSchema *)PyCapsule_GetPointer(schema_capsule, "arrow_schema");

    struct ArrowArray *external_array =
        (struct ArrowArray *)PyCapsule_GetPointer(array_capsule, "arrow_array");

    if (xsize < 0 || ysize < 0) {
        return (Imaging)ImagingError_ValueError("bad image size");
    }

    im = ImagingNewPrologue(mode, xsize, ysize);
    if (!im) {
        return NULL;
    }

    int64_t pixels = (int64_t)xsize * (int64_t)ysize;

    // fmt:off   // don't reformat this
    // stored as a single array, one element per pixel, either single band
    // or multiband, where each pixel is an I32.
    if (((strcmp(schema->format, "I") == 0  // int32
          && im->pixelsize == 4             // 4xchar* storage
          && im->bands >= 2)                // INT32 into any INT32 Storage mode
         ||                                 // (()||()) &&
         (strcmp(schema->format, im->arrow_band_format) == 0  // same mode
          && im->bands == 1))                                 // Single band match
        && pixels == external_array->length) {
        // one arrow element per, and it matches a pixelsize*char
        if (ImagingBorrowArrow(im, external_array, im->pixelsize, array_capsule)) {
            return im;
        }
    }
    // Stored as [[r,g,b,a],...]
    if (strcmp(schema->format, "+w:4") == 0  // 4 up array
        && im->pixelsize == 4                // storage as 32 bpc
        && schema->n_children > 0            // make sure schema is well formed.
        && schema->children                  // make sure schema is well formed
        && strcmp(schema->children[0]->format, "C") == 0  // Expected format
        && strcmp(im->arrow_band_format, "C") == 0        // Expected Format
        && pixels == external_array->length               // expected length
        && external_array->n_children == 1                // array is well formed
        && external_array->children                       // array is well formed
        && 4 * pixels == external_array->children[0]->length) {
        // 4 up element of char into pixelsize == 4
        if (ImagingBorrowArrow(im, external_array, 1, array_capsule)) {
            return im;
        }
    }
    // Stored as [r,g,b,a,r,g,b,a,...]
    if (strcmp(schema->format, "C") == 0            // uint8
        && im->pixelsize == 4                       // storage as 32 bpc
        && schema->n_children == 0                  // make sure schema is well formed.
        && strcmp(im->arrow_band_format, "C") == 0  // expected format
        && 4 * pixels == external_array->length) {  // expected length
        // single flat array, interleaved storage.
        if (ImagingBorrowArrow(im, external_array, 1, array_capsule)) {
            return im;
        }
    }
    // fmt: on
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
