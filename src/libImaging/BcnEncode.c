/*
 * The Python Imaging Library
 *
 * encoder for DXT1-compressed data
 *
 * Format documentation:
 *   https://web.archive.org/web/20170802060935/http://oss.sgi.com/projects/ogl-sample/registry/EXT/texture_compression_s3tc.txt
 *
 */

#include "Imaging.h"

typedef struct {
    UINT8 color[3];
} rgb;

typedef struct {
    UINT8 color[4];
} rgba;

static rgb
decode_565(UINT16 x) {
    rgb item;
    int r, g, b;
    r = (x & 0xf800) >> 8;
    r |= r >> 5;
    item.color[0] = r;
    g = (x & 0x7e0) >> 3;
    g |= g >> 6;
    item.color[1] = g;
    b = (x & 0x1f) << 3;
    b |= b >> 5;
    item.color[2] = b;
    return item;
}

static UINT16
encode_565(rgba item) {
    UINT8 r, g, b;
    r = item.color[0] >> (8 - 5);
    g = item.color[1] >> (8 - 6);
    b = item.color[2] >> (8 - 5);
    return (r << (5 + 6)) | (g << 5) | b;
}

static void
encode_bc1_color(Imaging im, ImagingCodecState state, UINT8 *dst, int separate_alpha) {
    int i, j, k;
    UINT16 color_min = 0, color_max = 0;
    rgb color_min_rgb, color_max_rgb;
    rgba block[16], *current_rgba;

    // Determine the min and max colors in this 4x4 block
    int first = 1;
    int transparency = 0;
    for (i = 0; i < 4; i++) {
        for (j = 0; j < 4; j++) {
            current_rgba = &block[i + j * 4];

            int x = state->x + i * im->pixelsize;
            int y = state->y + j;
            if (x >= state->xsize * im->pixelsize || y >= state->ysize) {
                // The 4x4 block extends past the edge of the image
                for (k = 0; k < 3; k++) {
                    current_rgba->color[k] = 0;
                }
                continue;
            }

            for (k = 0; k < 3; k++) {
                current_rgba->color[k] =
                    (UINT8)im->image[y][x + (im->pixelsize == 1 ? 0 : k)];
            }
            if (separate_alpha) {
                if ((UINT8)im->image[y][x + 3] == 0) {
                    current_rgba->color[3] = 0;
                    transparency = 1;
                    continue;
                } else {
                    current_rgba->color[3] = 1;
                }
            }

            UINT16 color = encode_565(*current_rgba);
            if (first || color < color_min) {
                color_min = color;
            }
            if (first || color > color_max) {
                color_max = color;
            }
            first = 0;
        }
    }

    if (transparency) {
        *dst++ = color_min;
        *dst++ = color_min >> 8;
    }
    *dst++ = color_max;
    *dst++ = color_max >> 8;
    if (!transparency) {
        *dst++ = color_min;
        *dst++ = color_min >> 8;
    }

    color_min_rgb = decode_565(color_min);
    color_max_rgb = decode_565(color_max);
    for (i = 0; i < 4; i++) {
        UINT8 l = 0;
        for (j = 3; j > -1; j--) {
            current_rgba = &block[i * 4 + j];
            if (transparency && !current_rgba->color[3]) {
                l |= 3 << (j * 2);
                continue;
            }

            float distance = 0;
            int total = 0;
            for (k = 0; k < 3; k++) {
                float denom =
                    (float)abs(color_max_rgb.color[k] - color_min_rgb.color[k]);
                if (denom != 0) {
                    distance +=
                        abs(current_rgba->color[k] - color_min_rgb.color[k]) / denom;
                    total += 1;
                }
            }
            if (total == 0) {
                continue;
            }
            if (transparency) {
                distance *= 4 / total;
                if (distance < 1) {
                    // color_max
                } else if (distance < 3) {
                    l |= 2 << (j * 2);  // 1/2 * color_min + 1/2 * color_max
                } else {
                    l |= 1 << (j * 2);  // color_min
                }
            } else {
                distance *= 6 / total;
                if (distance < 1) {
                    l |= 1 << (j * 2);  // color_min
                } else if (distance < 3) {
                    l |= 3 << (j * 2);  // 1/3 * color_min + 2/3 * color_max
                } else if (distance < 5) {
                    l |= 2 << (j * 2);  // 2/3 * color_min + 1/3 * color_max
                } else {
                    // color_max
                }
            }
        }
        *dst++ = l;
    }
}

