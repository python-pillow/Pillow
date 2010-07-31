/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for PCX data
 *
 * history:
 * 99-02-07 fl	created
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

    ptr = buf;

    if (!state->state) {

        /* sanity check */
        if (state->xsize <= 0 || state->ysize <= 0) {
            state->errcode = IMAGING_CODEC_END;
            return 0;
        }

	state->bytes = (state->xsize*state->bits + 7) / 8;
        state->state = FETCH;

    }

    for (;;)

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

            state->y++;

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

            while (state->x < state->bytes) {

                if (state->count == 63) {

                    /* this run is full; flush it */
                    if (bytes < 2)
                        return ptr - buf;
                    *ptr++ = 0xff;
                    *ptr++ = state->LAST;
                    bytes -= 2;

                    state->count = 0;

                }

                this = state->buffer[state->x];

                if (this == state->LAST) {

                    /* extend the current run */
                    state->x++;
                    state->count++;

                } else {

                    /* start a new run */
                    if (state->count == 1 && (state->LAST < 0xc0)) {
                        if (bytes < 1)
                            return ptr - buf;
                        *ptr++ = state->LAST;
                        bytes--;
                    } else {
                        if (state->count > 0) {
                            if (bytes < 2)
                                return ptr - buf;
                            *ptr++ = 0xc0 | state->count;
                            *ptr++ = state->LAST;
                            bytes -= 2;
                        }
                    }

                    state->LAST = this;
                    state->count = 1;

                    state->x++;

                }
            }

            /* end of line; flush the current run */
            if (state->count == 1 && (state->LAST < 0xc0)) {
                if (bytes < 1)
                    return ptr - buf;
                *ptr++ = state->LAST;
                bytes--;
            } else {
                if (state->count > 0) {
                    if (bytes < 2)
                        return ptr - buf;
                    *ptr++ = 0xc0 | state->count;
                    *ptr++ = state->LAST;
                    bytes -= 2;
                }
            }

            /* read next line */
            state->state = FETCH;
            break;

        }
}
