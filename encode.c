/*
 * The Python Imaging Library.
 *
 * standard encoder interfaces for the Imaging library
 *
 * History:
 * 1996-04-19 fl   Based on decoders.c
 * 1996-05-12 fl   Compile cleanly as C++
 * 1996-12-30 fl   Plugged potential memory leak for tiled images
 * 1997-01-03 fl   Added GIF encoder
 * 1997-01-05 fl   Plugged encoder buffer leaks
 * 1997-01-11 fl   Added encode_to_file method
 * 1998-03-09 fl   Added mode/rawmode argument to encoders
 * 1998-07-09 fl   Added interlace argument to GIF encoder
 * 1999-02-07 fl   Added PCX encoder
 *
 * Copyright (c) 1997-2001 by Secret Labs AB
 * Copyright (c) 1996-1997 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

/* FIXME: make these pluggable! */

#include "Python.h"

#include "Imaging.h"
#include "py3.h"
#include "Gif.h"

#ifdef HAVE_UNISTD_H
#include <unistd.h> /* write */
#endif

/* -------------------------------------------------------------------- */
/* Common                                                               */
/* -------------------------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    int (*encode)(Imaging im, ImagingCodecState state,
                  UINT8* buffer, int bytes);
    int (*cleanup)(ImagingCodecState state);
    struct ImagingCodecStateInstance state;
    Imaging im;
    PyObject* lock;
    int pushes_fd;
} ImagingEncoderObject;

static PyTypeObject ImagingEncoderType;

static ImagingEncoderObject*
PyImaging_EncoderNew(int contextsize)
{
    ImagingEncoderObject *encoder;
    void *context;

    if(PyType_Ready(&ImagingEncoderType) < 0)
        return NULL;

    encoder = PyObject_New(ImagingEncoderObject, &ImagingEncoderType);
    if (encoder == NULL)
        return NULL;

    /* Clear the encoder state */
    memset(&encoder->state, 0, sizeof(encoder->state));

    /* Allocate encoder context */
    if (contextsize > 0) {
        context = (void*) calloc(1, contextsize);
        if (!context) {
            Py_DECREF(encoder);
            (void) PyErr_NoMemory();
            return NULL;
        }
    } else
        context = 0;

    /* Initialize encoder context */
    encoder->state.context = context;

    /* Most encoders don't need this */
    encoder->cleanup = NULL;

    /* Target image */
    encoder->lock = NULL;
    encoder->im = NULL;
    encoder->pushes_fd = 0;

    return encoder;
}

static void
_dealloc(ImagingEncoderObject* encoder)
{
    if (encoder->cleanup)
        encoder->cleanup(&encoder->state);
    free(encoder->state.buffer);
    free(encoder->state.context);
    Py_XDECREF(encoder->lock);
    Py_XDECREF(encoder->state.fd);
    PyObject_Del(encoder);
}

static PyObject*
_encode_cleanup(ImagingEncoderObject* encoder, PyObject* args)
{
    int status = 0;

    if (encoder->cleanup){
        status = encoder->cleanup(&encoder->state);
    }

    return Py_BuildValue("i", status);
}

static PyObject*
_encode(ImagingEncoderObject* encoder, PyObject* args)
{
    PyObject* buf;
    PyObject* result;
    int status;

    /* Encode to a Python string (allocated by this method) */

    int bufsize = 16384;

    if (!PyArg_ParseTuple(args, "|i", &bufsize))
        return NULL;

    buf = PyBytes_FromStringAndSize(NULL, bufsize);
    if (!buf)
        return NULL;

    status = encoder->encode(encoder->im, &encoder->state,
                             (UINT8*) PyBytes_AsString(buf), bufsize);

    /* adjust string length to avoid slicing in encoder */
    if (_PyBytes_Resize(&buf, (status > 0) ? status : 0) < 0)
        return NULL;

    result = Py_BuildValue("iiO", status, encoder->state.errcode, buf);

    Py_DECREF(buf); /* must release buffer!!! */

    return result;
}

