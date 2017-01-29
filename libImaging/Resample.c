#include "Imaging.h"

#include <math.h>


#define ROUND_UP(f) ((int) ((f) >= 0.0 ? (f) + 0.5F : (f) - 0.5F))

struct filter {
    double (*filter)(double x);
    double support;
};

static inline double box_filter(double x)
{
    if (x >= -0.5 && x < 0.5)
        return 1.0;
    return 0.0;
}

static inline double bilinear_filter(double x)
{
    if (x < 0.0)
        x = -x;
    if (x < 1.0)
        return 1.0-x;
    return 0.0;
}

static inline double hamming_filter(double x)
{
    if (x < 0.0)
        x = -x;
    if (x == 0.0)
        return 1.0;
    x = x * M_PI;
    return sin(x) / x * (0.54f + 0.46f * cos(x));
}

static inline double bicubic_filter(double x)
{
    /* https://en.wikipedia.org/wiki/Bicubic_interpolation#Bicubic_convolution_algorithm */
#define a -0.5
    if (x < 0.0)
        x = -x;
    if (x < 1.0)
        return ((a + 2.0) * x - (a + 3.0)) * x*x + 1;
    if (x < 2.0)
        return (((x - 5) * x + 8) * x - 4) * a;
    return 0.0;
#undef a
}

static inline double sinc_filter(double x)
{
    if (x == 0.0)
        return 1.0;
    x = x * M_PI;
    return sin(x) / x;
}

static inline double lanczos_filter(double x)
{
    /* truncated sinc */
    if (-3.0 <= x && x < 3.0)
        return sinc_filter(x) * sinc_filter(x/3);
    return 0.0;
}

static struct filter BOX = { box_filter, 0.5 };
static struct filter BILINEAR = { bilinear_filter, 1.0 };
static struct filter HAMMING = { hamming_filter, 1.0 };
static struct filter BICUBIC = { bicubic_filter, 2.0 };
static struct filter LANCZOS = { lanczos_filter, 3.0 };


/* 8 bits for result. Filter can have negative areas.
   In one cases the sum of the coefficients will be negative,
   in the other it will be more than 1.0. That is why we need
   two extra bits for overflow and int type. */
#define PRECISION_BITS (32 - 8 - 2)


UINT8 _lookups[512] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
    64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
    96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127,
    128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
    144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
    160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
    176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
    192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
    208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
    224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
    240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255
};

UINT8 *lookups = &_lookups[128];


static inline UINT8 clip8(int in)
{
    return lookups[in >> PRECISION_BITS];
}


int
precompute_coeffs(int inSize, int outSize, struct filter *filterp,
                  int **xboundsp, double **kkp) {
    double support, scale, filterscale;
    double center, ww, ss;
    int xx, x, kmax, xmin, xmax;
    int *xbounds;
    double *kk, *k;

    /* prepare for horizontal stretch */
    filterscale = scale = (double) inSize / outSize;
    if (filterscale < 1.0) {
        filterscale = 1.0;
    }

    /* determine support size (length of resampling filter) */
    support = filterp->support * filterscale;

    /* maximum number of coeffs */
    kmax = (int) ceil(support) * 2 + 1;

    // check for overflow
    if (outSize > INT_MAX / (kmax * sizeof(double)))
        return 0;

    /* coefficient buffer */
    /* malloc check ok, overflow checked above */
    kk = malloc(outSize * kmax * sizeof(double));
    if ( ! kk)
        return 0;

    /* malloc check ok, kmax*sizeof(double) > 2*sizeof(int) */
    xbounds = malloc(outSize * 2 * sizeof(int));
    if ( ! xbounds) {
        free(kk);
        return 0;
    }

    for (xx = 0; xx < outSize; xx++) {
        center = (xx + 0.5) * scale;
        ww = 0.0;
        ss = 1.0 / filterscale;
        xmin = (int) floor(center - support);
        if (xmin < 0)
            xmin = 0;
        xmax = (int) ceil(center + support);
        if (xmax > inSize)
            xmax = inSize;
        xmax -= xmin;
        k = &kk[xx * kmax];
        for (x = 0; x < xmax; x++) {
            double w = filterp->filter((x + xmin - center + 0.5) * ss);
            k[x] = w;
            ww += w;
            
            // We can skip extreme coefficients if they are zeroes.
            if (w == 0) {
                // Skip from the start.
                if (x == 0) {
                    // At next loop `x` will be 0.
                    x -= 1;
                    // But `w` will not be 0, because it based on `xmin`.
                    xmin += 1;
                    xmax -= 1;
                } else if (x == xmax - 1) {
                    // Truncate the last coefficient for current `xx`.
                    xmax -= 1;
                }
            }
        }
        for (x = 0; x < xmax; x++) {
            if (ww != 0.0)
                k[x] /= ww;
        }
        // Remaining values should stay empty if they are used despite of xmax.
        for (; x < kmax; x++) {
            k[x] = 0;
        }
        xbounds[xx * 2 + 0] = xmin;
        xbounds[xx * 2 + 1] = xmax;
    }
    *xboundsp = xbounds;
    *kkp = kk;
    return kmax;
}


