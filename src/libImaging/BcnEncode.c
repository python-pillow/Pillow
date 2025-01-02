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
    ((((b) << 8) & 0xF800) | (((g) << 3) & 0x7E0) | ((r) >> 3))

#define UNPACK_SHORT_565(source, r, g, b) \
    (r) = GET_BITS((source), 0, 5);       \
    (g) = GET_BITS((source), 5, 6);       \
    (b) = GET_BITS((source), 11, 5);

#define WRITE_SHORT(buf, value) \
    *(buf++) = value & 0xFF;    \
    *(buf++) = value >> 8;

#define WRITE_INT(buf, value)        \
    WRITE_SHORT(buf, value & 0xFFFF) \
    WRITE_SHORT(buf, value >> 16)

#define WRITE_BC1_BLOCK(buf, block) \
    WRITE_SHORT(buf, block.c0)      \
    WRITE_SHORT(buf, block.c1)      \
    WRITE_INT(buf, block.lut)

static inline UINT16
rgb565_diff(UINT16 c0, UINT16 c1) {
    UINT8 r0, g0, b0, r1, g1, b1;
    UNPACK_SHORT_565(c0, r0, g0, b0)
    UNPACK_SHORT_565(c1, r1, g1, b1)
    return ((UINT16)abs(r0 - r1)) + abs(g0 - g1) + abs(b0 - b1);
}

static inline UINT16
rgb565_lerp(UINT16 c0, UINT16 c1, UINT8 a_fac, UINT8 b_fac) {
    UINT8 r0, g0, b0, r1, g1, b1;
    UNPACK_SHORT_565(c0, r0, g0, b0)
    UNPACK_SHORT_565(c1, r1, g1, b1)
    return PACK_SHORT_565(
        (r0 * a_fac + r1 * b_fac) / (a_fac + b_fac),
        (g0 * a_fac + g1 * b_fac) / (a_fac + b_fac),
        (b0 * a_fac + b1 * b_fac) / (a_fac + b_fac)
    );
}

typedef struct {
    UINT16 value;
    UINT8 frequency;
} Color;

static void
selection_sort(Color arr[], UINT32 n) {
    UINT32 min_idx, i, j;

    for (i = 0; i < n - 1; i++) {
        min_idx = i;
        for (j = i + 1; j < n; j++) {
            if (arr[j].frequency < arr[min_idx].frequency) {
                min_idx = j;
            }
        }
        SWAP(Color, arr[min_idx], arr[i]);
    }
}

static void
pick_2_major_colors(
    const UINT16 *unique_colors,
    const UINT8 *color_freq,
    UINT16 color_count,
    UINT16 *color0,
    UINT16 *color1
) {
    UINT32 i;
    Color colors[16];
    memset(colors, 0, sizeof(colors));
    for (i = 0; i < color_count; ++i) {
        colors[i].value = unique_colors[i];
        colors[i].frequency = color_freq[i];
    }
    selection_sort(colors, color_count);
    *color0 = colors[color_count - 1].value;

    if (color_count == 1) {
        *color1 = colors[color_count - 1].value;
    } else {
        *color1 = colors[color_count - 2].value;
    }
}

static UINT8
get_closest_color_index(const UINT16 *colors, UINT16 color) {
    UINT16 color_error = 0xFFF8;
    UINT16 lowest_id = 0;
    UINT32 color_id;

    for (color_id = 0; color_id < 4; color_id++) {
        UINT8 error = rgb565_diff(colors[color_id], color);
        if (error == 0) {
            return color_id;
        }
        if (error <= color_error) {
            color_error = error;
            lowest_id = color_id;
        }
    }
    return lowest_id;
}

int
encode_bc1(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    UINT8 *dst = buf;
    UINT8 alpha = 0;
    INT32 block_index;
    if (strcmp(((BCNSTATE *)state->context)->pixel_format, "DXT1A") == 0) {
        alpha = 1;
    }
    INT32 block_count = (im->xsize * im->ysize) / 16;
    if (block_count * sizeof(bc1_color) > bytes) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return 0;
    }

    memset(buf, 0, block_count * sizeof(bc1_color));
    for (block_index = 0; block_index < block_count; block_index++) {
        state->x = (block_index % (im->xsize / 4));
        state->y = (block_index / (im->xsize / 4));
        UINT16 unique_count = 0;

        UINT16 all_colors[16];
        UINT16 unique_colors[16];
        UINT8 color_frequency[16];
        UINT8 opaque[16];
        UINT8 local_alpha = 0;
        memset(all_colors, 0, sizeof(all_colors));
        memset(unique_colors, 0, sizeof(unique_colors));
        memset(color_frequency, 0, sizeof(color_frequency));
        memset(opaque, 0, sizeof(opaque));
        UINT32 by, bx, x, y;
        for (by = 0; by < 4; ++by) {
            for (bx = 0; bx < 4; ++bx) {
                x = (state->x * 4) + bx;
                y = (state->y * 4) + by;
                UINT8 r = im->image[y][x * im->pixelsize + 2];
                UINT8 g = im->image[y][x * im->pixelsize + 1];
                UINT8 b = im->image[y][x * im->pixelsize + 0];
                UINT8 a = im->image[y][x * im->pixelsize + 3];
                UINT16 color = PACK_SHORT_565(r, g, b);
                opaque[bx + by * 4] = a >= 128;
                local_alpha |= a <= 128;
                all_colors[bx + by * 4] = color;

                UINT8 new_color = 1;
                UINT16 color_id = 1;
                for (color_id = 0; color_id < unique_count; color_id++) {
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
        if (alpha && local_alpha) {
            if (c0 > c1) {
                SWAP(UINT16, c0, c1);
            }
        } else {
            if (c0 < c1) {
                SWAP(UINT16, c0, c1);
            }
        }

        UINT16 palette[4] = {c0, c1, 0, 0};
        if (alpha && local_alpha) {
            palette[2] = rgb565_lerp(c0, c1, 1, 1);
            palette[3] = 0;
        } else {
            palette[2] = rgb565_lerp(c0, c1, 2, 1);
            palette[3] = rgb565_lerp(c0, c1, 1, 2);
        }
        bc1_color block = {0};
        block.c0 = c0;
        block.c1 = c1;
        UINT32 color_id;
        for (color_id = 0; color_id < 16; ++color_id) {
            UINT8 bc_color_id;
            if ((alpha && local_alpha) && !opaque[color_id]) {
                bc_color_id = 3;
            } else {
                bc_color_id = get_closest_color_index(palette, all_colors[color_id]);
            }
            SET_BITS(block.lut, color_id * 2, 2, bc_color_id);
        }
        WRITE_BC1_BLOCK(dst, block)
    }
    state->errcode = IMAGING_CODEC_END;
    return dst - buf;
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
