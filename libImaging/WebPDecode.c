/*
 * The Python Imaging Library.
 *
 * decoder for WebP image data.
 */


#ifdef  HAVE_LIBWEBP

#include "Imaging.h"
#include "WebP.h"

#include <assert.h>

static int _vp8_status_to_codec_status(VP8StatusCode code)
{
    switch (code)
    {
    case VP8_STATUS_OK:
        return 0;
    case VP8_STATUS_OUT_OF_MEMORY:
        return IMAGING_CODEC_MEMORY;
    case VP8_STATUS_BITSTREAM_ERROR:
    case VP8_STATUS_NOT_ENOUGH_DATA:
    case VP8_STATUS_SUSPENDED:
        return IMAGING_CODEC_BROKEN;
    case VP8_STATUS_INVALID_PARAM:
    case VP8_STATUS_UNSUPPORTED_FEATURE:
        return IMAGING_CODEC_CONFIG;
    default:
    case VP8_STATUS_USER_ABORT:
        return IMAGING_CODEC_UNKNOWN;
    }
}

/* -------------------------------------------------------------------- */
/* Decoder                                                              */
/* -------------------------------------------------------------------- */

int ImagingWebPDecode(Imaging im, ImagingCodecState state, UINT8 *buf, int bytes)
{
    WEBPSTATE         *context = (WEBPSTATE *)state->context;
    WebPDecoderConfig *config = &context->config;
    VP8StatusCode      vp8_status_code;

    if (!state->state)
    {
        if (!WebPInitDecoderConfig(config))
        {
            /* Mismatched version. */
            state->errcode = IMAGING_CODEC_CONFIG;
            return -1;
        }

        if (0 == strcmp("RGBA", context->rawmode))
            config->output.colorspace = MODE_RGBA;
        else
            config->output.colorspace = MODE_RGB;

        /* If block storage is used, and we're not stripping alpha, then directly decode to it. */
        if (NULL != im->block && (MODE_RGBA == config->output.colorspace || !context->has_alpha))
        {
            assert(4 == im->pixelsize);

            /* Force RGBA so RGB is correctly unpacked. */
            config->output.colorspace = MODE_RGBA;
            config->output.is_external_memory = 1;
            config->output.u.RGBA.stride = im->linesize;
            config->output.u.RGBA.size = config->output.u.RGBA.stride * state->ysize;
            config->output.u.RGBA.rgba = (uint8_t *)im->block + state->xoff * 4 + state->yoff * im->linesize;
        }
        else
        {
            context->output = &config->output;
        }

        if (state->xsize != context->width || state->ysize != context->height)
        {
            config->options.scaled_width = state->xsize;
            config->options.scaled_height = state->ysize;
            config->options.use_scaling = 1;
        }

        context->decoder = WebPIDecode(NULL, 0, config);
        if (NULL == context->decoder)
        {
            state->errcode = _vp8_status_to_codec_status(vp8_status_code);
            return -1;
        }

        state->state = 1;
    }

    /* Consume the buffer, decoding as much as possible. */
    vp8_status_code = WebPIAppend(context->decoder, buf, bytes);
    if (VP8_STATUS_NOT_ENOUGH_DATA != vp8_status_code &&
        VP8_STATUS_SUSPENDED != vp8_status_code &&
        VP8_STATUS_OK != vp8_status_code)
    {
        state->errcode = _vp8_status_to_codec_status(vp8_status_code);
        return -1;
    }

    if (VP8_STATUS_NOT_ENOUGH_DATA != vp8_status_code)
    {
        /* Check progress, and unpack available data. */

        const uint8_t *rgba;
        int            last_y;
        int            width;
        int            height;
        int            stride;

        rgba = WebPIDecGetRGB(context->decoder, &last_y, &width, &height, &stride);
        if (NULL != rgba)
        {
            assert(width == state->xsize);
            assert(height == state->ysize);
            assert(last_y <= state->ysize);

            if (config->output.is_external_memory)
            {
                state->y = last_y;
            }
            else for (; state->y < last_y; ++state->y)
            {
                assert(state->y < state->ysize);
                state->shuffle((UINT8 *)im->image[state->y + state->yoff] +
                               state->xoff * im->pixelsize,
                               rgba + state->y * stride, state->xsize);
            }
        }
    }

    if (VP8_STATUS_OK == vp8_status_code)
    {
        /* We're finished! */
        state->errcode = IMAGING_CODEC_END;
        return -1;
    }

    /* Return number of bytes consumed. */
    return bytes;
}

/* -------------------------------------------------------------------- */
/* Cleanup                                                              */
/* -------------------------------------------------------------------- */

int ImagingWebPDecodeCleanup(ImagingCodecState state)
{
    WEBPSTATE* context = (WEBPSTATE*) state->context;

    if (NULL != context->output)
    {
        WebPFreeDecBuffer(context->output);
        context->output = NULL;
    }

    if (NULL != context->decoder)
    {
        WebPIDelete(context->decoder);
        context->decoder = NULL;
    }

    return -1;
}

#endif

