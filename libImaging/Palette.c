/*
 * The Python Imaging Library
 * $Id$
 *
 * imaging palette object
 *
 * history:
 * 1996-05-05 fl   Added to library
 * 1996-05-27 fl   Added colour mapping stuff
 * 1997-05-12 fl   Support RGBA palettes
 * 2005-02-09 fl   Removed grayscale entries from web palette
 *
 * Copyright (c) Secret Labs AB 1997-2005.  All rights reserved.
 * Copyright (c) Fredrik Lundh 1995-1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include <math.h>


ImagingPalette
ImagingPaletteNew(const char* mode)
{
    /* Create a palette object */

    int i;
    ImagingPalette palette;

    if (strcmp(mode, "RGB") && strcmp(mode, "RGBA"))
	return (ImagingPalette) ImagingError_ModeError();

    palette = calloc(1, sizeof(struct ImagingPaletteInstance));
    if (!palette)
	return (ImagingPalette) ImagingError_MemoryError();

    strcpy(palette->mode, mode);

    /* Initialize to ramp */
    for (i = 0; i < 256; i++) {
	palette->palette[i*4+0] =
	palette->palette[i*4+1] =
	palette->palette[i*4+2] = (UINT8) i;
	palette->palette[i*4+3] = 255; /* opaque */
    }

    return palette;
}

ImagingPalette
ImagingPaletteNewBrowser(void)
{
    /* Create a standard "browser" palette object */

    int i, r, g, b;
    ImagingPalette palette;

    palette = ImagingPaletteNew("RGB");
    if (!palette)
	return NULL;

    /* Blank out unused entries */
    /* FIXME: Add 10-level windows palette here? */

    for (i = 0; i < 10; i++) {
	palette->palette[i*4+0] =
	palette->palette[i*4+1] =
	palette->palette[i*4+2] = 0;
    }

    /* Simple 6x6x6 colour cube */

    for (b = 0; b < 256; b += 51)
	for (g = 0; g < 256; g += 51)
	    for (r = 0; r < 256; r += 51) {
		palette->palette[i*4+0] = r;
		palette->palette[i*4+1] = g;
		palette->palette[i*4+2] = b;
		i++;
	    }

    /* Blank out unused entries */
    /* FIXME: add 30-level greyscale wedge here? */

    for (; i < 256; i++) {
	palette->palette[i*4+0] =
	palette->palette[i*4+1] =
	palette->palette[i*4+2] = 0;
    }

    return palette;
}

ImagingPalette
ImagingPaletteDuplicate(ImagingPalette palette)
{
    /* Duplicate palette descriptor */

    ImagingPalette new_palette;

    if (!palette)
	return NULL;

    new_palette = malloc(sizeof(struct ImagingPaletteInstance));
    if (!new_palette)
	return (ImagingPalette) ImagingError_MemoryError();

    memcpy(new_palette, palette, sizeof(struct ImagingPaletteInstance));

    /* Don't share the cache */
    new_palette->cache = NULL;

    return new_palette;
}

void
ImagingPaletteDelete(ImagingPalette palette)
{
    /* Destroy palette object */

    if (palette) {
	if (palette->cache)
	    free(palette->cache);
	free(palette);
    }
}


/* -------------------------------------------------------------------- */
/* Colour mapping							*/
/* -------------------------------------------------------------------- */

/* This code is used to map RGB triplets to palette indices, using
   a palette index cache. */

/*
 * This implementation is loosely based on the corresponding code in
 * the IJG JPEG library by Thomas G. Lane.  Original algorithms by
 * Paul Heckbert and Spencer W. Thomas.
 *
 * The IJG JPEG library is copyright (C) 1991-1995, Thomas G. Lane.  */

#define	DIST(a, b, s) (a - b) * (a - b) * s

/* Colour weights (no scaling, for now) */
#define	RSCALE	1
#define	GSCALE	1
#define	BSCALE	1

/* Calculated scaled distances */
#define	RDIST(a, b) DIST(a, b, RSCALE*RSCALE)
#define	GDIST(a, b) DIST(a, b, GSCALE*GSCALE)
#define	BDIST(a, b) DIST(a, b, BSCALE*BSCALE)

/* Incremental steps */
#define RSTEP	(4 * RSCALE)
#define GSTEP	(4 * GSCALE)
#define BSTEP	(4 * BSCALE)

#define	BOX	8

#define	BOXVOLUME BOX*BOX*BOX

