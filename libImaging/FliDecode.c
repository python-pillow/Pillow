/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for Autodesk Animator FLI/FLC animations
 *
 * history:
 *	97-01-03 fl	Created
 *	97-01-17 fl	Added SS2 support (FLC)
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"


#define	I16(ptr)\
    ((ptr)[0] + ((ptr)[1] << 8))

#define	I32(ptr)\
    ((ptr)[0] + ((ptr)[1] << 8) + ((ptr)[2] << 16) + ((ptr)[3] << 24))


int
ImagingFliDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* ptr;
    int framesize;
    int c, chunks;
    int l, lines;
    int i, j, x = 0, y, ymax;

    /* If not even the chunk size is present, we'd better leave */

    if (bytes < 4)
	return 0;

    /* We don't decode anything unless we have a full chunk in the
       input buffer (on the other hand, the Python part of the driver
       makes sure this is always the case) */

    ptr = buf;

    framesize = I32(ptr);
    if (framesize < I32(ptr))
	return 0;

    /* Make sure this is a frame chunk.  The Python driver takes
       case of other chunk types. */

    if (I16(ptr+4) != 0xF1FA) {
	state->errcode = IMAGING_CODEC_UNKNOWN;
	return -1;
    }

    chunks = I16(ptr+6);
    ptr += 16;

    /* Process subchunks */
    for (c = 0; c < chunks; c++) {
	UINT8 *data = ptr + 6;
	switch (I16(ptr+4)) {
	case 4: case 11:
	    /* FLI COLOR chunk */
	    break; /* ignored; handled by Python code */
	case 7:
	    /* FLI SS2 chunk (word delta) */
	    lines = I16(data); data += 2;
	    for (l = y = 0; l < lines && y < state->ysize; l++, y++) {
		UINT8* buf = (UINT8*) im->image[y];
		int p, packets;
		packets = I16(data); data += 2;
		while (packets & 0x8000) {
		    /* flag word */
		    if (packets & 0x4000) {
			y += 65536 - packets; /* skip lines */
			if (y >= state->ysize) {
			    state->errcode = IMAGING_CODEC_OVERRUN;
			    return -1;
			}
			buf = (UINT8*) im->image[y];
		    } else {
			/* store last byte (used if line width is odd) */
			buf[state->xsize-1] = (UINT8) packets;
		    }
		    packets = I16(data); data += 2;
		}
		for (p = x = 0; p < packets; p++) {
		    x += data[0]; /* pixel skip */
		    if (data[1] >= 128) {
			i = 256-data[1]; /* run */
			if (x + i + i > state->xsize)
			    break;
			for (j = 0; j < i; j++) {
			    buf[x++] = data[2];
			    buf[x++] = data[3];
			}
			data += 2 + 2;
		    } else {
			i = 2 * (int) data[1]; /* chunk */
			if (x + i > state->xsize)
			    break;
			memcpy(buf + x, data + 2, i);
			data += 2 + i;
			x += i;
		    }
		}
		if (p < packets)
		    break; /* didn't process all packets */
	    }
	    if (l < lines) {
		/* didn't process all lines */
		state->errcode = IMAGING_CODEC_OVERRUN;
		return -1;
	    }
	    break;
	case 12:
	    /* FLI LC chunk (byte delta) */
	    y = I16(data); ymax = y + I16(data+2); data += 4;
	    for (; y < ymax && y < state->ysize; y++) {
		UINT8* out = (UINT8*) im->image[y];
		int p, packets = *data++;
		for (p = x = 0; p < packets; p++, x += i) {
		    x += data[0]; /* skip pixels */
		    if (data[1] & 0x80) {
			i = 256-data[1]; /* run */
			if (x + i > state->xsize)
			    break;
			memset(out + x, data[2], i);
			data += 3;
		    } else {
			i = data[1]; /* chunk */
			if (x + i > state->xsize)
			    break;
			memcpy(out + x, data + 2, i);
			data += i + 2;
		    }
		}
		if (p < packets)
		    break; /* didn't process all packets */
	    }
	    if (y < ymax) {
		/* didn't process all lines */
		state->errcode = IMAGING_CODEC_OVERRUN;
		return -1;
	    }
	    break;
	case 13:
	    /* FLI BLACK chunk */
	    for (y = 0; y < state->ysize; y++)
		memset(im->image[y], 0, state->xsize);
	    break;
	case 15:
	    /* FLI BRUN chunk */
	    for (y = 0; y < state->ysize; y++) {
		UINT8* out = (UINT8*) im->image[y];
		data += 1; /* ignore packetcount byte */
		for (x = 0; x < state->xsize; x += i) {
		    if (data[0] & 0x80) {
			i = 256 - data[0];
			if (x + i > state->xsize)
			    break; /* safety first */
			memcpy(out + x, data + 1, i);
			data += i + 1;
		    } else {
			i = data[0];
			if (x + i > state->xsize)
			    break; /* safety first */
			memset(out + x, data[1], i);
			data += 2;
		    }
		}
		if (x != state->xsize) {
		    /* didn't unpack whole line */
		    state->errcode = IMAGING_CODEC_OVERRUN;
		    return -1;
		}
	    }
	    break;
	case 16:
	    /* COPY chunk */
	    for (y = 0; y < state->ysize; y++) {
		UINT8* buf = (UINT8*) im->image[y];
		memcpy(buf, data, state->xsize);
		data += state->xsize;
	    }
	    break;
	case 18:
	    /* PSTAMP chunk */
	    break; /* ignored */
	default:
	    /* unknown chunk */
	    /* printf("unknown FLI/FLC chunk: %d\n", I16(ptr+4)); */
	    state->errcode = IMAGING_CODEC_UNKNOWN;
	    return -1;
	}
	ptr += I32(ptr);
    }

    return -1; /* end of frame */
}
