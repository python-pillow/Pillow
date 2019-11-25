#include "Imaging.h"

#include <math.h>

#define ROUND_UP(f) ((int) ((f) >= 0.0 ? (f) + 0.5F : (f) - 0.5F))


UINT32
division_UINT32(int divider, int result_bits)
{
    UINT32 max_dividend = (1 << result_bits) * divider;
    float max_int = (1 << 30) * 4.0;
    return (UINT32) (max_int / max_dividend);
}

void
ImagingReduce2x2(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int xscale = 2, yscale = 2;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*yscale + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*yscale + 1];
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7];
                        v = MAKE_UINT32((ss0 + amend) >> 2, 0,
                                        0, (ss3 + amend) >> 2);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6];
                        v = MAKE_UINT32((ss0 + amend) >> 2, (ss1 + amend) >> 2,
                                        (ss2 + amend) >> 2, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7];
                        v = MAKE_UINT32((ss0 + amend) >> 2, (ss1 + amend) >> 2,
                                        (ss2 + amend) >> 2, (ss3 + amend) >> 2);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce3x3(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int xscale = 3, yscale = 3;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*yscale + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*yscale + 1];
                UINT8 *line2 = (UINT8 *)imIn->image[y*yscale + 2];
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, 0,
                            0, ((ss3 + amend) * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, ((ss1 + amend) * multiplier) >> 24,
                            ((ss2 + amend) * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, ((ss1 + amend) * multiplier) >> 24,
                            ((ss2 + amend) * multiplier) >> 24, ((ss3 + amend) * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce4x4(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int xscale = 4, yscale = 4;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*yscale + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*yscale + 1];
                UINT8 *line2 = (UINT8 *)imIn->image[y*yscale + 2];
                UINT8 *line3 = (UINT8 *)imIn->image[y*yscale + 3];
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] + line0[x*xscale*4 + 15] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] + line1[x*xscale*4 + 15] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11] + line2[x*xscale*4 + 15] +
                              line3[x*xscale*4 + 3] + line3[x*xscale*4 + 7] + line3[x*xscale*4 + 11] + line3[x*xscale*4 + 15];
                        v = MAKE_UINT32((ss0 + amend) >> 4, 0,
                                        0, (ss3 + amend) >> 4);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] + line0[x*xscale*4 + 13] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] + line1[x*xscale*4 + 13] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9] + line2[x*xscale*4 + 13] +
                              line3[x*xscale*4 + 1] + line3[x*xscale*4 + 5] + line3[x*xscale*4 + 9] + line3[x*xscale*4 + 13];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] + line0[x*xscale*4 + 14] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] + line1[x*xscale*4 + 14] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10] + line2[x*xscale*4 + 14] +
                              line3[x*xscale*4 + 2] + line3[x*xscale*4 + 6] + line3[x*xscale*4 + 10] + line3[x*xscale*4 + 14];
                        v = MAKE_UINT32((ss0 + amend) >> 4, (ss1 + amend) >> 4,
                                        (ss2 + amend) >> 4, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] + line0[x*xscale*4 + 13] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] + line1[x*xscale*4 + 13] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9] + line2[x*xscale*4 + 13] +
                              line3[x*xscale*4 + 1] + line3[x*xscale*4 + 5] + line3[x*xscale*4 + 9] + line3[x*xscale*4 + 13];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] + line0[x*xscale*4 + 14] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] + line1[x*xscale*4 + 14] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10] + line2[x*xscale*4 + 14] +
                              line3[x*xscale*4 + 2] + line3[x*xscale*4 + 6] + line3[x*xscale*4 + 10] + line3[x*xscale*4 + 14];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] + line0[x*xscale*4 + 15] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] + line1[x*xscale*4 + 15] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11] + line2[x*xscale*4 + 15] +
                              line3[x*xscale*4 + 3] + line3[x*xscale*4 + 7] + line3[x*xscale*4 + 11] + line3[x*xscale*4 + 15];
                        v = MAKE_UINT32((ss0 + amend) >> 4, (ss1 + amend) >> 4,
                                        (ss2 + amend) >> 4, (ss3 + amend) >> 4);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce5x5(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int xscale = 5, yscale = 5;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*yscale + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*yscale + 1];
                UINT8 *line2 = (UINT8 *)imIn->image[y*yscale + 2];
                UINT8 *line3 = (UINT8 *)imIn->image[y*yscale + 3];
                UINT8 *line4 = (UINT8 *)imIn->image[y*yscale + 4];
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] + line0[x*xscale*4 + 16] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] + line1[x*xscale*4 + 16] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] + line2[x*xscale*4 + 16] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12] + line3[x*xscale*4 + 16] +
                              line4[x*xscale*4 + 0] + line4[x*xscale*4 + 4] + line4[x*xscale*4 + 8] + line4[x*xscale*4 + 12] + line4[x*xscale*4 + 16];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] + line0[x*xscale*4 + 15] + line0[x*xscale*4 + 19] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] + line1[x*xscale*4 + 15] + line1[x*xscale*4 + 19] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11] + line2[x*xscale*4 + 15] + line2[x*xscale*4 + 19] +
                              line3[x*xscale*4 + 3] + line3[x*xscale*4 + 7] + line3[x*xscale*4 + 11] + line3[x*xscale*4 + 15] + line3[x*xscale*4 + 19] +
                              line4[x*xscale*4 + 3] + line4[x*xscale*4 + 7] + line4[x*xscale*4 + 11] + line4[x*xscale*4 + 15] + line4[x*xscale*4 + 19];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, 0,
                            0, ((ss3 + amend) * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] + line0[x*xscale*4 + 16] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] + line1[x*xscale*4 + 16] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] + line2[x*xscale*4 + 16] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12] + line3[x*xscale*4 + 16] +
                              line4[x*xscale*4 + 0] + line4[x*xscale*4 + 4] + line4[x*xscale*4 + 8] + line4[x*xscale*4 + 12] + line4[x*xscale*4 + 16];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] + line0[x*xscale*4 + 13] + line0[x*xscale*4 + 17] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] + line1[x*xscale*4 + 13] + line1[x*xscale*4 + 17] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9] + line2[x*xscale*4 + 13] + line2[x*xscale*4 + 17] +
                              line3[x*xscale*4 + 1] + line3[x*xscale*4 + 5] + line3[x*xscale*4 + 9] + line3[x*xscale*4 + 13] + line3[x*xscale*4 + 17] +
                              line4[x*xscale*4 + 1] + line4[x*xscale*4 + 5] + line4[x*xscale*4 + 9] + line4[x*xscale*4 + 13] + line4[x*xscale*4 + 17];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] + line0[x*xscale*4 + 14] + line0[x*xscale*4 + 18] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] + line1[x*xscale*4 + 14] + line1[x*xscale*4 + 18] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10] + line2[x*xscale*4 + 14] + line2[x*xscale*4 + 18] +
                              line3[x*xscale*4 + 2] + line3[x*xscale*4 + 6] + line3[x*xscale*4 + 10] + line3[x*xscale*4 + 14] + line3[x*xscale*4 + 18] +
                              line4[x*xscale*4 + 2] + line4[x*xscale*4 + 6] + line4[x*xscale*4 + 10] + line4[x*xscale*4 + 14] + line4[x*xscale*4 + 18];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, ((ss1 + amend) * multiplier) >> 24,
                            ((ss2 + amend) * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] + line0[x*xscale*4 + 16] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] + line1[x*xscale*4 + 16] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] + line2[x*xscale*4 + 16] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12] + line3[x*xscale*4 + 16] +
                              line4[x*xscale*4 + 0] + line4[x*xscale*4 + 4] + line4[x*xscale*4 + 8] + line4[x*xscale*4 + 12] + line4[x*xscale*4 + 16];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] + line0[x*xscale*4 + 13] + line0[x*xscale*4 + 17] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] + line1[x*xscale*4 + 13] + line1[x*xscale*4 + 17] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9] + line2[x*xscale*4 + 13] + line2[x*xscale*4 + 17] +
                              line3[x*xscale*4 + 1] + line3[x*xscale*4 + 5] + line3[x*xscale*4 + 9] + line3[x*xscale*4 + 13] + line3[x*xscale*4 + 17] +
                              line4[x*xscale*4 + 1] + line4[x*xscale*4 + 5] + line4[x*xscale*4 + 9] + line4[x*xscale*4 + 13] + line4[x*xscale*4 + 17];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] + line0[x*xscale*4 + 14] + line0[x*xscale*4 + 18] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] + line1[x*xscale*4 + 14] + line1[x*xscale*4 + 18] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10] + line2[x*xscale*4 + 14] + line2[x*xscale*4 + 18] +
                              line3[x*xscale*4 + 2] + line3[x*xscale*4 + 6] + line3[x*xscale*4 + 10] + line3[x*xscale*4 + 14] + line3[x*xscale*4 + 18] +
                              line4[x*xscale*4 + 2] + line4[x*xscale*4 + 6] + line4[x*xscale*4 + 10] + line4[x*xscale*4 + 14] + line4[x*xscale*4 + 18];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] + line0[x*xscale*4 + 15] + line0[x*xscale*4 + 19] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] + line1[x*xscale*4 + 15] + line1[x*xscale*4 + 19] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11] + line2[x*xscale*4 + 15] + line2[x*xscale*4 + 19] +
                              line3[x*xscale*4 + 3] + line3[x*xscale*4 + 7] + line3[x*xscale*4 + 11] + line3[x*xscale*4 + 15] + line3[x*xscale*4 + 19] +
                              line4[x*xscale*4 + 3] + line4[x*xscale*4 + 7] + line4[x*xscale*4 + 11] + line4[x*xscale*4 + 15] + line4[x*xscale*4 + 19];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, ((ss1 + amend) * multiplier) >> 24,
                            ((ss2 + amend) * multiplier) >> 24, ((ss3 + amend) * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce6x6(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int xscale = 6, yscale = 6;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*yscale + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*yscale + 1];
                UINT8 *line2 = (UINT8 *)imIn->image[y*yscale + 2];
                UINT8 *line3 = (UINT8 *)imIn->image[y*yscale + 3];
                UINT8 *line4 = (UINT8 *)imIn->image[y*yscale + 4];
                UINT8 *line5 = (UINT8 *)imIn->image[y*yscale + 5];
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] + line0[x*xscale*4 + 16] + line0[x*xscale*4 + 20] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] + line1[x*xscale*4 + 16] + line1[x*xscale*4 + 20] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] + line2[x*xscale*4 + 16] + line2[x*xscale*4 + 20] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12] + line3[x*xscale*4 + 16] + line3[x*xscale*4 + 20] +
                              line4[x*xscale*4 + 0] + line4[x*xscale*4 + 4] + line4[x*xscale*4 + 8] + line4[x*xscale*4 + 12] + line4[x*xscale*4 + 16] + line4[x*xscale*4 + 20] +
                              line5[x*xscale*4 + 0] + line5[x*xscale*4 + 4] + line5[x*xscale*4 + 8] + line5[x*xscale*4 + 12] + line5[x*xscale*4 + 16] + line5[x*xscale*4 + 20];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] + line0[x*xscale*4 + 15] + line0[x*xscale*4 + 19] + line0[x*xscale*4 + 23] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] + line1[x*xscale*4 + 15] + line1[x*xscale*4 + 19] + line1[x*xscale*4 + 23] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11] + line2[x*xscale*4 + 15] + line2[x*xscale*4 + 19] + line2[x*xscale*4 + 23] +
                              line3[x*xscale*4 + 3] + line3[x*xscale*4 + 7] + line3[x*xscale*4 + 11] + line3[x*xscale*4 + 15] + line3[x*xscale*4 + 19] + line3[x*xscale*4 + 23] +
                              line4[x*xscale*4 + 3] + line4[x*xscale*4 + 7] + line4[x*xscale*4 + 11] + line4[x*xscale*4 + 15] + line4[x*xscale*4 + 19] + line4[x*xscale*4 + 23] +
                              line5[x*xscale*4 + 3] + line5[x*xscale*4 + 7] + line5[x*xscale*4 + 11] + line5[x*xscale*4 + 15] + line5[x*xscale*4 + 19] + line5[x*xscale*4 + 23];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, 0,
                            0, ((ss3 + amend) * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] + line0[x*xscale*4 + 16] + line0[x*xscale*4 + 20] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] + line1[x*xscale*4 + 16] + line1[x*xscale*4 + 20] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] + line2[x*xscale*4 + 16] + line2[x*xscale*4 + 20] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12] + line3[x*xscale*4 + 16] + line3[x*xscale*4 + 20] +
                              line4[x*xscale*4 + 0] + line4[x*xscale*4 + 4] + line4[x*xscale*4 + 8] + line4[x*xscale*4 + 12] + line4[x*xscale*4 + 16] + line4[x*xscale*4 + 20] +
                              line5[x*xscale*4 + 0] + line5[x*xscale*4 + 4] + line5[x*xscale*4 + 8] + line5[x*xscale*4 + 12] + line5[x*xscale*4 + 16] + line5[x*xscale*4 + 20];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] + line0[x*xscale*4 + 13] + line0[x*xscale*4 + 17] + line0[x*xscale*4 + 21] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] + line1[x*xscale*4 + 13] + line1[x*xscale*4 + 17] + line1[x*xscale*4 + 21] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9] + line2[x*xscale*4 + 13] + line2[x*xscale*4 + 17] + line2[x*xscale*4 + 21] +
                              line3[x*xscale*4 + 1] + line3[x*xscale*4 + 5] + line3[x*xscale*4 + 9] + line3[x*xscale*4 + 13] + line3[x*xscale*4 + 17] + line3[x*xscale*4 + 21] +
                              line4[x*xscale*4 + 1] + line4[x*xscale*4 + 5] + line4[x*xscale*4 + 9] + line4[x*xscale*4 + 13] + line4[x*xscale*4 + 17] + line4[x*xscale*4 + 21] +
                              line5[x*xscale*4 + 1] + line5[x*xscale*4 + 5] + line5[x*xscale*4 + 9] + line5[x*xscale*4 + 13] + line5[x*xscale*4 + 17] + line5[x*xscale*4 + 21];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] + line0[x*xscale*4 + 14] + line0[x*xscale*4 + 18] + line0[x*xscale*4 + 22] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] + line1[x*xscale*4 + 14] + line1[x*xscale*4 + 18] + line1[x*xscale*4 + 22] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10] + line2[x*xscale*4 + 14] + line2[x*xscale*4 + 18] + line2[x*xscale*4 + 22] +
                              line3[x*xscale*4 + 2] + line3[x*xscale*4 + 6] + line3[x*xscale*4 + 10] + line3[x*xscale*4 + 14] + line3[x*xscale*4 + 18] + line3[x*xscale*4 + 22] +
                              line4[x*xscale*4 + 2] + line4[x*xscale*4 + 6] + line4[x*xscale*4 + 10] + line4[x*xscale*4 + 14] + line4[x*xscale*4 + 18] + line4[x*xscale*4 + 22] +
                              line5[x*xscale*4 + 2] + line5[x*xscale*4 + 6] + line5[x*xscale*4 + 10] + line5[x*xscale*4 + 14] + line5[x*xscale*4 + 18] + line5[x*xscale*4 + 22];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, ((ss1 + amend) * multiplier) >> 24,
                            ((ss2 + amend) * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        ss0 = line0[x*xscale*4 + 0] + line0[x*xscale*4 + 4] + line0[x*xscale*4 + 8] + line0[x*xscale*4 + 12] + line0[x*xscale*4 + 16] + line0[x*xscale*4 + 20] +
                              line1[x*xscale*4 + 0] + line1[x*xscale*4 + 4] + line1[x*xscale*4 + 8] + line1[x*xscale*4 + 12] + line1[x*xscale*4 + 16] + line1[x*xscale*4 + 20] +
                              line2[x*xscale*4 + 0] + line2[x*xscale*4 + 4] + line2[x*xscale*4 + 8] + line2[x*xscale*4 + 12] + line2[x*xscale*4 + 16] + line2[x*xscale*4 + 20] +
                              line3[x*xscale*4 + 0] + line3[x*xscale*4 + 4] + line3[x*xscale*4 + 8] + line3[x*xscale*4 + 12] + line3[x*xscale*4 + 16] + line3[x*xscale*4 + 20] +
                              line4[x*xscale*4 + 0] + line4[x*xscale*4 + 4] + line4[x*xscale*4 + 8] + line4[x*xscale*4 + 12] + line4[x*xscale*4 + 16] + line4[x*xscale*4 + 20] +
                              line5[x*xscale*4 + 0] + line5[x*xscale*4 + 4] + line5[x*xscale*4 + 8] + line5[x*xscale*4 + 12] + line5[x*xscale*4 + 16] + line5[x*xscale*4 + 20];
                        ss1 = line0[x*xscale*4 + 1] + line0[x*xscale*4 + 5] + line0[x*xscale*4 + 9] + line0[x*xscale*4 + 13] + line0[x*xscale*4 + 17] + line0[x*xscale*4 + 21] +
                              line1[x*xscale*4 + 1] + line1[x*xscale*4 + 5] + line1[x*xscale*4 + 9] + line1[x*xscale*4 + 13] + line1[x*xscale*4 + 17] + line1[x*xscale*4 + 21] +
                              line2[x*xscale*4 + 1] + line2[x*xscale*4 + 5] + line2[x*xscale*4 + 9] + line2[x*xscale*4 + 13] + line2[x*xscale*4 + 17] + line2[x*xscale*4 + 21] +
                              line3[x*xscale*4 + 1] + line3[x*xscale*4 + 5] + line3[x*xscale*4 + 9] + line3[x*xscale*4 + 13] + line3[x*xscale*4 + 17] + line3[x*xscale*4 + 21] +
                              line4[x*xscale*4 + 1] + line4[x*xscale*4 + 5] + line4[x*xscale*4 + 9] + line4[x*xscale*4 + 13] + line4[x*xscale*4 + 17] + line4[x*xscale*4 + 21] +
                              line5[x*xscale*4 + 1] + line5[x*xscale*4 + 5] + line5[x*xscale*4 + 9] + line5[x*xscale*4 + 13] + line5[x*xscale*4 + 17] + line5[x*xscale*4 + 21];
                        ss2 = line0[x*xscale*4 + 2] + line0[x*xscale*4 + 6] + line0[x*xscale*4 + 10] + line0[x*xscale*4 + 14] + line0[x*xscale*4 + 18] + line0[x*xscale*4 + 22] +
                              line1[x*xscale*4 + 2] + line1[x*xscale*4 + 6] + line1[x*xscale*4 + 10] + line1[x*xscale*4 + 14] + line1[x*xscale*4 + 18] + line1[x*xscale*4 + 22] +
                              line2[x*xscale*4 + 2] + line2[x*xscale*4 + 6] + line2[x*xscale*4 + 10] + line2[x*xscale*4 + 14] + line2[x*xscale*4 + 18] + line2[x*xscale*4 + 22] +
                              line3[x*xscale*4 + 2] + line3[x*xscale*4 + 6] + line3[x*xscale*4 + 10] + line3[x*xscale*4 + 14] + line3[x*xscale*4 + 18] + line3[x*xscale*4 + 22] +
                              line4[x*xscale*4 + 2] + line4[x*xscale*4 + 6] + line4[x*xscale*4 + 10] + line4[x*xscale*4 + 14] + line4[x*xscale*4 + 18] + line4[x*xscale*4 + 22] +
                              line5[x*xscale*4 + 2] + line5[x*xscale*4 + 6] + line5[x*xscale*4 + 10] + line5[x*xscale*4 + 14] + line5[x*xscale*4 + 18] + line5[x*xscale*4 + 22];
                        ss3 = line0[x*xscale*4 + 3] + line0[x*xscale*4 + 7] + line0[x*xscale*4 + 11] + line0[x*xscale*4 + 15] + line0[x*xscale*4 + 19] + line0[x*xscale*4 + 23] +
                              line1[x*xscale*4 + 3] + line1[x*xscale*4 + 7] + line1[x*xscale*4 + 11] + line1[x*xscale*4 + 15] + line1[x*xscale*4 + 19] + line1[x*xscale*4 + 23] +
                              line2[x*xscale*4 + 3] + line2[x*xscale*4 + 7] + line2[x*xscale*4 + 11] + line2[x*xscale*4 + 15] + line2[x*xscale*4 + 19] + line2[x*xscale*4 + 23] +
                              line3[x*xscale*4 + 3] + line3[x*xscale*4 + 7] + line3[x*xscale*4 + 11] + line3[x*xscale*4 + 15] + line3[x*xscale*4 + 19] + line3[x*xscale*4 + 23] +
                              line4[x*xscale*4 + 3] + line4[x*xscale*4 + 7] + line4[x*xscale*4 + 11] + line4[x*xscale*4 + 15] + line4[x*xscale*4 + 19] + line4[x*xscale*4 + 23] +
                              line5[x*xscale*4 + 3] + line5[x*xscale*4 + 7] + line5[x*xscale*4 + 11] + line5[x*xscale*4 + 15] + line5[x*xscale*4 + 19] + line5[x*xscale*4 + 23];
                        v = MAKE_UINT32(
                            ((ss0 + amend) * multiplier) >> 24, ((ss1 + amend) * multiplier) >> 24,
                            ((ss2 + amend) * multiplier) >> 24, ((ss3 + amend) * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce1xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 1;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0];
                            ss3 += line[x*xscale*4 + 3];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0];
                            ss1 += line[x*xscale*4 + 1];
                            ss2 += line[x*xscale*4 + 2];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0];
                            ss1 += line[x*xscale*4 + 1];
                            ss2 += line[x*xscale*4 + 2];
                            ss3 += line[x*xscale*4 + 3];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce2xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 2;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce3xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce4xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 4;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] +
                                   line[x*xscale*4 + 8] + line[x*xscale*4 + 12];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] +
                                   line[x*xscale*4 + 11] + line[x*xscale*4 + 15];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] +
                                   line[x*xscale*4 + 8]  + line[x*xscale*4 + 12];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] +
                                   line[x*xscale*4 + 9]  + line[x*xscale*4 + 13];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] +
                                   line[x*xscale*4 + 10]  + line[x*xscale*4 + 14];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] +
                                   line[x*xscale*4 + 8] + line[x*xscale*4 + 12];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] +
                                   line[x*xscale*4 + 9] + line[x*xscale*4 + 13];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] +
                                   line[x*xscale*4 + 10] + line[x*xscale*4 + 14];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] +
                                   line[x*xscale*4 + 11] + line[x*xscale*4 + 15];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce5xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 5;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] +
                                   line[x*xscale*4 + 8] + line[x*xscale*4 + 12] + line[x*xscale*4 + 16];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] +
                                   line[x*xscale*4 + 11] + line[x*xscale*4 + 15] + line[x*xscale*4 + 19];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] +
                                   line[x*xscale*4 + 8] + line[x*xscale*4 + 12] + line[x*xscale*4 + 16];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] +
                                   line[x*xscale*4 + 9] + line[x*xscale*4 + 13] + line[x*xscale*4 + 17];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] +
                                   line[x*xscale*4 + 10] + line[x*xscale*4 + 14] + line[x*xscale*4 + 18];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] +
                                   line[x*xscale*4 + 8] + line[x*xscale*4 + 12] + line[x*xscale*4 + 16];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] +
                                   line[x*xscale*4 + 9] + line[x*xscale*4 + 13] + line[x*xscale*4 + 17];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] +
                                   line[x*xscale*4 + 10] + line[x*xscale*4 + 14] + line[x*xscale*4 + 18];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] +
                                   line[x*xscale*4 + 11] + line[x*xscale*4 + 15] + line[x*xscale*4 + 19];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce6xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 6;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11] +
                                   line[x*xscale*4 + 15] + line[x*xscale*4 + 19] + line[x*xscale*4 + 23];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9] +
                                   line[x*xscale*4 + 13] + line[x*xscale*4 + 17] + line[x*xscale*4 + 21];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10] +
                                   line[x*xscale*4 + 14] + line[x*xscale*4 + 18] + line[x*xscale*4 + 22];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9] +
                                   line[x*xscale*4 + 13] + line[x*xscale*4 + 17] + line[x*xscale*4 + 21];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10] +
                                   line[x*xscale*4 + 14] + line[x*xscale*4 + 18] + line[x*xscale*4 + 22];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11] +
                                   line[x*xscale*4 + 15] + line[x*xscale*4 + 19] + line[x*xscale*4 + 23];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce7xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 7;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20] +
                                   line[x*xscale*4 + 24];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11] +
                                   line[x*xscale*4 + 15] + line[x*xscale*4 + 19] + line[x*xscale*4 + 23] +
                                   line[x*xscale*4 + 27];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20] +
                                   line[x*xscale*4 + 24];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9] +
                                   line[x*xscale*4 + 13] + line[x*xscale*4 + 17] + line[x*xscale*4 + 21] +
                                   line[x*xscale*4 + 25];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10] +
                                   line[x*xscale*4 + 14] + line[x*xscale*4 + 18] + line[x*xscale*4 + 22] +
                                   line[x*xscale*4 + 26];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20] +
                                   line[x*xscale*4 + 24];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9] +
                                   line[x*xscale*4 + 13] + line[x*xscale*4 + 17] + line[x*xscale*4 + 21] +
                                   line[x*xscale*4 + 25];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10] +
                                   line[x*xscale*4 + 14] + line[x*xscale*4 + 18] + line[x*xscale*4 + 22] +
                                   line[x*xscale*4 + 26];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11] +
                                   line[x*xscale*4 + 15] + line[x*xscale*4 + 19] + line[x*xscale*4 + 23] +
                                   line[x*xscale*4 + 27];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}

