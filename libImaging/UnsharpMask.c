/* PILusm, a gaussian blur and unsharp masking library for PIL
   By Kevin Cazabon, copyright 2003
   kevin_cazabon@hotmail.com
   kevin@cazabon.com */

/* Originally released under LGPL.  Graciously donated to PIL
   for distribution under the standard PIL license in 2009." */

#include "Python.h"
#include "Imaging.h"


static inline UINT8 clip(double in)
{
    if (in >= 255.0)
        return (UINT8) 255;
    if (in <= 0.0)
        return (UINT8) 0;
    return (UINT8) (in + 0.5);
}

Imaging ImagingGaussianBlur(Imaging im, Imaging imOut, float radius,
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

    return ImagingBoxBlur(imOut, im, l + a, passes);
}


Imaging
ImagingUnsharpMask(Imaging im, Imaging imOut, float radius, int percent,
                   int threshold)
{
    ImagingSectionCookie cookie;

    Imaging result;
    int channel = 0;
    int channels = 0;
    int hasAlpha = 0;

    int x = 0;
    int y = 0;

    int *lineIn = NULL;
    int *lineOut = NULL;
    UINT8 *lineIn8 = NULL;
    UINT8 *lineOut8 = NULL;

    int diff = 0;

    INT32 newPixel = 0;

    if (strcmp(im->mode, "RGB") == 0) {
        channels = 3;
    } else if (strcmp(im->mode, "RGBA") == 0) {
        channels = 3;
    } else if (strcmp(im->mode, "RGBX") == 0) {
        channels = 3;
    } else if (strcmp(im->mode, "CMYK") == 0) {
        channels = 4;
    } else if (strcmp(im->mode, "L") == 0) {
        channels = 1;
    } else
        return ImagingError_ModeError();

    /* first, do a gaussian blur on the image, putting results in imOut
       temporarily */
    result = ImagingGaussianBlur(im, imOut, radius, 3);
    if (!result)
        return NULL;

    /* now, go through each pixel, compare "normal" pixel to blurred
       pixel.  if the difference is more than threshold values, apply
       the OPPOSITE correction to the amount of blur, multiplied by
       percent. */

    ImagingSectionEnter(&cookie);

    if (strcmp(im->mode, "RGBX") == 0 || strcmp(im->mode, "RGBA") == 0) {
        hasAlpha = 1;
    }

    for (y = 0; y < im->ysize; y++) {
        if (channels == 1) {
            lineIn8 = im->image8[y];
            lineOut8 = imOut->image8[y];
        } else {
            lineIn = im->image32[y];
            lineOut = imOut->image32[y];
        }
        for (x = 0; x < im->xsize; x++) {
            newPixel = 0;
            /* compare in/out pixels, apply sharpening */
            if (channels == 1) {
                diff =
                    ((UINT8 *) & lineIn8[x])[0] -
                    ((UINT8 *) & lineOut8[x])[0];
                if (abs(diff) > threshold) {
                    /* add the diff*percent to the original pixel */
                    imOut->image8[y][x] =
                        clip((((UINT8 *) & lineIn8[x])[0]) +
                             (diff * ((float) percent) / 100.0));
                } else {
                    /* newPixel is the same as imIn */
                    imOut->image8[y][x] = ((UINT8 *) & lineIn8[x])[0];
                }
            }

            else {
                for (channel = 0; channel < channels; channel++) {
                    diff = (int) ((((UINT8 *) & lineIn[x])[channel]) -
                                  (((UINT8 *) & lineOut[x])[channel]));
                    if (abs(diff) > threshold) {
                        /* add the diff*percent to the original pixel
                           this may not work for little-endian systems, fix it! */
                        newPixel =
                            newPixel |
                            clip((float) (((UINT8 *) & lineIn[x])[channel])
                                 +
                                 (diff *
                                  (((float) percent /
                                    100.0)))) << (channel * 8);
                    } else {
                        /* newPixel is the same as imIn
                           this may not work for little-endian systems, fix it! */
                        newPixel =
                            newPixel | ((UINT8 *) & lineIn[x])[channel] <<
                            (channel * 8);
                    }
                }
                if (hasAlpha) {
                    /* preserve the alpha channel
                       this may not work for little-endian systems, fix it! */
                    newPixel =
                        newPixel | ((UINT8 *) & lineIn[x])[channel] << 24;
                }
                imOut->image32[y][x] = newPixel;
            }
        }
    }

    ImagingSectionLeave(&cookie);

    return imOut;
}
