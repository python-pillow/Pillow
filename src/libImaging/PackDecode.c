/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for PackBits image data.
 *
 * history:
 * 96-04-19 fl Created
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

int
ImagingPackbitsDecode(
    Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    UINT8 n;
    UINT8 *ptr;
    int i;

    ptr = buf;

    for (;;) {
        if (bytes < 1) {
            return ptr - buf;
        }

        if (ptr[0] & 0x80) {
            if (ptr[0] == 0x80) {
                /* Nop */
                ptr++;
                bytes--;
                continue;
            }

            /* Run */
            if (bytes < 2) {
                return ptr - buf;
            }

            for (n = 257 - ptr[0]; n > 0; n--) {
                if (state->x >= state->bytes) {
                    /* state->errcode = IMAGING_CODEC_OVERRUN; */
                    break;
                }
                state->buffer[state->x++] = ptr[1];
            }

            ptr += 2;
            bytes -= 2;

        } else {
            /* Literal */
            n = ptr[0] + 2;

            if (bytes < n) {
                return ptr - buf;
            }

            for (i = 1; i < n; i++) {
                if (state->x >= state->bytes) {
                    /* state->errcode = IMAGING_CODEC_OVERRUN; */
                    break;
                }
                state->buffer[state->x++] = ptr[i];
            }

            ptr += n;
            bytes -= n;
        }

        if (state->x >= state->bytes) {
            /* Got a full line, unpack it */
            state->shuffle(
                (UINT8 *)im->image[state->y + state->yoff] +
                    state->xoff * im->pixelsize,
                state->buffer,
                state->xsize);

            state->x = 0;

            if (++state->y >= state->ysize) {
                /* End of file (errcode = 0) */
                return -1;
            }
        }
    }
}
