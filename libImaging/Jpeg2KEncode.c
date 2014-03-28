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

#include "Jpeg2K.h"

#define CINEMA_24_CS_LENGTH   1302083
#define CINEMA_48_CS_LENGTH    651041
#define COMP_24_CS_MAX_LENGTH 1041666
#define COMP_48_CS_MAX_LENGTH  520833

/* -------------------------------------------------------------------- */
/* Error handler                                                        */
/* -------------------------------------------------------------------- */

static void
j2k_error(const char *msg, void *client_data)
{
    JPEG2KENCODESTATE *state = (JPEG2KENCODESTATE *) client_data;
    free((void *)state->error_msg);
    state->error_msg = strdup(msg);
}

/* -------------------------------------------------------------------- */
/* Buffer output stream                                                 */
/* -------------------------------------------------------------------- */

static OPJ_SIZE_T
j2k_write(void *p_buffer, OPJ_SIZE_T p_nb_bytes, void *p_user_data)
{
    ImagingIncrementalCodec encoder = (ImagingIncrementalCodec)p_user_data;
    size_t len = ImagingIncrementalCodecWrite(encoder, p_buffer, p_nb_bytes);

    return len ? len : (OPJ_SIZE_T)-1;
}

static OPJ_OFF_T
j2k_skip(OPJ_OFF_T p_nb_bytes, void *p_user_data)
{
    ImagingIncrementalCodec encoder = (ImagingIncrementalCodec)p_user_data;
    off_t pos = ImagingIncrementalCodecSkip(encoder, p_nb_bytes);

    return pos ? pos : (OPJ_OFF_T)-1;
}

static OPJ_BOOL
j2k_seek(OPJ_OFF_T p_nb_bytes, void *p_user_data)
{
    ImagingIncrementalCodec encoder = (ImagingIncrementalCodec)p_user_data;
    off_t pos = ImagingIncrementalCodecSeek(encoder, p_nb_bytes);

    return pos == p_nb_bytes;
}

/* -------------------------------------------------------------------- */
/* Encoder                                                              */
/* -------------------------------------------------------------------- */

typedef void (*j2k_pack_tile_t)(Imaging im, UINT8 *buf,
                                unsigned x0, unsigned y0,
                                unsigned w, unsigned h);

static void
j2k_pack_l(Imaging im, UINT8 *buf,
           unsigned x0, unsigned y0, unsigned w, unsigned h)
{
    UINT8 *ptr = buf;
    unsigned x,y;
    for (y = 0; y < h; ++y) {
        UINT8 *data = (UINT8 *)(im->image[y + y0] + x0);
        for (x = 0; x < w; ++x)
            *ptr++ = *data++;
    }
}

static void
j2k_pack_la(Imaging im, UINT8 *buf,
            unsigned x0, unsigned y0, unsigned w, unsigned h)
{
    UINT8 *ptr = buf;
    UINT8 *ptra = buf + w * h;
    unsigned x,y;
    for (y = 0; y < h; ++y) {
        UINT8 *data = (UINT8 *)(im->image[y + y0] + 4 * x0);
        for (x = 0; x < w; ++x) {
            *ptr++ = data[0];
            *ptra++ = data[3];
            data += 4;
        }
    }
}

static void
j2k_pack_rgb(Imaging im, UINT8 *buf,
             unsigned x0, unsigned y0, unsigned w, unsigned h)
{
    UINT8 *pr = buf;
    UINT8 *pg = pr + w * h;
    UINT8 *pb = pg + w * h;
    unsigned x,y;
    for (y = 0; y < h; ++y) {
        UINT8 *data = (UINT8 *)(im->image[y + y0] + 4 * x0);
        for (x = 0; x < w; ++x) {
            *pr++ = data[0];
            *pg++ = data[1];
            *pb++ = data[2];
            data += 4;
        }
    }
}

static void
j2k_pack_rgba(Imaging im, UINT8 *buf,
              unsigned x0, unsigned y0, unsigned w, unsigned h)
{
    UINT8 *pr = buf;
    UINT8 *pg = pr + w * h;
    UINT8 *pb = pg + w * h;
    UINT8 *pa = pb + w * h;
    unsigned x,y;
    for (y = 0; y < h; ++y) {
        UINT8 *data = (UINT8 *)(im->image[y + y0] + 4 * x0);
        for (x = 0; x < w; ++x) {
            *pr++ = *data++;
            *pg++ = *data++;
            *pb++ = *data++;
            *pa++ = *data++;
        }
    }
}

