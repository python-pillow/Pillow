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
    int x, y;
    int ss0, ss1, ss2, ss3;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / 2; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*2 + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*2 + 1];
                if (imIn->bands == 2) {

                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / 2; x++) {
                        UINT32 v;
                        ss0 = line0[x*2*4 + 0] + line0[x*2*4 + 4] +
                              line1[x*2*4 + 0] + line1[x*2*4 + 4];
                        ss1 = line0[x*2*4 + 1] + line0[x*2*4 + 5] +
                              line1[x*2*4 + 1] + line1[x*2*4 + 5];
                        ss2 = line0[x*2*4 + 2] + line0[x*2*4 + 6] +
                              line1[x*2*4 + 2] + line1[x*2*4 + 6];
                        v = MAKE_UINT32((ss0 + 2) >> 2, (ss1 + 2) >> 2,
                                        (ss2 + 2) >> 2, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4

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
        ImagingReduce2xN(imOut, imIn, yscale);
    } else if (xscale == 3) {
        ImagingReduce3xN(imOut, imIn, yscale);
    } else if (xscale == 4) {
        ImagingReduce4xN(imOut, imIn, yscale);
    } else if (xscale == 5) {
        ImagingReduce5xN(imOut, imIn, yscale);
    } else if (xscale == 6) {
        ImagingReduce6xN(imOut, imIn, yscale);
    } else if (xscale == 7) {
        ImagingReduce7xN(imOut, imIn, yscale);
    } else if (xscale == 8) {
        ImagingReduce8xN(imOut, imIn, yscale);
    }

    ImagingReduceCorners(imOut, imIn, xscale, yscale);

    return imOut;
}
