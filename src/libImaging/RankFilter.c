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

#define RANK_MIN(a, b) ((a) < (b) ? (a) : (b))
#define RANK_MAX(a, b) ((a) < (b) ? (b) : (a))

#define MINMAX_BODY(type, op)                                     \
    do {                                                          \
        for (int y = 0; y < ysize; y++) {                         \
            type *out = (type *)imOut->image[y];                  \
            memcpy(out, im->image[y], xsize * sizeof(type));      \
            for (int i = 0; i < size; i++) {                      \
                const type *row = (const type *)im->image[y + i]; \
                for (int k = (i == 0); k < size; k++) {           \
                    const type *in = row + k;                     \
                    for (int x = 0; x < xsize; x++) {             \
                        out[x] = op(out[x], in[x]);               \
                    }                                             \
                }                                                 \
            }                                                     \
        }                                                         \
    } while (0)

// Median selection networks for 3x3 and 5x5 windows,
// original public-domain code via http://ndevilla.free.fr/median/median/src/optmed.c

#define CSWAP(type, p, i, j)                        \
    do {                                            \
        const type lo_ = p[i] < p[j] ? p[i] : p[j]; \
        p[j] = p[i] < p[j] ? p[j] : p[i];           \
        p[i] = lo_;                                 \
    } while (0)

#define MEDIAN_NETWORK_3(type, p) \
    CSWAP(type, p, 1, 2);         \
    CSWAP(type, p, 4, 5);         \
    CSWAP(type, p, 7, 8);         \
    CSWAP(type, p, 0, 1);         \
    CSWAP(type, p, 3, 4);         \
    CSWAP(type, p, 6, 7);         \
    CSWAP(type, p, 1, 2);         \
    CSWAP(type, p, 4, 5);         \
    CSWAP(type, p, 7, 8);         \
    CSWAP(type, p, 0, 3);         \
    CSWAP(type, p, 5, 8);         \
    CSWAP(type, p, 4, 7);         \
    CSWAP(type, p, 3, 6);         \
    CSWAP(type, p, 1, 4);         \
    CSWAP(type, p, 2, 5);         \
    CSWAP(type, p, 4, 7);         \
    CSWAP(type, p, 4, 2);         \
    CSWAP(type, p, 6, 4);         \
    CSWAP(type, p, 4, 2)

