/*
 * The Python Imaging Library
 * $Id$
 *
 * convert images
 *
 * history:
 * 1995-06-15 fl   created
 * 1995-11-28 fl   added some "RGBA" and "CMYK" conversions
 * 1996-04-22 fl   added "1" conversions (same as "L")
 * 1996-05-05 fl   added palette conversions (hack)
 * 1996-07-23 fl   fixed "1" conversions to zero/non-zero convention
 * 1996-11-01 fl   fixed "P" to "L" and "RGB" to "1" conversions
 * 1996-12-29 fl   set alpha byte in RGB converters
 * 1997-05-12 fl   added ImagingConvert2
 * 1997-05-30 fl   added floating point support
 * 1997-08-27 fl   added "P" to "1" and "P" to "F" conversions
 * 1998-01-11 fl   added integer support
 * 1998-07-01 fl   added "YCbCr" support
 * 1998-07-02 fl   added "RGBX" conversions (sort of)
 * 1998-07-04 fl   added floyd-steinberg dithering
 * 1998-07-12 fl   changed "YCrCb" to "YCbCr" (!)
 * 1998-12-29 fl   added basic "I;16" and "I;16B" conversions
 * 1999-02-03 fl   added "RGBa", and "BGR" conversions (experimental)
 * 2003-09-26 fl   added "LA" and "PA" conversions (experimental)
 * 2005-05-05 fl   fixed "P" to "1" threshold
 * 2005-12-08 fl   fixed palette memory leak in topalette
 *
 * Copyright (c) 1997-2005 by Secret Labs AB.
 * Copyright (c) 1995-1997 by Fredrik Lundh.
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

#define MAX(a, b) (a) > (b) ? (a) : (b)
#define MIN(a, b) (a) < (b) ? (a) : (b)

#define CLIP16(v) ((v) <= 0 ? 0 : (v) >= 65535 ? 65535 : (v))

/* ITU-R Recommendation 601-2 (assuming nonlinear RGB) */
#define L(rgb) ((INT32)(rgb)[0] * 299 + (INT32)(rgb)[1] * 587 + (INT32)(rgb)[2] * 114)
#define L24(rgb) ((rgb)[0] * 19595 + (rgb)[1] * 38470 + (rgb)[2] * 7471 + 0x8000)

/* ------------------- */
/* 1 (bit) conversions */
/* ------------------- */

static void
bit2l(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) *out++ = (*in++ != 0) ? 255 : 0;
}

static void
bit2rgb(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        UINT8 v = (*in++ != 0) ? 255 : 0;
        *out++ = v;
        *out++ = v;
        *out++ = v;
        *out++ = 255;
    }
}

static void
bit2cmyk(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = 0;
        *out++ = 0;
        *out++ = 0;
        *out++ = (*in++ != 0) ? 0 : 255;
    }
}

static void
bit2ycbcr(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = (*in++ != 0) ? 255 : 0;
        *out++ = 128;
        *out++ = 128;
        *out++ = 255;
    }
}

static void
bit2hsv(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out += 4) {
        UINT8 v = (*in++ != 0) ? 255 : 0;
        out[0] = 0;
        out[1] = 0;
        out[2] = v;
        out[3] = 255;
    }
}

/* ----------------- */
/* RGB/L conversions */
/* ----------------- */

static void
l2bit(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = (*in++ >= 128) ? 255 : 0;
    }
}

static void
lA2la(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    unsigned int alpha, pixel, tmp;
    for (x = 0; x < xsize; x++, in += 4) {
        alpha = in[3];
        pixel = MULDIV255(in[0], alpha, tmp);
        *out++ = (UINT8)pixel;
        *out++ = (UINT8)pixel;
        *out++ = (UINT8)pixel;
        *out++ = (UINT8)alpha;
    }
}

/* RGBa -> RGBA conversion to remove premultiplication
   Needed for correct transforms/resizing on RGBA images */
static void
la2lA(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    unsigned int alpha, pixel;
    for (x = 0; x < xsize; x++, in += 4) {
        alpha = in[3];
        if (alpha == 255 || alpha == 0) {
            pixel = in[0];
        } else {
            pixel = CLIP8((255 * in[0]) / alpha);
        }
        *out++ = (UINT8)pixel;
        *out++ = (UINT8)pixel;
        *out++ = (UINT8)pixel;
        *out++ = (UINT8)alpha;
    }
}

static void
l2la(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        UINT8 v = *in++;
        *out++ = v;
        *out++ = v;
        *out++ = v;
        *out++ = 255;
    }
}

static void
l2rgb(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        UINT8 v = *in++;
        *out++ = v;
        *out++ = v;
        *out++ = v;
        *out++ = 255;
    }
}

static void
l2hsv(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out += 4) {
        UINT8 v = *in++;
        out[0] = 0;
        out[1] = 0;
        out[2] = v;
        out[3] = 255;
    }
}

static void
la2l(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = in[0];
    }
}

static void
la2rgb(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        UINT8 v = in[0];
        *out++ = v;
        *out++ = v;
        *out++ = v;
        *out++ = in[3];
    }
}

static void
la2hsv(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        UINT8 v = in[0];
        out[0] = 0;
        out[1] = 0;
        out[2] = v;
        out[3] = in[3];
    }
}

static void
rgb2bit(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        /* ITU-R Recommendation 601-2 (assuming nonlinear RGB) */
        *out++ = (L(in) >= 128000) ? 255 : 0;
    }
}

static void
rgb2l(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        /* ITU-R Recommendation 601-2 (assuming nonlinear RGB) */
        *out++ = L24(in) >> 16;
    }
}

static void
rgb2la(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        /* ITU-R Recommendation 601-2 (assuming nonlinear RGB) */
        out[0] = out[1] = out[2] = L24(in) >> 16;
        out[3] = 255;
    }
}

