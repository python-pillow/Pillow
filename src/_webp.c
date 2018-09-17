#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "Imaging.h"
#include "py3.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>

#ifdef HAVE_WEBPMUX
#include <webp/mux.h>
#include <webp/demux.h>

/*
 * Check the versions from mux.h and demux.h, to ensure the WebPAnimEncoder and
 * WebPAnimDecoder APIs are present (initial support was added in 0.5.0). The
 * very early versions had some significant differences, so we require later
 * versions, before enabling animation support.
 */
#if WEBP_MUX_ABI_VERSION >= 0x0104 && WEBP_DEMUX_ABI_VERSION >= 0x0105
#define HAVE_WEBPANIM
#endif

#endif

/* -------------------------------------------------------------------- */
/* WebP Muxer Error Handling                                            */
/* -------------------------------------------------------------------- */

#ifdef HAVE_WEBPMUX

static const char* const kErrorMessages[-WEBP_MUX_NOT_ENOUGH_DATA + 1] = {
    "WEBP_MUX_NOT_FOUND", "WEBP_MUX_INVALID_ARGUMENT", "WEBP_MUX_BAD_DATA",
    "WEBP_MUX_MEMORY_ERROR", "WEBP_MUX_NOT_ENOUGH_DATA"
};

PyObject* HandleMuxError(WebPMuxError err, char* chunk) {
    char message[100];
    int message_len;
    assert(err <= WEBP_MUX_NOT_FOUND && err >= WEBP_MUX_NOT_ENOUGH_DATA);

    // Check for a memory error first
    if (err == WEBP_MUX_MEMORY_ERROR) {
        return PyErr_NoMemory();
    }

    // Create the error message
    if (chunk == NULL) {
        message_len = sprintf(message, "could not assemble chunks: %s", kErrorMessages[-err]);
    } else {
        message_len = sprintf(message, "could not set %.4s chunk: %s", chunk, kErrorMessages[-err]);
    }
    if (message_len < 0) {
        PyErr_SetString(PyExc_RuntimeError, "failed to construct error message");
        return NULL;
    }

    // Set the proper error type
    switch (err) {
        case WEBP_MUX_NOT_FOUND:
        case WEBP_MUX_INVALID_ARGUMENT:
            PyErr_SetString(PyExc_ValueError, message);
            break;

        case WEBP_MUX_BAD_DATA:
        case WEBP_MUX_NOT_ENOUGH_DATA:
            PyErr_SetString(PyExc_IOError, message);
            break;

        default:
            PyErr_SetString(PyExc_RuntimeError, message);
            break;
    }
    return NULL;
}

#endif

/* -------------------------------------------------------------------- */
/* WebP Animation Support                                               */
/* -------------------------------------------------------------------- */

#ifdef HAVE_WEBPANIM

// Encoder type
typedef struct {
    PyObject_HEAD
    WebPAnimEncoder* enc;
    WebPPicture frame;
} WebPAnimEncoderObject;

static PyTypeObject WebPAnimEncoder_Type;

// Decoder type
typedef struct {
    PyObject_HEAD
    WebPAnimDecoder* dec;
    WebPAnimInfo info;
    WebPData data;
    char* mode;
} WebPAnimDecoderObject;

static PyTypeObject WebPAnimDecoder_Type;

