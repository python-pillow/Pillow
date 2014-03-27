/*
 * The Python Imaging Library.
 *
 * standard decoder interfaces for the Imaging library
 *
 * history:
 * 1996-03-28 fl   Moved from _imagingmodule.c
 * 1996-04-15 fl   Support subregions in setimage
 * 1996-04-19 fl   Allocate decoder buffer (where appropriate)
 * 1996-05-02 fl   Added jpeg decoder
 * 1996-05-12 fl   Compile cleanly as C++
 * 1996-05-16 fl   Added hex decoder
 * 1996-05-26 fl   Added jpeg configuration parameters
 * 1996-12-14 fl   Added zip decoder
 * 1996-12-30 fl   Plugged potential memory leak for tiled images
 * 1997-01-03 fl   Added fli and msp decoders
 * 1997-01-04 fl   Added sun_rle and tga_rle decoders
 * 1997-05-31 fl   Added bitfield decoder
 * 1998-09-11 fl   Added orientation and pixelsize fields to tga_rle decoder
 * 1998-12-29 fl   Added mode/rawmode argument to decoders
 * 1998-12-30 fl   Added mode argument to *all* decoders
 * 2002-06-09 fl   Added stride argument to pcx decoder
 *
 * Copyright (c) 1997-2002 by Secret Labs AB.
 * Copyright (c) 1995-2002 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */

/* FIXME: make these pluggable! */

#include "Python.h"

#include "Imaging.h"
#include "py3.h"

#include "Gif.h"
#include "Lzw.h"
#include "Raw.h"
#include "Bit.h"


/* -------------------------------------------------------------------- */
/* Common                                                               */
/* -------------------------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    int (*decode)(Imaging im, ImagingCodecState state,
                  UINT8* buffer, int bytes);
    int (*cleanup)(ImagingCodecState state);
    struct ImagingCodecStateInstance state;
    Imaging im;
    PyObject* lock;
    int     handles_eof;
} ImagingDecoderObject;

static PyTypeObject ImagingDecoderType;

static ImagingDecoderObject*
PyImaging_DecoderNew(int contextsize)
{
    ImagingDecoderObject *decoder;
    void *context;

    if(PyType_Ready(&ImagingDecoderType) < 0)
        return NULL;

    decoder = PyObject_New(ImagingDecoderObject, &ImagingDecoderType);
    if (decoder == NULL)
        return NULL;

    /* Clear the decoder state */
    memset(&decoder->state, 0, sizeof(decoder->state));

    /* Allocate decoder context */
    if (contextsize > 0) {
        context = (void*) calloc(1, contextsize);
        if (!context) {
            Py_DECREF(decoder);
            (void) PyErr_NoMemory();
            return NULL;
        }
    } else
        context = 0;

    /* Initialize decoder context */
    decoder->state.context = context;

    /* Target image */
    decoder->lock = NULL;
    decoder->im = NULL;

    /* Initialize the cleanup function pointer */
    decoder->cleanup = NULL;

    /* Most decoders don't want to handle EOF themselves */
    decoder->handles_eof = 0;

    return decoder;
}

static void
_dealloc(ImagingDecoderObject* decoder)
{
    free(decoder->state.buffer);
    free(decoder->state.context);
    Py_XDECREF(decoder->lock);
    PyObject_Del(decoder);
}

static PyObject*
_decode(ImagingDecoderObject* decoder, PyObject* args)
{
    UINT8* buffer;
    int bufsize, status;

    if (!PyArg_ParseTuple(args, PY_ARG_BYTES_LENGTH, &buffer, &bufsize))
        return NULL;

    status = decoder->decode(decoder->im, &decoder->state, buffer, bufsize);

    return Py_BuildValue("ii", status, decoder->state.errcode);
}

static PyObject*
_decode_cleanup(ImagingDecoderObject* decoder, PyObject* args)
{
    int status = 0;

    if (decoder->cleanup){
        status = decoder->cleanup(&decoder->state);
    }

    return Py_BuildValue("i", status);
}



