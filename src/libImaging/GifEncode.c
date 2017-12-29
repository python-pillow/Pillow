/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for uncompressed GIF data
 *
 * history:
 * 97-01-05 fl	created (writes uncompressed data)
 * 97-08-27 fl	fixed off-by-one error in buffer size test
 * 98-07-09 fl	added interlace write support
 * 99-02-07 fl	rewritten, now uses a run-length encoding strategy
 * 99-02-08 fl	improved run-length encoding for long runs
 *
 * Copyright (c) Secret Labs AB 1997-99.
 * Copyright (c) Fredrik Lundh 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include "Gif.h"

/* codes from 0 to 255 are literals */
#define CLEAR_CODE 256
#define EOF_CODE 257
#define FIRST_CODE 258
#define LAST_CODE 511

enum { INIT, ENCODE, ENCODE_EOF, FLUSH, EXIT };

/* to make things a little less complicated, we use a simple output
   queue to hold completed blocks.  the following inlined function
   adds a byte to the current block.  it allocates a new block if
   necessary. */

static inline int
emit(GIFENCODERSTATE *context, int byte)
{
    /* write a byte to the output buffer */

    if (!context->block || context->block->size == 255) {
        GIFENCODERBLOCK* block;

        /* no room in the current block (or no current block);
           allocate a new one */

        /* add current block to end of flush queue */
        if (context->block) {
            block = context->flush;
            while (block && block->next)
                block = block->next;
            if (block)
                block->next = context->block;
            else
                context->flush = context->block;
        }

        /* get a new block */
        if (context->free) {
            block = context->free;
            context->free = NULL;
        } else {
            /* malloc check ok, small constant allocation */
            block = malloc(sizeof(GIFENCODERBLOCK));
            if (!block)
                return 0;
        }

        block->size = 0;
        block->next = NULL;

        context->block = block;

    }

    /* write new byte to block */
    context->block->data[context->block->size++] = byte;

    return 1;
}

/* write a code word to the current block.  this is a macro to make
   sure it's inlined on all platforms */

#define EMIT(code) {\
    context->bitbuffer |= ((INT32) (code)) << context->bitcount;\
    context->bitcount += 9;\
    while (context->bitcount >= 8) {\
        if (!emit(context, (UINT8) context->bitbuffer)) {\
            state->errcode = IMAGING_CODEC_MEMORY;\
            return 0;\
        }\
        context->bitbuffer >>= 8;\
        context->bitcount -= 8;\
    }\
}

/* write a run.  we use a combination of literals and combinations of
   literals.  this can give quite decent compression for images with
   long stretches of identical pixels.  but remember: if you want
   really good compression, use another file format. */

#define EMIT_RUN(label) {\
label:\
    while (context->count > 0) {\
        int run = 2;\
        EMIT(context->last);\
        context->count--;\
        if (state->count++ == LAST_CODE) {\
            EMIT(CLEAR_CODE);\
            state->count = FIRST_CODE;\
            goto label;\
        }\
        while (context->count >= run) {\
            EMIT(state->count - 1);\
            context->count -= run;\
            run++;\
            if (state->count++ == LAST_CODE) {\
                EMIT(CLEAR_CODE);\
                state->count = FIRST_CODE;\
                goto label;\
            }\
        }\
        if (context->count > 1) {\
            EMIT(state->count - 1 - (run - context->count));\
            context->count = 0;\
            if (state->count++ == LAST_CODE) {\
                EMIT(CLEAR_CODE);\
                state->count = FIRST_CODE;\
            }\
            break;\
        }\
    }\
}

int
ImagingGifEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    UINT8* ptr;
    int this;

    GIFENCODERBLOCK* block;
    GIFENCODERSTATE *context = (GIFENCODERSTATE*) state->context;

    if (!state->state) {

	/* place a clear code in the output buffer */
	context->bitbuffer = CLEAR_CODE;
	context->bitcount = 9;

	state->count = FIRST_CODE;

	if (context->interlace) {
	    context->interlace = 1;
	    context->step = 8;
	} else
	    context->step = 1;

        context->last = -1;

        /* sanity check */
        if (state->xsize <= 0 || state->ysize <= 0)
            state->state = ENCODE_EOF;

    }

    ptr = buf;

    for (;;)

	switch (state->state) {

        case INIT:
        case ENCODE:

            /* identify and store a run of pixels */

            if (state->x == 0 || state->x >= state->xsize) {

                if (!context->interlace && state->y >= state->ysize) {
                    state->state = ENCODE_EOF;
                    break;
                }

                if (context->flush) {
                    state->state = FLUSH;
                    break;
                }

                /* get another line of data */
                state->shuffle(
                    state->buffer,
                    (UINT8*) im->image[state->y + state->yoff] +
                    state->xoff * im->pixelsize, state->xsize
                    );

                state->x = 0;

                if (state->state == INIT) {
                    /* preload the run-length buffer and get going */
                    context->last = state->buffer[0];
                    context->count = state->x = 1;
                    state->state = ENCODE;
                }

                /* step forward, according to the interlace settings */
                state->y += context->step;
                while (context->interlace && state->y >= state->ysize)
                    switch (context->interlace) {
                    case 1:
                        state->y = 4;
                        context->interlace = 2;
                        break;
                    case 2:
                        context->step = 4;
                        state->y = 2;
                        context->interlace = 3;
                        break;
                    case 3:
                        context->step = 2;
                        state->y = 1;
                        context->interlace = 0;
                        break;
                    default:
                        /* just make sure we don't loop forever */
                        context->interlace = 0;
                    }

            }

            this = state->buffer[state->x++];

            if (this == context->last)
                context->count++;
            else {
                EMIT_RUN(label1);
                context->last = this;
                context->count = 1;
            }
	    break;


        case ENCODE_EOF:

            /* write the final run */
            EMIT_RUN(label2);

            /* write an end of image marker */
            EMIT(EOF_CODE);

            /* empty the bit buffer */
            while (context->bitcount > 0) {
                if (!emit(context, (UINT8) context->bitbuffer)) {
                    state->errcode = IMAGING_CODEC_MEMORY;
                    return 0;
                }
                context->bitbuffer >>= 8;
                context->bitcount -= 8;
            }

            /* flush the last block, and exit */
            if (context->block) {
                GIFENCODERBLOCK* block;
                block = context->flush;
                while (block && block->next)
                    block = block->next;
                if (block)
                    block->next = context->block;
                else
                    context->flush = context->block;
                context->block = NULL;
            }

            state->state = EXIT;

            /* fall through... */

	case EXIT:
	case FLUSH:

            while (context->flush) {

                /* get a block from the flush queue */
                block = context->flush;

                if (block->size > 0) {

                    /* make sure it fits into the output buffer */
                    if (bytes < block->size+1)
                        return ptr - buf;

                    ptr[0] = block->size;
                    memcpy(ptr+1, block->data, block->size);

                    ptr += block->size+1;
                    bytes -= block->size+1;

                }

                context->flush = block->next;

                if (context->free)
                    free(context->free);
                context->free = block;

            }

            if (state->state == EXIT) {
                /* this was the last block! */
                if (context->free)
                    free(context->free);
                state->errcode = IMAGING_CODEC_END;
                return ptr - buf;
            }

            state->state = ENCODE;
	    break;
        }
}