static void
encode_bc2_block(Imaging im, ImagingCodecState state, UINT8 *dst) {
    int i, j;
    UINT8 block[16], current_alpha;
    for (i = 0; i < 4; i++) {
        for (j = 0; j < 4; j++) {
            int x = state->x + i * im->pixelsize;
            int y = state->y + j;
            if (x >= state->xsize * im->pixelsize || y >= state->ysize) {
                // The 4x4 block extends past the edge of the image
                block[i + j * 4] = 0;
                continue;
            }

            current_alpha = (UINT8)im->image[y][x + 3];
            block[i + j * 4] = current_alpha;
        }
    }

    for (i = 0; i < 4; i++) {
        UINT16 l = 0;
        for (j = 3; j > -1; j--) {
            current_alpha = block[i * 4 + j];
            l |= current_alpha << (j * 4);
        }
        *dst++ = l;
        *dst++ = l >> 8;
    }
}

static void
encode_bc3_alpha(Imaging im, ImagingCodecState state, UINT8 *dst, int o) {
    int i, j;
    UINT8 alpha_min = 0, alpha_max = 0;
    UINT8 block[16], current_alpha;

    // Determine the min and max colors in this 4x4 block
    int first = 1;
    for (i = 0; i < 4; i++) {
        for (j = 0; j < 4; j++) {
            int x = state->x + i * im->pixelsize;
            int y = state->y + j;
            if (x >= state->xsize * im->pixelsize || y >= state->ysize) {
                // The 4x4 block extends past the edge of the image
                block[i + j * 4] = 0;
                continue;
            }

            current_alpha = (UINT8)im->image[y][x + o];
            block[i + j * 4] = current_alpha;

            if (first || current_alpha < alpha_min) {
                alpha_min = current_alpha;
            }
            if (first || current_alpha > alpha_max) {
                alpha_max = current_alpha;
            }
            first = 0;
        }
    }

    *dst++ = alpha_min;
    *dst++ = alpha_max;

    float denom = (float)abs(alpha_max - alpha_min);
    for (i = 0; i < 2; i++) {
        UINT32 l = 0;
        for (j = 7; j > -1; j--) {
            current_alpha = block[i * 8 + j];
            if (!current_alpha) {
                l |= 6 << (j * 3);
                continue;
            } else if (current_alpha == 255) {
                l |= 7 << (j * 3);
                continue;
            }

            float distance =
                denom == 0 ? 0 : abs(current_alpha - alpha_min) / denom * 10;
            if (distance < 3) {
                l |= 2 << (j * 3);  // 4/5 * alpha_min + 1/5 * alpha_max
            } else if (distance < 5) {
                l |= 3 << (j * 3);  // 3/5 * alpha_min + 2/5 * alpha_max
            } else if (distance < 7) {
                l |= 4 << (j * 3);  // 2/5 * alpha_min + 3/5 * alpha_max
            } else {
                l |= 5 << (j * 3);  // 1/5 * alpha_min + 4/5 * alpha_max
            }
        }
        *dst++ = l;
        *dst++ = l >> 8;
        *dst++ = l >> 16;
    }
}

int
ImagingBcnEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    int n = state->state;
    int has_alpha_channel =
        strcmp(im->mode, "RGBA") == 0 || strcmp(im->mode, "LA") == 0;

    UINT8 *dst = buf;

    for (;;) {
        // Loop writes a max of 16 bytes per iteration
        if (dst + 16 >= bytes + buf) {
            break;
        }
        if (n == 5) {
            encode_bc3_alpha(im, state, dst, 0);
            dst += 8;

            encode_bc3_alpha(im, state, dst, 1);
        } else {
            if (n == 2 || n == 3) {
                if (has_alpha_channel) {
                    if (n == 2) {
                        encode_bc2_block(im, state, dst);
                    } else {
                        encode_bc3_alpha(im, state, dst, 3);
                    }
                    dst += 8;
                } else {
                    for (int i = 0; i < 8; i++) {
                        *dst++ = 0xff;
                    }
                }
            }
            encode_bc1_color(im, state, dst, n == 1 && has_alpha_channel);
        }
        dst += 8;

        state->x += im->pixelsize * 4;

        if (state->x >= state->xsize * im->pixelsize) {
            state->x = 0;
            state->y += 4;
            if (state->y >= state->ysize) {
                state->errcode = IMAGING_CODEC_END;
                break;
            }
        }
    }

    return dst - buf;
}
