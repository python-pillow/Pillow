/*
 * The Python Imaging Library
 *
 * a simple math add-on for the Python Imaging Library
 *
 * history:
 * 1999-02-15 fl   Created
 * 2005-05-05 fl   Simplified and cleaned up for PIL 1.1.6
 *
 * Copyright (c) 1999-2005 by Secret Labs AB
 * Copyright (c) 2005 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

#include "Python.h"

#include "libImaging/Imaging.h"

#include "math.h"
#include "float.h"

#define MAX_INT32 2147483647.0
#define MIN_INT32 -2147483648.0

#define MATH_FUNC_UNOP_MAGIC "Pillow Math unary func"
#define MATH_FUNC_BINOP_MAGIC "Pillow Math binary func"

#define UNOP(name, op, type)                   \
    void name(Imaging out, Imaging im1) {      \
        int x, y;                              \
        for (y = 0; y < out->ysize; y++) {     \
            type *p0 = (type *)out->image[y];  \
            type *p1 = (type *)im1->image[y];  \
            for (x = 0; x < out->xsize; x++) { \
                *p0 = op(type, *p1);           \
                p0++;                          \
                p1++;                          \
            }                                  \
        }                                      \
    }

#define BINOP(name, op, type)                          \
    void name(Imaging out, Imaging im1, Imaging im2) { \
        int x, y;                                      \
        for (y = 0; y < out->ysize; y++) {             \
            type *p0 = (type *)out->image[y];          \
            type *p1 = (type *)im1->image[y];          \
            type *p2 = (type *)im2->image[y];          \
            for (x = 0; x < out->xsize; x++) {         \
                *p0 = op(type, *p1, *p2);              \
                p0++;                                  \
                p1++;                                  \
                p2++;                                  \
            }                                          \
        }                                              \
    }

#define NEG(type, v1) -(v1)
#define INVERT(type, v1) ~(v1)

#define ADD(type, v1, v2) (v1) + (v2)
#define SUB(type, v1, v2) (v1) - (v2)
#define MUL(type, v1, v2) (v1) * (v2)

#define MIN(type, v1, v2) ((v1) < (v2)) ? (v1) : (v2)
#define MAX(type, v1, v2) ((v1) > (v2)) ? (v1) : (v2)

#define AND(type, v1, v2) (v1) & (v2)
#define OR(type, v1, v2) (v1) | (v2)
#define XOR(type, v1, v2) (v1) ^ (v2)
#define LSHIFT(type, v1, v2) (v1) << (v2)
#define RSHIFT(type, v1, v2) (v1) >> (v2)

#define ABS_I(type, v1) abs((v1))
#define ABS_F(type, v1) fabs((v1))

/* --------------------------------------------------------------------
 * some day, we should add FPE protection mechanisms.  see pyfpe.h for
 * details.
 *
 * PyFPE_START_PROTECT("Error in foobar", return 0)
 * PyFPE_END_PROTECT(result)
 */

#define DIV_I(type, v1, v2) ((v2) != 0) ? (v1) / (v2) : 0
#define DIV_F(type, v1, v2) ((v2) != 0.0F) ? (v1) / (v2) : 0.0F

#define MOD_I(type, v1, v2) ((v2) != 0) ? (v1) % (v2) : 0
#define MOD_F(type, v1, v2) ((v2) != 0.0F) ? fmod((v1), (v2)) : 0.0F

static int
powi(int x, int y) {
    double v = pow(x, y) + 0.5;
    if (errno == EDOM) {
        return 0;
    }
    if (v < MIN_INT32) {
        v = MIN_INT32;
    } else if (v > MAX_INT32) {
        v = MAX_INT32;
    }
    return (int)v;
}

#define POW_I(type, v1, v2) powi(v1, v2)
#define POW_F(type, v1, v2) powf(v1, v2) /* FIXME: EDOM handling */

#define DIFF_I(type, v1, v2) abs((v1) - (v2))
#define DIFF_F(type, v1, v2) fabs((v1) - (v2))

