#include "Imaging.h"

#include <math.h>

#define ROUND_UP(f) ((int)((f) >= 0.0 ? (f) + 0.5F : (f)-0.5F))

UINT32
division_UINT32(int divider, int result_bits) {
    UINT32 max_dividend = (1 << result_bits) * divider;
    float max_int = (1 << 30) * 4.0;
    return (UINT32)(max_int / max_dividend);
}

void
ImagingReduceNxN(Imaging imOut, Imaging imIn, int box[4], int xscale, int yscale) {
    /* The most general implementation for any xscale and yscale
     */
    int x, y, xx, yy;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy_from = box[1] + y * yscale;
            for (x = 0; x < box[2] / xscale; x++) {
                int xx_from = box[0] + x * xscale;
                UINT32 ss = amend;
                for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                    UINT8 *line0 = (UINT8 *)imIn->image8[yy];
                    UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
                    for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                        ss += line0[xx + 0] + line0[xx + 1] + line1[xx + 0] +
                              line1[xx + 1];
                    }
                    if (xscale & 0x01) {
                        ss += line0[xx + 0] + line1[xx + 0];
                    }
                }
                if (yscale & 0x01) {
                    UINT8 *line = (UINT8 *)imIn->image8[yy];
                    for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                        ss += line[xx + 0] + line[xx + 1];
                    }
                    if (xscale & 0x01) {
                        ss += line[xx + 0];
                    }
                }
                imOut->image8[y][x] = (ss * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy_from = box[1] + y * yscale;
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss3 = amend;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        UINT8 *line0 = (UINT8 *)imIn->image[yy];
                        UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss0 += line0[xx * 4 + 0] + line0[xx * 4 + 4] +
                                   line1[xx * 4 + 0] + line1[xx * 4 + 4];
                            ss3 += line0[xx * 4 + 3] + line0[xx * 4 + 7] +
                                   line1[xx * 4 + 3] + line1[xx * 4 + 7];
                        }
                        if (xscale & 0x01) {
                            ss0 += line0[xx * 4 + 0] + line1[xx * 4 + 0];
                            ss3 += line0[xx * 4 + 3] + line1[xx * 4 + 3];
                        }
                    }
                    if (yscale & 0x01) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss0 += line[xx * 4 + 0] + line[xx * 4 + 4];
                            ss3 += line[xx * 4 + 3] + line[xx * 4 + 7];
                        }
                        if (xscale & 0x01) {
                            ss0 += line[xx * 4 + 0];
                            ss3 += line[xx * 4 + 3];
                        }
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24, 0, 0, (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        UINT8 *line0 = (UINT8 *)imIn->image[yy];
                        UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss0 += line0[xx * 4 + 0] + line0[xx * 4 + 4] +
                                   line1[xx * 4 + 0] + line1[xx * 4 + 4];
                            ss1 += line0[xx * 4 + 1] + line0[xx * 4 + 5] +
                                   line1[xx * 4 + 1] + line1[xx * 4 + 5];
                            ss2 += line0[xx * 4 + 2] + line0[xx * 4 + 6] +
                                   line1[xx * 4 + 2] + line1[xx * 4 + 6];
                        }
                        if (xscale & 0x01) {
                            ss0 += line0[xx * 4 + 0] + line1[xx * 4 + 0];
                            ss1 += line0[xx * 4 + 1] + line1[xx * 4 + 1];
                            ss2 += line0[xx * 4 + 2] + line1[xx * 4 + 2];
                        }
                    }
                    if (yscale & 0x01) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss0 += line[xx * 4 + 0] + line[xx * 4 + 4];
                            ss1 += line[xx * 4 + 1] + line[xx * 4 + 5];
                            ss2 += line[xx * 4 + 2] + line[xx * 4 + 6];
                        }
                        if (xscale & 0x01) {
                            ss0 += line[xx * 4 + 0];
                            ss1 += line[xx * 4 + 1];
                            ss2 += line[xx * 4 + 2];
                        }
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24,
                        (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        UINT8 *line0 = (UINT8 *)imIn->image[yy];
                        UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss0 += line0[xx * 4 + 0] + line0[xx * 4 + 4] +
                                   line1[xx * 4 + 0] + line1[xx * 4 + 4];
                            ss1 += line0[xx * 4 + 1] + line0[xx * 4 + 5] +
                                   line1[xx * 4 + 1] + line1[xx * 4 + 5];
                            ss2 += line0[xx * 4 + 2] + line0[xx * 4 + 6] +
                                   line1[xx * 4 + 2] + line1[xx * 4 + 6];
                            ss3 += line0[xx * 4 + 3] + line0[xx * 4 + 7] +
                                   line1[xx * 4 + 3] + line1[xx * 4 + 7];
                        }
                        if (xscale & 0x01) {
                            ss0 += line0[xx * 4 + 0] + line1[xx * 4 + 0];
                            ss1 += line0[xx * 4 + 1] + line1[xx * 4 + 1];
                            ss2 += line0[xx * 4 + 2] + line1[xx * 4 + 2];
                            ss3 += line0[xx * 4 + 3] + line1[xx * 4 + 3];
                        }
                    }
                    if (yscale & 0x01) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss0 += line[xx * 4 + 0] + line[xx * 4 + 4];
                            ss1 += line[xx * 4 + 1] + line[xx * 4 + 5];
                            ss2 += line[xx * 4 + 2] + line[xx * 4 + 6];
                            ss3 += line[xx * 4 + 3] + line[xx * 4 + 7];
                        }
                        if (xscale & 0x01) {
                            ss0 += line[xx * 4 + 0];
                            ss1 += line[xx * 4 + 1];
                            ss2 += line[xx * 4 + 2];
                            ss3 += line[xx * 4 + 3];
                        }
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24,
                        (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24,
                        (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce1xN(Imaging imOut, Imaging imIn, int box[4], int yscale) {
    /* Optimized implementation for xscale = 1.
     */
    int x, y, yy;
    int xscale = 1;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy_from = box[1] + y * yscale;
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                UINT32 ss = amend;
                for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                    UINT8 *line0 = (UINT8 *)imIn->image8[yy];
                    UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
                    ss += line0[xx + 0] + line1[xx + 0];
                }
                if (yscale & 0x01) {
                    UINT8 *line = (UINT8 *)imIn->image8[yy];
                    ss += line[xx + 0];
                }
                imOut->image8[y][x] = (ss * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy_from = box[1] + y * yscale;
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss3 = amend;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        UINT8 *line0 = (UINT8 *)imIn->image[yy];
                        UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                        ss0 += line0[xx * 4 + 0] + line1[xx * 4 + 0];
                        ss3 += line0[xx * 4 + 3] + line1[xx * 4 + 3];
                    }
                    if (yscale & 0x01) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        ss0 += line[xx * 4 + 0];
                        ss3 += line[xx * 4 + 3];
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24, 0, 0, (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        UINT8 *line0 = (UINT8 *)imIn->image[yy];
                        UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                        ss0 += line0[xx * 4 + 0] + line1[xx * 4 + 0];
                        ss1 += line0[xx * 4 + 1] + line1[xx * 4 + 1];
                        ss2 += line0[xx * 4 + 2] + line1[xx * 4 + 2];
                    }
                    if (yscale & 0x01) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        ss0 += line[xx * 4 + 0];
                        ss1 += line[xx * 4 + 1];
                        ss2 += line[xx * 4 + 2];
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24,
                        (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        UINT8 *line0 = (UINT8 *)imIn->image[yy];
                        UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
                        ss0 += line0[xx * 4 + 0] + line1[xx * 4 + 0];
                        ss1 += line0[xx * 4 + 1] + line1[xx * 4 + 1];
                        ss2 += line0[xx * 4 + 2] + line1[xx * 4 + 2];
                        ss3 += line0[xx * 4 + 3] + line1[xx * 4 + 3];
                    }
                    if (yscale & 0x01) {
                        UINT8 *line = (UINT8 *)imIn->image[yy];
                        ss0 += line[xx * 4 + 0];
                        ss1 += line[xx * 4 + 1];
                        ss2 += line[xx * 4 + 2];
                        ss3 += line[xx * 4 + 3];
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24,
                        (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24,
                        (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduceNx1(Imaging imOut, Imaging imIn, int box[4], int xscale) {
    /* Optimized implementation for yscale = 1.
     */
    int x, y, xx;
    int yscale = 1;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line = (UINT8 *)imIn->image8[yy];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx_from = box[0] + x * xscale;
                UINT32 ss = amend;
                for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                    ss += line[xx + 0] + line[xx + 1];
                }
                if (xscale & 0x01) {
                    ss += line[xx + 0];
                }
                imOut->image8[y][x] = (ss * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line = (UINT8 *)imIn->image[yy];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss3 = amend;
                    for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                        ss0 += line[xx * 4 + 0] + line[xx * 4 + 4];
                        ss3 += line[xx * 4 + 3] + line[xx * 4 + 7];
                    }
                    if (xscale & 0x01) {
                        ss0 += line[xx * 4 + 0];
                        ss3 += line[xx * 4 + 3];
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24, 0, 0, (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend;
                    for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                        ss0 += line[xx * 4 + 0] + line[xx * 4 + 4];
                        ss1 += line[xx * 4 + 1] + line[xx * 4 + 5];
                        ss2 += line[xx * 4 + 2] + line[xx * 4 + 6];
                    }
                    if (xscale & 0x01) {
                        ss0 += line[xx * 4 + 0];
                        ss1 += line[xx * 4 + 1];
                        ss2 += line[xx * 4 + 2];
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24,
                        (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    UINT32 v;
                    UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                    for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                        ss0 += line[xx * 4 + 0] + line[xx * 4 + 4];
                        ss1 += line[xx * 4 + 1] + line[xx * 4 + 5];
                        ss2 += line[xx * 4 + 2] + line[xx * 4 + 6];
                        ss3 += line[xx * 4 + 3] + line[xx * 4 + 7];
                    }
                    if (xscale & 0x01) {
                        ss0 += line[xx * 4 + 0];
                        ss1 += line[xx * 4 + 1];
                        ss2 += line[xx * 4 + 2];
                        ss3 += line[xx * 4 + 3];
                    }
                    v = MAKE_UINT32(
                        (ss0 * multiplier) >> 24,
                        (ss1 * multiplier) >> 24,
                        (ss2 * multiplier) >> 24,
                        (ss3 * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce1x2(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 1 and yscale = 2.
     */
    int xscale = 1, yscale = 2;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line1[xx + 0];
                imOut->image8[y][x] = (ss0 + amend) >> 1;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line1[xx * 4 + 0];
                    ss3 = line0[xx * 4 + 3] + line1[xx * 4 + 3];
                    v = MAKE_UINT32((ss0 + amend) >> 1, 0, 0, (ss3 + amend) >> 1);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line1[xx * 4 + 0];
                    ss1 = line0[xx * 4 + 1] + line1[xx * 4 + 1];
                    ss2 = line0[xx * 4 + 2] + line1[xx * 4 + 2];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 1, (ss1 + amend) >> 1, (ss2 + amend) >> 1, 0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line1[xx * 4 + 0];
                    ss1 = line0[xx * 4 + 1] + line1[xx * 4 + 1];
                    ss2 = line0[xx * 4 + 2] + line1[xx * 4 + 2];
                    ss3 = line0[xx * 4 + 3] + line1[xx * 4 + 3];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 1,
                        (ss1 + amend) >> 1,
                        (ss2 + amend) >> 1,
                        (ss3 + amend) >> 1);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce2x1(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 2 and yscale = 1.
     */
    int xscale = 2, yscale = 1;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line0[xx + 1];
                imOut->image8[y][x] = (ss0 + amend) >> 1;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7];
                    v = MAKE_UINT32((ss0 + amend) >> 1, 0, 0, (ss3 + amend) >> 1);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 1, (ss1 + amend) >> 1, (ss2 + amend) >> 1, 0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 1,
                        (ss1 + amend) >> 1,
                        (ss2 + amend) >> 1,
                        (ss3 + amend) >> 1);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce2x2(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 2 and yscale = 2.
     */
    int xscale = 2, yscale = 2;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line0[xx + 1] + line1[xx + 0] + line1[xx + 1];
                imOut->image8[y][x] = (ss0 + amend) >> 2;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line1[xx * 4 + 0] +
                          line1[xx * 4 + 4];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line1[xx * 4 + 3] +
                          line1[xx * 4 + 7];
                    v = MAKE_UINT32((ss0 + amend) >> 2, 0, 0, (ss3 + amend) >> 2);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line1[xx * 4 + 0] +
                          line1[xx * 4 + 4];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line1[xx * 4 + 1] +
                          line1[xx * 4 + 5];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line1[xx * 4 + 2] +
                          line1[xx * 4 + 6];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 2, (ss1 + amend) >> 2, (ss2 + amend) >> 2, 0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line1[xx * 4 + 0] +
                          line1[xx * 4 + 4];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line1[xx * 4 + 1] +
                          line1[xx * 4 + 5];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line1[xx * 4 + 2] +
                          line1[xx * 4 + 6];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line1[xx * 4 + 3] +
                          line1[xx * 4 + 7];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 2,
                        (ss1 + amend) >> 2,
                        (ss2 + amend) >> 2,
                        (ss3 + amend) >> 2);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce1x3(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 1 and yscale = 3.
     */
    int xscale = 1, yscale = 3;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image8[yy + 2];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line1[xx + 0] + line2[xx + 0];
                imOut->image8[y][x] = ((ss0 + amend) * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image[yy + 2];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line1[xx * 4 + 0] + line2[xx * 4 + 0];
                    ss3 = line0[xx * 4 + 3] + line1[xx * 4 + 3] + line2[xx * 4 + 3];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        0,
                        0,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line1[xx * 4 + 0] + line2[xx * 4 + 0];
                    ss1 = line0[xx * 4 + 1] + line1[xx * 4 + 1] + line2[xx * 4 + 1];
                    ss2 = line0[xx * 4 + 2] + line1[xx * 4 + 2] + line2[xx * 4 + 2];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line1[xx * 4 + 0] + line2[xx * 4 + 0];
                    ss1 = line0[xx * 4 + 1] + line1[xx * 4 + 1] + line2[xx * 4 + 1];
                    ss2 = line0[xx * 4 + 2] + line1[xx * 4 + 2] + line2[xx * 4 + 2];
                    ss3 = line0[xx * 4 + 3] + line1[xx * 4 + 3] + line2[xx * 4 + 3];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce3x1(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 3 and yscale = 1.
     */
    int xscale = 3, yscale = 1;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line0[xx + 1] + line0[xx + 2];
                imOut->image8[y][x] = ((ss0 + amend) * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        0,
                        0,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce3x3(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 3 and yscale = 3.
     */
    int xscale = 3, yscale = 3;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image8[yy + 2];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line0[xx + 1] + line0[xx + 2] + line1[xx + 0] +
                      line1[xx + 1] + line1[xx + 2] + line2[xx + 0] + line2[xx + 1] +
                      line2[xx + 2];
                imOut->image8[y][x] = ((ss0 + amend) * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image[yy + 2];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line1[xx * 4 + 0] + line1[xx * 4 + 4] + line1[xx * 4 + 8] +
                          line2[xx * 4 + 0] + line2[xx * 4 + 4] + line2[xx * 4 + 8];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11] +
                          line1[xx * 4 + 3] + line1[xx * 4 + 7] + line1[xx * 4 + 11] +
                          line2[xx * 4 + 3] + line2[xx * 4 + 7] + line2[xx * 4 + 11];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        0,
                        0,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line1[xx * 4 + 0] + line1[xx * 4 + 4] + line1[xx * 4 + 8] +
                          line2[xx * 4 + 0] + line2[xx * 4 + 4] + line2[xx * 4 + 8];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9] +
                          line1[xx * 4 + 1] + line1[xx * 4 + 5] + line1[xx * 4 + 9] +
                          line2[xx * 4 + 1] + line2[xx * 4 + 5] + line2[xx * 4 + 9];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10] +
                          line1[xx * 4 + 2] + line1[xx * 4 + 6] + line1[xx * 4 + 10] +
                          line2[xx * 4 + 2] + line2[xx * 4 + 6] + line2[xx * 4 + 10];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line1[xx * 4 + 0] + line1[xx * 4 + 4] + line1[xx * 4 + 8] +
                          line2[xx * 4 + 0] + line2[xx * 4 + 4] + line2[xx * 4 + 8];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9] +
                          line1[xx * 4 + 1] + line1[xx * 4 + 5] + line1[xx * 4 + 9] +
                          line2[xx * 4 + 1] + line2[xx * 4 + 5] + line2[xx * 4 + 9];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10] +
                          line1[xx * 4 + 2] + line1[xx * 4 + 6] + line1[xx * 4 + 10] +
                          line2[xx * 4 + 2] + line2[xx * 4 + 6] + line2[xx * 4 + 10];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11] +
                          line1[xx * 4 + 3] + line1[xx * 4 + 7] + line1[xx * 4 + 11] +
                          line2[xx * 4 + 3] + line2[xx * 4 + 7] + line2[xx * 4 + 11];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce4x4(Imaging imOut, Imaging imIn, int box[4]) {
    /* Optimized implementation for xscale = 4 and yscale = 4.
     */
    int xscale = 4, yscale = 4;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image8[yy + 2];
            UINT8 *line3 = (UINT8 *)imIn->image8[yy + 3];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line0[xx + 1] + line0[xx + 2] + line0[xx + 3] +
                      line1[xx + 0] + line1[xx + 1] + line1[xx + 2] + line1[xx + 3] +
                      line2[xx + 0] + line2[xx + 1] + line2[xx + 2] + line2[xx + 3] +
                      line3[xx + 0] + line3[xx + 1] + line3[xx + 2] + line3[xx + 3];
                imOut->image8[y][x] = (ss0 + amend) >> 4;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image[yy + 2];
            UINT8 *line3 = (UINT8 *)imIn->image[yy + 3];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line0[xx * 4 + 12] + line1[xx * 4 + 0] + line1[xx * 4 + 4] +
                          line1[xx * 4 + 8] + line1[xx * 4 + 12] + line2[xx * 4 + 0] +
                          line2[xx * 4 + 4] + line2[xx * 4 + 8] + line2[xx * 4 + 12] +
                          line3[xx * 4 + 0] + line3[xx * 4 + 4] + line3[xx * 4 + 8] +
                          line3[xx * 4 + 12];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11] +
                          line0[xx * 4 + 15] + line1[xx * 4 + 3] + line1[xx * 4 + 7] +
                          line1[xx * 4 + 11] + line1[xx * 4 + 15] + line2[xx * 4 + 3] +
                          line2[xx * 4 + 7] + line2[xx * 4 + 11] + line2[xx * 4 + 15] +
                          line3[xx * 4 + 3] + line3[xx * 4 + 7] + line3[xx * 4 + 11] +
                          line3[xx * 4 + 15];
                    v = MAKE_UINT32((ss0 + amend) >> 4, 0, 0, (ss3 + amend) >> 4);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line0[xx * 4 + 12] + line1[xx * 4 + 0] + line1[xx * 4 + 4] +
                          line1[xx * 4 + 8] + line1[xx * 4 + 12] + line2[xx * 4 + 0] +
                          line2[xx * 4 + 4] + line2[xx * 4 + 8] + line2[xx * 4 + 12] +
                          line3[xx * 4 + 0] + line3[xx * 4 + 4] + line3[xx * 4 + 8] +
                          line3[xx * 4 + 12];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9] +
                          line0[xx * 4 + 13] + line1[xx * 4 + 1] + line1[xx * 4 + 5] +
                          line1[xx * 4 + 9] + line1[xx * 4 + 13] + line2[xx * 4 + 1] +
                          line2[xx * 4 + 5] + line2[xx * 4 + 9] + line2[xx * 4 + 13] +
                          line3[xx * 4 + 1] + line3[xx * 4 + 5] + line3[xx * 4 + 9] +
                          line3[xx * 4 + 13];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10] +
                          line0[xx * 4 + 14] + line1[xx * 4 + 2] + line1[xx * 4 + 6] +
                          line1[xx * 4 + 10] + line1[xx * 4 + 14] + line2[xx * 4 + 2] +
                          line2[xx * 4 + 6] + line2[xx * 4 + 10] + line2[xx * 4 + 14] +
                          line3[xx * 4 + 2] + line3[xx * 4 + 6] + line3[xx * 4 + 10] +
                          line3[xx * 4 + 14];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 4, (ss1 + amend) >> 4, (ss2 + amend) >> 4, 0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line0[xx * 4 + 12] + line1[xx * 4 + 0] + line1[xx * 4 + 4] +
                          line1[xx * 4 + 8] + line1[xx * 4 + 12] + line2[xx * 4 + 0] +
                          line2[xx * 4 + 4] + line2[xx * 4 + 8] + line2[xx * 4 + 12] +
                          line3[xx * 4 + 0] + line3[xx * 4 + 4] + line3[xx * 4 + 8] +
                          line3[xx * 4 + 12];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9] +
                          line0[xx * 4 + 13] + line1[xx * 4 + 1] + line1[xx * 4 + 5] +
                          line1[xx * 4 + 9] + line1[xx * 4 + 13] + line2[xx * 4 + 1] +
                          line2[xx * 4 + 5] + line2[xx * 4 + 9] + line2[xx * 4 + 13] +
                          line3[xx * 4 + 1] + line3[xx * 4 + 5] + line3[xx * 4 + 9] +
                          line3[xx * 4 + 13];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10] +
                          line0[xx * 4 + 14] + line1[xx * 4 + 2] + line1[xx * 4 + 6] +
                          line1[xx * 4 + 10] + line1[xx * 4 + 14] + line2[xx * 4 + 2] +
                          line2[xx * 4 + 6] + line2[xx * 4 + 10] + line2[xx * 4 + 14] +
                          line3[xx * 4 + 2] + line3[xx * 4 + 6] + line3[xx * 4 + 10] +
                          line3[xx * 4 + 14];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11] +
                          line0[xx * 4 + 15] + line1[xx * 4 + 3] + line1[xx * 4 + 7] +
                          line1[xx * 4 + 11] + line1[xx * 4 + 15] + line2[xx * 4 + 3] +
                          line2[xx * 4 + 7] + line2[xx * 4 + 11] + line2[xx * 4 + 15] +
                          line3[xx * 4 + 3] + line3[xx * 4 + 7] + line3[xx * 4 + 11] +
                          line3[xx * 4 + 15];
                    v = MAKE_UINT32(
                        (ss0 + amend) >> 4,
                        (ss1 + amend) >> 4,
                        (ss2 + amend) >> 4,
                        (ss3 + amend) >> 4);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduce5x5(Imaging imOut, Imaging imIn, int box[4]) {
    /* Fast special case for xscale = 5 and yscale = 5.
     */
    int xscale = 5, yscale = 5;
    int x, y;
    UINT32 ss0, ss1, ss2, ss3;
    UINT32 multiplier = division_UINT32(yscale * xscale, 8);
    UINT32 amend = yscale * xscale / 2;

    if (imIn->image8) {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image8[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image8[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image8[yy + 2];
            UINT8 *line3 = (UINT8 *)imIn->image8[yy + 3];
            UINT8 *line4 = (UINT8 *)imIn->image8[yy + 4];
            for (x = 0; x < box[2] / xscale; x++) {
                int xx = box[0] + x * xscale;
                ss0 = line0[xx + 0] + line0[xx + 1] + line0[xx + 2] + line0[xx + 3] +
                      line0[xx + 4] + line1[xx + 0] + line1[xx + 1] + line1[xx + 2] +
                      line1[xx + 3] + line1[xx + 4] + line2[xx + 0] + line2[xx + 1] +
                      line2[xx + 2] + line2[xx + 3] + line2[xx + 4] + line3[xx + 0] +
                      line3[xx + 1] + line3[xx + 2] + line3[xx + 3] + line3[xx + 4] +
                      line4[xx + 0] + line4[xx + 1] + line4[xx + 2] + line4[xx + 3] +
                      line4[xx + 4];
                imOut->image8[y][x] = ((ss0 + amend) * multiplier) >> 24;
            }
        }
    } else {
        for (y = 0; y < box[3] / yscale; y++) {
            int yy = box[1] + y * yscale;
            UINT8 *line0 = (UINT8 *)imIn->image[yy + 0];
            UINT8 *line1 = (UINT8 *)imIn->image[yy + 1];
            UINT8 *line2 = (UINT8 *)imIn->image[yy + 2];
            UINT8 *line3 = (UINT8 *)imIn->image[yy + 3];
            UINT8 *line4 = (UINT8 *)imIn->image[yy + 4];
            if (imIn->bands == 2) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line0[xx * 4 + 12] + line0[xx * 4 + 16] + line1[xx * 4 + 0] +
                          line1[xx * 4 + 4] + line1[xx * 4 + 8] + line1[xx * 4 + 12] +
                          line1[xx * 4 + 16] + line2[xx * 4 + 0] + line2[xx * 4 + 4] +
                          line2[xx * 4 + 8] + line2[xx * 4 + 12] + line2[xx * 4 + 16] +
                          line3[xx * 4 + 0] + line3[xx * 4 + 4] + line3[xx * 4 + 8] +
                          line3[xx * 4 + 12] + line3[xx * 4 + 16] + line4[xx * 4 + 0] +
                          line4[xx * 4 + 4] + line4[xx * 4 + 8] + line4[xx * 4 + 12] +
                          line4[xx * 4 + 16];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11] +
                          line0[xx * 4 + 15] + line0[xx * 4 + 19] + line1[xx * 4 + 3] +
                          line1[xx * 4 + 7] + line1[xx * 4 + 11] + line1[xx * 4 + 15] +
                          line1[xx * 4 + 19] + line2[xx * 4 + 3] + line2[xx * 4 + 7] +
                          line2[xx * 4 + 11] + line2[xx * 4 + 15] + line2[xx * 4 + 19] +
                          line3[xx * 4 + 3] + line3[xx * 4 + 7] + line3[xx * 4 + 11] +
                          line3[xx * 4 + 15] + line3[xx * 4 + 19] + line4[xx * 4 + 3] +
                          line4[xx * 4 + 7] + line4[xx * 4 + 11] + line4[xx * 4 + 15] +
                          line4[xx * 4 + 19];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        0,
                        0,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else if (imIn->bands == 3) {
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line0[xx * 4 + 12] + line0[xx * 4 + 16] + line1[xx * 4 + 0] +
                          line1[xx * 4 + 4] + line1[xx * 4 + 8] + line1[xx * 4 + 12] +
                          line1[xx * 4 + 16] + line2[xx * 4 + 0] + line2[xx * 4 + 4] +
                          line2[xx * 4 + 8] + line2[xx * 4 + 12] + line2[xx * 4 + 16] +
                          line3[xx * 4 + 0] + line3[xx * 4 + 4] + line3[xx * 4 + 8] +
                          line3[xx * 4 + 12] + line3[xx * 4 + 16] + line4[xx * 4 + 0] +
                          line4[xx * 4 + 4] + line4[xx * 4 + 8] + line4[xx * 4 + 12] +
                          line4[xx * 4 + 16];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9] +
                          line0[xx * 4 + 13] + line0[xx * 4 + 17] + line1[xx * 4 + 1] +
                          line1[xx * 4 + 5] + line1[xx * 4 + 9] + line1[xx * 4 + 13] +
                          line1[xx * 4 + 17] + line2[xx * 4 + 1] + line2[xx * 4 + 5] +
                          line2[xx * 4 + 9] + line2[xx * 4 + 13] + line2[xx * 4 + 17] +
                          line3[xx * 4 + 1] + line3[xx * 4 + 5] + line3[xx * 4 + 9] +
                          line3[xx * 4 + 13] + line3[xx * 4 + 17] + line4[xx * 4 + 1] +
                          line4[xx * 4 + 5] + line4[xx * 4 + 9] + line4[xx * 4 + 13] +
                          line4[xx * 4 + 17];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10] +
                          line0[xx * 4 + 14] + line0[xx * 4 + 18] + line1[xx * 4 + 2] +
                          line1[xx * 4 + 6] + line1[xx * 4 + 10] + line1[xx * 4 + 14] +
                          line1[xx * 4 + 18] + line2[xx * 4 + 2] + line2[xx * 4 + 6] +
                          line2[xx * 4 + 10] + line2[xx * 4 + 14] + line2[xx * 4 + 18] +
                          line3[xx * 4 + 2] + line3[xx * 4 + 6] + line3[xx * 4 + 10] +
                          line3[xx * 4 + 14] + line3[xx * 4 + 18] + line4[xx * 4 + 2] +
                          line4[xx * 4 + 6] + line4[xx * 4 + 10] + line4[xx * 4 + 14] +
                          line4[xx * 4 + 18];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        0);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            } else {  // bands == 4
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx = box[0] + x * xscale;
                    UINT32 v;
                    ss0 = line0[xx * 4 + 0] + line0[xx * 4 + 4] + line0[xx * 4 + 8] +
                          line0[xx * 4 + 12] + line0[xx * 4 + 16] + line1[xx * 4 + 0] +
                          line1[xx * 4 + 4] + line1[xx * 4 + 8] + line1[xx * 4 + 12] +
                          line1[xx * 4 + 16] + line2[xx * 4 + 0] + line2[xx * 4 + 4] +
                          line2[xx * 4 + 8] + line2[xx * 4 + 12] + line2[xx * 4 + 16] +
                          line3[xx * 4 + 0] + line3[xx * 4 + 4] + line3[xx * 4 + 8] +
                          line3[xx * 4 + 12] + line3[xx * 4 + 16] + line4[xx * 4 + 0] +
                          line4[xx * 4 + 4] + line4[xx * 4 + 8] + line4[xx * 4 + 12] +
                          line4[xx * 4 + 16];
                    ss1 = line0[xx * 4 + 1] + line0[xx * 4 + 5] + line0[xx * 4 + 9] +
                          line0[xx * 4 + 13] + line0[xx * 4 + 17] + line1[xx * 4 + 1] +
                          line1[xx * 4 + 5] + line1[xx * 4 + 9] + line1[xx * 4 + 13] +
                          line1[xx * 4 + 17] + line2[xx * 4 + 1] + line2[xx * 4 + 5] +
                          line2[xx * 4 + 9] + line2[xx * 4 + 13] + line2[xx * 4 + 17] +
                          line3[xx * 4 + 1] + line3[xx * 4 + 5] + line3[xx * 4 + 9] +
                          line3[xx * 4 + 13] + line3[xx * 4 + 17] + line4[xx * 4 + 1] +
                          line4[xx * 4 + 5] + line4[xx * 4 + 9] + line4[xx * 4 + 13] +
                          line4[xx * 4 + 17];
                    ss2 = line0[xx * 4 + 2] + line0[xx * 4 + 6] + line0[xx * 4 + 10] +
                          line0[xx * 4 + 14] + line0[xx * 4 + 18] + line1[xx * 4 + 2] +
                          line1[xx * 4 + 6] + line1[xx * 4 + 10] + line1[xx * 4 + 14] +
                          line1[xx * 4 + 18] + line2[xx * 4 + 2] + line2[xx * 4 + 6] +
                          line2[xx * 4 + 10] + line2[xx * 4 + 14] + line2[xx * 4 + 18] +
                          line3[xx * 4 + 2] + line3[xx * 4 + 6] + line3[xx * 4 + 10] +
                          line3[xx * 4 + 14] + line3[xx * 4 + 18] + line4[xx * 4 + 2] +
                          line4[xx * 4 + 6] + line4[xx * 4 + 10] + line4[xx * 4 + 14] +
                          line4[xx * 4 + 18];
                    ss3 = line0[xx * 4 + 3] + line0[xx * 4 + 7] + line0[xx * 4 + 11] +
                          line0[xx * 4 + 15] + line0[xx * 4 + 19] + line1[xx * 4 + 3] +
                          line1[xx * 4 + 7] + line1[xx * 4 + 11] + line1[xx * 4 + 15] +
                          line1[xx * 4 + 19] + line2[xx * 4 + 3] + line2[xx * 4 + 7] +
                          line2[xx * 4 + 11] + line2[xx * 4 + 15] + line2[xx * 4 + 19] +
                          line3[xx * 4 + 3] + line3[xx * 4 + 7] + line3[xx * 4 + 11] +
                          line3[xx * 4 + 15] + line3[xx * 4 + 19] + line4[xx * 4 + 3] +
                          line4[xx * 4 + 7] + line4[xx * 4 + 11] + line4[xx * 4 + 15] +
                          line4[xx * 4 + 19];
                    v = MAKE_UINT32(
                        ((ss0 + amend) * multiplier) >> 24,
                        ((ss1 + amend) * multiplier) >> 24,
                        ((ss2 + amend) * multiplier) >> 24,
                        ((ss3 + amend) * multiplier) >> 24);
                    memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                }
            }
        }
    }
}

