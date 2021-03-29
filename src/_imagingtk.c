/*
 * The Python Imaging Library.
 *
 * tkinter hooks
 *
 * history:
 * 99-07-26 fl created
 * 99-08-15 fl moved to its own support module
 *
 * Copyright (c) Secret Labs AB 1999.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Python.h"
#include "libImaging/Imaging.h"

#include "Tk/_tkmini.h"

/* must link with Tk/tkImaging.c */
extern void
TkImaging_Init(Tcl_Interp *interp);
extern int
load_tkinter_funcs(void);

/* copied from _tkinter.c (this isn't as bad as it may seem: for new
   versions, we use _tkinter's interpaddr hook instead, and all older
   versions use this structure layout) */

typedef struct {
    PyObject_HEAD Tcl_Interp *interp;
} TkappObject;

static PyObject *
_tkinit(PyObject *self, PyObject *args) {
    Tcl_Interp *interp;

    PyObject *arg;
    int is_interp;
    if (!PyArg_ParseTuple(args, "Oi", &arg, &is_interp)) {
        return NULL;
    }

    if (is_interp) {
        interp = (Tcl_Interp *)PyLong_AsVoidPtr(arg);
    } else {
        TkappObject *app;
        /* Do it the hard way.  This will break if the TkappObject
        layout changes */
        app = (TkappObject *)PyLong_AsVoidPtr(arg);
        interp = app->interp;
    }

    /* This will bomb if interp is invalid... */
    TkImaging_Init(interp);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef functions[] = {
    /* Tkinter interface stuff */
    {"tkinit", (PyCFunction)_tkinit, 1},
    {NULL, NULL} /* sentinel */
};

PyMODINIT_FUNC
PyInit__imagingtk(void) {
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingtk", /* m_name */
        NULL,         /* m_doc */
        -1,           /* m_size */
        functions,    /* m_methods */
    };
    PyObject *m;
    m = PyModule_Create(&module_def);
    return (load_tkinter_funcs() == 0) ? m : NULL;
}
