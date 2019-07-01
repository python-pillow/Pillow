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

#define C16N\
        (out[0]=tmp[0], out[1]=tmp[1]);
#define C16S\
        (out[1]=tmp[0], out[0]=tmp[1]);
#define C32N\
        (out[0]=tmp[0], out[1]=tmp[1], out[2]=tmp[2], out[3]=tmp[3]);
#define C32S\
        (out[3]=tmp[0], out[2]=tmp[1], out[1]=tmp[2], out[0]=tmp[3]);
#define C64N\
        (out[0]=tmp[0], out[1]=tmp[1], out[2]=tmp[2], out[3]=tmp[3],\
         out[4]=tmp[4], out[5]=tmp[5], out[6]=tmp[6], out[7]=tmp[7]);
#define C64S\
        (out[7]=tmp[0], out[6]=tmp[1], out[5]=tmp[2], out[4]=tmp[3],\
         out[3]=tmp[4], out[2]=tmp[5], out[1]=tmp[6], out[0]=tmp[7]);

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
pack1(UINT8* out, const UINT8* in, int pixels)
{
    int i, m, b;
    /* bilevel (black is 0) */
    b = 0; m = 128;
    for (i = 0; i < pixels; i++) {
        if (in[i] != 0)
            b |= m;
        m >>= 1;
        if (m == 0) {
            *out++ = b;
            b = 0; m = 128;
        }
    }
    if (m != 128)
        *out++ = b;
}

static void
pack1I(UINT8* out, const UINT8* in, int pixels)
{
    int i, m, b;
    /* bilevel (black is 1) */
    b = 0; m = 128;
    for (i = 0; i < pixels; i++) {
        if (in[i] == 0)
            b |= m;
        m >>= 1;
        if (m == 0) {
            *out++ = b;
            b = 0; m = 128;
        }
    }
    if (m != 128)
        *out++ = b;
}

static void
pack1R(UINT8* out, const UINT8* in, int pixels)
{
    int i, m, b;
    /* bilevel, lsb first (black is 0) */
    b = 0; m = 1;
    for (i = 0; i < pixels; i++) {
        if (in[i] != 0)
            b |= m;
        m <<= 1;
        if (m == 256){
            *out++ = b;
            b = 0; m = 1;
        }
    }
    if (m != 1)
        *out++ = b;
}

static void
pack1IR(UINT8* out, const UINT8* in, int pixels)
{
    int i, m, b;
    /* bilevel, lsb first (black is 1) */
    b = 0; m = 1;
    for (i = 0; i < pixels; i++) {
        if (in[i] == 0)
            b |= m;
        m <<= 1;
        if (m == 256){
            *out++ = b;
            b = 0; m = 1;
        }
    }
    if (m != 1)
        *out++ = b;
}

static void
pack1L(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* bilevel, stored as bytes */
    for (i = 0; i < pixels; i++)
        out[i] = (in[i] != 0) ? 255 : 0;
}

static void
packP4(UINT8* out, const UINT8* in, int pixels)
{
    while (pixels >= 2) {
        *out++ = (in[0] << 4) |
                 (in[1] & 15);
        in += 2; pixels -= 2;
    }

    if (pixels)
        out[0] = (in[0] << 4);
}

static void
packP2(UINT8* out, const UINT8* in, int pixels)
{
    while (pixels >= 4) {
        *out++ = (in[0] << 6) |
                 ((in[1] & 3) << 4) |
                 ((in[2] & 3) << 2) |
                 (in[3] & 3);
        in += 4; pixels -= 4;
    }

    switch (pixels) {
    case 3:
        out[0] = (in[0] << 6) |
                 ((in[1] & 3) << 4) |
                 ((in[2] & 3) << 2);
        break;
    case 2:
        out[0] = (in[0] << 6) |
                 ((in[1] & 3) << 4);
        break;
    case 1:
        out[0] = (in[0] << 6);
    }
}

static void
packL16(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* L -> L;16, e.g: \xff77 -> \x00\xff\x00\x77 */
    for (i = 0; i < pixels; i++) {
        out[0] = 0;
        out[1] = in[i];
        out += 2;
    }
}

static void
packL16B(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* L -> L;16B, e.g: \xff77 -> \xff\x00\x77\x00 */
    for (i = 0; i < pixels; i++) {
        out[0] = in[i];
        out[1] = 0;
        out += 2;
    }
}


