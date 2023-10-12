/*
 * The Python Imaging Library
 * $Id$
 *
 * imaging access objects
 *
 * Copyright (c) Fredrik Lundh 2009.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/* use make_hash.py from the pillow-scripts repository to calculate these values */
#define ACCESS_TABLE_SIZE 35
#define ACCESS_TABLE_HASH 8940

static struct ImagingAccessInstance access_table[ACCESS_TABLE_SIZE];

static inline UINT32
hash(const char *mode) {
    UINT32 i = ACCESS_TABLE_HASH;
    while (*mode) {
        i = ((i << 5) + i) ^ (UINT8)*mode++;
    }
    return i % ACCESS_TABLE_SIZE;
}

static ImagingAccess
add_item(const char *mode) {
    UINT32 i = hash(mode);
    /* printf("hash %s => %d\n", mode, i); */
    if (access_table[i].mode && strcmp(access_table[i].mode, mode) != 0) {
        fprintf(
            stderr,
            "AccessInit: hash collision: %d for both %s and %s\n",
            i,
            mode,
            access_table[i].mode);
        exit(1);
    }
    access_table[i].mode = mode;
    return &access_table[i];
}

/* fetch individual pixel */

static void
get_pixel_32_2bands(Imaging im, int x, int y, void *color) {
    char *out = color;
    UINT8 *p = (UINT8 *)&im->image32[y][x];
    out[0] = p[0];
    out[1] = p[3];
}

static void
get_pixel_8(Imaging im, int x, int y, void *color) {
    char *out = color;
    out[0] = im->image8[y][x];
}

static void
get_pixel_16L(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image[y][x + x];
#ifdef WORDS_BIGENDIAN
    UINT16 out = in[0] + (in[1] << 8);
    memcpy(color, &out, sizeof(out));
#else
    memcpy(color, in, sizeof(UINT16));
#endif
}

static void
get_pixel_16B(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image[y][x + x];
#ifdef WORDS_BIGENDIAN
    memcpy(color, in, sizeof(UINT16));
#else
    UINT16 out = in[1] + (in[0] << 8);
    memcpy(color, &out, sizeof(out));
#endif
}

static void
get_pixel_16(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image[y][x + x];
    memcpy(color, in, sizeof(UINT16));
}

static void
get_pixel_BGR15(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image8[y][x * 2];
    UINT16 pixel = in[0] + (in[1] << 8);
    char *out = color;
    out[0] = (pixel & 31) * 255 / 31;
    out[1] = ((pixel >> 5) & 31) * 255 / 31;
    out[2] = ((pixel >> 10) & 31) * 255 / 31;
}

static void
get_pixel_BGR16(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image8[y][x * 2];
    UINT16 pixel = in[0] + (in[1] << 8);
    char *out = color;
    out[0] = (pixel & 31) * 255 / 31;
    out[1] = ((pixel >> 5) & 63) * 255 / 63;
    out[2] = ((pixel >> 11) & 31) * 255 / 31;
}

static void
get_pixel_BGR24(Imaging im, int x, int y, void *color) {
    memcpy(color, &im->image8[y][x * 3], sizeof(UINT8) * 3);
}

static void
get_pixel_32(Imaging im, int x, int y, void *color) {
    memcpy(color, &im->image32[y][x], sizeof(INT32));
}

static void
get_pixel_32L(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image[y][x * 4];
#ifdef WORDS_BIGENDIAN
    INT32 out = in[0] + (in[1] << 8) + (in[2] << 16) + (in[3] << 24);
    memcpy(color, &out, sizeof(out));
#else
    memcpy(color, in, sizeof(INT32));
#endif
}

static void
get_pixel_32B(Imaging im, int x, int y, void *color) {
    UINT8 *in = (UINT8 *)&im->image[y][x * 4];
#ifdef WORDS_BIGENDIAN
    memcpy(color, in, sizeof(INT32));
#else
    INT32 out = in[3] + (in[2] << 8) + (in[1] << 16) + (in[0] << 24);
    memcpy(color, &out, sizeof(out));
#endif
}