static void
rgb2i(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out_ += 4) {
        INT32 v = L24(in) >> 16;
        memcpy(out_, &v, sizeof(v));
    }
}

static void
rgb2f(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out_ += 4) {
        FLOAT32 v = (float)L(in) / 1000.0F;
        memcpy(out_, &v, sizeof(v));
    }
}

static void
rgb2bgr15(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out_ += 2) {
        UINT16 v = ((((UINT16)in[0]) << 7) & 0x7c00) +
                   ((((UINT16)in[1]) << 2) & 0x03e0) +
                   ((((UINT16)in[2]) >> 3) & 0x001f);
        memcpy(out_, &v, sizeof(v));
    }
}

static void
rgb2bgr16(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out_ += 2) {
        UINT16 v = ((((UINT16)in[0]) << 8) & 0xf800) +
                   ((((UINT16)in[1]) << 3) & 0x07e0) +
                   ((((UINT16)in[2]) >> 3) & 0x001f);
        memcpy(out_, &v, sizeof(v));
    }
}

static void
rgb2bgr24(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = in[2];
        *out++ = in[1];
        *out++ = in[0];
    }
}

static void
rgb2hsv_row(UINT8 *out, const UINT8 *in) {  // following colorsys.py
    float h, s, rc, gc, bc, cr;
    UINT8 maxc, minc;
    UINT8 r, g, b;
    UINT8 uh, us, uv;

    r = in[0];
    g = in[1];
    b = in[2];
    maxc = MAX(r, MAX(g, b));
    minc = MIN(r, MIN(g, b));
    uv = maxc;
    if (minc == maxc) {
        uh = 0;
        us = 0;
    } else {
        cr = (float)(maxc - minc);
        s = cr / (float)maxc;
        rc = ((float)(maxc - r)) / cr;
        gc = ((float)(maxc - g)) / cr;
        bc = ((float)(maxc - b)) / cr;
        if (r == maxc) {
            h = bc - gc;
        } else if (g == maxc) {
            h = 2.0 + rc - bc;
        } else {
            h = 4.0 + gc - rc;
        }
        // incorrect hue happens if h/6 is negative.
        h = fmod((h / 6.0 + 1.0), 1.0);

        uh = (UINT8)CLIP8((int)(h * 255.0));
        us = (UINT8)CLIP8((int)(s * 255.0));
    }
    out[0] = uh;
    out[1] = us;
    out[2] = uv;
}

static void
rgb2hsv(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        rgb2hsv_row(out, in);
        out[3] = in[3];
    }
}

static void
hsv2rgb(UINT8 *out, const UINT8 *in, int xsize) {  // following colorsys.py

    int p, q, t;
    UINT8 up, uq, ut;
    int i, x;
    float f, fs;
    UINT8 h, s, v;

    for (x = 0; x < xsize; x++, in += 4) {
        h = in[0];
        s = in[1];
        v = in[2];

        if (s == 0) {
            *out++ = v;
            *out++ = v;
            *out++ = v;
        } else {
            i = floor((float)h * 6.0 / 255.0);      // 0 - 6
            f = (float)h * 6.0 / 255.0 - (float)i;  // 0-1 : remainder.
            fs = ((float)s) / 255.0;

            p = round((float)v * (1.0 - fs));
            q = round((float)v * (1.0 - fs * f));
            t = round((float)v * (1.0 - fs * (1.0 - f)));
            up = (UINT8)CLIP8(p);
            uq = (UINT8)CLIP8(q);
            ut = (UINT8)CLIP8(t);

            switch (i % 6) {
                case 0:
                    *out++ = v;
                    *out++ = ut;
                    *out++ = up;
                    break;
                case 1:
                    *out++ = uq;
                    *out++ = v;
                    *out++ = up;
                    break;
                case 2:
                    *out++ = up;
                    *out++ = v;
                    *out++ = ut;
                    break;
                case 3:
                    *out++ = up;
                    *out++ = uq;
                    *out++ = v;
                    break;
                case 4:
                    *out++ = ut;
                    *out++ = up;
                    *out++ = v;
                    break;
                case 5:
                    *out++ = v;
                    *out++ = up;
                    *out++ = uq;
                    break;
            }
        }
        *out++ = in[3];
    }
}

/* ---------------- */
/* RGBA conversions */
/* ---------------- */

static void
rgb2rgba(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = *in++;
        *out++ = *in++;
        *out++ = *in++;
        *out++ = 255;
        in++;
    }
}

static void
rgba2la(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        /* ITU-R Recommendation 601-2 (assuming nonlinear RGB) */
        out[0] = out[1] = out[2] = L24(in) >> 16;
        out[3] = in[3];
    }
}

static void
rgba2rgb(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = *in++;
        *out++ = *in++;
        *out++ = *in++;
        *out++ = 255;
        in++;
    }
}

static void
rgbA2rgba(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    unsigned int alpha, tmp;
    for (x = 0; x < xsize; x++) {
        alpha = in[3];
        *out++ = MULDIV255(*in++, alpha, tmp);
        *out++ = MULDIV255(*in++, alpha, tmp);
        *out++ = MULDIV255(*in++, alpha, tmp);
        *out++ = *in++;
    }
}

/* RGBa -> RGBA conversion to remove premultiplication
   Needed for correct transforms/resizing on RGBA images */
static void
rgba2rgbA(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    unsigned int alpha;
    for (x = 0; x < xsize; x++, in += 4) {
        alpha = in[3];
        if (alpha == 255 || alpha == 0) {
            *out++ = in[0];
            *out++ = in[1];
            *out++ = in[2];
        } else {
            *out++ = CLIP8((255 * in[0]) / alpha);
            *out++ = CLIP8((255 * in[1]) / alpha);
            *out++ = CLIP8((255 * in[2]) / alpha);
        }
        *out++ = in[3];
    }
}

