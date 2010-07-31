/*
 * The Python Imaging Library
 * $Id$
 *
 * built-in image file handling
 *
 * history:
 * 1995-11-26 fl  Created, supports PGM/PPM
 * 1996-08-07 fl  Write "1" images as PGM
 * 1999-02-21 fl  Don't write non-standard modes
 *
 * Copyright (c) 1997-99 by Secret Labs AB.
 * Copyright (c) 1995-96 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include <ctype.h>

Imaging
ImagingOpenPPM(const char* infile)
{
    FILE* fp;
    int i, c, v;
    char* mode;
    int x, y, max;
    Imaging im;

    if (!infile)
	return ImagingError_ValueError(NULL);

    fp = fopen(infile, "rb");
    if (!fp)
	return ImagingError_IOError();

    /* PPM magic */
    if (fgetc(fp) != 'P')
	goto error;
    switch (fgetc(fp)) {
    case '4': /* FIXME: 1-bit images are not yet supported */
	goto error;
    case '5':
	mode = "L";
	break;
    case '6':
	mode = "RGB";
	break;
    default:
	goto error;
    }

    i = 0;
    c = fgetc(fp);

    x = y = max = 0;

    while (i < 3) {	

	/* Ignore optional comment fields */
	while (c == '\n') {
	    c = fgetc(fp);
	    if (c == '#') {
		do {
		    c = fgetc(fp);
		    if (c == EOF)
			goto error;
		} while (c != '\n');
		c = fgetc(fp);
	    }
	}

	/* Skip forward to next value */
	while (isspace(c))
	    c = fgetc(fp);

	/* And parse it */
	v = 0;
	while (isdigit(c)) {
	    v = v * 10 + (c - '0');
	    c = fgetc(fp);
	}

	if (c == EOF)
	    goto error;

	switch (i++) {
	case 0:
	    x = v;
	    break;
	case 1:
	    y = v;
	    break;
	case 2:
	    max = v;
	    break;
	}
    }

    im = ImagingNew(mode, x, y);
    if (!im)
	return NULL;

    /* if (max != 255) ... FIXME: does anyone ever use this feature? */

    if (strcmp(im->mode, "L") == 0) {

	/* PPM "L" */
	for (y = 0; y < im->ysize; y++)
	    if (fread(im->image[y], im->xsize, 1, fp) != 1)
		goto error;

    } else {

	/* PPM "RGB" or PyPPM mode */
	for (y = 0; y < im->ysize; y++)
	    for (x = i = 0; x < im->xsize; x++, i += im->pixelsize)
		if (fread(im->image[y]+i, im->bands, 1, fp) != 1)
		    goto error;
    }

    fclose(fp);

    return im;

error:
    fclose(fp);
    return ImagingError_IOError();
}


int
ImagingSaveRaw(Imaging im, FILE* fp)
{
    int x, y, i;

    if (strcmp(im->mode, "1") == 0 || strcmp(im->mode, "L") == 0) {

        /* @PIL227: FIXME: for mode "1", map != 0 to 255 */

	/* PGM "L" */
	for (y = 0; y < im->ysize; y++)
	    fwrite(im->image[y], 1, im->xsize, fp);

    } else {

	/* PPM "RGB" or other internal format */
	for (y = 0; y < im->ysize; y++)
	    for (x = i = 0; x < im->xsize; x++, i += im->pixelsize)
		fwrite(im->image[y]+i, 1, im->bands, fp);

    }

    return 1;
}


int
ImagingSavePPM(Imaging im, const char* outfile)
{
    FILE* fp;

    if (!im) {
	(void) ImagingError_ValueError(NULL);
	return 0;
    }

    fp = fopen(outfile, "wb");
    if (!fp) {
	(void) ImagingError_IOError();
	return 0;
    }

    if (strcmp(im->mode, "1") == 0 || strcmp(im->mode, "L") == 0) {
	/* Write "PGM" */
	fprintf(fp, "P5\n%d %d\n255\n", im->xsize, im->ysize);
    } else if (strcmp(im->mode, "RGB") == 0) {
        /* Write "PPM" */
        fprintf(fp, "P6\n%d %d\n255\n", im->xsize, im->ysize);
    } else {
	(void) ImagingError_ModeError();
        return 0;
    }

    ImagingSaveRaw(im, fp);

    fclose(fp);

    return 1;
}