int
normalize_coeffs_8bpc(int outSize, int kmax, double *prekk, INT32 **kkp)
{
    int x;
    INT32 *kk;

    /* malloc check ok, overflow checked in precompute_coeffs */
    kk = malloc(outSize * kmax * sizeof(INT32));
    if ( ! kk) {
        return 0;
    }

    for (x = 0; x < outSize * kmax; x++) {
        if (prekk[x] < 0) {
            kk[x] = (int) (-0.5 + prekk[x] * (1 << PRECISION_BITS));
        } else {
            kk[x] = (int) (0.5 + prekk[x] * (1 << PRECISION_BITS));
        }
    }

    *kkp = kk;
    return kmax;
}



Imaging
ImagingResampleHorizontal_8bpc(Imaging imIn, int xsize, struct filter *filterp)
{
    ImagingSectionCookie cookie;
    Imaging imOut;
    int ss0, ss1, ss2, ss3;
    int xx, yy, x, kmax, xmin, xmax;
    int *xbounds;
    INT32 *k, *kk;
    double *prekk;

    kmax = precompute_coeffs(imIn->xsize, xsize, filterp, &xbounds, &prekk);
    if ( ! kmax) {
        return (Imaging) ImagingError_MemoryError();
    }

    kmax = normalize_coeffs_8bpc(xsize, kmax, prekk, &kk);
    free(prekk);
    if ( ! kmax) {
        free(xbounds);
        return (Imaging) ImagingError_MemoryError();
    }

    imOut = ImagingNew(imIn->mode, xsize, imIn->ysize);
    if ( ! imOut) {
        free(kk);
        free(xbounds);
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {
        for (yy = 0; yy < imOut->ysize; yy++) {
            for (xx = 0; xx < xsize; xx++) {
                xmin = xbounds[xx * 2 + 0];
                xmax = xbounds[xx * 2 + 1];
                k = &kk[xx * kmax];
                ss0 = 1 << (PRECISION_BITS -1);
                for (x = 0; x < xmax; x++)
                    ss0 += ((UINT8) imIn->image8[yy][x + xmin]) * k[x];
                imOut->image8[yy][xx] = clip8(ss0);
            }
        }
    } else if (imIn->type == IMAGING_TYPE_UINT8) {
        if (imIn->bands == 2) {
            for (yy = 0; yy < imOut->ysize; yy++) {
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss0 = ss3 = 1 << (PRECISION_BITS -1);
                    for (x = 0; x < xmax; x++) {
                        ss0 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 0]) * k[x];
                        ss3 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 3]) * k[x];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 3] = clip8(ss3);
                }
            }
        } else if (imIn->bands == 3) {
            for (yy = 0; yy < imOut->ysize; yy++) {
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss0 = ss1 = ss2 = 1 << (PRECISION_BITS -1);
                    for (x = 0; x < xmax; x++) {
                        ss0 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 0]) * k[x];
                        ss1 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 1]) * k[x];
                        ss2 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 2]) * k[x];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 1] = clip8(ss1);
                    imOut->image[yy][xx*4 + 2] = clip8(ss2);
                }
            }
        } else {
            for (yy = 0; yy < imOut->ysize; yy++) {
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss0 = ss1 = ss2 = ss3 = 1 << (PRECISION_BITS -1);
                    for (x = 0; x < xmax; x++) {
                        ss0 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 0]) * k[x];
                        ss1 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 1]) * k[x];
                        ss2 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 2]) * k[x];
                        ss3 += ((UINT8) imIn->image[yy][(x + xmin)*4 + 3]) * k[x];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 1] = clip8(ss1);
                    imOut->image[yy][xx*4 + 2] = clip8(ss2);
                    imOut->image[yy][xx*4 + 3] = clip8(ss3);
                }
            }
        }
    }

    ImagingSectionLeave(&cookie);
    free(kk);
    free(xbounds);
    return imOut;
}


