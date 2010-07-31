/* PILusm, a gaussian blur and unsharp masking library for PIL
   By Kevin Cazabon, copyright 2003
   kevin_cazabon@hotmail.com
   kevin@cazabon.com */

/* Originally released under LGPL.  Graciously donated to PIL
   for distribution under the standard PIL license in 2009." */

#include "Python.h"
#include "Imaging.h"

#define PILUSMVERSION "0.6.1"

/* version history

0.6.1   converted to C and added to PIL 1.1.7

0.6.0   fixed/improved float radius support (oops!)
        now that radius can be a float (properly), changed radius value to
            be an actual radius (instead of diameter).  So, you should get
            similar results from PIL_usm as from other paint programs when
            using the SAME values (no doubling of radius required any more).
            Be careful, this may "break" software if you had it set for 2x
            or 5x the radius as was recommended with earlier versions.
        made PILusm thread-friendly (release GIL before lengthly operations,
            and re-acquire it before returning to Python).  This makes a huge
            difference with multi-threaded applications on dual-processor
            or "Hyperthreading"-enabled systems (Pentium4, Xeon, etc.)

0.5.0   added support for float radius values!

0.4.0   tweaked gaussian curve calculation to be closer to consistent shape
            across a wide range of radius values

0.3.0   changed deviation calculation in gausian algorithm to be dynamic
        _gblur now adds 1 to the user-supplied radius before using it so
            that a value of "0" returns the original image instead of a
            black one.
        fixed handling of alpha channel in RGBX, RGBA images
        improved speed of gblur by reducing unnecessary checks and assignments

0.2.0   fixed L-mode image support

0.1.0   initial release

*/

static inline UINT8 clip(double in)
{
    if (in >= 255.0)
	return (UINT8) 255;
    if (in <= 0.0)
	return (UINT8) 0;
    return (UINT8) in;
}

