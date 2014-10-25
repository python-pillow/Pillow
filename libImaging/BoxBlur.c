#include "Python.h"
#include "Imaging.h"


#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))


typedef UINT8 pixel[4];

void
LineBoxBlur32(pixel *line, UINT32 *lineOut, int lastx, int radius, int edgeA,
    int edgeB, UINT32 ww, UINT32 fw)
{
    int x;
    UINT32 acc[4];
    UINT32 bulk[4];

    #define MOVE_ACC(acc, substract, add) \
        acc[0] += line[add][0] - line[substract][0]; \
        acc[1] += line[add][1] - line[substract][1]; \
        acc[2] += line[add][2] - line[substract][2]; \
        acc[3] += line[add][3] - line[substract][3];

    #define ADD_FAR(bulk, acc, left, right) \
        bulk[0] = (acc[0] * ww) + (line[left][0] + line[right][0]) * fw; \
        bulk[1] = (acc[1] * ww) + (line[left][1] + line[right][1]) * fw; \
        bulk[2] = (acc[2] * ww) + (line[left][2] + line[right][2]) * fw; \
        bulk[3] = (acc[3] * ww) + (line[left][3] + line[right][3]) * fw;

    #define SAVE(acc) \
        (UINT8)((acc[0] + (1 << 23)) >> 24) << 0  | (UINT8)((acc[1] + (1 << 23)) >> 24) << 8 | \
        (UINT8)((acc[2] + (1 << 23)) >> 24) << 16 | (UINT8)((acc[3] + (1 << 23)) >> 24) << 24

    /* Compute acc for -1 pixel (outside of image):
       From "-radius-1" to "-1" get first pixel,
       then from "0" to "radius-1". */
    acc[0] = line[0][0] * (radius + 1);
    acc[1] = line[0][1] * (radius + 1);
    acc[2] = line[0][2] * (radius + 1);
    acc[3] = line[0][3] * (radius + 1);
    /* As radius can be bigger than xsize, iterate to edgeA -1. */
    for (x = 0; x < edgeA - 1; x++) {
        acc[0] += line[x][0];
        acc[1] += line[x][1];
        acc[2] += line[x][2];
        acc[3] += line[x][3];
    }
    /* Then multiply remainder to last x. */
    acc[0] += line[lastx][0] * (radius - edgeA + 1);
    acc[1] += line[lastx][1] * (radius - edgeA + 1);
    acc[2] += line[lastx][2] * (radius - edgeA + 1);
    acc[3] += line[lastx][3] * (radius - edgeA + 1);

    if (edgeA <= edgeB)
    {
        /* Substract pixel from left ("0").
           Add pixels from radius. */
        for (x = 0; x < edgeA; x++) {
            MOVE_ACC(acc, 0, x + radius);
            ADD_FAR(bulk, acc, 0, x + radius + 1);
            lineOut[x] = SAVE(bulk);
        }
        /* Substract previous pixel from "-radius".
           Add pixels from radius. */
        for (x = edgeA; x < edgeB; x++) {
            MOVE_ACC(acc, x - radius - 1, x + radius);
            ADD_FAR(bulk, acc, x - radius - 1, x + radius + 1);
            lineOut[x] = SAVE(bulk);
        }
        /* Substract previous pixel from "-radius".
           Add last pixel. */
        for (x = edgeB; x <= lastx; x++) {
            MOVE_ACC(acc, x - radius - 1, lastx);
            ADD_FAR(bulk, acc, x - radius - 1, lastx);
            lineOut[x] = SAVE(bulk);
        }
    }
    else
    {
        for (x = 0; x < edgeB; x++) {
            MOVE_ACC(acc, 0, x + radius);
            ADD_FAR(bulk, acc, 0, x + radius + 1);
            lineOut[x] = SAVE(bulk);
        }
        for (x = edgeB; x < edgeA; x++) {
            MOVE_ACC(acc, 0, lastx);
            ADD_FAR(bulk, acc, 0, lastx);
            lineOut[x] = SAVE(bulk);
        }
        for (x = edgeA; x <= lastx; x++) {
            MOVE_ACC(acc, x - radius - 1, lastx);
            ADD_FAR(bulk, acc, x - radius - 1, lastx);
            lineOut[x] = SAVE(bulk);
        }
    }

    #undef MOVE_ACC
    #undef ADD_FAR
    #undef SAVE
}


void
LineBoxBlur8(UINT8 *line, UINT8 *lineOut, int lastx, int radius, int edgeA,
    int edgeB, UINT32 ww, UINT32 fw)
{
    int x;
    UINT32 acc;
    UINT32 bulk;

    #define MOVE_ACC(acc, substract, add) \
        acc += line[add] - line[substract];

    #define ADD_FAR(bulk, acc, left, right) \
        bulk = (acc * ww) + (line[left] + line[right]) * fw;

    #define SAVE(acc) \
        (UINT8)((acc + (1 << 23)) >> 24)

    acc = line[0] * (radius + 1);
    for (x = 0; x < edgeA - 1; x++) {
        acc += line[x];
    }
    acc += line[lastx] * (radius - edgeA + 1);

    if (edgeA <= edgeB)
    {
        for (x = 0; x < edgeA; x++) {
            MOVE_ACC(acc, 0, x + radius);
            ADD_FAR(bulk, acc, 0, x + radius + 1);
            lineOut[x] = SAVE(bulk);
        }
        for (x = edgeA; x < edgeB; x++) {
            MOVE_ACC(acc, x - radius - 1, x + radius);
            ADD_FAR(bulk, acc, x - radius - 1, x + radius + 1);
            lineOut[x] = SAVE(bulk);
        }
        for (x = edgeB; x <= lastx; x++) {
            MOVE_ACC(acc, x - radius - 1, lastx);
            ADD_FAR(bulk, acc, x - radius - 1, lastx);
            lineOut[x] = SAVE(bulk);
        }
    }
    else
    {
        for (x = 0; x < edgeB; x++) {
            MOVE_ACC(acc, 0, x + radius);
            ADD_FAR(bulk, acc, 0, x + radius + 1);
            lineOut[x] = SAVE(bulk);
        }
        for (x = edgeB; x < edgeA; x++) {
            MOVE_ACC(acc, 0, lastx);
            ADD_FAR(bulk, acc, 0, lastx);
            lineOut[x] = SAVE(bulk);
        }
        for (x = edgeA; x <= lastx; x++) {
            MOVE_ACC(acc, x - radius - 1, lastx);
            ADD_FAR(bulk, acc, x - radius - 1, lastx);
            lineOut[x] = SAVE(bulk);
        }
    }

    #undef MOVE_ACC
    #undef ADD_FAR
    #undef SAVE
}



