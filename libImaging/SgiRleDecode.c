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
#include "Sgi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SGI_HEADER_SIZE 512
#define SGI_MAGIC 0x01DA
#define RLE_COPY_FLAG 0x80
#define RLE_MAX_RUN 0x7f

static void read4B(uint32_t* dest, UINT8* buf)
{
    *dest = (uint32_t)((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
}

static int expandrow(UINT8* dest, UINT8* src, int n)
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
                *dest++ = *src++;
            }
                
        }
        else {
            pixel = *src++;
            while (count--) {
                *dest++ = pixel;
            }
        }
        
    }
    return 0;
}

static int expandrow2(UINT16* dest, UINT16* src, int n)
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
                *dest++ = *src++;
            }
        }
        else {
            while (count--) {
                *dest++ = *src;
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
    SGISTATE *context;
    UINT8 *ptr;
    uint32_t rleoffset, rlelength;

    context = (SGISTATE*)state->context;
    // oldcount = context->bytescount;

    ptr = buf;

    switch (state->state)
    {
        case 0:
            /* decoder initialization */
            if (state->ystep < 0)
                state->y = im->ysize - 1;
            else 
                state->ystep = 1;

            context->tablen = im->ysize * im->bands;
            context->starttab = calloc(context->tablen, sizeof(uint32_t));
            context->lengthtab = calloc(context->tablen, sizeof(uint32_t));

            state->state++;
            break;
        case 1:
            /* read offsets table */
            for (; context->starttabidx < context->tablen; 
                context->starttabidx++, ptr+=4, bytes-=4) {

                /* check overflow */
                if (bytes < 4)
                    return ptr - buf;

                read4B(&context->starttab[context->starttabidx], ptr);
            }
            state->state++;
            break;
        case 2:
            /* read lengths table */
            for (; context->lengthtabidx < context->tablen; 
                context->lengthtabidx++, ptr+=4, bytes-=4) {

                /* check overflow */
                if (bytes < 4)
                    return ptr - buf;

                read4B(&context->lengthtab[context->lengthtabidx], ptr);
            }
            state->state++;
            break;
        case 3:
            /* rows decompression */
            for (; context->rowno < im->ysize * im->bands; 
                context->rowno++, state->y += state->ystep )
            {
                context->channo = (int)(context->rowno / im->ysize);
                rleoffset = context->starttab[context->rowno];
                rleoffset -= SGI_HEADER_SIZE;
                rlelength = context->lengthtab[context->rowno];

                /* check overflow */
                if (rlelength > bytes)
                    return ptr - buf;

                if (context->bpc == 1) {
                    if(expandrow(state->buffer, ptr, rlelength)) {
                        /* err: compressed row doesn't finish with 0 */
                        state->errcode = IMAGING_CODEC_OVERRUN;
                        return ptr - buf;
                    }
                        
                }
                else {
                    if(expandrow2((UINT16*)state->buffer, (UINT16*)ptr, rlelength)) {
                        /* err: compressed row doesn't finish with 0 */
                        state->errcode = IMAGING_CODEC_OVERRUN;
                        return ptr - buf;
                    }
                }

                /* reset index */
                if (state->y == -1)
                    state->y = im->ysize - 1;
                if (state->y == im->ysize)
                    state->y = 0;

                /* set image data */
                for (state->x = context->channo; state->x < im->xsize * im->pixelsize; state->x+=im->pixelsize)
                    ((UINT8*)im->image[state->y])[state->x] = *state->buffer++;

                state->buffer -= im->xsize;

                bytes -= rlelength;
                ptr += rlelength;
            }
            return -1; /* no error */
        default:
            break;
    }
  
    return ptr - buf;
}

int ImagingSgiRleDecodeCleanup(ImagingCodecState state) {

    // SGISTATE *context;
    // context = (SGISTATE*)state->context;

    // free(context->starttab);
    // free(context->lengthtab);
    // // free(context);

    return -1;
}