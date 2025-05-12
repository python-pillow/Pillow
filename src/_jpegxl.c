#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>
#include "libImaging/Imaging.h"

#include <jxl/codestream_header.h>
#include <jxl/decode.h>
#include <jxl/types.h>
#include <jxl/thread_parallel_runner.h>

#define _JXL_CHECK(call_name)              \
    if (decp->status != JXL_DEC_SUCCESS) { \
        jxl_call_name = call_name;         \
        goto end;                          \
    }

void
_jxl_get_pixel_format(JxlPixelFormat *pf, const JxlBasicInfo *bi) {
    pf->num_channels = bi->num_color_channels + bi->num_extra_channels;

    if (bi->exponent_bits_per_sample > 0 || bi->alpha_exponent_bits > 0) {
        pf->data_type = JXL_TYPE_FLOAT;  // not yet supported
    } else if (bi->bits_per_sample > 8) {
        pf->data_type = JXL_TYPE_UINT16;  // not yet supported
    } else {
        pf->data_type = JXL_TYPE_UINT8;
    }

    // this *might* cause some issues on Big-Endian systems
    // would be great to test it
    pf->endianness = JXL_NATIVE_ENDIAN;
    pf->align = 0;
}

// TODO: floating point mode
char *
_jxl_get_mode(const JxlBasicInfo *bi) {
    // 16-bit single channel images are supported
    if (bi->bits_per_sample == 16 && bi->num_color_channels == 1 &&
        bi->alpha_bits == 0 && !bi->alpha_premultiplied) {
        return "I;16";
    }

    // PIL doesn't support high bit depth images
    // it will throw an exception but that's for your own good
    // you wouldn't want to see distorted image
    if (bi->bits_per_sample != 8) {
        return NULL;
    }

    // image has transparency
    if (bi->alpha_bits > 0) {
        if (bi->num_color_channels == 3) {
            if (bi->alpha_premultiplied) {
                return "RGBa";
            }
            return "RGBA";
        }
        if (bi->num_color_channels == 1) {
            if (bi->alpha_premultiplied) {
                return "La";
            }
            return "LA";
        }
    }

    // image has no transparency
    if (bi->num_color_channels == 3) {
        return "RGB";
    }
    if (bi->num_color_channels == 1) {
        return "L";
    }

    // could not recognize mode
    return NULL;
}

// Decoder type
typedef struct {
    PyObject_HEAD JxlDecoder *decoder;
    void *runner;

    uint8_t *jxl_data;        // input jxl bitstream
    Py_ssize_t jxl_data_len;  // length of input jxl bitstream

    uint8_t *outbuf;
    Py_ssize_t outbuf_len;

    uint8_t *jxl_icc;
    Py_ssize_t jxl_icc_len;
    uint8_t *jxl_exif;
    Py_ssize_t jxl_exif_len;
    uint8_t *jxl_xmp;
    Py_ssize_t jxl_xmp_len;

    JxlDecoderStatus status;
    JxlBasicInfo basic_info;
    JxlPixelFormat pixel_format;

    Py_ssize_t n_frames;

    char *mode;
} JpegXlDecoderObject;

static PyTypeObject JpegXlDecoder_Type;

void
_jxl_decoder_dealloc(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (decp->jxl_data) {
        free(decp->jxl_data);
        decp->jxl_data = NULL;
        decp->jxl_data_len = 0;
    }
    if (decp->outbuf) {
        free(decp->outbuf);
        decp->outbuf = NULL;
        decp->outbuf_len = 0;
    }
    if (decp->jxl_icc) {
        free(decp->jxl_icc);
        decp->jxl_icc = NULL;
        decp->jxl_icc_len = 0;
    }
    if (decp->jxl_exif) {
        free(decp->jxl_exif);
        decp->jxl_exif = NULL;
        decp->jxl_exif_len = 0;
    }
    if (decp->jxl_xmp) {
        free(decp->jxl_xmp);
        decp->jxl_xmp = NULL;
        decp->jxl_xmp_len = 0;
    }

    if (decp->decoder) {
        JxlDecoderDestroy(decp->decoder);
        decp->decoder = NULL;
    }

    if (decp->runner) {
        JxlThreadParallelRunnerDestroy(decp->runner);
        decp->runner = NULL;
    }
}