// Encoder functions
PyObject* _anim_encoder_new(PyObject* self, PyObject* args)
{
    int width, height;
    uint32_t bgcolor;
    int loop_count;
    int minimize_size;
    int kmin, kmax;
    int allow_mixed;
    int verbose;
    WebPAnimEncoderOptions enc_options;
    WebPAnimEncoderObject* encp = NULL;
    WebPAnimEncoder* enc = NULL;

    if (!PyArg_ParseTuple(args, "iiIiiiiii",
        &width, &height, &bgcolor, &loop_count, &minimize_size,
        &kmin, &kmax, &allow_mixed, &verbose)) {
        return NULL;
    }

    // Setup and configure the encoder's options (these are animation-specific)
    if (!WebPAnimEncoderOptionsInit(&enc_options)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to initialize encoder options");
        return NULL;
    }
    enc_options.anim_params.bgcolor = bgcolor;
    enc_options.anim_params.loop_count = loop_count;
    enc_options.minimize_size = minimize_size;
    enc_options.kmin = kmin;
    enc_options.kmax = kmax;
    enc_options.allow_mixed = allow_mixed;
    enc_options.verbose = verbose;

    // Validate canvas dimensions
    if (width <= 0 || height <= 0) {
        PyErr_SetString(PyExc_ValueError, "invalid canvas dimensions");
        return NULL;
    }

    // Create a new animation encoder and picture frame
    encp = PyObject_New(WebPAnimEncoderObject, &WebPAnimEncoder_Type);
    if (encp) {
        if (WebPPictureInit(&(encp->frame))) {
            enc = WebPAnimEncoderNew(width, height, &enc_options);
            if (enc) {
                encp->enc = enc;
                return (PyObject*) encp;
            }
            WebPPictureFree(&(encp->frame));
        }
        PyObject_Del(encp);
    }
    PyErr_SetString(PyExc_RuntimeError, "could not create encoder object");
    return NULL;
}

PyObject* _anim_encoder_dealloc(PyObject* self)
{
    WebPAnimEncoderObject* encp = (WebPAnimEncoderObject*)self;
    WebPPictureFree(&(encp->frame));
    WebPAnimEncoderDelete(encp->enc);
    Py_RETURN_NONE;
}

PyObject* _anim_encoder_add(PyObject* self, PyObject* args)
{
    uint8_t* rgb;
    Py_ssize_t size;
    int timestamp;
    int width;
    int height;
    char* mode;
    int lossless;
    float quality_factor;
    int method;
    WebPConfig config;
    WebPAnimEncoderObject* encp = (WebPAnimEncoderObject*)self;
    WebPAnimEncoder* enc = encp->enc;
    WebPPicture* frame = &(encp->frame);

    if (!PyArg_ParseTuple(args, "z#iiisifi",
        (char**)&rgb, &size, &timestamp, &width, &height, &mode,
        &lossless, &quality_factor, &method)) {
        return NULL;
    }

    // Check for NULL frame, which sets duration of final frame
    if (!rgb) {
        WebPAnimEncoderAdd(enc, NULL, timestamp, NULL);
        Py_RETURN_NONE;
    }

    // Setup config for this frame
    if (!WebPConfigInit(&config)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to initialize config!");
        return NULL;
    }
    config.lossless = lossless;
    config.quality = quality_factor;
    config.method = method;

    // Validate the config
    if (!WebPValidateConfig(&config)) {
        PyErr_SetString(PyExc_ValueError, "invalid configuration");
        return NULL;
    }

    // Populate the frame with raw bytes passed to us
    frame->width = width;
    frame->height = height;
    frame->use_argb = 1; // Don't convert RGB pixels to YUV
    if (strcmp(mode, "RGBA")==0) {
        WebPPictureImportRGBA(frame, rgb, 4 * width);
    } else if (strcmp(mode, "RGBX")==0) {
        WebPPictureImportRGBX(frame, rgb, 4 * width);
    } else {
        WebPPictureImportRGB(frame, rgb, 3 * width);
    }

    // Add the frame to the encoder
    if (!WebPAnimEncoderAdd(enc, frame, timestamp, &config)) {
        PyErr_SetString(PyExc_RuntimeError, WebPAnimEncoderGetError(enc));
        return NULL;
    }

    Py_RETURN_NONE;
}

