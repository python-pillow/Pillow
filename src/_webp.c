#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "libImaging/Imaging.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>
#include <webp/mux.h>
#include <webp/demux.h>

/*
 * Check the ABI versions to ensure the APIs and config options used here are are
 * present
 */
#if WEBP_ENCODER_ABI_VERSION < 0x020f || WEBP_MUX_ABI_VERSION < 0x0108 || \
    WEBP_DEMUX_ABI_VERSION < 0x0107
#error libwebp 1.2.0 and above is required. Upgrade libwebp or build Pillow with --disable-webp flag
#endif

void
ImagingSectionEnter(ImagingSectionCookie *cookie) {
    *cookie = (PyThreadState *)PyEval_SaveThread();
}

void
ImagingSectionLeave(ImagingSectionCookie *cookie) {
    PyEval_RestoreThread((PyThreadState *)*cookie);
}

/* -------------------------------------------------------------------- */
/* WebP Muxer Error Handling                                            */
/* -------------------------------------------------------------------- */

static const char *const kErrorMessages[-WEBP_MUX_NOT_ENOUGH_DATA + 1] = {
    "WEBP_MUX_NOT_FOUND",
    "WEBP_MUX_INVALID_ARGUMENT",
    "WEBP_MUX_BAD_DATA",
    "WEBP_MUX_MEMORY_ERROR",
    "WEBP_MUX_NOT_ENOUGH_DATA"
};

PyObject *
HandleMuxError(WebPMuxError err, char *chunk) {
    assert(err <= WEBP_MUX_NOT_FOUND && err >= WEBP_MUX_NOT_ENOUGH_DATA);

    PyObject *err_type;
    switch (err) {
        case WEBP_MUX_MEMORY_ERROR:
            return PyErr_NoMemory();

        case WEBP_MUX_NOT_FOUND:
        case WEBP_MUX_INVALID_ARGUMENT:
            err_type = PyExc_ValueError;
            break;

        case WEBP_MUX_BAD_DATA:
        case WEBP_MUX_NOT_ENOUGH_DATA:
            err_type = PyExc_OSError;
            break;

        default:
            err_type = PyExc_RuntimeError;
            break;
    }

    if (chunk == NULL) {
        PyErr_Format(err_type, "could not assemble chunks: %s", kErrorMessages[-err]);
    } else {
        PyErr_Format(
            err_type, "could not set %.4s chunk: %s", chunk, kErrorMessages[-err]
        );
    }
    return NULL;
}

/* -------------------------------------------------------------------- */
/* Encoder configuration                                                */
/* -------------------------------------------------------------------- */

typedef struct {
    const char *name;
    size_t offset;
    int is_float;
} WebPConfigOption;