// sets input jxl bitstream loaded into jxl_data
// has to be called after every rewind
void
_jxl_decoder_set_input(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    decp->status =
        JxlDecoderSetInput(decp->decoder, decp->jxl_data, decp->jxl_data_len);

    // the input contains the whole jxl bitstream so it can be closed
    JxlDecoderCloseInput(decp->decoder);
}

PyObject *
_jxl_decoder_rewind(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;
    JxlDecoderRewind(decp->decoder);
    Py_RETURN_NONE;
}

bool
_jxl_decoder_count_frames(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    decp->n_frames = 0;

    // count all JXL_DEC_NEED_IMAGE_OUT_BUFFER events
    while (decp->status != JXL_DEC_SUCCESS) {
        decp->status = JxlDecoderProcessInput(decp->decoder);

        if (decp->status == JXL_DEC_NEED_IMAGE_OUT_BUFFER) {
            if (JxlDecoderSkipCurrentFrame(decp->decoder) != JXL_DEC_SUCCESS) {
                return false;
            }
            decp->n_frames++;
        }
    }

    _jxl_decoder_rewind((PyObject *)decp);

    return true;
}

PyObject *
_jxl_decoder_new(PyObject *self, PyObject *args) {
    PyBytesObject *jxl_string;

    JpegXlDecoderObject *decp = NULL;
    decp = PyObject_New(JpegXlDecoderObject, &JpegXlDecoder_Type);
    decp->mode = NULL;
    decp->jxl_data = NULL;
    decp->jxl_data_len = 0;
    decp->outbuf = NULL;
    decp->outbuf_len = 0;
    decp->jxl_icc = NULL;
    decp->jxl_icc_len = 0;
    decp->jxl_exif = NULL;
    decp->jxl_exif_len = 0;
    decp->jxl_xmp = NULL;
    decp->jxl_xmp_len = 0;
    decp->n_frames = 0;

    // used for printing more detailed error messages
    char *jxl_call_name;

    // parse one argument which is a string with jxl data
    if (!PyArg_ParseTuple(args, "S", &jxl_string)) {
        return NULL;
    }

    // this data needs to be copied to JpegXlDecoderObject
    // so that input bitstream is preserved across calls
    const uint8_t *_tmp_jxl_data;
    Py_ssize_t _tmp_jxl_data_len;

    // convert jxl data string to C uint8_t pointer
    PyBytes_AsStringAndSize(
        (PyObject *)jxl_string, (char **)&_tmp_jxl_data, &_tmp_jxl_data_len
    );

    // here occurs this copying (inefficiency)
    decp->jxl_data = malloc(_tmp_jxl_data_len);
    memcpy(decp->jxl_data, _tmp_jxl_data, _tmp_jxl_data_len);
    decp->jxl_data_len = _tmp_jxl_data_len;

    size_t suggested_num_threads = JxlThreadParallelRunnerDefaultNumWorkerThreads();
    decp->runner = JxlThreadParallelRunnerCreate(NULL, suggested_num_threads);
    decp->decoder = JxlDecoderCreate(NULL);

    decp->status = JxlDecoderSetParallelRunner(
        decp->decoder, JxlThreadParallelRunner, decp->runner
    );
    _JXL_CHECK("JxlDecoderSetParallelRunner")

    decp->status = JxlDecoderSubscribeEvents(
        decp->decoder,
        JXL_DEC_BASIC_INFO | JXL_DEC_COLOR_ENCODING | JXL_DEC_FRAME | JXL_DEC_BOX |
            JXL_DEC_FULL_IMAGE
    );
    _JXL_CHECK("JxlDecoderSubscribeEvents")

    // tell libjxl to decompress boxes (for example Exif is usually compressed)
    decp->status = JxlDecoderSetDecompressBoxes(decp->decoder, JXL_TRUE);
    _JXL_CHECK("JxlDecoderSetDecompressBoxes")

    _jxl_decoder_set_input((PyObject *)decp);
    _JXL_CHECK("JxlDecoderSetInput")

    // decode everything up to the first frame
    do {
        decp->status = JxlDecoderProcessInput(decp->decoder);

decoder_loop_skip_process:

        // there was an error at JxlDecoderProcessInput stage
        if (decp->status == JXL_DEC_ERROR) {
            jxl_call_name = "JxlDecoderProcessInput";
            goto end;
        }

        // got basic info
        if (decp->status == JXL_DEC_BASIC_INFO) {
            decp->status = JxlDecoderGetBasicInfo(decp->decoder, &decp->basic_info);
            _JXL_CHECK("JxlDecoderGetBasicInfo");

            _jxl_get_pixel_format(&decp->pixel_format, &decp->basic_info);
            if (decp->pixel_format.data_type != JXL_TYPE_UINT8 &&
                decp->pixel_format.data_type != JXL_TYPE_UINT16) {
                // only 8 bit integer value images are supported for now
                PyErr_SetString(
                    PyExc_NotImplementedError, "unsupported pixel data type"
                );
                goto end_with_custom_error;
            }
            decp->mode = _jxl_get_mode(&decp->basic_info);

            continue;
        }

        // got color encoding
        if (decp->status == JXL_DEC_COLOR_ENCODING) {
            decp->status = JxlDecoderGetICCProfileSize(
                decp->decoder,
#if JPEGXL_MINOR_VERSION < 9
                NULL,
#endif
                JXL_COLOR_PROFILE_TARGET_DATA,
                &decp->jxl_icc_len
            );
            _JXL_CHECK("JxlDecoderGetICCProfileSize");

            decp->jxl_icc = malloc(decp->jxl_icc_len);
            if (!decp->jxl_icc) {
                PyErr_SetString(PyExc_OSError, "jxl_icc malloc failed");
                goto end_with_custom_error;
            }

            decp->status = JxlDecoderGetColorAsICCProfile(
                decp->decoder,
#if JPEGXL_MINOR_VERSION < 9
                NULL,
#endif
                JXL_COLOR_PROFILE_TARGET_DATA,
                decp->jxl_icc,
                decp->jxl_icc_len
            );
            _JXL_CHECK("JxlDecoderGetColorAsICCProfile");

            continue;
        }

        if (decp->status == JXL_DEC_BOX) {
            char btype[4];
            decp->status = JxlDecoderGetBoxType(decp->decoder, btype, JXL_TRUE);
            _JXL_CHECK("JxlDecoderGetBoxType");

            bool is_box_exif = !memcmp(btype, "Exif", 4);
            bool is_box_xmp = !memcmp(btype, "xml ", 4);
            if (!is_box_exif && !is_box_xmp) {
                // not exif/xmp box so continue
                continue;
            }

            size_t cur_compr_box_size;
            decp->status = JxlDecoderGetBoxSizeRaw(decp->decoder, &cur_compr_box_size);
            _JXL_CHECK("JxlDecoderGetBoxSizeRaw");

            uint8_t *final_jxl_buf = NULL;
            Py_ssize_t final_jxl_buf_len = 0;

            // cur_box_size is actually compressed box size
            // it will also serve as our chunk size
            do {
                uint8_t *_new_jxl_buf =
                    realloc(final_jxl_buf, final_jxl_buf_len + cur_compr_box_size);
                if (!_new_jxl_buf) {
                    PyErr_SetString(PyExc_OSError, "failed to allocate final_jxl_buf");
                    goto end;
                }
                final_jxl_buf = _new_jxl_buf;

                decp->status = JxlDecoderSetBoxBuffer(
                    decp->decoder, final_jxl_buf + final_jxl_buf_len, cur_compr_box_size
                );
                _JXL_CHECK("JxlDecoderSetBoxBuffer");

                decp->status = JxlDecoderProcessInput(decp->decoder);

                size_t remaining = JxlDecoderReleaseBoxBuffer(decp->decoder);
                final_jxl_buf_len += (cur_compr_box_size - remaining);
            } while (decp->status == JXL_DEC_BOX_NEED_MORE_OUTPUT);

            if (is_box_exif) {
                decp->jxl_exif = final_jxl_buf;
                decp->jxl_exif_len = final_jxl_buf_len;
            } else {
                decp->jxl_xmp = final_jxl_buf;
                decp->jxl_xmp_len = final_jxl_buf_len;
            }

            // dirty hack: skip first step of decoding loop since
            // we already did it in do...while above
            goto decoder_loop_skip_process;
        }

    } while (decp->status != JXL_DEC_FRAME);

    // couldn't determine Image mode or it is unsupported
    if (!decp->mode) {
        PyErr_SetString(PyExc_NotImplementedError, "only 8-bit images are supported");
        goto end_with_custom_error;
    }

    if (decp->basic_info.have_animation) {
        // get frame count by iterating over image out events
        if (!_jxl_decoder_count_frames((PyObject *)decp)) {
            PyErr_SetString(PyExc_OSError, "something went wrong when counting frames");
            goto end_with_custom_error;
        }
    }

    return (PyObject *)decp;

    // on success we should never reach here

    // set error message
    char err_msg[128];

end:
    snprintf(
        err_msg,
        128,
        "could not create decoder object. libjxl call: %s returned: %d",
        jxl_call_name,
        decp->status
    );
    PyErr_SetString(PyExc_OSError, err_msg);

end_with_custom_error:

    // deallocate
    _jxl_decoder_dealloc((PyObject *)decp);
    PyObject_Del(decp);

    return NULL;
}

