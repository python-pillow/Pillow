/*
 * The Python Imaging Library.
 * $Id$
 *
 * a fast, suspendable TIFF LZW decoder
 *
 * description:
 *	This code is based on the GIF decoder.  There are some
 *	subtle differences between GIF and TIFF LZW, though:
 *	- The fill order is different. In the TIFF file, you
 *	  must shift new bits in to the right, not to the left.
 *	- There is no blocking in the input data stream.
 *	- The code size is increased one step earlier than
 *	  for GIF
 *	- Image data are seen as a byte stream, not a pixel
 *	  stream. This means that the code size will always
 *	  start at 9 bits.
 *
 * history:
 *	95-09-13 fl	Created (derived from GifDecode.c)
 *	96-03-28 fl	Revised API, integrated with PIL
 *	97-01-05 fl	Added filter support, added extra consistency checks
 *
 * Copyright (c) Fredrik Lundh 1995-97.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include <stdio.h>
#include <stdlib.h>	/* memcpy() */

#include "Lzw.h"


int
ImagingLzwDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* p;
    int c, i;
    int thiscode;
    LZWSTATE* context = (LZWSTATE*) state->context;

    unsigned char *ptr = buf;

    if (!state->state) {

	/* Clear code */
	context->clear = 1 << 8;

	/* End code */
	context->end = context->clear + 1;

	state->state = 1;
    }

    for (;;) {

	if (state->state == 1) {

	    /* First free entry in table */
	    context->next = context->clear + 2;

	    /* Initial code size */
	    context->codesize = 8 + 1;
	    context->codemask = (1 << context->codesize) - 1;

	    /* Buffer pointer.  We fill the buffer from right, which
	       allows us to return all of it in one operation. */
	    context->bufferindex = LZWBUFFER;

	    state->state = 2;
	}

	if (context->bufferindex < LZWBUFFER) {

	    /* Return whole buffer in one chunk */
	    i = LZWBUFFER - context->bufferindex;
	    p = &context->buffer[context->bufferindex];

	    context->bufferindex = LZWBUFFER;

	} else {

	    /* Get current symbol */
	    while (context->bitcount < context->codesize) {

		if (bytes < 1)
		    return ptr - buf;;

		/* Read next byte */
		c = *ptr++; bytes--;

		/* New bits are shifted in from from the right. */
		context->bitbuffer = (context->bitbuffer << 8) | c;
		context->bitcount += 8;

	    }

	    /* Extract current symbol from bit buffer. */
	    c = (context->bitbuffer >> (context->bitcount -
					 context->codesize))
		& context->codemask;

	    /* Adjust buffer */
	    context->bitcount -= context->codesize;

	    /* If c is less than clear, it's a data byte.  Otherwise,
	       it's either clear/end or a code symbol which should be
	       expanded. */

	    if (c == context->clear) {
		if (state->state != 2)
		    state->state = 1;
		continue;
	    }

	    if (c == context->end)
		break;

	    i = 1;
	    p = &context->lastdata;

	    if (state->state == 2) {

		/* First valid symbol after clear; use as is */
		if (c > context->clear) {
		    state->errcode = IMAGING_CODEC_BROKEN;
		    return -1;
		}

		context->lastdata = context->lastcode = c;
		state->state = 3;

	    } else {

		thiscode = c;

		if (c > context->next) {
		    state->errcode = IMAGING_CODEC_BROKEN;
		    return -1;
		}

		if (c == context->next) {

		    /* c == next is allowed, by some strange reason */
		    if (context->bufferindex <= 0) {
			state->errcode = IMAGING_CODEC_BROKEN;
			return -1;
		    }

		    context->buffer[--context->bufferindex] = context->lastdata;
		    c = context->lastcode;
		}

		while (c >= context->clear) {

		    /* Copy data string to buffer (beginning from right) */

		    if (context->bufferindex <= 0 || c >= LZWTABLE) {
			state->errcode = IMAGING_CODEC_BROKEN;
			return -1;
		    }

		    context->buffer[--context->bufferindex] =
			context->data[c];
		    c = context->link[c];
		}

		context->lastdata = c;

		if (context->next < LZWTABLE) {

		    /* While we still have room for it, add this
		       symbol to the table. */
		    context->data[context->next] = c;
		    context->link[context->next] = context->lastcode;

		    context->next++;

		    if (context->next == context->codemask &&
			context->codesize < LZWBITS) {

			/* Expand code size */
			context->codesize++;
			context->codemask = (1 << context->codesize) - 1;

		    }
		}
		context->lastcode = thiscode;
	    }
	}

	/* Update the output image */
	for (c = 0; c < i; c++) {

	    state->buffer[state->x] = p[c];

	    if (++state->x >= state->bytes) {

		int x, bpp;

		/* Apply filter */
		switch (context->filter) {
		case 2:
		    /* Horizontal differing ("prior") */
		    bpp = (state->bits + 7) / 8;
		    for (x = bpp; x < state->bytes; x++)
			state->buffer[x] += state->buffer[x-bpp];
		}

		/* Got a full line, unpack it */
		state->shuffle((UINT8*) im->image[state->y + state->yoff] +
			       state->xoff * im->pixelsize, state->buffer,
			       state->xsize);

		state->x = 0;

		if (++state->y >= state->ysize)
		    /* End of file (errcode = 0) */
		    return -1;
	    }
	}
    }

    return ptr - buf;
}