static void
packLA(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* LA, pixel interleaved */
    for (i = 0; i < pixels; i++) {
        out[0] = in[R];
        out[1] = in[A];
        out += 2; in += 4;
    }
}

static void
packLAL(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* LA, line interleaved */
    for (i = 0; i < pixels; i++) {
        out[i] = in[R];
        out[i+pixels] = in[A];
        in += 4;
    }
}

void
ImagingPackRGB(UINT8* out, const UINT8* in, int pixels)
{
    int i = 0;
    /* RGB triplets */
#ifdef __sparc
    /* SPARC CPUs cannot read integers from nonaligned addresses. */
    for (; i < pixels; i++) {
        out[0] = in[R];
        out[1] = in[G];
        out[2] = in[B];
        out += 3; in += 4;
    }
#else
    for (; i < pixels-1; i++) {
        memcpy(out, in + i * 4, 4);
        out += 3;
    }
    for (; i < pixels; i++) {
        out[0] = in[i*4+R];
        out[1] = in[i*4+G];
        out[2] = in[i*4+B];
        out += 3;
    }
#endif
}

void
ImagingPackXRGB(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* XRGB, triplets with left padding */
    for (i = 0; i < pixels; i++) {
        out[0] = 0;
        out[1] = in[R];
        out[2] = in[G];
        out[3] = in[B];
        out += 4; in += 4;
    }
}

void
ImagingPackBGR(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* RGB, reversed bytes */
    for (i = 0; i < pixels; i++) {
        out[0] = in[B];
        out[1] = in[G];
        out[2] = in[R];
        out += 3; in += 4;
    }
}

void
ImagingPackBGRX(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* BGRX, reversed bytes with right padding */
    for (i = 0; i < pixels; i++) {
        out[0] = in[B];
        out[1] = in[G];
        out[2] = in[R];
        out[3] = 0;
        out += 4; in += 4;
    }
}

void
ImagingPackXBGR(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* XBGR, reversed bytes with left padding */
    for (i = 0; i < pixels; i++) {
        out[0] = 0;
        out[1] = in[B];
        out[2] = in[G];
        out[3] = in[R];
        out += 4; in += 4;
    }
}

void
ImagingPackBGRA(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* BGRX, reversed bytes with right padding */
    for (i = 0; i < pixels; i++) {
        out[0] = in[B];
        out[1] = in[G];
        out[2] = in[R];
        out[3] = in[A];
        out += 4; in += 4;
    }
}

void
ImagingPackABGR(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* XBGR, reversed bytes with left padding */
    for (i = 0; i < pixels; i++) {
        out[0] = in[A];
        out[1] = in[B];
        out[2] = in[G];
        out[3] = in[R];
        out += 4; in += 4;
    }
}

void
ImagingPackBGRa(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* BGRa, reversed bytes with premultiplied alpha */
    for (i = 0; i < pixels; i++) {
        int alpha = out[3] = in[A];
        int tmp;
        out[0] = MULDIV255(in[B], alpha, tmp);
        out[1] = MULDIV255(in[G], alpha, tmp);
        out[2] = MULDIV255(in[R], alpha, tmp);
        out += 4; in += 4;
    }
}

static void
packRGBL(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* RGB, line interleaved */
    for (i = 0; i < pixels; i++) {
        out[i] = in[R];
        out[i+pixels] = in[G];
        out[i+pixels+pixels] = in[B];
        in += 4;
    }
}

static void
packRGBXL(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* RGBX, line interleaved */
    for (i = 0; i < pixels; i++) {
        out[i] = in[R];
        out[i+pixels] = in[G];
        out[i+pixels+pixels] = in[B];
        out[i+pixels+pixels+pixels] = in[X];
        in += 4;
    }
}

static void
packI16B(UINT8* out, const UINT8* in_, int pixels)
{
    int i;
    UINT16 tmp_;
    UINT8* tmp = (UINT8*) &tmp_;
    for (i = 0; i < pixels; i++) {
        INT32 in;
        memcpy(&in, in_, sizeof(in));
        if (in <= 0)
            tmp_ = 0;
        else if (in > 65535)
            tmp_ = 65535;
        else
            tmp_ = in;
        C16B;
        out += 2; in_ += sizeof(in);
    }
}