enum {
    J2K_STATE_START = 0,
    J2K_STATE_ENCODING = 1,
    J2K_STATE_DONE = 2,
    J2K_STATE_FAILED = 3,
};

static void
j2k_set_cinema_params(Imaging im, int components, opj_cparameters_t *params)
{
    float rate;
    unsigned n;

    /* These settings have been copied from opj_compress in the OpenJPEG
       sources. */

    params->tile_size_on = OPJ_FALSE;
    params->cp_tdx = params->cp_tdy = 1;
    params->tp_flag = 'C';
    params->tp_on = 1;
    params->cp_tx0 = params->cp_ty0 = 0;
    params->image_offset_x0 = params->image_offset_y0 = 0;
    params->cblockw_init = 32;
    params->cblockh_init = 32;
    params->csty |= 0x01;
    params->prog_order = OPJ_CPRL;
    params->roi_compno = -1;
    params->subsampling_dx = params->subsampling_dy = 1;
    params->irreversible = 1;

    if (params->cp_cinema == OPJ_CINEMA4K_24) {
        float max_rate = ((float)(components * im->xsize * im->ysize * 8)
                          / (CINEMA_24_CS_LENGTH * 8));

        params->POC[0].tile = 1;
        params->POC[0].resno0 = 0;
        params->POC[0].compno0 = 0;
        params->POC[0].layno1 = 1;
        params->POC[0].resno1 = params->numresolution - 1;
        params->POC[0].compno1 = 3;
        params->POC[0].prg1 = OPJ_CPRL;
        params->POC[1].tile = 1;
        params->POC[1].resno0 = 0;
        params->POC[1].compno0 = 0;
        params->POC[1].layno1 = 1;
        params->POC[1].resno1 = params->numresolution - 1;
        params->POC[1].compno1 = 3;
        params->POC[1].prg1 = OPJ_CPRL;
        params->numpocs = 2;

        for (n = 0; n < params->tcp_numlayers; ++n) {
            rate = 0;
            if (params->tcp_rates[0] == 0) {
                params->tcp_rates[n] = max_rate;
            } else {
                rate = ((float)(components * im->xsize * im->ysize * 8)
                        / (params->tcp_rates[n] * 8));
                if (rate > CINEMA_24_CS_LENGTH)
                    params->tcp_rates[n] = max_rate;
            }
        }

        params->max_comp_size = COMP_24_CS_MAX_LENGTH;
    } else {
        float max_rate = ((float)(components * im->xsize * im->ysize * 8)
                          / (CINEMA_48_CS_LENGTH * 8));

        for (n = 0; n < params->tcp_numlayers; ++n) {
            rate = 0;
            if (params->tcp_rates[0] == 0) {
                params->tcp_rates[n] = max_rate;
            } else {
                rate = ((float)(components * im->xsize * im->ysize * 8)
                        / (params->tcp_rates[n] * 8));
                if (rate > CINEMA_48_CS_LENGTH)
                    params->tcp_rates[n] = max_rate;
            }
        }

        params->max_comp_size = COMP_48_CS_MAX_LENGTH;
    }
}

