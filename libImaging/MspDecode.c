/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for MSP version 2 data.
 *
 * history:
 *	97-01-03 fl	Created
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"


int
ImagingMspDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    int n;
    UINT8* ptr;

    ptr = buf;

    for (;;) {

	if (bytes < 1)
	    return ptr - buf;

	if (ptr[0] == 0) {

	    /* Run (3 bytes block) */
	    if (bytes < 3)
		break;

	    n = ptr[1];

	    if (state->x + n > state->bytes) {
		state->errcode = IMAGING_CODEC_OVERRUN;
		return -1;
	    }

	    memset(state->buffer + state->x, ptr[2], n);

	    ptr += 3;
	    bytes -= 3;

	} else {

	    /* Literal (1+n bytes block) */
	    n = ptr[0];

	    if (bytes < 1 + n)
		break;

	    if (state->x + n > state->bytes) {
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