static void
packI16N_I16B(UINT8* out, const UINT8* in, int pixels){
    int i;
    UINT8* tmp = (UINT8*) in;
    for (i = 0; i < pixels; i++) {
        C16B;
        out += 2; tmp += 2;
    }

}
static void
packI16N_I16(UINT8* out, const UINT8* in, int pixels){
    int i;
    UINT8* tmp = (UINT8*) in;
    for (i = 0; i < pixels; i++) {
        C16L;
        out += 2; tmp += 2;
    }
}


static void
packI32S(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    UINT8* tmp = (UINT8*) in;
    for (i = 0; i < pixels; i++) {
        C32L;
        out += 4; tmp += 4;
    }
}

void
ImagingPackLAB(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    /* LAB triplets */
    for (i = 0; i < pixels; i++) {
        out[0] = in[0];
        out[1] = in[1] ^ 128; /* signed in outside world */
        out[2] = in[2] ^ 128;
        out += 3; in += 4;
    }
}

static void
copy1(UINT8* out, const UINT8* in, int pixels)
{
    /* L, P */
    memcpy(out, in, pixels);
}

static void
copy2(UINT8* out, const UINT8* in, int pixels)
{
    /* I;16, etc */
    memcpy(out, in, pixels*2);
}

static void
copy3(UINT8* out, const UINT8* in, int pixels)
{
    /* BGR;24, etc */
    memcpy(out, in, pixels*3);
}

static void
copy4(UINT8* out, const UINT8* in, int pixels)
{
    /* RGBA, CMYK quadruples */
    memcpy(out, in, 4*pixels);
}

static void
copy4I(UINT8* out, const UINT8* in, int pixels)
{
    /* RGBA, CMYK quadruples, inverted */
    int i;
    for (i = 0; i < pixels*4; i++)
        out[i] = ~in[i];
}

static void
band0(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    for (i = 0; i < pixels; i++, in += 4)
        out[i] = in[0];
}

static void
band1(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    for (i = 0; i < pixels; i++, in += 4)
        out[i] = in[1];
}

static void
band2(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    for (i = 0; i < pixels; i++, in += 4)
        out[i] = in[2];
}

static void
band3(UINT8* out, const UINT8* in, int pixels)
{
    int i;
    for (i = 0; i < pixels; i++, in += 4)
        out[i] = in[3];
}

