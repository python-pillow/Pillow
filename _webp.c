#include <Python.h>
#include "py3.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>


PyObject* WebPGetFeatures_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject *webp_string;
    uint8_t* webp = NULL;
    VP8StatusCode vp8_status_code = VP8_STATUS_OK;
    Py_ssize_t size;
    WebPBitstreamFeatures features;


    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    PyBytes_AsStringAndSize((PyObject *) webp_string, (char**)&webp, &size);

    vp8_status_code = WebPGetFeatures(webp, size, &features);

    if (vp8_status_code == VP8_STATUS_OK) {
        printf("%i", features.has_alpha);

    } else {
        // TODO: raise some sort of error
        printf("Error occured checking webp file with code: %d\n", vp8_status_code);
        Py_INCREF(Py_None);
        return Py_None;
    }

    return Py_BuildValue("b", features.has_alpha);
}


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

    PyBytes_AsStringAndSize((PyObject *) rgb_string, (char**)&rgb, &size);

    if (stride * height > size) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    ret_size = WebPEncodeRGB(rgb, width, height, stride, quality_factor, &output);
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output, ret_size);
        free(output);
        return ret;
    }
    Py_INCREF(Py_None);
    return Py_None;

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
        Py_INCREF(Py_None);
        return Py_None;
    }

    PyBytes_AsStringAndSize((PyObject *) rgba_string, (char**)&rgba, &size);

    if (stride * height > size) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    ret_size = WebPEncodeRGBA(rgba, width, height, stride, quality_factor, &output);
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output, ret_size);
        free(output);
        return ret;
    }
    Py_INCREF(Py_None);
    return Py_None;

}


PyObject* WebPDecode_wrapper(PyObject* self, PyObject* args)
{
    PyBytesObject *webp_string;
	int width;
    int height;
    uint8_t *webp;
    uint8_t *output;
    Py_ssize_t size;
    PyObject *ret, *bytes;
	WebPDecoderConfig config;
    VP8StatusCode vp8_status_code = VP8_STATUS_OK;
	char* mode = NULL;

    if (!PyArg_ParseTuple(args, "S", &webp_string)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

	if (!WebPInitDecoderConfig(&config)) {
        Py_INCREF(Py_None);
        return Py_None;
    }		

    PyBytes_AsStringAndSize((PyObject *) webp_string, (char**)&webp, &size);

    vp8_status_code = WebPGetFeatures(webp, size, &config.input);
	if (vp8_status_code == VP8_STATUS_OK) {
		vp8_status_code = WebPDecode(webp, size, &config);
	}	
	
	if (vp8_status_code != VP8_STATUS_OK) {
        Py_INCREF(Py_None);
        return Py_None;
	}	
	
	if (config.output.colorspace < MODE_YUV) {
		bytes = PyBytes_FromStringAndSize((char *)config.output.u.RGBA.rgba, config.output.u.RGBA.size);
	} else {
		// Skipping YUV for now. 
		bytes = PyBytes_FromStringAndSize((char *)config.output.u.YUVA.y, config.output.u.YUVA.y_size);
	}
	switch(config.output.colorspace) {
		// UNDONE, alternate orderings
	case MODE_RGB:
		mode = "RGB";
		break;
	case MODE_RGBA:
		mode = "RGBA";
		break;
	default:
		mode = "ERR";
	}

	height = config.output.height;
	width = config.output.width;


	ret = Py_BuildValue("SiiS", bytes, width, height, PyBytes_FromString(mode));
	WebPFreeDecBuffer(&config.output);
	return ret;
}




static PyMethodDef webpMethods[] =
{
    {"WebPGetFeatures", WebPGetFeatures_wrapper, METH_VARARGS, "WebPGetFeatures"},
    {"WebPEncodeRGB", WebPEncodeRGB_wrapper, METH_VARARGS, "WebPEncodeRGB"},
    {"WebPEncodeRGBA", WebPEncodeRGBA_wrapper, METH_VARARGS, "WebPEncodeRGBA"},
    {"WebPDecode", WebPDecode_wrapper, METH_VARARGS, "WebPDecode"},
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
