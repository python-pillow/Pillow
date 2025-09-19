/*
 * The Python Imaging Library.
 * $Id$
 *
 * code to pack raw data
 *
 * history:
 * 1996-04-30 fl   Created
 * 1996-05-12 fl   Published a few RGB packers
 * 1996-11-01 fl   More RGB packers (Tk booster stuff)
 * 1996-12-30 fl   Added P;1, P;2 and P;4 packers
 * 1997-06-02 fl   Added F (F;32NF) packer
 * 1997-08-28 fl   Added 1 as L packer
 * 1998-02-08 fl   Added I packer
 * 1998-03-09 fl   Added mode field, RGBA/RGBX as RGB packers
 * 1998-07-01 fl   Added YCbCr support
 * 1998-07-12 fl   Added I 16 packer
 * 1999-02-03 fl   Added BGR packers
 * 2003-09-26 fl   Added LA/PA packers
 * 2006-06-22 fl   Added CMYK;I packer
 *
 * Copyright (c) 1997-2006 by Secret Labs AB.
 * Copyright (c) 1996-1997 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#define R 0
#define G 1
#define B 2
#define X 3
#define A 3

#define C 0
#define M 1
#define Y 2
#define K 3

/* byte swapping macros */

#define C16N (out[0] = tmp[0], out[1] = tmp[1]);
#define C16S (out[1] = tmp[0], out[0] = tmp[1]);
#define C32N (out[0] = tmp[0], out[1] = tmp[1], out[2] = tmp[2], out[3] = tmp[3]);
#define C32S (out[3] = tmp[0], out[2] = tmp[1], out[1] = tmp[2], out[0] = tmp[3]);
#define C64N          \
    (out[0] = tmp[0], \
     out[1] = tmp[1], \
     out[2] = tmp[2], \
     out[3] = tmp[3], \
     out[4] = tmp[4], \
     out[5] = tmp[5], \
     out[6] = tmp[6], \
     out[7] = tmp[7]);
#define C64S          \
    (out[7] = tmp[0], \
     out[6] = tmp[1], \
     out[5] = tmp[2], \
     out[4] = tmp[3], \
     out[3] = tmp[4], \
     out[2] = tmp[5], \
     out[1] = tmp[6], \
     out[0] = tmp[7]);

#ifdef WORDS_BIGENDIAN
#define C16B C16N
#define C16L C16S
#define C32B C32N
#define C32L C32S
#define C64B C64N
#define C64L C64S
#else
#define C16B C16S
#define C16L C16N
#define C32B C32S
#define C32L C32N
#define C64B C64S
#define C64L C64N
#endif

static void
pack1(UINT8 *out, const UINT8 *in, int pixels) {
    int i, m, b;
    /* bilevel (black is 0) */
    b = 0;
    m = 128;
    for (i = 0; i < pixels; i++) {
        if (in[i] != 0) {
            b |= m;
        }
        m >>= 1;
        if (m == 0) {
            *out++ = b;
            b = 0;
            m = 128;
        }
    }
    if (m != 128) {
        *out++ = b;
    }
}

static void
pack1I(UINT8 *out, const UINT8 *in, int pixels) {
    int i, m, b;
    /* bilevel (black is 1) */
    b = 0;
    m = 128;
    for (i = 0; i < pixels; i++) {
        if (in[i] == 0) {
            b |= m;
        }
        m >>= 1;
        if (m == 0) {
            *out++ = b;
            b = 0;
            m = 128;
        }
    }
    if (m != 128) {
        *out++ = b;
    }
}

static void
pack1R(UINT8 *out, const UINT8 *in, int pixels) {
    int i, m, b;
    /* bilevel, lsb first (black is 0) */
    b = 0;
    m = 1;
    for (i = 0; i < pixels; i++) {
        if (in[i] != 0) {
            b |= m;
        }
        m <<= 1;
        if (m == 256) {
            *out++ = b;
            b = 0;
            m = 1;
        }
    }
    if (m != 1) {
        *out++ = b;
    }
}

