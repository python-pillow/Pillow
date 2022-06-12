/*
 * The Python Imaging Library.
 * $Id$
 *
 * decoder for JPEG2000 image data.
 *
 * history:
 * 2014-03-12 ajh  Created
 *
 * Copyright (c) 2014 Coriolis Systems Limited
 * Copyright (c) 2014 Alastair Houghton
 *
 * See the README file for details on usage and redistribution.
 */

#include "Imaging.h"

#ifdef HAVE_OPENJPEG

#include <stdlib.h>
#include "Jpeg2K.h"

typedef struct {
    OPJ_UINT32 tile_index;
    OPJ_UINT32 data_size;
    OPJ_INT32 x0, y0, x1, y1;
    OPJ_UINT32 nb_comps;
} JPEG2KTILEINFO;

/* -------------------------------------------------------------------- */
/* Error handler                                                        */
/* -------------------------------------------------------------------- */

static void
j2k_error(const char *msg, void *client_data) {
    JPEG2KDECODESTATE *state = (JPEG2KDECODESTATE *)client_data;
    free((void *)state->error_msg);
    state->error_msg = strdup(msg);
}

/* -------------------------------------------------------------------- */
/* Buffer input stream                                                  */
/* -------------------------------------------------------------------- */

static OPJ_SIZE_T
j2k_read(void *p_buffer, OPJ_SIZE_T p_nb_bytes, void *p_user_data) {
    ImagingCodecState state = (ImagingCodecState)p_user_data;

    size_t len = _imaging_read_pyFd(state->fd, p_buffer, p_nb_bytes);

    return len ? len : (OPJ_SIZE_T)-1;
}

static OPJ_OFF_T
j2k_skip(OPJ_OFF_T p_nb_bytes, void *p_user_data) {
    off_t pos;
    ImagingCodecState state = (ImagingCodecState)p_user_data;

    _imaging_seek_pyFd(state->fd, p_nb_bytes, SEEK_CUR);
    pos = _imaging_tell_pyFd(state->fd);

    return pos ? pos : (OPJ_OFF_T)-1;
}

/* -------------------------------------------------------------------- */
/* Unpackers                                                            */
/* -------------------------------------------------------------------- */

typedef void (*j2k_unpacker_t)(
    opj_image_t *in, const JPEG2KTILEINFO *tileInfo, const UINT8 *data, Imaging im);

struct j2k_decode_unpacker {
    const char *mode;
    OPJ_COLOR_SPACE color_space;
    unsigned components;
    /* bool indicating if unpacker supports subsampling */
    int subsampling;
    j2k_unpacker_t unpacker;
};

static inline unsigned
j2ku_shift(unsigned x, int n) {
    if (n < 0) {
        return x >> -n;
    } else {
        return x << n;
    }
}

