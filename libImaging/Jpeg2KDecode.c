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

#include <unistd.h>
#include "Jpeg2K.h"

/* -------------------------------------------------------------------- */
/* Error handler                                                        */
/* -------------------------------------------------------------------- */

static void
j2k_error(const char *msg, void *client_data)
{
    JPEG2KSTATE *state = (JPEG2KSTATE *) client_data;
    free((void *)state->error_msg);
    state->error_msg = strdup(msg);
}

/* -------------------------------------------------------------------- */
/* Buffer input stream                                                  */
/* -------------------------------------------------------------------- */

static OPJ_SIZE_T
j2k_read(void *p_buffer, OPJ_SIZE_T p_nb_bytes, void *p_user_data)
{
    ImagingIncrementalDecoder decoder = (ImagingIncrementalDecoder)p_user_data;

    return ImagingIncrementalDecoderRead(decoder, p_buffer, p_nb_bytes);
}

static OPJ_SIZE_T
j2k_write(void *p_buffer, OPJ_SIZE_T p_nb_bytes, void *p_user_data)
{
    return OPJ_FALSE;
}

static OPJ_OFF_T
j2k_skip(OPJ_OFF_T p_nb_bytes, void *p_user_data)
{
    ImagingIncrementalDecoder decoder = (ImagingIncrementalDecoder)p_user_data;

    return ImagingIncrementalDecoderSkip(decoder, p_nb_bytes);
}

static OPJ_BOOL
j2k_seek(OPJ_OFF_T p_nb_bytes, void *p_user_data)
{
    // We *deliberately* don't implement this
    return OPJ_FALSE;
}

/* -------------------------------------------------------------------- */
/* Unpackers                                                            */
/* -------------------------------------------------------------------- */

typedef void (*j2k_unpacker_t)(opj_image_t *in, Imaging im);

struct j2k_decode_unpacker {
    const char          *mode;
    OPJ_COLOR_SPACE     color_space;
    unsigned            components;
    j2k_unpacker_t      unpacker;
};

static inline
unsigned j2ku_shift(unsigned x, int n)
{
    if (n < 0)
        return x >> -n;
    else
        return x << n;
}

static void
j2ku_gray_l(opj_image_t *in, Imaging im)
{
    unsigned x0 = in->comps[0].x0, y0 = in->comps[0].y0;
    unsigned w = in->comps[0].w, h = in->comps[0].h;
    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    unsigned x, y;

    if (shift < 0)
        offset += 1 << (-shift - 1);

    for (y = 0; y < h; ++y) {
        OPJ_INT32 *data = &in->comps[0].data[y * w];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
        for (x = 0; x < w; ++x)
            *row++ = j2ku_shift(offset + *data++, shift);
    }
}

static void
j2ku_gray_rgb(opj_image_t *in, Imaging im)
{
    unsigned x0 = in->comps[0].x0, y0 = in->comps[0].y0;
    unsigned w = in->comps[0].w, h = in->comps[0].h;
    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    unsigned x, y;

    if (shift < 0)
        offset += 1 << (-shift - 1);

    for (y = 0; y < h; ++y) {
        OPJ_INT32 *data = &in->comps[0].data[y * w];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0;
        for (x = 0; x < w; ++x) {
            UINT8 byte = j2ku_shift(offset + *data++, shift);
            row[0] = row[1] = row[2] = byte;
            row[3] = 0xff;
            row += 4;
        }
    }
}

static void
j2ku_graya_la(opj_image_t *in, Imaging im)
{
    unsigned x0 = in->comps[0].x0, y0 = in->comps[0].y0;
    unsigned w = in->comps[0].w, h = in->comps[0].h;
    int shift = 8 - in->comps[0].prec;
    int offset = in->comps[0].sgnd ? 1 << (in->comps[0].prec - 1) : 0;
    int ashift = 8 - in->comps[1].prec;
    int aoffset = in->comps[1].sgnd ? 1 << (in->comps[1].prec - 1) : 0;
    unsigned x, y;

    if (shift < 0)
        offset += 1 << (-shift - 1);
    if (ashift < 0)
        aoffset += 1 << (-ashift - 1);

    for (y = 0; y < h; ++y) {
        OPJ_INT32 *data = &in->comps[0].data[y * w];
        OPJ_INT32 *adata = &in->comps[1].data[y * w];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (x = 0; x < w; ++x) {
            UINT8 byte = j2ku_shift(offset + *data++, shift);
            row[0] = row[1] = row[2] = byte;
            row[3] = (unsigned)(offset + *adata++) >> shift;
            row += 4;
        }
    }
}