static void
pack1IR(UINT8 *out, const UINT8 *in, int pixels) {
    int i, m, b;
    /* bilevel, lsb first (black is 1) */
    b = 0;
    m = 1;
    for (i = 0; i < pixels; i++) {
        if (in[i] == 0) {
            b |= m;
        }
        m <<= 1;
        if (m == 256) {
            *out++ = b;
            b = 0;
            m = 1;
        }
    }
    if (m != 1) {
        *out++ = b;
    }
}

static void
pack1L(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* bilevel, stored as bytes */
    for (i = 0; i < pixels; i++) {
        out[i] = (in[i] != 0) ? 255 : 0;
    }
}

static void
packP4(UINT8 *out, const UINT8 *in, int pixels) {
    while (pixels >= 2) {
        *out++ = (in[0] << 4) | (in[1] & 15);
        in += 2;
        pixels -= 2;
    }

    if (pixels) {
        out[0] = (in[0] << 4);
    }
}

static void
packP2(UINT8 *out, const UINT8 *in, int pixels) {
    while (pixels >= 4) {
        *out++ = (in[0] << 6) | ((in[1] & 3) << 4) | ((in[2] & 3) << 2) | (in[3] & 3);
        in += 4;
        pixels -= 4;
    }

    switch (pixels) {
        case 3:
            out[0] = (in[0] << 6) | ((in[1] & 3) << 4) | ((in[2] & 3) << 2);
            break;
        case 2:
            out[0] = (in[0] << 6) | ((in[1] & 3) << 4);
            break;
        case 1:
            out[0] = (in[0] << 6);
    }
}

static void
packL16(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* L -> L;16, e.g: \xff77 -> \x00\xff\x00\x77 */
    for (i = 0; i < pixels; i++) {
        out[0] = 0;
        out[1] = in[i];
        out += 2;
    }
}

static void
packL16B(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* L -> L;16B, e.g: \xff77 -> \xff\x00\x77\x00 */
    for (i = 0; i < pixels; i++) {
        out[0] = in[i];
        out[1] = 0;
        out += 2;
    }
}

static void
packLA(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* LA, pixel interleaved */
    for (i = 0; i < pixels; i++) {
        out[0] = in[R];
        out[1] = in[A];
        out += 2;
        in += 4;
    }
}

static void
packLAL(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* LA, line interleaved */
    for (i = 0; i < pixels; i++) {
        out[i] = in[R];
        out[i + pixels] = in[A];
        in += 4;
    }
}

void
ImagingPackRGB(UINT8 *out, const UINT8 *in, int pixels) {
    int i = 0;
    /* RGB triplets */
    for (; i < pixels - 1; i++) {
        memcpy(out, in + i * 4, 4);
        out += 3;
    }
    for (; i < pixels; i++) {
        out[0] = in[i * 4 + R];
        out[1] = in[i * 4 + G];
        out[2] = in[i * 4 + B];
        out += 3;
    }
}

void
ImagingPackXRGB(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* XRGB, triplets with left padding */
    for (i = 0; i < pixels; i++) {
        out[0] = 0;
        out[1] = in[R];
        out[2] = in[G];
        out[3] = in[B];
        out += 4;
        in += 4;
    }
}

void
ImagingPackBGR(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* RGB, reversed bytes */
    for (i = 0; i < pixels; i++) {
        out[0] = in[B];
        out[1] = in[G];
        out[2] = in[R];
        out += 3;
        in += 4;
    }
}

void
ImagingPackBGRX(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* BGRX, reversed bytes with right padding */
    for (i = 0; i < pixels; i++) {
        out[0] = in[B];
        out[1] = in[G];
        out[2] = in[R];
        out[3] = 0;
        out += 4;
        in += 4;
    }
}

void
ImagingPackXBGR(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* XBGR, reversed bytes with left padding */
    for (i = 0; i < pixels; i++) {
        out[0] = 0;
        out[1] = in[B];
        out[2] = in[G];
        out[3] = in[R];
        out += 4;
        in += 4;
    }
}