static void
j2ku_gray_l(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;

    unsigned x, y;

    if (csiz == 3) {
        csiz = 4;
    }

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }

    /* csiz*h*w + offset = tileinfo.datasize */
    switch (csiz) {
        case 1:
            for (y = 0; y < h; ++y) {
                const UINT8 *data = &tiledata[y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
        case 2:
            for (y = 0; y < h; ++y) {
                const UINT16 *data = (const UINT16 *)&tiledata[2 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
        case 4:
            for (y = 0; y < h; ++y) {
                const UINT32 *data = (const UINT32 *)&tiledata[4 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
    }
}

static void
j2ku_gray_i(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 16 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;

    unsigned x, y;

    if (csiz == 3) {
        csiz = 4;
    }

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }

    switch (csiz) {
        case 1:
            for (y = 0; y < h; ++y) {
                const UINT8 *data = &tiledata[y * w];
                UINT16 *row = (UINT16 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
        case 2:
            for (y = 0; y < h; ++y) {
                const UINT16 *data = (const UINT16 *)&tiledata[2 * y * w];
                UINT16 *row = (UINT16 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT16 pixel = j2ku_shift(offset + *data++, shift);
                    #ifdef WORDS_BIGENDIAN
                        pixel = (pixel >> 8) | (pixel << 8);
                    #endif
                    *row++ = pixel;
                }
            }
            break;
        case 4:
            for (y = 0; y < h; ++y) {
                const UINT32 *data = (const UINT32 *)&tiledata[4 * y * w];
                UINT16 *row = (UINT16 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    *row++ = j2ku_shift(offset + *data++, shift);
                }
            }
            break;
    }
}

static void
j2ku_gray_rgb(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;

    unsigned x, y;

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }

    if (csiz == 3) {
        csiz = 4;
    }

    switch (csiz) {
        case 1:
            for (y = 0; y < h; ++y) {
                const UINT8 *data = &tiledata[y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT8 byte = j2ku_shift(offset + *data++, shift);
                    row[0] = row[1] = row[2] = byte;
                    row[3] = 0xff;
                    row += 4;
                }
            }
            break;
        case 2:
            for (y = 0; y < h; ++y) {
                const UINT16 *data = (UINT16 *)&tiledata[2 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT8 byte = j2ku_shift(offset + *data++, shift);
                    row[0] = row[1] = row[2] = byte;
                    row[3] = 0xff;
                    row += 4;
                }
            }
            break;
        case 4:
            for (y = 0; y < h; ++y) {
                const UINT32 *data = (UINT32 *)&tiledata[4 * y * w];
                UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
                for (x = 0; x < w; ++x) {
                    UINT8 byte = j2ku_shift(offset + *data++, shift);
                    row[0] = row[1] = row[2] = byte;
                    row[3] = 0xff;
                    row += 4;
                }
            }
            break;
    }
}

static void
j2ku_graya_la(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int csiz = (in->comps[0].prec + 7) >> 3;
    int ashift = 8 - in->comps[1].prec;
    int aoffset = in->comps[1].sgnd ? 1 << (in->comps[1].prec - 1) : 0;
    int acsiz = (in->comps[1].prec + 7) >> 3;
    const UINT8 *atiledata;

    unsigned x, y;

    if (csiz == 3) {
        csiz = 4;
    }
    if (acsiz == 3) {
        acsiz = 4;
    }

    if (shift < 0) {
        offset += 1 << (-shift - 1);
    }
    if (ashift < 0) {
        aoffset += 1 << (-ashift - 1);
    }

    atiledata = tiledata + csiz * w * h;

    for (y = 0; y < h; ++y) {
        const UINT8 *data = &tiledata[csiz * y * w];
        const UINT8 *adata = &atiledata[acsiz * y * w];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (x = 0; x < w; ++x) {
            UINT32 word = 0, aword = 0, byte;

            switch (csiz) {
                case 1:
                    word = *data++;
                    break;
                case 2:
                    word = *(const UINT16 *)data;
                    data += 2;
                    break;
                case 4:
                    word = *(const UINT32 *)data;
                    data += 4;
                    break;
            }

            switch (acsiz) {
                case 1:
                    aword = *adata++;
                    break;
                case 2:
                    aword = *(const UINT16 *)adata;
                    adata += 2;
                    break;
                case 4:
                    aword = *(const UINT32 *)adata;
                    adata += 4;
                    break;
            }

            byte = j2ku_shift(offset + word, shift);
            row[0] = row[1] = row[2] = byte;
            row[3] = j2ku_shift(aoffset + aword, ashift);
            row += 4;
        }
    }
}

static void
j2ku_srgb_rgb(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[3], offsets[3], csiz[3];
    unsigned dx[3], dy[3];
    const UINT8 *cdata[3];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 3; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[3];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (n = 0; n < 3; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 3; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row[3] = 0xff;
            row += 4;
        }
    }
}

static void
j2ku_sycc_rgb(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[3], offsets[3], csiz[3];
    unsigned dx[3], dy[3];
    const UINT8 *cdata[3];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 3; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[3];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        UINT8 *row_start = row;
        for (n = 0; n < 3; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 3; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row[3] = 0xff;
            row += 4;
        }

        ImagingConvertYCbCr2RGB(row_start, row_start, w);
    }
}

static void
j2ku_srgba_rgba(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[4], offsets[4], csiz[4];
    unsigned dx[4], dy[4];
    const UINT8 *cdata[4];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 4; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[4];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (n = 0; n < 4; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 4; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row += 4;
        }
    }
}

static void
j2ku_sycca_rgba(
    opj_image_t *in,
    const JPEG2KTILEINFO *tileinfo,
    const UINT8 *tiledata,
    Imaging im) {
    unsigned x0 = tileinfo->x0 - in->x0, y0 = tileinfo->y0 - in->y0;
    unsigned w = tileinfo->x1 - tileinfo->x0;
    unsigned h = tileinfo->y1 - tileinfo->y0;

    int shifts[4], offsets[4], csiz[4];
    unsigned dx[4], dy[4];
    const UINT8 *cdata[4];
    const UINT8 *cptr = tiledata;
    unsigned n, x, y;

    for (n = 0; n < 4; ++n) {
        cdata[n] = cptr;
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        csiz[n] = (in->comps[n].prec + 7) >> 3;
        dx[n] = (in->comps[n].dx);
        dy[n] = (in->comps[n].dy);

        if (csiz[n] == 3) {
            csiz[n] = 4;
        }

        if (shifts[n] < 0) {
            offsets[n] += 1 << (-shifts[n] - 1);
        }

        cptr += csiz[n] * (w / dx[n]) * (h / dy[n]);
    }

    for (y = 0; y < h; ++y) {
        const UINT8 *data[4];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        UINT8 *row_start = row;
        for (n = 0; n < 4; ++n) {
            data[n] = &cdata[n][csiz[n] * (y / dy[n]) * (w / dx[n])];
        }

        for (x = 0; x < w; ++x) {
            for (n = 0; n < 4; ++n) {
                UINT32 word = 0;

                switch (csiz[n]) {
                    case 1:
                        word = data[n][x / dx[n]];
                        break;
                    case 2:
                        word = ((const UINT16 *)data[n])[x / dx[n]];
                        break;
                    case 4:
                        word = ((const UINT32 *)data[n])[x / dx[n]];
                        break;
                }

                row[n] = j2ku_shift(offsets[n] + word, shifts[n]);
            }
            row += 4;
        }

        ImagingConvertYCbCr2RGB(row_start, row_start, w);
    }
}

static const struct j2k_decode_unpacker j2k_unpackers[] = {
    {"L", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_l},
    {"I;16", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_i},
    {"I;16B", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_i},
    {"LA", OPJ_CLRSPC_GRAY, 2, 0, j2ku_graya_la},
    {"RGB", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_rgb},
    {"RGB", OPJ_CLRSPC_GRAY, 2, 0, j2ku_gray_rgb},
    {"RGB", OPJ_CLRSPC_SRGB, 3, 1, j2ku_srgb_rgb},
    {"RGB", OPJ_CLRSPC_SYCC, 3, 1, j2ku_sycc_rgb},
    {"RGB", OPJ_CLRSPC_SRGB, 4, 1, j2ku_srgb_rgb},
    {"RGB", OPJ_CLRSPC_SYCC, 4, 1, j2ku_sycc_rgb},
    {"RGBA", OPJ_CLRSPC_GRAY, 1, 0, j2ku_gray_rgb},
    {"RGBA", OPJ_CLRSPC_GRAY, 2, 0, j2ku_graya_la},
    {"RGBA", OPJ_CLRSPC_SRGB, 3, 1, j2ku_srgb_rgb},
    {"RGBA", OPJ_CLRSPC_SYCC, 3, 1, j2ku_sycc_rgb},
    {"RGBA", OPJ_CLRSPC_SRGB, 4, 1, j2ku_srgba_rgba},
    {"RGBA", OPJ_CLRSPC_SYCC, 4, 1, j2ku_sycca_rgba},
};

/* -------------------------------------------------------------------- */
/* Decoder                                                              */
/* -------------------------------------------------------------------- */

enum {
    J2K_STATE_START = 0,
    J2K_STATE_DECODING = 1,
    J2K_STATE_DONE = 2,
    J2K_STATE_FAILED = 3,
};

static int
j2k_decode_entry(Imaging im, ImagingCodecState state) {
    JPEG2KDECODESTATE *context = (JPEG2KDECODESTATE *)state->context;
    opj_stream_t *stream = NULL;
    opj_image_t *image = NULL;
    opj_codec_t *codec = NULL;
    opj_dparameters_t params;
    OPJ_COLOR_SPACE color_space;
    j2k_unpacker_t unpack = NULL;
    size_t buffer_size = 0, tile_bytes = 0;
    unsigned n, tile_height, tile_width;
    int subsampling;
    int total_component_width = 0;

    stream = opj_stream_create(BUFFER_SIZE, OPJ_TRUE);

    if (!stream) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    opj_stream_set_read_function(stream, j2k_read);
    opj_stream_set_skip_function(stream, j2k_skip);

    /* OpenJPEG 2.0 doesn't have OPJ_VERSION_MAJOR */
#ifndef OPJ_VERSION_MAJOR
    opj_stream_set_user_data(stream, state);
#else
    opj_stream_set_user_data(stream, state, NULL);

    /* Hack: if we don't know the length, the largest file we can
       possibly support is 4GB.  We can't go larger than this, because
       OpenJPEG truncates this value for the final box in the file, and
       the box lengths in OpenJPEG are currently 32 bit. */
    if (context->length < 0) {
        opj_stream_set_user_data_length(stream, 0xffffffff);
    } else {
        opj_stream_set_user_data_length(stream, context->length);
    }
#endif

    /* Setup decompression context */
    context->error_msg = NULL;

    opj_set_default_decoder_parameters(&params);
    params.cp_reduce = context->reduce;
    params.cp_layer = context->layers;

    codec = opj_create_decompress(context->format);

    if (!codec) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    opj_set_error_handler(codec, j2k_error, context);
    opj_setup_decoder(codec, &params);

    if (!opj_read_header(stream, codec, &image)) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    /* Check that this image is something we can handle */
    if (image->numcomps < 1 || image->numcomps > 4 ||
        image->color_space == OPJ_CLRSPC_UNKNOWN) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    /*
     * Find first component with subsampling.
     *
     * This is a heuristic to determine the colorspace if unspecified.
     */
    subsampling = -1;
    for (n = 0; n < image->numcomps; ++n) {
        if (image->comps[n].dx != 1 || image->comps[n].dy != 1) {
            subsampling = n;
            break;
        }
    }

    /*
         Colorspace    Number of components    PIL mode
       ------------------------------------------------------
         sRGB          3                       RGB
         sRGB          4                       RGBA
         gray          1                       L or I
         gray          2                       LA
         YCC           3                       YCbCr


       If colorspace is unspecified, we assume:

           Number of components   Subsampling   Colorspace
         -------------------------------------------------------
           1                      Any           gray
           2                      Any           gray (+ alpha)
           3                      -1, 0         sRGB
           3                      1, 2          YCbCr
           4                      -1, 0, 3      sRGB (+ alpha)
           4                      1, 2          YCbCr (+ alpha)

    */

    /* Find the correct unpacker */
    color_space = image->color_space;

    if (color_space == OPJ_CLRSPC_UNSPECIFIED) {
        switch (image->numcomps) {
            case 1:
            case 2:
                color_space = OPJ_CLRSPC_GRAY;
                break;
            case 3:
            case 4:
                switch (subsampling) {
                    case -1:
                    case 0:
                    case 3:
                        color_space = OPJ_CLRSPC_SRGB;
                        break;
                    case 1:
                    case 2:
                        color_space = OPJ_CLRSPC_SYCC;
                        break;
                }
            break;
        }
    }

    for (n = 0; n < sizeof(j2k_unpackers) / sizeof(j2k_unpackers[0]); ++n) {
        if (color_space == j2k_unpackers[n].color_space &&
            image->numcomps == j2k_unpackers[n].components &&
            (j2k_unpackers[n].subsampling || (subsampling == -1)) &&
            strcmp(im->mode, j2k_unpackers[n].mode) == 0) {
            unpack = j2k_unpackers[n].unpacker;
            break;
        }
    }

    if (!unpack) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    /* Decode the image tile-by-tile; this means we only need use as much
       memory as is required for one tile's worth of components. */
    for (;;) {
        JPEG2KTILEINFO tile_info;
        OPJ_BOOL should_continue;
        unsigned correction = (1 << params.cp_reduce) - 1;

        if (!opj_read_tile_header(
                codec,
                stream,
                &tile_info.tile_index,
                &tile_info.data_size,
                &tile_info.x0,
                &tile_info.y0,
                &tile_info.x1,
                &tile_info.y1,
                &tile_info.nb_comps,
                &should_continue)) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
        }

        if (!should_continue) {
            break;
        }

        /* Adjust the tile co-ordinates based on the reduction (OpenJPEG
           doesn't do this for us) */
        tile_info.x0 = (tile_info.x0 + correction) >> context->reduce;
        tile_info.y0 = (tile_info.y0 + correction) >> context->reduce;
        tile_info.x1 = (tile_info.x1 + correction) >> context->reduce;
        tile_info.y1 = (tile_info.y1 + correction) >> context->reduce;

        /* Check the tile bounds; if the tile is outside the image area,
           or if it has a negative width or height (i.e. the coordinates are
           swapped), bail. */
        if (tile_info.x0 >= tile_info.x1 || tile_info.y0 >= tile_info.y1 ||
            tile_info.x0 < 0 || tile_info.y0 < 0 ||
            (OPJ_UINT32)tile_info.x0 < image->x0 ||
            (OPJ_UINT32)tile_info.y0 < image->y0 ||
            (OPJ_INT32)(tile_info.x1 - image->x0) > im->xsize ||
            (OPJ_INT32)(tile_info.y1 - image->y0) > im->ysize) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
        }

        if (tile_info.nb_comps != image->numcomps) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
        }

        /* Sometimes the tile_info.datasize we get back from openjpeg
           is less than sum(comp_bytes)*w*h, and we overflow in the
           shuffle stage */

        tile_width = tile_info.x1 - tile_info.x0;
        tile_height = tile_info.y1 - tile_info.y0;

        /* Total component width = sum (component_width) e.g, it's
         legal for an la file to have a 1 byte width for l, and 4 for
         a, and then a malicious file could have a smaller tile_bytes
        */

        for (n=0; n < tile_info.nb_comps; n++) {
            // see csize /acsize calcs
            int csize = (image->comps[n].prec + 7) >> 3;
            csize = (csize == 3) ? 4 : csize;
            total_component_width += csize;
        }
        if ((tile_width > UINT_MAX / total_component_width) ||
            (tile_height > UINT_MAX / total_component_width) ||
            (tile_width > UINT_MAX / (tile_height * total_component_width)) ||
            (tile_height > UINT_MAX / (tile_width * total_component_width))) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
        }

        tile_bytes = tile_width * tile_height * total_component_width;

        if (tile_bytes > tile_info.data_size) {
            tile_info.data_size = tile_bytes;
        }

        if (buffer_size < tile_info.data_size) {
            /* malloc check ok, overflow and tile size sanity check above */
            UINT8 *new = realloc(state->buffer, tile_info.data_size);
            if (!new) {
                state->errcode = IMAGING_CODEC_MEMORY;
                state->state = J2K_STATE_FAILED;
                goto quick_exit;
            }
            /* Undefined behavior, sometimes decode_tile_data doesn't
               fill the buffer and we do things with it later, leading
               to valgrind errors. */
            memset(new, 0, tile_info.data_size);
            state->buffer = new;
            buffer_size = tile_info.data_size;
        }

        if (!opj_decode_tile_data(
                codec,
                tile_info.tile_index,
                (OPJ_BYTE *)state->buffer,
                tile_info.data_size,
                stream)) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
        }

        unpack(image, &tile_info, state->buffer, im);
    }

    if (!opj_end_decompress(codec, stream)) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    state->state = J2K_STATE_DONE;
    state->errcode = IMAGING_CODEC_END;

    if (context->pfile) {
        if (fclose(context->pfile)) {
            context->pfile = NULL;
        }
    }

