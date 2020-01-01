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

static void read4B(UINT32* dest, UINT8* buf)
{
    *dest = (UINT32)((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
}

static int expandrow(UINT8* dest, UINT8* src, int n, int z, int xsize)
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
        if (count > xsize) {
            return -1;
        }
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

static int expandrow2(UINT8* dest, const UINT8* src, int n, int z, int xsize)
{
    UINT8 pixel, count;


    for (;n > 0; n--)
    {
        pixel = src[1];
        src+=2;
        if (n == 1 && pixel != 0)
            return n;
        count = pixel & RLE_MAX_RUN;
        if (!count)
            return count;
        if (count > xsize) {
            return -1;
        }
        if (pixel & RLE_COPY_FLAG) {
            while(count--) {
                memcpy(dest, src, 2);
                src += 2;
                dest += z * 2;
            }
        }
        else {
            while (count--) {
                memcpy(dest, src, 2);
                dest += z * 2;
            }
            src+=2;
        }
    }
    return 0;
}


int
ImagingSgiRleDecode(Imaging im, ImagingCodecState state,
		    UINT8* buf, Py_ssize_t bytes)
{
    UINT8 *ptr;
    SGISTATE *c;
    int err = 0;
    int status;

    /* Get all data from File descriptor */
    c = (SGISTATE*)state->context;
    _imaging_seek_pyFd(state->fd, 0L, SEEK_END);
    c->bufsize = _imaging_tell_pyFd(state->fd);
    c->bufsize -= SGI_HEADER_SIZE;
    ptr = malloc(sizeof(UINT8) * c->bufsize);
    if (!ptr) {
        return IMAGING_CODEC_MEMORY;
    }
    _imaging_seek_pyFd(state->fd, SGI_HEADER_SIZE, SEEK_SET);
    _imaging_read_pyFd(state->fd, (char*)ptr, c->bufsize);


    /* decoder initialization */
    state->count = 0;
    state->y = 0;
    if (state->ystep < 0) {
        state->y = im->ysize - 1;
    } else {
        state->ystep = 1;
    }

    if (im->xsize > INT_MAX / im->bands ||
        im->ysize > INT_MAX / im->bands) {
        err = IMAGING_CODEC_MEMORY;
        goto sgi_finish_decode;
    }

    /* Allocate memory for RLE tables and rows */
    free(state->buffer);
    state->buffer = NULL;
    /* malloc overflow check above */
    state->buffer = calloc(im->xsize * im->bands, sizeof(UINT8) * 2);
    c->tablen = im->bands * im->ysize;
    c->starttab = calloc(c->tablen, sizeof(UINT32));
    c->lengthtab = calloc(c->tablen, sizeof(UINT32));
    if (!state->buffer ||
        !c->starttab ||
        !c->lengthtab) {
        err = IMAGING_CODEC_MEMORY;
        goto sgi_finish_decode;
    }
    /* populate offsets table */
    for (c->tabindex = 0, c->bufindex = 0; c->tabindex < c->tablen; c->tabindex++, c->bufindex+=4)
        read4B(&c->starttab[c->tabindex], &ptr[c->bufindex]);
    /* populate lengths table */
    for (c->tabindex = 0, c->bufindex = c->tablen * sizeof(UINT32); c->tabindex < c->tablen; c->tabindex++, c->bufindex+=4)
        read4B(&c->lengthtab[c->tabindex], &ptr[c->bufindex]);

    state->count += c->tablen * sizeof(UINT32) * 2;

    /* read compressed rows */
    for (c->rowno = 0; c->rowno < im->ysize; c->rowno++, state->y += state->ystep)
    {
        for (c->channo = 0; c->channo < im->bands; c->channo++)
        {
            c->rleoffset = c->starttab[c->rowno + c->channo * im->ysize];
            c->rlelength = c->lengthtab[c->rowno + c->channo * im->ysize];
            c->rleoffset -= SGI_HEADER_SIZE;

            if (c->rleoffset + c->rlelength > c->bufsize) {
                state->errcode = IMAGING_CODEC_OVERRUN;
                return -1;
            }

            /* row decompression */
            if (c->bpc ==1) {
                status = expandrow(&state->buffer[c->channo], &ptr[c->rleoffset], c->rlelength, im->bands, im->xsize);
            }
            else {
                status = expandrow2(&state->buffer[c->channo * 2], &ptr[c->rleoffset], c->rlelength, im->bands, im->xsize);
            }
            if (status == -1) {
                state->errcode = IMAGING_CODEC_OVERRUN;
                return -1;
            } else if (status == 1) {
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
    if (err != 0){
        return err;
    }
    return state->count - c->bufsize;
}
