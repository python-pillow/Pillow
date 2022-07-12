/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for uncompressed GIF data
 *
 * history:
 * 97-01-05 fl created (writes uncompressed data)
 * 97-08-27 fl fixed off-by-one error in buffer size test
 * 98-07-09 fl added interlace write support
 * 99-02-07 fl rewritten, now uses a run-length encoding strategy
 * 99-02-08 fl improved run-length encoding for long runs
 * 2020-12-12 rdg Reworked for LZW compression.
 *
 * Copyright (c) Secret Labs AB 1997-99.
 * Copyright (c) Fredrik Lundh 1997.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include "Gif.h"

enum { INIT, ENCODE, FINISH };

/* GIF LZW encoder by Raymond Gardner. */
/* Released here under PIL license. */

/* This LZW encoder conforms to the GIF LZW format specified in the original
 * Compuserve GIF 87a and GIF 89a specifications (see e.g.
 * https://www.w3.org/Graphics/GIF/spec-gif87.txt Appendix C and
 * https://www.w3.org/Graphics/GIF/spec-gif89a.txt Appendix F).
 */

/* Return values */
#define GLZW_OK                 0
#define GLZW_NO_INPUT_AVAIL     1
#define GLZW_NO_OUTPUT_AVAIL    2
#define GLZW_INTERNAL_ERROR     3

#define CODE_LIMIT              4096

/* Values of entry_state */
enum { LZW_INITIAL, LZW_TRY_IN1, LZW_TRY_IN2, LZW_TRY_OUT1, LZW_TRY_OUT2,
    LZW_FINISHED };

/* Values of control_state */
enum { PUT_HEAD, PUT_INIT_CLEAR, PUT_CLEAR, PUT_LAST_HEAD, PUT_END };

static void glzwe_reset(GIFENCODERSTATE *st) {
    st->next_code = st->end_code + 1;
    st->max_code = 2 * st->clear_code - 1;
    st->code_width = st->bits + 1;
    memset(st->codes, 0, sizeof(st->codes));
}

static void glzwe_init(GIFENCODERSTATE *st) {
    st->clear_code = 1 << st->bits;
    st->end_code = st->clear_code + 1;
    glzwe_reset(st);
    st->entry_state = LZW_INITIAL;
    st->buf_bits_left = 8;
    st->code_buffer = 0;
}

static int glzwe(GIFENCODERSTATE *st, const UINT8 *in_ptr, UINT8 *out_ptr,
        UINT32 *in_avail, UINT32 *out_avail,
        UINT32 end_of_data) {
    switch (st->entry_state) {

    case LZW_TRY_IN1:
get_first_byte:
        if (!*in_avail) {
            if (end_of_data) {
                goto end_of_data;
            }
            st->entry_state = LZW_TRY_IN1;
            return GLZW_NO_INPUT_AVAIL;
        }
        st->head = *in_ptr++;
        (*in_avail)--;

    case LZW_TRY_IN2:
encode_loop:
        if (!*in_avail) {
            if (end_of_data) {
                st->code = st->head;
                st->put_state = PUT_LAST_HEAD;
                goto put_code;
            }
            st->entry_state = LZW_TRY_IN2;
            return GLZW_NO_INPUT_AVAIL;
        }
        st->tail = *in_ptr++;
        (*in_avail)--;

        /* Knuth TAOCP vol 3 sec. 6.4 algorithm D. */
        /* Hash found experimentally to be pretty good. */
        /* This works ONLY with TABLE_SIZE a power of 2. */
        st->probe = ((st->head ^ (st->tail << 6)) * 31) & (TABLE_SIZE - 1);
        while (st->codes[st->probe]) {
            if ((st->codes[st->probe] & 0xFFFFF) ==
                                        ((st->head << 8) | st->tail)) {
                st->head = st->codes[st->probe] >> 20;
                goto encode_loop;
            } else {
        /* Reprobe decrement must be nonzero and relatively prime to table
         * size. So, any odd positive number for power-of-2 size. */
                if ((st->probe -= ((st->tail << 2) | 1)) < 0) {
                    st->probe += TABLE_SIZE;
                }
            }
        }
        /* Key not found, probe is at empty slot. */
        st->code = st->head;
        st->put_state = PUT_HEAD;
        goto put_code;
insert_code_or_clear: /* jump here after put_code */
        if (st->next_code < CODE_LIMIT) {
            st->codes[st->probe] = (st->next_code << 20) |
                                    (st->head << 8) | st->tail;
            if (st->next_code > st->max_code) {
                st->max_code = st->max_code * 2 + 1;
                st->code_width++;
            }
            st->next_code++;
        } else {
            st->code = st->clear_code;
            st->put_state = PUT_CLEAR;
            goto put_code;
reset_after_clear: /* jump here after put_code */
            glzwe_reset(st);
        }
        st->head = st->tail;
        goto encode_loop;

    case LZW_INITIAL:
        glzwe_reset(st);
        st->code = st->clear_code;
        st->put_state = PUT_INIT_CLEAR;
put_code:
        st->code_bits_left = st->code_width;
check_buf_bits:
        if (!st->buf_bits_left) {   /* out buffer full */

    case LZW_TRY_OUT1:
            if (!*out_avail) {
                st->entry_state = LZW_TRY_OUT1;
                return GLZW_NO_OUTPUT_AVAIL;
            }
            *out_ptr++ = st->code_buffer;
            (*out_avail)--;
            st->code_buffer = 0;
            st->buf_bits_left = 8;
        }
        /* code bits to pack */
        UINT32 n = st->buf_bits_left < st->code_bits_left
                        ? st->buf_bits_left : st->code_bits_left;
        st->code_buffer |=
                        (st->code & ((1 << n) - 1)) << (8 - st->buf_bits_left);
        st->code >>= n;
        st->buf_bits_left -= n;
        st->code_bits_left -= n;
        if (st->code_bits_left) {
            goto check_buf_bits;
        }
        switch (st->put_state) {
        case PUT_INIT_CLEAR:
            goto get_first_byte;
        case PUT_HEAD:
            goto insert_code_or_clear;
        case PUT_CLEAR:
            goto reset_after_clear;
        case PUT_LAST_HEAD:
            goto end_of_data;
        case PUT_END:
            goto flush_code_buffer;
        default:
            return GLZW_INTERNAL_ERROR;
        }

end_of_data:
        st->code = st->end_code;
        st->put_state = PUT_END;
        goto put_code;
flush_code_buffer: /* jump here after put_code */
        if (st->buf_bits_left < 8) {

    case LZW_TRY_OUT2:
            if (!*out_avail) {
                st->entry_state = LZW_TRY_OUT2;
                return GLZW_NO_OUTPUT_AVAIL;
            }
            *out_ptr++ = st->code_buffer;
            (*out_avail)--;
        }
        st->entry_state = LZW_FINISHED;
        return GLZW_OK;

    case LZW_FINISHED:
        return GLZW_OK;

    default:
        return GLZW_INTERNAL_ERROR;
    }
}
/* -END- GIF LZW encoder. */