#define MEDIAN_NETWORK_5(type, p) \
    CSWAP(type, p, 0, 1);         \
    CSWAP(type, p, 3, 4);         \
    CSWAP(type, p, 2, 4);         \
    CSWAP(type, p, 2, 3);         \
    CSWAP(type, p, 6, 7);         \
    CSWAP(type, p, 5, 7);         \
    CSWAP(type, p, 5, 6);         \
    CSWAP(type, p, 9, 10);        \
    CSWAP(type, p, 8, 10);        \
    CSWAP(type, p, 8, 9);         \
    CSWAP(type, p, 12, 13);       \
    CSWAP(type, p, 11, 13);       \
    CSWAP(type, p, 11, 12);       \
    CSWAP(type, p, 15, 16);       \
    CSWAP(type, p, 14, 16);       \
    CSWAP(type, p, 14, 15);       \
    CSWAP(type, p, 18, 19);       \
    CSWAP(type, p, 17, 19);       \
    CSWAP(type, p, 17, 18);       \
    CSWAP(type, p, 21, 22);       \
    CSWAP(type, p, 20, 22);       \
    CSWAP(type, p, 20, 21);       \
    CSWAP(type, p, 23, 24);       \
    CSWAP(type, p, 2, 5);         \
    CSWAP(type, p, 3, 6);         \
    CSWAP(type, p, 0, 6);         \
    CSWAP(type, p, 0, 3);         \
    CSWAP(type, p, 4, 7);         \
    CSWAP(type, p, 1, 7);         \
    CSWAP(type, p, 1, 4);         \
    CSWAP(type, p, 11, 14);       \
    CSWAP(type, p, 8, 14);        \
    CSWAP(type, p, 8, 11);        \
    CSWAP(type, p, 12, 15);       \
    CSWAP(type, p, 9, 15);        \
    CSWAP(type, p, 9, 12);        \
    CSWAP(type, p, 13, 16);       \
    CSWAP(type, p, 10, 16);       \
    CSWAP(type, p, 10, 13);       \
    CSWAP(type, p, 20, 23);       \
    CSWAP(type, p, 17, 23);       \
    CSWAP(type, p, 17, 20);       \
    CSWAP(type, p, 21, 24);       \
    CSWAP(type, p, 18, 24);       \
    CSWAP(type, p, 18, 21);       \
    CSWAP(type, p, 19, 22);       \
    CSWAP(type, p, 8, 17);        \
    CSWAP(type, p, 9, 18);        \
    CSWAP(type, p, 0, 18);        \
    CSWAP(type, p, 0, 9);         \
    CSWAP(type, p, 10, 19);       \
    CSWAP(type, p, 1, 19);        \
    CSWAP(type, p, 1, 10);        \
    CSWAP(type, p, 11, 20);       \
    CSWAP(type, p, 2, 20);        \
    CSWAP(type, p, 2, 11);        \
    CSWAP(type, p, 12, 21);       \
    CSWAP(type, p, 3, 21);        \
    CSWAP(type, p, 3, 12);        \
    CSWAP(type, p, 13, 22);       \
    CSWAP(type, p, 4, 22);        \
    CSWAP(type, p, 4, 13);        \
    CSWAP(type, p, 14, 23);       \
    CSWAP(type, p, 5, 23);        \
    CSWAP(type, p, 5, 14);        \
    CSWAP(type, p, 15, 24);       \
    CSWAP(type, p, 6, 24);        \
    CSWAP(type, p, 6, 15);        \
    CSWAP(type, p, 7, 16);        \
    CSWAP(type, p, 7, 19);        \
    CSWAP(type, p, 13, 21);       \
    CSWAP(type, p, 15, 23);       \
    CSWAP(type, p, 7, 13);        \
    CSWAP(type, p, 7, 15);        \
    CSWAP(type, p, 1, 9);         \
    CSWAP(type, p, 3, 11);        \
    CSWAP(type, p, 5, 17);        \
    CSWAP(type, p, 11, 17);       \
    CSWAP(type, p, 9, 17);        \
    CSWAP(type, p, 4, 10);        \
    CSWAP(type, p, 6, 12);        \
    CSWAP(type, p, 7, 14);        \
    CSWAP(type, p, 4, 6);         \
    CSWAP(type, p, 4, 7);         \
    CSWAP(type, p, 12, 14);       \
    CSWAP(type, p, 10, 14);       \
    CSWAP(type, p, 6, 7);         \
    CSWAP(type, p, 10, 12);       \
    CSWAP(type, p, 6, 10);        \
    CSWAP(type, p, 6, 17);        \
    CSWAP(type, p, 12, 17);       \
    CSWAP(type, p, 7, 17);        \
    CSWAP(type, p, 7, 10);        \
    CSWAP(type, p, 12, 18);       \
    CSWAP(type, p, 7, 12);        \
    CSWAP(type, p, 10, 18);       \
    CSWAP(type, p, 12, 20);       \
    CSWAP(type, p, 10, 20);       \
    CSWAP(type, p, 10, 12)

// restrict safe: imOut is a fresh allocation.
#define MEDIAN_BODY(type, size)                           \
    do {                                                  \
        for (int y = 0; y < ysize; y++) {                 \
            const type *rows[size];                       \
            for (int i = 0; i < size; i++) {              \
                rows[i] = (const type *)im->image[y + i]; \
            }                                             \
            type *restrict out = (type *)imOut->image[y]; \
            for (int x = 0; x < xsize; x++) {             \
                type p[size * size];                      \
                for (int i = 0; i < size; i++) {          \
                    for (int k = 0; k < size; k++) {      \
                        p[i * size + k] = rows[i][x + k]; \
                    }                                     \
                }                                         \
                MEDIAN_NETWORK_##size(type, p);           \
                out[x] = p[size * size / 2];              \
            }                                             \
        }                                                 \
    } while (0)

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
#define RANK_BODY(type, rank_fn)                                          \
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
                out[x] = rank_fn(buf, size2, rank);                       \
            }                                                             \
        }                                                                 \
        free(buf);                                                        \
    } while (0)

#define RANK_DISPATCH(type)                          \
    do {                                             \
        if (rank == 0) {                             \
            MINMAX_BODY(type, RANK_MIN);             \
        } else if (rank == size2 - 1) {              \
            MINMAX_BODY(type, RANK_MAX);             \
        } else if (rank == size2 / 2 && size == 3) { \
            MEDIAN_BODY(type, 3);                    \
        } else if (rank == size2 / 2 && size == 5) { \
            MEDIAN_BODY(type, 5);                    \
        } else {                                     \
            RANK_BODY(type, Rank##type);             \
        }                                            \
    } while (0)

    if (im->image8) {
        RANK_DISPATCH(UINT8);
    } else if (im->type == IMAGING_TYPE_INT32) {
        RANK_DISPATCH(INT32);
    } else if (im->type == IMAGING_TYPE_FLOAT32) {
        RANK_DISPATCH(FLOAT32);
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