PyObject* _anim_encoder_assemble(PyObject* self, PyObject* args)
{
    uint8_t* icc_bytes;
    uint8_t* exif_bytes;
    uint8_t* xmp_bytes;
    Py_ssize_t icc_size;
    Py_ssize_t exif_size;
    Py_ssize_t xmp_size;
    WebPData webp_data;
    WebPAnimEncoderObject* encp = (WebPAnimEncoderObject*)self;
    WebPAnimEncoder* enc = encp->enc;
    WebPMux* mux = NULL;
    PyObject* ret = NULL;

    if (!PyArg_ParseTuple(args, "s#s#s#",
    &icc_bytes, &icc_size, &exif_bytes, &exif_size, &xmp_bytes, &xmp_size)) {
        return NULL;
    }

    // Init the output buffer
    WebPDataInit(&webp_data);

    // Assemble everything into the output buffer
    if (!WebPAnimEncoderAssemble(enc, &webp_data)) {
        PyErr_SetString(PyExc_RuntimeError, WebPAnimEncoderGetError(enc));
        return NULL;
    }

    // Re-mux to add metadata as needed
    if (icc_size > 0 || exif_size > 0 || xmp_size > 0) {
        WebPMuxError err = WEBP_MUX_OK;
        int i_icc_size = (int)icc_size;
        int i_exif_size = (int)exif_size;
        int i_xmp_size = (int)xmp_size;
        WebPData icc_profile = { icc_bytes, i_icc_size };
        WebPData exif = { exif_bytes, i_exif_size };
        WebPData xmp = { xmp_bytes, i_xmp_size };

        mux = WebPMuxCreate(&webp_data, 1);
        if (mux == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "could not re-mux to add metadata");
            return NULL;
        }
        WebPDataClear(&webp_data);

        // Add ICCP chunk
        if (i_icc_size > 0) {
            err = WebPMuxSetChunk(mux, "ICCP", &icc_profile, 1);
            if (err != WEBP_MUX_OK) {
                return HandleMuxError(err, "ICCP");
            }
        }

        // Add EXIF chunk
        if (i_exif_size > 0) {
            err = WebPMuxSetChunk(mux, "EXIF", &exif, 1);
            if (err != WEBP_MUX_OK) {
                return HandleMuxError(err, "EXIF");
            }
        }

        // Add XMP chunk
        if (i_xmp_size > 0) {
            err = WebPMuxSetChunk(mux, "XMP ", &xmp, 1);
            if (err != WEBP_MUX_OK) {
                return HandleMuxError(err, "XMP");
            }
        }

        err = WebPMuxAssemble(mux, &webp_data);
        if (err != WEBP_MUX_OK) {
            return HandleMuxError(err, NULL);
        }
    }

    // Convert to Python bytes
    ret = PyBytes_FromStringAndSize((char*)webp_data.bytes, webp_data.size);
    WebPDataClear(&webp_data);

    // If we had to re-mux, we should free it now that we're done with it
    if (mux != NULL) {
        WebPMuxDelete(mux);
    }

    return ret;
}

// Decoder functions
PyObject* _anim_decoder_new(PyObject* self, PyObject* args)
{
    PyBytesObject *webp_string;
    const uint8_t *webp;
    Py_ssize_t size;
    WebPData webp_src;
    char* mode;
    WebPDecoderConfig config;
    WebPAnimDecoderObject* decp = NULL;
    WebPAnimDecoder* dec = NULL;

    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        return NULL;
    }
    PyBytes_AsStringAndSize((PyObject *)webp_string, (char**)&webp, &size);
    webp_src.bytes = webp;
    webp_src.size = size;

    // Sniff the mode, since the decoder API doesn't tell us
    mode = "RGBA";
    if (WebPGetFeatures(webp, size, &config.input) == VP8_STATUS_OK) {
        if (!config.input.has_alpha) {
            mode = "RGBX";
        }
    }

    // Create the decoder (default mode is RGBA, if no options passed)
    decp = PyObject_New(WebPAnimDecoderObject, &WebPAnimDecoder_Type);
    if (decp) {
        decp->mode = mode;
        if (WebPDataCopy(&webp_src, &(decp->data))) {
            dec = WebPAnimDecoderNew(&(decp->data), NULL);
            if (dec) {
                if (WebPAnimDecoderGetInfo(dec, &(decp->info))) {
                    decp->dec = dec;
                    return (PyObject*)decp;
                }
            }
        }
        PyObject_Del(decp);
    }
    PyErr_SetString(PyExc_RuntimeError, "could not create decoder object");
    return NULL;
}

PyObject* _anim_decoder_dealloc(PyObject* self)
{
    WebPAnimDecoderObject* decp = (WebPAnimDecoderObject *)self;
    WebPDataClear(&(decp->data));
    WebPAnimDecoderDelete(decp->dec);
    Py_RETURN_NONE;
}