static PyObject*
_encode_to_pyfd(ImagingEncoderObject* encoder, PyObject* args)
{

    PyObject *result;
    int status;

    if (!encoder->pushes_fd) {
        // UNDONE, appropriate errcode???
        result = Py_BuildValue("ii", 0, IMAGING_CODEC_CONFIG);;
        return result;
    }

    status = encoder->encode(encoder->im, &encoder->state,
                             (UINT8*) NULL, 0);

    result = Py_BuildValue("ii", status, encoder->state.errcode);

    return result;
}

static PyObject*
_encode_to_file(ImagingEncoderObject* encoder, PyObject* args)
{
    UINT8* buf;
    int status;
    ImagingSectionCookie cookie;

    /* Encode to a file handle */

    int fh;
    int bufsize = 16384;

    if (!PyArg_ParseTuple(args, "i|i", &fh, &bufsize))
        return NULL;

    /* Allocate an encoder buffer */
    /* malloc check ok, either constant int, or checked by PyArg_ParseTuple */
    buf = (UINT8*) malloc(bufsize);
    if (!buf)
        return PyErr_NoMemory();

    ImagingSectionEnter(&cookie);

    do {

        /* This replaces the inner loop in the ImageFile _save
           function. */

        status = encoder->encode(encoder->im, &encoder->state, buf, bufsize);

        if (status > 0)
            if (write(fh, buf, status) < 0) {
                ImagingSectionLeave(&cookie);
                free(buf);
                return PyErr_SetFromErrno(PyExc_IOError);
            }

    } while (encoder->state.errcode == 0);

    ImagingSectionLeave(&cookie);

    free(buf);

    return Py_BuildValue("i", encoder->state.errcode);
}

extern Imaging PyImaging_AsImaging(PyObject *op);

