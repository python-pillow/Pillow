/*
 * The Python Imaging Library.
 *
 * standard memory mapping interface for the Imaging library
 *
 * history:
 * 1998-03-05 fl   added Win32 read mapping
 * 1999-02-06 fl   added "I;16" support
 * 2003-04-21 fl   added PyImaging_MapBuffer primitive
 *
 * Copyright (c) 1998-2003 by Secret Labs AB.
 * Copyright (c) 2003 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */

/*
 * FIXME: should move the memory mapping primitives into libImaging!
 */

#include "Python.h"

#include "libImaging/Imaging.h"

/* compatibility wrappers (defined in _imaging.c) */
extern int
PyImaging_CheckBuffer(PyObject *buffer);
extern int
PyImaging_GetBuffer(PyObject *buffer, Py_buffer *view);

extern PyObject *
PyImagingNew(Imaging im);

/* -------------------------------------------------------------------- */
/* Buffer mapper */

typedef struct ImagingBufferInstance {
    struct ImagingMemoryInstance im;
    PyObject *target;
    Py_buffer view;
} ImagingBufferInstance;

static void
mapping_destroy_buffer(Imaging im) {
    ImagingBufferInstance *buffer = (ImagingBufferInstance *)im;

    PyBuffer_Release(&buffer->view);
    Py_XDECREF(buffer->target);
}

PyObject *
PyImaging_MapBuffer(PyObject *self, PyObject *args) {
    Py_ssize_t y, size;
    Imaging im;

    PyObject *target;
    Py_buffer view;
    char *mode;
    char *codec;
    Py_ssize_t offset;
    int xsize, ysize;
    int stride;
    int ystep;

    if (!PyArg_ParseTuple(
            args,
            "O(ii)sn(sii)",
            &target,
            &xsize,
            &ysize,
            &codec,
            &offset,
            &mode,
            &stride,
            &ystep)) {
        return NULL;
    }

    if (!PyImaging_CheckBuffer(target)) {
        PyErr_SetString(PyExc_TypeError, "expected string or buffer");
        return NULL;
    }

    if (stride <= 0) {
        if (!strcmp(mode, "L") || !strcmp(mode, "P")) {
            stride = xsize;
        } else if (!strncmp(mode, "I;16", 4)) {
            stride = xsize * 2;
        } else {
            stride = xsize * 4;
        }
    }

    if (stride > 0 && ysize > PY_SSIZE_T_MAX / stride) {
        PyErr_SetString(PyExc_MemoryError, "Integer overflow in ysize");
        return NULL;
    }

    size = (Py_ssize_t)ysize * stride;

    if (offset > PY_SSIZE_T_MAX - size) {
        PyErr_SetString(PyExc_MemoryError, "Integer overflow in offset");
        return NULL;
    }

    /* check buffer size */
    if (PyImaging_GetBuffer(target, &view) < 0) {
        return NULL;
    }

    if (view.len < 0) {
        PyErr_SetString(PyExc_ValueError, "buffer has negative size");
        PyBuffer_Release(&view);
        return NULL;
    }
    if (offset + size > view.len) {
        PyErr_SetString(PyExc_ValueError, "buffer is not large enough");
        PyBuffer_Release(&view);
        return NULL;
    }

    im = ImagingNewPrologueSubtype(mode, xsize, ysize, sizeof(ImagingBufferInstance));
    if (!im) {
        PyBuffer_Release(&view);
        return NULL;
    }

    /* setup file pointers */
    if (ystep > 0) {
        for (y = 0; y < ysize; y++) {
            im->image[y] = (char *)view.buf + offset + y * stride;
        }
    } else {
        for (y = 0; y < ysize; y++) {
            im->image[ysize - y - 1] = (char *)view.buf + offset + y * stride;
        }
    }

    im->destroy = mapping_destroy_buffer;

    Py_INCREF(target);
    ((ImagingBufferInstance *)im)->target = target;
    ((ImagingBufferInstance *)im)->view = view;

    return PyImagingNew(im);
}