static int
j2k_encode_entry(Imaging im, ImagingCodecState state,
                 ImagingIncrementalCodec encoder)
{
    JPEG2KENCODESTATE *context = (JPEG2KENCODESTATE *)state->context;
    opj_stream_t *stream = NULL;
    opj_image_t *image = NULL;
    opj_codec_t *codec = NULL;
    opj_cparameters_t params;
    unsigned components;
    OPJ_COLOR_SPACE color_space;
    opj_image_cmptparm_t image_params[4];
    unsigned xsiz, ysiz;
    unsigned tile_width, tile_height;
    unsigned tiles_x, tiles_y, num_tiles;
    unsigned x, y, tile_ndx;
    unsigned n;
    j2k_pack_tile_t pack;
    int ret = -1;

    stream = opj_stream_default_create(OPJ_FALSE);

    if (!stream) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    opj_stream_set_write_function(stream, j2k_write);
    opj_stream_set_skip_function(stream, j2k_skip);
    opj_stream_set_seek_function(stream, j2k_seek);

    opj_stream_set_user_data(stream, encoder);

    /* Setup an opj_image */
    if (strcmp (im->mode, "L") == 0) {
        components = 1;
        color_space = OPJ_CLRSPC_GRAY;
        pack = j2k_pack_l;
    } else if (strcmp (im->mode, "LA") == 0) {
        components = 2; 
        color_space = OPJ_CLRSPC_GRAY;
        pack = j2k_pack_la;
    } else if (strcmp (im->mode, "RGB") == 0) {
        components = 3;
        color_space = OPJ_CLRSPC_SRGB;
        pack = j2k_pack_rgb;
    } else if (strcmp (im->mode, "YCbCr") == 0) {
        components = 3;
        color_space = OPJ_CLRSPC_SYCC;
        pack = j2k_pack_rgb;
    } else if (strcmp (im->mode, "RGBA") == 0) {
        components = 4;
        color_space = OPJ_CLRSPC_SRGB;
        pack = j2k_pack_rgba;
    } else {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    for (n = 0; n < components; ++n) {
        image_params[n].dx = image_params[n].dy = 1;
        image_params[n].w = im->xsize;
        image_params[n].h = im->ysize;
        image_params[n].x0 = image_params[n].y0 = 0;
        image_params[n].prec = 8;
        image_params[n].bpp = 8;
        image_params[n].sgnd = 0;
    }

    image = opj_image_create(components, image_params, color_space);

    /* Setup compression context */
    context->error_msg = NULL;

    opj_set_default_encoder_parameters(&params);
    
    params.image_offset_x0 = context->offset_x;
    params.image_offset_y0 = context->offset_y;

    if (context->tile_size_x && context->tile_size_y) {
        params.tile_size_on = OPJ_TRUE;
        params.cp_tx0 = context->tile_offset_x;
        params.cp_ty0 = context->tile_offset_y;
        params.cp_tdx = context->tile_size_x;
        params.cp_tdy = context->tile_size_y;

        tile_width = params.cp_tdx;
        tile_height = params.cp_tdy;
    } else {
        params.cp_tx0 = 0;
        params.cp_ty0 = 0;
        params.cp_tdx = 1;
        params.cp_tdy = 1;

        tile_width = im->xsize;
        tile_height = im->ysize;
    }

    if (context->quality_layers && PySequence_Check(context->quality_layers)) {
        Py_ssize_t len = PySequence_Length(context->quality_layers);
        Py_ssize_t n;
        float *pq;

        if (len) {
            if (len > sizeof(params.tcp_rates) / sizeof(params.tcp_rates[0]))
                len = sizeof(params.tcp_rates)/sizeof(params.tcp_rates[0]);

            params.tcp_numlayers = (int)len;

            if (context->quality_is_in_db) {
                params.cp_disto_alloc = params.cp_fixed_alloc = 0;
                params.cp_fixed_quality = 1;
                pq = params.tcp_distoratio;
            } else {
                params.cp_disto_alloc = 1;
                params.cp_fixed_alloc = params.cp_fixed_quality = 0;
                pq = params.tcp_rates;
            }

            for (n = 0; n < len; ++n) {
                PyObject *obj = PySequence_ITEM(context->quality_layers, n);
                pq[n] = PyFloat_AsDouble(obj);
            }
        }
    } else {
        params.tcp_numlayers = 1;
        params.tcp_rates[0] = 0;
        params.cp_disto_alloc = 1;
    }

    if (context->num_resolutions)
        params.numresolution = context->num_resolutions;

    if (context->cblk_width >= 4 && context->cblk_width <= 1024
        && context->cblk_height >= 4 && context->cblk_height <= 1024
        && context->cblk_width * context->cblk_height <= 4096) {
        params.cblockw_init = context->cblk_width;
        params.cblockh_init = context->cblk_height;
    }

    if (context->precinct_width >= 4 && context->precinct_height >= 4
        && context->precinct_width >= context->cblk_width
        && context->precinct_height > context->cblk_height) {
        params.prcw_init[0] = context->precinct_width;
        params.prch_init[0] = context->precinct_height;
        params.res_spec = 1;
        params.csty |= 0x01;
    }

    params.irreversible = context->irreversible;

    params.prog_order = context->progression;

    params.cp_cinema = context->cinema_mode;

    switch (params.cp_cinema) {
    case OPJ_OFF:
        params.cp_rsiz = OPJ_STD_RSIZ;
        break;
    case OPJ_CINEMA2K_24:
    case OPJ_CINEMA2K_48:
        params.cp_rsiz = OPJ_CINEMA2K;
        if (params.numresolution > 6)
            params.numresolution = 6;
        break;
    case OPJ_CINEMA4K_24:
        params.cp_rsiz = OPJ_CINEMA4K;
        if (params.numresolution > 7)
            params.numresolution = 7;
        break;
    }

    if (context->cinema_mode != OPJ_OFF)
        j2k_set_cinema_params(im, components, &params);

    /* Set up the reference grid in the image */
    image->x0 = params.image_offset_x0;
    image->y0 = params.image_offset_y0;
    image->x1 = xsiz = im->xsize + params.image_offset_x0;
    image->y1 = ysiz = im->ysize + params.image_offset_y0;

    /* Create the compressor */
    codec = opj_create_compress(context->format);

    if (!codec) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    opj_set_error_handler(codec, j2k_error, context);
    opj_setup_encoder(codec, &params, image);

    /* Start encoding */
    if (!opj_start_compress(codec, image, stream)) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    /* Write each tile */
    tiles_x = (im->xsize + (params.image_offset_x0 - params.cp_tx0)
               + tile_width - 1) / tile_width;
    tiles_y = (im->ysize + (params.image_offset_y0 - params.cp_ty0)
               + tile_height - 1) / tile_height;

    num_tiles = tiles_x * tiles_y;

    state->buffer = malloc (tile_width * tile_height * components);

    tile_ndx = 0;
    for (y = 0; y < tiles_y; ++y) {
        unsigned ty0 = params.cp_ty0 + y * tile_height;
        unsigned ty1 = ty0 + tile_height;
        unsigned pixy, pixh;

        if (ty0 < params.image_offset_y0)
            ty0 = params.image_offset_y0;
        if (ty1 > ysiz)
            ty1 = ysiz;

        pixy = ty0 - params.image_offset_y0;
        pixh = ty1 - ty0;

        for (x = 0; x < tiles_x; ++x) {
            unsigned tx0 = params.cp_tx0 + x * tile_width;
            unsigned tx1 = tx0 + tile_width;
            unsigned pixx, pixw;
            unsigned data_size;

            if (tx0 < params.image_offset_x0)
                tx0 = params.image_offset_x0;
            if (tx1 > xsiz)
                tx1 = xsiz;

            pixx = tx0 - params.image_offset_x0;
            pixw = tx1 - tx0;

            pack(im, state->buffer, pixx, pixy, pixw, pixh);

            data_size = pixw * pixh * components;

            if (!opj_write_tile(codec, tile_ndx++, state->buffer,
                                data_size, stream)) {
                state->errcode = IMAGING_CODEC_BROKEN;
                state->state = J2K_STATE_FAILED;
                goto quick_exit;
            }
        }
    }

    if (!opj_end_compress(codec, stream)) {
        state->errcode = IMAGING_CODEC_BROKEN;
        state->state = J2K_STATE_FAILED;
        goto quick_exit;
    }

    state->errcode = IMAGING_CODEC_END;
    state->state = J2K_STATE_DONE;
    ret = (int)ImagingIncrementalCodecBytesInBuffer(encoder);

 quick_exit:
    if (codec)
        opj_destroy_codec(codec);
    if (image)
        opj_image_destroy(image);
    if (stream)
        opj_stream_destroy(stream);

    return ret;
}

int
ImagingJpeg2KEncode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes)
{
    JPEG2KENCODESTATE *context = (JPEG2KENCODESTATE *)state->context;

    if (state->state == J2K_STATE_FAILED)
        return -1;

    if (state->state == J2K_STATE_START) {
        int seekable = (context->format != OPJ_CODEC_J2K 
                        ? INCREMENTAL_CODEC_SEEKABLE 
                        : INCREMENTAL_CODEC_NOT_SEEKABLE);

        context->encoder = ImagingIncrementalCodecCreate(j2k_encode_entry,
                                                         im, state,
                                                         INCREMENTAL_CODEC_WRITE,
                                                         seekable,
                                                         context->fd);

        if (!context->encoder) {
            state->errcode = IMAGING_CODEC_BROKEN;
            state->state = J2K_STATE_FAILED;
            return -1;
        }

        state->state = J2K_STATE_ENCODING;
    }

    return ImagingIncrementalCodecPushBuffer(context->encoder, buf, bytes);
}

/* -------------------------------------------------------------------- */
/* Cleanup                                                              */
/* -------------------------------------------------------------------- */

int
ImagingJpeg2KEncodeCleanup(ImagingCodecState state) {
    JPEG2KENCODESTATE *context = (JPEG2KENCODESTATE *)state->context;

    if (context->quality_layers)
        Py_DECREF(context->quality_layers);

    if (context->error_msg)
        free ((void *)context->error_msg);

    if (context->encoder)
        ImagingIncrementalCodecDestroy(context->encoder);

    return -1;
}

#endif /* HAVE_OPENJPEG */

/*
 * Local Variables:
 * c-basic-offset: 4
 * End:
 *
 */
