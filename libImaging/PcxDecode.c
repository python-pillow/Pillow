/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for PCX image data.
 *
 * history:
 *	95-09-14 fl	Created
 *
 * Copyright (c) Fredrik Lundh 1995.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

int
ImagingPcxDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8 n;
    UINT8* ptr;

    ptr = buf;

    for (;;) {

	if (bytes < 1)
	    return ptr - buf;

	if ((*ptr & 0xC0) == 0xC0) {

	    /* Run */
	    if (bytes < 2)
		return ptr - buf;

	    n = ptr[0] & 0x3F;
	    
	    while (n > 0) {
		if (state->x >= state->bytes) {
		    state->errcode = IMAGING_CODEC_OVERRUN;
		    break;
		}
		state->buffer[state->x++] = ptr[1];
		n--;
	    }

	    ptr += 2; bytes -= 2;

	} else {

	    /* Literal */
	    state->buffer[state->x++] = ptr[0];
	    ptr++; bytes--;

	}

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
}