static void
rgba2rgb_(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    unsigned int alpha;
    for (x = 0; x < xsize; x++, in += 4) {
        alpha = in[3];
        if (alpha == 255 || alpha == 0) {
            *out++ = in[0];
            *out++ = in[1];
            *out++ = in[2];
        } else {
            *out++ = CLIP8((255 * in[0]) / alpha);
            *out++ = CLIP8((255 * in[1]) / alpha);
            *out++ = CLIP8((255 * in[2]) / alpha);
        }
        *out++ = 255;
    }
}

/*
 * Conversion of RGB + single transparent color to RGBA,
 * where any pixel that matches the color will have the
 * alpha channel set to 0
 */

static void
rgbT2rgba(UINT8 *out, int xsize, int r, int g, int b) {
#ifdef WORDS_BIGENDIAN
    UINT32 trns = ((r & 0xff) << 24) | ((g & 0xff) << 16) | ((b & 0xff) << 8) | 0xff;
    UINT32 repl = trns & 0xffffff00;
#else
    UINT32 trns = (0xff << 24) | ((b & 0xff) << 16) | ((g & 0xff) << 8) | (r & 0xff);
    UINT32 repl = trns & 0x00ffffff;
#endif

    int i;

    for (i = 0; i < xsize; i++, out += sizeof(trns)) {
        UINT32 v;
        memcpy(&v, out, sizeof(v));
        if (v == trns) {
            memcpy(out, &repl, sizeof(repl));
        }
    }
}

/* ---------------- */
/* CMYK conversions */
/* ---------------- */

static void
l2cmyk(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = 0;
        *out++ = 0;
        *out++ = 0;
        *out++ = ~(*in++);
    }
}

static void
la2cmyk(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = 0;
        *out++ = 0;
        *out++ = 0;
        *out++ = ~(in[0]);
    }
}

static void
rgb2cmyk(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        /* Note: no undercolour removal */
        *out++ = ~(*in++);
        *out++ = ~(*in++);
        *out++ = ~(*in++);
        *out++ = 0;
        in++;
    }
}

void
cmyk2rgb(UINT8 *out, const UINT8 *in, int xsize) {
    int x, nk, tmp;
    for (x = 0; x < xsize; x++) {
        nk = 255 - in[3];
        out[0] = CLIP8(nk - MULDIV255(in[0], nk, tmp));
        out[1] = CLIP8(nk - MULDIV255(in[1], nk, tmp));
        out[2] = CLIP8(nk - MULDIV255(in[2], nk, tmp));
        out[3] = 255;
        out += 4;
        in += 4;
    }
}

static void
cmyk2hsv(UINT8 *out, const UINT8 *in, int xsize) {
    int x, nk, tmp;
    for (x = 0; x < xsize; x++) {
        nk = 255 - in[3];
        out[0] = CLIP8(nk - MULDIV255(in[0], nk, tmp));
        out[1] = CLIP8(nk - MULDIV255(in[1], nk, tmp));
        out[2] = CLIP8(nk - MULDIV255(in[2], nk, tmp));
        rgb2hsv_row(out, out);
        out[3] = 255;
        out += 4;
        in += 4;
    }
}

/* ------------- */
/* I conversions */
/* ------------- */

static void
bit2i(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out_ += 4) {
        INT32 v = (*in++ != 0) ? 255 : 0;
        memcpy(out_, &v, sizeof(v));
    }
}

static void
l2i(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out_ += 4) {
        INT32 v = *in++;
        memcpy(out_, &v, sizeof(v));
    }
}

static void
i2l(UINT8 *out, const UINT8 *in_, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out++, in_ += 4) {
        INT32 v;
        memcpy(&v, in_, sizeof(v));
        if (v <= 0) {
            *out = 0;
        } else if (v >= 255) {
            *out = 255;
        } else {
            *out = (UINT8)v;
        }
    }
}

static void
i2f(UINT8 *out_, const UINT8 *in_, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in_ += 4, out_ += 4) {
        INT32 i;
        FLOAT32 f;
        memcpy(&i, in_, sizeof(i));
        f = i;
        memcpy(out_, &f, sizeof(f));
    }
}

static void
i2rgb(UINT8 *out, const UINT8 *in_, int xsize) {
    int x;
    INT32 *in = (INT32 *)in_;
    for (x = 0; x < xsize; x++, in++, out += 4) {
        if (*in <= 0) {
            out[0] = out[1] = out[2] = 0;
        } else if (*in >= 255) {
            out[0] = out[1] = out[2] = 255;
        } else {
            out[0] = out[1] = out[2] = (UINT8)*in;
        }
        out[3] = 255;
    }
}

static void
i2hsv(UINT8 *out, const UINT8 *in_, int xsize) {
    int x;
    INT32 *in = (INT32 *)in_;
    for (x = 0; x < xsize; x++, in++, out += 4) {
        out[0] = 0;
        out[1] = 0;
        if (*in <= 0) {
            out[2] = 0;
        } else if (*in >= 255) {
            out[2] = 255;
        } else {
            out[2] = (UINT8)*in;
        }
        out[3] = 255;
    }
}

/* ------------- */
/* F conversions */
/* ------------- */

static void
bit2f(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out_ += 4) {
        FLOAT32 f = (*in++ != 0) ? 255.0F : 0.0F;
        memcpy(out_, &f, sizeof(f));
    }
}

static void
l2f(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out_ += 4) {
        FLOAT32 f = (FLOAT32)*in++;
        memcpy(out_, &f, sizeof(f));
    }
}

static void
f2l(UINT8 *out, const UINT8 *in_, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, out++, in_ += 4) {
        FLOAT32 v;
        memcpy(&v, in_, sizeof(v));
        if (v <= 0.0) {
            *out = 0;
        } else if (v >= 255.0) {
            *out = 255;
        } else {
            *out = (UINT8)v;
        }
    }
}

