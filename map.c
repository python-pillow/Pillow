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

#include "Imaging.h"

#ifdef WIN32
#define WIN32_LEAN_AND_MEAN
#undef INT8
#undef UINT8
#undef INT16
#undef UINT16
#undef INT32
#undef INT64
#undef UINT32
#include "windows.h"
#endif

#include "py3.h"

/* compatibility wrappers (defined in _imaging.c) */
extern int PyImaging_CheckBuffer(PyObject* buffer);
extern int PyImaging_GetBuffer(PyObject* buffer, Py_buffer *view);

/* -------------------------------------------------------------------- */
/* Standard mapper */

typedef struct {
    PyObject_HEAD
    char* base;
    int   size;
    int   offset;
#ifdef WIN32
    HANDLE hFile;
    HANDLE hMap;
#endif
} ImagingMapperObject;

static PyTypeObject ImagingMapperType;

ImagingMapperObject*
PyImaging_MapperNew(const char* filename, int readonly)
{
    ImagingMapperObject *mapper;

    if (PyType_Ready(&ImagingMapperType) < 0)
        return NULL;

    mapper = PyObject_New(ImagingMapperObject, &ImagingMapperType);
    if (mapper == NULL)
        return NULL;

    mapper->base = NULL;
    mapper->size = mapper->offset = 0;

#ifdef WIN32
    mapper->hFile = (HANDLE)-1;
    mapper->hMap  = (HANDLE)-1;

    /* FIXME: currently supports readonly mappings only */
    mapper->hFile = CreateFile(
        filename,
        GENERIC_READ,
        FILE_SHARE_READ,
        NULL, OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL);
    if (mapper->hFile == (HANDLE)-1) {
        PyErr_SetString(PyExc_IOError, "cannot open file");
        PyObject_Del(mapper);
        return NULL;
    }

    mapper->hMap = CreateFileMapping(
        mapper->hFile, NULL,
        PAGE_READONLY,
        0, 0, NULL);
    if (mapper->hMap == (HANDLE)-1) {
        CloseHandle(mapper->hFile);
        PyErr_SetString(PyExc_IOError, "cannot map file");
        PyObject_Del(mapper);
        return NULL;
    }

    mapper->base = (char*) MapViewOfFile(
        mapper->hMap,
        FILE_MAP_READ,
        0, 0, 0);

    mapper->size = GetFileSize(mapper->hFile, 0);
#endif

    return mapper;
}

static void
mapping_dealloc(ImagingMapperObject* mapper)
{
#ifdef WIN32
    if (mapper->base != 0)
        UnmapViewOfFile(mapper->base);
    if (mapper->hMap != (HANDLE)-1)
        CloseHandle(mapper->hMap);
    if (mapper->hFile != (HANDLE)-1)
        CloseHandle(mapper->hFile);
    mapper->base = 0;
    mapper->hMap = mapper->hFile = (HANDLE)-1;
#endif
    PyObject_Del(mapper);
}

/* -------------------------------------------------------------------- */
/* standard file operations */

static PyObject*
mapping_read(ImagingMapperObject* mapper, PyObject* args)
{
    PyObject* buf;

    int size = -1;
    if (!PyArg_ParseTuple(args, "|i", &size))
        return NULL;

    /* check size */
    if (size < 0 || mapper->offset + size > mapper->size)
        size = mapper->size - mapper->offset;
    if (size < 0)
        size = 0;

    buf = PyBytes_FromStringAndSize(NULL, size);
    if (!buf)
        return NULL;

    if (size > 0) {
        memcpy(PyBytes_AsString(buf), mapper->base + mapper->offset, size);
        mapper->offset += size;
    }

    return buf;
}

