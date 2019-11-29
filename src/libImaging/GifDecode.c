/*
 * The Python Imaging Library.
 * $Id$
 *
 * a fast, suspendable GIF decoder
 *
 * history:
 * 95-09-03 fl	Created
 * 95-09-05 fl	Fixed sign problem on 16-bit platforms
 * 95-09-13 fl	Added some storage shortcuts
 * 96-03-28 fl	Revised API, integrated with PIL
 * 96-12-10 fl	Added interlace support
 * 96-12-16 fl	Fixed premature termination bug introduced by last fix
 * 97-01-05 fl	Don't mess up on bogus configuration
 * 97-01-17 fl	Don't mess up on very small, interlaced files
 * 99-02-07 fl	Minor speedups
 *
 * Copyright (c) Secret Labs AB 1997-99.
 * Copyright (c) Fredrik Lundh 1995-97.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include <stdio.h>
#include <memory.h>	/* memcpy() */

#include "Gif.h"


#define NEWLINE(state, context) {\
    state->x = 0;\
    state->y += context->step;\
    while (state->y >= state->ysize)\
	switch (context->interlace) {\
	case 1:\
	    context->repeat = state->y = 4;\
	    context->interlace = 2;\
	    break;\
	case 2:\
	    context->step = 4;\
	    context->repeat = state->y = 2;\
	    context->interlace = 3;\
	    break;\
	case 3:\
	    context->step = 2;\
	    context->repeat = state->y = 1;\
	    context->interlace = 0;\
	    break;\
	default:\
	    return -1;\
        }\
    if (state->y < state->ysize)\
        out = im->image8[state->y + state->yoff] + state->xoff;\
}


int
ImagingGifDecode(Imaging im, ImagingCodecState state, UINT8* buffer, Py_ssize_t bytes)
{
    UINT8* p;
    UINT8* out;
    int c, i;
    int thiscode;
    GIFDECODERSTATE *context = (GIFDECODERSTATE*) state->context;

    UINT8 *ptr = buffer;

    if (!state->state) {

	/* Initialise state */
	if (context->bits < 0 || context->bits > 12) {
	    state->errcode = IMAGING_CODEC_CONFIG;
	    return -1;
	}

	/* Clear code */
	context->clear = 1 << context->bits;

	/* End code */
	context->end = context->clear + 1;

	/* Interlace */
	if (context->interlace) {
	    context->interlace = 1;
	    context->step = context->repeat = 8;
	} else
	    context->step = 1;

	state->state = 1;
    }

    out = im->image8[state->y + state->yoff] + state->xoff + state->x;

    for (;;) {

	if (state->state == 1) {

	    /* First free entry in table */
	    context->next = context->clear + 2;

	    /* Initial code size */
	    context->codesize = context->bits + 1;
	    context->codemask = (1 << context->codesize) - 1;

	    /* Buffer pointer.  We fill the buffer from right, which
	       allows us to return all of it in one operation. */
	    context->bufferindex = GIFBUFFER;

	    state->state = 2;
	}

	if (context->bufferindex < GIFBUFFER) {

	    /* Return whole buffer in one chunk */
	    i = GIFBUFFER - context->bufferindex;
	    p = &context->buffer[context->bufferindex];

	    context->bufferindex = GIFBUFFER;

	} else {

	    /* Get current symbol */

	    while (context->bitcount < context->codesize) {

		if (context->blocksize > 0) {

		    /* Read next byte */
		    c = *ptr++; bytes--;

		    context->blocksize--;

		    /* New bits are shifted in from from the left. */
		    context->bitbuffer |= (INT32) c << context->bitcount;
		    context->bitcount += 8;

		} else {

		    /* New GIF block */

		    /* We don't start decoding unless we have a full block */
		    if (bytes < 1)
			return ptr - buffer;
		    c = *ptr;
		    if (bytes < c+1)
			return ptr - buffer;

		    context->blocksize = c;

		    ptr++; bytes--;

		}
	    }

	    /* Extract current symbol from bit buffer. */
	    c = (int) context->bitbuffer & context->codemask;

	    /* Adjust buffer */
	    context->bitbuffer >>= context->codesize;
	    context->bitcount -= context->codesize;

	    /* If c is less than "clear", it's a data byte.  Otherwise,
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

		    /* c == next is allowed. not sure why. */

		    if (context->bufferindex <= 0) {
			state->errcode = IMAGING_CODEC_BROKEN;
			return -1;
		    }

		    context->buffer[--context->bufferindex] =
			context->lastdata;

		    c = context->lastcode;

		}

		while (c >= context->clear) {

		    /* Copy data string to buffer (beginning from right) */

		    if (context->bufferindex <= 0 || c >= GIFTABLE) {
			state->errcode = IMAGING_CODEC_BROKEN;
			return -1;
		    }

		    context->buffer[--context->bufferindex] =
			context->data[c];

		    c = context->link[c];
		}

		context->lastdata = c;

		if (context->next < GIFTABLE) {

		    /* We'll only add this symbol if we have room
		       for it (take advise, Netscape!) */
		    context->data[context->next] = c;
		    context->link[context->next] = context->lastcode;

		    if (context->next == context->codemask &&
			context->codesize < GIFBITS) {

			/* Expand code size */
			context->codesize++;
			context->codemask = (1 << context->codesize) - 1;
		    }

		    context->next++;

		}

		context->lastcode = thiscode;

	    }
	}

	/* Copy the bytes into the image */
	if (state->y >= state->ysize) {
	    state->errcode = IMAGING_CODEC_OVERRUN;
	    return -1;
	}

	/* To squeeze some extra pixels out of this loop, we test for
	   some common cases and handle them separately. */

	/* FIXME: should we handle the transparency index in here??? */

	if (i == 1) {
	    if (state->x < state->xsize-1) {
		/* Single pixel, not at the end of the line. */
		*out++ = p[0];
		state->x++;
		continue;
	    }
	} else if (state->x + i <= state->xsize) {
	    /* This string fits into current line. */
	    memcpy(out, p, i);
            out += i;
	    state->x += i;
	    if (state->x == state->xsize) {
		NEWLINE(state, context);
	    }
	    continue;
	}

	/* No shortcut, copy pixel by pixel */
	for (c = 0; c < i; c++) {
	    *out++ = p[c];
	    if (++state->x >= state->xsize) {
		NEWLINE(state, context);
	    }
	}
    }

    return ptr - buffer;
}
