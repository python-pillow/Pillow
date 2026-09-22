/*
 * The Python Imaging Library
 * $Id$
 *
 * min, max, median filters
 *
 * history:
 * 2002-06-08 fl    Created
 *
 * Copyright (c) Secret Labs AB 2002.  All rights reserved.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/* Fast rank algorithm (due to Wirth), based on public domain code
   by Nicolas Devillard, available at http://ndevilla.free.fr */

#define RANK_INNER_BODY(type)  \
    int i, j, l, m;            \
    type x;                    \
    l = 0;                     \
    m = n - 1;                 \
    while (l < m) {            \
        x = a[k];              \
        i = l;                 \
        j = m;                 \
        do {                   \
            while (a[i] < x) { \
                i++;           \
            }                  \
            while (x < a[j]) { \
                j--;           \
            }                  \
            if (i <= j) {      \
                type t = a[i]; \
                a[i] = a[j];   \
                a[j] = t;      \
                i++;           \
                j--;           \
            }                  \
        } while (i <= j);      \
        if (j < k) {           \
            l = i;             \
        }                      \
        if (k < i) {           \
            m = j;             \
        }                      \
    }                          \
    return a[k]

static UINT8
RankUINT8(UINT8 a[], int n, int k) {
    RANK_INNER_BODY(UINT8);
}

static INT32
RankINT32(INT32 a[], int n, int k) {
    RANK_INNER_BODY(INT32);
}

static FLOAT32
RankFLOAT32(FLOAT32 a[], int n, int k) {
    RANK_INNER_BODY(FLOAT32);
}

Imaging
ImagingRankFilter(Imaging im, int size, int rank) {
    Imaging imOut = NULL;
    int margin, size2;

    if (!im || im->bands != 1 || im->type == IMAGING_TYPE_I16) {
        return (Imaging)ImagingError_ModeError();
    }

    if (!(size & 1)) {
        return (Imaging)ImagingError_ValueError("bad filter size");
    }

    /* malloc check ok, for overflow in the define below */
    if (size > INT_MAX / (size * (int)sizeof(FLOAT32))) {
        return (Imaging)ImagingError_ValueError("filter size too large");
    }

    size2 = size * size;
    margin = (size - 1) / 2;

    if (rank < 0 || rank >= size2) {
        return (Imaging)ImagingError_ValueError("bad rank value");
    }

    // Every output pixel is written by the rank loop below
    imOut = ImagingNewDirty(im->mode, im->xsize - 2 * margin, im->ysize - 2 * margin);
    if (!imOut) {
        return NULL;
    }
    int xsize = imOut->xsize, ysize = imOut->ysize;

    /* malloc check ok, checked above */
    // restrict safe: buf is a private allocation, imOut is a fresh allocation.
#define RANK_BODY(type)                                                   \
    do {                                                                  \
        type *restrict buf = malloc(size2 * sizeof(type));                \
        if (!buf) {                                                       \
            goto nomemory;                                                \
        }                                                                 \
        for (int y = 0; y < ysize; y++) {                                 \
            type *restrict out = (type *)imOut->image[y];                 \
            for (int x = 0; x < xsize; x++) {                             \
                type *restrict p = buf;                                   \
                for (int i = 0; i < size; i++) {                          \
                    const type *row = (const type *)im->image[y + i] + x; \
                    for (int k = 0; k < size; k++) {                      \
                        *p++ = row[k];                                    \
                    }                                                     \
                }                                                         \
                out[x] = Rank##type(buf, size2, rank);                    \
            }                                                             \
        }                                                                 \
        free(buf);                                                        \
    } while (0)

    if (im->image8) {
        RANK_BODY(UINT8);
    } else if (im->type == IMAGING_TYPE_INT32) {
        RANK_BODY(INT32);
    } else if (im->type == IMAGING_TYPE_FLOAT32) {
        RANK_BODY(FLOAT32);
    } else {
        /* safety net (we shouldn't end up here) */
        ImagingDelete(imOut);
        return (Imaging)ImagingError_ModeError();
    }

    ImagingCopyPalette(imOut, im);

    return imOut;

nomemory:
    ImagingDelete(imOut);
    return (Imaging)ImagingError_MemoryError();
}
