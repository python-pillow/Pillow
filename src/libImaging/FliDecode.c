/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for Autodesk Animator FLI/FLC animations
 *
 * history:
 * 97-01-03 fl Created
 * 97-01-17 fl Added SS2 support (FLC)
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#define I16(ptr) ((ptr)[0] + ((ptr)[1] << 8))

#define I32(ptr) ((ptr)[0] + ((ptr)[1] << 8) + ((ptr)[2] << 16) + ((ptr)[3] << 24))

#define ERR_IF_DATA_OOB(offset)                 \
    if ((data + (offset)) > ptr + bytes) {      \
        state->errcode = IMAGING_CODEC_OVERRUN; \
        return -1;                              \
    }

int
ImagingFliDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    UINT8 *ptr;
    int framesize;
    int c, chunks, advance;
    int l, lines;
    int i, j, x = 0, y, ymax;

    /* If not even the chunk size is present, we'd better leave */

    if (bytes < 4) {
        return 0;
    }

    /* We don't decode anything unless we have a full chunk in the
       input buffer */

    ptr = buf;

    framesize = I32(ptr);
    if (framesize < I32(ptr)) {
        return 0;
    }

    /* Make sure this is a frame chunk.  The Python driver takes
       case of other chunk types. */

    if (bytes < 8) {
        state->errcode = IMAGING_CODEC_OVERRUN;
        return -1;
    }
    if (I16(ptr + 4) != 0xF1FA) {
        state->errcode = IMAGING_CODEC_UNKNOWN;
        return -1;
    }

    chunks = I16(ptr + 6);
    ptr += 16;
    bytes -= 16;

    /* Process subchunks */
    for (c = 0; c < chunks; c++) {
        UINT8 *data;
        if (bytes < 10) {
            state->errcode = IMAGING_CODEC_OVERRUN;
            return -1;
        }
        data = ptr + 6;
        switch (I16(ptr + 4)) {
            case 4:
            case 11:
                /* FLI COLOR chunk */
                break; /* ignored; handled by Python code */
            case 7:
                /* FLI SS2 chunk (word delta) */
                /* OOB ok, we've got 4 bytes min on entry */
                lines = I16(data);
                data += 2;
                for (l = y = 0; l < lines && y < state->ysize; l++, y++) {
                    UINT8 *local_buf = (UINT8 *)im->image[y];
                    int p, packets;
                    ERR_IF_DATA_OOB(2)
                    packets = I16(data);
                    data += 2;
                    while (packets & 0x8000) {
                        /* flag word */
                        if (packets & 0x4000) {
                            y += 65536 - packets; /* skip lines */
                            if (y >= state->ysize) {
                                state->errcode = IMAGING_CODEC_OVERRUN;
                                return -1;
                            }
                            local_buf = (UINT8 *)im->image[y];
                        } else {
                            /* store last byte (used if line width is odd) */
                            local_buf[state->xsize - 1] = (UINT8)packets;
                        }
                        ERR_IF_DATA_OOB(2)
                        packets = I16(data);
                        data += 2;
                    }
                    for (p = x = 0; p < packets; p++) {
                        ERR_IF_DATA_OOB(2)
                        x += data[0]; /* pixel skip */
                        if (data[1] >= 128) {
                            ERR_IF_DATA_OOB(4)
                            i = 256 - data[1]; /* run */
                            if (x + i + i > state->xsize) {
                                break;
                            }
                            for (j = 0; j < i; j++) {
                                local_buf[x++] = data[2];
                                local_buf[x++] = data[3];
                            }
                            data += 2 + 2;
                        } else {
                            i = 2 * (int)data[1]; /* chunk */
                            if (x + i > state->xsize) {
                                break;
                            }
                            ERR_IF_DATA_OOB(2 + i)
                            memcpy(local_buf + x, data + 2, i);
                            data += 2 + i;
                            x += i;
                        }
                    }
                    if (p < packets) {
                        break; /* didn't process all packets */
                    }
                }
                if (l < lines) {
                    /* didn't process all lines */
                    state->errcode = IMAGING_CODEC_OVERRUN;
                    return -1;
                }
                break;
            case 12:
                /* FLI LC chunk (byte delta) */
                /* OOB Check ok, we have 4 bytes min here */
                y = I16(data);
                ymax = y + I16(data + 2);
                data += 4;
                for (; y < ymax && y < state->ysize; y++) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    ERR_IF_DATA_OOB(1)
                    int p, packets = *data++;
                    for (p = x = 0; p < packets; p++, x += i) {
                        ERR_IF_DATA_OOB(2)
                        x += data[0]; /* skip pixels */
                        if (data[1] & 0x80) {
                            i = 256 - data[1]; /* run */
                            if (x + i > state->xsize) {
                                break;
                            }
                            ERR_IF_DATA_OOB(3)
                            memset(out + x, data[2], i);
                            data += 3;
                        } else {
                            i = data[1]; /* chunk */
                            if (x + i > state->xsize) {
                                break;
                            }
                            ERR_IF_DATA_OOB(2 + i)
                            memcpy(out + x, data + 2, i);
                            data += i + 2;
                        }
                    }
                    if (p < packets) {
                        break; /* didn't process all packets */
                    }
                }
                if (y < ymax) {
                    /* didn't process all lines */
                    state->errcode = IMAGING_CODEC_OVERRUN;
                    return -1;
                }
                break;
            case 13:
                /* FLI BLACK chunk */
                for (y = 0; y < state->ysize; y++) {
                    memset(im->image[y], 0, state->xsize);
                }
                break;
            case 15:
                /* FLI BRUN chunk */
                /* OOB, ok, we've got 4 bytes min on entry */
                for (y = 0; y < state->ysize; y++) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    data += 1; /* ignore packetcount byte */
                    for (x = 0; x < state->xsize; x += i) {
                        ERR_IF_DATA_OOB(2)
                        if (data[0] & 0x80) {
                            i = 256 - data[0];
                            if (x + i > state->xsize) {
                                break; /* safety first */
                            }
                            ERR_IF_DATA_OOB(i + 1)
                            memcpy(out + x, data + 1, i);
                            data += i + 1;
                        } else {
                            i = data[0];
                            if (x + i > state->xsize) {
                                break; /* safety first */
                            }
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
                if (state->xsize > bytes / state->ysize) {
                    /* not enough data for frame */
                    return ptr - buf; /* bytes consumed */
                }
                for (y = 0; y < state->ysize; y++) {
                    UINT8 *local_buf = (UINT8 *)im->image[y];
                    memcpy(local_buf, data, state->xsize);
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
        advance = I32(ptr);
        if (advance == 0 ) {
            // If there's no advance, we're in an infinite loop
            state->errcode = IMAGING_CODEC_BROKEN;
            return -1;
        }
        if (advance < 0 || advance > bytes) {
            state->errcode = IMAGING_CODEC_OVERRUN;
            return -1;
        }
        ptr += advance;
        bytes -= advance;
    }

    return -1; /* end of frame */
}
