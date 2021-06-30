/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for Sgi RLE data.
 *
 * history:
 * 2017-07-28 mb    fixed for images larger than 64KB
 * 2017-07-20 mb    created
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

static void
read4B(UINT32 *dest, UINT8 *buf) {
    *dest = (UINT32)((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
}

/*
   SgiRleDecoding is done in a single channel row oriented set of RLE chunks.

   * The file is arranged as
     - SGI Header
     - Rle Offset Table
     - Rle Length Table
     - Scanline Data

   * Each RLE atom is c->bpc bytes wide (1 or 2)

   * Each RLE Chunk is [specifier atom] [ 1 or n data atoms ]

   * Copy Atoms are a byte with the high bit set, and the low 7 are
     the number of bytes to copy from the source to the
     destination. e.g.

         CBBBBBBBB or 0CHLHLHLHLHLHL   (B=byte, H/L = Hi low bytes)

   * Run atoms do not have the high bit set, and the low 7 bits are
     the number of copies of the next atom to copy to the
     destination. e.g.:

         RB -> BBBBB or RHL -> HLHLHLHLHL

   The upshot of this is, there is no way to determine the required
   length of the input buffer from reloffset and rlelength without
   going through the data at that scan line.

   Furthermore, there's no requirement that individual scan lines
   pointed to from the rleoffset table are in any sort of order or
   used only once, or even disjoint. There's also no requirement that
   all of the data in the scan line area of the image file be used

 */
static int
expandrow(UINT8 *dest, UINT8 *src, int n, int z, int xsize, UINT8 *end_of_buffer) {
    /*
     * n here is the number of rlechunks
     * z is the number of channels, for calculating the interleave
     *   offset to go to RGBA style pixels
     * xsize is the row width
     * end_of_buffer is the address of the end of the input buffer
     */

    UINT8 pixel, count;
    int x = 0;

    for (; n > 0; n--) {
        if (src > end_of_buffer) {
            return -1;
        }
        pixel = *src++;
        if (n == 1 && pixel != 0) {
            return n;
        }
        count = pixel & RLE_MAX_RUN;
        if (!count) {
            return count;
        }
        if (x + count > xsize) {
            return -1;
        }
        x += count;
        if (pixel & RLE_COPY_FLAG) {
            if (src + count > end_of_buffer) {
                return -1;
            }
            while (count--) {
                *dest = *src++;
                dest += z;
            }

        } else {
            if (src > end_of_buffer) {
                return -1;
            }
            pixel = *src++;
            while (count--) {
                *dest = pixel;
                dest += z;
            }
        }
    }
    return 0;
}

static int
expandrow2(UINT8 *dest, const UINT8 *src, int n, int z, int xsize, UINT8 *end_of_buffer) {
    UINT8 pixel, count;
    int x = 0;

    for (; n > 0; n--) {
        if (src + 1 > end_of_buffer) {
            return -1;
        }
        pixel = src[1];
        src += 2;
        if (n == 1 && pixel != 0) {
            return n;
        }
        count = pixel & RLE_MAX_RUN;
        if (!count) {
            return count;
        }
        if (x + count > xsize) {
            return -1;
        }
        x += count;
        if (pixel & RLE_COPY_FLAG) {
            if (src + 2 * count > end_of_buffer) {
                return -1;
            }
            while (count--) {
                memcpy(dest, src, 2);
                src += 2;
                dest += z * 2;
            }
        } else {
            if (src + 2 > end_of_buffer) {
                return -1;
            }
            while (count--) {
                memcpy(dest, src, 2);
                dest += z * 2;
            }
            src += 2;
        }
    }
    return 0;
}

int
ImagingSgiRleDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    UINT8 *ptr;
    SGISTATE *c;
    int err = 0;
    int status;

    /* size check */
    if (im->xsize > INT_MAX / im->bands || im->ysize > INT_MAX / im->bands) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    /* Get all data from File descriptor */
    c = (SGISTATE *)state->context;
    _imaging_seek_pyFd(state->fd, 0L, SEEK_END);
    c->bufsize = _imaging_tell_pyFd(state->fd);
    c->bufsize -= SGI_HEADER_SIZE;

    c->tablen = im->bands * im->ysize;
    /* below, we populate the starttab and lentab into the bufsize,
       each with 4 bytes per element of tablen
       Check here before we allocate any memory
    */
    if (c->bufsize < 8 * c->tablen) {
        state->errcode = IMAGING_CODEC_OVERRUN;
        return -1;
    }

    ptr = malloc(sizeof(UINT8) * c->bufsize);
    if (!ptr) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }
    _imaging_seek_pyFd(state->fd, SGI_HEADER_SIZE, SEEK_SET);
    if (_imaging_read_pyFd(state->fd, (char *)ptr, c->bufsize) != c->bufsize) {
        state->errcode = IMAGING_CODEC_UNKNOWN;
        return -1;
    }


    /* decoder initialization */
    state->count = 0;
    state->y = 0;
    if (state->ystep < 0) {
        state->y = im->ysize - 1;
    } else {
        state->ystep = 1;
    }

    /* Allocate memory for RLE tables and rows */
    free(state->buffer);
    state->buffer = NULL;
    /* malloc overflow check above */
    state->buffer = calloc(im->xsize * im->bands, sizeof(UINT8) * 2);
    c->starttab = calloc(c->tablen, sizeof(UINT32));
    c->lengthtab = calloc(c->tablen, sizeof(UINT32));
    if (!state->buffer || !c->starttab || !c->lengthtab) {
        err = IMAGING_CODEC_MEMORY;
        goto sgi_finish_decode;
    }
    /* populate offsets table */
    for (c->tabindex = 0, c->bufindex = 0; c->tabindex < c->tablen;
         c->tabindex++, c->bufindex += 4) {
        read4B(&c->starttab[c->tabindex], &ptr[c->bufindex]);
    }
    /* populate lengths table */
    for (c->tabindex = 0, c->bufindex = c->tablen * sizeof(UINT32);
         c->tabindex < c->tablen;
         c->tabindex++, c->bufindex += 4) {
        read4B(&c->lengthtab[c->tabindex], &ptr[c->bufindex]);
    }

    /* read compressed rows */
    for (c->rowno = 0; c->rowno < im->ysize; c->rowno++, state->y += state->ystep) {
        for (c->channo = 0; c->channo < im->bands; c->channo++) {
            c->rleoffset = c->starttab[c->rowno + c->channo * im->ysize];
            c->rlelength = c->lengthtab[c->rowno + c->channo * im->ysize];

            // Check for underflow of rleoffset-SGI_HEADER_SIZE
            if (c->rleoffset < SGI_HEADER_SIZE) {
                state->errcode = IMAGING_CODEC_OVERRUN;
                goto sgi_finish_decode;
            }

            c->rleoffset -= SGI_HEADER_SIZE;

            /* row decompression */
            if (c->bpc == 1) {
                status = expandrow(
                    &state->buffer[c->channo],
                    &ptr[c->rleoffset],
                    c->rlelength,
                    im->bands,
                    im->xsize,
                    &ptr[c->bufsize-1]);
            } else {
                status = expandrow2(
                    &state->buffer[c->channo * 2],
                    &ptr[c->rleoffset],
                    c->rlelength,
                    im->bands,
                    im->xsize,
                    &ptr[c->bufsize-1]);
            }
            if (status == -1) {
                state->errcode = IMAGING_CODEC_OVERRUN;
                goto sgi_finish_decode;
            } else if (status == 1) {
                goto sgi_finish_decode;
            }

        }

        /* store decompressed data in image */
        state->shuffle((UINT8 *)im->image[state->y], state->buffer, im->xsize);
    }

sgi_finish_decode:;

    free(c->starttab);
    free(c->lengthtab);
    free(ptr);
    if (err != 0) {
        state->errcode = err;
        return -1;
    }
    return 0;
}
