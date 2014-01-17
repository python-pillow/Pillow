/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for ZIP (deflated) image data.
 *
 * history:
 * 1996-12-14 fl   Created (for PNG)
 * 1997-01-15 fl   Prepared to read TIFF/ZIP
 * 2001-11-19 fl   PNG incomplete read patch (from Bernhard Herzog)
 *
 * Copyright (c) Fredrik Lundh 1996.
 * Copyright (c) Secret Labs AB 1997-2001.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#ifdef	HAVE_LIBZ

#include "Zip.h"

static const int OFFSET[] = { 7, 3, 3, 1, 1, 0, 0 };
static const int STARTING_COL[] = { 0, 4, 0, 2, 0, 1, 0 };
static const int STARTING_ROW[] = { 0, 0, 4, 0, 2, 0, 1 };
static const int COL_INCREMENT[] = { 8, 8, 4, 4, 2, 2, 1 };
static const int ROW_INCREMENT[] = { 8, 8, 8, 4, 4, 2, 2 };

/* Get the length in bytes of a scanline in the pass specified,
 * for interlaced images */
static int get_row_len(ImagingCodecState state, int pass)
{
    int row_len = (state->xsize + OFFSET[pass]) / COL_INCREMENT[pass];
    return ((row_len * state->bits) + 7) / 8;
}

/* -------------------------------------------------------------------- */
/* Decoder								*/
/* -------------------------------------------------------------------- */

