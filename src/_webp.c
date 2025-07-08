#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "libImaging/Imaging.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>
#include <webp/mux.h>
#include <webp/demux.h>

/*
 * Check the versions from mux.h and demux.h, to ensure the WebPAnimEncoder and
 * WebPAnimDecoder APIs are present (initial support was added in 0.5.0). The
 * very early versions had some significant differences, so we require later
 * versions.
 */
#if WEBP_MUX_ABI_VERSION < 0x0106 || WEBP_DEMUX_ABI_VERSION < 0x0107
#error libwebp 0.5.0 and above is required. Upgrade libwebp or build Pillow with --disable-webp flag
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
    char message[100];
    int message_len;
    assert(err <= WEBP_MUX_NOT_FOUND && err >= WEBP_MUX_NOT_ENOUGH_DATA);

    // Check for a memory error first
    if (err == WEBP_MUX_MEMORY_ERROR) {
        return PyErr_NoMemory();
    }

    // Create the error message
    if (chunk == NULL) {
        message_len =
            sprintf(message, "could not assemble chunks: %s", kErrorMessages[-err]);
    } else {
        message_len = sprintf(
            message, "could not set %.4s chunk: %s", chunk, kErrorMessages[-err]
        );
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
            PyErr_SetString(PyExc_OSError, message);
            break;

        default:
            PyErr_SetString(PyExc_RuntimeError, message);
            break;
    }
    return NULL;
}

/* -------------------------------------------------------------------- */
/* Frame import                                                         */
/* -------------------------------------------------------------------- */

static int
import_frame_libwebp(WebPPicture *frame, Imaging im) {
    if (strcmp(im->mode, "RGBA") && strcmp(im->mode, "RGB") &&
        strcmp(im->mode, "RGBX")) {
        PyErr_SetString(PyExc_ValueError, "unsupported image mode");
        return -1;
    }

    frame->width = im->xsize;
    frame->height = im->ysize;
    frame->use_argb = 1;  // Don't convert RGB pixels to YUV

    if (!WebPPictureAlloc(frame)) {
        PyErr_SetString(PyExc_MemoryError, "can't allocate picture frame");
        return -2;
    }

    int ignore_fourth_channel = strcmp(im->mode, "RGBA");
    for (int y = 0; y < im->ysize; ++y) {
        UINT8 *src = (UINT8 *)im->image32[y];
        UINT32 *dst = frame->argb + frame->argb_stride * y;
        if (ignore_fourth_channel) {
            for (int x = 0; x < im->xsize; ++x) {
                dst[x] =
                    ((UINT32)(src[x * 4 + 2]) | ((UINT32)(src[x * 4 + 1]) << 8) |
                     ((UINT32)(src[x * 4]) << 16) | (0xff << 24));
            }
        } else {
            for (int x = 0; x < im->xsize; ++x) {
                dst[x] =
                    ((UINT32)(src[x * 4 + 2]) | ((UINT32)(src[x * 4 + 1]) << 8) |
                     ((UINT32)(src[x * 4]) << 16) | ((UINT32)(src[x * 4 + 3]) << 24));
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
    char *mode;
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
}

PyObject *
_anim_encoder_add(PyObject *self, PyObject *args) {
    PyObject *i0;
    Imaging im;
    int timestamp;
    int lossless;
    float quality_factor;
    float alpha_quality_factor;
    int method;
    ImagingSectionCookie cookie;
    WebPConfig config;
    WebPAnimEncoderObject *encp = (WebPAnimEncoderObject *)self;
    WebPAnimEncoder *enc = encp->enc;
    WebPPicture *frame = &(encp->frame);

    if (!PyArg_ParseTuple(
            args,
            "Oiiffi",
            &i0,
            &timestamp,
            &lossless,
            &quality_factor,
            &alpha_quality_factor,
            &method
        )) {
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

    // Setup config for this frame
    if (!WebPConfigInit(&config)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to initialize config!");
        return NULL;
    }
    config.lossless = lossless;
    config.quality = quality_factor;
    config.alpha_quality = alpha_quality_factor;
    config.method = method;

    // Validate the config
    if (!WebPValidateConfig(&config)) {
        PyErr_SetString(PyExc_ValueError, "invalid configuration");
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
    char *mode;
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
}

PyObject *
_anim_decoder_get_info(PyObject *self) {
    WebPAnimDecoderObject *decp = (WebPAnimDecoderObject *)self;
    WebPAnimInfo *info = &(decp->info);

    return Py_BuildValue(
        "(II)IIIs",
        info->canvas_width,
        info->canvas_height,
        info->loop_count,
        info->bgcolor,
        info->frame_count,
        decp->mode
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
_anim_decoder_get_next(PyObject *self) {
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

    ret = Py_BuildValue("Si", bytes, timestamp);

    Py_DECREF(bytes);
    return ret;
}

PyObject *
_anim_decoder_reset(PyObject *self) {
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
    int lossless;
    float quality_factor;
    float alpha_quality_factor;
    int method;
    int exact;
    Imaging im;
    PyObject *i0;
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
            "Oiffs#iis#s#",
            &i0,
            &lossless,
            &quality_factor,
            &alpha_quality_factor,
            &icc_bytes,
            &icc_size,
            &method,
            &exact,
            &exif_bytes,
            &exif_size,
            &xmp_bytes,
            &xmp_size
        )) {
        return NULL;
    }

    if (!PyCapsule_IsValid(i0, IMAGING_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", IMAGING_MAGIC);
        return NULL;
    }

    im = (Imaging)PyCapsule_GetPointer(i0, IMAGING_MAGIC);

    // Setup config for this frame
    if (!WebPConfigInit(&config)) {
        PyErr_SetString(PyExc_RuntimeError, "failed to initialize config!");
        return NULL;
    }
    config.lossless = lossless;
    config.quality = quality_factor;
    config.alpha_quality = alpha_quality_factor;
    config.method = method;
    config.exact = exact;

    // Validate the config
    if (!WebPValidateConfig(&config)) {
        PyErr_SetString(PyExc_ValueError, "invalid configuration");
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
    PyDict_SetItemString(d, "webpdecoder_version", v ? v : Py_None);
    Py_XDECREF(v);

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
