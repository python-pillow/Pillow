#include "Python.h"
#include "Imaging.h"


#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))


Imaging
HorizontalBoxBlur32(Imaging im, Imaging imOut, float floatRadius)
{
    ImagingSectionCookie cookie;

    int x, y, pix;
    UINT32 acc[4];
    UINT32 bulk[4];

    typedef UINT8 pixel[4];
    pixel *line;
    int lastx = im->xsize - 1;

    int radius = (int) floatRadius;
    UINT32 ww = (UINT32) (1 << 24) / (floatRadius * 2 + 1);
    UINT32 fw = ((1 << 24) - (radius * 2 + 1) * ww) / 2;

    int edgeA = MIN(radius + 1, im->xsize);
    int edgeB = MAX(im->xsize - radius - 1, 0);

    // printf(">>> %d %d %d\n", radius, ww, fw);

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

    ImagingSectionEnter(&cookie);

    for (y = 0; y < im->ysize; y++) {
        line = (pixel *) im->image32[y];

        /* Compute acc for -1 pixel (outside of image):
           From "-radius-1" to "-1" get first pixel,
           then from "0" to "radius-1". */
        acc[0] = line[0][0] * (radius + 1);
        acc[1] = line[0][1] * (radius + 1);
        acc[2] = line[0][2] * (radius + 1);
        acc[3] = line[0][3] * (radius + 1);
        /* As radius can be bigger than xsize, iterate to edgeA -1. */
        for (pix = 0; pix < edgeA - 1; pix++) {
            acc[0] += line[pix][0];
            acc[1] += line[pix][1];
            acc[2] += line[pix][2];
            acc[3] += line[pix][3];
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
                imOut->image32[x][y] = SAVE(bulk);
            }
            /* Substract previous pixel from "-radius".
               Add pixels from radius. */
            for (x = edgeA; x < edgeB; x++) {
                MOVE_ACC(acc, x - radius - 1, x + radius);
                ADD_FAR(bulk, acc, x - radius - 1, x + radius + 1);
                imOut->image32[x][y] = SAVE(bulk);
            }
            /* Substract previous pixel from "-radius".
               Add last pixel. */
            for (x = edgeB; x < im->xsize; x++) {
                MOVE_ACC(acc, x - radius - 1, lastx);
                ADD_FAR(bulk, acc, x - radius - 1, lastx);
                imOut->image32[x][y] = SAVE(bulk);
            }
        }
        else
        {
            for (x = 0; x < edgeB; x++) {
                MOVE_ACC(acc, 0, x + radius);
                ADD_FAR(bulk, acc, 0, x + radius + 1);
                imOut->image32[x][y] = SAVE(bulk);
            }
            for (x = edgeB; x < edgeA; x++) {
                MOVE_ACC(acc, 0, lastx);
                ADD_FAR(bulk, acc, 0, lastx);
                imOut->image32[x][y] = SAVE(bulk);
            }
            for (x = edgeA; x < im->xsize; x++) {
                MOVE_ACC(acc, x - radius - 1, lastx);
                ADD_FAR(bulk, acc, x - radius - 1, lastx);
                imOut->image32[x][y] = SAVE(bulk);
            }
        }
    }

    ImagingSectionLeave(&cookie);

    #undef MOVE_ACC
    #undef ADD_FAR
    #undef SAVE

    return imOut;
}


