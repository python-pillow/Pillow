/*
 * The Python Imaging Library.
 *
 * Decoder for the FITS tiled-image RICE_1 integer compression format.
 * See https://fits.gsfc.nasa.gov/registry/tilecompression.html
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"
#include "FitsRice.h"

/* Retain partial fields when a feed ends, without reading beyond this tile. */
static int
read_bits(
    FITSRICESTATE *context, UINT8 **ptr, const UINT8 *end, int count, UINT32 *value
) {
    while (context->bitcount < count) {
        if (*ptr == end || context->remaining == 0) {
            return 0;
        }
        context->bitbuffer = (context->bitbuffer << 8) | *(*ptr)++;
        context->bitcount += 8;
        context->remaining--;
    }
    context->bitcount -= count;
    *value = (UINT32)(context->bitbuffer >> context->bitcount);
    context->bitbuffer &= (UINT64_C(1) << context->bitcount) - 1;
    return 1;
}

int
ImagingFitsRiceDecode(
    Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes
) {
    enum { INITIAL, BLOCK, UNARY, REMAINDER, DIRECT, OUTPUT, DONE };
    FITSRICESTATE *context = state->context;
    UINT8 *ptr = buf;
    const UINT8 *end = buf + (bytes > INT_MAX ? INT_MAX : bytes);
    UINT32 value;

    for (;;) {
        switch (state->state) {
            case INITIAL:
                if (!read_bits(context, &ptr, end, 8 * context->bytepix, &value)) {
                    goto incomplete;
                }
                /* The first sample is also represented by a difference in block 0. */
                context->lastpix = value;
                state->y = state->ysize - 1;
                state->state = BLOCK;
                break;

            case BLOCK:
                if (!read_bits(context, &ptr, end, context->fsbits, &value)) {
                    goto incomplete;
                }
                if (value > (UINT32)context->fsmax + 1) {
                    state->errcode = IMAGING_CODEC_BROKEN;
                    return -1;
                }
                context->fs = (int)value - 1;
                context->blockleft = context->blocksize;
                context->difference = 0;
                context->quotient = 0;
                state->state = context->fs < 0                 ? OUTPUT
                               : context->fs == context->fsmax ? DIRECT
                                                               : UNARY;
                break;

            case UNARY:
                if (!read_bits(context, &ptr, end, 1, &value)) {
                    goto incomplete;
                }
                if (value) {
                    state->state = REMAINDER;
                } else {
                    if (context->quotient == (context->mask >> context->fs)) {
                        state->errcode = IMAGING_CODEC_BROKEN;
                        return -1;
                    }
                    context->quotient++;
                }
                break;

            case REMAINDER:
                if (!read_bits(context, &ptr, end, context->fs, &value)) {
                    goto incomplete;
                }
                context->difference = (context->quotient << context->fs) | value;
                state->state = OUTPUT;
                break;

            case DIRECT:
                if (!read_bits(context, &ptr, end, 8 * context->bytepix, &value)) {
                    goto incomplete;
                }
                context->difference = value;
                state->state = OUTPUT;
                break;

            case OUTPUT:
                /* Undo mapping and differencing with unsigned modular arithmetic. */
                value = (context->difference >> 1) ^ (0U - (context->difference & 1U));
                context->lastpix = (context->lastpix + value) & context->mask;
                for (int i = 0; i < context->output_bytes; i++) {
                    state->buffer[state->x * context->output_bytes + i] =
                        (UINT8)(context->lastpix >>
                                (8 * (context->output_bytes - i - 1)));
                }
                if (++state->x == state->xsize) {
                    state->shuffle(
                        (UINT8 *)im->image[state->y + state->yoff] +
                            state->xoff * im->pixelsize,
                        state->buffer,
                        state->xsize
                    );
                    state->x = 0;
                    if (--state->y < 0) {
                        state->state = DONE;
                        return -1;
                    }
                }
                context->quotient = 0;
                if (--context->blockleft == 0) {
                    state->state = BLOCK;
                } else {
                    state->state = context->fs < 0                 ? OUTPUT
                                   : context->fs == context->fsmax ? DIRECT
                                                                   : UNARY;
                }
                break;

            case DONE:
                return -1;
        }
    }

incomplete:
    if (context->remaining == 0) {
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }
    return (int)(ptr - buf);
}