void
ImagingPackBGRA(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* BGRA, reversed bytes with right alpha */
    for (i = 0; i < pixels; i++) {
        out[0] = in[B];
        out[1] = in[G];
        out[2] = in[R];
        out[3] = in[A];
        out += 4;
        in += 4;
    }
}

void
ImagingPackABGR(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* ABGR, reversed bytes with left alpha */
    for (i = 0; i < pixels; i++) {
        out[0] = in[A];
        out[1] = in[B];
        out[2] = in[G];
        out[3] = in[R];
        out += 4;
        in += 4;
    }
}

void
ImagingPackBGRa(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* BGRa, reversed bytes with premultiplied alpha */
    for (i = 0; i < pixels; i++) {
        int alpha = out[3] = in[A];
        int tmp;
        out[0] = MULDIV255(in[B], alpha, tmp);
        out[1] = MULDIV255(in[G], alpha, tmp);
        out[2] = MULDIV255(in[R], alpha, tmp);
        out += 4;
        in += 4;
    }
}

static void
packRGBL(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* RGB, line interleaved */
    for (i = 0; i < pixels; i++) {
        out[i] = in[R];
        out[i + pixels] = in[G];
        out[i + pixels + pixels] = in[B];
        in += 4;
    }
}

static void
packRGBXL(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* RGBX, line interleaved */
    for (i = 0; i < pixels; i++) {
        out[i] = in[R];
        out[i + pixels] = in[G];
        out[i + pixels + pixels] = in[B];
        out[i + pixels + pixels + pixels] = in[X];
        in += 4;
    }
}

static void
packI16B(UINT8 *out, const UINT8 *in_, int pixels) {
    int i;
    UINT16 tmp_;
    UINT8 *tmp = (UINT8 *)&tmp_;
    for (i = 0; i < pixels; i++) {
        INT32 in;
        memcpy(&in, in_, sizeof(in));
        if (in <= 0) {
            tmp_ = 0;
        } else if (in > 65535) {
            tmp_ = 65535;
        } else {
            tmp_ = in;
        }
        C16B;
        out += 2;
        in_ += sizeof(in);
    }
}

static void
packI16N_I16B(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    UINT8 *tmp = (UINT8 *)in;
    for (i = 0; i < pixels; i++) {
        C16B;
        out += 2;
        tmp += 2;
    }
}
static void
packI16N_I16(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    UINT8 *tmp = (UINT8 *)in;
    for (i = 0; i < pixels; i++) {
        C16L;
        out += 2;
        tmp += 2;
    }
}

static void
packI32S(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    UINT8 *tmp = (UINT8 *)in;
    for (i = 0; i < pixels; i++) {
        C32L;
        out += 4;
        tmp += 4;
    }
}

void
ImagingPackLAB(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    /* LAB triplets */
    for (i = 0; i < pixels; i++) {
        out[0] = in[0];
        out[1] = in[1] ^ 128; /* signed in outside world */
        out[2] = in[2] ^ 128;
        out += 3;
        in += 4;
    }
}

static void
copy1(UINT8 *out, const UINT8 *in, int pixels) {
    /* L, P */
    memcpy(out, in, pixels);
}

static void
copy2(UINT8 *out, const UINT8 *in, int pixels) {
    /* I;16, etc */
    memcpy(out, in, pixels * 2);
}

static void
copy4(UINT8 *out, const UINT8 *in, int pixels) {
    /* RGBA, CMYK quadruples */
    memcpy(out, in, 4 * pixels);
}

static void
copy4I(UINT8 *out, const UINT8 *in, int pixels) {
    /* RGBA, CMYK quadruples, inverted */
    int i;
    for (i = 0; i < pixels * 4; i++) {
        out[i] = ~in[i];
    }
}

static void
band0(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    for (i = 0; i < pixels; i++, in += 4) {
        out[i] = in[0];
    }
}

static void
band1(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    for (i = 0; i < pixels; i++, in += 4) {
        out[i] = in[1];
    }
}

static void
band2(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    for (i = 0; i < pixels; i++, in += 4) {
        out[i] = in[2];
    }
}

