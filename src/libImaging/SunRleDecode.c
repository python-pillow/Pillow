/*
 * THIS IS WORK IN PROGRESS
 *
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for SUN RLE data.
 *
 * history:
 *      97-01-04 fl     Created
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

static int
sun_rle_next_row(Imaging im, ImagingCodecState state) {
    state->shuffle(
        (UINT8 *)im->image[state->y + state->yoff] + state->xoff * im->pixelsize,
        state->buffer,
        state->xsize
    );
    state->x = 0;
    if (++state->y >= state->ysize) {
        return -1;
    }
    return 0;
}

int
ImagingSunRleDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    int n;
    int stride;
    UINT8 *ptr = buf;
    UINT8 value;

    if (state->bytes <= 0) {
        return 0;
    }

    /* Stored scanlines are padded to a multiple of 16 bits and the RLE stream
       encodes the padding bytes too, so rows advance on the padded stride while
       only the first state->bytes bytes are image data. */
    stride = state->bytes + (state->bytes & 1);

    for (;;) {
        if (bytes < 1) {
            return ptr - buf;
        }

        if (ptr[0] == 0x80) {
            if (bytes < 2) {
                break;
            }

            n = ptr[1];
            if (n == 0) {
                /* Literal 0x80 (2 bytes) */
                value = 0x80;
                n = 1;
                ptr += 2;
                bytes -= 2;
            } else {
                /* Run (3 bytes): output n+1 pixels of the value */
                if (bytes < 3) {
                    break;
                }
                n += 1;
                value = ptr[2];
                ptr += 3;
                bytes -= 3;
            }

            /* Runs may cross scanlines, including the padding bytes. */
            while (n > 0) {
                int take = stride - state->x;
                if (take > n) {
                    take = n;
                }
                if (state->x < state->bytes) {
                    int writable = state->bytes - state->x;
                    if (writable > take) {
                        writable = take;
                    }
                    memset(state->buffer + state->x, value, writable);
                }
                state->x += take;
                n -= take;
                if (state->x >= stride) {
                    if (sun_rle_next_row(im, state) < 0) {
                        return -1;
                    }
                }
            }
        } else {
            /* Literal byte */
            if (state->x < state->bytes) {
                state->buffer[state->x] = ptr[0];
            }
            state->x += 1;
            ptr += 1;
            bytes -= 1;
            if (state->x >= stride) {
                if (sun_rle_next_row(im, state) < 0) {
                    return -1;
                }
            }
        }
    }

    return ptr - buf;
}
