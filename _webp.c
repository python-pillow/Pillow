#include <Python.h>
#include "py3.h"
#include <webp/encode.h>
#include <webp/decode.h>

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
        Py_INCREF(Py_None);
        return Py_None;
    }

    PyBytes_AsStringAndSize((PyObject *) rgb_string, &rgb, &size);

    if (stride * height > size) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    ret_size = WebPEncodeRGB(rgb, width, height, stride, quality_factor, &output);
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize(output, ret_size);
        free(output);
        return ret;
    }
    Py_INCREF(Py_None);
    return Py_None;

}

PyObject* WebPDecodeRGB_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject *webp_string;
    float quality_factor;
    int width;
    int height;
    uint8_t *webp;
    uint8_t *output;
    Py_ssize_t size;
    PyObject *ret;

    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    PyBytes_AsStringAndSize((PyObject *) webp_string, &webp, &size);

    output = WebPDecodeRGB(webp, size, &width, &height);

    ret = PyBytes_FromStringAndSize(output, width * height * 3);
    free(output);
    return Py_BuildValue("Sii", ret, width, height);
}

static PyMethodDef webpMethods[] =
{
    {"WebPEncodeRGB", WebPEncodeRGB_wrapper, METH_VARARGS, "WebPEncodeRGB"},
    {"WebPDecodeRGB", WebPDecodeRGB_wrapper, METH_VARARGS, "WebPEncodeRGB"},
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
init_webp()
{
    PyObject* m;
    m = Py_InitModule("_webp", webpMethods);
}
#endif
