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


Imaging
ImagingUnsharpMask(Imaging imOut, Imaging imIn, float radius, int percent,
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

    if (strcmp(imIn->mode, "RGB") == 0) {
        channels = 3;
    } else if (strcmp(imIn->mode, "RGBA") == 0) {
        channels = 3;
    } else if (strcmp(imIn->mode, "RGBX") == 0) {
        channels = 3;
    } else if (strcmp(imIn->mode, "CMYK") == 0) {
        channels = 4;
    } else if (strcmp(imIn->mode, "L") == 0) {
        channels = 1;
    } else
        return ImagingError_ModeError();

    /* first, do a gaussian blur on the image, putting results in imOut
       temporarily */
    result = ImagingGaussianBlur(imOut, imIn, radius, 3);
    if (!result)
        return NULL;

    /* now, go through each pixel, compare "normal" pixel to blurred
       pixel.  if the difference is more than threshold values, apply
       the OPPOSITE correction to the amount of blur, multiplied by
       percent. */

    ImagingSectionEnter(&cookie);

    if (strcmp(imIn->mode, "RGBX") == 0 || strcmp(imIn->mode, "RGBA") == 0) {
        hasAlpha = 1;
    }

    for (y = 0; y < imIn->ysize; y++) {
        if (channels == 1) {
            lineIn8 = imIn->image8[y];
            lineOut8 = imOut->image8[y];
        } else {
            lineIn = imIn->image32[y];
            lineOut = imOut->image32[y];
        }
        for (x = 0; x < imIn->xsize; x++) {
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
