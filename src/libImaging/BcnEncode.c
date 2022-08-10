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

#define PACK_SHORT_565(r, g, b) \
    ((((r) << 8) & 0xF800) | (((g) << 3) & 0x7E0) | ((b) >> 3))
#define BIT_MASK(bit_count) ((1 << (bit_count)) - 1)
#define SET_BITS(target, bit_offset, bit_count, value) \
    target |= (((value)&BIT_MASK(bit_count)) << (bit_offset))
#define SWAP(TYPE, A, B) \
    do {                 \
        TYPE TMP = A;    \
        A = B;           \
        B = TMP;         \
    } while (0)

static UINT16
rgb565_diff(UINT16 a, UINT16 b) {
    UINT8 r0, g0, b0, r1, g1, b1;
    r0 = a & 31;
    a >>= 5;
    g0 = a & 63;
    a >>= 6;
    b0 = a & 31;
    r1 = b & 31;
    b >>= 5;
    g1 = a & 63;
    b >>= 6;
    b1 = b & 31;

    return abs(r0 - r1) + abs(g0 - g1) + abs(b0 - b1);
}

static inline UINT16
rgb565_lerp(UINT16 a, UINT16 b, UINT8 a_fac, UINT8 b_fac) {
    UINT8 r0, g0, b0, r1, g1, b1;
    r0 = a & 31;
    a >>= 5;
    g0 = a & 63;
    a >>= 6;
    b0 = a & 31;
    r1 = b & 31;
    b >>= 5;
    g1 = b & 63;
    b >>= 6;
    b1 = b & 31;
    return PACK_SHORT_565(
        (r0 * a_fac + r1 * b_fac) / (a_fac + b_fac),
        (g0 * a_fac + g1 * b_fac) / (a_fac + b_fac),
        (b0 * a_fac + b1 * b_fac) / (a_fac + b_fac));
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
    Color colors[16] = {
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    };
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
get_closest_color_index(const UINT16 colors[4], UINT16 color) {
    UINT16 color_error = 65535;
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
ImagingBcnEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    UINT8 *output = buf;
    BOOL has_alpha = 1;
    if (strchr(im->mode, 'A') == NULL)
        has_alpha = 0;
    UINT32 row_block_count = im->xsize / 4;

    UINT16 unique_count = 0;
    UINT16 all_colors[16] = {0};
    UINT16 unique_colors[16] = {0};
    UINT8 color_frequency[16] = {0};

    for (int block_x = 0; block_x < row_block_count; ++block_x) {
        for (int by = 0; by < 4; ++by) {
            for (int bx = 0; bx < 16; bx += 4) {
                UINT8 r = (im->image[state->y + by][bx]);
                UINT8 g = (im->image[state->y + by][bx + 1]);
                UINT8 b = (im->image[state->y + by][bx] + 2);
                UINT16 color = PACK_SHORT_565(r, g, b);
                all_colors[bx + by * 4] = color;
                BOOL new_color = 1;
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

        UINT16 color0 = 0, color1 = 0;
        pick_2_major_colors(
            unique_colors, color_frequency, unique_count, &color0, &color1);
        if (color0 < color1)
            SWAP(UINT16, color0, color1);

        UINT16 output_colors[4] = {color0, color1, 0, 0};
        if (has_alpha) {
            output_colors[2] = rgb565_lerp(color0, color1, 1, 1);
            output_colors[3] = 0;
        } else {
            output_colors[2] = rgb565_lerp(color0, color1, 2, 1);
            output_colors[3] = rgb565_lerp(color0, color1, 1, 2);
        }
        bc1_color *block = &((bc1_color *)output)[block_x];

        block->c0 = color0;
        block->c1 = color1;
        for (UINT32 color_id = 0; color_id < 16; ++color_id) {
            UINT8 bc_color_id =
                get_closest_color_index(output_colors, all_colors[color_id]);
            SET_BITS(block->lut, color_id * 2, 2, bc_color_id);
        }

        output += sizeof(bc1_color);
    }

    return output - buf;
}
