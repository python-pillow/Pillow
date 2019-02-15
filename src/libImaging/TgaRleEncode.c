
#include "Imaging.h"

#include <assert.h>
#include <string.h>


static int comparePixels(const UINT8* buf, int x, int bytesPerPixel)
{
    buf += x * bytesPerPixel;
    return memcmp(buf, buf + bytesPerPixel, bytesPerPixel) == 0;
}


int
ImagingTgaRleEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* dst;
    int bytesPerPixel;

    if (state->state == 0) {
        if (state->ystep < 0) {
            state->ystep = -1;
            state->y = state->ysize - 1;
        } else
            state->ystep = 1;

        state->state = 1;
    }

    dst = buf;
    bytesPerPixel = (state->bits + 7) / 8;

    while (1) {
        int flushCount;

        /*
         * state->count is the numbers of bytes in the packet,
         * excluding the 1-byte descriptor.
         */
        if (state->count == 0) {
            UINT8* row;
            UINT8 descriptor;
            int startX;

            assert(state->x <= state->xsize);

            /* Make sure we have space for the descriptor. */
            if (bytes < 1)
                break;

            if (state->x == state->xsize) {
                state->x = 0;

                state->y += state->ystep;
                if (state->y < 0 || state->y >= state->ysize) {
                    state->errcode = IMAGING_CODEC_END;
                    break;
                }
            }

            if (state->x == 0)
                state->shuffle(
                    state->buffer,
                    (UINT8*)im->image[state->y + state->yoff]
                        + state->xoff * im->pixelsize,
                    state->xsize);

            row = state->buffer;

            /* Start with a raw packet for 1 px. */
            descriptor = 0;
            startX = state->x;
            state->count = bytesPerPixel;

            if (state->x + 1 < state->xsize) {
                int maxLookup;
                int isRaw;

                isRaw = !comparePixels(row, state->x, bytesPerPixel);
                ++state->x;

                /*
                 * A packet can contain up to 128 pixels;
                 * 2 are already behind (state->x points to
                 * the second one).
                 */
                maxLookup = state->x + 126;
                /* A packet must not span multiple rows. */
                if (maxLookup > state->xsize - 1)
                    maxLookup = state->xsize - 1;

                if (isRaw) {
                    while (state->x < maxLookup)
                        if (!comparePixels(row, state->x, bytesPerPixel))
                            ++state->x;
                        else {
                            /* Two identical pixels will go to RLE packet. */
                            --state->x;
                            break;
                        }

                    state->count += (state->x - startX) * bytesPerPixel;
                } else {
                    descriptor |= 0x80;

                    while (state->x < maxLookup)
                        if (comparePixels(row, state->x, bytesPerPixel))
                            ++state->x;
                        else
                            break;
                }
            }

            /*
             * state->x currently points to the last pixel to be
             * included in the packet. The pixel count in the
             * descriptor is 1 less than actual number of pixels in
             * the packet, that is, state->x == startX if we encode
             * only 1 pixel.
             */
            descriptor += state->x - startX;
            *dst++ = descriptor;
            --bytes;

            /* Advance to past-the-last encoded pixel. */
            ++state->x;
        }

        assert(bytes >= 0);
        assert(state->count > 0);
        assert(state->x > 0);
        assert(state->count <= state->x * bytesPerPixel);

        if (bytes == 0)
            break;

        flushCount = state->count;
        if (flushCount > bytes)
            flushCount = bytes;

        memcpy(
            dst,
            state->buffer + (state->x * bytesPerPixel - state->count),
            flushCount);
        dst += flushCount;
        bytes -= flushCount;

        state->count -= flushCount;
    }

    return dst - buf;
}