static void
f2i(UINT8 *out_, const UINT8 *in_, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in_ += 4, out_ += 4) {
        FLOAT32 f;
        INT32 i;
        memcpy(&f, in_, sizeof(f));
        i = f;
        memcpy(out_, &i, sizeof(i));
    }
}

/* ----------------- */
/* YCbCr conversions */
/* ----------------- */

/* See ConvertYCbCr.c for RGB/YCbCr tables */

static void
l2ycbcr(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++) {
        *out++ = *in++;
        *out++ = 128;
        *out++ = 128;
        *out++ = 255;
    }
}

static void
la2ycbcr(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = in[0];
        *out++ = 128;
        *out++ = 128;
        *out++ = 255;
    }
}

static void
ycbcr2l(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = in[0];
    }
}

static void
ycbcr2la(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        out[0] = out[1] = out[2] = in[0];
        out[3] = 255;
    }
}

/* ------------------------- */
/* I;16 (16-bit) conversions */
/* ------------------------- */

static void
I_I16L(UINT8 *out, const UINT8 *in_, int xsize) {
    int x, v;
    for (x = 0; x < xsize; x++, in_ += 4) {
        INT32 i;
        memcpy(&i, in_, sizeof(i));
        v = CLIP16(i);
        *out++ = (UINT8)v;
        *out++ = (UINT8)(v >> 8);
    }
}

static void
I_I16B(UINT8 *out, const UINT8 *in_, int xsize) {
    int x, v;
    for (x = 0; x < xsize; x++, in_ += 4) {
        INT32 i;
        memcpy(&i, in_, sizeof(i));
        v = CLIP16(i);
        *out++ = (UINT8)(v >> 8);
        *out++ = (UINT8)v;
    }
}

static void
I16L_I(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 2, out_ += 4) {
        INT32 v = in[0] + ((int)in[1] << 8);
        memcpy(out_, &v, sizeof(v));
    }
}

static void
I16B_I(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 2, out_ += 4) {
        INT32 v = in[1] + ((int)in[0] << 8);
        memcpy(out_, &v, sizeof(v));
    }
}

static void
I16L_F(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 2, out_ += 4) {
        FLOAT32 v = in[0] + ((int)in[1] << 8);
        memcpy(out_, &v, sizeof(v));
    }
}

static void
I16B_F(UINT8 *out_, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 2, out_ += 4) {
        FLOAT32 v = in[1] + ((int)in[0] << 8);
        memcpy(out_, &v, sizeof(v));
    }
}

static void
L_I16L(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in++) {
        *out++ = *in;
        *out++ = 0;
    }
}

static void
L_I16B(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in++) {
        *out++ = 0;
        *out++ = *in;
    }
}

static void
I16L_L(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 2) {
        if (in[1] != 0) {
            *out++ = 255;
        } else {
            *out++ = in[0];
        }
    }
}

static void
I16B_L(UINT8 *out, const UINT8 *in, int xsize) {
    int x;
    for (x = 0; x < xsize; x++, in += 2) {
        if (in[0] != 0) {
            *out++ = 255;
        } else {
            *out++ = in[1];
        }
    }
}

static struct {
    const char *from;
    const char *to;
    ImagingShuffler convert;
} converters[] = {

    {"1", "L", bit2l},
    {"1", "I", bit2i},
    {"1", "F", bit2f},
    {"1", "RGB", bit2rgb},
    {"1", "RGBA", bit2rgb},
    {"1", "RGBX", bit2rgb},
    {"1", "CMYK", bit2cmyk},
    {"1", "YCbCr", bit2ycbcr},
    {"1", "HSV", bit2hsv},

    {"L", "1", l2bit},
    {"L", "LA", l2la},
    {"L", "I", l2i},
    {"L", "F", l2f},
    {"L", "RGB", l2rgb},
    {"L", "RGBA", l2rgb},
    {"L", "RGBX", l2rgb},
    {"L", "CMYK", l2cmyk},
    {"L", "YCbCr", l2ycbcr},
    {"L", "HSV", l2hsv},

    {"LA", "L", la2l},
    {"LA", "La", lA2la},
    {"LA", "RGB", la2rgb},
    {"LA", "RGBA", la2rgb},
    {"LA", "RGBX", la2rgb},
    {"LA", "CMYK", la2cmyk},
    {"LA", "YCbCr", la2ycbcr},
    {"LA", "HSV", la2hsv},

    {"La", "LA", la2lA},

    {"I", "L", i2l},
    {"I", "F", i2f},
    {"I", "RGB", i2rgb},
    {"I", "RGBA", i2rgb},
    {"I", "RGBX", i2rgb},
    {"I", "HSV", i2hsv},

    {"F", "L", f2l},
    {"F", "I", f2i},

    {"RGB", "1", rgb2bit},
    {"RGB", "L", rgb2l},
    {"RGB", "LA", rgb2la},
    {"RGB", "I", rgb2i},
    {"RGB", "F", rgb2f},
    {"RGB", "BGR;15", rgb2bgr15},
    {"RGB", "BGR;16", rgb2bgr16},
    {"RGB", "BGR;24", rgb2bgr24},
    {"RGB", "RGBA", rgb2rgba},
    {"RGB", "RGBX", rgb2rgba},
    {"RGB", "CMYK", rgb2cmyk},
    {"RGB", "YCbCr", ImagingConvertRGB2YCbCr},
    {"RGB", "HSV", rgb2hsv},

    {"RGBA", "1", rgb2bit},
    {"RGBA", "L", rgb2l},
    {"RGBA", "LA", rgba2la},
    {"RGBA", "I", rgb2i},
    {"RGBA", "F", rgb2f},
    {"RGBA", "RGB", rgba2rgb},
    {"RGBA", "RGBa", rgbA2rgba},
    {"RGBA", "RGBX", rgb2rgba},
    {"RGBA", "CMYK", rgb2cmyk},
    {"RGBA", "YCbCr", ImagingConvertRGB2YCbCr},
    {"RGBA", "HSV", rgb2hsv},

    {"RGBa", "RGBA", rgba2rgbA},
    {"RGBa", "RGB", rgba2rgb_},

    {"RGBX", "1", rgb2bit},
    {"RGBX", "L", rgb2l},
    {"RGBX", "LA", rgb2la},
    {"RGBX", "I", rgb2i},
    {"RGBX", "F", rgb2f},
    {"RGBX", "RGB", rgba2rgb},
    {"RGBX", "CMYK", rgb2cmyk},
    {"RGBX", "YCbCr", ImagingConvertRGB2YCbCr},
    {"RGBX", "HSV", rgb2hsv},

    {"CMYK", "RGB", cmyk2rgb},
    {"CMYK", "RGBA", cmyk2rgb},
    {"CMYK", "RGBX", cmyk2rgb},
    {"CMYK", "HSV", cmyk2hsv},

    {"YCbCr", "L", ycbcr2l},
    {"YCbCr", "LA", ycbcr2la},
    {"YCbCr", "RGB", ImagingConvertYCbCr2RGB},

    {"HSV", "RGB", hsv2rgb},

    {"I", "I;16", I_I16L},
    {"I;16", "I", I16L_I},
    {"L", "I;16", L_I16L},
    {"I;16", "L", I16L_L},

    {"I", "I;16L", I_I16L},
    {"I;16L", "I", I16L_I},
    {"I", "I;16B", I_I16B},
    {"I;16B", "I", I16B_I},

    {"L", "I;16L", L_I16L},
    {"I;16L", "L", I16L_L},
    {"L", "I;16B", L_I16B},
    {"I;16B", "L", I16B_L},
#ifdef WORDS_BIGENDIAN
    {"L", "I;16N", L_I16B},
    {"I;16N", "L", I16B_L},
#else
    {"L", "I;16N", L_I16L},
    {"I;16N", "L", I16L_L},
#endif

    {"I;16", "F", I16L_F},
    {"I;16L", "F", I16L_F},
    {"I;16B", "F", I16B_F},

    {NULL}};