Imaging
HorizontalBoxBlur8(Imaging im, Imaging imOut, float floatRadius)
{
    ImagingSectionCookie cookie;

    int x, y, pix;
    unsigned int acc;
    unsigned int bulk;

    UINT8 *line;
    int lastx = im->xsize - 1;

    int radius = (int) floatRadius;
    UINT32 ww = (UINT32) (1 << 24) / (floatRadius * 2 + 1);
    UINT32 fw = ((1 << 24) - (radius * 2 + 1) * ww) / 2;

    int edgeA = MIN(radius + 1, im->xsize);
    int edgeB = MAX(im->xsize - radius - 1, 0);


    #define MOVE_ACC(acc, substract, add) \
        acc += line[add] - line[substract];

    #define ADD_FAR(bulk, acc, left, right) \
        bulk = (acc * ww) + (line[left] + line[right]) * fw;

    #define SAVE(acc) \
        (UINT8)((acc + (1 << 23)) >> 24)

    ImagingSectionEnter(&cookie);

    for (y = 0; y < im->ysize; y++) {
        line = im->image8[y];

        acc = line[0] * (radius + 1);
        for (pix = 0; pix < edgeA - 1; pix++) {
            acc += line[pix];
        }
        acc += line[lastx] * (radius - edgeA + 1);

        if (edgeA <= edgeB)
        {
            for (x = 0; x < edgeA; x++) {
                MOVE_ACC(acc, 0, x + radius);
                ADD_FAR(bulk, acc, 0, x + radius + 1);
                imOut->image8[x][y] = SAVE(bulk);
            }
            for (x = edgeA; x < edgeB; x++) {
                MOVE_ACC(acc, x - radius - 1, x + radius);
                ADD_FAR(bulk, acc, x - radius - 1, x + radius + 1);
                imOut->image8[x][y] = SAVE(bulk);
            }
            for (x = edgeB; x < im->xsize; x++) {
                MOVE_ACC(acc, x - radius - 1, lastx);
                ADD_FAR(bulk, acc, x - radius - 1, lastx);
                imOut->image8[x][y] = SAVE(bulk);
            }
        }
        else
        {
            for (x = 0; x < edgeB; x++) {
                MOVE_ACC(acc, 0, x + radius);
                ADD_FAR(bulk, acc, 0, x + radius + 1);
                imOut->image8[x][y] = SAVE(bulk);
            }
            for (x = edgeB; x < edgeA; x++) {
                MOVE_ACC(acc, 0, lastx);
                ADD_FAR(bulk, acc, 0, lastx);
                imOut->image8[x][y] = SAVE(bulk);
            }
            for (x = edgeA; x < im->xsize; x++) {
                MOVE_ACC(acc, x - radius - 1, lastx);
                ADD_FAR(bulk, acc, x - radius - 1, lastx);
                imOut->image8[x][y] = SAVE(bulk);
            }
        }
    }

    ImagingSectionLeave(&cookie);

    #undef MOVE_ACC
    #undef ADD_FAR
    #undef SAVE

    return imOut;
}


Imaging
ImagingBoxBlur(Imaging im, Imaging imOut, float radius)
{
    if (strcmp(im->mode, imOut->mode) ||
        im->type  != imOut->type  ||
        im->bands != imOut->bands ||
        im->xsize != imOut->xsize ||
        im->ysize != imOut->ysize)
        return ImagingError_Mismatch();

    if (im->type != IMAGING_TYPE_UINT8)
        return ImagingError_ModeError();

    if ( ! (strcmp(im->mode, "RGB") == 0 ||
            strcmp(im->mode, "RGBA") == 0 ||
            strcmp(im->mode, "RGBX") == 0 ||
            strcmp(im->mode, "CMYK") == 0 ||
            strcmp(im->mode, "L") == 0 ||
            strcmp(im->mode, "LA") == 0))
        return ImagingError_ModeError();

    /* Create transposed temp image (im->ysize x im->xsize). */
    Imaging temp = ImagingNew(im->mode, im->ysize, im->xsize);
    if ( ! temp)
        return NULL;

    /* Apply one-dimensional blur.
       HorizontalBoxBlur32 transposes image at same time. */
    if (strcmp(im->mode, "L") == 0) {
        HorizontalBoxBlur8(im, temp, radius);
    } else {
        HorizontalBoxBlur32(im, temp, radius);
    }

    /* Blur transposed result from previout step in same direction.
       Reseult will be transposed again. We'll get original image
       blurred in both directions. */
    if (strcmp(im->mode, "L") == 0) {
        HorizontalBoxBlur8(temp, imOut, radius);
    } else {
        HorizontalBoxBlur32(temp, imOut, radius);
    }

    ImagingDelete(temp);

    return imOut;
}