extern Imaging PyImaging_AsImaging(PyObject *op);

static PyObject*
_setimage(ImagingDecoderObject* decoder, PyObject* args)
{
    PyObject* op;
    Imaging im;
    ImagingCodecState state;
    int x0, y0, x1, y1;

    x0 = y0 = x1 = y1 = 0;

    /* FIXME: should publish the ImagingType descriptor */
    if (!PyArg_ParseTuple(args, "O|(iiii)", &op, &x0, &y0, &x1, &y1))
        return NULL;
    im = PyImaging_AsImaging(op);
    if (!im)
        return NULL;

    decoder->im = im;

    state = &decoder->state;

    /* Setup decoding tile extent */
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
        state->xsize + state->xoff > (int) im->xsize ||
        state->ysize <= 0 ||
        state->ysize + state->yoff > (int) im->ysize) {
        PyErr_SetString(PyExc_ValueError, "tile cannot extend outside image");
        return NULL;
    }

    /* Allocate memory buffer (if bits field is set) */
    if (state->bits > 0) {
        if (!state->bytes)
            state->bytes = (state->bits * state->xsize+7)/8;
        state->buffer = (UINT8*) malloc(state->bytes);
        if (!state->buffer)
            return PyErr_NoMemory();
    }

    /* Keep a reference to the image object, to make sure it doesn't
       go away before we do */
    Py_INCREF(op);
    Py_XDECREF(decoder->lock);
    decoder->lock = op;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_get_handles_eof(ImagingDecoderObject *decoder)
{
    return PyBool_FromLong(decoder->handles_eof);
}

static struct PyMethodDef methods[] = {
    {"decode", (PyCFunction)_decode, 1},
    {"cleanup", (PyCFunction)_decode_cleanup, 1},
    {"setimage", (PyCFunction)_setimage, 1},
    {NULL, NULL} /* sentinel */
};

static struct PyGetSetDef getseters[] = {
    {"handles_eof", (getter)_get_handles_eof, NULL,
     "True if this decoder expects to handle EOF itself.",
     NULL},
    {NULL, NULL, NULL, NULL, NULL} /* sentinel */
};

static PyTypeObject ImagingDecoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ImagingDecoder",               /*tp_name*/
    sizeof(ImagingDecoderObject),   /*tp_size*/
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
get_unpacker(ImagingDecoderObject* decoder, const char* mode,
             const char* rawmode)
{
    int bits;
    ImagingShuffler unpack;

    unpack = ImagingFindUnpacker(mode, rawmode, &bits);
    if (!unpack) {
        Py_DECREF(decoder);
        PyErr_SetString(PyExc_ValueError, "unknown raw mode");
        return -1;
    }

    decoder->state.shuffle = unpack;
    decoder->state.bits = bits;

    return 0;
}