static struct {
    const char* mode;
    const char* rawmode;
    int bits;
    ImagingShuffler pack;
} packers[] = {

    /* bilevel */
    {"1",       "1",            1,      pack1},
    {"1",       "1;I",          1,      pack1I},
    {"1",       "1;R",          1,      pack1R},
    {"1",       "1;IR",         1,      pack1IR},
    {"1",       "L",            8,      pack1L},

    /* greyscale */
    {"L",       "L",            8,      copy1},
    {"L",       "L;16",         16,     packL16},
    {"L",       "L;16B",        16,     packL16B},

    /* greyscale w. alpha */
    {"LA",      "LA",           16,     packLA},
    {"LA",      "LA;L",         16,     packLAL},

    /* palette */
    {"P",       "P;1",          1,      pack1},
    {"P",       "P;2",          2,      packP2},
    {"P",       "P;4",          4,      packP4},
    {"P",       "P",            8,      copy1},

    /* palette w. alpha */
    {"PA",      "PA",           16,     packLA},
    {"PA",      "PA;L",         16,     packLAL},

    /* true colour */
    {"RGB",     "RGB",          24,     ImagingPackRGB},
    {"RGB",     "RGBX",         32,     copy4},
    {"RGB",     "XRGB",         32,     ImagingPackXRGB},
    {"RGB",     "BGR",          24,     ImagingPackBGR},
    {"RGB",     "BGRX",         32,     ImagingPackBGRX},
    {"RGB",     "XBGR",         32,     ImagingPackXBGR},
    {"RGB",     "RGB;L",        24,     packRGBL},
    {"RGB",     "R",            8,      band0},
    {"RGB",     "G",            8,      band1},
    {"RGB",     "B",            8,      band2},

    /* true colour w. alpha */
    {"RGBA",    "RGBA",         32,     copy4},
    {"RGBA",    "RGBA;L",       32,     packRGBXL},
    {"RGBA",    "RGB",          24,     ImagingPackRGB},
    {"RGBA",    "BGR",          24,     ImagingPackBGR},
    {"RGBA",    "BGRA",         32,     ImagingPackBGRA},
    {"RGBA",    "ABGR",         32,     ImagingPackABGR},
    {"RGBA",    "BGRa",         32,     ImagingPackBGRa},
    {"RGBA",    "R",            8,      band0},
    {"RGBA",    "G",            8,      band1},
    {"RGBA",    "B",            8,      band2},
    {"RGBA",    "A",            8,      band3},

    /* true colour w. alpha premultiplied */
    {"RGBa",    "RGBa",         32,     copy4},
    {"RGBa",    "BGRa",         32,     ImagingPackBGRA},
    {"RGBa",    "aBGR",         32,     ImagingPackABGR},

    /* true colour w. padding */
    {"RGBX",    "RGBX",         32,     copy4},
    {"RGBX",    "RGBX;L",       32,     packRGBXL},
    {"RGBX",    "RGB",          24,     ImagingPackRGB},
    {"RGBX",    "BGR",          24,     ImagingPackBGR},
    {"RGBX",    "BGRX",         32,     ImagingPackBGRX},
    {"RGBX",    "XBGR",         32,     ImagingPackXBGR},
    {"RGBX",    "R",            8,      band0},
    {"RGBX",    "G",            8,      band1},
    {"RGBX",    "B",            8,      band2},
    {"RGBX",    "X",            8,      band3},

    /* colour separation */
    {"CMYK",    "CMYK",         32,     copy4},
    {"CMYK",    "CMYK;I",       32,     copy4I},
    {"CMYK",    "CMYK;L",       32,     packRGBXL},
    {"CMYK",    "C",            8,      band0},
    {"CMYK",    "M",            8,      band1},
    {"CMYK",    "Y",            8,      band2},
    {"CMYK",    "K",            8,      band3},

    /* video (YCbCr) */
    {"YCbCr",   "YCbCr",        24,     ImagingPackRGB},
    {"YCbCr",   "YCbCr;L",      24,     packRGBL},
    {"YCbCr",   "YCbCrX",       32,     copy4},
    {"YCbCr",   "YCbCrK",       32,     copy4},
    {"YCbCr",   "Y",            8,      band0},
    {"YCbCr",   "Cb",           8,      band1},
    {"YCbCr",   "Cr",           8,      band2},

    /* LAB Color */
    {"LAB",     "LAB",         24,     ImagingPackLAB},
    {"LAB",     "L",           8,      band0},
    {"LAB",     "A",           8,      band1},
    {"LAB",     "B",           8,      band2},

    /* HSV */
    {"HSV",     "HSV",         24,     ImagingPackRGB},
    {"HSV",     "H",           8,      band0},
    {"HSV",     "S",           8,      band1},
    {"HSV",     "V",           8,      band2},

    /* integer */
    {"I",       "I",            32,     copy4},
    {"I",       "I;16B",        16,     packI16B},
    {"I",       "I;32S",        32,     packI32S},
    {"I",       "I;32NS",       32,     copy4},

    /* floating point */
    {"F",       "F",            32,     copy4},
    {"F",       "F;32F",        32,     packI32S},
    {"F",       "F;32NF",       32,     copy4},

    /* storage modes */
    {"I;16",    "I;16",         16,     copy2},
    {"I;16",    "I;16B",        16,     packI16N_I16B},
    {"I;16B",   "I;16B",        16,     copy2},
    {"I;16L",   "I;16L",        16,     copy2},
    {"I;16",    "I;16N",        16,     packI16N_I16}, // LibTiff native->image endian.
    {"I;16L",   "I;16N",        16,     packI16N_I16},
    {"I;16B",   "I;16N",        16,     packI16N_I16B},
    {"BGR;15",  "BGR;15",       16,     copy2},
    {"BGR;16",  "BGR;16",       16,     copy2},
    {"BGR;24",  "BGR;24",       24,     copy3},

    {NULL} /* sentinel */
};


ImagingShuffler
ImagingFindPacker(const char* mode, const char* rawmode, int* bits_out)
{
    int i;

    /* find a suitable pixel packer */
    for (i = 0; packers[i].rawmode; i++)
        if (strcmp(packers[i].mode, mode) == 0 &&
            strcmp(packers[i].rawmode, rawmode) == 0) {
            if (bits_out)
                *bits_out = packers[i].bits;
            return packers[i].pack;
        }
    return NULL;
}