static const WebPConfigOption webp_config_options[] = {
    // clang-format off
    {.name = "alpha_compression", .offset = offsetof(WebPConfig, alpha_compression), .is_float = 0},
    {.name = "alpha_filtering", .offset = offsetof(WebPConfig, alpha_filtering), .is_float = 0},
    {.name = "alpha_quality", .offset = offsetof(WebPConfig, alpha_quality), .is_float = 0},
    {.name = "autofilter", .offset = offsetof(WebPConfig, autofilter), .is_float = 0},
    {.name = "emulate_jpeg_size", .offset = offsetof(WebPConfig, emulate_jpeg_size), .is_float = 0},
    {.name = "exact", .offset = offsetof(WebPConfig, exact), .is_float = 0},
    {.name = "filter_sharpness", .offset = offsetof(WebPConfig, filter_sharpness), .is_float = 0},
    {.name = "filter_strength", .offset = offsetof(WebPConfig, filter_strength), .is_float = 0},
    {.name = "filter_type", .offset = offsetof(WebPConfig, filter_type), .is_float = 0},
    {.name = "lossless", .offset = offsetof(WebPConfig, lossless), .is_float = 0},
    {.name = "low_memory", .offset = offsetof(WebPConfig, low_memory), .is_float = 0},
    {.name = "method", .offset = offsetof(WebPConfig, method), .is_float = 0},
    {.name = "near_lossless", .offset = offsetof(WebPConfig, near_lossless), .is_float = 0},
    {.name = "partition_limit", .offset = offsetof(WebPConfig, partition_limit), .is_float = 0},
    {.name = "partitions", .offset = offsetof(WebPConfig, partitions), .is_float = 0},
    {.name = "pass", .offset = offsetof(WebPConfig, pass), .is_float = 0},
    {.name = "preprocessing", .offset = offsetof(WebPConfig, preprocessing), .is_float = 0},
    {.name = "qmax", .offset = offsetof(WebPConfig, qmax), .is_float = 0},
    {.name = "qmin", .offset = offsetof(WebPConfig, qmin), .is_float = 0},
    {.name = "quality", .offset = offsetof(WebPConfig, quality), .is_float = 1},
    {.name = "segments", .offset = offsetof(WebPConfig, segments), .is_float = 0},
    {.name = "sns_strength", .offset = offsetof(WebPConfig, sns_strength), .is_float = 0},
    {.name = "target_psnr", .offset = offsetof(WebPConfig, target_PSNR), .is_float = 1},
    {.name = "target_size", .offset = offsetof(WebPConfig, target_size), .is_float = 0},
    {.name = "thread_level", .offset = offsetof(WebPConfig, thread_level), .is_float = 0},
    {.name = "use_sharp_yuv", .offset = offsetof(WebPConfig, use_sharp_yuv), .is_float = 0},
    // clang-format on

    // show_compressed, use_delta_palette, and image_hint, while defined in WebPConfig,
    // are deliberately not exposed since they're either useless or reserved-internal.
};

/**
 * Cast a float value from a dict of encoder options.
 * @param options Options dict.
 * @param name Name of option.
 * @param out Pointer to float to write to. MUST be non-NULL.
 * @return 0 on success, -1 on failure (with a Python exception set).
 */
static int
config_get_float(PyObject *options, const char *name, float *out) {
    PyObject *value = PyDict_GetItemString(options, name);
    if (value == NULL) {
        return 0;
    }
    double f = PyFloat_AsDouble(value);
    if (f == -1.0 && PyErr_Occurred()) {
        return -1;
    }
    *out = (float)f;
    return 0;
}

/**
 * Initialize and validate a WebPConfig from a dict of encoder options.
 * @param config Pointer to WebPConfig to initialize.
 * @param options Dict of encoder options to read from.
 * @return 0 on success, -1 on failure (with a Python exception set).
 */
static int
config_setup(WebPConfig *config, PyObject *options) {
    if (!WebPConfigInit(config)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to initialize config!");
        return -1;
    }

    // Preset + quality needs to be set first, as it will override other options.
    PyObject *preset = PyDict_GetItemString(options, "preset");
    if (preset != NULL) {
        long preset_value = PyLong_AsLong(preset);
        if (preset_value == -1 && PyErr_Occurred()) {
            return -1;
        }
        float quality = config->quality;
        if (config_get_float(options, "quality", &quality)) {
            return -1;
        }
        if (!WebPConfigPreset(config, (WebPPreset)preset_value, quality)) {
            PyErr_SetString(PyExc_ValueError, "invalid preset");
            return -1;
        }
    }

    for (size_t i = 0; i < sizeof(webp_config_options) / sizeof(webp_config_options[0]);
         i++) {
        const WebPConfigOption *option = &webp_config_options[i];
        char *field = (char *)config + option->offset;
        if (option->is_float) {
            if (config_get_float(options, option->name, (float *)field)) {
                return -1;
            }
        } else {
            PyObject *value = PyDict_GetItemString(options, option->name);
            if (value == NULL) {
                continue;
            }
            long i_value = PyLong_AsLong(value);
            if (i_value == -1 && PyErr_Occurred()) {
                return -1;
            }
            *(int *)field = (int)i_value;
        }
    }

    if (!WebPValidateConfig(config)) {
        PyErr_SetString(PyExc_ValueError, "WebP configuration validation failed");
        return -1;
    }

    return 0;
}

/* -------------------------------------------------------------------- */
/* Frame import                                                         */
/* -------------------------------------------------------------------- */

