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
ImagingReduceNxN(Imaging imOut, Imaging imIn, int xscale, int yscale)
{
    /* The most general implementation for any xscale and yscale
    */
    int x, y, xx, yy, xi;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale - 1; yy += 2) {
                            UINT8 *line0 = (UINT8 *)imIn->image[yy];
                            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                            for (xi = 0; xi < xscale - 1; xi += 2) {
                                xx = x*xscale + xi;
                                ss0 += line0[xx*4 + 0] + line0[xx*4 + 4] +
                                       line1[xx*4 + 0] + line1[xx*4 + 4];
                                ss3 += line0[xx*4 + 3] + line0[xx*4 + 7] +
                                       line1[xx*4 + 3] + line1[xx*4 + 7];
                            }
                            for (; xi < xscale; xi++) {
                                xx = x*xscale + xi;
                                ss0 += line0[xx*4 + 0] + line1[xx*4 + 0];
                                ss3 += line0[xx*4 + 3] + line1[xx*4 + 3];
                            }
                        }
                        for (; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            for (xi = 0; xi < xscale - 1; xi += 2) {
                                xx = x*xscale + xi;
                                ss0 += line[xx*4 + 0] + line[xx*4 + 4];
                                ss3 += line[xx*4 + 3] + line[xx*4 + 7];
                            }
                            for (; xi < xscale; xi++) {
                                xx = x*xscale + xi;
                                ss0 += line[xx*4 + 0];
                                ss3 += line[xx*4 + 3];
                            }
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
                        for (yy = y*yscale; yy < y*yscale + yscale - 1; yy += 2) {
                            UINT8 *line0 = (UINT8 *)imIn->image[yy];
                            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                            for (xi = 0; xi < xscale - 1; xi += 2) {
                                xx = x*xscale + xi;
                                ss0 += line0[xx*4 + 0] + line0[xx*4 + 4] +
                                       line1[xx*4 + 0] + line1[xx*4 + 4];
                                ss1 += line0[xx*4 + 1] + line0[xx*4 + 5] +
                                       line1[xx*4 + 1] + line1[xx*4 + 5];
                                ss2 += line0[xx*4 + 2] + line0[xx*4 + 6] +
                                       line1[xx*4 + 2] + line1[xx*4 + 6];
                            }
                            for (; xi < xscale; xi++) {
                                xx = x*xscale + xi;
                                ss0 += line0[xx*4 + 0] + line1[xx*4 + 0];
                                ss1 += line0[xx*4 + 1] + line1[xx*4 + 1];
                                ss2 += line0[xx*4 + 2] + line1[xx*4 + 2];
                            }
                        }
                        for (; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            for (xi = 0; xi < xscale - 1; xi += 2) {
                                xx = x*xscale + xi;
                                ss0 += line[xx*4 + 0] + line[xx*4 + 4];
                                ss1 += line[xx*4 + 1] + line[xx*4 + 5];
                                ss2 += line[xx*4 + 2] + line[xx*4 + 6];
                            }
                            for (; xi < xscale; xi++) {
                                xx = x*xscale + xi;
                                ss0 += line[xx*4 + 0];
                                ss1 += line[xx*4 + 1];
                                ss2 += line[xx*4 + 2];
                            }
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
                        for (yy = y*yscale; yy < y*yscale + yscale - 1; yy += 2) {
                            UINT8 *line0 = (UINT8 *)imIn->image[yy];
                            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                            for (xi = 0; xi < xscale - 1; xi += 2) {
                                xx = x*xscale + xi;
                                ss0 += line0[xx*4 + 0] + line0[xx*4 + 4] +
                                       line1[xx*4 + 0] + line1[xx*4 + 4];
                                ss1 += line0[xx*4 + 1] + line0[xx*4 + 5] +
                                       line1[xx*4 + 1] + line1[xx*4 + 5];
                                ss2 += line0[xx*4 + 2] + line0[xx*4 + 6] +
                                       line1[xx*4 + 2] + line1[xx*4 + 6];
                                ss3 += line0[xx*4 + 3] + line0[xx*4 + 7] +
                                       line1[xx*4 + 3] + line1[xx*4 + 7];
                            }
                            for (; xi < xscale; xi++) {
                                xx = x*xscale + xi;
                                ss0 += line0[xx*4 + 0] + line1[xx*4 + 0];
                                ss1 += line0[xx*4 + 1] + line1[xx*4 + 1];
                                ss2 += line0[xx*4 + 2] + line1[xx*4 + 2];
                                ss3 += line0[xx*4 + 3] + line1[xx*4 + 3];
                            }
                        }
                        for (; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            for (xi = 0; xi < xscale - 1; xi += 2) {
                                xx = x*xscale + xi;
                                ss0 += line[xx*4 + 0] + line[xx*4 + 4];
                                ss1 += line[xx*4 + 1] + line[xx*4 + 5];
                                ss2 += line[xx*4 + 2] + line[xx*4 + 6];
                                ss3 += line[xx*4 + 3] + line[xx*4 + 7];
                            }
                            for (; xi < xscale; xi++) {
                                xx = x*xscale + xi;
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
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
}


void
ImagingReduce1xN(Imaging imOut, Imaging imIn, int yscale)
{
    /* Optimized implementation for xscale = 1.
    */
    int x, y, yy;
    int xscale = 1;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (yy = y*yscale; yy < y*yscale + yscale - 1; yy += 2) {
                            UINT8 *line0 = (UINT8 *)imIn->image[yy];
                            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                            ss0 += line0[x*4 + 0] + line1[x*4 + 0];
                            ss3 += line0[x*4 + 3] + line1[x*4 + 3];
                        }
                        for (; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*4 + 0];
                            ss3 += line[x*4 + 3];
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
                        for (yy = y*yscale; yy < y*yscale + yscale - 1; yy += 2) {
                            UINT8 *line0 = (UINT8 *)imIn->image[yy];
                            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                            ss0 += line0[x*4 + 0] + line1[x*4 + 0];
                            ss1 += line0[x*4 + 1] + line1[x*4 + 1];
                            ss2 += line0[x*4 + 2] + line1[x*4 + 2];
                        }
                        for (; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*4 + 0];
                            ss1 += line[x*4 + 1];
                            ss2 += line[x*4 + 2];
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
                        for (yy = y*yscale; yy < y*yscale + yscale - 1; yy += 2) {
                            UINT8 *line0 = (UINT8 *)imIn->image[yy];
                            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                            ss0 += line0[x*4 + 0] + line1[x*4 + 0];
                            ss1 += line0[x*4 + 1] + line1[x*4 + 1];
                            ss2 += line0[x*4 + 2] + line1[x*4 + 2];
                            ss3 += line0[x*4 + 3] + line1[x*4 + 3];
                        }
                        for (; yy < y*yscale + yscale; yy ++) {
                            UINT8 *line = (UINT8 *)imIn->image[yy];
                            ss0 += line[x*4 + 0];
                            ss1 += line[x*4 + 1];
                            ss2 += line[x*4 + 2];
                            ss3 += line[x*4 + 3];
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
}


void
ImagingReduceNx1(Imaging imOut, Imaging imIn, int xscale)
{
    /* Optimized implementation for yscale = 1.
    */
    int x, y, xx, xi;
    int yscale = 1;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / yscale; y++) {
                UINT8 *line = (UINT8 *)imIn->image[y];
                if (imIn->bands == 2) {
                    for (x = 0; x < imIn->xsize / xscale; x++) {
                        UINT32 v;
                        UINT32 ss0 = amend, ss3 = amend;
                        for (xi = 0; xi < xscale - 1; xi += 2) {
                            xx = x*xscale + xi;
                            ss0 += line[xx*4 + 0] + line[xx*4 + 4];
                            ss3 += line[xx*4 + 3] + line[xx*4 + 7];
                        }
                        for (; xi < xscale; xi++) {
                            xx = x*xscale + xi;
                            ss0 += line[xx*4 + 0];
                            ss3 += line[xx*4 + 3];
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
                        for (xi = 0; xi < xscale - 1; xi += 2) {
                            xx = x*xscale + xi;
                            ss0 += line[xx*4 + 0] + line[xx*4 + 4];
                            ss1 += line[xx*4 + 1] + line[xx*4 + 5];
                            ss2 += line[xx*4 + 2] + line[xx*4 + 6];
                        }
                        for (; xi < xscale; xi++) {
                            xx = x*xscale + xi;
                            ss0 += line[xx*4 + 0];
                            ss1 += line[xx*4 + 1];
                            ss2 += line[xx*4 + 2];
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
                        for (xi = 0; xi < xscale - 1; xi += 2) {
                            xx = x*xscale + xi;
                            ss0 += line[xx*4 + 0] + line[xx*4 + 4];
                            ss1 += line[xx*4 + 1] + line[xx*4 + 5];
                            ss2 += line[xx*4 + 2] + line[xx*4 + 6];
                            ss3 += line[xx*4 + 3] + line[xx*4 + 7];
                        }
                        for (; xi < xscale; xi++) {
                            xx = x*xscale + xi;
                            ss0 += line[xx*4 + 0];
                            ss1 += line[xx*4 + 1];
                            ss2 += line[xx*4 + 2];
                            ss3 += line[xx*4 + 3];
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
}


void
ImagingReduce2x2(Imaging imOut, Imaging imIn)
{
    /* Fast special case for xscale = 2 and yscale = 2.
    */
    int xscale = 2, yscale = 2;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

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
}

void
ImagingReduce3x3(Imaging imOut, Imaging imIn)
{
    /* Fast special case for xscale = 3 and yscale = 3.
    */
    int xscale = 3, yscale = 3;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

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
}

void
ImagingReduce4x4(Imaging imOut, Imaging imIn)
{
    /* Fast special case for xscale = 4 and yscale = 4.
    */
    int xscale = 4, yscale = 4;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

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
}


void
ImagingReduce5x5(Imaging imOut, Imaging imIn)
{
    /* Fast special case for xscale = 5 and yscale = 5.
    */
    int xscale = 5, yscale = 5;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

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
}


void
ImagingReduceCorners(Imaging imOut, Imaging imIn, int xscale, int yscale)
{
    int x, y, xx, yy;

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
}


Imaging
ImagingReduce(Imaging imIn, int xscale, int yscale)
{
    ImagingSectionCookie cookie;
    Imaging imOut = NULL;

    imOut = ImagingNewDirty(imIn->mode,
                            (imIn->xsize + xscale - 1) / xscale,
                            (imIn->ysize + yscale - 1) / yscale);
    if ( ! imOut) {
        return NULL;
    }

    ImagingSectionEnter(&cookie);

    if (xscale == yscale) {
        if (xscale == 2) {
            ImagingReduce2x2(imOut, imIn);
        } else if (xscale == 3) {
            ImagingReduce3x3(imOut, imIn);
        } else if (xscale == 4) {
            ImagingReduce4x4(imOut, imIn);
        } else if (xscale == 5) {
            ImagingReduce5x5(imOut, imIn);
        } else {
            ImagingReduceNxN(imOut, imIn, xscale, yscale);
        }
    } else {
        if (xscale == 1) {
            ImagingReduce1xN(imOut, imIn, yscale);
        } else if (yscale == 1) {
            ImagingReduceNx1(imOut, imIn, xscale);
        } else {
            ImagingReduceNxN(imOut, imIn, xscale, yscale);
        }
    }

    ImagingReduceCorners(imOut, imIn, xscale, yscale);

    ImagingSectionLeave(&cookie);

    return imOut;
}
