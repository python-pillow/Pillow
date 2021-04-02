/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for Xbm data
 *
 * history:
 * 96-11-01 fl created
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

int
ImagingXbmEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    const char *hex = "0123456789abcdef";

    UINT8 *ptr = buf;
    int i, n;

    if (!state->state) {
        /* 8 pixels are stored in no more than 6 bytes */
        state->bytes = 6 * (state->xsize + 7) / 8;

        state->state = 1;
    }

    if (bytes < state->bytes) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return 0;
    }

    ptr = buf;

    while (bytes >= state->bytes) {
        state->shuffle(
            state->buffer,
            (UINT8 *)im->image[state->y + state->yoff] + state->xoff * im->pixelsize,
            state->xsize);

        if (state->y < state->ysize - 1) {
            /* any line but the last */
            for (n = 0; n < state->xsize; n += 8) {
                i = state->buffer[n / 8];

                *ptr++ = '0';
                *ptr++ = 'x';
                *ptr++ = hex[(i >> 4) & 15];
                *ptr++ = hex[i & 15];
                *ptr++ = ',';
                bytes -= 5;

                if (++state->count >= 79 / 5) {
                    *ptr++ = '\n';
                    bytes--;
                    state->count = 0;
                }
            }

            state->y++;

        } else {
            /* last line */
            for (n = 0; n < state->xsize; n += 8) {
                i = state->buffer[n / 8];

                *ptr++ = '0';
                *ptr++ = 'x';
                *ptr++ = hex[(i >> 4) & 15];
                *ptr++ = hex[i & 15];

                if (n < state->xsize - 8) {
                    *ptr++ = ',';
                    if (++state->count >= 79 / 5) {
                        *ptr++ = '\n';
                        bytes--;
                        state->count = 0;
                    }
                } else {
                    *ptr++ = '\n';
                }

                bytes -= 5;
            }

            state->errcode = IMAGING_CODEC_END;
            break;
        }
    }

    return ptr - buf;
}