#ifdef WORDS_BIGENDIAN
#define ARGB_A 0
#define ARGB_R 1
#define ARGB_G 2
#define ARGB_B 3
#else
#define ARGB_B 0
#define ARGB_G 1
#define ARGB_R 2
#define ARGB_A 3
#endif

static int
import_frame_libwebp(WebPPicture *frame, Imaging im) {
    if (im->mode != IMAGING_MODE_RGBA && im->mode != IMAGING_MODE_RGB &&
        im->mode != IMAGING_MODE_RGBX) {
        PyErr_SetString(PyExc_ValueError, "unsupported image mode");
        return -1;
    }

    int xsize = im->xsize, ysize = im->ysize;

    frame->width = xsize;
    frame->height = ysize;
    frame->use_argb = 1;  // Don't convert RGB pixels to YUV

    if (!WebPPictureAlloc(frame)) {
        PyErr_SetString(PyExc_MemoryError, "can't allocate picture frame");
        return -2;
    }

    // restrict safe: imIn is read-only,
    // frame is a fresh allocation from libwebp.
    int ignore_fourth_channel = im->mode != IMAGING_MODE_RGBA;
    for (int y = 0; y < ysize; ++y) {
        const UINT8 *restrict src = (const UINT8 *)im->image32[y];
        UINT8 *restrict dst = (UINT8 *)(frame->argb + frame->argb_stride * y);
        if (ignore_fourth_channel) {
            for (int x = 0; x < xsize; x++, src += 4, dst += 4) {
                dst[ARGB_R] = src[0];
                dst[ARGB_G] = src[1];
                dst[ARGB_B] = src[2];
                dst[ARGB_A] = 0xff;
            }
        } else {
            for (int x = 0; x < xsize; x++, src += 4, dst += 4) {
                dst[ARGB_R] = src[0];
                dst[ARGB_G] = src[1];
                dst[ARGB_B] = src[2];
                dst[ARGB_A] = src[3];
            }
        }
    }

    return 0;
}

/* -------------------------------------------------------------------- */
/* WebP Animation Support                                               */
/* -------------------------------------------------------------------- */

// Encoder type
typedef struct {
    PyObject_HEAD WebPAnimEncoder *enc;
    WebPPicture frame;
} WebPAnimEncoderObject;

static PyTypeObject WebPAnimEncoder_Type;

// Decoder type
typedef struct {
    PyObject_HEAD WebPAnimDecoder *dec;
    WebPAnimInfo info;
    WebPData data;
    ModeID mode;
} WebPAnimDecoderObject;

static PyTypeObject WebPAnimDecoder_Type;

// Encoder functions
PyObject *
_anim_encoder_new(PyObject *self, PyObject *args) {
    int width, height;
    uint32_t bgcolor;
    int loop_count;
    int minimize_size;
    int kmin, kmax;
    int allow_mixed;
    int verbose;
    WebPAnimEncoderOptions enc_options;
    WebPAnimEncoderObject *encp = NULL;
    WebPAnimEncoder *enc = NULL;

    if (!PyArg_ParseTuple(
            args,
            "(ii)Iiiiiii",
            &width,
            &height,
            &bgcolor,
            &loop_count,
            &minimize_size,
            &kmin,
            &kmax,
            &allow_mixed,
            &verbose
        )) {
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
                return (PyObject *)encp;
            }
            WebPPictureFree(&(encp->frame));
        }
        PyObject_Del(encp);
    }
    PyErr_SetString(PyExc_RuntimeError, "could not create encoder object");
    return NULL;
}

void
_anim_encoder_dealloc(PyObject *self) {
    WebPAnimEncoderObject *encp = (WebPAnimEncoderObject *)self;
    WebPPictureFree(&(encp->frame));
    WebPAnimEncoderDelete(encp->enc);
    Py_TYPE(self)->tp_free(self);
}