void
ImagingReduceCorners(Imaging imOut, Imaging imIn, int box[4], int xscale, int yscale) {
    /* Fill the last row and the last column for any xscale and yscale.
     */
    int x, y, xx, yy;

    if (imIn->image8) {
        if (box[2] % xscale) {
            int scale = (box[2] % xscale) * yscale;
            UINT32 multiplier = division_UINT32(scale, 8);
            UINT32 amend = scale / 2;
            for (y = 0; y < box[3] / yscale; y++) {
                int yy_from = box[1] + y * yscale;
                UINT32 ss = amend;
                x = box[2] / xscale;

                for (yy = yy_from; yy < yy_from + yscale; yy++) {
                    UINT8 *line = (UINT8 *)imIn->image8[yy];
                    for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                        ss += line[xx + 0];
                    }
                }
                imOut->image8[y][x] = (ss * multiplier) >> 24;
            }
        }
        if (box[3] % yscale) {
            int scale = xscale * (box[3] % yscale);
            UINT32 multiplier = division_UINT32(scale, 8);
            UINT32 amend = scale / 2;
            y = box[3] / yscale;
            for (x = 0; x < box[2] / xscale; x++) {
                int xx_from = box[0] + x * xscale;
                UINT32 ss = amend;
                for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                    UINT8 *line = (UINT8 *)imIn->image8[yy];
                    for (xx = xx_from; xx < xx_from + xscale; xx++) {
                        ss += line[xx + 0];
                    }
                }
                imOut->image8[y][x] = (ss * multiplier) >> 24;
            }
        }
        if (box[2] % xscale && box[3] % yscale) {
            int scale = (box[2] % xscale) * (box[3] % yscale);
            UINT32 multiplier = division_UINT32(scale, 8);
            UINT32 amend = scale / 2;
            UINT32 ss = amend;
            x = box[2] / xscale;
            y = box[3] / yscale;
            for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                UINT8 *line = (UINT8 *)imIn->image8[yy];
                for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                    ss += line[xx + 0];
                }
            }
            imOut->image8[y][x] = (ss * multiplier) >> 24;
        }
    } else {
        if (box[2] % xscale) {
            int scale = (box[2] % xscale) * yscale;
            UINT32 multiplier = division_UINT32(scale, 8);
            UINT32 amend = scale / 2;
            for (y = 0; y < box[3] / yscale; y++) {
                int yy_from = box[1] + y * yscale;
                UINT32 v;
                UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                x = box[2] / xscale;

                for (yy = yy_from; yy < yy_from + yscale; yy++) {
                    UINT8 *line = (UINT8 *)imIn->image[yy];
                    for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                        ss0 += line[xx * 4 + 0];
                        ss1 += line[xx * 4 + 1];
                        ss2 += line[xx * 4 + 2];
                        ss3 += line[xx * 4 + 3];
                    }
                }
                v = MAKE_UINT32(
                    (ss0 * multiplier) >> 24,
                    (ss1 * multiplier) >> 24,
                    (ss2 * multiplier) >> 24,
                    (ss3 * multiplier) >> 24);
                memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
            }
        }
        if (box[3] % yscale) {
            int scale = xscale * (box[3] % yscale);
            UINT32 multiplier = division_UINT32(scale, 8);
            UINT32 amend = scale / 2;
            y = box[3] / yscale;
            for (x = 0; x < box[2] / xscale; x++) {
                int xx_from = box[0] + x * xscale;
                UINT32 v;
                UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
                for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                    UINT8 *line = (UINT8 *)imIn->image[yy];
                    for (xx = xx_from; xx < xx_from + xscale; xx++) {
                        ss0 += line[xx * 4 + 0];
                        ss1 += line[xx * 4 + 1];
                        ss2 += line[xx * 4 + 2];
                        ss3 += line[xx * 4 + 3];
                    }
                }
                v = MAKE_UINT32(
                    (ss0 * multiplier) >> 24,
                    (ss1 * multiplier) >> 24,
                    (ss2 * multiplier) >> 24,
                    (ss3 * multiplier) >> 24);
                memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
            }
        }
        if (box[2] % xscale && box[3] % yscale) {
            int scale = (box[2] % xscale) * (box[3] % yscale);
            UINT32 multiplier = division_UINT32(scale, 8);
            UINT32 amend = scale / 2;
            UINT32 v;
            UINT32 ss0 = amend, ss1 = amend, ss2 = amend, ss3 = amend;
            x = box[2] / xscale;
            y = box[3] / yscale;
            for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                UINT8 *line = (UINT8 *)imIn->image[yy];
                for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                    ss0 += line[xx * 4 + 0];
                    ss1 += line[xx * 4 + 1];
                    ss2 += line[xx * 4 + 2];
                    ss3 += line[xx * 4 + 3];
                }
            }
            v = MAKE_UINT32(
                (ss0 * multiplier) >> 24,
                (ss1 * multiplier) >> 24,
                (ss2 * multiplier) >> 24,
                (ss3 * multiplier) >> 24);
            memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
        }
    }
}