static PyObject*
_setimage(ImagingEncoderObject* encoder, PyObject* args)
{
    PyObject* op;
    Imaging im;
    ImagingCodecState state;
    int x0, y0, x1, y1;

    /* Define where image data should be stored */

    x0 = y0 = x1 = y1 = 0;

    /* FIXME: should publish the ImagingType descriptor */
    if (!PyArg_ParseTuple(args, "O|(iiii)", &op, &x0, &y0, &x1, &y1))
        return NULL;
    im = PyImaging_AsImaging(op);
    if (!im)
        return NULL;

    encoder->im = im;

    state = &encoder->state;

    if (x0 == 0 && x1 == 0) {
        state->xsize = im->xsize;
        state->ysize = im->ysize;
    } else {
        state->xoff = x0;
        state->yoff = y0;
        state->xsize = x1 - x0;
        state->ysize = y1 - y0;
    }

    if (state->xsize <= 0 ||
        state->xsize + state->xoff > im->xsize ||
        state->ysize <= 0 ||
        state->ysize + state->yoff > im->ysize) {
        PyErr_SetString(PyExc_SystemError, "tile cannot extend outside image");
        return NULL;
    }

    /* Allocate memory buffer (if bits field is set) */
    if (state->bits > 0) {
        if (state->xsize > ((INT_MAX / state->bits)-7)) {
            return PyErr_NoMemory();
        }
        state->bytes = (state->bits * state->xsize+7)/8;
        /* malloc check ok, overflow checked above */
        state->buffer = (UINT8*) malloc(state->bytes);
        if (!state->buffer)
            return PyErr_NoMemory();
    }

    /* Keep a reference to the image object, to make sure it doesn't
       go away before we do */
    Py_INCREF(op);
    Py_XDECREF(encoder->lock);
    encoder->lock = op;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_setfd(ImagingEncoderObject* encoder, PyObject* args)
{
    PyObject* fd;
    ImagingCodecState state;

    if (!PyArg_ParseTuple(args, "O", &fd))
        return NULL;

    state = &encoder->state;

    Py_XINCREF(fd);
    state->fd = fd;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_get_pushes_fd(ImagingEncoderObject *encoder)
{
    return PyBool_FromLong(encoder->pushes_fd);
}

static struct PyMethodDef methods[] = {
    {"encode", (PyCFunction)_encode, 1},
    {"cleanup", (PyCFunction)_encode_cleanup, 1},
    {"encode_to_file", (PyCFunction)_encode_to_file, 1},
    {"encode_to_pyfd", (PyCFunction)_encode_to_pyfd, 1},
    {"setimage", (PyCFunction)_setimage, 1},
    {"setfd", (PyCFunction)_setfd, 1},
    {NULL, NULL} /* sentinel */
};

static struct PyGetSetDef getseters[] = {
   {"pushes_fd", (getter)_get_pushes_fd, NULL,
     "True if this decoder expects to push directly to self.fd",
     NULL},
    {NULL, NULL, NULL, NULL, NULL} /* sentinel */
};

static PyTypeObject ImagingEncoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ImagingEncoder",               /*tp_name*/
    sizeof(ImagingEncoderObject),   /*tp_size*/
    0,                              /*tp_itemsize*/
    /* methods */
    (destructor)_dealloc,           /*tp_dealloc*/
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
    getseters,                  /*tp_getset*/
};

/* -------------------------------------------------------------------- */

int
get_packer(ImagingEncoderObject* encoder, const char* mode,
           const char* rawmode)
{
    int bits;
    ImagingShuffler pack;

    pack = ImagingFindPacker(mode, rawmode, &bits);
    if (!pack) {
        Py_DECREF(encoder);
        PyErr_Format(PyExc_ValueError, "No packer found from %s to %s", mode, rawmode);
        return -1;
    }

    encoder->state.shuffle = pack;
    encoder->state.bits = bits;

    return 0;
}


/* -------------------------------------------------------------------- */
/* EPS                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_EpsEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    encoder = PyImaging_EncoderNew(0);
    if (encoder == NULL)
        return NULL;

    encoder->encode = ImagingEpsEncode;

    return (PyObject*) encoder;
}


/* -------------------------------------------------------------------- */
/* GIF                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_GifEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    char *mode;
    char *rawmode;
    int bits = 8;
    int interlace = 0;
    if (!PyArg_ParseTuple(args, "ss|ii", &mode, &rawmode, &bits, &interlace))
        return NULL;

    encoder = PyImaging_EncoderNew(sizeof(GIFENCODERSTATE));
    if (encoder == NULL)
        return NULL;

    if (get_packer(encoder, mode, rawmode) < 0)
        return NULL;

    encoder->encode = ImagingGifEncode;

    ((GIFENCODERSTATE*)encoder->state.context)->bits = bits;
    ((GIFENCODERSTATE*)encoder->state.context)->interlace = interlace;

    return (PyObject*) encoder;
}


/* -------------------------------------------------------------------- */
/* PCX                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_PcxEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    char *mode;
    char *rawmode;
    int bits = 8;

    if (!PyArg_ParseTuple(args, "ss|ii", &mode, &rawmode, &bits)) {
        return NULL;
    }

    encoder = PyImaging_EncoderNew(0);
    if (encoder == NULL) {
        return NULL;
    }

    if (get_packer(encoder, mode, rawmode) < 0) {
        return NULL;
    }

    encoder->encode = ImagingPcxEncode;

    return (PyObject*) encoder;
}


/* -------------------------------------------------------------------- */
/* RAW                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_RawEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    char *mode;
    char *rawmode;
    int stride = 0;
    int ystep = 1;

    if (!PyArg_ParseTuple(args, "ss|ii", &mode, &rawmode, &stride, &ystep))
        return NULL;

    encoder = PyImaging_EncoderNew(0);
    if (encoder == NULL)
        return NULL;

    if (get_packer(encoder, mode, rawmode) < 0)
        return NULL;

    encoder->encode = ImagingRawEncode;

    encoder->state.ystep = ystep;
    encoder->state.count = stride;

    return (PyObject*) encoder;
}


/* -------------------------------------------------------------------- */
/* XBM                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_XbmEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    encoder = PyImaging_EncoderNew(0);
    if (encoder == NULL)
        return NULL;

    if (get_packer(encoder, "1", "1;R") < 0)
        return NULL;

    encoder->encode = ImagingXbmEncode;

    return (PyObject*) encoder;
}


/* -------------------------------------------------------------------- */
/* ZIP                                                                  */
/* -------------------------------------------------------------------- */

#ifdef HAVE_LIBZ

#include "Zip.h"

PyObject*
PyImaging_ZipEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    char* mode;
    char* rawmode;
    int optimize = 0;
    int compress_level = -1;
    int compress_type = -1;
    char* dictionary = NULL;
    int dictionary_size = 0;
    if (!PyArg_ParseTuple(args, "ss|iii"PY_ARG_BYTES_LENGTH, &mode, &rawmode,
                          &optimize,
                          &compress_level, &compress_type,
                          &dictionary, &dictionary_size))
        return NULL;

    /* Copy to avoid referencing Python's memory */
    if (dictionary && dictionary_size > 0) {
        /* malloc check ok, size comes from PyArg_ParseTuple */
        char* p = malloc(dictionary_size);
        if (!p)
            return PyErr_NoMemory();
        memcpy(p, dictionary, dictionary_size);
        dictionary = p;
    } else
        dictionary = NULL;

    encoder = PyImaging_EncoderNew(sizeof(ZIPSTATE));
    if (encoder == NULL)
        return NULL;

    if (get_packer(encoder, mode, rawmode) < 0)
        return NULL;

    encoder->encode = ImagingZipEncode;
    encoder->cleanup = ImagingZipEncodeCleanup;

    if (rawmode[0] == 'P')
        /* disable filtering */
        ((ZIPSTATE*)encoder->state.context)->mode = ZIP_PNG_PALETTE;

    ((ZIPSTATE*)encoder->state.context)->optimize = optimize;
    ((ZIPSTATE*)encoder->state.context)->compress_level = compress_level;
    ((ZIPSTATE*)encoder->state.context)->compress_type = compress_type;
    ((ZIPSTATE*)encoder->state.context)->dictionary = dictionary;
    ((ZIPSTATE*)encoder->state.context)->dictionary_size = dictionary_size;

    return (PyObject*) encoder;
}
#endif