PyObject* _anim_decoder_get_info(PyObject* self, PyObject* args)
{
    WebPAnimDecoderObject* decp = (WebPAnimDecoderObject *)self;
    WebPAnimInfo* info = &(decp->info);

    return Py_BuildValue("IIIIIs",
        info->canvas_width, info->canvas_height,
        info->loop_count,
        info->bgcolor,
        info->frame_count,
        decp->mode
    );
}

PyObject* _anim_decoder_get_chunk(PyObject* self, PyObject* args)
{
    char* mode;
    WebPAnimDecoderObject* decp = (WebPAnimDecoderObject *)self;
    const WebPDemuxer* demux;
    WebPChunkIterator iter;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s", &mode)) {
        return NULL;
    }

    demux = WebPAnimDecoderGetDemuxer(decp->dec);
    if (!WebPDemuxGetChunk(demux, mode, 1, &iter)) {
        Py_RETURN_NONE;
    }

    ret = PyBytes_FromStringAndSize((const char*)iter.chunk.bytes, iter.chunk.size);
    WebPDemuxReleaseChunkIterator(&iter);

    return ret;
}

PyObject* _anim_decoder_get_next(PyObject* self, PyObject* args)
{
    uint8_t* buf;
    int timestamp;
    PyObject* bytes;
    PyObject* ret;
    WebPAnimDecoderObject* decp = (WebPAnimDecoderObject*)self;

    if (!WebPAnimDecoderGetNext(decp->dec, &buf, &timestamp)) {
        PyErr_SetString(PyExc_IOError, "failed to read next frame");
        return NULL;
    }

    bytes = PyBytes_FromStringAndSize((char *)buf,
        decp->info.canvas_width * 4 * decp->info.canvas_height);

    ret = Py_BuildValue("Si", bytes, timestamp);

    Py_DECREF(bytes);
    return ret;
}

PyObject* _anim_decoder_has_more_frames(PyObject* self, PyObject* args)
{
    WebPAnimDecoderObject* decp = (WebPAnimDecoderObject*)self;
    return Py_BuildValue("i", WebPAnimDecoderHasMoreFrames(decp->dec));
}

PyObject* _anim_decoder_reset(PyObject* self, PyObject* args)
{
    WebPAnimDecoderObject* decp = (WebPAnimDecoderObject *)self;
    WebPAnimDecoderReset(decp->dec);
    Py_RETURN_NONE;
}

/* -------------------------------------------------------------------- */
/* Type Definitions                                                     */
/* -------------------------------------------------------------------- */

// WebPAnimEncoder methods
static struct PyMethodDef _anim_encoder_methods[] = {
    {"add", (PyCFunction)_anim_encoder_add, METH_VARARGS, "add"},
    {"assemble", (PyCFunction)_anim_encoder_assemble, METH_VARARGS, "assemble"},
    {NULL, NULL} /* sentinel */
};

// WebPAnimDecoder type definition
static PyTypeObject WebPAnimEncoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "WebPAnimEncoder",          /*tp_name */
    sizeof(WebPAnimEncoderObject),   /*tp_size */
    0,                          /*tp_itemsize */
    /* methods */
    (destructor)_anim_encoder_dealloc, /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number */
    0,                          /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    _anim_encoder_methods,      /*tp_methods*/
    0,                          /*tp_members*/
    0,     /*tp_getset*/
};

// WebPAnimDecoder methods
static struct PyMethodDef _anim_decoder_methods[] = {
    {"get_info", (PyCFunction)_anim_decoder_get_info, METH_VARARGS, "get_info"},
    {"get_chunk", (PyCFunction)_anim_decoder_get_chunk, METH_VARARGS, "get_chunk"},
    {"get_next", (PyCFunction)_anim_decoder_get_next, METH_VARARGS, "get_next"},
    {"has_more_frames", (PyCFunction)_anim_decoder_has_more_frames, METH_VARARGS, "has_more_frames"},
    {"reset", (PyCFunction)_anim_decoder_reset, METH_VARARGS, "reset"},
    {NULL, NULL} /* sentinel */
};

