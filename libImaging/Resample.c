#include "Imaging.h"

#include <math.h>


#define ROUND_UP(f) ((int) ((f) >= 0.0 ? (f) + 0.5F : (f) - 0.5F))


struct filter {
    double (*filter)(double x);
    double support;
};

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

static inline double bilinear_filter(double x)
{
    if (x < 0.0)
        x = -x;
    if (x < 1.0)
        return 1.0-x;
    return 0.0;
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

static struct filter LANCZOS = { lanczos_filter, 3.0 };
static struct filter BILINEAR = { bilinear_filter, 1.0 };
static struct filter BICUBIC = { bicubic_filter, 2.0 };



/* 8 bits for result. Filter can have negative areas.
   In one cases the sum of the coefficients will be negative,
   in the other it will be more than 1.0. That is why we need
   two extra bits for overflow and int type. */
#define PRECISION_BITS (32 - 8 - 2)


static inline UINT8 clip8(int in)
{
    if (in >= (1 << PRECISION_BITS << 8))
       return 255;
    if (in <= 0)
        return 0;
    return (UINT8) (in >> PRECISION_BITS);
}


int
ImagingPrecompute(int inSize, int outSize, struct filter *filterp,
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

    /* maximum number of coofs */
    kmax = (int) ceil(support) * 2 + 1;

    // check for overflow
    if (outSize > SIZE_MAX / (kmax * sizeof(double)))
        return 0;

    // sizeof(double) should be greater than 0 as well
    if (outSize > SIZE_MAX / (2 * sizeof(double)))
        return 0;

    /* coefficient buffer */
    kk = malloc(outSize * kmax * sizeof(double));
    if ( ! kk)
        return 0;

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
        k = &kk[xx * kmax];
        for (x = xmin; x < xmax; x++) {
            double w = filterp->filter((x - center + 0.5) * ss);
            k[x - xmin] = w;
            ww += w;
        }
        for (x = 0; x < xmax - xmin; x++) {
            if (ww != 0.0)
                k[x] /= ww;
        }
        xbounds[xx * 2 + 0] = xmin;
        xbounds[xx * 2 + 1] = xmax;
    }
    *xboundsp = xbounds;
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
    int *k, *kk;
    double *prekk;


    kmax = ImagingPrecompute(imIn->xsize, xsize, filterp, &xbounds, &prekk);
    if ( ! kmax) {
        return (Imaging) ImagingError_MemoryError();
    }
    
    kk = malloc(xsize * kmax * sizeof(int));
    if ( ! kk) {
        free(xbounds);
        free(prekk);
        return (Imaging) ImagingError_MemoryError();
    }

    for (xx = 0; xx < xsize; xx++) {
        xmin = xbounds[xx * 2 + 0];
        xmax = xbounds[xx * 2 + 1];
        k = &kk[xx * kmax];
        for (x = 0; x < xmax - xmin; x++) {
            k[x] = (int) floor(0.5 + prekk[xx * kmax + x] * (1 << PRECISION_BITS));
        }
    }

    free(prekk);

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
                for (x = xmin; x < xmax; x++)
                    ss0 += ((UINT8) imIn->image8[yy][x]) * k[x - xmin];
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
                    ss0 = ss1 = 1 << (PRECISION_BITS -1);
                    for (x = xmin; x < xmax; x++) {
                        ss0 += ((UINT8) imIn->image[yy][x*4 + 0]) * k[x - xmin];
                        ss1 += ((UINT8) imIn->image[yy][x*4 + 3]) * k[x - xmin];
                    }
                    imOut->image[yy][xx*4 + 0] = clip8(ss0);
                    imOut->image[yy][xx*4 + 3] = clip8(ss1);
                }
            }
        } else if (imIn->bands == 3) {
            for (yy = 0; yy < imOut->ysize; yy++) {
                for (xx = 0; xx < xsize; xx++) {
                    xmin = xbounds[xx * 2 + 0];
                    xmax = xbounds[xx * 2 + 1];
                    k = &kk[xx * kmax];
                    ss0 = ss1 = ss2 = 1 << (PRECISION_BITS -1);
                    for (x = xmin; x < xmax; x++) {
                        ss0 += ((UINT8) imIn->image[yy][x*4 + 0]) * k[x - xmin];
                        ss1 += ((UINT8) imIn->image[yy][x*4 + 1]) * k[x - xmin];
                        ss2 += ((UINT8) imIn->image[yy][x*4 + 2]) * k[x - xmin];
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
                    for (x = xmin; x < xmax; x++) {
                        ss0 += ((UINT8) imIn->image[yy][x*4 + 0]) * k[x - xmin];
                        ss1 += ((UINT8) imIn->image[yy][x*4 + 1]) * k[x - xmin];
                        ss2 += ((UINT8) imIn->image[yy][x*4 + 2]) * k[x - xmin];
                        ss3 += ((UINT8) imIn->image[yy][x*4 + 3]) * k[x - xmin];
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

    kmax = ImagingPrecompute(imIn->xsize, xsize, filterp, &xbounds, &kk);
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
                    for (x = xmin; x < xmax; x++)
                        ss += IMAGING_PIXEL_I(imIn, x, yy) * k[x - xmin];
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
                    for (x = xmin; x < xmax; x++)
                        ss += IMAGING_PIXEL_F(imIn, x, yy) * k[x - xmin];
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
    Imaging imTemp1, imTemp2, imTemp3;
    Imaging imOut;
    struct filter *filterp;
    Imaging (*ResampleHorizontal)(Imaging imIn, int xsize, struct filter *filterp);

    if (strcmp(imIn->mode, "P") == 0 || strcmp(imIn->mode, "1") == 0)
        return (Imaging) ImagingError_ModeError();

    if (imIn->type == IMAGING_TYPE_SPECIAL) {
        return (Imaging) ImagingError_ModeError();
    } else if (imIn->image8) {
        ResampleHorizontal = ImagingResampleHorizontal_8bpc;
    } else {
        switch(imIn->type) {
            case IMAGING_TYPE_UINT8:
                ResampleHorizontal = ImagingResampleHorizontal_8bpc;
                break;
            case IMAGING_TYPE_INT32:
            case IMAGING_TYPE_FLOAT32:
                ResampleHorizontal = ImagingResampleHorizontal_32bpc;
                break;
            default:
                return (Imaging) ImagingError_ModeError();
        }
    }

    /* check filter */
    switch (filter) {
    case IMAGING_TRANSFORM_LANCZOS:
        filterp = &LANCZOS;
        break;
    case IMAGING_TRANSFORM_BILINEAR:
        filterp = &BILINEAR;
        break;
    case IMAGING_TRANSFORM_BICUBIC:
        filterp = &BICUBIC;
        break;
    default:
        return (Imaging) ImagingError_ValueError(
            "unsupported resampling filter"
            );
    }

    /* two-pass resize, first pass */
    imTemp1 = ResampleHorizontal(imIn, xsize, filterp);
    if ( ! imTemp1)
        return NULL;

    /* transpose image once */
    imTemp2 = ImagingTransposeToNew(imTemp1);
    ImagingDelete(imTemp1);
    if ( ! imTemp2)
        return NULL;

    /* second pass */
    imTemp3 = ResampleHorizontal(imTemp2, ysize, filterp);
    ImagingDelete(imTemp2);
    if ( ! imTemp3)
        return NULL;

    /* transpose result */
    imOut = ImagingTransposeToNew(imTemp3);
    ImagingDelete(imTemp3);
    if ( ! imOut)
        return NULL;

    return imOut;
}