/* -------------------------------------------------------------------- */
/* JPEG                                                                 */
/* -------------------------------------------------------------------- */

#ifdef HAVE_LIBJPEG

/* We better define this encoder last in this file, so the following
   undef's won't mess things up for the Imaging library proper. */

#undef  HAVE_PROTOTYPES
#undef  HAVE_STDDEF_H
#undef  HAVE_STDLIB_H
#undef  UINT8
#undef  UINT16
#undef  UINT32
#undef  INT8
#undef  INT16
#undef  INT32

#include "Jpeg.h"

static unsigned int* get_qtables_arrays(PyObject* qtables, int* qtablesLen) {
    PyObject* tables;
    PyObject* table;
    PyObject* table_data;
    int i, j, num_tables;
    unsigned int *qarrays;

    if ((qtables ==  NULL) || (qtables == Py_None)) {
        return NULL;
    }

    if (!PySequence_Check(qtables)) {
        PyErr_SetString(PyExc_ValueError, "Invalid quantization tables");
        return NULL;
    }

    tables = PySequence_Fast(qtables, "expected a sequence");
    num_tables = PySequence_Size(qtables);
    if (num_tables < 1 || num_tables > NUM_QUANT_TBLS) {
        PyErr_SetString(PyExc_ValueError,
            "Not a valid number of quantization tables. Should be between 1 and 4.");
        Py_DECREF(tables);
        return NULL;
    }
    /* malloc check ok, num_tables <4, DCTSIZE2 == 64 from jpeglib.h */
    qarrays = (unsigned int*) malloc(num_tables * DCTSIZE2 * sizeof(unsigned int));
    if (!qarrays) {
        Py_DECREF(tables);
        PyErr_NoMemory();
        return NULL;
    }
    for (i = 0; i < num_tables; i++) {
        table = PySequence_Fast_GET_ITEM(tables, i);
        if (!PySequence_Check(table)) {
            PyErr_SetString(PyExc_ValueError, "Invalid quantization tables");
            goto JPEG_QTABLES_ERR;
        }
        if (PySequence_Size(table) != DCTSIZE2) {
            PyErr_SetString(PyExc_ValueError, "Invalid quantization table size");
            goto JPEG_QTABLES_ERR;
        }
        table_data = PySequence_Fast(table, "expected a sequence");
        for (j = 0; j < DCTSIZE2; j++) {
            qarrays[i * DCTSIZE2 + j] = PyInt_AS_LONG(PySequence_Fast_GET_ITEM(table_data, j));
        }
        Py_DECREF(table_data);
    }

    *qtablesLen = num_tables;

JPEG_QTABLES_ERR:
    Py_DECREF(tables);  // Run on both error and not error
    if (PyErr_Occurred()) {
        free(qarrays);
        qarrays = NULL;
        return NULL;
    }

    return qarrays;
}