quick_exit:
    if (codec) {
        opj_destroy_codec(codec);
    }
    if (image) {
        opj_image_destroy(image);
    }
    if (stream) {
        opj_stream_destroy(stream);
    }

    return -1;
}

int
ImagingJpeg2KDecode(Imaging im, ImagingCodecState state, UINT8 *buf, Py_ssize_t bytes) {
    if (bytes) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        return -1;
    }

    if (state->state == J2K_STATE_DONE || state->state == J2K_STATE_FAILED) {
        return -1;
    }

    if (state->state == J2K_STATE_START) {
        state->state = J2K_STATE_DECODING;

        return j2k_decode_entry(im, state);
    }

    if (state->state == J2K_STATE_DECODING) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        return -1;
    }
    return -1;
}

/* -------------------------------------------------------------------- */
/* Cleanup                                                              */
/* -------------------------------------------------------------------- */

int
ImagingJpeg2KDecodeCleanup(ImagingCodecState state) {
    JPEG2KDECODESTATE *context = (JPEG2KDECODESTATE *)state->context;

    if (context->error_msg) {
        free((void *)context->error_msg);
    }

    context->error_msg = NULL;

    return -1;
}

const char *
ImagingJpeg2KVersion(void) {
    return opj_version();
}

#endif /* HAVE_OPENJPEG */

/*
 * Local Variables:
 * c-basic-offset: 4
 * End:
 *
 */
