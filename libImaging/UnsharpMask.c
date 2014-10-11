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

static Imaging
gblur(Imaging im, Imaging imOut, float radius, int channels)
{
    ImagingSectionCookie cookie;

    float *maskData = NULL;
    int y = 0;
    int x = 0;
    float sum = 0.0;

    float *buffer = NULL;

    int *line = NULL;
    UINT8 *line8 = NULL;

    int pix = 0;
    float newPixel[4];
    int channel = 0;
    int offset = 0;
    INT32 newPixelFinals;

    int effectiveRadius = 0;
    int window = 0;
    int hasAlpha = 0;

    /* Do the gaussian blur */

    /* For a symmetrical gaussian blur, instead of doing a radius*radius
       matrix lookup, you get the EXACT same results by doing a radius*1
       transform, followed by a 1*radius transform.  This reduces the
       number of lookups exponentially (10 lookups per pixel for a
       radius of 5 instead of 25 lookups).  So, we blur the lines first,
       then we blur the resulting columns. */

    /* Only pixels in effective radius from source pixel are accounted.
       The Gaussian values outside 3 x radius is near zero. */
    effectiveRadius = (int) ceil(radius * 2.57);
    /* Window is number of pixels forming the result pixel on one axis.
       It is source pixel and effective radius in both directions. */
    window = effectiveRadius * 2 + 1;

    /* create the maskData for the gaussian curve */
    maskData = malloc(window * sizeof(float));
    for (pix = 0; pix < window; pix++) {
        offset = pix - effectiveRadius;
        /* http://en.wikipedia.org/wiki/Gaussian_blur
           "1 / sqrt(2 * pi * dev)" is constant and will be eliminated by
           normalization. */
        maskData[pix] = pow(2.718281828459,
                            -offset * offset / (2 * radius * radius));
    }

    for (pix = 0; pix < window; pix++) {
        /* this is done separately now due to the correction for float
           radius values above */
        sum += maskData[pix];
    }

    for (pix = 0; pix < window; pix++) {
        maskData[pix] *= (1.0 / sum);
        // printf("%d %f\n", pix, maskData[pix]);
    }
    // printf("\n");

    /* create a temporary memory buffer for the data for the first pass
       memset the buffer to 0 so we can use it directly with += */

    /* don't bother about alpha */
    buffer = calloc((size_t) (im->xsize * im->ysize * channels),
                    sizeof(float));
    if (buffer == NULL)
        return ImagingError_MemoryError();

    /* be nice to other threads while you go off to lala land */
    ImagingSectionEnter(&cookie);

    /* perform a blur on each line, and place in the temporary storage buffer */
    for (y = 0; y < im->ysize; y++) {
        if (channels == 1 && im->image8 != NULL) {
            line8 = (UINT8 *) im->image8[y];
        } else {
            line = im->image32[y];
        }
        for (x = 0; x < im->xsize; x++) {
            /* for each neighbor pixel, factor in its value/weighting to the
               current pixel */
            for (pix = 0; pix < window; pix++) {
                /* figure the offset of this neighbor pixel */
                offset = pix - effectiveRadius;
                if (x + offset < 0)
                    offset = -x;
                else if (x + offset >= im->xsize)
                    offset = im->xsize - x - 1;

                /* add (neighbor pixel value * maskData[pix]) to the current
                   pixel value */
                if (channels == 1) {
                    buffer[(y * im->xsize) + x] +=
                        ((float) ((UINT8 *) & line8[x + offset])[0]) *
                        (maskData[pix]);
                } else {
                    for (channel = 0; channel < channels; channel++) {
                        buffer[(y * im->xsize * channels) +
                               (x * channels) + channel] +=
                            ((float) ((UINT8 *) & line[x + offset])
                             [channel]) * (maskData[pix]);
                    }
                }
            }
        }
    }

    if (strcmp(im->mode, "RGBX") == 0 || strcmp(im->mode, "RGBA") == 0) {
        hasAlpha = 1;
    }

    /* perform a blur on each column in the buffer, and place in the
       output image */
    for (x = 0; x < im->xsize; x++) {
        for (y = 0; y < im->ysize; y++) {
            newPixel[0] = newPixel[1] = newPixel[2] = newPixel[3] = 0;
            /* for each neighbor pixel, factor in its value/weighting to the
               current pixel */
            for (pix = 0; pix < window; pix++) {
                /* figure the offset of this neighbor pixel */
                offset = pix - effectiveRadius;
                if (y + offset < 0)
                    offset = -y;
                else if (y + offset >= im->ysize)
                    offset = im->ysize - y - 1;

                /* add (neighbor pixel value * maskData[pix]) to the current
                   pixel value */
                for (channel = 0; channel < channels; channel++) {
                    newPixel[channel] +=
                        (buffer
                         [((y + offset) * im->xsize * channels) +
                          (x * channels) + channel]) * (maskData[pix]);
                }
            }
            /* if the image is RGBX or RGBA, copy the 4th channel data to
               newPixel, so it gets put in imOut */
            if (hasAlpha) {
                newPixel[3] = (float) ((UINT8 *) & im->image32[y][x])[3];
            }

            /* pack the channels into an INT32 so we can put them back in
               the PIL image */
            newPixelFinals = 0;
            if (channels == 1) {
                newPixelFinals = clip(newPixel[0]);
            } else {
                /* for RGB, the fourth channel isn't used anyways, so just
                   pack a 0 in there, this saves checking the mode for each
                   pixel. */
                /* this doesn't work on little-endian machines... fix it! */
                newPixelFinals =
                    clip(newPixel[0]) | clip(newPixel[1]) << 8 |
                    clip(newPixel[2]) << 16 | clip(newPixel[3]) << 24;
            }
            /* set the resulting pixel in imOut */
            if (channels == 1) {
                imOut->image8[y][x] = (UINT8) newPixelFinals;
            } else {
                imOut->image32[y][x] = newPixelFinals;
            }
        }
    }

    /* free the buffer */
    free(buffer);

    /* get the GIL back so Python knows who you are */
    ImagingSectionLeave(&cookie);

    return imOut;
}

Imaging ImagingGaussianBlur(Imaging im, Imaging imOut, float radius)
{
    int channels = 0;

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

    return gblur(im, imOut, radius, channels);
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
    result = gblur(im, imOut, radius, channels);
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