#define EQ(type, v1, v2) (v1) == (v2)
#define NE(type, v1, v2) (v1) != (v2)
#define LT(type, v1, v2) (v1) < (v2)
#define LE(type, v1, v2) (v1) <= (v2)
#define GT(type, v1, v2) (v1) > (v2)
#define GE(type, v1, v2) (v1) >= (v2)

UNOP(abs_I, ABS_I, INT32)
UNOP(neg_I, NEG, INT32)

BINOP(add_I, ADD, INT32)
BINOP(sub_I, SUB, INT32)
BINOP(mul_I, MUL, INT32)
BINOP(div_I, DIV_I, INT32)
BINOP(mod_I, MOD_I, INT32)
BINOP(pow_I, POW_I, INT32)
BINOP(diff_I, DIFF_I, INT32)

UNOP(invert_I, INVERT, INT32)
BINOP(and_I, AND, INT32)
BINOP(or_I, OR, INT32)
BINOP(xor_I, XOR, INT32)
BINOP(lshift_I, LSHIFT, INT32)
BINOP(rshift_I, RSHIFT, INT32)

BINOP(min_I, MIN, INT32)
BINOP(max_I, MAX, INT32)

BINOP(eq_I, EQ, INT32)
BINOP(ne_I, NE, INT32)
BINOP(lt_I, LT, INT32)
BINOP(le_I, LE, INT32)
BINOP(gt_I, GT, INT32)
BINOP(ge_I, GE, INT32)

UNOP(abs_F, ABS_F, FLOAT32)
UNOP(neg_F, NEG, FLOAT32)

BINOP(add_F, ADD, FLOAT32)
BINOP(sub_F, SUB, FLOAT32)
BINOP(mul_F, MUL, FLOAT32)
BINOP(div_F, DIV_F, FLOAT32)
BINOP(mod_F, MOD_F, FLOAT32)
BINOP(pow_F, POW_F, FLOAT32)
BINOP(diff_F, DIFF_F, FLOAT32)

BINOP(min_F, MIN, FLOAT32)
BINOP(max_F, MAX, FLOAT32)

BINOP(eq_F, EQ, FLOAT32)
BINOP(ne_F, NE, FLOAT32)
BINOP(lt_F, LT, FLOAT32)
BINOP(le_F, LE, FLOAT32)
BINOP(gt_F, GT, FLOAT32)
BINOP(ge_F, GE, FLOAT32)

