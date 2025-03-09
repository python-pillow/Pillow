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

#include "Bcn.h"

typedef struct {
    UINT8 color[3];
} rgb;

typedef struct {
    UINT8 color[3];
    int alpha;
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

int
ImagingBcnEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes) {
    UINT8 *dst = buf;

    for (;;) {
        int i, j, k;
        UINT16 color_min = 0, color_max = 0;
        rgb color_min_rgb, color_max_rgb;
        rgba block[16], *current_rgba;

        // Determine the min and max colors in this 4x4 block
        int has_alpha_channel =
            strcmp(im->mode, "RGBA") == 0 || strcmp(im->mode, "LA") == 0;
        int first = 1;
        int transparency = 0;
        for (i = 0; i < 4; i++) {
            for (j = 0; j < 4; j++) {
                int x = state->x + i * im->pixelsize;
                int y = state->y + j;
                if (x >= state->xsize * im->pixelsize || y >= state->ysize) {
                    // The 4x4 block extends past the edge of the image
                    continue;
                }

                current_rgba = &block[i + j * 4];
                for (k = 0; k < 3; k++) {
                    current_rgba->color[k] =
                        (UINT8)im->image[y][x + (im->pixelsize == 1 ? 0 : k)];
                }
                if (has_alpha_channel) {
                    if ((UINT8)im->image[y][x + 3] == 0) {
                        current_rgba->alpha = 0;
                        transparency = 1;
                        continue;
                    } else {
                        current_rgba->alpha = 1;
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
                if (transparency && !current_rgba->alpha) {
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
                            abs(current_rgba->color[k] - color_min_rgb.color[k]) /
                            denom;
                        total += 1;
                    }
                }
                if (total == 0) {
                    continue;
                }
                distance *= 6 / total;
                if (transparency) {
                    if (distance < 1.5) {
                        // color_max
                    } else if (distance < 4.5) {
                        l |= 2 << (j * 2);  // 1/2 * color_min + 1/2 * color_max
                    } else {
                        l |= 1 << (j * 2);  // color_min
                    }
                } else {
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