/* FIXME: translate indexed versions to pointer versions below this line */

/* ------------------- */
/* Palette conversions */
/* ------------------- */

static void
p2bit(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    /* FIXME: precalculate grayscale palette? */
    for (x = 0; x < xsize; x++) {
        *out++ = (L(&palette->palette[in[x] * 4]) >= 128000) ? 255 : 0;
    }
}

static void
pa2bit(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    /* FIXME: precalculate grayscale palette? */
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = (L(&palette->palette[in[0] * 4]) >= 128000) ? 255 : 0;
    }
}

static void
p2l(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    /* FIXME: precalculate grayscale palette? */
    for (x = 0; x < xsize; x++) {
        *out++ = L24(&palette->palette[in[x] * 4]) >> 16;
    }
}

static void
pa2l(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    /* FIXME: precalculate grayscale palette? */
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = L24(&palette->palette[in[0] * 4]) >> 16;
    }
}

static void
pa2p(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = in[0];
    }
}

static void
p2pa(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    int rgb = strcmp(palette->mode, "RGB");
    for (x = 0; x < xsize; x++, in++) {
        const UINT8 *rgba = &palette->palette[in[0] * 4];
        *out++ = in[0];
        *out++ = in[0];
        *out++ = in[0];
        *out++ = rgb == 0 ? 255 : rgba[3];
    }
}

static void
p2la(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    /* FIXME: precalculate grayscale palette? */
    for (x = 0; x < xsize; x++, out += 4) {
        const UINT8 *rgba = &palette->palette[*in++ * 4];
        out[0] = out[1] = out[2] = L24(rgba) >> 16;
        out[3] = rgba[3];
    }
}

static void
pa2la(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    /* FIXME: precalculate grayscale palette? */
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        out[0] = out[1] = out[2] = L24(&palette->palette[in[0] * 4]) >> 16;
        out[3] = in[3];
    }
}

static void
p2i(UINT8 *out_, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, out_ += 4) {
        INT32 v = L24(&palette->palette[in[x] * 4]) >> 16;
        memcpy(out_, &v, sizeof(v));
    }
}

static void
pa2i(UINT8 *out_, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    INT32 *out = (INT32 *)out_;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = L24(&palette->palette[in[0] * 4]) >> 16;
    }
}

static void
p2f(UINT8 *out_, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, out_ += 4) {
        FLOAT32 v = L(&palette->palette[in[x] * 4]) / 1000.0F;
        memcpy(out_, &v, sizeof(v));
    }
}

static void
pa2f(UINT8 *out_, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    FLOAT32 *out = (FLOAT32 *)out_;
    for (x = 0; x < xsize; x++, in += 4) {
        *out++ = (float)L(&palette->palette[in[0] * 4]) / 1000.0F;
    }
}

static void
p2rgb(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++) {
        const UINT8 *rgb = &palette->palette[*in++ * 4];
        *out++ = rgb[0];
        *out++ = rgb[1];
        *out++ = rgb[2];
        *out++ = 255;
    }
}

static void
pa2rgb(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        const UINT8 *rgb = &palette->palette[in[0] * 4];
        *out++ = rgb[0];
        *out++ = rgb[1];
        *out++ = rgb[2];
        *out++ = 255;
    }
}

static void
p2hsv(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, out += 4) {
        const UINT8 *rgb = &palette->palette[*in++ * 4];
        rgb2hsv_row(out, rgb);
        out[3] = 255;
    }
}

static void
pa2hsv(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, in += 4, out += 4) {
        const UINT8 *rgb = &palette->palette[in[0] * 4];
        rgb2hsv_row(out, rgb);
        out[3] = 255;
    }
}