Imaging
ImagingResampleVertical_8bpc(Imaging imIn, int ysize, struct filter *filterp)
{
    ImagingSectionCookie cookie;
    Imaging imOut;
    int ss0, ss1, ss2, ss3;
    int xx, yy, y, kmax, ymin, ymax;
    int *xbounds;
    INT32 *k, *kk;
    double *prekk;

    kmax = precompute_coeffs(imIn->ysize, ysize, filterp, &xbounds, &prekk);
    if ( ! kmax) {
        return (Imaging) ImagingError_MemoryError();
    }

    kmax = normalize_coeffs_8bpc(ysize, kmax, prekk, &kk);
    free(prekk);
    if ( ! kmax) {
        free(xbounds);
        return (Imaging) ImagingError_MemoryError();
    }

    imOut = ImagingNew(imIn->mode, imIn->xsize, ysize);
    if ( ! imOut) {
        free(kk);
        free(xbounds);
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {
        for (yy = 0; yy < ysize; yy++) {
            k = &kk[yy * kmax];
            ymin = xbounds[yy * 2 + 0];
            ymax = xbounds[yy * 2 + 1];
            for (xx = 0; xx < imOut->xsize; xx++) {
                ss0 = 1 << (PRECISION_BITS -1);
                for (y = 0; y < ymax; y++)
                    ss0 += ((UINT8) imIn->image8[y + ymin][xx]) * k[y];
                imOut->image8[yy][xx] = clip8(ss0);
            }
        }
    } else if (imIn->type == IMAGING_TYPE_UINT8) {
        if (imIn->bands == 2) {
            for (yy = 0; yy < ysize; yy++) {
                k = &kk[yy * kmax];
                ymin = xbounds[yy * 2 + 0];
                ymax = xbounds[yy * 2 + 1];
                for (xx = 0; xx < imOut->xsize; xx++) {
                    ss0 = ss3 = 1 << (PRECISION_BITS -1);
                    for (y = 0; y < ymax; y++) {
                        ss0 += ((UINT8) imIn->image[y + ymin][xx*4 + 0]) * k[y];
                        ss3 += ((UINT8) imIn->image[y + ymin][xx*4 + 3]) * k[y];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 3] = clip8(ss3);
                }
            }
        } else if (imIn->bands == 3) {
            for (yy = 0; yy < ysize; yy++) {
                k = &kk[yy * kmax];
                ymin = xbounds[yy * 2 + 0];
                ymax = xbounds[yy * 2 + 1];
                for (xx = 0; xx < imOut->xsize; xx++) {
                    ss0 = ss1 = ss2 = 1 << (PRECISION_BITS -1);
                    for (y = 0; y < ymax; y++) {
                        ss0 += ((UINT8) imIn->image[y + ymin][xx*4 + 0]) * k[y];
                        ss1 += ((UINT8) imIn->image[y + ymin][xx*4 + 1]) * k[y];
                        ss2 += ((UINT8) imIn->image[y + ymin][xx*4 + 2]) * k[y];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 1] = clip8(ss1);
                    imOut->image[yy][xx*4 + 2] = clip8(ss2);
                }
            }
        } else {
            for (yy = 0; yy < ysize; yy++) {
                k = &kk[yy * kmax];
                ymin = xbounds[yy * 2 + 0];
                ymax = xbounds[yy * 2 + 1];
                for (xx = 0; xx < imOut->xsize; xx++) {
                    ss0 = ss1 = ss2 = ss3 = 1 << (PRECISION_BITS -1);
                    for (y = 0; y < ymax; y++) {
                        ss0 += ((UINT8) imIn->image[y + ymin][xx*4 + 0]) * k[y];
                        ss1 += ((UINT8) imIn->image[y + ymin][xx*4 + 1]) * k[y];
                        ss2 += ((UINT8) imIn->image[y + ymin][xx*4 + 2]) * k[y];
                        ss3 += ((UINT8) imIn->image[y + ymin][xx*4 + 3]) * k[y];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 1] = clip8(ss1);
                    imOut->image[yy][xx*4 + 2] = clip8(ss2);
                    imOut->image[yy][xx*4 + 3] = clip8(ss3);
                }
            }
        }
    }

    ImagingSectionLeave(&cookie);
    free(kk);
    free(xbounds);
    return imOut;
}


Imaging
ImagingResampleHorizontal_32bpc(Imaging imIn, int xsize, struct filter *filterp)
{
    ImagingSectionCookie cookie;
    Imaging imOut;
    double ss;
    int xx, yy, x, kmax, xmin, xmax;
    int *xbounds;
    double *k, *kk;

    kmax = precompute_coeffs(imIn->xsize, xsize, filterp, &xbounds, &kk);
    if ( ! kmax) {
        return (Imaging) ImagingError_MemoryError();
    }

    imOut = ImagingNew(imIn->mode, xsize, imIn->ysize);
    if ( ! imOut) {
        free(kk);
        free(xbounds);
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    switch(imIn->type) {
        case IMAGING_TYPE_INT32:
            for (yy = 0; yy < imOut->ysize; yy++) {
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss = 0.0;
                    for (x = 0; x < xmax; x++)
                        ss += IMAGING_PIXEL_I(imIn, x + xmin, yy) * k[x];
                    IMAGING_PIXEL_I(imOut, xx, yy) = ROUND_UP(ss);
                }
            }
            break;

        case IMAGING_TYPE_FLOAT32:
            for (yy = 0; yy < imOut->ysize; yy++) {
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss = 0.0;
                    for (x = 0; x < xmax; x++)
                        ss += IMAGING_PIXEL_F(imIn, x + xmin, yy) * k[x];
                    IMAGING_PIXEL_F(imOut, xx, yy) = ss;
                }
            }
            break;
    }

    ImagingSectionLeave(&cookie);
    free(kk);
    free(xbounds);
    return imOut;
}