void
ImagingReduceNxN_32bpc(
    Imaging imOut, Imaging imIn, int box[4], int xscale, int yscale) {
    /* The most general implementation for any xscale and yscale
     */
    int x, y, xx, yy;
    double multiplier = 1.0 / (yscale * xscale);

    switch (imIn->type) {
        case IMAGING_TYPE_INT32:
            for (y = 0; y < box[3] / yscale; y++) {
                int yy_from = box[1] + y * yscale;
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    double ss = 0;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        INT32 *line0 = (INT32 *)imIn->image32[yy];
                        INT32 *line1 = (INT32 *)imIn->image32[yy + 1];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss += line0[xx + 0] + line0[xx + 1] + line1[xx + 0] +
                                  line1[xx + 1];
                        }
                        if (xscale & 0x01) {
                            ss += line0[xx + 0] + line1[xx + 0];
                        }
                    }
                    if (yscale & 0x01) {
                        INT32 *line = (INT32 *)imIn->image32[yy];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss += line[xx + 0] + line[xx + 1];
                        }
                        if (xscale & 0x01) {
                            ss += line[xx + 0];
                        }
                    }
                    IMAGING_PIXEL_I(imOut, x, y) = ROUND_UP(ss * multiplier);
                }
            }
            break;

        case IMAGING_TYPE_FLOAT32:
            for (y = 0; y < box[3] / yscale; y++) {
                int yy_from = box[1] + y * yscale;
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    double ss = 0;
                    for (yy = yy_from; yy < yy_from + yscale - 1; yy += 2) {
                        FLOAT32 *line0 = (FLOAT32 *)imIn->image32[yy];
                        FLOAT32 *line1 = (FLOAT32 *)imIn->image32[yy + 1];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss += line0[xx + 0] + line0[xx + 1] + line1[xx + 0] +
                                  line1[xx + 1];
                        }
                        if (xscale & 0x01) {
                            ss += line0[xx + 0] + line1[xx + 0];
                        }
                    }
                    if (yscale & 0x01) {
                        FLOAT32 *line = (FLOAT32 *)imIn->image32[yy];
                        for (xx = xx_from; xx < xx_from + xscale - 1; xx += 2) {
                            ss += line[xx + 0] + line[xx + 1];
                        }
                        if (xscale & 0x01) {
                            ss += line[xx + 0];
                        }
                    }
                    IMAGING_PIXEL_F(imOut, x, y) = ss * multiplier;
                }
            }
            break;
    }
}