PyObject *
_anim_encoder_add(PyObject *self, PyObject *args) {
    PyObject *i0;
    Imaging im;
    int timestamp;
    PyObject *options;
    ImagingSectionCookie cookie;
    WebPConfig config;
    WebPAnimEncoderObject *encp = (WebPAnimEncoderObject *)self;
    WebPAnimEncoder *enc = encp->enc;
    WebPPicture *frame = &(encp->frame);

    if (!PyArg_ParseTuple(args, "OiO!", &i0, &timestamp, &PyDict_Type, &options)) {
        return NULL;
    }

    // Check for NULL frame, which sets duration of final frame
    if (i0 == Py_None) {
        WebPAnimEncoderAdd(enc, NULL, timestamp, NULL);
        Py_RETURN_NONE;
    }

    if (!PyCapsule_IsValid(i0, IMAGING_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", IMAGING_MAGIC);
        return NULL;
    }

    im = (Imaging)PyCapsule_GetPointer(i0, IMAGING_MAGIC);
    if (!im) {
        return NULL;
    }

    if (config_setup(&config, options)) {
        return NULL;
    }

    if (import_frame_libwebp(frame, im)) {
        return NULL;
    }

    ImagingSectionEnter(&cookie);
    int ok = WebPAnimEncoderAdd(enc, frame, timestamp, &config);
    ImagingSectionLeave(&cookie);

    if (!ok) {
        PyErr_SetString(PyExc_RuntimeError, WebPAnimEncoderGetError(enc));
        return NULL;
    }

    Py_RETURN_NONE;
}

PyObject *
_anim_encoder_assemble(PyObject *self, PyObject *args) {
    uint8_t *icc_bytes;
    uint8_t *exif_bytes;
    uint8_t *xmp_bytes;
    Py_ssize_t icc_size;
    Py_ssize_t exif_size;
    Py_ssize_t xmp_size;
    WebPData webp_data;
    WebPAnimEncoderObject *encp = (WebPAnimEncoderObject *)self;
    WebPAnimEncoder *enc = encp->enc;
    WebPMux *mux = NULL;
    PyObject *ret = NULL;

    if (!PyArg_ParseTuple(
            args,
            "s#s#s#",
            &icc_bytes,
            &icc_size,
            &exif_bytes,
            &exif_size,
            &xmp_bytes,
            &xmp_size
        )) {
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
        WebPData icc_profile = {icc_bytes, i_icc_size};
        WebPData exif = {exif_bytes, i_exif_size};
        WebPData xmp = {xmp_bytes, i_xmp_size};

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
    ret = PyBytes_FromStringAndSize((char *)webp_data.bytes, webp_data.size);
    WebPDataClear(&webp_data);

    // If we had to re-mux, we should free it now that we're done with it
    if (mux != NULL) {
        WebPMuxDelete(mux);
    }

    return ret;
}

// Decoder functions
PyObject *
_anim_decoder_new(PyObject *self, PyObject *args) {
    PyBytesObject *webp_string;
    const uint8_t *webp;
    Py_ssize_t size;
    WebPData webp_src;
    ModeID mode;
    WebPDecoderConfig config;
    WebPAnimDecoderObject *decp = NULL;
    WebPAnimDecoder *dec = NULL;

    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        return NULL;
    }
    PyBytes_AsStringAndSize((PyObject *)webp_string, (char **)&webp, &size);
    webp_src.bytes = webp;
    webp_src.size = size;

    // Sniff the mode, since the decoder API doesn't tell us
    mode = IMAGING_MODE_RGBA;
    if (WebPGetFeatures(webp, size, &config.input) == VP8_STATUS_OK) {
        if (!config.input.has_alpha) {
            mode = IMAGING_MODE_RGBX;
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
                    return (PyObject *)decp;
                }
            }
            WebPDataClear(&(decp->data));
        }
        PyObject_Del(decp);
    }
    PyErr_SetString(PyExc_OSError, "could not create decoder object");
    return NULL;
}

void
_anim_decoder_dealloc(PyObject *self) {
    WebPAnimDecoderObject *decp = (WebPAnimDecoderObject *)self;
    WebPDataClear(&(decp->data));
    WebPAnimDecoderDelete(decp->dec);
    Py_TYPE(self)->tp_free(self);
}

PyObject *
_anim_decoder_get_info(PyObject *self, PyObject *args) {
    WebPAnimDecoderObject *decp = (WebPAnimDecoderObject *)self;
    WebPAnimInfo *info = &(decp->info);

    return Py_BuildValue(
        "(II)IIIs",
        info->canvas_width,
        info->canvas_height,
        info->loop_count,
        info->bgcolor,
        info->frame_count,
        getModeData(decp->mode)->name
    );
}

