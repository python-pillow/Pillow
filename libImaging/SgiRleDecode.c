/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for Sgi RLE data.
 *
 * history:
 * 2017-07-20 mb    created
 *
 * Copyright (c) Mickael Bonfill 2017.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"
#include "stdio.h"

#define SGI_HEAD_LEN 512

static UINT32 getlong(UINT8 *buf)
{
    return (UINT32)(buf[0]<<24)+(buf[1]<<16)+(buf[2]<<8)+(buf[3]<<0);
}

static void expandrow(UINT8* optr,UINT8* iptr, int ooffset, int ioffset)
{
    UINT8 pixel, count;

    optr += ooffset;
    iptr += ioffset;
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
    UINT8 *ptr, *scanline;
    UINT32 *starttab, *lengthtab;
    UINT32 rleoffset, rlelength;
    int zsize, tablen, rowno, channo;

    /* "working copy" of buffer pointer */
    ptr = buf;

    /* get the channels count */
    zsize = im->bands;

    /* initialization */
    if (state->state == 0) {

        /* check image orientation */
        if (state->ystep < 0) {
            state->y = state->ysize-1;
            state->ystep = -1;
        } else {
            state->ystep = 1;
            state->y = 0;
        }

        state->state = 1;
      
    }

    /* allocate memory for compressed and uncompressed rows */
    scanline = (UINT8*)malloc(sizeof(UINT8) * state->xsize);

    /* allocate memory for rle tabs */
    tablen = state->ysize * zsize * sizeof(UINT32);

    starttab = (UINT32*)malloc(tablen);
    lengthtab = (UINT32*)malloc(tablen);


    /* get RLE offset and length tabs  */
    int i;
    for (i = 0; i < state->ysize * zsize; i++) {
        starttab[i] = getlong(&ptr[i * 4]);
    }
    for (i = 0; i < state->ysize * zsize; i++) {
        lengthtab[i] = getlong(&ptr[tablen + i * 4]);
    }

    /* get scanlines informations */
    for (rowno = 0; rowno < state->ysize; ++rowno) {

        for (channo = 0; channo < zsize; ++channo) {

            rleoffset = starttab[rowno + channo * state->ysize];
            rlelength = lengthtab[rowno + channo * state->ysize];

            /* 
             * we also need to substract the file header and RLE tabs length
             * from the offset
             */
            rleoffset -= SGI_HEAD_LEN;

            /* decompress raw data */
            expandrow(scanline, ptr, 0, rleoffset);

            /* populate the state buffer */
            for (state->x = 0; state->x < sizeof(*scanline) * state->xsize; state->x += 1) {
                state->buffer[state->x * zsize + channo] = (UINT8)(scanline[state->x]);
            }

        }

        /* Unpack the full line stored in the state buffer */
        state->shuffle((UINT8*) im->image[state->y + state->yoff] +
                state->xoff * im->pixelsize, state->buffer,
                state->xsize);

        state->y += state->ystep;
    }

    free(scanline);    
    free(starttab);
    free(lengthtab);

    return -1; /* end of file (errcode=0) */
}