// WebPAnimDecoder type definition
static PyTypeObject WebPAnimDecoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "WebPAnimDecoder",          /*tp_name */
    sizeof(WebPAnimDecoderObject),   /*tp_size */
    0,                          /*tp_itemsize */
    /* methods */
    (destructor)_anim_decoder_dealloc, /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number */
    0,                          /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    _anim_decoder_methods,      /*tp_methods*/
    0,                          /*tp_members*/
    0,     /*tp_getset*/
};

#endif

/* -------------------------------------------------------------------- */
/* Legacy WebP Support                                                  */
/* -------------------------------------------------------------------- */

PyObject* WebPEncode_wrapper(PyObject* self, PyObject* args)
{
    int width;
    int height;
    int lossless;
    float quality_factor;
    uint8_t* rgb;
    uint8_t* icc_bytes;
    uint8_t* exif_bytes;
    uint8_t* xmp_bytes;
    uint8_t* output;
    char* mode;
    Py_ssize_t size;
    Py_ssize_t icc_size;
    Py_ssize_t exif_size;
    Py_ssize_t xmp_size;
    size_t ret_size;

    if (!PyArg_ParseTuple(args, PY_ARG_BYTES_LENGTH"iiifss#s#s#",
                (char**)&rgb, &size, &width, &height, &lossless, &quality_factor, &mode,
                &icc_bytes, &icc_size, &exif_bytes, &exif_size, &xmp_bytes, &xmp_size)) {
        return NULL;
    }
    if (strcmp(mode, "RGBA")==0){
        if (size < width * height * 4){
            Py_RETURN_NONE;
        }
        #if WEBP_ENCODER_ABI_VERSION >= 0x0100
        if (lossless) {
            ret_size = WebPEncodeLosslessRGBA(rgb, width, height, 4 * width, &output);
        } else
        #endif
        {
            ret_size = WebPEncodeRGBA(rgb, width, height, 4 * width, quality_factor, &output);
        }
    } else if (strcmp(mode, "RGB")==0){
        if (size < width * height * 3){
            Py_RETURN_NONE;
        }
        #if WEBP_ENCODER_ABI_VERSION >= 0x0100
        if (lossless) {
            ret_size = WebPEncodeLosslessRGB(rgb, width, height, 3 * width, &output);
        } else
        #endif
        {
            ret_size = WebPEncodeRGB(rgb, width, height, 3 * width, quality_factor, &output);
        }
    } else {
        Py_RETURN_NONE;
    }

#ifndef HAVE_WEBPMUX
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output, ret_size);
        free(output);
        return ret;
    }
#else
    {
    /* I want to truncate the *_size items that get passed into WebP
       data. Pypy2.1.0 had some issues where the Py_ssize_t items had
       data in the upper byte. (Not sure why, it shouldn't have been there)
    */
    int i_icc_size = (int)icc_size;
    int i_exif_size = (int)exif_size;
    int i_xmp_size = (int)xmp_size;
    WebPData output_data = {0};
    WebPData image = { output, ret_size };
    WebPData icc_profile = { icc_bytes, i_icc_size };
    WebPData exif = { exif_bytes, i_exif_size };
    WebPData xmp = { xmp_bytes, i_xmp_size };
    WebPMuxError err;
    int dbg = 0;

    int copy_data = 0;  // value 1 indicates given data WILL be copied to the mux
                        // and value 0 indicates data will NOT be copied.

    WebPMux* mux = WebPMuxNew();
    WebPMuxSetImage(mux, &image, copy_data);

    if (dbg) {
        /* was getting %ld icc_size == 0, icc_size>0 was true */
        fprintf(stderr, "icc size %d, %d \n", i_icc_size, i_icc_size > 0);
    }

    if (i_icc_size > 0) {
        if (dbg) {
            fprintf(stderr, "Adding ICC Profile\n");
        }
        err = WebPMuxSetChunk(mux, "ICCP", &icc_profile, copy_data);
        if (err != WEBP_MUX_OK) {
            return HandleMuxError(err, "ICCP");
        }
    }

    if (dbg) {
        fprintf(stderr, "exif size %d \n", i_exif_size);
    }
    if (i_exif_size > 0) {
        if (dbg) {
            fprintf(stderr, "Adding Exif Data\n");
        }
        err = WebPMuxSetChunk(mux, "EXIF", &exif, copy_data);
        if (err != WEBP_MUX_OK) {
            return HandleMuxError(err, "EXIF");
        }
    }

    if (dbg) {
        fprintf(stderr, "xmp size %d \n", i_xmp_size);
    }
    if (i_xmp_size > 0) {
        if (dbg){
            fprintf(stderr, "Adding XMP Data\n");
        }
        err = WebPMuxSetChunk(mux, "XMP ", &xmp, copy_data);
        if (err != WEBP_MUX_OK) {
            return HandleMuxError(err, "XMP ");
        }
    }

    WebPMuxAssemble(mux, &output_data);
    WebPMuxDelete(mux);
    free(output);

    ret_size = output_data.size;
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output_data.bytes, ret_size);
        WebPDataClear(&output_data);
        return ret;
    }
    }