void
ImagingPaletteCacheUpdate(ImagingPalette palette, int r, int g, int b)
{
    int i, j;
    unsigned int dmin[256], dmax;
    int r0, g0, b0;
    int r1, g1, b1;
    int rc, gc, bc;
    unsigned int d[BOXVOLUME];
    UINT8 c[BOXVOLUME];

    /* Get box boundaries for the given (r,g,b)-triplet.  Each box
       covers eight cache slots (32 colour values, that is). */

    r0 = r & 0xe0; r1 = r0 + 0x1f; rc = (r0 + r1) / 2;
    g0 = g & 0xe0; g1 = g0 + 0x1f; gc = (g0 + g1) / 2;
    b0 = b & 0xe0; b1 = b0 + 0x1f; bc = (b0 + b1) / 2;

    /* Step 1 -- Select relevant palette entries (after Heckbert) */

    /* For each palette entry, calculate the min and max distances to
     * any position in the box given by the colour we're looking for. */

    dmax = (unsigned int) ~0;

    for (i = 0; i < 256; i++) {

	int r, g, b;
	unsigned int tmin, tmax;

	/* Find min and max distances to any point in the box */
	r = palette->palette[i*4+0];
	tmin = (r < r0) ? RDIST(r, r1) : (r > r1) ? RDIST(r, r0) : 0;
	tmax = (r <= rc) ? RDIST(r, r1) : RDIST(r, r0);

	g = palette->palette[i*4+1];
	tmin += (g < g0) ? GDIST(g, g1) : (g > g1) ? GDIST(g, g0) : 0;
	tmax += (g <= gc) ? GDIST(g, g1) : GDIST(g, g0);

	b = palette->palette[i*4+2];
	tmin += (b < b0) ? BDIST(b, b1) : (b > b1) ? BDIST(b, b0) : 0;
	tmax += (b <= bc) ? BDIST(b, b1) : BDIST(b, b0);

	dmin[i] = tmin;
	if (tmax < dmax)
	    dmax = tmax; /* keep the smallest max distance only */

    }

    /* Step 2 -- Incrementally update cache slot (after Thomas) */

    /* Find the box containing the nearest palette entry, and update
     * all slots in that box.  We only check boxes for which the min
     * distance is less than or equal the smallest max distance */

    for (i = 0; i < BOXVOLUME; i++)
	d[i] = (unsigned int) ~0;

    for (i = 0; i < 256; i++)

	if (dmin[i] <= dmax) {

	    int rd, gd, bd;
	    int ri, gi, bi;
	    int rx, gx, bx;

	    ri = (r0 - palette->palette[i*4+0]) * RSCALE;
	    gi = (g0 - palette->palette[i*4+1]) * GSCALE;
	    bi = (b0 - palette->palette[i*4+2]) * BSCALE;

	    rd = ri*ri + gi*gi + bi*bi;

	    ri = ri * (2 * RSTEP) + RSTEP * RSTEP;
	    gi = gi * (2 * GSTEP) + GSTEP * GSTEP;
	    bi = bi * (2 * BSTEP) + BSTEP * BSTEP;

	    rx = ri;
	    for (r = j = 0; r < BOX; r++) {
		gd = rd; gx = gi;
		for (g = 0; g < BOX; g++) {
		    bd = gd; bx = bi;
		    for (b = 0; b < BOX; b++) {
			if ((unsigned int) bd < d[j]) {
			    d[j] = bd;
			    c[j] = (UINT8) i;
			}
			bd += bx;
			bx += 2 * BSTEP * BSTEP;
			j++;
		    }
		    gd += gx;
		    gx += 2 * GSTEP * GSTEP;
		}
		rd += rx;
		rx += 2 * RSTEP * RSTEP;
	    }
	}

    /* Step 3 -- Update cache */

    /* The c array now contains the closest match for each
     * cache slot in the box.  Update the cache. */

    j = 0;
    for (r = r0; r < r1; r+=4)
	for (g = g0; g < g1; g+=4)
	    for (b = b0; b < b1; b+=4)
		ImagingPaletteCache(palette, r, g, b) = c[j++];
}


int
ImagingPaletteCachePrepare(ImagingPalette palette)
{
    /* Add a colour cache to a palette */

    int i;
    int entries = 64*64*64;

    if (palette->cache == NULL) {

	/* The cache is 512k.  It might be a good idea to break it
	   up into a pointer array (e.g. an 8-bit image?) */

	palette->cache = (INT16*) malloc(entries * sizeof(INT16));
	if (!palette->cache) {
	    (void) ImagingError_MemoryError();
	    return -1;
	}

	/* Mark all entries as empty */
	for (i = 0; i < entries; i++)
	    palette->cache[i] = 0x100;

    }

    return 0;
}


void
ImagingPaletteCacheDelete(ImagingPalette palette)
{
    /* Release the colour cache, if any */

    if (palette && palette->cache) {
	free(palette->cache);
	palette->cache = NULL;
    }
}