static void
p2rgba(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++) {
        const UINT8 *rgba = &palette->palette[*in++ * 4];
        *out++ = rgba[0];
        *out++ = rgba[1];
        *out++ = rgba[2];
        *out++ = rgba[3];
    }
}

static void
pa2rgba(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    int x;
    for (x = 0; x < xsize; x++, in += 4) {
        const UINT8 *rgb = &palette->palette[in[0] * 4];
        *out++ = rgb[0];
        *out++ = rgb[1];
        *out++ = rgb[2];
        *out++ = in[3];
    }
}

static void
p2cmyk(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    p2rgb(out, in, xsize, palette);
    rgb2cmyk(out, out, xsize);
}

static void
pa2cmyk(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    pa2rgb(out, in, xsize, palette);
    rgb2cmyk(out, out, xsize);
}

static void
p2ycbcr(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    p2rgb(out, in, xsize, palette);
    ImagingConvertRGB2YCbCr(out, out, xsize);
}

static void
pa2ycbcr(UINT8 *out, const UINT8 *in, int xsize, ImagingPalette palette) {
    pa2rgb(out, in, xsize, palette);
    ImagingConvertRGB2YCbCr(out, out, xsize);
}

static Imaging
frompalette(Imaging imOut, Imaging imIn, const char *mode) {
    ImagingSectionCookie cookie;
    int alpha;
    int y;
    void (*convert)(UINT8 *, const UINT8 *, int, ImagingPalette);

    /* Map palette image to L, RGB, RGBA, or CMYK */

    if (!imIn->palette) {
        return (Imaging)ImagingError_ValueError("no palette");
    }

    alpha = !strcmp(imIn->mode, "PA");

    if (strcmp(mode, "1") == 0) {
        convert = alpha ? pa2bit : p2bit;
    } else if (strcmp(mode, "L") == 0) {
        convert = alpha ? pa2l : p2l;
    } else if (strcmp(mode, "LA") == 0) {
        convert = alpha ? pa2la : p2la;
    } else if (strcmp(mode, "P") == 0) {
        convert = pa2p;
    } else if (strcmp(mode, "PA") == 0) {
        convert = p2pa;
    } else if (strcmp(mode, "I") == 0) {
        convert = alpha ? pa2i : p2i;
    } else if (strcmp(mode, "F") == 0) {
        convert = alpha ? pa2f : p2f;
    } else if (strcmp(mode, "RGB") == 0) {
        convert = alpha ? pa2rgb : p2rgb;
    } else if (strcmp(mode, "RGBA") == 0 || strcmp(mode, "RGBX") == 0) {
        convert = alpha ? pa2rgba : p2rgba;
    } else if (strcmp(mode, "CMYK") == 0) {
        convert = alpha ? pa2cmyk : p2cmyk;
    } else if (strcmp(mode, "YCbCr") == 0) {
        convert = alpha ? pa2ycbcr : p2ycbcr;
    } else if (strcmp(mode, "HSV") == 0) {
        convert = alpha ? pa2hsv : p2hsv;
    } else {
        return (Imaging)ImagingError_ValueError("conversion not supported");
    }

    imOut = ImagingNew2Dirty(mode, imOut, imIn);
    if (!imOut) {
        return NULL;
    }
    if (strcmp(mode, "P") == 0 || strcmp(mode, "PA") == 0) {
        ImagingPaletteDelete(imOut->palette);
        imOut->palette = ImagingPaletteDuplicate(imIn->palette);
    }

    ImagingSectionEnter(&cookie);
    for (y = 0; y < imIn->ysize; y++) {
        (*convert)(
            (UINT8 *)imOut->image[y],
            (UINT8 *)imIn->image[y],
            imIn->xsize,
            imIn->palette);
    }
    ImagingSectionLeave(&cookie);

    return imOut;
}

