/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for PCX image data.
 *
 * history:
 * 95-09-14 fl Created
 *
 * Copyright (c) Fredrik Lundh 1995.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

int
ImagingPcxDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    UINT8 n;
    UINT8 *ptr;

    if ((state->xsize * state->bits + 7) / 8 > state->bytes) {
        state->errcode = IMAGING_CODEC_OVERRUN;
        return -1;
    }

    ptr = buf;

    for (;;) {
        if (bytes < 1) {
            return ptr - buf;
        }

        if ((*ptr & 0xC0) == 0xC0) {
            /* Run */
            if (bytes < 2) {
                return ptr - buf;
            }

            n = ptr[0] & 0x3F;

            while (n > 0) {
                if (state->x >= state->bytes) {
                    state->errcode = IMAGING_CODEC_OVERRUN;
                    break;
                }
                state->buffer[state->x++] = ptr[1];
                n--;
            }

            ptr += 2;
            bytes -= 2;

        } else {
            /* Literal */
            state->buffer[state->x++] = ptr[0];
            ptr++;
            bytes--;
        }

        if (state->x >= state->bytes) {
            int bands;
            int xsize = 0;
            int stride = 0;
            if (state->bits == 2 || state->bits == 4) {
                xsize = (state->xsize + 7) / 8;
                bands = state->bits;
                stride = state->bytes / state->bits;
            } else {
                xsize = state->xsize;
                bands = state->bytes / state->xsize;
                if (bands != 0) {
                    stride = state->bytes / bands;
                }
            }
            if (stride > xsize) {
                int i;
                for (i = 1; i < bands; i++) {  // note -- skipping first band
                    memmove(
                        &state->buffer[i * xsize], &state->buffer[i * stride], xsize
                    );
                }
            }
            /* Got a full line, unpack it */
            state->shuffle(
                (UINT8 *)im->image[state->y + state->yoff] +
                    state->xoff * im->pixelsize,
                state->buffer,
                state->xsize
            );

            state->x = 0;

            if (++state->y >= state->ysize) {
                /* End of file (errcode = 0) */
                return -1;
            }
        }
    }
}