#endif
    Py_RETURN_NONE;
}

PyObject* WebPDecode_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject* webp_string;
    const uint8_t* webp;
    Py_ssize_t size;
    PyObject *ret = Py_None, *bytes = NULL, *pymode = NULL, *icc_profile = NULL, *exif = NULL;
    WebPDecoderConfig config;
    VP8StatusCode vp8_status_code = VP8_STATUS_OK;
    char* mode = "RGB";

    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        return NULL;
    }

    if (!WebPInitDecoderConfig(&config)) {
        Py_RETURN_NONE;
    }

    PyBytes_AsStringAndSize((PyObject*) webp_string, (char**)&webp, &size);

    vp8_status_code = WebPGetFeatures(webp, size, &config.input);
    if (vp8_status_code == VP8_STATUS_OK) {
        // If we don't set it, we don't get alpha.
        // Initialized to MODE_RGB
        if (config.input.has_alpha) {
            config.output.colorspace = MODE_RGBA;
            mode = "RGBA";
        }

#ifndef HAVE_WEBPMUX
        vp8_status_code = WebPDecode(webp, size, &config);
#else
       {
        int copy_data = 0;
        WebPData data = { webp, size };
        WebPMuxFrameInfo image;
        WebPData icc_profile_data = {0};
        WebPData exif_data = {0};

        WebPMux* mux = WebPMuxCreate(&data, copy_data);
        if (NULL == mux)
            goto end;

        if (WEBP_MUX_OK != WebPMuxGetFrame(mux, 1, &image))
        {
            WebPMuxDelete(mux);
            goto end;
        }

        webp = image.bitstream.bytes;
        size = image.bitstream.size;

        vp8_status_code = WebPDecode(webp, size, &config);

        if (WEBP_MUX_OK == WebPMuxGetChunk(mux, "ICCP", &icc_profile_data))
            icc_profile = PyBytes_FromStringAndSize((const char*)icc_profile_data.bytes, icc_profile_data.size);

        if (WEBP_MUX_OK == WebPMuxGetChunk(mux, "EXIF", &exif_data))
            exif = PyBytes_FromStringAndSize((const char*)exif_data.bytes, exif_data.size);

        WebPDataClear(&image.bitstream);
        WebPMuxDelete(mux);
        }
#endif
    }

    if (vp8_status_code != VP8_STATUS_OK)
        goto end;

    if (config.output.colorspace < MODE_YUV) {
        bytes = PyBytes_FromStringAndSize((char*)config.output.u.RGBA.rgba,
                                          config.output.u.RGBA.size);
    } else {
        // Skipping YUV for now. Need Test Images.
        // UNDONE -- unclear if we'll ever get here if we set mode_rgb*
        bytes = PyBytes_FromStringAndSize((char*)config.output.u.YUVA.y,
                                          config.output.u.YUVA.y_size);
    }

#if PY_VERSION_HEX >= 0x03000000
    pymode = PyUnicode_FromString(mode);
#else
    pymode = PyString_FromString(mode);