#if defined(_MSC_VER)
#pragma optimize("", off)
#endif
static Imaging
topalette(
    Imaging imOut,
    Imaging imIn,
    const char *mode,
    ImagingPalette inpalette,
    int dither) {
    ImagingSectionCookie cookie;
    int alpha;
    int x, y;
    ImagingPalette palette = inpalette;

    /* Map L or RGB/RGBX/RGBA to palette image */
    if (strcmp(imIn->mode, "L") != 0 && strncmp(imIn->mode, "RGB", 3) != 0) {
        return (Imaging)ImagingError_ValueError("conversion not supported");
    }

    alpha = !strcmp(mode, "PA");

    if (palette == NULL) {
        /* FIXME: make user configurable */
        if (imIn->bands == 1) {
            palette = ImagingPaletteNew("RGB");

            palette->size = 256;
            int i;
            for (i = 0; i < 256; i++) {
                palette->palette[i * 4] = palette->palette[i * 4 + 1] =
                    palette->palette[i * 4 + 2] = (UINT8)i;
            }
        } else {
            palette = ImagingPaletteNewBrowser(); /* Standard colour cube */
        }
    }

    if (!palette) {
        return (Imaging)ImagingError_ValueError("no palette");
    }

    imOut = ImagingNew2Dirty(mode, imOut, imIn);
    if (!imOut) {
        if (palette != inpalette) {
            ImagingPaletteDelete(palette);
        }
        return NULL;
    }

    ImagingPaletteDelete(imOut->palette);
    imOut->palette = ImagingPaletteDuplicate(palette);

    if (imIn->bands == 1) {
        /* grayscale image */

        /* Grayscale palette: copy data as is */
        ImagingSectionEnter(&cookie);
        for (y = 0; y < imIn->ysize; y++) {
            if (alpha) {
                l2la((UINT8 *)imOut->image[y], (UINT8 *)imIn->image[y], imIn->xsize);
            } else {
                memcpy(imOut->image[y], imIn->image[y], imIn->linesize);
            }
        }
        ImagingSectionLeave(&cookie);

    } else {
        /* colour image */

        /* Create mapping cache */
        if (ImagingPaletteCachePrepare(palette) < 0) {
            ImagingDelete(imOut);
            if (palette != inpalette) {
                ImagingPaletteDelete(palette);
            }
            return NULL;
        }

        if (dither) {
            /* floyd-steinberg dither */

            int *errors;
            errors = calloc(imIn->xsize + 1, sizeof(int) * 3);
            if (!errors) {
                ImagingDelete(imOut);
                return ImagingError_MemoryError();
            }

            /* Map each pixel to the nearest palette entry */
            ImagingSectionEnter(&cookie);
            for (y = 0; y < imIn->ysize; y++) {
                int r, r0, r1, r2;
                int g, g0, g1, g2;
                int b, b0, b1, b2;
                UINT8 *in = (UINT8 *)imIn->image[y];
                UINT8 *out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];
                int *e = errors;

                r = r0 = r1 = 0;
                g = g0 = g1 = 0;
                b = b0 = b1 = b2 = 0;

                for (x = 0; x < imIn->xsize; x++, in += 4) {
                    int d2;
                    INT16 *cache;

                    r = CLIP8(in[0] + (r + e[3 + 0]) / 16);
                    g = CLIP8(in[1] + (g + e[3 + 1]) / 16);
                    b = CLIP8(in[2] + (b + e[3 + 2]) / 16);

                    /* get closest colour */
                    cache = &ImagingPaletteCache(palette, r, g, b);
                    if (cache[0] == 0x100) {
                        ImagingPaletteCacheUpdate(palette, r, g, b);
                    }
                    if (alpha) {
                        out[x * 4] = out[x * 4 + 1] = out[x * 4 + 2] = (UINT8)cache[0];
                        out[x * 4 + 3] = 255;
                    } else {
                        out[x] = (UINT8)cache[0];
                    }

                    r -= (int)palette->palette[cache[0] * 4];
                    g -= (int)palette->palette[cache[0] * 4 + 1];
                    b -= (int)palette->palette[cache[0] * 4 + 2];

                    /* propagate errors (don't ask ;-) */
                    r2 = r;
                    d2 = r + r;
                    r += d2;
                    e[0] = r + r0;
                    r += d2;
                    r0 = r + r1;
                    r1 = r2;
                    r += d2;
                    g2 = g;
                    d2 = g + g;
                    g += d2;
                    e[1] = g + g0;
                    g += d2;
                    g0 = g + g1;
                    g1 = g2;
                    g += d2;
                    b2 = b;
                    d2 = b + b;
                    b += d2;
                    e[2] = b + b0;
                    b += d2;
                    b0 = b + b1;
                    b1 = b2;
                    b += d2;

                    e += 3;
                }

                e[0] = b0;
                e[1] = b1;
                e[2] = b2;
            }
            ImagingSectionLeave(&cookie);
            free(errors);

        } else {
            /* closest colour */
            ImagingSectionEnter(&cookie);
            for (y = 0; y < imIn->ysize; y++) {
                int r, g, b;
                UINT8 *in = (UINT8 *)imIn->image[y];
                UINT8 *out = alpha ? (UINT8 *)imOut->image32[y] : imOut->image8[y];

                for (x = 0; x < imIn->xsize; x++, in += 4) {
                    INT16 *cache;

                    r = in[0];
                    g = in[1];
                    b = in[2];

                    /* get closest colour */
                    cache = &ImagingPaletteCache(palette, r, g, b);
                    if (cache[0] == 0x100) {
                        ImagingPaletteCacheUpdate(palette, r, g, b);
                    }
                    if (alpha) {
                        out[x * 4] = out[x * 4 + 1] = out[x * 4 + 2] = (UINT8)cache[0];
                        out[x * 4 + 3] = 255;
                    } else {
                        out[x] = (UINT8)cache[0];
                    }
                }
            }
            ImagingSectionLeave(&cookie);
        }
        if (inpalette != palette) {
            ImagingPaletteCacheDelete(palette);
        }
    }

    if (inpalette != palette) {
        ImagingPaletteDelete(palette);
    }

    return imOut;
}

static Imaging
tobilevel(Imaging imOut, Imaging imIn) {
    ImagingSectionCookie cookie;
    int x, y;
    int *errors;

    /* Map L or RGB to dithered 1 image */
    if (strcmp(imIn->mode, "L") != 0 && strcmp(imIn->mode, "RGB") != 0) {
        return (Imaging)ImagingError_ValueError("conversion not supported");
    }

    imOut = ImagingNew2Dirty("1", imOut, imIn);
    if (!imOut) {
        return NULL;
    }

    errors = calloc(imIn->xsize + 1, sizeof(int));
    if (!errors) {
        ImagingDelete(imOut);
        return ImagingError_MemoryError();
    }

    if (imIn->bands == 1) {
        /* map each pixel to black or white, using error diffusion */
        ImagingSectionEnter(&cookie);
        for (y = 0; y < imIn->ysize; y++) {
            int l, l0, l1, l2, d2;
            UINT8 *in = (UINT8 *)imIn->image[y];
            UINT8 *out = imOut->image8[y];

            l = l0 = l1 = 0;

            for (x = 0; x < imIn->xsize; x++) {
                /* pick closest colour */
                l = CLIP8(in[x] + (l + errors[x + 1]) / 16);
                out[x] = (l > 128) ? 255 : 0;

                /* propagate errors */
                l -= (int)out[x];
                l2 = l;
                d2 = l + l;
                l += d2;
                errors[x] = l + l0;
                l += d2;
                l0 = l + l1;
                l1 = l2;
                l += d2;
            }

            errors[x] = l0;
        }
        ImagingSectionLeave(&cookie);

    } else {
        /* map each pixel to black or white, using error diffusion */
        ImagingSectionEnter(&cookie);
        for (y = 0; y < imIn->ysize; y++) {
            int l, l0, l1, l2, d2;
            UINT8 *in = (UINT8 *)imIn->image[y];
            UINT8 *out = imOut->image8[y];

            l = l0 = l1 = 0;

            for (x = 0; x < imIn->xsize; x++, in += 4) {
                /* pick closest colour */
                l = CLIP8(L(in) / 1000 + (l + errors[x + 1]) / 16);
                out[x] = (l > 128) ? 255 : 0;

                /* propagate errors */
                l -= (int)out[x];
                l2 = l;
                d2 = l + l;
                l += d2;
                errors[x] = l + l0;
                l += d2;
                l0 = l + l1;
                l1 = l2;
                l += d2;
            }

            errors[x] = l0;
        }
        ImagingSectionLeave(&cookie);
    }

    free(errors);

    return imOut;
}
#if defined(_MSC_VER)
#pragma optimize("", on)
#endif

