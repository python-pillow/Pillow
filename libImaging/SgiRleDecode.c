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

static unsigned long getlong(UINT8 *buf)
{
	return (unsigned long)(buf[0]<<24)+(buf[1]<<16)+(buf[2]<<8)+(buf[3]<<0);
}

static void readlongtab(UINT8** buf, int n, unsigned long *tab)
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
	int n, depth;
    UINT8* ptr;

    ptr = buf;

    if (state->state == 0) {

	/* check image orientation */
	if (state->ystep < 0) {
	    state->y = state->ysize-1;
	    state->ystep = -1;
	} else
	    state->ystep = 1;

	state->state = 1;

    }

    /* get the channels count */
    int zsize = state->bits / state->count;

    /* allocate memory for the buffer used for full lines later */
    state->buffer = (UINT8*)malloc(sizeof(UINT8) * state->xsize * zsize);


    /* get RLE offset and length tabs  */
    unsigned long *starttab, *lengthtab;
    int tablen = state->ysize * zsize * sizeof(unsigned long);

    starttab = (unsigned long *)malloc(tablen);
    lengthtab = (unsigned long *)malloc(tablen);

    readlongtab(&ptr, state->ysize * zsize, starttab);
    readlongtab(&ptr, state->ysize * zsize, lengthtab);

    /* get scanlines informations */
    for (int rowno = 0; rowno < state->ysize; ++rowno) {

    	for (int channo = 0; channo < zsize; ++channo) {

    		unsigned long rleoffset = starttab[rowno + channo * state->ysize];

            /* 
             * we also need to substract the file header and RLE tabs length
             * from the offset
             */
            rleoffset -= 512;
            rleoffset -= tablen;

    		unsigned long rlelength = lengthtab[rowno + channo * state->ysize];

    		UINT8* rledata;
    		rledata = (UINT8*)malloc(sizeof(UINT8) * rlelength);
    		memcpy(rledata, &ptr[rleoffset], rlelength * sizeof(UINT8));
    		UINT8* scanline;
    		scanline = (UINT8*)malloc(sizeof(UINT8) * state->xsize);

            /* decompress raw data */
    		expandrow(scanline, rledata, 0);

            /* populate the state buffer */
    		for (int x = 0; x < state->xsize; ++x) {
   				state->buffer[x * zsize + channo] = scanline[x];
    		}

    		free(rledata);
    		free(scanline);
    	}

        /* Unpack the full line stored in the state buffer */
        state->shuffle((UINT8*) im->image[state->y + state->yoff] +
                state->xoff * im->pixelsize, state->buffer,
                state->xsize);

    	state->y += state->ystep;
    }
    
    free(starttab);
    free(lengthtab);

    return -1;
}