static PyObject*
mapping_seek(ImagingMapperObject* mapper, PyObject* args)
{
    int offset;
    int whence = 0;
    if (!PyArg_ParseTuple(args, "i|i", &offset, &whence))
        return NULL;

    switch (whence) {
        case 0: /* SEEK_SET */
            mapper->offset = offset;
            break;
        case 1: /* SEEK_CUR */
            mapper->offset += offset;
            break;
        case 2: /* SEEK_END */
            mapper->offset = mapper->size + offset;
            break;
        default:
            /* FIXME: raise ValueError? */
            break;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/* -------------------------------------------------------------------- */
/* map entire image */

extern PyObject*PyImagingNew(Imaging im);

static void
ImagingDestroyMap(Imaging im)
{
    return; /* nothing to do! */
}

static PyObject*
mapping_readimage(ImagingMapperObject* mapper, PyObject* args)
{
    int y, size;
    Imaging im;

    char* mode;
    int xsize;
    int ysize;
    int stride;
    int orientation;
    if (!PyArg_ParseTuple(args, "s(ii)ii", &mode, &xsize, &ysize,
                          &stride, &orientation))
        return NULL;

    if (stride <= 0) {
        /* FIXME: maybe we should call ImagingNewPrologue instead */
        if (!strcmp(mode, "L") || !strcmp(mode, "P"))
            stride = xsize;
        else if (!strcmp(mode, "I;16") || !strcmp(mode, "I;16B"))
            stride = xsize * 2;
        else
            stride = xsize * 4;
    }

    size = ysize * stride;

    if (mapper->offset + size > mapper->size) {
        PyErr_SetString(PyExc_IOError, "image file truncated");
        return NULL;
    }

    im = ImagingNewPrologue(mode, xsize, ysize);
    if (!im)
        return NULL;

    /* setup file pointers */
    if (orientation > 0)
        for (y = 0; y < ysize; y++)
            im->image[y] = mapper->base + mapper->offset + y * stride;
    else
        for (y = 0; y < ysize; y++)
            im->image[ysize-y-1] = mapper->base + mapper->offset + y * stride;

    im->destroy = ImagingDestroyMap;

    if (!ImagingNewEpilogue(im))
        return NULL;

    mapper->offset += size;

    return PyImagingNew(im);
}

static struct PyMethodDef methods[] = {
    /* standard file interface */
    {"read", (PyCFunction)mapping_read, 1},
    {"seek", (PyCFunction)mapping_seek, 1},
    /* extensions */
    {"readimage", (PyCFunction)mapping_readimage, 1},
    {NULL, NULL} /* sentinel */
};

static PyTypeObject ImagingMapperType = {
        PyVarObject_HEAD_INIT(NULL, 0)
        "ImagingMapper",                /*tp_name*/
        sizeof(ImagingMapperObject),    /*tp_size*/
        0,                              /*tp_itemsize*/
        /* methods */
        (destructor)mapping_dealloc,    /*tp_dealloc*/
        0,                              /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number */
    0,                          /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    methods,                    /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
};

PyObject*
PyImaging_Mapper(PyObject* self, PyObject* args)
{
    char* filename;
    if (!PyArg_ParseTuple(args, "s", &filename))
        return NULL;

    return (PyObject*) PyImaging_MapperNew(filename, 1);
}

/* -------------------------------------------------------------------- */
/* Buffer mapper */

typedef struct ImagingBufferInstance {
    struct ImagingMemoryInstance im;
    PyObject* target;
    Py_buffer view;
} ImagingBufferInstance;

static void
mapping_destroy_buffer(Imaging im)
{
    ImagingBufferInstance* buffer = (ImagingBufferInstance*) im;

    PyBuffer_Release(&buffer->view);
    Py_XDECREF(buffer->target);
}

PyObject*
PyImaging_MapBuffer(PyObject* self, PyObject* args)
{
    Py_ssize_t y, size;
    Imaging im;

    PyObject* target;
    Py_buffer view;
    char* mode;
    char* codec;
    PyObject* bbox;
    Py_ssize_t offset;
    int xsize, ysize;
    int stride;
    int ystep;

    if (!PyArg_ParseTuple(args, "O(ii)sOn(sii)", &target, &xsize, &ysize,
                          &codec, &bbox, &offset, &mode, &stride, &ystep))
        return NULL;

    if (!PyImaging_CheckBuffer(target)) {
        PyErr_SetString(PyExc_TypeError, "expected string or buffer");
        return NULL;
    }

    if (stride <= 0) {
        if (!strcmp(mode, "L") || !strcmp(mode, "P"))
            stride = xsize;
        else if (!strncmp(mode, "I;16", 4))
            stride = xsize * 2;
        else
            stride = xsize * 4;
    }

    size = (Py_ssize_t) ysize * stride;

    /* check buffer size */
    if (PyImaging_GetBuffer(target, &view) < 0)
        return NULL;

    if (view.len < 0) {
        PyErr_SetString(PyExc_ValueError, "buffer has negative size");
        return NULL;
    }
    if (offset + size > view.len) {
        PyErr_SetString(PyExc_ValueError, "buffer is not large enough");
        return NULL;
    }

    im = ImagingNewPrologueSubtype(
        mode, xsize, ysize, sizeof(ImagingBufferInstance)
        );
    if (!im)
        return NULL;

    /* setup file pointers */
    if (ystep > 0)
        for (y = 0; y < ysize; y++)
            im->image[y] = (char*)view.buf + offset + y * stride;
    else
        for (y = 0; y < ysize; y++)
            im->image[ysize-y-1] = (char*)view.buf + offset + y * stride;

    im->destroy = mapping_destroy_buffer;

    Py_INCREF(target);
    ((ImagingBufferInstance*) im)->target = target;
    ((ImagingBufferInstance*) im)->view = view;

    if (!ImagingNewEpilogue(im))
        return NULL;

    return PyImagingNew(im);
}