PyObject *
_jxl_decoder_get_info(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    return Py_BuildValue(
        "(II)sOIIII",
        decp->basic_info.xsize,
        decp->basic_info.ysize,
        decp->mode,
        decp->basic_info.have_animation ? Py_True : Py_False,
        decp->basic_info.animation.tps_numerator,
        decp->basic_info.animation.tps_denominator,
        decp->basic_info.animation.num_loops,
        decp->n_frames
    );
}

PyObject *
_jxl_decoder_get_next(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;
    PyObject *bytes;
    PyObject *ret;
    JxlFrameHeader fhdr = {};

    char *jxl_call_name;

    // process events until next frame output is ready
    while (decp->status != JXL_DEC_NEED_IMAGE_OUT_BUFFER) {
        decp->status = JxlDecoderProcessInput(decp->decoder);

        // every frame was decoded successfully
        if (decp->status == JXL_DEC_SUCCESS) {
            Py_RETURN_NONE;
        }

        // this should only occur after rewind
        if (decp->status == JXL_DEC_NEED_MORE_INPUT) {
            _jxl_decoder_set_input((PyObject *)decp);
            _JXL_CHECK("JxlDecoderSetInput")
            continue;
        }

        if (decp->status == JXL_DEC_FRAME) {
            // decode frame header
            decp->status = JxlDecoderGetFrameHeader(decp->decoder, &fhdr);
            _JXL_CHECK("JxlDecoderGetFrameHeader");
            continue;
        }
    }

    size_t new_outbuf_len;
    decp->status = JxlDecoderImageOutBufferSize(
        decp->decoder, &decp->pixel_format, &new_outbuf_len
    );
    _JXL_CHECK("JxlDecoderImageOutBufferSize");

    // only allocate memory when current buffer is too small
    if (decp->outbuf_len < new_outbuf_len) {
        decp->outbuf_len = new_outbuf_len;
        uint8_t *_new_outbuf = realloc(decp->outbuf, decp->outbuf_len);
        if (!_new_outbuf) {
            PyErr_SetString(PyExc_OSError, "failed to allocate outbuf");
            goto end_with_custom_error;
        }
        decp->outbuf = _new_outbuf;
    }

    decp->status = JxlDecoderSetImageOutBuffer(
        decp->decoder, &decp->pixel_format, decp->outbuf, decp->outbuf_len
    );
    _JXL_CHECK("JxlDecoderSetImageOutBuffer");

    // decode image into output_buffer
    decp->status = JxlDecoderProcessInput(decp->decoder);

    if (decp->status != JXL_DEC_FULL_IMAGE) {
        PyErr_SetString(PyExc_OSError, "failed to read next frame");
        goto end_with_custom_error;
    }

    bytes = PyBytes_FromStringAndSize((char *)(decp->outbuf), decp->outbuf_len);

    ret = Py_BuildValue("SIi", bytes, fhdr.duration, fhdr.is_last);

    Py_DECREF(bytes);
    return ret;

    // we also shouldn't reach here if frame read was ok

    // set error message
    char err_msg[128];

end:
    snprintf(
        err_msg,
        128,
        "could not read frame. libjxl call: %s returned: %d",
        jxl_call_name,
        decp->status
    );
    PyErr_SetString(PyExc_OSError, err_msg);

end_with_custom_error:

    // no need to deallocate anything here
    // user can just ignore error

    return NULL;
}