void
ImagingReduceCorners_32bpc(
    Imaging imOut, Imaging imIn, int box[4], int xscale, int yscale) {
    /* Fill the last row and the last column for any xscale and yscale.
     */
    int x, y, xx, yy;

    switch (imIn->type) {
        case IMAGING_TYPE_INT32:
            if (box[2] % xscale) {
                double multiplier = 1.0 / ((box[2] % xscale) * yscale);
                for (y = 0; y < box[3] / yscale; y++) {
                    int yy_from = box[1] + y * yscale;
                    double ss = 0;
                    x = box[2] / xscale;
                    for (yy = yy_from; yy < yy_from + yscale; yy++) {
                        INT32 *line = (INT32 *)imIn->image32[yy];
                        for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                            ss += line[xx + 0];
                        }
                    }
                    IMAGING_PIXEL_I(imOut, x, y) = ROUND_UP(ss * multiplier);
                }
            }
            if (box[3] % yscale) {
                double multiplier = 1.0 / (xscale * (box[3] % yscale));
                y = box[3] / yscale;
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    double ss = 0;
                    for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                        INT32 *line = (INT32 *)imIn->image32[yy];
                        for (xx = xx_from; xx < xx_from + xscale; xx++) {
                            ss += line[xx + 0];
                        }
                    }
                    IMAGING_PIXEL_I(imOut, x, y) = ROUND_UP(ss * multiplier);
                }
            }
            if (box[2] % xscale && box[3] % yscale) {
                double multiplier = 1.0 / ((box[2] % xscale) * (box[3] % yscale));
                double ss = 0;
                x = box[2] / xscale;
                y = box[3] / yscale;
                for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                    INT32 *line = (INT32 *)imIn->image32[yy];
                    for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                        ss += line[xx + 0];
                    }
                }
                IMAGING_PIXEL_I(imOut, x, y) = ROUND_UP(ss * multiplier);
            }
            break;

        case IMAGING_TYPE_FLOAT32:
            if (box[2] % xscale) {
                double multiplier = 1.0 / ((box[2] % xscale) * yscale);
                for (y = 0; y < box[3] / yscale; y++) {
                    int yy_from = box[1] + y * yscale;
                    double ss = 0;
                    x = box[2] / xscale;
                    for (yy = yy_from; yy < yy_from + yscale; yy++) {
                        FLOAT32 *line = (FLOAT32 *)imIn->image32[yy];
                        for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                            ss += line[xx + 0];
                        }
                    }
                    IMAGING_PIXEL_F(imOut, x, y) = ss * multiplier;
                }
            }
            if (box[3] % yscale) {
                double multiplier = 1.0 / (xscale * (box[3] % yscale));
                y = box[3] / yscale;
                for (x = 0; x < box[2] / xscale; x++) {
                    int xx_from = box[0] + x * xscale;
                    double ss = 0;
                    for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                        FLOAT32 *line = (FLOAT32 *)imIn->image32[yy];
                        for (xx = xx_from; xx < xx_from + xscale; xx++) {
                            ss += line[xx + 0];
                        }
                    }
                    IMAGING_PIXEL_F(imOut, x, y) = ss * multiplier;
                }
            }
            if (box[2] % xscale && box[3] % yscale) {
                double multiplier = 1.0 / ((box[2] % xscale) * (box[3] % yscale));
                double ss = 0;
                x = box[2] / xscale;
                y = box[3] / yscale;
                for (yy = box[1] + y * yscale; yy < box[1] + box[3]; yy++) {
                    FLOAT32 *line = (FLOAT32 *)imIn->image32[yy];
                    for (xx = box[0] + x * xscale; xx < box[0] + box[2]; xx++) {
                        ss += line[xx + 0];
                    }
                }
                IMAGING_PIXEL_F(imOut, x, y) = ss * multiplier;
            }
            break;
    }
}

