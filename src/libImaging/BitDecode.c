/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for packed bitfields (converts to floating point)
 *
 * history:
 *	97-05-31 fl	created (much more than originally intended)
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include "Bit.h"


int
ImagingBitDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    BITSTATE* bitstate = state->context;
    UINT8* ptr;

    if (state->state == 0) {

	/* Initialize context variables */

        /* this decoder only works for float32 image buffers */
        if (im->type != IMAGING_TYPE_FLOAT32) {
	    state->errcode = IMAGING_CODEC_CONFIG;
	    return -1;
        }

        /* sanity check */
        if (bitstate->bits < 1 || bitstate->bits >= 32) {
	    state->errcode = IMAGING_CODEC_CONFIG;
	    return -1;
        }

        bitstate->mask = (1<<bitstate->bits)-1;

        if (bitstate->sign)
            bitstate->signmask = (1<<(bitstate->bits-1));

	/* check image orientation */
	if (state->ystep < 0) {
	    state->y = state->ysize-1;
	    state->ystep = -1;
	} else
	    state->ystep = 1;

	state->state = 1;

    }

    ptr = buf;

    while (bytes > 0) {

        UINT8 byte = *ptr;

        ptr++;
        bytes--;

        /* get a byte from the input stream and insert in the bit buffer */
        if (bitstate->fill&1)
            /* fill MSB first */
            bitstate->bitbuffer |= (unsigned long) byte << bitstate->bitcount;
        else
            /* fill LSB first */
            bitstate->bitbuffer = (bitstate->bitbuffer << 8) | byte;

        bitstate->bitcount += 8;

        while (bitstate->bitcount >= bitstate->bits) {

            /* get a pixel from the bit buffer */
            unsigned long data;
            FLOAT32 pixel;

            if (bitstate->fill&2) {
                /* store LSB first */
                data = bitstate->bitbuffer & bitstate->mask;
                if (bitstate->bitcount > 32)
                    /* bitbuffer overflow; restore it from last input byte */
                    bitstate->bitbuffer = byte >> (8 - (bitstate->bitcount -
                                                        bitstate->bits));
                else
                    bitstate->bitbuffer >>= bitstate->bits;
            } else
                /* store MSB first */
                data = (bitstate->bitbuffer >> (bitstate->bitcount -
                                                bitstate->bits))
                       & bitstate->mask;

            bitstate->bitcount -= bitstate->bits;

            if (bitstate->lutsize > 0) {
                /* map through lookup table */
                if (data <= 0)
                    pixel = bitstate->lut[0];
                else if (data >= bitstate->lutsize)
                    pixel = bitstate->lut[bitstate->lutsize-1];
                else
                    pixel = bitstate->lut[data];
            } else {
                /* convert */
                if (data & bitstate->signmask)
                    /* image memory contains signed data */
                    pixel = (FLOAT32) (INT32) (data | ~bitstate->mask);
                else
                    pixel = (FLOAT32) data;
            }

            *(FLOAT32*)(&im->image32[state->y][state->x]) = pixel;

            /* step forward */
	    if (++state->x >= state->xsize) {
                /* new line */
                state->y += state->ystep;
                if (state->y < 0 || state->y >= state->ysize) {
                    /* end of file (errcode = 0) */
                    return -1;
                }
                state->x = 0;
                /* reset bit buffer */
                if (bitstate->pad > 0)
                    bitstate->bitcount = 0;
            }
        }
    }

    return ptr - buf;
}
