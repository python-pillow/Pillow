/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for XBM hex image data
 *
 * history:
 *	96-04-13 fl	Created
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#define	HEX(v) ((v >= '0' && v <= '9') ? v - '0' :\
		(v >= 'a' && v <= 'f') ? v - 'a' + 10 :\
		(v >= 'A' && v <= 'F') ? v - 'A' + 10 : 0)

int
ImagingXbmDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    enum { BYTE = 1, SKIP };

    UINT8* ptr;

    if (!state->state)
	state->state = SKIP;

    ptr = buf;

    for (;;) {

	if (state->state == SKIP) {

	    /* Skip forward until next 'x' */

	    while (bytes > 0) {
		if (*ptr == 'x')
		    break;
		ptr++;
		bytes--;
	    }

	    if (bytes == 0)
		return ptr - buf;

	    state->state = BYTE;

	}

	if (bytes < 3)
	    return ptr - buf;

	state->buffer[state->x] = (HEX(ptr[1])<<4) + HEX(ptr[2]);

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

	ptr += 3;
	bytes -= 3;

	state->state = SKIP;

    }

}