static void
band3(UINT8 *out, const UINT8 *in, int pixels) {
    int i;
    for (i = 0; i < pixels; i++, in += 4) {
        out[i] = in[3];
    }
}

static struct {
    const ModeID mode;
    const RawModeID rawmode;
    int bits;
    ImagingShuffler pack;
} packers[] = {

    /* bilevel */
    {IMAGING_MODE_1, IMAGING_RAWMODE_1, 1, pack1},
    {IMAGING_MODE_1, IMAGING_RAWMODE_1_I, 1, pack1I},
    {IMAGING_MODE_1, IMAGING_RAWMODE_1_R, 1, pack1R},
    {IMAGING_MODE_1, IMAGING_RAWMODE_1_IR, 1, pack1IR},
    {IMAGING_MODE_1, IMAGING_RAWMODE_L, 8, pack1L},

    /* grayscale */
    {IMAGING_MODE_L, IMAGING_RAWMODE_L, 8, copy1},
    {IMAGING_MODE_L, IMAGING_RAWMODE_L_16, 16, packL16},
    {IMAGING_MODE_L, IMAGING_RAWMODE_L_16B, 16, packL16B},

    /* grayscale w. alpha */
    {IMAGING_MODE_LA, IMAGING_RAWMODE_LA, 16, packLA},
    {IMAGING_MODE_LA, IMAGING_RAWMODE_LA_L, 16, packLAL},

    /* grayscale w. alpha premultiplied */
    {IMAGING_MODE_La, IMAGING_RAWMODE_La, 16, packLA},

    /* palette */
    {IMAGING_MODE_P, IMAGING_RAWMODE_P_1, 1, pack1},
    {IMAGING_MODE_P, IMAGING_RAWMODE_P_2, 2, packP2},
    {IMAGING_MODE_P, IMAGING_RAWMODE_P_4, 4, packP4},
    {IMAGING_MODE_P, IMAGING_RAWMODE_P, 8, copy1},

    /* palette w. alpha */
    {IMAGING_MODE_PA, IMAGING_RAWMODE_PA, 16, packLA},
    {IMAGING_MODE_PA, IMAGING_RAWMODE_PA_L, 16, packLAL},

    /* true colour */
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_RGB, 24, ImagingPackRGB},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_RGBX, 32, copy4},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_RGBA, 32, copy4},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_XRGB, 32, ImagingPackXRGB},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_BGR, 24, ImagingPackBGR},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_BGRX, 32, ImagingPackBGRX},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_XBGR, 32, ImagingPackXBGR},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_RGB_L, 24, packRGBL},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_R, 8, band0},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_G, 8, band1},
    {IMAGING_MODE_RGB, IMAGING_RAWMODE_B, 8, band2},

    /* true colour w. alpha */
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_RGBA, 32, copy4},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_RGBA_L, 32, packRGBXL},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_RGB, 24, ImagingPackRGB},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_BGR, 24, ImagingPackBGR},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_BGRA, 32, ImagingPackBGRA},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_ABGR, 32, ImagingPackABGR},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_BGRa, 32, ImagingPackBGRa},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_R, 8, band0},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_G, 8, band1},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_B, 8, band2},
    {IMAGING_MODE_RGBA, IMAGING_RAWMODE_A, 8, band3},

    /* true colour w. alpha premultiplied */
    {IMAGING_MODE_RGBa, IMAGING_RAWMODE_RGBa, 32, copy4},
    {IMAGING_MODE_RGBa, IMAGING_RAWMODE_BGRa, 32, ImagingPackBGRA},
    {IMAGING_MODE_RGBa, IMAGING_RAWMODE_aBGR, 32, ImagingPackABGR},

    /* true colour w. padding */
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_RGBX, 32, copy4},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_RGBX_L, 32, packRGBXL},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_RGB, 24, ImagingPackRGB},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_BGR, 24, ImagingPackBGR},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_BGRX, 32, ImagingPackBGRX},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_XBGR, 32, ImagingPackXBGR},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_R, 8, band0},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_G, 8, band1},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_B, 8, band2},
    {IMAGING_MODE_RGBX, IMAGING_RAWMODE_X, 8, band3},

    /* colour separation */
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_CMYK, 32, copy4},
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_CMYK_I, 32, copy4I},
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_CMYK_L, 32, packRGBXL},
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_C, 8, band0},
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_M, 8, band1},
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_Y, 8, band2},
    {IMAGING_MODE_CMYK, IMAGING_RAWMODE_K, 8, band3},

    /* video (YCbCr) */
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_YCbCr, 24, ImagingPackRGB},
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_YCbCr_L, 24, packRGBL},
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_YCbCrX, 32, copy4},
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_YCbCrK, 32, copy4},
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_Y, 8, band0},
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_Cb, 8, band1},
    {IMAGING_MODE_YCbCr, IMAGING_RAWMODE_Cr, 8, band2},

    /* LAB Color */
    {IMAGING_MODE_LAB, IMAGING_RAWMODE_LAB, 24, ImagingPackLAB},
    {IMAGING_MODE_LAB, IMAGING_RAWMODE_L, 8, band0},
    {IMAGING_MODE_LAB, IMAGING_RAWMODE_A, 8, band1},
    {IMAGING_MODE_LAB, IMAGING_RAWMODE_B, 8, band2},

    /* HSV */
    {IMAGING_MODE_HSV, IMAGING_RAWMODE_HSV, 24, ImagingPackRGB},
    {IMAGING_MODE_HSV, IMAGING_RAWMODE_H, 8, band0},
    {IMAGING_MODE_HSV, IMAGING_RAWMODE_S, 8, band1},
    {IMAGING_MODE_HSV, IMAGING_RAWMODE_V, 8, band2},

    /* integer */
    {IMAGING_MODE_I, IMAGING_RAWMODE_I, 32, copy4},
    {IMAGING_MODE_I, IMAGING_RAWMODE_I_16B, 16, packI16B},
    {IMAGING_MODE_I, IMAGING_RAWMODE_I_32S, 32, packI32S},
    {IMAGING_MODE_I, IMAGING_RAWMODE_I_32NS, 32, copy4},

    /* floating point */
    {IMAGING_MODE_F, IMAGING_RAWMODE_F, 32, copy4},
    {IMAGING_MODE_F, IMAGING_RAWMODE_F_32F, 32, packI32S},
    {IMAGING_MODE_F, IMAGING_RAWMODE_F_32NF, 32, copy4},

    /* storage modes */
    {IMAGING_MODE_I_16, IMAGING_RAWMODE_I_16, 16, copy2},
