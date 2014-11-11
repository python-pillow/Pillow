/*
 * The Python Imaging Library
 * $Id$
 *
 * imaging display object for Windows
 *
 * history:
 * 1996-05-12 fl  Created
 * 1996-05-17 fl  Up and running
 * 1996-05-21 fl  Added palette stuff
 * 1996-05-26 fl  Added query palette and mode inquery
 * 1997-09-21 fl  Added draw primitive
 * 1998-01-20 fl  Use StretchDIBits instead of StretchBlt
 * 1998-12-30 fl  Plugged a resource leak in DeleteDIB (from Roger Burnham)
 *
 * Copyright (c) Secret Labs AB 1997-2001.
 * Copyright (c) Fredrik Lundh 1996.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#ifdef _WIN32

#include "ImDib.h"


char*
ImagingGetModeDIB(int size_out[2])
{
    /* Get device characteristics */

    HDC dc;
    char* mode;

    dc = CreateCompatibleDC(NULL);

    mode = "P";
    if (!(GetDeviceCaps(dc, RASTERCAPS) & RC_PALETTE)) {
	mode = "RGB";
	if (GetDeviceCaps(dc, BITSPIXEL) == 1)
	    mode = "1";
    }

    if (size_out) {
	size_out[0] = GetDeviceCaps(dc, HORZRES);
	size_out[1] = GetDeviceCaps(dc, VERTRES);
    }

    DeleteDC(dc);

    return mode;
}


ImagingDIB
ImagingNewDIB(const char *mode, int xsize, int ysize)
{
    /* Create a Windows bitmap */

    ImagingDIB dib;
    RGBQUAD *palette;
    int i;

    /* Check mode */
    if (strcmp(mode, "1") != 0 && strcmp(mode, "L") != 0 &&
	strcmp(mode, "RGB") != 0)
	return (ImagingDIB) ImagingError_ModeError();

    /* Create DIB context and info header */
    dib = (ImagingDIB) malloc(sizeof(*dib));
    if (!dib)
	return (ImagingDIB) ImagingError_MemoryError();
    dib->info = (BITMAPINFO*) malloc(sizeof(BITMAPINFOHEADER) +
                                     256 * sizeof(RGBQUAD));
    if (!dib->info) {
        free(dib);
	return (ImagingDIB) ImagingError_MemoryError();
    }

    memset(dib->info, 0, sizeof(BITMAPINFOHEADER));
    dib->info->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    dib->info->bmiHeader.biWidth = xsize;
    dib->info->bmiHeader.biHeight = ysize;
    dib->info->bmiHeader.biPlanes = 1;
    dib->info->bmiHeader.biBitCount = strlen(mode)*8;
    dib->info->bmiHeader.biCompression = BI_RGB;

    /* Create DIB */
    dib->dc = CreateCompatibleDC(NULL);
    if (!dib->dc) {
	free(dib->info);
	free(dib);
	return (ImagingDIB) ImagingError_MemoryError();
    }

    dib->bitmap = CreateDIBSection(dib->dc, dib->info, DIB_RGB_COLORS,
                                   &dib->bits, NULL, 0);
    if (!dib->bitmap) {
        free(dib->info);
	free(dib);
	return (ImagingDIB) ImagingError_MemoryError();
    }

    strcpy(dib->mode, mode);
    dib->xsize = xsize;
    dib->ysize = ysize;

    dib->pixelsize = strlen(mode);
    dib->linesize = (xsize * dib->pixelsize + 3) & -4;

    if (dib->pixelsize == 1)
	dib->pack = dib->unpack = (ImagingShuffler) memcpy;
    else {
	dib->pack = ImagingPackBGR;
	dib->unpack = ImagingPackBGR;
    }

    /* Bind the DIB to the device context */
    dib->old_bitmap = SelectObject(dib->dc, dib->bitmap);

    palette = dib->info->bmiColors;

    /* Bind a palette to it as well (only required for 8-bit DIBs) */
    if (dib->pixelsize == 1) {
	for (i = 0; i < 256; i++) {
	    palette[i].rgbRed =
	    palette[i].rgbGreen =
	    palette[i].rgbBlue = i;
	    palette[i].rgbReserved = 0;
        }
	SetDIBColorTable(dib->dc, 0, 256, palette);
    }

    /* Create an associated palette (for 8-bit displays only) */
    if (strcmp(ImagingGetModeDIB(NULL), "P") == 0) {

	char palbuf[sizeof(LOGPALETTE)+256*sizeof(PALETTEENTRY)];
	LPLOGPALETTE pal = (LPLOGPALETTE) palbuf;
	int i, r, g, b;

	/* Load system palette */
	pal->palVersion = 0x300;
	pal->palNumEntries = 256;
	GetSystemPaletteEntries(dib->dc, 0, 256, pal->palPalEntry);

	if (strcmp(mode, "L") == 0) {

	    /* Greyscale DIB.  Fill all 236 slots with a greyscale ramp
	     * (this is usually overkill on Windows since VGA only offers
	     * 6 bits greyscale resolution).  Ignore the slots already
	     * allocated by Windows */

	    i = 10;
	    for (r = 0; r < 236; r++) {
		pal->palPalEntry[i].peRed =
		pal->palPalEntry[i].peGreen =
	        pal->palPalEntry[i].peBlue = i;
		i++;
	    }

	    dib->palette = CreatePalette(pal);

	} else if (strcmp(mode, "RGB") == 0) {

#ifdef CUBE216

	    /* Colour DIB.  Create a 6x6x6 colour cube (216 entries) and
	     * add 20 extra greylevels for best result with greyscale
	     * images. */

	    i = 10;
	    for (r = 0; r < 256; r += 51)
		for (g = 0; g < 256; g += 51)
		    for (b = 0; b < 256; b += 51) {
			pal->palPalEntry[i].peRed = r;
			pal->palPalEntry[i].peGreen = g;
			pal->palPalEntry[i].peBlue = b;
			i++;
		    }
	    for (r = 1; r < 22-1; r++) {
		/* Black and white are already provided by the cube. */
		pal->palPalEntry[i].peRed =
		pal->palPalEntry[i].peGreen =
		pal->palPalEntry[i].peBlue = r * 255 / (22-1);
		i++;
	    }

#else

	    /* Colour DIB.  Alternate palette. */

	    i = 10;
	    for (r = 0; r < 256; r += 37)
		for (g = 0; g < 256; g += 32)
		    for (b = 0; b < 256; b += 64) {
			pal->palPalEntry[i].peRed = r;
			pal->palPalEntry[i].peGreen = g;
			pal->palPalEntry[i].peBlue = b;
			i++;
		    }

#endif

#if 0
	    {
		/* DEBUG: dump palette to file */
		FILE *err = fopen("dib.pal", "w");
		for (i = 0; i < 256; i++)
		    fprintf(err, "%d: %d/%d/%d\n", i,
			    pal->palPalEntry[i].peRed,
			    pal->palPalEntry[i].peGreen,
			    pal->palPalEntry[i].peBlue);
		fclose(err);
	    }
#endif

	    dib->palette = CreatePalette(pal);

	}

    }

    return dib;
}

