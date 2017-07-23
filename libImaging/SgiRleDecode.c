/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for Sgi RLE data.
 *
 * history:
 * 2017-07-20 mb	created
 *
 * Copyright (c) Mickael Bonfill 2017.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"
#include "stdio.h"

typedef unsigned long ULONG;

static ULONG getlong(UINT8 *buf)
{
	return (ULONG)(buf[0]<<24)+(buf[1]<<16)+(buf[2]<<8)+(buf[3]<<0);
}

static void readlongtab(UINT8** buf, int n, ULONG *tab)
{
	int i;
	for (i = 0; i < n; i++) {
        tab[i] = getlong(*buf);
        *buf += 4;
    }
}

static void expandrow(UINT8* optr,UINT8* iptr, int z)
{
	UINT8 pixel, count;

	optr += z;
	while(1) {
		pixel = *iptr++;
		if ( !(count = (pixel & 0x7f)) )
			return;
		if(pixel & 0x80) {
			while(count--) 
				*optr++ = *iptr++;
		} else {
			pixel = *iptr++;
			while(count--) 
				*optr++ = pixel;
		}
	}
}

int
ImagingSgiRleDecode(Imaging im, ImagingCodecState state,
		    UINT8* buf, int bytes)
{
    UINT8 *ptr, *rledata, *scanline;
    ULONG *starttab, *lengthtab;
    ULONG rleoffset, rlelength, prevrlelength;
    int zsize, tablen, rowno, channo, x;

    ptr = buf;

    /* get the channels count */
    zsize = im->bands;
    prevrlelength = (ULONG)state->xsize;

    if (state->state == 0) {

	/* check image orientation */
	if (state->ystep < 0) {
	    state->y = state->ysize-1;
	    state->ystep = -1;
	} else
	    state->ystep = 1;

    free(state->buffer);

    /* allocate memory for the buffer used for full lines later */
    state->buffer = (UINT8*)malloc(sizeof(UINT8) * state->xsize * zsize);

    /* allocate memory for compressed and uncompressed rows */
    rledata = (UINT8*)malloc(sizeof(UINT8) * state->xsize);
    scanline = (UINT8*)malloc(sizeof(UINT8) * state->xsize);

	state->state = 1;

    }

    /* get RLE offset and length tabs  */
    tablen = state->ysize * zsize * sizeof(ULONG);

    starttab = (ULONG*)malloc(tablen);
    lengthtab = (ULONG*)malloc(tablen);

    readlongtab(&ptr, state->ysize * zsize, starttab);
    readlongtab(&ptr, state->ysize * zsize, lengthtab);

    /* get scanlines informations */
    for (rowno = 0; rowno < state->ysize; ++rowno) {

    	for (channo = 0; channo < zsize; ++channo) {

    		rleoffset = starttab[rowno + channo * state->ysize];
            rlelength = lengthtab[rowno + channo * state->ysize];

            /* 
             * we also need to substract the file header and RLE tabs length
             * from the offset
             */
            rleoffset -= 512;
            rleoffset -= tablen;    		

            if (prevrlelength != rlelength)
                rledata = (UINT8*)realloc(rledata, sizeof(UINT8) * rlelength);

            prevrlelength = rlelength;

    		memcpy(rledata, &ptr[rleoffset], rlelength * sizeof(UINT8));

            /* decompress raw data */
    		expandrow(scanline, rledata, 0);

            /* populate the state buffer */
    		for (x = 0; x < state->xsize; ++x) {
   				state->buffer[x * zsize + channo] = scanline[x];
    		}

    	}

        /* Unpack the full line stored in the state buffer */
        state->shuffle((UINT8*) im->image[state->y + state->yoff] +
                state->xoff * im->pixelsize, state->buffer,
                state->xsize);

    	state->y += state->ystep;
    }

    free(rledata);
    free(scanline);    
    free(starttab);
    free(lengthtab);

    return -1; /* end of file (errcode=0) */
}