#ifdef WORDS_BIGENDIAN
    {IMAGING_MODE_I_16, IMAGING_RAWMODE_I_16B, 16, packI16N_I16},
#else
    {IMAGING_MODE_I_16, IMAGING_RAWMODE_I_16B, 16, packI16N_I16B},
#endif
    {IMAGING_MODE_I_16B, IMAGING_RAWMODE_I_16B, 16, copy2},
    {IMAGING_MODE_I_16L, IMAGING_RAWMODE_I_16L, 16, copy2},
    {IMAGING_MODE_I_16N, IMAGING_RAWMODE_I_16N, 16, copy2},
    // LibTiff native->image endian.
    {IMAGING_MODE_I_16, IMAGING_RAWMODE_I_16N, 16, packI16N_I16},
    {IMAGING_MODE_I_16L, IMAGING_RAWMODE_I_16N, 16, packI16N_I16},
    {IMAGING_MODE_I_16B, IMAGING_RAWMODE_I_16N, 16, packI16N_I16B}
};

ImagingShuffler
ImagingFindPacker(const ModeID mode, const RawModeID rawmode, int *bits_out) {
    for (size_t i = 0; i < sizeof(packers) / sizeof(*packers); i++) {
        if (packers[i].mode == mode && packers[i].rawmode == rawmode) {
            if (bits_out) {
                *bits_out = packers[i].bits;
            }
            return packers[i].pack;
        }
    }
    return NULL;
}
