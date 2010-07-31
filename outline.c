/*
 * THIS IS WORK IN PROGRESS.
 *
 * The Python Imaging Library.
 *
 * "arrow" outline stuff.  the contents of this module
 * will be merged with the path module and the rest of
 * the arrow graphics  package, but not before PIL 1.1.
 * use at your own risk.
 *
 * history:
 * 99-01-10 fl  Added to PIL (experimental)
 *
 * Copyright (c) Secret Labs AB 1999.
 * Copyright (c) Fredrik Lundh 1999.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Python.h"

#if PY_VERSION_HEX < 0x01060000
#define PyObject_New PyObject_NEW
#define PyObject_Del PyMem_DEL
#endif

#include "Imaging.h"


/* -------------------------------------------------------------------- */
/* Class								*/

typedef struct {
    PyObject_HEAD
    ImagingOutline outline;
} OutlineObject;

staticforward PyTypeObject OutlineType;

#define PyOutline_Check(op) ((op)->ob_type == &OutlineType)

static OutlineObject*
_outline_new(void)
{
    OutlineObject *self;

    self = PyObject_New(OutlineObject, &OutlineType);
    if (self == NULL)
	return NULL;

    self->outline = ImagingOutlineNew();

    return self;
}

static void
_outline_dealloc(OutlineObject* self)
{
    ImagingOutlineDelete(self->outline);
    PyObject_Del(self);
}

ImagingOutline
PyOutline_AsOutline(PyObject* outline)
{
    if (PyOutline_Check(outline))
        return ((OutlineObject*) outline)->outline;

    return NULL;
}


/* -------------------------------------------------------------------- */
/* Factories								*/

PyObject*
PyOutline_Create(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":outline"))
        return NULL;

    return (PyObject*) _outline_new();
}


/* -------------------------------------------------------------------- */
/* Methods								*/

static PyObject*
_outline_move(OutlineObject* self, PyObject* args)
{
    float x0, y0;
    if (!PyArg_ParseTuple(args, "ff", &x0, &y0))
	return NULL;

    ImagingOutlineMove(self->outline, x0, y0);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_outline_line(OutlineObject* self, PyObject* args)
{
    float x1, y1;
    if (!PyArg_ParseTuple(args, "ff", &x1, &y1))
	return NULL;

    ImagingOutlineLine(self->outline, x1, y1);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_outline_curve(OutlineObject* self, PyObject* args)
{
    float x1, y1, x2, y2, x3, y3;
    if (!PyArg_ParseTuple(args, "ffffff", &x1, &y1, &x2, &y2, &x3, &y3))
	return NULL;

    ImagingOutlineCurve(self->outline, x1, y1, x2, y2, x3, y3);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_outline_close(OutlineObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":close"))
        return NULL;

    ImagingOutlineClose(self->outline);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_outline_transform(OutlineObject* self, PyObject* args)
{
    double a[6];
    if (!PyArg_ParseTuple(args, "(dddddd)", a+0, a+1, a+2, a+3, a+4, a+5))
        return NULL;

    ImagingOutlineTransform(self->outline, a);

    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef _outline_methods[] = {
    {"line", (PyCFunction)_outline_line, 1},
    {"curve", (PyCFunction)_outline_curve, 1},
    {"move", (PyCFunction)_outline_move, 1},
    {"close", (PyCFunction)_outline_close, 1},
    {"transform", (PyCFunction)_outline_transform, 1},
    {NULL, NULL} /* sentinel */
};

static PyObject*  
_outline_getattr(OutlineObject* self, char* name)
{
    return Py_FindMethod(_outline_methods, (PyObject*) self, name);
}

statichere PyTypeObject OutlineType = {
	PyObject_HEAD_INIT(NULL)
	0,				/*ob_size*/
	"Outline",			/*tp_name*/
	sizeof(OutlineObject),		/*tp_size*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)_outline_dealloc,	/*tp_dealloc*/
	0,				/*tp_print*/
	(getattrfunc)_outline_getattr,	/*tp_getattr*/
	0				/*tp_setattr*/
};
