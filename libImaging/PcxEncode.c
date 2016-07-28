/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for PCX data
 *
 * history:
 * 99-02-07 fl  created
 *
 * Copyright (c) Fredrik Lundh 1999.
 * Copyright (c) Secret Labs AB 1999.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

enum { INIT, FETCH, ENCODE };

/* we're reusing "ystep" to store the last value */
#define LAST ystep

int
ImagingPcxEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* ptr;
    int this;
    int bytes_per_line = 0;
    int padding = 0;
    int stride = 0;
    int bpp = 0;
    int planes = 1;
    int i;

    ptr = buf;

    if (!state->state) {
        /* sanity check */
        if (state->xsize <= 0 || state->ysize <= 0) {
            state->errcode = IMAGING_CODEC_END;
            return 0;
        }
        state->state = FETCH;
    }

    bpp = state->bits;
    if (state->bits == 24){
        planes = 3;
        bpp = 8;
    }

    bytes_per_line = (state->xsize*bpp + 7) / 8;
    /* The stride here needs to be kept in sync with the version in
       PcxImagePlugin.py. If it's not, the header and the body of the
       image will be out of sync and bad things will happen on decode.
    */
    stride = bytes_per_line + (bytes_per_line % 2);

    padding = stride - bytes_per_line;


    for (;;) {

        switch (state->state) {
        case FETCH:

            /* get a line of data */
            if (state->y >= state->ysize) {
                state->errcode = IMAGING_CODEC_END;
                return ptr - buf;
            }

            state->shuffle(state->buffer,
                           (UINT8*) im->image[state->y + state->yoff] +
                           state->xoff * im->pixelsize, state->xsize);

            state->y += 1;

            state->count = 1;
            state->LAST = state->buffer[0];

            state->x = 1;

            state->state = ENCODE;
            /* fall through */

        case ENCODE:
            /* compress this line */

            /* when we arrive here, "count" contains the number of
               bytes having the value of "LAST" that we've already
               seen */
            do {
                /* If we're encoding an odd width file, and we've
                   got more than one plane, we need to pad each
                   color row with padding bytes at the end. Since
                   The pixels are stored RRRRRGGGGGBBBBB, so we need
                   to have the padding be RRRRRPGGGGGPBBBBBP. Hence
                   the double loop
                */
                while (state->x % bytes_per_line) {

                    if (state->count == 63) {
                        /* this run is full; flush it */
                        if (bytes < 2) {
                            return ptr - buf;
                        }
                        ptr[0] = 0xff;
                        ptr[1] = state->LAST;
                        ptr += 2;
                        bytes -= 2;

                        state->count = 0;
                    }

                    this = state->buffer[state->x];

                    if (this == state->LAST) {
                        /* extend the current run */
                        state->x += 1;
                        state->count += 1;

                    } else {
                        /* start a new run */
                        if (state->count == 1 && (state->LAST < 0xc0)) {
                            if (bytes < 1) {
                                return ptr - buf;
                            }
                            ptr[0] = state->LAST;
                            ptr += 1;
                            bytes -= 1;
                        } else {
                            if (state->count > 0) {
                                if (bytes < 2) {
                                    return ptr - buf;
                                }
                                ptr[0] = 0xc0 | state->count;
                                ptr[1] = state->LAST;
                                ptr += 2;
                                bytes -= 2;
                            }
                        }

                        state->LAST = this;
                        state->count = 1;

                        state->x += 1;
                    }
                }

                /* end of line; flush the current run */
                if (state->count == 1 && (state->LAST < 0xc0)) {
                    if (bytes < 1 + padding) {
                        return ptr - buf;
                    }
                    ptr[0] = state->LAST;
                    ptr += 1;
                    bytes -= 1;
                } else {
                    if (state->count > 0) {
                        if (bytes < 2 + padding) {
                            return ptr - buf;
                        }
                        ptr[0] = 0xc0 | state->count;
                        ptr[1] = state->LAST;
                        ptr += 2;
                        bytes -= 2;
                    }
                }
                /* add the padding */
                for (i = 0; i < padding; i++) {
                    ptr[0] = 0;
                    ptr += 1;
                    bytes -= 1;
                }
                /* reset for the next color plane. */
                if (state->x < planes * bytes_per_line) {
                    state->count = 1;
                    state->LAST = state->buffer[state->x];
                    state->x += 1;
                }
            } while (state->x < planes * bytes_per_line);

            /* read next line */
            state->state = FETCH;
            break;
        }
    }
}

