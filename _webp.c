#include <Python.h>
#include "py3.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>


PyObject* WebPEncodeRGB_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject *rgb_string;
    int width;
    int height;
    int stride;
    float quality_factor;
    uint8_t *rgb;
    uint8_t *output;
    Py_ssize_t size;
    size_t ret_size;

    if (!PyArg_ParseTuple(args, "Siiif", &rgb_string, &width, &height, &stride, &quality_factor)) {
        Py_RETURN_NONE;
    }

    PyBytes_AsStringAndSize((PyObject *) rgb_string, (char**)&rgb, &size);

    if (stride * height > size) {
        Py_RETURN_NONE;
    }

    ret_size = WebPEncodeRGB(rgb, width, height, stride, quality_factor, &output);
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output, ret_size);
        free(output);
        return ret;
    }
    Py_RETURN_NONE;
}


PyObject* WebPEncodeRGBA_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject *rgba_string;
    int width;
    int height;
    int stride;
    float quality_factor;
    uint8_t *rgba;
    uint8_t *output;
    Py_ssize_t size;
    size_t ret_size;

    if (!PyArg_ParseTuple(args, "Siiif", &rgba_string, &width, &height, &stride, &quality_factor)) {
        Py_RETURN_NONE;
   }

    PyBytes_AsStringAndSize((PyObject *) rgba_string, (char**)&rgba, &size);

    if (stride * height > size) {
        Py_RETURN_NONE;
    }

    ret_size = WebPEncodeRGBA(rgba, width, height, stride, quality_factor, &output);
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output, ret_size);
        free(output);
        return ret;
    }
    Py_RETURN_NONE;
}


PyObject* WebPDecode_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject *webp_string;
    uint8_t *webp;
    Py_ssize_t size;
    PyObject *ret, *bytes, *pymode;
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
        vp8_status_code = WebPDecode(webp, size, &config);
    }   
    
    if (vp8_status_code != VP8_STATUS_OK) {
        Py_RETURN_NONE;
    }   
    
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
    ret = Py_BuildValue("SiiS", bytes, config.output.width, 
                        config.output.height, pymode);
    WebPFreeDecBuffer(&config.output);
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
    {"WebPEncodeRGB", WebPEncodeRGB_wrapper, METH_VARARGS, "WebPEncodeRGB"},
    {"WebPEncodeRGBA", WebPEncodeRGBA_wrapper, METH_VARARGS, "WebPEncodeRGBA"},
    {"WebPDecode", WebPDecode_wrapper, METH_VARARGS, "WebPDecode"},
    {"WebPDecoderVersion", WebPDecoderVersion_wrapper, METH_VARARGS, "WebPVersion"},
    {"WebPDecoderBuggyAlpha", WebPDecoderBuggyAlpha_wrapper, METH_VARARGS, "WebPDecoderBuggyAlpha"},
    {NULL, NULL}
};


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
    return m;
}
#else
PyMODINIT_FUNC
init_webp(void)
{
    Py_InitModule("_webp", webpMethods);
}
#endif
