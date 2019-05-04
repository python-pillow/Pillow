/*
 * THIS IS WORK IN PROGRESS
 *
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for SUN RLE data.
 *
 * history:
 *      97-01-04 fl     Created
 *
 * Copyright (c) Fredrik Lundh 1997.
 * Copyright (c) Secret Labs AB 1997.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"


int
ImagingSunRleDecode(Imaging im, ImagingCodecState state, UINT8* buf, Py_ssize_t bytes)
{
    int n;
    UINT8* ptr;
    UINT8 extra_data = 0;
    UINT8 extra_bytes = 0;

    ptr = buf;

    for (;;) {

        if (bytes < 1)
            return ptr - buf;

        if (ptr[0] == 0x80) {

            if (bytes < 2)
                break;

            n = ptr[1];


            if (n == 0) {

                /* Literal 0x80 (2 bytes) */
                n = 1;

                state->buffer[state->x] = 0x80;

                ptr += 2;
                bytes -= 2;

            } else {

                /* Run (3 bytes) */
                if (bytes < 3)
                    break;

                /* from (https://www.fileformat.info/format/sunraster/egff.htm)

                   For example, a run of 100 pixels with the value of
                   0Ah would encode as the values 80h 64h 0Ah. A
                   single pixel value of 80h would encode as the
                   values 80h 00h. The four unencoded bytes 12345678h
                   would be stored in the RLE stream as 12h 34h 56h
                   78h.  100 pixels, n=100, not 100 pixels, n=99.

                   But Wait! There's More!
                   (https://www.fileformat.info/format/sunraster/spec/598a59c4fac64c52897585d390d86360/view.htm)

                   If the first byte is 0x80, and the second byte is
                   not zero, the record is three bytes long. The
                   second byte is a count and the third byte is a
                   value. Output (count+1) pixels of that value.

                   2 specs, same site, but Imagemagick and GIMP seem
                   to agree on the second one.
                */
                n += 1;

                if (state->x + n > state->bytes) {
                    extra_bytes = n;  /* full value */
                    n = state->bytes - state->x;
                    extra_bytes -= n;
                    extra_data = ptr[2];
                }

                memset(state->buffer + state->x, ptr[2], n);

                ptr += 3;
                bytes -= 3;

            }

        } else {

            /* Literal byte */
            n = 1;

            state->buffer[state->x] = ptr[0];

            ptr += 1;
            bytes -= 1;

        }

        for (;;) {
            state->x += n;

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

            if (extra_bytes == 0) {
                break;
            }

            if (state->x > 0) {
                break; // assert
            }

            if (extra_bytes >= state->bytes) {
                n = state->bytes;
            } else {
                n = extra_bytes;
            }
            memset(state->buffer + state->x, extra_data, n);
            extra_bytes -= n;
        }
    }

    return ptr - buf;
}