void
ImagingPasteDIB(ImagingDIB dib, Imaging im, int xy[4])
{
    /* Paste image data into a bitmap */

    /* FIXME: check size! */

    int y;
    for (y = 0; y < im->ysize; y++)
	dib->pack(dib->bits + dib->linesize*(dib->ysize-(xy[1]+y)-1) +
		  xy[0]*dib->pixelsize, im->image[y], im->xsize);

}

void
ImagingExposeDIB(ImagingDIB dib, int dc)
{
    /* Copy bitmap to display */

    if (dib->palette != 0)
	SelectPalette((HDC) dc, dib->palette, FALSE);
    BitBlt((HDC) dc, 0, 0, dib->xsize, dib->ysize, dib->dc, 0, 0, SRCCOPY);
}

void
ImagingDrawDIB(ImagingDIB dib, int dc, int dst[4], int src[4])
{
    /* Copy bitmap to printer/display */

    if (GetDeviceCaps((HDC) dc, RASTERCAPS) & RC_STRETCHDIB) {
        /* stretchdib (printers) */
        StretchDIBits((HDC) dc, dst[0], dst[1], dst[2]-dst[0], dst[3]-dst[1],
                      src[0], src[1], src[2]-src[0], src[3]-src[1], dib->bits,
                      dib->info, DIB_RGB_COLORS, SRCCOPY);
    } else {
        /* stretchblt (displays) */
        if (dib->palette != 0)
            SelectPalette((HDC) dc, dib->palette, FALSE);
        StretchBlt((HDC) dc, dst[0], dst[1], dst[2]-dst[0], dst[3]-dst[1],
                   dib->dc, src[0], src[1], src[2]-src[0], src[3]-src[1],
                   SRCCOPY);
    }
}

int
ImagingQueryPaletteDIB(ImagingDIB dib, int dc)
{
    /* Install bitmap palette */

    int n;

    if (dib->palette != 0) {

	/* Realize associated palette */
	HPALETTE now = SelectPalette((HDC) dc, dib->palette, FALSE);
	n = RealizePalette((HDC) dc);

	/* Restore palette */
	SelectPalette((HDC) dc, now, FALSE);

    } else
	n = 0;

    return n; /* number of colours that was changed */
}

void
ImagingDeleteDIB(ImagingDIB dib)
{
    /* Clean up */

    if (dib->palette)
	DeleteObject(dib->palette);
    if (dib->bitmap) {
        SelectObject(dib->dc, dib->old_bitmap);
	DeleteObject(dib->bitmap);
    }
    if (dib->dc)
	DeleteDC(dib->dc);
    free(dib->info);
}

#endif /* _WIN32 */