PyObject *
_jxl_decoder_get_icc(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (!decp->jxl_icc) {
        Py_RETURN_NONE;
    }

    return PyBytes_FromStringAndSize((const char *)decp->jxl_icc, decp->jxl_icc_len);
}

PyObject *
_jxl_decoder_get_exif(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (!decp->jxl_exif) {
        Py_RETURN_NONE;
    }

    return PyBytes_FromStringAndSize((const char *)decp->jxl_exif, decp->jxl_exif_len);
}

PyObject *
_jxl_decoder_get_xmp(PyObject *self) {
    JpegXlDecoderObject *decp = (JpegXlDecoderObject *)self;

    if (!decp->jxl_xmp) {
        Py_RETURN_NONE;
    }

    return PyBytes_FromStringAndSize((const char *)decp->jxl_xmp, decp->jxl_xmp_len);
}

// Version as string
const char *
JpegXlDecoderVersion_str(void) {
    static char version[20];
    sprintf(
        version,
        "%d.%d.%d",
        JPEGXL_MAJOR_VERSION,
        JPEGXL_MINOR_VERSION,
        JPEGXL_PATCH_VERSION
    );
    return version;
}

/* -------------------------------------------------------------------- */
/* Type Definitions                                                     */
/* -------------------------------------------------------------------- */

