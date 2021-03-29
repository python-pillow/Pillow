/*
 * The Python Imaging Library
 * $Id$
 *
 * various special effects and image generators
 *
 * history:
 * 1997-05-21 fl   Just for fun
 * 1997-06-05 fl   Added mandelbrot generator
 * 2003-05-24 fl   Added perlin_turbulence generator (in progress)
 *
 * Copyright (c) 1997-2003 by Fredrik Lundh.
 * Copyright (c) 1997 by Secret Labs AB.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include <math.h>

Imaging
ImagingEffectMandelbrot(int xsize, int ysize, double extent[4], int quality) {
    /* Generate a Mandelbrot set covering the given extent */

    Imaging im;
    int x, y, k;
    double width, height;
    double x1, y1, xi2, yi2, cr, ci, radius;
    double dr, di;

    /* Check arguments */
    width = extent[2] - extent[0];
    height = extent[3] - extent[1];
    if (width < 0.0 || height < 0.0 || quality < 2) {
        return (Imaging)ImagingError_ValueError(NULL);
    }

    im = ImagingNewDirty("L", xsize, ysize);
    if (!im) {
        return NULL;
    }

    dr = width / (xsize - 1);
    di = height / (ysize - 1);

    radius = 100.0;

    for (y = 0; y < ysize; y++) {
        UINT8 *buf = im->image8[y];
        for (x = 0; x < xsize; x++) {
            x1 = y1 = xi2 = yi2 = 0.0;
            cr = x * dr + extent[0];
            ci = y * di + extent[1];
            for (k = 1;; k++) {
                y1 = 2 * x1 * y1 + ci;
                x1 = xi2 - yi2 + cr;
                xi2 = x1 * x1;
                yi2 = y1 * y1;
                if ((xi2 + yi2) > radius) {
                    buf[x] = k * 255 / quality;
                    break;
                }
                if (k > quality) {
                    buf[x] = 0;
                    break;
                }
            }
        }
    }
    return im;
}

Imaging
ImagingEffectNoise(int xsize, int ysize, float sigma) {
    /* Generate Gaussian noise centered around 128 */

    Imaging imOut;
    int x, y;
    int nextok;
    double this, next;

    imOut = ImagingNewDirty("L", xsize, ysize);
    if (!imOut) {
        return NULL;
    }

    next = 0.0;
    nextok = 0;

    for (y = 0; y < imOut->ysize; y++) {
        UINT8 *out = imOut->image8[y];
        for (x = 0; x < imOut->xsize; x++) {
            if (nextok) {
                this = next;
                nextok = 0;
            } else {
                /* after numerical recipes */
                double v1, v2, radius, factor;
                do {
                    v1 = rand() * (2.0 / RAND_MAX) - 1.0;
                    v2 = rand() * (2.0 / RAND_MAX) - 1.0;
                    radius = v1 * v1 + v2 * v2;
                } while (radius >= 1.0);
                factor = sqrt(-2.0 * log(radius) / radius);
                this = factor * v1;
                next = factor * v2;
            }
            out[x] = CLIP8(128 + sigma * this);
        }
    }

    return imOut;
}

Imaging
ImagingEffectSpread(Imaging imIn, int distance) {
    /* Randomly spread pixels in an image */

    Imaging imOut;
    int x, y;

    imOut = ImagingNewDirty(imIn->mode, imIn->xsize, imIn->ysize);

    if (!imOut) {
        return NULL;
    }

#define SPREAD(type, image)                                                       \
    if (distance == 0) {                                                          \
        for (y = 0; y < imOut->ysize; y++) {                                      \
            for (x = 0; x < imOut->xsize; x++) {                                  \
                imOut->image[y][x] = imIn->image[y][x];                           \
            }                                                                     \
        }                                                                         \
    } else {                                                                      \
        for (y = 0; y < imOut->ysize; y++) {                                      \
            for (x = 0; x < imOut->xsize; x++) {                                  \
                int xx = x + (rand() % distance) - distance / 2;                  \
                int yy = y + (rand() % distance) - distance / 2;                  \
                if (xx >= 0 && xx < imIn->xsize && yy >= 0 && yy < imIn->ysize) { \
                    imOut->image[yy][xx] = imIn->image[y][x];                     \
                    imOut->image[y][x] = imIn->image[yy][xx];                     \
                } else {                                                          \
                    imOut->image[y][x] = imIn->image[y][x];                       \
                }                                                                 \
            }                                                                     \
        }                                                                         \
    }

    if (imIn->image8) {
        SPREAD(UINT8, image8);
    } else {
        SPREAD(INT32, image32);
    }

    ImagingCopyPalette(imOut, imIn);

    return imOut;
}
