#include "Python.h"
#include "Imaging.h"


Imaging
HorizontalBoxBlur32(Imaging im, Imaging imOut, float floatRadius)
{
    ImagingSectionCookie cookie;

    int x, y, pix;
    int acc[4];

    typedef UINT8 pixel[4];
    pixel *line;
    int lastx = im->xsize - 1;

    int radius = (int) floatRadius;
    int window = radius * 2 + 1;

    #define SAVE(acc) \
        (UINT8)(acc[0] / window) | (UINT8)(acc[1] / window) << 8 | \
        (UINT8)(acc[2] / window) << 16 | (UINT8)(acc[3] / window) << 24

    #define MOVE_ACC(acc, substract, add) \
        acc[0] -= line[substract][0]; \
        acc[1] -= line[substract][1]; \
        acc[2] -= line[substract][2]; \
        acc[3] -= line[substract][3]; \
        acc[0] += line[add][0]; \
        acc[1] += line[add][1]; \
        acc[2] += line[add][2]; \
        acc[3] += line[add][3];

    ImagingSectionEnter(&cookie);

    for (y = 0; y < im->ysize; y++) {
        line = (pixel *) im->image32[y];

        /* Compute acc for -1 pixel (outside of image):
           From "-radius-1" to "0" get first pixel,
           then from "1" to "radius-1". */
        acc[0] = line[0][0] * (radius + 2);
        acc[1] = line[0][1] * (radius + 2);
        acc[2] = line[0][2] * (radius + 2);
        acc[3] = line[0][3] * (radius + 2);
        for (pix = 1; pix < radius; pix++) {
            acc[0] += line[pix][0];
            acc[1] += line[pix][1];
            acc[2] += line[pix][2];
            acc[3] += line[pix][3];
        }

        /* Substract pixel from left ("0").
           Add pixels from radius. */
        for (x = 0; x <= radius; x++) {
            MOVE_ACC(acc, 0, x + radius);
            imOut->image32[x][y] = SAVE(acc);
        }
        /* Substract previous pixel from "-radius".
           Add pixels from radius. */
        for (x = radius + 1; x < im->xsize - radius; x++) {
            MOVE_ACC(acc, x - radius - 1, x + radius);
            imOut->image32[x][y] = SAVE(acc);
        }
        /* Substract previous pixel from "-radius".
           Add last pixel. */
        for (x = im->xsize - radius; x < im->xsize; x++) {
            MOVE_ACC(acc, x - radius - 1, lastx);
            imOut->image32[x][y] = SAVE(acc);
        }
    }

    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingBoxBlur(Imaging im, Imaging imOut, float radius)
{
    /* Create transposed temp image (im->ysize x im->xsize). */
    Imaging temp = ImagingNew(im->mode, im->ysize, im->xsize);
    if ( ! temp)
        return NULL;

    /* Apply one-dimensional blur.
       HorizontalBoxBlur32 transposes image at same time. */
    if ( ! HorizontalBoxBlur32(im, temp, radius)) {
        ImagingDelete(temp);
        return NULL;
    }

    /* Blur in same direction transposed result from previout step.
       Reseult will be transposes again. We'll get original image
       blurred in both directions. */
    if ( ! HorizontalBoxBlur32(temp, imOut, radius)) {
        ImagingDelete(temp);
        return NULL;
    }

    ImagingDelete(temp);

    return imOut;
}
