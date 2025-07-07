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

static PyObject *
_tkinit(PyObject *self, PyObject *args) {
    Tcl_Interp *interp;

    PyObject *arg;
    if (!PyArg_ParseTuple(args, "O", &arg)) {
        return NULL;
    }

    interp = (Tcl_Interp *)PyLong_AsVoidPtr(arg);

    /* This will bomb if interp is invalid... */
    TkImaging_Init(interp);

    Py_RETURN_NONE;
}

static PyMethodDef functions[] = {
    /* Tkinter interface stuff */
    {"tkinit", (PyCFunction)_tkinit, 1},
    {NULL, NULL} /* sentinel */
};

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, load_tkinter_funcs},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

PyMODINIT_FUNC
PyInit__imagingtk(void) {
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_imagingtk",
        .m_methods = functions,
        .m_slots = slots
    };

    return PyModuleDef_Init(&module_def);
}
