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

/* Sliding histogram rank filter for 8-bit images (Huang, 1979).
   Moving the window one pixel to the right removes one column and adds
   another, so each step costs O(size) instead of the O(size^2) needed to
   copy and select the whole window. "below" counts the window samples
   less than v, the current output value, which moves only a little
   between neighbouring pixels. */
static void
RankUINT8(Imaging imOut, Imaging im, int size, int rank) {
    int x, y, i, v, below;
    int hist[256];

    if (imOut->xsize <= 0) {
        return;
    }

    for (y = 0; y < imOut->ysize; y++) {
        UINT8 *out = imOut->image8[y];
        UINT8 **in = &im->image8[y];

        memset(hist, 0, sizeof(hist));
        for (i = 0; i < size; i++) {
            for (x = 0; x < size; x++) {
                hist[in[i][x]]++;
            }
        }
        v = 0;
        below = 0;
        while (below + hist[v] <= rank) {
            below += hist[v++];
        }
        out[0] = (UINT8)v;

        for (x = 1; x < imOut->xsize; x++) {
            for (i = 0; i < size; i++) {
                UINT8 a = in[i][x - 1];
                UINT8 b = in[i][x + size - 1];
                hist[a]--;
                hist[b]++;
                below += (b < v) - (a < v);
            }
            while (below > rank) {
                below -= hist[--v];
            }
            while (below + hist[v] <= rank) {
                below += hist[v++];
            }
            out[x] = (UINT8)v;
        }
    }
}

/* Fast rank algorithm (due to Wirth), based on public domain code
   by Nicolas Devillard, available at http://ndevilla.free.fr */

#define SWAP(type, a, b)       \
    {                          \
        register type t = (a); \
        (a) = (b);             \
        (b) = t;               \
    }

#define MakeRankFunction(type)                       \
    static type Rank##type(type a[], int n, int k) { \
        register int i, j, l, m;                     \
        register type x;                             \
        l = 0;                                       \
        m = n - 1;                                   \
        while (l < m) {                              \
            x = a[k];                                \
            i = l;                                   \
            j = m;                                   \
            do {                                     \
                while (a[i] < x) {                   \
                    i++;                             \
                }                                    \
                while (x < a[j]) {                   \
                    j--;                             \
                }                                    \
                if (i <= j) {                        \
                    SWAP(type, a[i], a[j]);          \
                    i++;                             \
                    j--;                             \
                }                                    \
            } while (i <= j);                        \
            if (j < k) {                             \
                l = i;                               \
            }                                        \
            if (k < i) {                             \
                m = j;                               \
            }                                        \
        }                                            \
        return a[k];                                 \
    }

MakeRankFunction(INT32) MakeRankFunction(FLOAT32)

    Imaging ImagingRankFilter(Imaging im, int size, int rank) {
    Imaging imOut = NULL;
    ImagingSectionCookie cookie;
    int x, y;
    int i, margin, size2;

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

    /* malloc check ok, checked above */
#define RANK_BODY(type)                                                           \
    do {                                                                          \
        type *buf = malloc(size2 * sizeof(type));                                 \
        if (!buf) {                                                               \
            goto nomemory;                                                        \
        }                                                                         \
        ImagingSectionEnter(&cookie);                                             \
        for (y = 0; y < imOut->ysize; y++) {                                      \
            for (x = 0; x < imOut->xsize; x++) {                                  \
                for (i = 0; i < size; i++) {                                      \
                    memcpy(                                                       \
                        buf + i * size,                                           \
                        &IMAGING_PIXEL_##type(im, x, y + i),                      \
                        size * sizeof(type)                                       \
                    );                                                            \
                }                                                                 \
                IMAGING_PIXEL_##type(imOut, x, y) = Rank##type(buf, size2, rank); \
            }                                                                     \
        }                                                                         \
        ImagingSectionLeave(&cookie);                                             \
        free(buf);                                                                \
    } while (0)

    if (im->image8) {
        ImagingSectionEnter(&cookie);
        RankUINT8(imOut, im, size, rank);
        ImagingSectionLeave(&cookie);
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