static Imaging
gblur(Imaging im, Imaging imOut, float floatRadius, int channels, int padding)
{
    ImagingSectionCookie cookie;

    float *maskData = NULL;
    int y = 0;
    int x = 0;
    float z = 0;
    float sum = 0.0;
    float dev = 0.0;

    float *buffer = NULL;

    int *line = NULL;
    UINT8 *line8 = NULL;

    int pix = 0;
    float newPixel[4];
    int channel = 0;
    int offset = 0;
    INT32 newPixelFinals;

    int radius = 0;
    float remainder = 0.0;

    int i;

    /* Do the gaussian blur */

    /* For a symmetrical gaussian blur, instead of doing a radius*radius
       matrix lookup, you get the EXACT same results by doing a radius*1
       transform, followed by a 1*radius transform.  This reduces the
       number of lookups exponentially (10 lookups per pixel for a
       radius of 5 instead of 25 lookups).  So, we blur the lines first,
       then we blur the resulting columns. */

    /* first, round radius off to the next higher integer and hold the
       remainder this is used so we can support float radius values
       properly. */

    remainder = floatRadius - ((int) floatRadius);
    floatRadius = ceil(floatRadius);

    /* Next, double the radius and offset by 2.0... that way "0" returns
       the original image instead of a black one.  We multiply it by 2.0
       so that it is a true "radius", not a diameter (the results match
       other paint programs closer that way too). */
    radius = (int) ((floatRadius * 2.0) + 2.0);

    /* create the maskData for the gaussian curve */
    maskData = malloc(radius * sizeof(float));
    /* FIXME: error checking */
    for (x = 0; x < radius; x++) {
	z = ((float) (x + 2) / ((float) radius));
	dev = 0.5 + (((float) (radius * radius)) * 0.001);
	/* you can adjust this factor to change the shape/center-weighting
	   of the gaussian */
	maskData[x] = (float) pow((1.0 / sqrt(2.0 * 3.14159265359 * dev)),
				  ((-(z - 1.0) * -(x - 1.0)) /
				   (2.0 * dev)));
    }

    /* if there's any remainder, multiply the first/last values in
       MaskData it.  this allows us to support float radius values. */
    if (remainder > 0.0) {
	maskData[0] *= remainder;
	maskData[radius - 1] *= remainder;
    }

    for (x = 0; x < radius; x++) {
	/* this is done separately now due to the correction for float
	   radius values above */
	sum += maskData[x];
    }

    for (i = 0; i < radius; i++) {
	maskData[i] *= (1.0 / sum);
	/* printf("%f\n", maskData[i]); */
    }

    /* create a temporary memory buffer for the data for the first pass
       memset the buffer to 0 so we can use it directly with += */

    /* don't bother about alpha/padding */
    buffer = calloc((size_t) (im->xsize * im->ysize * channels),
		    sizeof(float));
    if (buffer == NULL)
	return ImagingError_MemoryError();

    /* be nice to other threads while you go off to lala land */
    ImagingSectionEnter(&cookie);

    /* memset(buffer, 0, sizeof(buffer)); */

    newPixel[0] = newPixel[1] = newPixel[2] = newPixel[3] = 0;

    /* perform a blur on each line, and place in the temporary storage buffer */
    for (y = 0; y < im->ysize; y++) {
	if (channels == 1 && im->image8 != NULL) {
	    line8 = (UINT8 *) im->image8[y];
	} else {
	    line = im->image32[y];
	}
	for (x = 0; x < im->xsize; x++) {
	    newPixel[0] = newPixel[1] = newPixel[2] = newPixel[3] = 0;
	    /* for each neighbor pixel, factor in its value/weighting to the
	       current pixel */
	    for (pix = 0; pix < radius; pix++) {
		/* figure the offset of this neighbor pixel */
		offset =
		    (int) ((-((float) radius / 2.0) + (float) pix) + 0.5);
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

    /* perform a blur on each column in the buffer, and place in the
       output image */
    for (x = 0; x < im->xsize; x++) {
	for (y = 0; y < im->ysize; y++) {
	    newPixel[0] = newPixel[1] = newPixel[2] = newPixel[3] = 0;
	    /* for each neighbor pixel, factor in its value/weighting to the
	       current pixel */
	    for (pix = 0; pix < radius; pix++) {
		/* figure the offset of this neighbor pixel */
		offset =
		    (int) (-((float) radius / 2.0) + (float) pix + 0.5);
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
	    if (strcmp(im->mode, "RGBX") == 0
		|| strcmp(im->mode, "RGBA") == 0) {
	      newPixel[3] = (float) ((UINT8 *) & line[x + offset])[3];
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
    int padding = 0;

    if (strcmp(im->mode, "RGB") == 0) {
	channels = 3;
	padding = 1;
    } else if (strcmp(im->mode, "RGBA") == 0) {
	channels = 3;
	padding = 1;
    } else if (strcmp(im->mode, "RGBX") == 0) {
	channels = 3;
	padding = 1;
    } else if (strcmp(im->mode, "CMYK") == 0) {
	channels = 4;
	padding = 0;
    } else if (strcmp(im->mode, "L") == 0) {
	channels = 1;
	padding = 0;
    } else
	return ImagingError_ModeError();

    return gblur(im, imOut, radius, channels, padding);
}

Imaging
ImagingUnsharpMask(Imaging im, Imaging imOut, float radius, int percent,
		   int threshold)
{
    ImagingSectionCookie cookie;

    Imaging result;
    int channel = 0;
    int channels = 0;
    int padding = 0;

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
	padding = 1;
    } else if (strcmp(im->mode, "RGBA") == 0) {
	channels = 3;
	padding = 1;
    } else if (strcmp(im->mode, "RGBX") == 0) {
	channels = 3;
	padding = 1;
    } else if (strcmp(im->mode, "CMYK") == 0) {
	channels = 4;
	padding = 0;
    } else if (strcmp(im->mode, "L") == 0) {
	channels = 1;
	padding = 0;
    } else
	return ImagingError_ModeError();

    /* first, do a gaussian blur on the image, putting results in imOut
       temporarily */
    result = gblur(im, imOut, radius, channels, padding);
    if (!result)
	return NULL;

    /* now, go through each pixel, compare "normal" pixel to blurred
       pixel.  if the difference is more than threshold values, apply
       the OPPOSITE correction to the amount of blur, multiplied by
       percent. */

    ImagingSectionEnter(&cookie);

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
		if (strcmp(im->mode, "RGBX") == 0
		    || strcmp(im->mode, "RGBA") == 0) {
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
