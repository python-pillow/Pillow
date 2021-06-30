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

int
ImagingSaveRaw(Imaging im, FILE *fp) {
    int x, y, i;

    if (strcmp(im->mode, "1") == 0 || strcmp(im->mode, "L") == 0) {
        /* @PIL227: FIXME: for mode "1", map != 0 to 255 */

        /* PGM "L" */
        for (y = 0; y < im->ysize; y++) {
            fwrite(im->image[y], 1, im->xsize, fp);
        }

    } else {
        /* PPM "RGB" or other internal format */
        for (y = 0; y < im->ysize; y++) {
            for (x = i = 0; x < im->xsize; x++, i += im->pixelsize) {
                fwrite(im->image[y] + i, 1, im->bands, fp);
            }
        }
    }

    return 1;
}

int
ImagingSavePPM(Imaging im, const char *outfile) {
    FILE *fp;

    if (!im) {
        (void)ImagingError_ValueError(NULL);
        return 0;
    }

    fp = fopen(outfile, "wb");
    if (!fp) {
        (void)ImagingError_OSError();
        return 0;
    }

    if (strcmp(im->mode, "1") == 0 || strcmp(im->mode, "L") == 0) {
        /* Write "PGM" */
        fprintf(fp, "P5\n%d %d\n255\n", im->xsize, im->ysize);
    } else if (strcmp(im->mode, "RGB") == 0) {
        /* Write "PPM" */
        fprintf(fp, "P6\n%d %d\n255\n", im->xsize, im->ysize);
    } else {
        fclose(fp);
        (void)ImagingError_ModeError();
        return 0;
    }

    ImagingSaveRaw(im, fp);

    fclose(fp);

    return 1;
}
