#include "Python.h"
#include "Imaging.h"


#define MAX(x, y) (((x) > (y)) ? (x) : (y))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))


Imaging
HorizontalBoxBlur32(Imaging im, Imaging imOut, float floatRadius)
{
    ImagingSectionCookie cookie;

    int x, y, pix;
    unsigned int acc[4];
    unsigned int bulk[4];

    typedef UINT8 pixel[4];
    pixel *line;
    int lastx = im->xsize - 1;

    int radius = (int) floatRadius;
    UINT8 rem = (UINT8) (256 * (floatRadius - radius));
    int w = 256 * (radius * 2 + 1) + rem * 2;
    int w2 = w / 2;

    int edgeA = MIN(radius + 1, im->xsize);
    int edgeB = MAX(im->xsize - radius - 1, 0);

    // printf("%d %d %d\n", rem, w, w2);

    #define MOVE_ACC(acc, substract, add) \
        acc[0] += line[add][0] - line[substract][0]; \
        acc[1] += line[add][1] - line[substract][1]; \
        acc[2] += line[add][2] - line[substract][2]; \
        acc[3] += line[add][3] - line[substract][3];

    #define ADD_FAR(bulk, acc, left, right) \
        bulk[0] = (acc[0] << 8) + (line[left][0] + line[right][0]) * rem; \
        bulk[1] = (acc[1] << 8) + (line[left][1] + line[right][1]) * rem; \
        bulk[2] = (acc[2] << 8) + (line[left][2] + line[right][2]) * rem; \
        bulk[3] = (acc[3] << 8) + (line[left][3] + line[right][3]) * rem;

    #define SAVE(acc) \
        (UINT8)((acc[0] + w2) / w) << 0  | (UINT8)((acc[1] + w2) / w) << 8 | \
        (UINT8)((acc[2] + w2) / w) << 16 | (UINT8)((acc[3] + w2) / w) << 24

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
    UINT8 rem = (UINT8) (256 * (floatRadius - radius));
    int w = 256 * (radius * 2 + 1) + rem * 2;
    int w2 = w / 2;

    int edgeA = MIN(radius + 1, im->xsize);
    int edgeB = MAX(im->xsize - radius - 1, 0);

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
                acc = acc + line[x + radius] - line[0];
                bulk = (acc << 8) + (line[0] + line[x + radius + 1]) * rem;
                imOut->image8[x][y] = (UINT8)((bulk + w2) / w);
            }
            for (x = edgeA; x < edgeB; x++) {
                acc = acc + line[x + radius] - line[x - radius - 1];
                bulk = (acc << 8) + (line[x - radius - 1] + line[x + radius + 1]) * rem;
                imOut->image8[x][y] = (UINT8)((bulk + w2) / w);
            }
            for (x = edgeB; x < im->xsize; x++) {
                acc = acc + line[lastx] - line[x - radius - 1];
                bulk = (acc << 8) + (line[x - radius - 1] + line[lastx]) * rem;
                imOut->image8[x][y] = (UINT8)((bulk + w2) / w);
            }
        }
        else
        {
            for (x = 0; x < edgeB; x++) {
                acc = acc + line[x + radius] - line[0];
                bulk = (acc << 8) + (line[0] + line[x + radius + 1]) * rem;
                imOut->image8[x][y] = (UINT8)((bulk + w2) / w);
            }
            for (x = edgeB; x < edgeA; x++) {
                acc = acc + line[lastx] - line[0];
                bulk = (acc << 8) + (line[0] + line[lastx]) * rem;
                imOut->image8[x][y] = (UINT8)((bulk + w2) / w);
            }
            for (x = edgeA; x < im->xsize; x++) {
                acc = acc + line[lastx] - line[x - radius - 1];
                bulk = (acc << 8) + (line[x - radius - 1] + line[lastx]) * rem;
                imOut->image8[x][y] = (UINT8)((bulk + w2) / w);
            }
        }
    }

    ImagingSectionLeave(&cookie);

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

    /* Blur in same direction transposed result from previout step.
       Reseult will be transposes again. We'll get original image
       blurred in both directions. */
    if (strcmp(im->mode, "L") == 0) {
        HorizontalBoxBlur8(temp, imOut, radius);
    } else {
        HorizontalBoxBlur32(temp, imOut, radius);
    }

    ImagingDelete(temp);

    return imOut;
}
