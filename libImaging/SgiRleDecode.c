/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for Sgi RLE data.
 *
 * history:
 * 2017-07-28 mb    fixed for images larger than 64KB
 * 2017-07-20 mb	created
 *
 * Copyright (c) Mickael Bonfill 2017.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"
#include "Sgi.h"

#define SGI_HEADER_SIZE 512
#define RLE_COPY_FLAG 0x80
#define RLE_MAX_RUN 0x7f

static void read4B(uint32_t* dest, UINT8* buf)
{
    *dest = (uint32_t)((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
}

static int expandrow(UINT8* dest, UINT8* src, int n, int z)
{
    UINT8 pixel, count;
    
    for (;n > 0; n--)
    {
        pixel = *src++;
        if (n == 1 && pixel != 0)
            return n;
        count = pixel & RLE_MAX_RUN;
        if (!count)
            return count;
        if (pixel & RLE_COPY_FLAG) {
            while(count--) {
                *dest = *src++;
                dest += z;
            }
                
        }
        else {
            pixel = *src++;
            while (count--) {
                *dest = pixel;
                dest += z;
            }
        }
        
    }
    return 0;
}

static int expandrow2(UINT16* dest, UINT16* src, int n, int z)
{
    UINT8 pixel, count;

   
    for (;n > 0; n--)
    {
        pixel = ((UINT8*)src)[1];
        ++src;
        if (n == 1 && pixel != 0)
            return n;
        count = pixel & RLE_MAX_RUN;
        if (!count)
            return count;
        if (pixel & RLE_COPY_FLAG) {
            while(count--) {
                *dest = *src++;
                dest += z;
            }
        }
        else {
            while (count--) {
                *dest = *src;
                dest += z;
            }
            ++src;
        }
    }
    return 0;
}


int
ImagingSgiRleDecode(Imaging im, ImagingCodecState state,
		    UINT8* buf, int bytes)
{
    UINT8 *ptr;
    SGISTATE *c;

    /* Get all data from File descriptor */    
    c = (SGISTATE*)state->context;
    _imaging_seek_pyFd(state->fd, 0L, SEEK_END);
    c->bufsize = _imaging_tell_pyFd(state->fd);
    c->bufsize -= SGI_HEADER_SIZE;
    ptr = malloc(sizeof(UINT8) * c->bufsize);
    _imaging_seek_pyFd(state->fd, SGI_HEADER_SIZE, SEEK_SET);
    _imaging_read_pyFd(state->fd, (char*)ptr, c->bufsize);


    /* decoder initialization */
    state->count = 0;
    state->y = 0;
    if (state->ystep < 0)
        state->y = im->ysize - 1;
    else
        state->ystep = 1;

    /* Allocate memory for RLE tables and rows */
    free(state->buffer);
    state->buffer = malloc(sizeof(UINT8) * 2 * im->xsize * im->bands);
    c->tablen = im->bands * im->ysize;
    c->starttab = calloc(c->tablen, sizeof(uint32_t));
    c->lengthtab = calloc(c->tablen, sizeof(uint32_t));

    /* populate offsets table */
    for (c->tabindex = 0, c->bufindex = 0; c->tabindex < c->tablen; c->tabindex++, c->bufindex+=4)
        read4B(&c->starttab[c->tabindex], &ptr[c->bufindex]);
    /* populate lengths table */
    for (c->tabindex = 0, c->bufindex = c->tablen * sizeof(uint32_t); c->tabindex < c->tablen; c->tabindex++, c->bufindex+=4)
        read4B(&c->lengthtab[c->tabindex], &ptr[c->bufindex]);

    state->count += c->tablen * sizeof(uint32_t) * 2;

    /* read compressed rows */
    for (c->rowno = 0; c->rowno < im->ysize; c->rowno++, state->y += state->ystep)
    {
        for (c->channo = 0; c->channo < im->bands; c->channo++)
        {
            c->rleoffset = c->starttab[c->rowno + c->channo * im->ysize];
            c->rlelength = c->lengthtab[c->rowno + c->channo * im->ysize];
            c->rleoffset -= SGI_HEADER_SIZE;
            
            /* row decompression */
            if (c->bpc ==1) {
                if(expandrow(&state->buffer[c->channo], &ptr[c->rleoffset], c->rlelength, im->bands))
                    goto sgi_finish_decode;
            }
            else {
                if(expandrow2((UINT16*)&state->buffer[c->channo * 2], (UINT16*)&ptr[c->rleoffset], c->rlelength, im->bands))
                    goto sgi_finish_decode;
            }
            
            state->count += c->rlelength;
        }
        
        /* store decompressed data in image */
        state->shuffle((UINT8*)im->image[state->y], state->buffer, im->xsize);
        
    }

    c->bufsize++;

sgi_finish_decode: ;
    
    free(c->starttab);
    free(c->lengthtab);
    free(ptr);
   
    return state->count - c->bufsize;
}
