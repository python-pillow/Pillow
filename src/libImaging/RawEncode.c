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
 * 96-04-30 fl	created
 * 97-01-03 fl	fixed padding
 *
 * Copyright (c) Fredrik Lundh 1996-97.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.  */


#include "Imaging.h"

int
ImagingRawEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* ptr;

    if (!state->state) {

	/* The "count" field holds the stride, if specified.  Fix
	   things up so "bytes" is the full size, and "count" the
	   packed size */

	if (state->count > 0) {
	    int bytes = state->count;

	    /* stride must not be less than real size */
	    if (state->count < state->bytes) {
		state->errcode = IMAGING_CODEC_CONFIG;
		return -1;
	    }
	    state->count = state->bytes;
	    state->bytes = bytes;
	} else
	    state->count = state->bytes;

	/* The "ystep" field specifies the orientation */

	if (state->ystep < 0) {
	    state->y = state->ysize-1;
	    state->ystep = -1;
	} else
	    state->ystep = 1;

	state->state = 1;

    }

    if (bytes < state->bytes) {
	state->errcode = IMAGING_CODEC_CONFIG;
	return 0;
    }

    ptr = buf;

    while (bytes >= state->bytes) {

	state->shuffle(ptr, (UINT8*) im->image[state->y + state->yoff] +
		       state->xoff * im->pixelsize, state->xsize);

	if (state->bytes > state->count)
	    /* zero-pad the buffer, if necessary */
	    memset(ptr + state->count, 0, state->bytes - state->count);

	ptr += state->bytes;
	bytes -= state->bytes;

	state->y += state->ystep;

	if (state->y < 0 || state->y >= state->ysize) {
	    state->errcode = IMAGING_CODEC_END;
	    break;
	}

    }

    return ptr - buf;

}
