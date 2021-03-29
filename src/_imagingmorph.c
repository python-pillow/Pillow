/*
 * The Python Imaging Library
 *
 * A binary morphology add-on for the Python Imaging Library
 *
 * History:
 *   2014-06-04 Initial version.
 *
 * Copyright (c) 2014 Dov Grobgeld <dov.grobgeld@gmail.com>
 *
 * See the README file for information on usage and redistribution.
 */

#include "Python.h"
#include "libImaging/Imaging.h"

#define LUT_SIZE (1 << 9)

/* Apply a morphologic LUT to a binary image. Outputs a
   a new binary image.

   Expected parameters:

      1. a LUT - a 512 byte size lookup table.
      2. an input Imaging image id.
      3. an output Imaging image id

   Returns number of changed pixels.
*/
static PyObject *
apply(PyObject *self, PyObject *args) {
    const char *lut;
    PyObject *py_lut;
    Py_ssize_t lut_len, i0, i1;
    Imaging imgin, imgout;
    int width, height;
    int row_idx, col_idx;
    UINT8 **inrows, **outrows;
    int num_changed_pixels = 0;

    if (!PyArg_ParseTuple(args, "Onn", &py_lut, &i0, &i1)) {
        PyErr_SetString(PyExc_RuntimeError, "Argument parsing problem");
        return NULL;
    }

    if (!PyBytes_Check(py_lut)) {
        PyErr_SetString(PyExc_RuntimeError, "The morphology LUT is not a bytes object");
        return NULL;
    }

    lut_len = PyBytes_Size(py_lut);

    if (lut_len < LUT_SIZE) {
        PyErr_SetString(PyExc_RuntimeError, "The morphology LUT has the wrong size");
        return NULL;
    }

    lut = PyBytes_AsString(py_lut);

    imgin = (Imaging)i0;
    imgout = (Imaging)i1;
    width = imgin->xsize;
    height = imgin->ysize;

    if (imgin->type != IMAGING_TYPE_UINT8 || imgin->bands != 1) {
        PyErr_SetString(PyExc_RuntimeError, "Unsupported image type");
        return NULL;
    }
    if (imgout->type != IMAGING_TYPE_UINT8 || imgout->bands != 1) {
        PyErr_SetString(PyExc_RuntimeError, "Unsupported image type");
        return NULL;
    }

    inrows = imgin->image8;
    outrows = imgout->image8;

    for (row_idx = 0; row_idx < height; row_idx++) {
        UINT8 *outrow = outrows[row_idx];
        UINT8 *inrow = inrows[row_idx];
        UINT8 *prow, *nrow; /* Previous and next row */

        /* zero boundary conditions. TBD support other modes */
        outrow[0] = outrow[width - 1] = 0;
        if (row_idx == 0 || row_idx == height - 1) {
            for (col_idx = 0; col_idx < width; col_idx++) {
                outrow[col_idx] = 0;
            }
            continue;
        }

        prow = inrows[row_idx - 1];
        nrow = inrows[row_idx + 1];

        for (col_idx = 1; col_idx < width - 1; col_idx++) {
            int cim = col_idx - 1;
            int cip = col_idx + 1;
            unsigned char b0 = prow[cim] & 1;
            unsigned char b1 = prow[col_idx] & 1;
            unsigned char b2 = prow[cip] & 1;

            unsigned char b3 = inrow[cim] & 1;
            unsigned char b4 = inrow[col_idx] & 1;
            unsigned char b5 = inrow[cip] & 1;

            unsigned char b6 = nrow[cim] & 1;
            unsigned char b7 = nrow[col_idx] & 1;
            unsigned char b8 = nrow[cip] & 1;

            int lut_idx =
                (b0 | (b1 << 1) | (b2 << 2) | (b3 << 3) | (b4 << 4) | (b5 << 5) |
                 (b6 << 6) | (b7 << 7) | (b8 << 8));
            outrow[col_idx] = 255 * (lut[lut_idx] & 1);
            num_changed_pixels += ((b4 & 1) != (outrow[col_idx] & 1));
        }
    }
    return Py_BuildValue("i", num_changed_pixels);
}