static void
j2ku_srgb_rgb(opj_image_t *in, Imaging im)
{
    unsigned x0 = in->comps[0].x0, y0 = in->comps[0].y0;
    unsigned w = in->comps[0].w, h = in->comps[0].h;
    int shifts[3], offsets[3];
    unsigned n, x, y;

    for (n = 0; n < 3; ++n) {
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        if (shifts[n] < 0)
            offsets[n] += 1 << (-shifts[n] - 1);
    }

    for (y = 0; y < h; ++y) {
        OPJ_INT32 *data[3];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (n = 0; n < 3; ++n)
            data[n] = &in->comps[n].data[y * w];
        
        for (x = 0; x < w; ++x) {
            for (n = 0; n < 3; ++n)
                row[n] = j2ku_shift(offsets[n] + *data[n]++, shifts[n]);
            row[3] = 0xff;
            row += 4;
        }
    }
}

static void
j2ku_sycc_rgb(opj_image_t *in, Imaging im)
{
    unsigned x0 = in->comps[0].x0, y0 = in->comps[0].y0;
    unsigned w = in->comps[0].w, h = in->comps[0].h;
    int shifts[3], offsets[3];
    unsigned n, x, y;

    for (n = 0; n < 3; ++n) {
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        if (shifts[n] < 0)
            offsets[n] += 1 << (-shifts[n] - 1);
    }

    for (y = 0; y < h; ++y) {
        OPJ_INT32 *data[3];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        UINT8 *row_start = row;
        for (n = 0; n < 3; ++n)
            data[n] = &in->comps[n].data[y * w];
        
        for (x = 0; x < w; ++x) {
            for (n = 0; n < 3; ++n)
                row[n] = j2ku_shift(offsets[n] + *data[n]++, shifts[n]);
            row[3] = 0xff;
            row += 4;
        }
        ImagingConvertYCbCr2RGB(row_start, row_start, w);
    }
}

static void
j2ku_srgba_rgba(opj_image_t *in, Imaging im)
{
    unsigned x0 = in->comps[0].x0, y0 = in->comps[0].y0;
    unsigned w = in->comps[0].w, h = in->comps[0].h;
    int shifts[4], offsets[4];
    unsigned n, x, y;

    for (n = 0; n < 4; ++n) {
        shifts[n] = 8 - in->comps[n].prec;
        offsets[n] = in->comps[n].sgnd ? 1 << (in->comps[n].prec - 1) : 0;
        if (shifts[n] < 0)
            offsets[n] += 1 << (-shifts[n] - 1);
    }

    for (y = 0; y < h; ++y) {
        OPJ_INT32 *data[4];
        UINT8 *row = (UINT8 *)im->image[y0 + y] + x0 * 4;
        for (n = 0; n < 4; ++n)
            data[n] = &in->comps[n].data[y * w];
        
        for (x = 0; x < w; ++x) {
            for (n = 0; n < 4; ++n)
                row[n] = j2ku_shift(offsets[n] + *data[n]++, shifts[n]);
            row += 4;
        }
    }
}

