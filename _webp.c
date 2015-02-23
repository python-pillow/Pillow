#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "py3.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>

#ifdef HAVE_WEBPMUX
#include <webp/mux.h>
#endif

PyObject* WebPEncode_wrapper(PyObject* self, PyObject* args)
{
    int width;
    int height;
    int lossless;
    float quality_factor;
    uint8_t *rgb;
    uint8_t *icc_bytes;
    uint8_t *exif_bytes;
    uint8_t *output;
    char *mode;
    Py_ssize_t size;
    Py_ssize_t icc_size;
    Py_ssize_t  exif_size;
    size_t ret_size;

    if (!PyArg_ParseTuple(args, "s#iiifss#s#",
                (char**)&rgb, &size, &width, &height, &lossless, &quality_factor, &mode,
                &icc_bytes, &icc_size, &exif_bytes, &exif_size)) {
        Py_RETURN_NONE;
    }
    if (strcmp(mode, "RGBA")==0){
        if (size < width * height * 4){
            Py_RETURN_NONE;
        }
        #if WEBP_ENCODER_ABI_VERSION >= 0x0100
        if (lossless) {
            ret_size = WebPEncodeLosslessRGBA(rgb, width, height, 4* width, &output);
        } else
        #endif
        {
            ret_size = WebPEncodeRGBA(rgb, width, height, 4* width, quality_factor, &output);
        }
    } else if (strcmp(mode, "RGB")==0){
        if (size < width * height * 3){
            Py_RETURN_NONE;
        }
        #if WEBP_ENCODER_ABI_VERSION >= 0x0100
        if (lossless) {
            ret_size = WebPEncodeLosslessRGB(rgb, width, height, 3* width, &output);
        } else
        #endif
        {
            ret_size = WebPEncodeRGB(rgb, width, height, 3* width, quality_factor, &output);
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
    /* I want to truncate the *_size items that get passed into webp
       data. Pypy2.1.0 had some issues where the Py_ssize_t items had
       data in the upper byte. (Not sure why, it shouldn't have been there)
    */
    int i_icc_size = (int)icc_size;
    int i_exif_size = (int)exif_size;
    WebPData output_data = {0};
    WebPData image = { output, ret_size };
    WebPData icc_profile = { icc_bytes, i_icc_size };
    WebPData exif = { exif_bytes, i_exif_size };
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
            fprintf (stderr, "Adding ICC Profile\n");
        }
        err = WebPMuxSetChunk(mux, "ICCP", &icc_profile, copy_data);
        if (dbg && err == WEBP_MUX_INVALID_ARGUMENT) {
            fprintf(stderr, "Invalid ICC Argument\n");
        } else if (dbg && err == WEBP_MUX_MEMORY_ERROR) {
            fprintf(stderr, "ICC Memory Error\n");
        }
    }

    if (dbg) {
        fprintf(stderr, "exif size %d \n", i_exif_size);
    }
    if (i_exif_size > 0) {
        if (dbg){
            fprintf (stderr, "Adding Exif Data\n");
        }
        err = WebPMuxSetChunk(mux, "EXIF", &exif, copy_data);
        if (dbg && err == WEBP_MUX_INVALID_ARGUMENT) {
            fprintf(stderr, "Invalid Exif Argument\n");
        } else if (dbg && err == WEBP_MUX_MEMORY_ERROR) {
            fprintf(stderr, "Exif Memory Error\n");
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
    PyBytesObject *webp_string;
    const uint8_t *webp;
    Py_ssize_t size;
    PyObject *ret = Py_None, *bytes = NULL, *pymode = NULL, *icc_profile = NULL, *exif = NULL;
    WebPDecoderConfig config;
    VP8StatusCode vp8_status_code = VP8_STATUS_OK;
    char* mode = "RGB";

    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        Py_RETURN_NONE;
    }

    if (!WebPInitDecoderConfig(&config)) {
        Py_RETURN_NONE;
    }

    PyBytes_AsStringAndSize((PyObject *) webp_string, (char**)&webp, &size);

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
        bytes = PyBytes_FromStringAndSize((char *)config.output.u.RGBA.rgba,
                                          config.output.u.RGBA.size);
    } else {
        // Skipping YUV for now. Need Test Images.
        // UNDONE -- unclear if we'll ever get here if we set mode_rgb*
        bytes = PyBytes_FromStringAndSize((char *)config.output.u.YUVA.y,
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
PyObject* WebPDecoderBuggyAlpha_wrapper(PyObject* self, PyObject* args){
    return Py_BuildValue("i", WebPGetDecoderVersion()==0x0103);
}

static PyMethodDef webpMethods[] =
{
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
    addMuxFlagToModule(m);
    return m;
}
#else
PyMODINIT_FUNC
init_webp(void)
{
    PyObject* m = Py_InitModule("_webp", webpMethods);
    addMuxFlagToModule(m);
}
#endif