/* Match a morphologic LUT to a binary image and return a list
   of the coordinates of all matching pixels.

   Expected parameters:

      1. a LUT - a 512 byte size lookup table.
      2. an input Imaging image id.

   Returns list of matching pixels.
*/
static PyObject *
match(PyObject *self, PyObject *args) {
    const char *lut;
    PyObject *py_lut;
    Py_ssize_t lut_len, i0;
    Imaging imgin;
    int width, height;
    int row_idx, col_idx;
    UINT8 **inrows;
    PyObject *ret = PyList_New(0);

    if (!PyArg_ParseTuple(args, "On", &py_lut, &i0)) {
        PyErr_SetString(PyExc_RuntimeError, "Argument parsing problem");
        return NULL;
    }

    if (!PyBytes_Check(py_lut)) {
        PyErr_SetString(PyExc_RuntimeError, "The morphology LUT is not a bytes object");
        return NULL;
    }

    lut_len = PyBytes_Size(py_lut);

    if (lut_len < LUT_SIZE) {
        PyErr_SetString(PyExc_RuntimeError, "The morphology LUT has the wrong size");
        return NULL;
    }

    lut = PyBytes_AsString(py_lut);
    imgin = (Imaging)i0;

    if (imgin->type != IMAGING_TYPE_UINT8 || imgin->bands != 1) {
        PyErr_SetString(PyExc_RuntimeError, "Unsupported image type");
        return NULL;
    }

    inrows = imgin->image8;
    width = imgin->xsize;
    height = imgin->ysize;

    for (row_idx = 1; row_idx < height - 1; row_idx++) {
        UINT8 *inrow = inrows[row_idx];
        UINT8 *prow, *nrow;

        prow = inrows[row_idx - 1];
        nrow = inrows[row_idx + 1];

        for (col_idx = 1; col_idx < width - 1; col_idx++) {
            int cim = col_idx - 1;
            int cip = col_idx + 1;
            unsigned char b0 = prow[cim] & 1;
            unsigned char b1 = prow[col_idx] & 1;
            unsigned char b2 = prow[cip] & 1;

            unsigned char b3 = inrow[cim] & 1;
            unsigned char b4 = inrow[col_idx] & 1;
            unsigned char b5 = inrow[cip] & 1;

            unsigned char b6 = nrow[cim] & 1;
            unsigned char b7 = nrow[col_idx] & 1;
            unsigned char b8 = nrow[cip] & 1;

            int lut_idx =
                (b0 | (b1 << 1) | (b2 << 2) | (b3 << 3) | (b4 << 4) | (b5 << 5) |
                 (b6 << 6) | (b7 << 7) | (b8 << 8));
            if (lut[lut_idx]) {
                PyObject *coordObj = Py_BuildValue("(nn)", col_idx, row_idx);
                PyList_Append(ret, coordObj);
            }
        }
    }

    return ret;
}

/* Return a list of the coordinates of all turned on pixels in an image.
   May be used to extract features after a sequence of MorphOps were applied.
   This is faster than match as only 1x1 lookup is made.
*/
static PyObject *
get_on_pixels(PyObject *self, PyObject *args) {
    Py_ssize_t i0;
    Imaging img;
    UINT8 **rows;
    int row_idx, col_idx;
    int width, height;
    PyObject *ret = PyList_New(0);

    if (!PyArg_ParseTuple(args, "n", &i0)) {
        PyErr_SetString(PyExc_RuntimeError, "Argument parsing problem");

        return NULL;
    }
    img = (Imaging)i0;
    rows = img->image8;
    width = img->xsize;
    height = img->ysize;

    for (row_idx = 0; row_idx < height; row_idx++) {
        UINT8 *row = rows[row_idx];
        for (col_idx = 0; col_idx < width; col_idx++) {
            if (row[col_idx]) {
                PyObject *coordObj = Py_BuildValue("(nn)", col_idx, row_idx);
                PyList_Append(ret, coordObj);
            }
        }
    }
    return ret;
}

static int
setup_module(PyObject *m) {
    PyObject *d = PyModule_GetDict(m);

    PyDict_SetItemString(d, "__version", PyUnicode_FromString("0.1"));

    return 0;
}

static PyMethodDef functions[] = {
    /* Functions */
    {"apply", (PyCFunction)apply, METH_VARARGS, NULL},
    {"get_on_pixels", (PyCFunction)get_on_pixels, METH_VARARGS, NULL},
    {"match", (PyCFunction)match, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}};

PyMODINIT_FUNC
PyInit__imagingmorph(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingmorph",                       /* m_name */
        "A module for doing image morphology", /* m_doc */
        -1,                                    /* m_size */
        functions,                             /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0) {
        return NULL;
    }

    return m;
}