int
ImagingGifEncode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes) {
    UINT8* ptr;
    UINT8* sub_block_ptr;
    UINT8* sub_block_limit;
    UINT8* buf_limit;
    GIFENCODERSTATE *context = (GIFENCODERSTATE*) state->context;
    int r;

    UINT32 in_avail, in_used;
    UINT32 out_avail, out_used;

    if (state->state == INIT) {
        state->state = ENCODE;
        glzwe_init(context);

        if (context->interlace) {
            context->interlace = 1;
            context->step = 8;
        } else {
            context->step = 1;
        }

        /* Need at least 2 bytes for data sub-block; 5 for empty image */
        if (bytes < 5) {
            state->errcode = IMAGING_CODEC_CONFIG;
            return 0;
        }
        /* sanity check */
        if (state->xsize <= 0 || state->ysize <= 0) {
            /* Is this better than an error return? */
            /* This will handle any legal "LZW Minimum Code Size" */
            memset(buf, 0, 5);
            in_avail = 0;
            out_avail = 5;
            r = glzwe(context, (const UINT8 *)"", buf + 1, &in_avail, &out_avail, 1);
            if (r == GLZW_OK) {
                r = 5 - out_avail;
                if (r < 1 || r > 3) {
                    state->errcode = IMAGING_CODEC_BROKEN;
                    return 0;
                }
                buf[0] = r;
                state->errcode = IMAGING_CODEC_END;
                return r + 2;
            } else {
                /* Should not be possible unless something external to this
                 * routine messes with our state data */
                state->errcode = IMAGING_CODEC_BROKEN;
                return 0;
            }
        }
        /* Init state->x to make if() below true the first time through. */
        state->x = state->xsize;
    }

    buf_limit = buf + bytes;
    sub_block_limit = sub_block_ptr = ptr = buf;

    /* On entry, buf is output buffer, bytes is space available in buf.
     * Loop here getting input until buf is full or image is all encoded. */
    for (;;) {
        /* Set up sub-block ptr and limit. sub_block_ptr stays at beginning
         * of sub-block until it is full. ptr will advance when any data is
         * placed in buf.
         */
        if (ptr >= sub_block_limit) {
            if (buf_limit - ptr < 2) { /* Need at least 2 for data sub-block */
                return ptr - buf;
            }
            sub_block_ptr = ptr;
            sub_block_limit = sub_block_ptr +
                (256 < buf_limit - sub_block_ptr ?
                 256 : buf_limit - sub_block_ptr);
            *ptr++ = 0;
        }

        /* Get next row of pixels. */
        /* This if() originally tested state->x==0 for the first time through.
         * This no longer works, as the loop will not advance state->x if
         * glzwe() does not consume any input; this would advance the row
         * spuriously.  Now pre-init state->x above for first time, and avoid
         * entering if() when state->state is FINISH, or it will loop
         * infinitely.
         */
        if (state->x >= state->xsize && state->state == ENCODE) {
            if (!context->interlace && state->y >= state->ysize) {
                state->state = FINISH;
                continue;
            }

            /* get another line of data */
            state->shuffle(
                state->buffer,
                (UINT8*) im->image[state->y + state->yoff] +
                state->xoff * im->pixelsize, state->xsize
            );
            state->x = 0;

            /* step forward, according to the interlace settings */
            state->y += context->step;
            while (context->interlace && state->y >= state->ysize) {
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
        }

        in_avail = state->xsize - state->x;   /* bytes left in line */
        out_avail = sub_block_limit - ptr;  /* bytes left in sub-block */
        r = glzwe(context, &state->buffer[state->x], ptr, &in_avail,
                &out_avail, state->state == FINISH);
        out_used = sub_block_limit - ptr - out_avail;
        *sub_block_ptr += out_used;
        ptr += out_used;
        in_used = state->xsize - state->x - in_avail;
        state->x += in_used;

        if (r == GLZW_OK) {
            /* Should not be possible when end-of-data flag is false. */
            state->errcode = IMAGING_CODEC_END;
            return ptr - buf;
        } else if (r == GLZW_NO_INPUT_AVAIL) {
            /* Used all the input line; get another line */
            continue;
        } else if (r == GLZW_NO_OUTPUT_AVAIL) {
            /* subblock is full */
            continue;
        } else {
            /* Should not be possible unless something external to this
             * routine messes with our state data */
            state->errcode = IMAGING_CODEC_BROKEN;
            return 0;
        }
    }
}
