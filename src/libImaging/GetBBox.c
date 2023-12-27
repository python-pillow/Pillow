/*
 * The Python Imaging Library
 * $Id$
 *
 * helpers to bounding boxes, min/max values, number of colors, etc.
 *
 * history:
 * 1996-07-22 fl   Created
 * 1996-12-30 fl   Added projection stuff
 * 1998-07-12 fl   Added extrema stuff
 * 2004-09-17 fl   Added colors stuff
 *
 * Copyright (c) 1997-2004 by Secret Labs AB.
 * Copyright (c) 1996-2004 by Fredrik Lundh.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

int
ImagingGetBBox(Imaging im, int bbox[4], int alpha_only) {
    /* Get the bounding box for any non-zero data in the image.*/

    int x, y;
    int has_data;

    /* Initialize bounding box to max values */
    bbox[0] = im->xsize;
    bbox[1] = -1;
    bbox[2] = bbox[3] = 0;

#define GETBBOX(image, mask)              \
    for (y = 0; y < im->ysize; y++) {     \
        has_data = 0;                     \
        for (x = 0; x < im->xsize; x++) { \
            if (im->image[y][x] & mask) { \
                has_data = 1;             \
                if (x < bbox[0]) {        \
                    bbox[0] = x;          \
                }                         \
                if (x >= bbox[2]) {       \
                    bbox[2] = x + 1;      \
                }                         \
            }                             \
        }                                 \
        if (has_data) {                   \
            if (bbox[1] < 0) {            \
                bbox[1] = y;              \
            }                             \
            bbox[3] = y + 1;              \
        }                                 \
    }

    if (im->image8) {
        GETBBOX(image8, 0xff);
    } else {
        INT32 mask = 0xffffffff;
        if (im->bands == 3) {
            ((UINT8 *)&mask)[3] = 0;
        } else if (alpha_only && (
            strcmp(im->mode, "RGBa") == 0 || strcmp(im->mode, "RGBA") == 0 ||
            strcmp(im->mode, "La") == 0 || strcmp(im->mode, "LA") == 0 ||
            strcmp(im->mode, "PA") == 0
        )) {
#ifdef WORDS_BIGENDIAN
            mask = 0x000000ff;
#else
            mask = 0xff000000;
#endif
        }
        GETBBOX(image32, mask);
    }

    /* Check that we got a box */
    if (bbox[1] < 0) {
        return 0; /* no data */
    }

    return 1; /* ok */
}

int
ImagingGetProjection(Imaging im, UINT8 *xproj, UINT8 *yproj) {
    /* Get projection arrays for non-zero data in the image.*/

    int x, y;
    int has_data;

    /* Initialize projection arrays */
    memset(xproj, 0, im->xsize);
    memset(yproj, 0, im->ysize);

#define GETPROJ(image, mask)              \
    for (y = 0; y < im->ysize; y++) {     \
        has_data = 0;                     \
        for (x = 0; x < im->xsize; x++) { \
            if (im->image[y][x] & mask) { \
                has_data = 1;             \
                xproj[x] = 1;             \
            }                             \
        }                                 \
        if (has_data) {                   \
            yproj[y] = 1;                 \
        }                                 \
    }

    if (im->image8) {
        GETPROJ(image8, 0xff);
    } else {
        INT32 mask = 0xffffffff;
        if (im->bands == 3) {
            ((UINT8 *)&mask)[3] = 0;
        }
        GETPROJ(image32, mask);
    }

    return 1; /* ok */
}

int
ImagingGetExtrema(Imaging im, void *extrema) {
    int x, y;
    INT32 imin, imax;
    FLOAT32 fmin, fmax;

    if (im->bands != 1) {
        (void)ImagingError_ModeError();
        return -1; /* mismatch */
    }

    if (!im->xsize || !im->ysize) {
        return 0; /* zero size */
    }

    switch (im->type) {
        case IMAGING_TYPE_UINT8:
            imin = imax = im->image8[0][0];
            for (y = 0; y < im->ysize; y++) {
                UINT8 *in = im->image8[y];
                for (x = 0; x < im->xsize; x++) {
                    if (imin > in[x]) {
                        imin = in[x];
                    } else if (imax < in[x]) {
                        imax = in[x];
                    }
                }
            }
            ((UINT8 *)extrema)[0] = (UINT8)imin;
            ((UINT8 *)extrema)[1] = (UINT8)imax;
            break;
        case IMAGING_TYPE_INT32:
            imin = imax = im->image32[0][0];
            for (y = 0; y < im->ysize; y++) {
                INT32 *in = im->image32[y];
                for (x = 0; x < im->xsize; x++) {
                    if (imin > in[x]) {
                        imin = in[x];
                    } else if (imax < in[x]) {
                        imax = in[x];
                    }
                }
            }
            memcpy(extrema, &imin, sizeof(imin));
            memcpy(((char *)extrema) + sizeof(imin), &imax, sizeof(imax));
            break;
        case IMAGING_TYPE_FLOAT32:
            fmin = fmax = ((FLOAT32 *)im->image32[0])[0];
            for (y = 0; y < im->ysize; y++) {
                FLOAT32 *in = (FLOAT32 *)im->image32[y];
                for (x = 0; x < im->xsize; x++) {
                    if (fmin > in[x]) {
                        fmin = in[x];
                    } else if (fmax < in[x]) {
                        fmax = in[x];
                    }
                }
            }
            memcpy(extrema, &fmin, sizeof(fmin));
            memcpy(((char *)extrema) + sizeof(fmin), &fmax, sizeof(fmax));
            break;
        case IMAGING_TYPE_SPECIAL:
            if (strcmp(im->mode, "I;16") == 0) {
                UINT16 v;
                UINT8 *pixel = *im->image8;
#ifdef WORDS_BIGENDIAN
                v = pixel[0] + (pixel[1] << 8);
#else
                memcpy(&v, pixel, sizeof(v));
#endif
                imin = imax = v;
                for (y = 0; y < im->ysize; y++) {
                    for (x = 0; x < im->xsize; x++) {
                        pixel = (UINT8 *)im->image[y] + x * sizeof(v);
#ifdef WORDS_BIGENDIAN
                        v = pixel[0] + (pixel[1] << 8);
#else
                        memcpy(&v, pixel, sizeof(v));
#endif
                        if (imin > v) {
                            imin = v;
                        } else if (imax < v) {
                            imax = v;
                        }
                    }
                }
                v = (UINT16)imin;
                memcpy(extrema, &v, sizeof(v));
                v = (UINT16)imax;
                memcpy(((char *)extrema) + sizeof(v), &v, sizeof(v));
                break;
            }
            /* FALL THROUGH */
        default:
            (void)ImagingError_ModeError();
            return -1;
    }
    return 1; /* ok */
}