/* -------------------------------------------------------------------- */
/* BIT (packed fields)                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_BitDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    int bits  = 8;
    int pad   = 8;
    int fill  = 0;
    int sign  = 0;
    int ystep = 1;
    if (!PyArg_ParseTuple(args, "s|iiiii", &mode, &bits, &pad, &fill,
                          &sign, &ystep))
        return NULL;

    if (strcmp(mode, "F") != 0) {
        PyErr_SetString(PyExc_ValueError, "bad image mode");
        return NULL;
    }

    decoder = PyImaging_DecoderNew(sizeof(BITSTATE));
    if (decoder == NULL)
        return NULL;

    decoder->decode = ImagingBitDecode;

    decoder->state.ystep = ystep;

    ((BITSTATE*)decoder->state.context)->bits = bits;
    ((BITSTATE*)decoder->state.context)->pad  = pad;
    ((BITSTATE*)decoder->state.context)->fill = fill;
    ((BITSTATE*)decoder->state.context)->sign = sign;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* FLI                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_FliDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    decoder->decode = ImagingFliDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* GIF                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_GifDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    int bits = 8;
    int interlace = 0;
    if (!PyArg_ParseTuple(args, "s|ii", &mode, &bits, &interlace))
        return NULL;

    if (strcmp(mode, "L") != 0 && strcmp(mode, "P") != 0) {
        PyErr_SetString(PyExc_ValueError, "bad image mode");
        return NULL;
    }

    decoder = PyImaging_DecoderNew(sizeof(GIFDECODERSTATE));
    if (decoder == NULL)
        return NULL;

    decoder->decode = ImagingGifDecode;

    ((GIFDECODERSTATE*)decoder->state.context)->bits = bits;
    ((GIFDECODERSTATE*)decoder->state.context)->interlace = interlace;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* HEX                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_HexDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    if (!PyArg_ParseTuple(args, "ss", &mode, &rawmode))
        return NULL;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingHexDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* LZW                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_TiffLzwDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    int filter = 0;
    if (!PyArg_ParseTuple(args, "ss|i", &mode, &rawmode, &filter))
        return NULL;

    decoder = PyImaging_DecoderNew(sizeof(LZWSTATE));
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingLzwDecode;

    ((LZWSTATE*)decoder->state.context)->filter = filter;

    return (PyObject*) decoder;
}

/* -------------------------------------------------------------------- */
/* LibTiff                                                              */
/* -------------------------------------------------------------------- */

#ifdef HAVE_LIBTIFF

#include "TiffDecode.h"

#include <string.h>
#ifdef __WIN32__
#define strcasecmp(s1, s2) stricmp(s1, s2)
#endif

PyObject*
PyImaging_LibTiffDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;
    char* mode;
    char* rawmode;
    char* compname;
    int fp;

    if (! PyArg_ParseTuple(args, "sssi", &mode, &rawmode, &compname, &fp))
        return NULL;

    TRACE(("new tiff decoder %s\n", compname));

    decoder = PyImaging_DecoderNew(sizeof(TIFFSTATE));
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    if (! ImagingLibTiffInit(&decoder->state, fp)) {
        Py_DECREF(decoder);
        PyErr_SetString(PyExc_RuntimeError, "tiff codec initialization failed");
        return NULL;
    }

    decoder->decode  = ImagingLibTiffDecode;

    return (PyObject*) decoder;
}

#endif

/* -------------------------------------------------------------------- */
/* MSP                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_MspDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, "1", "1") < 0)
        return NULL;

    decoder->decode = ImagingMspDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* PackBits                                                             */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_PackbitsDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    if (!PyArg_ParseTuple(args, "ss", &mode, &rawmode))
        return NULL;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingPackbitsDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* PCD                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_PcdDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    /* Unpack from PhotoYCC to RGB */
    if (get_unpacker(decoder, "RGB", "YCC;P") < 0)
        return NULL;

    decoder->decode = ImagingPcdDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* PCX                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_PcxDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    int stride;
    if (!PyArg_ParseTuple(args, "ssi", &mode, &rawmode, &stride))
        return NULL;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->state.bytes = stride;

    decoder->decode = ImagingPcxDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* RAW                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_RawDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    int stride = 0;
    int ystep  = 1;
    if (!PyArg_ParseTuple(args, "ss|ii", &mode, &rawmode, &stride, &ystep))
        return NULL;

    decoder = PyImaging_DecoderNew(sizeof(RAWSTATE));
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingRawDecode;

    decoder->state.ystep = ystep;

    ((RAWSTATE*)decoder->state.context)->stride = stride;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* SUN RLE                                                              */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_SunRleDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    if (!PyArg_ParseTuple(args, "ss", &mode, &rawmode))
        return NULL;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingSunRleDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* TGA RLE                                                              */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_TgaRleDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    int ystep = 1;
    int depth = 8;
    if (!PyArg_ParseTuple(args, "ss|ii", &mode, &rawmode, &ystep, &depth))
        return NULL;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingTgaRleDecode;

    decoder->state.ystep = ystep;
    decoder->state.count = depth / 8;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* XBM                                                                  */