// JpegXlDecoder methods
static struct PyMethodDef _jpegxl_decoder_methods[] = {
    {"get_info", (PyCFunction)_jxl_decoder_get_info, METH_NOARGS, "get_info"},
    {"get_next", (PyCFunction)_jxl_decoder_get_next, METH_NOARGS, "get_next"},
    {"get_icc", (PyCFunction)_jxl_decoder_get_icc, METH_NOARGS, "get_icc"},
    {"get_exif", (PyCFunction)_jxl_decoder_get_exif, METH_NOARGS, "get_exif"},
    {"get_xmp", (PyCFunction)_jxl_decoder_get_xmp, METH_NOARGS, "get_xmp"},
    {"rewind", (PyCFunction)_jxl_decoder_rewind, METH_NOARGS, "rewind"},
    {NULL, NULL} /* sentinel */
};

// JpegXlDecoder type definition
static PyTypeObject JpegXlDecoder_Type = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "JpegXlDecoder",
    .tp_basicsize = sizeof(JpegXlDecoderObject),
    .tp_dealloc = (destructor)_jxl_decoder_dealloc,
    .tp_methods = _jpegxl_decoder_methods,
};

/* -------------------------------------------------------------------- */
/* Module Setup                                                         */
/* -------------------------------------------------------------------- */

static PyMethodDef jpegxlMethods[] = {
    {"JpegXlDecoder", _jxl_decoder_new, METH_VARARGS, "JpegXlDecoder"}, {NULL, NULL}
};

static int
setup_module(PyObject *m) {
    if (PyType_Ready(&JpegXlDecoder_Type) < 0) {
        return -1;
    }

    // TODO(oloke) ready object types?
    PyObject *d = PyModule_GetDict(m);
    PyObject *v = PyUnicode_FromString(JpegXlDecoderVersion_str());
    PyDict_SetItemString(d, "libjxl_version", v ? v : Py_None);
    Py_XDECREF(v);

    return 0;
}

PyMODINIT_FUNC
PyInit__jpegxl(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_jpegxl",
        .m_size = -1,
        .m_methods = jpegxlMethods,
    };

    m = PyModule_Create(&module_def);
    if (setup_module(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