PyObject*
PyImaging_JpegEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    char *mode;
    char *rawmode;
    int quality = 0;
    int progressive = 0;
    int smooth = 0;
    int optimize = 0;
    int streamtype = 0; /* 0=interchange, 1=tables only, 2=image only */
    int xdpi = 0, ydpi = 0;
    int subsampling = -1; /* -1=default, 0=none, 1=medium, 2=high */
    PyObject* qtables=NULL;
    unsigned int *qarrays = NULL;
    int qtablesLen = 0;
    char* extra = NULL;
    int extra_size;
    char* rawExif = NULL;
    int rawExifLen = 0;

    if (!PyArg_ParseTuple(args, "ss|iiiiiiiiO"PY_ARG_BYTES_LENGTH""PY_ARG_BYTES_LENGTH,
                          &mode, &rawmode, &quality,
                          &progressive, &smooth, &optimize, &streamtype,
                          &xdpi, &ydpi, &subsampling, &qtables, &extra, &extra_size,
                          &rawExif, &rawExifLen))
        return NULL;

    encoder = PyImaging_EncoderNew(sizeof(JPEGENCODERSTATE));
    if (encoder == NULL)
        return NULL;

    if (get_packer(encoder, mode, rawmode) < 0)
        return NULL;

    // Freed in JpegEncode, Case 5
    qarrays = get_qtables_arrays(qtables, &qtablesLen);

    if (extra && extra_size > 0) {
        /* malloc check ok, length is from python parsearg */
        char* p = malloc(extra_size); // Freed in JpegEncode, Case 5
        if (!p)
            return PyErr_NoMemory();
        memcpy(p, extra, extra_size);
        extra = p;
    } else
        extra = NULL;

    if (rawExif && rawExifLen > 0) {
        /* malloc check ok, length is from python parsearg */
        char* pp = malloc(rawExifLen); // Freed in JpegEncode, Case 5
        if (!pp)
            return PyErr_NoMemory();
        memcpy(pp, rawExif, rawExifLen);
        rawExif = pp;
    } else
        rawExif = NULL;

    encoder->encode = ImagingJpegEncode;

    ((JPEGENCODERSTATE*)encoder->state.context)->quality = quality;
    ((JPEGENCODERSTATE*)encoder->state.context)->qtables = qarrays;
    ((JPEGENCODERSTATE*)encoder->state.context)->qtablesLen = qtablesLen;
    ((JPEGENCODERSTATE*)encoder->state.context)->subsampling = subsampling;
    ((JPEGENCODERSTATE*)encoder->state.context)->progressive = progressive;
    ((JPEGENCODERSTATE*)encoder->state.context)->smooth = smooth;
    ((JPEGENCODERSTATE*)encoder->state.context)->optimize = optimize;
    ((JPEGENCODERSTATE*)encoder->state.context)->streamtype = streamtype;
    ((JPEGENCODERSTATE*)encoder->state.context)->xdpi = xdpi;
    ((JPEGENCODERSTATE*)encoder->state.context)->ydpi = ydpi;
    ((JPEGENCODERSTATE*)encoder->state.context)->extra = extra;
    ((JPEGENCODERSTATE*)encoder->state.context)->extra_size = extra_size;
    ((JPEGENCODERSTATE*)encoder->state.context)->rawExif = rawExif;
    ((JPEGENCODERSTATE*)encoder->state.context)->rawExifLen = rawExifLen;

    return (PyObject*) encoder;
}