int
ImagingZipDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    ZIPSTATE* context = (ZIPSTATE*) state->context;
    int err;
    int n;
    UINT8* ptr;
    int i, bpp;
    int row_len;

    if (!state->state) {

	/* Initialization */
	if (context->mode == ZIP_PNG || context->mode == ZIP_PNG_PALETTE)
	    context->prefix = 1; /* PNG */

	/* Expand standard buffer to make room for the (optional) filter
	   prefix, and allocate a buffer to hold the previous line */
	free(state->buffer);
	state->buffer = (UINT8*) malloc(state->bytes+1);
	context->previous = (UINT8*) malloc(state->bytes+1);
	if (!state->buffer || !context->previous) {
	    state->errcode = IMAGING_CODEC_MEMORY;
	    return -1;
	}

        context->last_output = 0;

	/* Initialize to black */
	memset(context->previous, 0, state->bytes+1);

	/* Setup decompression context */
	context->z_stream.zalloc = (alloc_func) NULL;
	context->z_stream.zfree = (free_func) NULL;
	context->z_stream.opaque = (voidpf) NULL;

	err = inflateInit(&context->z_stream);
	if (err < 0) {
	    state->errcode = IMAGING_CODEC_CONFIG;
	    return -1;
	}

	if (context->interlaced) {
	    context->pass = 0;
	    state->y = STARTING_ROW[context->pass];
	}

	/* Ready to decode */
	state->state = 1;

    }

    if (context->interlaced) {
	row_len = get_row_len(state, context->pass);
    } else {
	row_len = state->bytes;
    }

    /* Setup the source buffer */
    context->z_stream.next_in = buf;
    context->z_stream.avail_in = bytes;

    /* Decompress what we've got this far */
    while (context->z_stream.avail_in > 0) {

	context->z_stream.next_out = state->buffer + context->last_output;
	context->z_stream.avail_out =
	    row_len + context->prefix - context->last_output;

	err = inflate(&context->z_stream, Z_NO_FLUSH);

	if (err < 0) {
	    /* Something went wrong inside the compression library */
	    if (err == Z_DATA_ERROR)
		state->errcode = IMAGING_CODEC_BROKEN;
	    else if (err == Z_MEM_ERROR)
		state->errcode = IMAGING_CODEC_MEMORY;
	    else
		state->errcode = IMAGING_CODEC_CONFIG;
	    free(context->previous);
	    inflateEnd(&context->z_stream);
	    return -1;
	}

	n = row_len + context->prefix - context->z_stream.avail_out;

	if (n < row_len + context->prefix) {
	    context->last_output = n;
	    break; /* need more input data */
	}

	/* Apply predictor */
	switch (context->mode) {
	case ZIP_PNG:
	    switch (state->buffer[0]) {
	    case 0:
		break;
	    case 1:
		/* prior */
		bpp = (state->bits + 7) / 8;
		for (i = bpp+1; i <= row_len; i++)
		    state->buffer[i] += state->buffer[i-bpp];
		break;
	    case 2:
		/* up */
		for (i = 1; i <= row_len; i++)
		    state->buffer[i] += context->previous[i];
		break;
	    case 3:
		/* average */
		bpp = (state->bits + 7) / 8;
		for (i = 1; i <= bpp; i++)
		    state->buffer[i] += context->previous[i]/2;
		for (; i <= row_len; i++)
		    state->buffer[i] +=
			(state->buffer[i-bpp] + context->previous[i])/2;
		break;
	    case 4:
		/* paeth filtering */
		bpp = (state->bits + 7) / 8;
		for (i = 1; i <= bpp; i++)
		    state->buffer[i] += context->previous[i];
		for (; i <= row_len; i++) {
		    int a, b, c;
		    int pa, pb, pc;

		    /* fetch pixels */
		    a = state->buffer[i-bpp];
		    b = context->previous[i];
		    c = context->previous[i-bpp];

		    /* distances to surrounding pixels */
		    pa = abs(b - c);
		    pb = abs(a - c);
		    pc = abs(a + b - 2*c);

		    /* pick predictor with the shortest distance */
		    state->buffer[i] +=
			(pa <= pb && pa <= pc) ? a : (pb <= pc) ? b : c;

		}
		break;
	    default:
		state->errcode = IMAGING_CODEC_UNKNOWN;
		free(context->previous);
		inflateEnd(&context->z_stream);
		return -1;
	    }
	    break;
	case ZIP_TIFF_PREDICTOR:
	    bpp = (state->bits + 7) / 8;
	    for (i = bpp+1; i <= row_len; i++)
		state->buffer[i] += state->buffer[i-bpp];
	    break;
	}

	/* Stuff data into the image */
	if (context->interlaced) {
	    int col = STARTING_COL[context->pass];
	    if (state->bits >= 8) {
		/* Stuff pixels in their correct location, one by one */
		for (i = 0; i < row_len; i += ((state->bits + 7) / 8)) {
		    state->shuffle((UINT8*) im->image[state->y] +
				   col * im->pixelsize,
				   state->buffer + context->prefix + i, 1);
		    col += COL_INCREMENT[context->pass];
		}
	    } else {
		/* Handle case with more than a pixel in each byte */
		int row_bits = ((state->xsize + OFFSET[context->pass])
		        / COL_INCREMENT[context->pass]) * state->bits;
		for (i = 0; i < row_bits; i += state->bits) {
		    UINT8 byte = *(state->buffer + context->prefix + (i / 8));
		    byte <<= (i % 8);
		    state->shuffle((UINT8*) im->image[state->y] +
				   col * im->pixelsize, &byte, 1);
		    col += COL_INCREMENT[context->pass];
		}
	    }
	    /* Find next valid scanline */
	    state->y += ROW_INCREMENT[context->pass];
	    while (state->y >= state->ysize || row_len <= 0) {
		context->pass++;
		if (context->pass == 7) {
		    /* Force exit below */
		    state->y = state->ysize;
		    break;
		}
		state->y = STARTING_ROW[context->pass];
		row_len = get_row_len(state, context->pass);
		/* Since we're moving to the "first" line, the previous line
		 * should be black to make filters work corectly */
		memset(state->buffer, 0, state->bytes+1);
	    }
	} else {
	    state->shuffle((UINT8*) im->image[state->y + state->yoff] +
			   state->xoff * im->pixelsize,
			   state->buffer + context->prefix,
			   state->xsize);
	    state->y++;
	}

        /* all inflate output has been consumed */
        context->last_output = 0;

	if (state->y >= state->ysize || err == Z_STREAM_END) {

	    /* The image and the data should end simultaneously */
	    /* if (state->y < state->ysize || err != Z_STREAM_END)
		state->errcode = IMAGING_CODEC_BROKEN; */

	    free(context->previous);
	    inflateEnd(&context->z_stream);
	    return -1; /* end of file (errcode=0) */

	}

	/* Swap buffer pointers */
	ptr = state->buffer;
	state->buffer = context->previous;
	context->previous = ptr;

    }

    return bytes; /* consumed all of it */

}

#endif