/* store individual pixel */

static void
put_pixel_8(Imaging im, int x, int y, const void *color) {
    im->image8[y][x] = *((UINT8 *)color);
}

static void
put_pixel_16L(Imaging im, int x, int y, const void *color) {
    memcpy(&im->image8[y][x + x], color, 2);
}

static void
put_pixel_16B(Imaging im, int x, int y, const void *color) {
    const char *in = color;
    UINT8 *out = (UINT8 *)&im->image8[y][x + x];
    out[0] = in[1];
    out[1] = in[0];
}

static void
put_pixel_BGR1516(Imaging im, int x, int y, const void *color) {
    memcpy(&im->image8[y][x * 2], color, 2);
}

static void
put_pixel_BGR24(Imaging im, int x, int y, const void *color) {
    memcpy(&im->image8[y][x * 3], color, 3);
}

static void
put_pixel_32L(Imaging im, int x, int y, const void *color) {
    memcpy(&im->image8[y][x * 4], color, 4);
}

static void
put_pixel_32B(Imaging im, int x, int y, const void *color) {
    const char *in = color;
    UINT8 *out = (UINT8 *)&im->image8[y][x * 4];
    out[0] = in[3];
    out[1] = in[2];
    out[2] = in[1];
    out[3] = in[0];
}

static void
put_pixel_32(Imaging im, int x, int y, const void *color) {
    memcpy(&im->image32[y][x], color, sizeof(INT32));
}

void
ImagingAccessInit() {
#define ADD(mode_, get_pixel_, put_pixel_)        \
    {                                             \
        ImagingAccess access = add_item(mode_);   \
        access->get_pixel = get_pixel_;           \
        access->put_pixel = put_pixel_;           \
    }

    /* populate access table */
    ADD("1", get_pixel_8, put_pixel_8);
    ADD("L", get_pixel_8, put_pixel_8);
    ADD("LA", get_pixel_32_2bands, put_pixel_32);
    ADD("La", get_pixel_32_2bands, put_pixel_32);
    ADD("I", get_pixel_32, put_pixel_32);
    ADD("I;16", get_pixel_16L, put_pixel_16L);
    ADD("I;16L", get_pixel_16L, put_pixel_16L);
    ADD("I;16B", get_pixel_16B, put_pixel_16B);
    ADD("I;16N", get_pixel_16, put_pixel_16L);
    ADD("I;32L", get_pixel_32L, put_pixel_32L);
    ADD("I;32B", get_pixel_32B, put_pixel_32B);
    ADD("F", get_pixel_32, put_pixel_32);
    ADD("P", get_pixel_8, put_pixel_8);
    ADD("PA", get_pixel_32_2bands, put_pixel_32);
    ADD("BGR;15", get_pixel_BGR15, put_pixel_BGR1516);
    ADD("BGR;16", get_pixel_BGR16, put_pixel_BGR1516);
    ADD("BGR;24", get_pixel_BGR24, put_pixel_BGR24);
    ADD("RGB", get_pixel_32, put_pixel_32);
    ADD("RGBA", get_pixel_32, put_pixel_32);
    ADD("RGBa", get_pixel_32, put_pixel_32);
    ADD("RGBX", get_pixel_32, put_pixel_32);
    ADD("CMYK", get_pixel_32, put_pixel_32);
    ADD("YCbCr", get_pixel_32, put_pixel_32);
    ADD("LAB", get_pixel_32, put_pixel_32);
    ADD("HSV", get_pixel_32, put_pixel_32);
}

ImagingAccess
ImagingAccessNew(Imaging im) {
    ImagingAccess access = &access_table[hash(im->mode)];
    if (im->mode[0] != access->mode[0] || strcmp(im->mode, access->mode) != 0) {
        return NULL;
    }
    return access;
}

void
_ImagingAccessDelete(Imaging im, ImagingAccess access) {}