void
ImagingReduce8xN(Imaging imOut, Imaging imIn, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, yy;
    int xscale = 8;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20] +
                                   line[x*xscale*4 + 24] + line[x*xscale*4 + 28];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11] +
                                   line[x*xscale*4 + 15] + line[x*xscale*4 + 19] + line[x*xscale*4 + 23] +
                                   line[x*xscale*4 + 27] + line[x*xscale*4 + 31];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, 0,
                            0, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20] +
                                   line[x*xscale*4 + 24] + line[x*xscale*4 + 28];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9] +
                                   line[x*xscale*4 + 13] + line[x*xscale*4 + 17] + line[x*xscale*4 + 21] +
                                   line[x*xscale*4 + 25] + line[x*xscale*4 + 29];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10] +
                                   line[x*xscale*4 + 14] + line[x*xscale*4 + 18] + line[x*xscale*4 + 22] +
                                   line[x*xscale*4 + 26] + line[x*xscale*4 + 30];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*xscale*4 + 0] + line[x*xscale*4 + 4] + line[x*xscale*4 + 8] +
                                   line[x*xscale*4 + 12] + line[x*xscale*4 + 16] + line[x*xscale*4 + 20] +
                                   line[x*xscale*4 + 24] + line[x*xscale*4 + 28];
                            ss1 += line[x*xscale*4 + 1] + line[x*xscale*4 + 5] + line[x*xscale*4 + 9] +
                                   line[x*xscale*4 + 13] + line[x*xscale*4 + 17] + line[x*xscale*4 + 21] +
                                   line[x*xscale*4 + 25] + line[x*xscale*4 + 29];
                            ss2 += line[x*xscale*4 + 2] + line[x*xscale*4 + 6] + line[x*xscale*4 + 10] +
                                   line[x*xscale*4 + 14] + line[x*xscale*4 + 18] + line[x*xscale*4 + 22] +
                                   line[x*xscale*4 + 26] + line[x*xscale*4 + 30];
                            ss3 += line[x*xscale*4 + 3] + line[x*xscale*4 + 7] + line[x*xscale*4 + 11] +
                                   line[x*xscale*4 + 15] + line[x*xscale*4 + 19] + line[x*xscale*4 + 23] +
                                   line[x*xscale*4 + 27] + line[x*xscale*4 + 31];
                        }
                        v = MAKE_UINT32(
                            (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                            (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}


void
ImagingReduceCorners(Imaging imOut, Imaging imIn, int xscale, int yscale)
{
    ImagingSectionCookie cookie;
    int x, y, xx, yy;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            if (imOut->xsize > imIn->xsize / xscale) {
                UINT32 multiplier = division_UINT32(xscale * yscale, 8);
                UINT32 amend = yscale;
                for (y = 0; y < imIn->ysize / yscale; y++) {
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                    x = imIn->xsize / xscale;

                    for (yy = y*yscale; yy < y*yscale + yscale; yy++) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        for (xx = x * xscale; xx < imIn->xsize; xx++) {
                            ss0 += line[xx*4 + 0];
                            ss1 += line[xx*4 + 1];
                            ss2 += line[xx*4 + 2];
                            ss3 += line[xx*4 + 3];
                        }
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24, (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24, (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}


Imaging
ImagingReduce(Imaging imIn, int xscale, int yscale)
{
    Imaging imOut = NULL;

    imOut = ImagingNewDirty(imIn->mode,
                            (imIn->xsize + xscale - 1) / xscale,
                            (imIn->ysize + yscale - 1) / yscale);
    if ( ! imOut) {
        return NULL;
    }

    if (xscale == 1) {
        ImagingReduce1xN(imOut, imIn, yscale);
    } else if (xscale == 2) {
        if (yscale == 2)
            ImagingReduce2x2(imOut, imIn);
        else
            ImagingReduce2xN(imOut, imIn, yscale);
    } else if (xscale == 3) {
        if (yscale == 3)
            ImagingReduce3x3(imOut, imIn);
        else
            ImagingReduce3xN(imOut, imIn, yscale);
    } else if (xscale == 4) {
        if (yscale == 4)
            ImagingReduce4x4(imOut, imIn);
        else
            ImagingReduce4xN(imOut, imIn, yscale);
    } else if (xscale == 5) {
        if (yscale == 5)
            ImagingReduce5x5(imOut, imIn);
        else
            ImagingReduce5xN(imOut, imIn, yscale);
    } else if (xscale == 6) {
        if (yscale == 6)
            ImagingReduce6x6(imOut, imIn);
        else
            ImagingReduce6xN(imOut, imIn, yscale);
    } else if (xscale == 7) {
        ImagingReduce7xN(imOut, imIn, yscale);
    } else if (xscale == 8) {
        ImagingReduce8xN(imOut, imIn, yscale);
    }

    ImagingReduceCorners(imOut, imIn, xscale, yscale);

    return imOut;
}
