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
    UINT16 out = in[0] + ((UINT16)in[1] << 8);
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
    UINT16 out = in[1] + ((UINT16)in[0] << 8);
    memcpy(color, &out, sizeof(out));
#endif
}

static void
get_pixel_32(Imaging im, int x, int y, void *color) {
    memcpy(color, &im->image32[y][x], sizeof(INT32));
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
put_pixel_32(Imaging im, int x, int y, const void *color) {
    memcpy(&im->image32[y][x], color, sizeof(INT32));
}

static struct ImagingAccessInstance accessors[] = {
    {IMAGING_MODE_1, get_pixel_8, put_pixel_8},
    {IMAGING_MODE_L, get_pixel_8, put_pixel_8},
    {IMAGING_MODE_LA, get_pixel_32_2bands, put_pixel_32},
    {IMAGING_MODE_La, get_pixel_32_2bands, put_pixel_32},
    {IMAGING_MODE_I, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_I_16, get_pixel_16L, put_pixel_16L},
    {IMAGING_MODE_I_16L, get_pixel_16L, put_pixel_16L},
    {IMAGING_MODE_I_16B, get_pixel_16B, put_pixel_16B},
#ifdef WORDS_BIGENDIAN
    {IMAGING_MODE_I_16N, get_pixel_16B, put_pixel_16B},
#else
    {IMAGING_MODE_I_16N, get_pixel_16L, put_pixel_16L},
#endif
    {IMAGING_MODE_F, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_P, get_pixel_8, put_pixel_8},
    {IMAGING_MODE_PA, get_pixel_32_2bands, put_pixel_32},
    {IMAGING_MODE_RGB, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_RGBA, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_RGBa, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_RGBX, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_CMYK, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_YCbCr, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_LAB, get_pixel_32, put_pixel_32},
    {IMAGING_MODE_HSV, get_pixel_32, put_pixel_32},
};

ImagingAccess
ImagingAccessNew(const Imaging im) {
    for (size_t i = 0; i < sizeof(accessors) / sizeof(*accessors); i++) {
        if (im->mode == accessors[i].mode) {
            return &accessors[i];
        }
    }
    return NULL;
}

void
_ImagingAccessDelete(Imaging im, ImagingAccess access) {}