Imaging
ImagingResampleVertical_32bpc(Imaging imIn, int ysize, struct filter *filterp)
{
    ImagingSectionCookie cookie;
    Imaging imOut;
    double ss;
    int xx, yy, y, kmax, ymin, ymax;
    int *xbounds;
    double *k, *kk;

    kmax = precompute_coeffs(imIn->ysize, ysize, filterp, &xbounds, &kk);
    if ( ! kmax) {
        return (Imaging) ImagingError_MemoryError();
    }

    imOut = ImagingNew(imIn->mode, imIn->xsize, ysize);
    if ( ! imOut) {
        free(kk);
        free(xbounds);
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    switch(imIn->type) {
        case IMAGING_TYPE_INT32:
            for (yy = 0; yy < ysize; yy++) {
                ymin = xbounds[yy * 2 + 0];
                ymax = xbounds[yy * 2 + 1];
                k = &kk[yy * kmax];
                for (xx = 0; xx < imOut->xsize; xx++) {
                    ss = 0.0;
                    for (y = 0; y < ymax; y++)
                        ss += IMAGING_PIXEL_I(imIn, xx, y + ymin) * k[y];
                    IMAGING_PIXEL_I(imOut, xx, yy) = ROUND_UP(ss);
                }
            }
            break;

        case IMAGING_TYPE_FLOAT32:
            for (yy = 0; yy < ysize; yy++) {
                ymin = xbounds[yy * 2 + 0];
                ymax = xbounds[yy * 2 + 1];
                k = &kk[yy * kmax];
                for (xx = 0; xx < imOut->xsize; xx++) {
                    ss = 0.0;
                    for (y = 0; y < ymax; y++)
                        ss += IMAGING_PIXEL_F(imIn, xx, y + ymin) * k[y];
                    IMAGING_PIXEL_F(imOut, xx, yy) = ss;
                }
            }
            break;
    }

    ImagingSectionLeave(&cookie);
    free(kk);
    free(xbounds);
    return imOut;
}


Imaging
ImagingResample(Imaging imIn, int xsize, int ysize, int filter)
{
    Imaging imTemp = NULL;
    Imaging imOut = NULL;
    struct filter *filterp;
    Imaging (*ResampleHorizontal)(Imaging imIn, int xsize, struct filter *filterp);
    Imaging (*ResampleVertical)(Imaging imIn, int xsize, struct filter *filterp);

    if (strcmp(imIn->mode, "P") == 0 || strcmp(imIn->mode, "1") == 0)
        return (Imaging) ImagingError_ModeError();

    if (imIn->type == IMAGING_TYPE_SPECIAL) {
        return (Imaging) ImagingError_ModeError();
    } else if (imIn->image8) {
        ResampleHorizontal = ImagingResampleHorizontal_8bpc;
        ResampleVertical = ImagingResampleVertical_8bpc;
    } else {
        switch(imIn->type) {
            case IMAGING_TYPE_UINT8:
                ResampleHorizontal = ImagingResampleHorizontal_8bpc;
                ResampleVertical = ImagingResampleVertical_8bpc;
                break;
            case IMAGING_TYPE_INT32:
            case IMAGING_TYPE_FLOAT32:
                ResampleHorizontal = ImagingResampleHorizontal_32bpc;
                ResampleVertical = ImagingResampleVertical_32bpc;
                break;
            default:
                return (Imaging) ImagingError_ModeError();
        }
    }

    /* check filter */
    switch (filter) {
    case IMAGING_TRANSFORM_BOX:
        filterp = &BOX;
        break;
    case IMAGING_TRANSFORM_BILINEAR:
        filterp = &BILINEAR;
        break;
    case IMAGING_TRANSFORM_HAMMING:
        filterp = &HAMMING;
        break;
    case IMAGING_TRANSFORM_BICUBIC:
        filterp = &BICUBIC;
        break;
    case IMAGING_TRANSFORM_LANCZOS:
        filterp = &LANCZOS;
        break;
    default:
        return (Imaging) ImagingError_ValueError(
            "unsupported resampling filter"
            );
    }

    /* two-pass resize, first pass */
    if (imIn->xsize != xsize) {
        imTemp = ResampleHorizontal(imIn, xsize, filterp);
        if ( ! imTemp)
            return NULL;
        imOut = imIn = imTemp;
    }

    /* second pass */
    if (imIn->ysize != ysize) {
        /* imIn can be the original image or horizontally resampled one */
        imOut = ResampleVertical(imIn, ysize, filterp);
        /* it's safe to call ImagingDelete with empty value
           if there was no previous step. */
        ImagingDelete(imTemp);
        if ( ! imOut)
            return NULL;
    }

    /* none of the previous steps are performed, copying */
    if ( ! imOut) {
        imOut = ImagingCopy(imIn);
    }

    return imOut;
}