#endif

/* -------------------------------------------------------------------- */
/* LibTiff                                                              */
/* -------------------------------------------------------------------- */

#ifdef HAVE_LIBTIFF

#include "TiffDecode.h"

#include <string.h>

PyObject*
PyImaging_LibTiffEncoderNew(PyObject* self, PyObject* args)
{
    ImagingEncoderObject* encoder;

    char* mode;
    char* rawmode;
    char* compname;
    char* filename;
    int fp;

    PyObject *dir;
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    int status;

    Py_ssize_t d_size;
    PyObject *keys, *values;


    if (! PyArg_ParseTuple(args, "sssisO", &mode, &rawmode, &compname, &fp, &filename, &dir)) {
        return NULL;
    }

    if (!PyDict_Check(dir)) {
        PyErr_SetString(PyExc_ValueError, "Invalid Dictionary");
        return NULL;
    } else {
        d_size = PyDict_Size(dir);
        TRACE(("dict size: %d\n", (int)d_size));
        keys = PyDict_Keys(dir);
        values = PyDict_Values(dir);
        for (pos=0;pos<d_size;pos++){
            TRACE(("  key: %d\n", (int)PyInt_AsLong(PyList_GetItem(keys,pos))));
        }
        pos = 0;
    }

    TRACE(("new tiff encoder %s fp: %d, filename: %s \n", compname, fp, filename));

    encoder = PyImaging_EncoderNew(sizeof(TIFFSTATE));
    if (encoder == NULL)
        return NULL;

    if (get_packer(encoder, mode, rawmode) < 0)
        return NULL;

    if (! ImagingLibTiffEncodeInit(&encoder->state, filename, fp)) {
        Py_DECREF(encoder);
        PyErr_SetString(PyExc_RuntimeError, "tiff codec initialization failed");
        return NULL;
    }

    for (pos = 0; pos < d_size; pos++) {
        key = PyList_GetItem(keys, pos);
        value = PyList_GetItem(values, pos);
        status = 0;
        TRACE(("Attempting to set key: %d\n", (int)PyInt_AsLong(key)));
        if (PyInt_Check(value)) {
            TRACE(("Setting from Int: %d %ld \n", (int)PyInt_AsLong(key),PyInt_AsLong(value)));
            status = ImagingLibTiffSetField(&encoder->state,
                                            (ttag_t) PyInt_AsLong(key),
                                            PyInt_AsLong(value));
        } else if (PyFloat_Check(value)) {
            TRACE(("Setting from Float: %d, %f \n", (int)PyInt_AsLong(key),PyFloat_AsDouble(value)));
            status = ImagingLibTiffSetField(&encoder->state,
                                            (ttag_t) PyInt_AsLong(key),
                                            (float)PyFloat_AsDouble(value));
        } else if (PyBytes_Check(value)) {
            TRACE(("Setting from Bytes: %d, %s \n", (int)PyInt_AsLong(key),PyBytes_AsString(value)));
            status = ImagingLibTiffSetField(&encoder->state,
                                            (ttag_t) PyInt_AsLong(key),
                                            PyBytes_AsString(value));
        } else if (PyTuple_Check(value)) {
            Py_ssize_t len,i;
            float *floatav;
            int *intav;
            TRACE(("Setting from Tuple: %d \n", (int)PyInt_AsLong(key)));
            len = PyTuple_Size(value);
            if (len) {
                if (PyInt_Check(PyTuple_GetItem(value,0))) {
                    TRACE((" %d elements, setting as ints \n", (int)len));
                    /* malloc check ok, calloc checks for overflow */
                    intav = calloc(len, sizeof(int));
                    if (intav) {
                        for (i=0;i<len;i++) {
                            intav[i] = (int)PyInt_AsLong(PyTuple_GetItem(value,i));
                        }
                        status = ImagingLibTiffSetField(&encoder->state,
                                                        (ttag_t) PyInt_AsLong(key),
                                                        len, intav);
                        free(intav);
                    }
                } else if (PyFloat_Check(PyTuple_GetItem(value,0))) {
                    TRACE((" %d elements, setting as floats \n", (int)len));
                    /* malloc check ok, calloc checks for overflow */
                    floatav = calloc(len, sizeof(float));
                    if (floatav) {
                        for (i=0;i<len;i++) {
                            floatav[i] = (float)PyFloat_AsDouble(PyTuple_GetItem(value,i));
                        }
                        status = ImagingLibTiffSetField(&encoder->state,
                                                        (ttag_t) PyInt_AsLong(key),
                                                        len, floatav);
                        free(floatav);
                    }
                } else {
                    TRACE(("Unhandled type in tuple for key %d : %s \n",
                           (int)PyInt_AsLong(key),
                           PyBytes_AsString(PyObject_Str(value))));
                }
            }
        } else {
            TRACE(("Unhandled type for key %d : %s \n",
                   (int)PyInt_AsLong(key),
                   PyBytes_AsString(PyObject_Str(value))));
        }
        if (!status) {
            TRACE(("Error setting Field\n"));
            Py_DECREF(encoder);
            PyErr_SetString(PyExc_RuntimeError, "Error setting from dictionary");
            return NULL;
        }
    }

    encoder->encode  = ImagingLibTiffEncode;

    return (PyObject*) encoder;
}