Imaging
ImagingReduce(Imaging imIn, int xscale, int yscale, int box[4]) {
    ImagingSectionCookie cookie;
    Imaging imOut = NULL;

    if (strcmp(imIn->mode, "P") == 0 || strcmp(imIn->mode, "1") == 0) {
        return (Imaging)ImagingError_ModeError();
    }

    if (imIn->type == IMAGING_TYPE_SPECIAL) {
        return (Imaging)ImagingError_ModeError();
    }

    imOut = ImagingNewDirty(
        imIn->mode, (box[2] + xscale - 1) / xscale, (box[3] + yscale - 1) / yscale);
    if (!imOut) {
        return NULL;
    }

    ImagingSectionEnter(&cookie);

    switch (imIn->type) {
        case IMAGING_TYPE_UINT8:
            if (xscale == 1) {
                if (yscale == 2) {
                    ImagingReduce1x2(imOut, imIn, box);
                } else if (yscale == 3) {
                    ImagingReduce1x3(imOut, imIn, box);
                } else {
                    ImagingReduce1xN(imOut, imIn, box, yscale);
                }
            } else if (yscale == 1) {
                if (xscale == 2) {
                    ImagingReduce2x1(imOut, imIn, box);
                } else if (xscale == 3) {
                    ImagingReduce3x1(imOut, imIn, box);
                } else {
                    ImagingReduceNx1(imOut, imIn, box, xscale);
                }
            } else if (xscale == yscale && xscale <= 5) {
                if (xscale == 2) {
                    ImagingReduce2x2(imOut, imIn, box);
                } else if (xscale == 3) {
                    ImagingReduce3x3(imOut, imIn, box);
                } else if (xscale == 4) {
                    ImagingReduce4x4(imOut, imIn, box);
                } else {
                    ImagingReduce5x5(imOut, imIn, box);
                }
            } else {
                ImagingReduceNxN(imOut, imIn, box, xscale, yscale);
            }

            ImagingReduceCorners(imOut, imIn, box, xscale, yscale);
            break;

        case IMAGING_TYPE_INT32:
        case IMAGING_TYPE_FLOAT32:
            ImagingReduceNxN_32bpc(imOut, imIn, box, xscale, yscale);

            ImagingReduceCorners_32bpc(imOut, imIn, box, xscale, yscale);
            break;
    }

    ImagingSectionLeave(&cookie);

    return imOut;
}
