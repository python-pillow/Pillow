/*
 * The Python Imaging Library.
 * $Id$
 *
 * coder for raw data
 *
 * FIXME: This encoder will fail if the buffer is not large enough to
 * hold one full line of data.  There's a workaround for this problem
 * in ImageFile.py, but it should be solved here instead.
 *
 * history:
 * 96-04-30 fl created
 * 97-01-03 fl fixed padding
 *
 * Copyright (c) Fredrik Lundh 1996-97.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.  */

#include "Imaging.h"

int
ImagingRawEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    UINT8 *ptr;

    if (!state->state) {
        /* The "count" field holds the stride, if specified */
        if (state->count > 0 && state->count < state->bytes) {
            /* stride must not be less than real size */
            state->errcode = IMAGING_CODEC_CONFIG;
            return -1;
        }

        /* The "ystep" field specifies the orientation */
        if (state->ystep < 0) {
            state->y = state->ysize - 1;
            state->ystep = -1;
        } else {
            state->ystep = 1;
        }

        state->state = 1;
    }

    int row = state->count > 0 ? state->count : state->bytes;
    if (bytes < row) {
        state->errcode = IMAGING_CODEC_CONFIG;
        return 0;
    }

    ptr = buf;

    while (bytes >= row) {
        state->shuffle(
            ptr,
            (UINT8 *)im->image[state->y + state->yoff] + state->xoff * im->pixelsize,
            state->xsize
        );

        if (row > state->bytes) {
            /* zero-pad the buffer, if necessary */
            memset(ptr + state->bytes, 0, row - state->bytes);
        }

        ptr += row;
        bytes -= row;

        state->y += state->ystep;

        if (state->y < 0 || state->y >= state->ysize) {
            state->errcode = IMAGING_CODEC_END;
            break;
        }
    }

    return ptr - buf;
}