PyObject *
_anim_decoder_get_chunk(PyObject *self, PyObject *args) {
    char *mode;
    WebPAnimDecoderObject *decp = (WebPAnimDecoderObject *)self;
    const WebPDemuxer *demux;
    WebPChunkIterator iter;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "s", &mode)) {
        return NULL;
    }

    demux = WebPAnimDecoderGetDemuxer(decp->dec);
    if (!WebPDemuxGetChunk(demux, mode, 1, &iter)) {
        Py_RETURN_NONE;
    }

    ret = PyBytes_FromStringAndSize((const char *)iter.chunk.bytes, iter.chunk.size);
    WebPDemuxReleaseChunkIterator(&iter);

    return ret;
}

PyObject *
_anim_decoder_get_next(PyObject *self, PyObject *args) {
    uint8_t *buf;
    int timestamp;
    int ok;
    PyObject *bytes;
    PyObject *ret;
    ImagingSectionCookie cookie;
    WebPAnimDecoderObject *decp = (WebPAnimDecoderObject *)self;

    ImagingSectionEnter(&cookie);
    ok = WebPAnimDecoderGetNext(decp->dec, &buf, &timestamp);
    ImagingSectionLeave(&cookie);
    if (!ok) {
        PyErr_SetString(PyExc_OSError, "failed to read next frame");
        return NULL;
    }

    bytes = PyBytes_FromStringAndSize(
        (char *)buf, decp->info.canvas_width * 4 * decp->info.canvas_height
    );
    if (!bytes) {
        return NULL;
    }

    ret = Py_BuildValue("Si", bytes, timestamp);

    Py_DECREF(bytes);
    return ret;
}

PyObject *
_anim_decoder_reset(PyObject *self, PyObject *args) {
    WebPAnimDecoderObject *decp = (WebPAnimDecoderObject *)self;
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

// WebPAnimEncoder type definition
static PyTypeObject WebPAnimEncoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "WebPAnimEncoder",
    .tp_basicsize = sizeof(WebPAnimEncoderObject),
    .tp_dealloc = (destructor)_anim_encoder_dealloc,
    .tp_methods = _anim_encoder_methods,
};

// WebPAnimDecoder methods
static struct PyMethodDef _anim_decoder_methods[] = {
    {"get_info", (PyCFunction)_anim_decoder_get_info, METH_NOARGS, "get_info"},
    {"get_chunk", (PyCFunction)_anim_decoder_get_chunk, METH_VARARGS, "get_chunk"},
    {"get_next", (PyCFunction)_anim_decoder_get_next, METH_NOARGS, "get_next"},
    {"reset", (PyCFunction)_anim_decoder_reset, METH_NOARGS, "reset"},
    {NULL, NULL} /* sentinel */
};

// WebPAnimDecoder type definition
static PyTypeObject WebPAnimDecoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "WebPAnimDecoder",
    .tp_basicsize = sizeof(WebPAnimDecoderObject),
    .tp_dealloc = (destructor)_anim_decoder_dealloc,
    .tp_methods = _anim_decoder_methods,
};

/* -------------------------------------------------------------------- */
/* Legacy WebP Support                                                  */
/* -------------------------------------------------------------------- */