static Imaging
convert(
    Imaging imOut, Imaging imIn, const char *mode, ImagingPalette palette, int dither) {
    ImagingSectionCookie cookie;
    ImagingShuffler convert;
    int y;

    if (!imIn) {
        return (Imaging)ImagingError_ModeError();
    }

    if (!mode) {
        /* Map palette image to full depth */
        if (!imIn->palette) {
            return (Imaging)ImagingError_ModeError();
        }
        mode = imIn->palette->mode;
    } else {
        /* Same mode? */
        if (!strcmp(imIn->mode, mode)) {
            return ImagingCopy2(imOut, imIn);
        }
    }

    /* test for special conversions */

    if (strcmp(imIn->mode, "P") == 0 || strcmp(imIn->mode, "PA") == 0) {
        return frompalette(imOut, imIn, mode);
    }

    if (strcmp(mode, "P") == 0 || strcmp(mode, "PA") == 0) {
        return topalette(imOut, imIn, mode, palette, dither);
    }

    if (dither && strcmp(mode, "1") == 0) {
        return tobilevel(imOut, imIn);
    }

    /* standard conversion machinery */

    convert = NULL;

    for (y = 0; converters[y].from; y++) {
        if (!strcmp(imIn->mode, converters[y].from) &&
            !strcmp(mode, converters[y].to)) {
            convert = converters[y].convert;
            break;
        }
    }

    if (!convert) {
#ifdef notdef
        return (Imaging)ImagingError_ValueError("conversion not supported");
#else
        static char buf[100];
        snprintf(buf, 100, "conversion from %.10s to %.10s not supported", imIn->mode, mode);
        return (Imaging)ImagingError_ValueError(buf);
#endif
    }

    imOut = ImagingNew2Dirty(mode, imOut, imIn);
    if (!imOut) {
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    for (y = 0; y < imIn->ysize; y++) {
        (*convert)((UINT8 *)imOut->image[y], (UINT8 *)imIn->image[y], imIn->xsize);
    }
    ImagingSectionLeave(&cookie);

    return imOut;
}

Imaging
ImagingConvert(Imaging imIn, const char *mode, ImagingPalette palette, int dither) {
    return convert(NULL, imIn, mode, palette, dither);
}

Imaging
ImagingConvert2(Imaging imOut, Imaging imIn) {
    return convert(imOut, imIn, imOut->mode, NULL, 0);
}

Imaging
ImagingConvertTransparent(Imaging imIn, const char *mode, int r, int g, int b) {
    ImagingSectionCookie cookie;
    ImagingShuffler convert;
    Imaging imOut = NULL;
    int y;

    if (!imIn) {
        return (Imaging)ImagingError_ModeError();
    }

    if (strcmp(imIn->mode, "RGB") == 0 && strcmp(mode, "RGBA") == 0) {
        convert = rgb2rgba;
    } else if ((strcmp(imIn->mode, "1") == 0 ||
                strcmp(imIn->mode, "I") == 0 ||
                strcmp(imIn->mode, "L") == 0
               ) && (
                strcmp(mode, "RGBA") == 0 ||
                strcmp(mode, "LA") == 0
               )) {
        if (strcmp(imIn->mode, "1") == 0) {
            convert = bit2rgb;
        } else if (strcmp(imIn->mode, "I") == 0) {
            convert = i2rgb;
        } else {
            convert = l2rgb;
        }
        g = b = r;
    } else {
        static char buf[100];
        snprintf(
            buf,
            100,
            "conversion from %.10s to %.10s not supported in convert_transparent",
            imIn->mode,
            mode);
        return (Imaging)ImagingError_ValueError(buf);
    }

    imOut = ImagingNew2Dirty(mode, imOut, imIn);
    if (!imOut) {
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    for (y = 0; y < imIn->ysize; y++) {
        (*convert)((UINT8 *)imOut->image[y], (UINT8 *)imIn->image[y], imIn->xsize);
        rgbT2rgba((UINT8 *)imOut->image[y], imIn->xsize, r, g, b);
    }
    ImagingSectionLeave(&cookie);

    return imOut;
}

Imaging
ImagingConvertInPlace(Imaging imIn, const char *mode) {
    ImagingSectionCookie cookie;
    ImagingShuffler convert;
    int y;

    /* limited support for inplace conversion */
    if (strcmp(imIn->mode, "L") == 0 && strcmp(mode, "1") == 0) {
        convert = l2bit;
    } else if (strcmp(imIn->mode, "1") == 0 && strcmp(mode, "L") == 0) {
        convert = bit2l;
    } else {
        return ImagingError_ModeError();
    }

    ImagingSectionEnter(&cookie);
    for (y = 0; y < imIn->ysize; y++) {
        (*convert)((UINT8 *)imIn->image[y], (UINT8 *)imIn->image[y], imIn->xsize);
    }
    ImagingSectionLeave(&cookie);

    return imIn;
}
