/*
 * The Python Imaging Library.
 * $Id$
 *
 * encoder for packed bitfields (ST3C/DXT)
 *
 * history:
 * 22-08-11 Initial implementation
 *
 * Copyright (c) REDxEYE 2022.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"
#include "Bcn.h"
#include "math.h"

#define BIT_MASK(bit_count) ((1 << (bit_count)) - 1)
#define SET_BITS(target, bit_offset, bit_count, value) \
    target |= (((value)&BIT_MASK(bit_count)) << (bit_offset))
#define SWAP(TYPE, A, B) \
    do {                 \
        TYPE TMP = A;    \
        A = B;           \
        B = TMP;         \
    } while (0)

typedef union {
    struct {
        UINT16 r : 5;
        UINT16 g : 6;
        UINT16 b : 5;
    } color;
    UINT16 value;
} rgb565;

static UINT16
pack_565(UINT8 r, UINT8 g, UINT8 b) {
    rgb565 color;
    color.color.r = r / (255 / 31);
    color.color.g = g / (255 / 63);
    color.color.b = b / (255 / 31);
    return color.value;
}

static UINT16
rgb565_diff(UINT16 a, UINT16 b) {
    rgb565 c0;
    c0.value = a;
    rgb565 c1;
    c1.value = b;
    return ((UINT16)abs(c0.color.r - c1.color.r)) + abs(c0.color.g - c1.color.g) +
           abs(c0.color.b - c1.color.b);
}

static inline UINT16
rgb565_lerp(UINT16 a, UINT16 b, UINT8 a_fac, UINT8 b_fac) {
    rgb565 c0;
    c0.value = a;
    rgb565 c1;
    c1.value = b;
    return pack_565(
        (c0.color.r * a_fac + c1.color.r * b_fac) / (a_fac + b_fac),
        (c0.color.g * a_fac + c1.color.g * b_fac) / (a_fac + b_fac),
        (c0.color.b * a_fac + c1.color.b * b_fac) / (a_fac + b_fac));
}

typedef struct {
    UINT16 value;
    UINT8 frequency;
} Color;

static void
selection_sort(Color arr[], uint32_t n) {
    uint32_t min_idx;

    for (uint32_t i = 0; i < n - 1; i++) {
        min_idx = i;
        for (uint32_t j = i + 1; j < n; j++)
            if (arr[j].frequency < arr[min_idx].frequency)
                min_idx = j;
        SWAP(Color, arr[min_idx], arr[i]);
    }
}

static void
pick_2_major_colors(
    const UINT16 *unique_colors,
    const UINT8 *color_freq,
    UINT16 color_count,
    UINT16 *color0,
    UINT16 *color1) {
    Color colors[16];
    memset(colors, 0, sizeof(colors));
    for (int i = 0; i < color_count; ++i) {
        colors[i].value = unique_colors[i];
        colors[i].frequency = color_freq[i];
    }
    selection_sort(colors, color_count);
    *color0 = colors[color_count - 1].value;

    if (color_count == 1) {
        *color1 = colors[color_count - 1].value;
    } else
        *color1 = colors[color_count - 2].value;
}

static UINT8
get_closest_color_index(const UINT16 *colors, UINT16 color) {
    UINT16 color_error = 0xFFF8;
    UINT16 lowest_id = 0;

    for (int color_id = 0; color_id < 4; color_id++) {
        UINT8 error = rgb565_diff(colors[color_id], color);
        if (error == 0) {
            return color_id;
        }
        if (error < color_error) {
            color_error = error;
            lowest_id = color_id;
        }
    }
    return lowest_id;
}

int
encode_bc1(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    bc1_color *blocks = (bc1_color *)buf;
    UINT8 no_alpha = 0;
    if (strchr(im->mode, 'A') == NULL)
        no_alpha = 1;
    UINT32 block_count = (im->xsize * im->ysize) / 16;
    if (block_count * sizeof(bc1_color) > bytes) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return 0;
    }

    memset(buf, 0, block_count * sizeof(bc1_color));
    for (int block_index = 0; block_index < block_count; block_index++) {
        state->x = (block_index % (im->xsize / 4));
        state->y = (block_index / (im->xsize / 4));
        UINT16 unique_count = 0;

        UINT16 all_colors[16];
        UINT16 unique_colors[16];
        UINT8 color_frequency[16];
        UINT8 opaque[16];
        memset(all_colors, 0, sizeof(all_colors));
        memset(unique_colors, 0, sizeof(unique_colors));
        memset(color_frequency, 0, sizeof(color_frequency));
        memset(opaque, 0, sizeof(opaque));

        for (int by = 0; by < 4; ++by) {
            for (int bx = 0; bx < 4; ++bx) {
                int x = (state->x * 4) + bx;
                int y = (state->y * 4) + by;
                UINT8 r = im->image[y][x * im->pixelsize + 2];
                UINT8 g = im->image[y][x * im->pixelsize + 1];
                UINT8 b = im->image[y][x * im->pixelsize + 0];
                UINT8 a = im->image[y][x * im->pixelsize + 3];
                UINT16 color = pack_565(r, g, b);
                opaque[bx + by * 4] = a >= 127;
                all_colors[bx + by * 4] = color;

                int new_color = 1;
                for (UINT16 color_id = 0; color_id < unique_count; color_id++) {
                    if (unique_colors[color_id] == color) {
                        color_frequency[color_id]++;
                        new_color = 0;
                        break;
                    }
                }
                if (new_color) {
                    unique_colors[unique_count] = color;
                    color_frequency[unique_count]++;
                    unique_count++;
                }
            }
        }

        UINT16 c0 = 0, c1 = 0;
        pick_2_major_colors(unique_colors, color_frequency, unique_count, &c0, &c1);
        if (c0 < c1 && no_alpha)
            SWAP(UINT16, c0, c1);

        UINT16 palette[4] = {c0, c1, 0, 0};
        if (no_alpha) {
            palette[2] = rgb565_lerp(c0, c1, 2, 1);
            palette[3] = rgb565_lerp(c0, c1, 1, 2);
        } else {
            palette[2] = rgb565_lerp(c0, c1, 1, 1);
            palette[3] = 0;
        }
        bc1_color *block = &blocks[block_index];

        block->c0 = c0;
        block->c1 = c1;
        for (UINT32 color_id = 0; color_id < 16; ++color_id) {
            UINT8 bc_color_id;
            if (opaque[color_id] || no_alpha)
                bc_color_id = get_closest_color_index(palette, all_colors[color_id]);
            else
                bc_color_id = 3;
            SET_BITS(block->lut, color_id * 2, 2, bc_color_id);
        }
    }
    state->errcode = IMAGING_CODEC_END;
    return block_count * sizeof(bc1_color);
}

int
ImagingBcnEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    switch (state->state) {
        case 1: {
            return encode_bc1(im, state, buf, bytes);
        }
        default: {
            state->errcode = IMAGING_CODEC_CONFIG;
            return 0;
        }
    }
}