/* -------------------------------------------------------------------- */

PyObject*
PyImaging_XbmDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    decoder = PyImaging_DecoderNew(0);
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, "1", "1;R") < 0)
        return NULL;

    decoder->decode = ImagingXbmDecode;

    return (PyObject*) decoder;
}


/* -------------------------------------------------------------------- */
/* ZIP                                                                  */
/* -------------------------------------------------------------------- */

#ifdef HAVE_LIBZ

#include "Zip.h"

PyObject*
PyImaging_ZipDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode;
    int interlaced = 0;
    if (!PyArg_ParseTuple(args, "ss|i", &mode, &rawmode, &interlaced))
        return NULL;

    decoder = PyImaging_DecoderNew(sizeof(ZIPSTATE));
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingZipDecode;

    ((ZIPSTATE*)decoder->state.context)->interlaced = interlaced;

    return (PyObject*) decoder;
}
#endif


/* -------------------------------------------------------------------- */
/* JPEG                                                                 */
/* -------------------------------------------------------------------- */

#ifdef HAVE_LIBJPEG

/* We better define this decoder last in this file, so the following
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

PyObject*
PyImaging_JpegDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;

    char* mode;
    char* rawmode; /* what we wan't from the decoder */
    char* jpegmode; /* what's in the file */
    int scale = 1;
    int draft = 0;
    if (!PyArg_ParseTuple(args, "ssz|ii", &mode, &rawmode, &jpegmode,
                          &scale, &draft))
        return NULL;

    if (!jpegmode)
        jpegmode = "";

    decoder = PyImaging_DecoderNew(sizeof(JPEGSTATE));
    if (decoder == NULL)
        return NULL;

    if (get_unpacker(decoder, mode, rawmode) < 0)
        return NULL;

    decoder->decode = ImagingJpegDecode;
    decoder->cleanup = ImagingJpegDecodeCleanup;

    strncpy(((JPEGSTATE*)decoder->state.context)->rawmode, rawmode, 8);
    strncpy(((JPEGSTATE*)decoder->state.context)->jpegmode, jpegmode, 8);

    ((JPEGSTATE*)decoder->state.context)->scale = scale;
    ((JPEGSTATE*)decoder->state.context)->draft = draft;

    return (PyObject*) decoder;
}
#endif

/* -------------------------------------------------------------------- */
/* JPEG 2000                                                            */
/* -------------------------------------------------------------------- */

#ifdef HAVE_OPENJPEG

#include "Jpeg2K.h"

PyObject*
PyImaging_Jpeg2KDecoderNew(PyObject* self, PyObject* args)
{
    ImagingDecoderObject* decoder;
    JPEG2KDECODESTATE *context;

    char* mode;
    char* format;
    OPJ_CODEC_FORMAT codec_format;
    int reduce = 0;
    int layers = 0;
    int fd = -1;
    if (!PyArg_ParseTuple(args, "ss|iii", &mode, &format,
                          &reduce, &layers, &fd))
        return NULL;

    if (strcmp(format, "j2k") == 0)
        codec_format = OPJ_CODEC_J2K;
    else if (strcmp(format, "jpt") == 0)
        codec_format = OPJ_CODEC_JPT;
    else if (strcmp(format, "jp2") == 0)
        codec_format = OPJ_CODEC_JP2;
    else
        return NULL;

    decoder = PyImaging_DecoderNew(sizeof(JPEG2KDECODESTATE));
    if (decoder == NULL)
        return NULL;

    decoder->handles_eof = 1;
    decoder->decode = ImagingJpeg2KDecode;
    decoder->cleanup = ImagingJpeg2KDecodeCleanup;

    context = (JPEG2KDECODESTATE *)decoder->state.context;

    context->fd = fd;
    context->format = codec_format;
    context->reduce = reduce;
    context->layers = layers;

    return (PyObject*) decoder;
}
#endif /* HAVE_OPENJPEG */
