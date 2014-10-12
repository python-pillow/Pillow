#include "Python.h"
#include "Imaging.h"


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
    int w = (int) (256 * (floatRadius * 2 + 1));
    int w2 = w / 2;

    // printf("%d %d %d\n", rem, w, w2);

    #define MOVE_ACC(acc, substract, add) \
        acc[0] -= line[substract][0]; \
        acc[1] -= line[substract][1]; \
        acc[2] -= line[substract][2]; \
        acc[3] -= line[substract][3]; \
        acc[0] += line[add][0]; \
        acc[1] += line[add][1]; \
        acc[2] += line[add][2]; \
        acc[3] += line[add][3];

    #define ADD_FAR(bulk, acc, left, right) \
        bulk[0] = (acc[0] << 8) + line[left][0] * rem + line[right][0] * rem; \
        bulk[1] = (acc[1] << 8) + line[left][1] * rem + line[right][1] * rem; \
        bulk[2] = (acc[2] << 8) + line[left][2] * rem + line[right][2] * rem; \
        bulk[3] = (acc[3] << 8) + line[left][3] * rem + line[right][3] * rem;

    #define SAVE(acc) \
        (UINT8)((acc[0] + w2) / w) << 0  | (UINT8)((acc[1] + w2) / w) << 8 | \
        (UINT8)((acc[2] + w2) / w) << 16 | (UINT8)((acc[3] + w2) / w) << 24

    ImagingSectionEnter(&cookie);

    for (y = 0; y < im->ysize; y++) {
        line = (pixel *) im->image32[y];

        /* Compute acc for -1 pixel (outside of image):
           From "-radius-1" to "0" get first pixel,
           then from "1" to "radius-1". */
        acc[0] = line[0][0] * (radius + 1);
        acc[1] = line[0][1] * (radius + 1);
        acc[2] = line[0][2] * (radius + 1);
        acc[3] = line[0][3] * (radius + 1);
        for (pix = 0; pix < radius; pix++) {
            acc[0] += line[pix][0];
            acc[1] += line[pix][1];
            acc[2] += line[pix][2];
            acc[3] += line[pix][3];
        }

        /* Substract pixel from left ("0").
           Add pixels from radius. */
        for (x = 0; x <= radius; x++) {
            MOVE_ACC(acc, 0, x + radius);
            ADD_FAR(bulk, acc, 0, x+radius+1);
            imOut->image32[x][y] = SAVE(bulk);
        }
        /* Substract previous pixel from "-radius".
           Add pixels from radius. */
        for (x = radius + 1; x < im->xsize - radius; x++) {
            MOVE_ACC(acc, x - radius - 1, x + radius);
            ADD_FAR(bulk, acc, x-radius-1, x+radius+1);
            imOut->image32[x][y] = SAVE(bulk);
        }
        /* Substract previous pixel from "-radius".
           Add last pixel. */
        for (x = im->xsize - radius; x < im->xsize; x++) {
            MOVE_ACC(acc, x - radius - 1, lastx);
            ADD_FAR(bulk, acc, x-radius-1, lastx);
            imOut->image32[x][y] = SAVE(bulk);
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