static PyObject *
_unop(PyObject *self, PyObject *args) {
    Imaging out;
    Imaging im1;
    void (*unop)(Imaging, Imaging);

    PyObject *op, *i0, *i1;
    if (!PyArg_ParseTuple(args, "OOO", &op, &i0, &i1)) {
        return NULL;
    }

    if (!PyCapsule_IsValid(op, MATH_FUNC_UNOP_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", MATH_FUNC_UNOP_MAGIC);
        return NULL;
    }
    if (!PyCapsule_IsValid(i0, IMAGING_MAGIC) ||
        !PyCapsule_IsValid(i1, IMAGING_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", IMAGING_MAGIC);
        return NULL;
    }

    unop = (void *)PyCapsule_GetPointer(op, MATH_FUNC_UNOP_MAGIC);
    out = (Imaging)PyCapsule_GetPointer(i0, IMAGING_MAGIC);
    im1 = (Imaging)PyCapsule_GetPointer(i1, IMAGING_MAGIC);

    unop(out, im1);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_binop(PyObject *self, PyObject *args) {
    Imaging out;
    Imaging im1;
    Imaging im2;
    void (*binop)(Imaging, Imaging, Imaging);

    PyObject *op, *i0, *i1, *i2;
    if (!PyArg_ParseTuple(args, "OOOO", &op, &i0, &i1, &i2)) {
        return NULL;
    }

    if (!PyCapsule_IsValid(op, MATH_FUNC_BINOP_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", MATH_FUNC_BINOP_MAGIC);
        return NULL;
    }
    if (!PyCapsule_IsValid(i0, IMAGING_MAGIC) ||
        !PyCapsule_IsValid(i1, IMAGING_MAGIC) ||
        !PyCapsule_IsValid(i2, IMAGING_MAGIC)) {
        PyErr_Format(PyExc_TypeError, "Expected '%s' Capsule", IMAGING_MAGIC);
        return NULL;
    }

    binop = (void *)PyCapsule_GetPointer(op, MATH_FUNC_BINOP_MAGIC);
    out = (Imaging)PyCapsule_GetPointer(i0, IMAGING_MAGIC);
    im1 = (Imaging)PyCapsule_GetPointer(i1, IMAGING_MAGIC);
    im2 = (Imaging)PyCapsule_GetPointer(i2, IMAGING_MAGIC);

    binop(out, im1, im2);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef _functions[] = {
    {"unop", _unop, 1}, {"binop", _binop, 1}, {NULL, NULL}
};

static void
install_unary(PyObject *d, char *name, void *func) {
    PyObject *v = PyCapsule_New(func, MATH_FUNC_UNOP_MAGIC, NULL);
    if (!v || PyDict_SetItemString(d, name, v)) {
        PyErr_Clear();
    }
    Py_XDECREF(v);
}

static void
install_binary(PyObject *d, char *name, void *func) {
    PyObject *v = PyCapsule_New(func, MATH_FUNC_BINOP_MAGIC, NULL);
    if (!v || PyDict_SetItemString(d, name, v)) {
        PyErr_Clear();
    }
    Py_XDECREF(v);
}

static int
setup_module(PyObject *m) {
    PyObject *d = PyModule_GetDict(m);

    install_unary(d, "abs_I", abs_I);
    install_unary(d, "neg_I", neg_I);
    install_binary(d, "add_I", add_I);
    install_binary(d, "sub_I", sub_I);
    install_binary(d, "diff_I", diff_I);
    install_binary(d, "mul_I", mul_I);
    install_binary(d, "div_I", div_I);
    install_binary(d, "mod_I", mod_I);
    install_binary(d, "min_I", min_I);
    install_binary(d, "max_I", max_I);
    install_binary(d, "pow_I", pow_I);

    install_unary(d, "invert_I", invert_I);
    install_binary(d, "and_I", and_I);
    install_binary(d, "or_I", or_I);
    install_binary(d, "xor_I", xor_I);
    install_binary(d, "lshift_I", lshift_I);
    install_binary(d, "rshift_I", rshift_I);

    install_binary(d, "eq_I", eq_I);
    install_binary(d, "ne_I", ne_I);
    install_binary(d, "lt_I", lt_I);
    install_binary(d, "le_I", le_I);
    install_binary(d, "gt_I", gt_I);
    install_binary(d, "ge_I", ge_I);

    install_unary(d, "abs_F", abs_F);
    install_unary(d, "neg_F", neg_F);
    install_binary(d, "add_F", add_F);
    install_binary(d, "sub_F", sub_F);
    install_binary(d, "diff_F", diff_F);
    install_binary(d, "mul_F", mul_F);
    install_binary(d, "div_F", div_F);
    install_binary(d, "mod_F", mod_F);
    install_binary(d, "min_F", min_F);
    install_binary(d, "max_F", max_F);
    install_binary(d, "pow_F", pow_F);

    install_binary(d, "eq_F", eq_F);
    install_binary(d, "ne_F", ne_F);
    install_binary(d, "lt_F", lt_F);
    install_binary(d, "le_F", le_F);
    install_binary(d, "gt_F", gt_F);
    install_binary(d, "ge_F", ge_F);

    return 0;
}

PyMODINIT_FUNC
PyInit__imagingmath(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingmath", /* m_name */
        NULL,           /* m_doc */
        -1,             /* m_size */
        _functions,     /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0) {
        return NULL;
    }

#ifdef Py_GIL_DISABLED
    PyUnstable_Module_SetGIL(m, Py_MOD_GIL_NOT_USED);
#endif

    return m;
}