static const struct j2k_decode_unpacker j2k_unpackers[] = {
    { "L", OPJ_CLRSPC_GRAY, 1, j2ku_gray_l },
    { "LA", OPJ_CLRSPC_GRAY, 2, j2ku_graya_la },
    { "RGB", OPJ_CLRSPC_GRAY, 1, j2ku_gray_rgb },
    { "RGB", OPJ_CLRSPC_GRAY, 2, j2ku_gray_rgb },
    { "RGB", OPJ_CLRSPC_SRGB, 3, j2ku_srgb_rgb },
    { "RGB", OPJ_CLRSPC_SYCC, 3, j2ku_sycc_rgb },
    { "RGBA", OPJ_CLRSPC_GRAY, 1, j2ku_gray_rgb },
    { "RGBA", OPJ_CLRSPC_GRAY, 2, j2ku_graya_la },
    { "RGBA", OPJ_CLRSPC_SRGB, 3, j2ku_srgb_rgb },
    { "RGBA", OPJ_CLRSPC_SYCC, 3, j2ku_sycc_rgb },
    { "RGBA", OPJ_CLRSPC_SRGB, 4, j2ku_srgba_rgba },
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
j2k_decode_entry(Imaging im, ImagingCodecState state,
                 ImagingIncrementalDecoder decoder)
{
    JPEG2KSTATE *context = (JPEG2KSTATE *) state->context;
    opj_stream_t *stream;
    opj_image_t *image;
    opj_codec_t *codec;
    opj_dparameters_t params;
    OPJ_COLOR_SPACE color_space;
    j2k_unpacker_t unpack;
    unsigned n;

    stream = opj_stream_default_create(OPJ_TRUE);

    if (!stream) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    opj_stream_set_read_function(stream, j2k_read);
    opj_stream_set_write_function(stream, j2k_write);
    opj_stream_set_skip_function(stream, j2k_skip);
    opj_stream_set_seek_function(stream, j2k_seek);

    opj_stream_set_user_data(stream, context->decoder);


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
    if (image->numcomps < 1 || image->numcomps > 4
        || image->color_space == OPJ_CLRSPC_UNKNOWN) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }
    
    for (n = 1; n < image->numcomps; ++n) {
        /* Check that the sample frequency is uniform */
        if (image->comps[0].dx != image->comps[n].dx
            || image->comps[0].dy != image->comps[n].dy) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
        }
        
        /* Check that the bit depth is uniform */
        if (image->comps[0].prec != image->comps[n].prec) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            goto quick_exit;
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
       
           Number of components   Colorspace
         -----------------------------------------
           1                      gray
           2                      gray (+ alpha)
           3                      sRGB
           4                      sRGB (+ alpha)
       
    */
    
    /* Find the correct unpacker */
    color_space = image->color_space;
    
    if (color_space == OPJ_CLRSPC_UNSPECIFIED) {
        switch (image->numcomps) {
        case 1: case 2: color_space = OPJ_CLRSPC_GRAY; break;
        case 3: case 4: color_space = OPJ_CLRSPC_SRGB; break;
        }
    }

    for (n = 0; n < sizeof(j2k_unpackers) / sizeof (j2k_unpackers[0]); ++n) {
        if (color_space == j2k_unpackers[n].color_space
            && image->numcomps == j2k_unpackers[n].components
            && strcmp (context->mode, j2k_unpackers[n].mode) == 0) {
            unpack = j2k_unpackers[n].unpacker;
            break;
        }
    }

    if (!unpack) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit; 
    }

    /* Decode and unpack the image */
    if (!opj_decode(codec, stream, image)
        || !opj_end_decompress(codec, stream)) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    unpack(image, im);

 quick_exit:
    if (codec)
        opj_destroy_codec(codec);
    if (image)
        opj_image_destroy(image);
    if (stream)
        opj_stream_destroy(stream);

    return -1;
}

int
ImagingJpeg2KDecode(Imaging im, ImagingCodecState state, UINT8* buf, int bytes)
{
    JPEG2KSTATE *context = (JPEG2KSTATE *) state->context;

    if (state->state == J2K_STATE_DONE || state->state == J2K_STATE_FAILED)
        return -1;

    if (state->state == J2K_STATE_START) {
        context->decoder = ImagingIncrementalDecoderCreate(j2k_decode_entry,
                                                           im, state);

        if (!context->decoder) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            return -1;
        }

        state->state = J2K_STATE_DECODING;
    }

    return ImagingIncrementalDecodeData(context->decoder, buf, bytes);
}

/* -------------------------------------------------------------------- */
/* Cleanup                                                              */
/* -------------------------------------------------------------------- */

int
ImagingJpeg2KDecodeCleanup(ImagingCodecState state) {
    JPEG2KSTATE *context = (JPEG2KSTATE *)state->context;

    if (context->decoder)
        ImagingIncrementalDecoderDestroy(context->decoder);

    return -1;
}

const char *
ImagingJpeg2KVersion(void)
{
    return opj_version();
}

#endif /* HAVE_OPENJPEG */

/*
 * Local Variables:
 * c-basic-offset: 4
 * End:
 *
 */
