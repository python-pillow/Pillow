/*
 * THIS IS WORK IN PROGRESS
 *
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for SUN RLE data.
 *
 * history:
 *	97-01-04 fl	Created
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"


int
ImagingSunRleDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    int n;
    UINT8* ptr;

    ptr = buf;

    for (;;) {

	if (bytes < 1)
	    return ptr - buf;

	if (ptr[0] == 0x80) {

	    if (bytes < 2)
		break;

	    n = ptr[1];

	    if (n == 0) {

		/* Literal 0x80 (2 bytes) */
		n = 1;

		state->buffer[state->x] = 0x80;

		ptr += 2;
		bytes -= 2;

	    } else {

		/* Run (3 bytes) */
		if (bytes < 3)
		    break;

		if (state->x + n > state->bytes) {
		    /* FIXME: is this correct? */
		    state->errcode = IMAGING_CODEC_OVERRUN;
		    return -1;
		}

		memset(state->buffer + state->x, ptr[2], n);
		
		ptr += 3;
		bytes -= 3;

	    }

	} else {

	    /* Literal (1+n bytes block) */
	    n = ptr[0];

	    if (bytes < 1 + n)
		break;

	    if (state->x + n > state->bytes) {
		/* FIXME: is this correct? */
		state->errcode = IMAGING_CODEC_OVERRUN;
		return -1;
	    }

	    memcpy(state->buffer + state->x, ptr + 1, n);

	    ptr += 1 + n;
	    bytes -= 1 + n;

	}

	state->x += n;

	if (state->x >= state->bytes) {

	    /* Got a full line, unpack it */
	    state->shuffle((UINT8*) im->image[state->y + state->yoff] +
			   state->xoff * im->pixelsize, state->buffer,
			   state->xsize);

	    state->x = 0;

	    if (++state->y >= state->ysize) {
		/* End of file (errcode = 0) */
		return -1;
	    }
	}

    }

    return ptr - buf;
}
