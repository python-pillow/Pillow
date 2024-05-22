/* PILusm, a gaussian blur and unsharp masking library for PIL
   By Kevin Cazabon, copyright 2003
   kevin_cazabon@hotmail.com
   kevin@cazabon.com */

/* Originally released under LGPL.  Graciously donated to PIL
   for distribution under the standard PIL license in 2009." */

#include "Imaging.h"

typedef UINT8 pixel[4];

static inline UINT8
clip8(int in) {
    if (in >= 255) {
        return 255;
    }
    if (in <= 0) {
        return 0;
    }
    return (UINT8)in;
}

Imaging
ImagingUnsharpMask(
    Imaging imOut, Imaging imIn, float radius, int percent, int threshold) {
    ImagingSectionCookie cookie;
    Imaging result;

    int x, y, diff;

    pixel *lineIn = NULL;
    pixel *lineOut = NULL;
    UINT8 *lineIn8 = NULL;
    UINT8 *lineOut8 = NULL;

    /* First, do a gaussian blur on the image, putting results in imOut
       temporarily. All format checks are in gaussian blur. */
    result = ImagingGaussianBlur(imOut, imIn, radius, radius, 3);
    if (!result) {
        return NULL;
    }

    /* Now, go through each pixel, compare "normal" pixel to blurred
       pixel. If the difference is more than threshold values, apply
       the OPPOSITE correction to the amount of blur, multiplied by
       percent. */

    ImagingSectionEnter(&cookie);

    for (y = 0; y < imIn->ysize; y++) {
        if (imIn->image8) {
            lineIn8 = imIn->image8[y];
            lineOut8 = imOut->image8[y];
            for (x = 0; x < imIn->xsize; x++) {
                /* compare in/out pixels, apply sharpening */
                diff = lineIn8[x] - lineOut8[x];
                if (abs(diff) > threshold) {
                    /* add the diff*percent to the original pixel */
                    lineOut8[x] = clip8(lineIn8[x] + diff * percent / 100);
                } else {
                    /* new pixel is the same as imIn */
                    lineOut8[x] = lineIn8[x];
                }
            }
        } else {
            lineIn = (pixel *)imIn->image32[y];
            lineOut = (pixel *)imOut->image32[y];
            for (x = 0; x < imIn->xsize; x++) {
                /* compare in/out pixels, apply sharpening */
                diff = lineIn[x][0] - lineOut[x][0];
                lineOut[x][0] = abs(diff) > threshold
                                    ? clip8(lineIn[x][0] + diff * percent / 100)
                                    : lineIn[x][0];

                diff = lineIn[x][1] - lineOut[x][1];
                lineOut[x][1] = abs(diff) > threshold
                                    ? clip8(lineIn[x][1] + diff * percent / 100)
                                    : lineIn[x][1];

                diff = lineIn[x][2] - lineOut[x][2];
                lineOut[x][2] = abs(diff) > threshold
                                    ? clip8(lineIn[x][2] + diff * percent / 100)
                                    : lineIn[x][2];

                diff = lineIn[x][3] - lineOut[x][3];
                lineOut[x][3] = abs(diff) > threshold
                                    ? clip8(lineIn[x][3] + diff * percent / 100)
                                    : lineIn[x][3];
            }
        }
    }

    ImagingSectionLeave(&cookie);

    return imOut;
}