/* static ImagingColorItem* getcolors8(Imaging im, int maxcolors, int* size);*/
static ImagingColorItem *
getcolors32(Imaging im, int maxcolors, int *size);

ImagingColorItem *
ImagingGetColors(Imaging im, int maxcolors, int *size) {
    /* FIXME: add support for 8-bit images */
    return getcolors32(im, maxcolors, size);
}

static ImagingColorItem *
getcolors32(Imaging im, int maxcolors, int *size) {
    unsigned int h;
    unsigned int i, incr;
    int colors;
    INT32 pixel_mask;
    int x, y;
    ImagingColorItem *table;
    ImagingColorItem *v;

    unsigned int code_size;
    unsigned int code_poly;
    unsigned int code_mask;

    /* note: the hash algorithm used here is based on the dictionary
       code in Python 2.1.3; the exact implementation is borrowed from
       Python's Unicode property database (written by yours truly) /F */

    static int SIZES[] = {
        4,         3,  8,         3,  16,        3,  32,         5,  64,       3,
        128,       3,  256,       29, 512,       17, 1024,       9,  2048,     5,
        4096,      83, 8192,      27, 16384,     43, 32768,      3,  65536,    45,
        131072,    9,  262144,    39, 524288,    39, 1048576,    9,  2097152,  5,
        4194304,   3,  8388608,   33, 16777216,  27, 33554432,   9,  67108864, 71,
        134217728, 39, 268435456, 9,  536870912, 5,  1073741824, 83, 0};

    code_size = code_poly = code_mask = 0;

    for (i = 0; SIZES[i]; i += 2) {
        if (SIZES[i] > maxcolors) {
            code_size = SIZES[i];
            code_poly = SIZES[i + 1];
            code_mask = code_size - 1;
            break;
        }
    }

    /* printf("code_size=%d\n", code_size); */
    /* printf("code_poly=%d\n", code_poly); */

    if (!code_size) {
        return ImagingError_MemoryError(); /* just give up */
    }

    if (!im->image32) {
        return ImagingError_ModeError();
    }

    table = calloc(code_size + 1, sizeof(ImagingColorItem));
    if (!table) {
        return ImagingError_MemoryError();
    }

    pixel_mask = 0xffffffff;
    if (im->bands == 3) {
        ((UINT8 *)&pixel_mask)[3] = 0;
    }

    colors = 0;

    for (y = 0; y < im->ysize; y++) {
        INT32 *p = im->image32[y];
        for (x = 0; x < im->xsize; x++) {
            INT32 pixel = p[x] & pixel_mask;
            h = (pixel); /* null hashing */
            i = (~h) & code_mask;
            v = &table[i];
            if (!v->count) {
                /* add to table */
                if (colors++ == maxcolors) {
                    goto overflow;
                }
                v->x = x;
                v->y = y;
                v->pixel = pixel;
                v->count = 1;
                continue;
            } else if (v->pixel == pixel) {
                v->count++;
                continue;
            }
            incr = (h ^ (h >> 3)) & code_mask;
            if (!incr) {
                incr = code_mask;
            }
            for (;;) {
                i = (i + incr) & code_mask;
                v = &table[i];
                if (!v->count) {
                    /* add to table */
                    if (colors++ == maxcolors) {
                        goto overflow;
                    }
                    v->x = x;
                    v->y = y;
                    v->pixel = pixel;
                    v->count = 1;
                    break;
                } else if (v->pixel == pixel) {
                    v->count++;
                    break;
                }
                incr = incr << 1;
                if (incr > code_mask) {
                    incr = incr ^ code_poly;
                }
            }
        }
    }

overflow:

    /* pack the table */
    for (x = y = 0; x < (int)code_size; x++)
        if (table[x].count) {
            if (x != y) {
                table[y] = table[x];
            }
            y++;
        }
    table[y].count = 0; /* mark end of table */

    *size = colors;

    return table;
}