#endif
    ret = Py_BuildValue("SiiSSS", bytes, config.output.width,
                        config.output.height, pymode,
                        NULL == icc_profile ? Py_None : icc_profile,
                        NULL == exif ? Py_None : exif);

end:
    WebPFreeDecBuffer(&config.output);

    Py_XDECREF(bytes);
    Py_XDECREF(pymode);
    Py_XDECREF(icc_profile);
    Py_XDECREF(exif);

    if (Py_None == ret)
        Py_RETURN_NONE;

    return ret;
}

// Return the decoder's version number, packed in hexadecimal using 8bits for
// each of major/minor/revision. E.g: v2.5.7 is 0x020507.
PyObject* WebPDecoderVersion_wrapper(PyObject* self, PyObject* args){
    return Py_BuildValue("i", WebPGetDecoderVersion());
}

/*
 * The version of webp that ships with (0.1.3) Ubuntu 12.04 doesn't handle alpha well.
 * Files that are valid with 0.3 are reported as being invalid.
 */
int WebPDecoderBuggyAlpha(void) {
    return WebPGetDecoderVersion()==0x0103;
}

PyObject* WebPDecoderBuggyAlpha_wrapper(PyObject* self, PyObject* args){
    return Py_BuildValue("i", WebPDecoderBuggyAlpha());
}

/* -------------------------------------------------------------------- */
/* Module Setup                                                         */
/* -------------------------------------------------------------------- */

static PyMethodDef webpMethods[] =
{
#ifdef HAVE_WEBPANIM
    {"WebPAnimDecoder", _anim_decoder_new, METH_VARARGS, "WebPAnimDecoder"},
    {"WebPAnimEncoder", _anim_encoder_new, METH_VARARGS, "WebPAnimEncoder"},
#endif
    {"WebPEncode", WebPEncode_wrapper, METH_VARARGS, "WebPEncode"},
    {"WebPDecode", WebPDecode_wrapper, METH_VARARGS, "WebPDecode"},
    {"WebPDecoderVersion", WebPDecoderVersion_wrapper, METH_VARARGS, "WebPVersion"},
    {"WebPDecoderBuggyAlpha", WebPDecoderBuggyAlpha_wrapper, METH_VARARGS, "WebPDecoderBuggyAlpha"},
    {NULL, NULL}
};

void addMuxFlagToModule(PyObject* m) {
#ifdef HAVE_WEBPMUX
    PyModule_AddObject(m, "HAVE_WEBPMUX", Py_True);
#else
    PyModule_AddObject(m, "HAVE_WEBPMUX", Py_False);
#endif
}

void addAnimFlagToModule(PyObject* m) {
#ifdef HAVE_WEBPANIM
    PyModule_AddObject(m, "HAVE_WEBPANIM", Py_True);
#else
    PyModule_AddObject(m, "HAVE_WEBPANIM", Py_False);
#endif
}

void addTransparencyFlagToModule(PyObject* m) {
    PyModule_AddObject(m, "HAVE_TRANSPARENCY",
		       PyBool_FromLong(!WebPDecoderBuggyAlpha()));
}

static int setup_module(PyObject* m) {
    addMuxFlagToModule(m);
    addAnimFlagToModule(m);
    addTransparencyFlagToModule(m);

#ifdef HAVE_WEBPANIM
    /* Ready object types */
    if (PyType_Ready(&WebPAnimDecoder_Type) < 0 ||
        PyType_Ready(&WebPAnimEncoder_Type) < 0)
        return -1;
#endif
    return 0;
}

#if PY_VERSION_HEX >= 0x03000000
PyMODINIT_FUNC
PyInit__webp(void) {
    PyObject* m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_webp",            /* m_name */
        NULL,               /* m_doc */
        -1,                 /* m_size */
        webpMethods,        /* m_methods */
    };

    m = PyModule_Create(&module_def);
    if (setup_module(m) < 0)
        return NULL;

    return m;
}
#else
PyMODINIT_FUNC
init_webp(void)
{
    PyObject* m = Py_InitModule("_webp", webpMethods);
    setup_module(m);
}
#endif