#endif

/* -------------------------------------------------------------------- */
/* JPEG	2000								*/
/* -------------------------------------------------------------------- */

#ifdef HAVE_OPENJPEG

#include "Jpeg2K.h"

static void
j2k_decode_coord_tuple(PyObject *tuple, int *x, int *y)
{
    *x = *y = 0;

    if (tuple && PyTuple_Check(tuple) && PyTuple_GET_SIZE(tuple) == 2) {
        *x = (int)PyInt_AsLong(PyTuple_GET_ITEM(tuple, 0));
        *y = (int)PyInt_AsLong(PyTuple_GET_ITEM(tuple, 1));

        if (*x < 0)
            *x = 0;
        if (*y < 0)
            *y = 0;
    }
}

PyObject*
PyImaging_Jpeg2KEncoderNew(PyObject *self, PyObject *args)
{
    ImagingEncoderObject *encoder;
    JPEG2KENCODESTATE *context;

    char *mode;
    char *format;
    OPJ_CODEC_FORMAT codec_format;
    PyObject *offset = NULL, *tile_offset = NULL, *tile_size = NULL;
    char *quality_mode = "rates";
    PyObject *quality_layers = NULL;
    int num_resolutions = 0;
    PyObject *cblk_size = NULL, *precinct_size = NULL;
    PyObject *irreversible = NULL;
    char *progression = "LRCP";
    OPJ_PROG_ORDER prog_order;
    char *cinema_mode = "no";
    OPJ_CINEMA_MODE cine_mode;
    int fd = -1;

    if (!PyArg_ParseTuple(args, "ss|OOOsOIOOOssi", &mode, &format,
                          &offset, &tile_offset, &tile_size,
                          &quality_mode, &quality_layers, &num_resolutions,
                          &cblk_size, &precinct_size,
                          &irreversible, &progression, &cinema_mode,
                          &fd))
        return NULL;

    if (strcmp (format, "j2k") == 0)
        codec_format = OPJ_CODEC_J2K;
    else if (strcmp (format, "jpt") == 0)
        codec_format = OPJ_CODEC_JPT;
    else if (strcmp (format, "jp2") == 0)
        codec_format = OPJ_CODEC_JP2;
    else
        return NULL;

    if (strcmp(progression, "LRCP") == 0)
        prog_order = OPJ_LRCP;
    else if (strcmp(progression, "RLCP") == 0)
        prog_order = OPJ_RLCP;
    else if (strcmp(progression, "RPCL") == 0)
        prog_order = OPJ_RPCL;
    else if (strcmp(progression, "PCRL") == 0)
        prog_order = OPJ_PCRL;
    else if (strcmp(progression, "CPRL") == 0)
        prog_order = OPJ_CPRL;
    else
        return NULL;

    if (strcmp(cinema_mode, "no") == 0)
        cine_mode = OPJ_OFF;
    else if (strcmp(cinema_mode, "cinema2k-24") == 0)
        cine_mode = OPJ_CINEMA2K_24;
    else if (strcmp(cinema_mode, "cinema2k-48") == 0)
        cine_mode = OPJ_CINEMA2K_48;
    else if (strcmp(cinema_mode, "cinema4k-24") == 0)
        cine_mode = OPJ_CINEMA4K_24;
    else
        return NULL;

    encoder = PyImaging_EncoderNew(sizeof(JPEG2KENCODESTATE));
    if (!encoder)
        return NULL;

    encoder->encode = ImagingJpeg2KEncode;
    encoder->cleanup = ImagingJpeg2KEncodeCleanup;
    encoder->pushes_fd = 1;

    context = (JPEG2KENCODESTATE *)encoder->state.context;

    context->fd = fd;
    context->format = codec_format;
    context->offset_x = context->offset_y = 0;


    j2k_decode_coord_tuple(offset, &context->offset_x, &context->offset_y);
    j2k_decode_coord_tuple(tile_offset,
                           &context->tile_offset_x,
                           &context->tile_offset_y);
    j2k_decode_coord_tuple(tile_size,
                           &context->tile_size_x,
                           &context->tile_size_y);

    /* Error on illegal tile offsets */
    if (context->tile_size_x && context->tile_size_y) {
        if (context->tile_offset_x <= context->offset_x - context->tile_size_x
            || context->tile_offset_y <= context->offset_y - context->tile_size_y) {
            PyErr_SetString(PyExc_ValueError,
                            "JPEG 2000 tile offset too small; top left tile must "
                            "intersect image area");
        }

        if (context->tile_offset_x > context->offset_x
            || context->tile_offset_y > context->offset_y) {
            PyErr_SetString(PyExc_ValueError,
                            "JPEG 2000 tile offset too large to cover image area");
            Py_DECREF(encoder);
            return NULL;
        }
    }

    if (quality_layers && PySequence_Check(quality_layers)) {
        context->quality_is_in_db = strcmp (quality_mode, "dB") == 0;
        context->quality_layers = quality_layers;
        Py_INCREF(quality_layers);
    }

    context->num_resolutions = num_resolutions;

    j2k_decode_coord_tuple(cblk_size,
                           &context->cblk_width,
                           &context->cblk_height);
    j2k_decode_coord_tuple(precinct_size,
                           &context->precinct_width,
                           &context->precinct_height);

    context->irreversible = PyObject_IsTrue(irreversible);
    context->progression = prog_order;
    context->cinema_mode = cine_mode;

    return (PyObject *)encoder;
}

#endif

/*
 * Local Variables:
 * c-basic-offset: 4
 * End:
 *
 */