PyObject *
WebPEncode_wrapper(PyObject *self, PyObject *args) {
    Imaging im;
    PyObject *i0;
    PyObject *options;
    uint8_t *icc_bytes;
    uint8_t *exif_bytes;
    uint8_t *xmp_bytes;
    uint8_t *output;
    Py_ssize_t icc_size;
    Py_ssize_t exif_size;
    Py_ssize_t xmp_size;
    size_t ret_size;
    int ok;
    ImagingSectionCookie cookie;
    WebPConfig config;
    WebPMemoryWriter writer;
    WebPPicture pic;

    if (!PyArg_ParseTuple(
            args,
            "Os#s#s#O!",
            &i0,
            &icc_bytes,
            &icc_size,
            &exif_bytes,
            &exif_size,
            &xmp_bytes,
            &xmp_size,
            &PyDict_Type,
            &options
        )) {
        return NULL;
    }

    if (!PyCapsule_IsValid(i0, IMAGING_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", IMAGING_MAGIC);
        return NULL;
    }

    im = (Imaging)PyCapsule_GetPointer(i0, IMAGING_MAGIC);
    if (!im) {
        return NULL;
    }

    if (config_setup(&config, options)) {
        return NULL;
    }

    if (!WebPPictureInit(&pic)) {
        PyErr_SetString(PyExc_ValueError, "could not initialise picture");
        return NULL;
    }

    if (import_frame_libwebp(&pic, im)) {
        return NULL;
    }

    WebPMemoryWriterInit(&writer);
    pic.writer = WebPMemoryWrite;
    pic.custom_ptr = &writer;

    ImagingSectionEnter(&cookie);
    ok = WebPEncode(&config, &pic);
    ImagingSectionLeave(&cookie);

    WebPPictureFree(&pic);

    output = writer.mem;
    ret_size = writer.size;

    if (!ok) {
        int error_code = (&pic)->error_code;
        char message[50] = "";
        if (error_code == VP8_ENC_ERROR_BAD_DIMENSION) {
            sprintf(
                message,
                ": Image size exceeds WebP limit of %d pixels",
                WEBP_MAX_DIMENSION
            );
        }
        PyErr_Format(PyExc_ValueError, "encoding error %d%s", error_code, message);
        free(output);
        return NULL;
    }

    {
        /* I want to truncate the *_size items that get passed into WebP
           data. Pypy2.1.0 had some issues where the Py_ssize_t items had
           data in the upper byte. (Not sure why, it shouldn't have been there)
        */
        int i_icc_size = (int)icc_size;
        int i_exif_size = (int)exif_size;
        int i_xmp_size = (int)xmp_size;
        WebPData output_data = {0};
        WebPData image = {output, ret_size};
        WebPData icc_profile = {icc_bytes, i_icc_size};
        WebPData exif = {exif_bytes, i_exif_size};
        WebPData xmp = {xmp_bytes, i_xmp_size};
        WebPMuxError err;
        int dbg = 0;

        int copy_data = 0;  // value 1 indicates given data WILL be copied to the mux
                            // and value 0 indicates data will NOT be copied.

        WebPMux *mux = WebPMuxNew();
        if (mux == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "could not create mux object");
            return NULL;
        }
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
            if (dbg) {
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
            PyObject *ret =
                PyBytes_FromStringAndSize((char *)output_data.bytes, ret_size);
            WebPDataClear(&output_data);
            return ret;
        }
    }
    Py_RETURN_NONE;
}

// Version as string
const char *
WebPDecoderVersion_str(void) {
    static char version[20];
    int version_number = WebPGetDecoderVersion();
    sprintf(
        version,
        "%d.%d.%d",
        version_number >> 16,
        (version_number >> 8) % 0x100,
        version_number % 0x100
    );
    return version;
}

/* -------------------------------------------------------------------- */
/* Module Setup                                                         */
/* -------------------------------------------------------------------- */

static PyMethodDef webpMethods[] = {
    {"WebPAnimDecoder", _anim_decoder_new, METH_VARARGS, "WebPAnimDecoder"},
    {"WebPAnimEncoder", _anim_encoder_new, METH_VARARGS, "WebPAnimEncoder"},
    {"WebPEncode", WebPEncode_wrapper, METH_VARARGS, "WebPEncode"},
    {NULL, NULL}
};

static int
setup_module(PyObject *m) {
    /* Ready object types */
    if (PyType_Ready(&WebPAnimDecoder_Type) < 0 ||
        PyType_Ready(&WebPAnimEncoder_Type) < 0) {
        return -1;
    }

    PyObject *d = PyModule_GetDict(m);
    PyObject *v = PyUnicode_FromString(WebPDecoderVersion_str());
    if (!v) {
        return -1;
    }
    PyDict_SetItemString(d, "webpdecoder_version", v);
    Py_DECREF(v);

    return 0;
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, setup_module},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

PyMODINIT_FUNC
PyInit__webp(void) {
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_webp",
        .m_methods = webpMethods,
        .m_slots = slots
    };

    return PyModuleDef_Init(&module_def);
}