Imaging
HorizontalBoxBlur(Imaging im, Imaging imOut, float floatRadius)
{
    ImagingSectionCookie cookie;

    int y;

    int radius = (int) floatRadius;
    UINT32 ww = (UINT32) (1 << 24) / (floatRadius * 2 + 1);
    UINT32 fw = ((1 << 24) - (radius * 2 + 1) * ww) / 2;

    int edgeA = MIN(radius + 1, im->xsize);
    int edgeB = MAX(im->xsize - radius - 1, 0);

    UINT32 *lineOut = calloc(im->xsize, sizeof(UINT32));
    if (lineOut == NULL)
        return ImagingError_MemoryError();

    // printf(">>> %d %d %d\n", radius, ww, fw);

    ImagingSectionEnter(&cookie);

    if (im->image8)
    {
        for (y = 0; y < im->ysize; y++) {
            LineBoxBlur8(
                im->image8[y],
                (im == imOut ? (UINT8 *) lineOut : imOut->image8[y]),
                im->xsize - 1,
                radius, edgeA, edgeB,
                ww, fw
            );
            if (im == imOut) {
                // Commit.
                memcpy(imOut->image8[y], lineOut, im->xsize);
            }
        }
    }
    else
    {
        for (y = 0; y < im->ysize; y++) {
            LineBoxBlur32(
                (pixel *) im->image32[y],
                im == imOut ? lineOut : (UINT32 *) imOut->image32[y],
                im->xsize - 1,
                radius, edgeA, edgeB,
                ww, fw
            );
            if (im == imOut) {
                // Commit.
                memcpy(imOut->image32[y], lineOut, im->xsize * 4);
            }
        }
    }

    ImagingSectionLeave(&cookie);

    free(lineOut);

    return imOut;
}


Imaging
ImagingBoxBlur(Imaging imOut, Imaging imIn, float radius, int n)
{
    int i;

    if (n < 1) {
        return ImagingError_ValueError(
            "number of passes must be greater than zero"
        );
    }

    if (strcmp(imIn->mode, imOut->mode) ||
        imIn->type  != imOut->type  ||
        imIn->bands != imOut->bands ||
        imIn->xsize != imOut->xsize ||
        imIn->ysize != imOut->ysize)
        return ImagingError_Mismatch();

    if (imIn->type != IMAGING_TYPE_UINT8)
        return ImagingError_ModeError();

    if ( ! (strcmp(imIn->mode, "RGB") == 0 ||
            strcmp(imIn->mode, "RGBA") == 0 ||
            strcmp(imIn->mode, "RGBX") == 0 ||
            strcmp(imIn->mode, "CMYK") == 0 ||
            strcmp(imIn->mode, "L") == 0 ||
            strcmp(imIn->mode, "LA") == 0))
        return ImagingError_ModeError();

    /* Create transposed temp image (imIn->ysize x imIn->xsize). */
    Imaging temp = ImagingNew(imIn->mode, imIn->ysize, imIn->xsize);
    if ( ! temp)
        return NULL;

    /* Apply one-dimensional blur.
       HorizontalBoxBlur transposes image at same time. */
    HorizontalBoxBlur(imIn, imOut, radius);
    for (i = 1; i < n; i ++) {
        HorizontalBoxBlur(imOut, imOut, radius);
    }
    ImagingTranspose(temp, imOut);

    /* Blur transposed result from previout step in same direction.
       Reseult will be transposed again. We'll get original image
       blurred in both directions. */
    for (i = 0; i < n; i ++) {
        HorizontalBoxBlur(temp, temp, radius);
    }
    ImagingTranspose(imOut, temp);

    ImagingDelete(temp);

    return imOut;
}


Imaging ImagingGaussianBlur(Imaging imOut, Imaging imIn, float radius,
    int passes)
{
    float sigma2, L, l, a;

    sigma2 = radius * radius / passes;
    // from http://www.mia.uni-saarland.de/Publications/gwosdek-ssvm11.pdf
    // [7] Box length.
    L = sqrt(12.0 * sigma2 + 1.0);
    // [11] Integer part of box radius.
    l = floor((L - 1.0) / 2.0);
    // [14], [Fig. 2] Fractional part of box radius.
    a = (2 * l + 1) * (l * (l + 1) - 3 * sigma2);
    a /= 6 * (sigma2 - (l + 1) * (l + 1));

    return ImagingBoxBlur(imOut, imIn, l + a, passes);
}
