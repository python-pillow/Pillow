/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for hex encoded image data
 *
 * history:
 *	96-05-16 fl	Created
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#define	HEX(v) ((v >= '0' && v <= '9') ? v - '0' :\
		(v >= 'a' && v <= 'f') ? v - 'a' + 10 :\
		(v >= 'A' && v <= 'F') ? v - 'A' + 10 : -1)

int
ImagingHexDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* ptr;
    int a, b;

    ptr = buf;

    for (;;) {

	if (bytes < 2)
	    return ptr - buf;

	a = HEX(ptr[0]);
	b = HEX(ptr[1]);

	if (a < 0 || b < 0) {

	    ptr++;
	    bytes--;

	} else {

	    ptr += 2;
	    bytes -= 2;

	    state->buffer[state->x] = (a<<4) + b;

	    if (++state->x >= state->bytes) {

		/* Got a full line, unpack it */
		state->shuffle((UINT8*) im->image[state->y], state->buffer,
			       state->xsize);

		state->x = 0;

		if (++state->y >= state->ysize) {
		    /* End of file (errcode = 0) */
		    return -1;
		}
	    }

	}
    }
}
