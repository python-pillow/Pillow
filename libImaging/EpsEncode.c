/* 
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for EPS hex data
 *
 * history:
 *	96-04-19 fl	created
 *	96-06-27 fl	don't drop last block of encoded data
 *
 * notes:
 *	FIXME: rename to HexEncode.c ??
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"


int
ImagingEpsEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    enum { HEXBYTE=1, NEWLINE };
    const char *hex = "0123456789abcdef";

    UINT8* ptr = buf;
    UINT8* in, i;

    if (!state->state) {
	state->state = HEXBYTE;
	state->xsize *= im->pixelsize; /* Hack! */
    }

    in = (UINT8*) im->image[state->y];

    for (;;) {

	if (state->state == NEWLINE) {
	    if (bytes < 1)
		break;
	    *ptr++ = '\n';
	    bytes--;
	    state->state = HEXBYTE;
	}

	if (bytes < 2)
	    break;

	i = in[state->x++];
	*ptr++ = hex[(i>>4)&15];
	*ptr++ = hex[i&15];
	bytes -= 2;

	/* Skip junk bytes */
	if (im->bands == 3 && (state->x & 3) == 3)
	    state->x++;

	if (++state->count >= 79/2) {
	    state->state = NEWLINE;
	    state->count = 0;
	}

	if (state->x >= state->xsize) {
	    state->x = 0;
	    if (++state->y >= state->ysize) {
		state->errcode = IMAGING_CODEC_END;
		break;
	    }
	    in = (UINT8*) im->image[state->y];
	}

    }

    return ptr - buf;
    
}
