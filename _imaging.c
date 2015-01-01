/*
 * The Python Imaging Library.
 *
 * the imaging library bindings
 *
 * history:
 * 1995-09-24 fl   Created
 * 1996-03-24 fl   Ready for first public release (release 0.0)
 * 1996-03-25 fl   Added fromstring (for Jack's "img" library)
 * 1996-03-28 fl   Added channel operations
 * 1996-03-31 fl   Added point operation
 * 1996-04-08 fl   Added new/new_block/new_array factories
 * 1996-04-13 fl   Added decoders
 * 1996-05-04 fl   Added palette hack
 * 1996-05-12 fl   Compile cleanly as C++
 * 1996-05-19 fl   Added matrix conversions, gradient fills
 * 1996-05-27 fl   Added display_mode
 * 1996-07-22 fl   Added getbbox, offset
 * 1996-07-23 fl   Added sequence semantics
 * 1996-08-13 fl   Added logical operators, point mode
 * 1996-08-16 fl   Modified paste interface
 * 1996-09-06 fl   Added putdata methods, use abstract interface
 * 1996-11-01 fl   Added xbm encoder
 * 1996-11-04 fl   Added experimental path stuff, draw_lines, etc
 * 1996-12-10 fl   Added zip decoder, crc32 interface
 * 1996-12-14 fl   Added modulo arithmetics
 * 1996-12-29 fl   Added zip encoder
 * 1997-01-03 fl   Added fli and msp decoders
 * 1997-01-04 fl   Added experimental sun_rle and tga_rle decoders
 * 1997-01-05 fl   Added gif encoder, getpalette hack
 * 1997-02-23 fl   Added histogram mask
 * 1997-05-12 fl   Minor tweaks to match the IFUNC95 interface
 * 1997-05-21 fl   Added noise generator, spread effect
 * 1997-06-05 fl   Added mandelbrot generator
 * 1997-08-02 fl   Modified putpalette to coerce image mode if necessary
 * 1998-01-11 fl   Added INT32 support
 * 1998-01-22 fl   Fixed draw_points to draw the last point too
 * 1998-06-28 fl   Added getpixel, getink, draw_ink
 * 1998-07-12 fl   Added getextrema
 * 1998-07-17 fl   Added point conversion to arbitrary formats
 * 1998-09-21 fl   Added support for resampling filters
 * 1998-09-22 fl   Added support for quad transform
 * 1998-12-29 fl   Added support for arcs, chords, and pieslices
 * 1999-01-10 fl   Added some experimental arrow graphics stuff
 * 1999-02-06 fl   Added draw_bitmap, font acceleration stuff
 * 2001-04-17 fl   Fixed some egcs compiler nits
 * 2001-09-17 fl   Added screen grab primitives (win32)
 * 2002-03-09 fl   Added stretch primitive
 * 2002-03-10 fl   Fixed filter handling in rotate
 * 2002-06-06 fl   Added I, F, and RGB support to putdata
 * 2002-06-08 fl   Added rankfilter
 * 2002-06-09 fl   Added support for user-defined filter kernels
 * 2002-11-19 fl   Added clipboard grab primitives (win32)
 * 2002-12-11 fl   Added draw context
 * 2003-04-26 fl   Tweaks for Python 2.3 beta 1
 * 2003-05-21 fl   Added createwindow primitive (win32)
 * 2003-09-13 fl   Added thread section hooks
 * 2003-09-15 fl   Added expand helper
 * 2003-09-26 fl   Added experimental LA support
 * 2004-02-21 fl   Handle zero-size images in quantize
 * 2004-06-05 fl   Added ptr attribute (used to access Imaging objects)
 * 2004-06-05 fl   Don't crash when fetching pixels from zero-wide images
 * 2004-09-17 fl   Added getcolors
 * 2004-10-04 fl   Added modefilter
 * 2005-10-02 fl   Added access proxy
 * 2006-06-18 fl   Always draw last point in polyline
 *
 * Copyright (c) 1997-2006 by Secret Labs AB
 * Copyright (c) 1995-2006 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

#define PILLOW_VERSION "2.7.0"

#include "Python.h"

#ifdef HAVE_LIBZ
#include "zlib.h"
#endif

#include "Imaging.h"

#include "py3.h"

/* Configuration stuff. Feel free to undef things you don't need. */
#define WITH_IMAGECHOPS /* ImageChops support */
#define WITH_IMAGEDRAW /* ImageDraw support */
#define WITH_MAPPING /* use memory mapping to read some file formats */
#define WITH_IMAGEPATH /* ImagePath stuff */
#define WITH_ARROW /* arrow graphics stuff (experimental) */
#define WITH_EFFECTS /* special effects */
#define WITH_QUANTIZE /* quantization support */
#define WITH_RANKFILTER /* rank filter */
#define WITH_MODEFILTER /* mode filter */
#define WITH_THREADING /* "friendly" threading support */
#define WITH_UNSHARPMASK /* Kevin Cazabon's unsharpmask module */

#define WITH_DEBUG /* extra debugging interfaces */

/* PIL Plus extensions */
#undef  WITH_CRACKCODE /* pil plus */

#undef    VERBOSE

#define CLIP(x) ((x) <= 0 ? 0 : (x) < 256 ? (x) : 255)

#define B16(p, i) ((((int)p[(i)]) << 8) + p[(i)+1])
#define L16(p, i) ((((int)p[(i)+1]) << 8) + p[(i)])
#define S16(v) ((v) < 32768 ? (v) : ((v) - 65536))

/* -------------------------------------------------------------------- */
/* OBJECT ADMINISTRATION                        */
/* -------------------------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    Imaging image;
    ImagingAccess access;
} ImagingObject;

static PyTypeObject Imaging_Type;

#ifdef WITH_IMAGEDRAW

typedef struct
{
    /* to write a character, cut out sxy from glyph data, place
       at current position plus dxy, and advance by (dx, dy) */
    int dx, dy;
    int dx0, dy0, dx1, dy1;
    int sx0, sy0, sx1, sy1;
} Glyph;

typedef struct {
    PyObject_HEAD
    ImagingObject* ref;
    Imaging bitmap;
    int ysize;
    int baseline;
    Glyph glyphs[256];
} ImagingFontObject;

static PyTypeObject ImagingFont_Type;

typedef struct {
    PyObject_HEAD
    ImagingObject* image;
    UINT8 ink[4];
    int blend;
} ImagingDrawObject;

static PyTypeObject ImagingDraw_Type;

#endif

typedef struct {
    PyObject_HEAD
    ImagingObject* image;
    int readonly;
} PixelAccessObject;

static PyTypeObject PixelAccess_Type;

PyObject*
PyImagingNew(Imaging imOut)
{
    ImagingObject* imagep;

    if (!imOut)
        return NULL;

    imagep = PyObject_New(ImagingObject, &Imaging_Type);
    if (imagep == NULL) {
        ImagingDelete(imOut);
        return NULL;
    }

#ifdef VERBOSE
    printf("imaging %p allocated\n", imagep);
#endif

    imagep->image = imOut;
    imagep->access = ImagingAccessNew(imOut);

    return (PyObject*) imagep;
}

static void
_dealloc(ImagingObject* imagep)
{

#ifdef VERBOSE
    printf("imaging %p deleted\n", imagep);
#endif

    if (imagep->access)
        ImagingAccessDelete(imagep->image, imagep->access);
    ImagingDelete(imagep->image);
    PyObject_Del(imagep);
}

#define PyImaging_Check(op) (Py_TYPE(op) == &Imaging_Type)

Imaging PyImaging_AsImaging(PyObject *op)
{
    if (!PyImaging_Check(op)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    return ((ImagingObject *)op)->image;
}


/* -------------------------------------------------------------------- */
/* THREAD HANDLING                                                      */
/* -------------------------------------------------------------------- */

void ImagingSectionEnter(ImagingSectionCookie* cookie)
{
#ifdef WITH_THREADING
    *cookie = (PyThreadState *) PyEval_SaveThread();
#endif
}

void ImagingSectionLeave(ImagingSectionCookie* cookie)
{
#ifdef WITH_THREADING
    PyEval_RestoreThread((PyThreadState*) *cookie);
#endif
}

/* -------------------------------------------------------------------- */
/* BUFFER HANDLING                                                      */
/* -------------------------------------------------------------------- */
/* Python compatibility API */

int PyImaging_CheckBuffer(PyObject* buffer)
{
#if PY_VERSION_HEX >= 0x03000000
    return PyObject_CheckBuffer(buffer);
#else
    return PyObject_CheckBuffer(buffer) || PyObject_CheckReadBuffer(buffer);
#endif
}

int PyImaging_GetBuffer(PyObject* buffer, Py_buffer *view)
{
    /* must call check_buffer first! */
#if PY_VERSION_HEX >= 0x03000000
    return PyObject_GetBuffer(buffer, view, PyBUF_SIMPLE);
#else
    /* Use new buffer protocol if available
       (mmap doesn't support this in 2.7, go figure) */
    if (PyObject_CheckBuffer(buffer)) {
        return PyObject_GetBuffer(buffer, view, PyBUF_SIMPLE);
    }

    /* Pretend we support the new protocol; PyBuffer_Release happily ignores
       calling bf_releasebuffer on objects that don't support it */
    view->buf = NULL;
    view->len = 0;
    view->readonly = 1;
    view->format = NULL;
    view->ndim = 0;
    view->shape = NULL;
    view->strides = NULL;
    view->suboffsets = NULL;
    view->itemsize = 0;
    view->internal = NULL;

    Py_INCREF(buffer);
    view->obj = buffer;

    return PyObject_AsReadBuffer(buffer, (void *) &view->buf, &view->len);
#endif
}

/* -------------------------------------------------------------------- */
/* EXCEPTION REROUTING                                                  */
/* -------------------------------------------------------------------- */

/* error messages */
static const char* must_be_sequence = "argument must be a sequence";
static const char* wrong_mode = "unrecognized image mode";
static const char* wrong_raw_mode = "unrecognized raw mode";
static const char* outside_image = "image index out of range";
static const char* outside_palette = "palette index out of range";
static const char* wrong_palette_size = "invalid palette size";
static const char* no_palette = "image has no palette";
static const char* readonly = "image is readonly";
/* static const char* no_content = "image has no content"; */

void *
ImagingError_IOError(void)
{
    PyErr_SetString(PyExc_IOError, "error when accessing file");
    return NULL;
}

void *
ImagingError_MemoryError(void)
{
    return PyErr_NoMemory();
}

void *
ImagingError_Mismatch(void)
{
    PyErr_SetString(PyExc_ValueError, "images do not match");
    return NULL;
}

void *
ImagingError_ModeError(void)
{
    PyErr_SetString(PyExc_ValueError, "image has wrong mode");
    return NULL;
}

void *
ImagingError_ValueError(const char *message)
{
    PyErr_SetString(
        PyExc_ValueError,
        (message) ? (char*) message : "unrecognized argument value"
        );
    return NULL;
}

void
ImagingError_Clear(void)
{
    PyErr_Clear();
}

/* -------------------------------------------------------------------- */
/* HELPERS                                */
/* -------------------------------------------------------------------- */

static int
getbands(const char* mode)
{
    Imaging im;
    int bands;

    /* FIXME: add primitive to libImaging to avoid extra allocation */
    im = ImagingNew(mode, 0, 0);
    if (!im)
        return -1;

    bands = im->bands;

    ImagingDelete(im);

    return bands;
}

#define TYPE_UINT8 (0x100|sizeof(UINT8))
#define TYPE_INT32 (0x200|sizeof(INT32))
#define TYPE_FLOAT32 (0x300|sizeof(FLOAT32))
#define TYPE_DOUBLE (0x400|sizeof(double))

static void*
getlist(PyObject* arg, int* length, const char* wrong_length, int type)
{
    int i, n, itemp;
    double dtemp;
    void* list;
    PyObject* seq;
    PyObject* op;
    
    if (!PySequence_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, must_be_sequence);
        return NULL;
    }

    n = PyObject_Length(arg);
    if (length && wrong_length && n != *length) {
        PyErr_SetString(PyExc_ValueError, wrong_length);
        return NULL;
    }

    list = malloc(n * (type & 0xff));
    if (!list)
        return PyErr_NoMemory();

    seq = PySequence_Fast(arg, must_be_sequence);
    if (!seq) {
        free(list);
        PyErr_SetString(PyExc_TypeError, must_be_sequence);
        return NULL;
    }
    
    for (i = 0; i < n; i++) {
        op = PySequence_Fast_GET_ITEM(seq, i);
        // DRY, branch prediction is going to work _really_ well 
        // on this switch. And 3 fewer loops to copy/paste. 
        switch (type) {
        case TYPE_UINT8:
            itemp = PyInt_AsLong(op);
            ((UINT8*)list)[i] = CLIP(itemp);
            break;
        case TYPE_INT32:
            itemp = PyInt_AsLong(op);
            ((INT32*)list)[i] = itemp;
            break;
        case TYPE_FLOAT32:
            dtemp = PyFloat_AsDouble(op);
            ((FLOAT32*)list)[i] = (FLOAT32) dtemp;
            break;
        case TYPE_DOUBLE:
            dtemp = PyFloat_AsDouble(op);
            ((double*)list)[i] = (double) dtemp;
            break;
        }
    }

    if (length)
        *length = n;

    PyErr_Clear();

    return list;
}

static inline PyObject*
getpixel(Imaging im, ImagingAccess access, int x, int y)
{
    union {
      UINT8 b[4];
      UINT16 h;
      INT32 i;
      FLOAT32 f;
    } pixel;

    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize) {
        PyErr_SetString(PyExc_IndexError, outside_image);
        return NULL;
    }

    access->get_pixel(im, x, y, &pixel);

    switch (im->type) {
    case IMAGING_TYPE_UINT8:
        switch (im->bands) {
        case 1:
            return PyInt_FromLong(pixel.b[0]);
        case 2:
            return Py_BuildValue("BB", pixel.b[0], pixel.b[1]);
        case 3:
            return Py_BuildValue("BBB", pixel.b[0], pixel.b[1], pixel.b[2]);
        case 4:
            return Py_BuildValue("BBBB", pixel.b[0], pixel.b[1], pixel.b[2], pixel.b[3]);
        }
        break;
    case IMAGING_TYPE_INT32:
        return PyInt_FromLong(pixel.i);
    case IMAGING_TYPE_FLOAT32:
        return PyFloat_FromDouble(pixel.f);
    case IMAGING_TYPE_SPECIAL:
        if (strncmp(im->mode, "I;16", 4) == 0)
            return PyInt_FromLong(pixel.h);
        break;
    }

    /* unknown type */
    Py_INCREF(Py_None);
    return Py_None;
}

static char*
getink(PyObject* color, Imaging im, char* ink)
{
    int r, g, b, a;
    double f;

    /* fill ink buffer (four bytes) with something that can
       be cast to either UINT8 or INT32 */

    switch (im->type) {
    case IMAGING_TYPE_UINT8:
        /* unsigned integer */
        if (im->bands == 1) {
            /* unsigned integer, single layer */
            r = PyInt_AsLong(color);
            if (r == -1 && PyErr_Occurred())
                return NULL;
            ink[0] = CLIP(r);
            ink[1] = ink[2] = ink[3] = 0;
        } else {
            a = 255;
#if PY_VERSION_HEX >= 0x03000000
            if (PyLong_Check(color)) {
                r = (int) PyLong_AsLong(color);
#else
            if (PyInt_Check(color) || PyLong_Check(color)) {
                if (PyInt_Check(color))
                    r = PyInt_AS_LONG(color);
                else
                    r = (int) PyLong_AsLong(color);
#endif

                /* compatibility: ABGR */
                a = (UINT8) (r >> 24);
                b = (UINT8) (r >> 16);
                g = (UINT8) (r >> 8);
                r = (UINT8) r;
            } else {
                if (im->bands == 2) {
                    if (!PyArg_ParseTuple(color, "i|i", &r, &a))
                        return NULL;
                    g = b = r;
                } else {
                    if (!PyArg_ParseTuple(color, "iii|i", &r, &g, &b, &a))
                        return NULL;
                }
            }
            ink[0] = CLIP(r);
            ink[1] = CLIP(g);
            ink[2] = CLIP(b);
            ink[3] = CLIP(a);
        }
        return ink;
    case IMAGING_TYPE_INT32:
        /* signed integer */
        r = PyInt_AsLong(color);
        if (r == -1 && PyErr_Occurred())
            return NULL;
        *(INT32*) ink = r;
        return ink;
    case IMAGING_TYPE_FLOAT32:
        /* floating point */
        f = PyFloat_AsDouble(color);
        if (f == -1.0 && PyErr_Occurred())
            return NULL;
        *(FLOAT32*) ink = (FLOAT32) f;
        return ink;
    case IMAGING_TYPE_SPECIAL:
        if (strncmp(im->mode, "I;16", 4) == 0) {
            r = PyInt_AsLong(color);
            if (r == -1 && PyErr_Occurred())
                return NULL;
            ink[0] = (UINT8) r;
            ink[1] = (UINT8) (r >> 8);
            ink[2] = ink[3] = 0;
            return ink;
        }
    }

    PyErr_SetString(PyExc_ValueError, wrong_mode);
    return NULL;
}

/* -------------------------------------------------------------------- */
/* FACTORIES                                */
/* -------------------------------------------------------------------- */

static PyObject*
_fill(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;
    PyObject* color;
    char buffer[4];
    Imaging im;

    xsize = ysize = 256;
    color = NULL;

    if (!PyArg_ParseTuple(args, "s|(ii)O", &mode, &xsize, &ysize, &color))
        return NULL;

    im = ImagingNew(mode, xsize, ysize);
    if (!im)
        return NULL;

    if (color) {
        if (!getink(color, im, buffer)) {
            ImagingDelete(im);
            return NULL;
        }
    } else
        buffer[0] = buffer[1] = buffer[2] = buffer[3] = 0;

    (void) ImagingFill(im, buffer);

    return PyImagingNew(im);
}

static PyObject*
_new(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
        return NULL;

    return PyImagingNew(ImagingNew(mode, xsize, ysize));
}

static PyObject*
_new_array(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
        return NULL;

    return PyImagingNew(ImagingNewArray(mode, xsize, ysize));
}

static PyObject*
_new_block(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
        return NULL;

    return PyImagingNew(ImagingNewBlock(mode, xsize, ysize));
}

static PyObject*
_getcount(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":getcount"))
        return NULL;

    return PyInt_FromLong(ImagingNewCount);
}

static PyObject*
_linear_gradient(PyObject* self, PyObject* args)
{
    char* mode;

    if (!PyArg_ParseTuple(args, "s", &mode))
        return NULL;

    return PyImagingNew(ImagingFillLinearGradient(mode));
}

static PyObject*
_radial_gradient(PyObject* self, PyObject* args)
{
    char* mode;

    if (!PyArg_ParseTuple(args, "s", &mode))
        return NULL;

    return PyImagingNew(ImagingFillRadialGradient(mode));
}

static PyObject*
_open_ppm(PyObject* self, PyObject* args)
{
    char* filename;

    if (!PyArg_ParseTuple(args, "s", &filename))
        return NULL;

    return PyImagingNew(ImagingOpenPPM(filename));
}

static PyObject*
_alpha_composite(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;

    if (!PyArg_ParseTuple(args, "O!O!",
              &Imaging_Type, &imagep1,
              &Imaging_Type, &imagep2))
        return NULL;

    return PyImagingNew(ImagingAlphaComposite(imagep1->image, imagep2->image));
}

static PyObject*
_blend(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;
    double alpha;

    alpha = 0.5;
    if (!PyArg_ParseTuple(args, "O!O!|d",
                          &Imaging_Type, &imagep1,
                          &Imaging_Type, &imagep2,
                          &alpha))
        return NULL;

    return PyImagingNew(ImagingBlend(imagep1->image, imagep2->image,
                     (float) alpha));
}

/* -------------------------------------------------------------------- */
/* METHODS                                */
/* -------------------------------------------------------------------- */

static PyObject*
_convert(ImagingObject* self, PyObject* args)
{
    char* mode;
    int dither = 0;
    ImagingObject *paletteimage = NULL;

    if (!PyArg_ParseTuple(args, "s|iO", &mode, &dither, &paletteimage))
        return NULL;
    if (paletteimage != NULL) {
        if (!PyImaging_Check(paletteimage)) {
            PyObject_Print((PyObject *)paletteimage, stderr, 0);
            PyErr_SetString(PyExc_ValueError, "palette argument must be image with mode 'P'");
            return NULL;
        }
        if (paletteimage->image->palette == NULL) {
            PyErr_SetString(PyExc_ValueError, "null palette");
            return NULL;
        }
    }

    return PyImagingNew(ImagingConvert(self->image, mode, paletteimage ? paletteimage->image->palette : NULL, dither));
}

static PyObject*
_convert2(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;
    if (!PyArg_ParseTuple(args, "O!O!",
                          &Imaging_Type, &imagep1,
                          &Imaging_Type, &imagep2))
        return NULL;

    if (!ImagingConvert2(imagep1->image, imagep2->image))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_convert_matrix(ImagingObject* self, PyObject* args)
{
    char* mode;
    float m[12];
    if (!PyArg_ParseTuple(args, "s(ffff)", &mode, m+0, m+1, m+2, m+3)) {
        PyErr_Clear();
    if (!PyArg_ParseTuple(args, "s(ffffffffffff)", &mode,
                  m+0, m+1, m+2, m+3,
                  m+4, m+5, m+6, m+7,
                  m+8, m+9, m+10, m+11))
        return NULL;
    }

    return PyImagingNew(ImagingConvertMatrix(self->image, mode, m));
}

static PyObject*
_convert_transparent(ImagingObject* self, PyObject* args)
{
    char* mode;
    int r,g,b;
    if (PyArg_ParseTuple(args, "s(iii)", &mode, &r, &g, &b)) {
        return PyImagingNew(ImagingConvertTransparent(self->image, mode, r, g, b));
    }
    PyErr_Clear();
    if (PyArg_ParseTuple(args, "si", &mode, &r)) {
        return PyImagingNew(ImagingConvertTransparent(self->image, mode, r, 0, 0));
    }
    return NULL;
}

static PyObject*
_copy(ImagingObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ""))
        return NULL;

    return PyImagingNew(ImagingCopy(self->image));
}

static PyObject*
_copy2(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;
    if (!PyArg_ParseTuple(args, "O!O!",
                          &Imaging_Type, &imagep1,
                          &Imaging_Type, &imagep2))
        return NULL;

    if (!ImagingCopy2(imagep1->image, imagep2->image))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_crop(ImagingObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    if (!PyArg_ParseTuple(args, "(iiii)", &x0, &y0, &x1, &y1))
        return NULL;

    return PyImagingNew(ImagingCrop(self->image, x0, y0, x1, y1));
}

static PyObject*
_expand_image(ImagingObject* self, PyObject* args)
{
    int x, y;
    int mode = 0;
    if (!PyArg_ParseTuple(args, "ii|i", &x, &y, &mode))
        return NULL;

    return PyImagingNew(ImagingExpand(self->image, x, y, mode));
}

static PyObject*
_filter(ImagingObject* self, PyObject* args)
{
    PyObject* imOut;
    int kernelsize;
    FLOAT32* kerneldata;

    int xsize, ysize;
    float divisor, offset;
    PyObject* kernel = NULL;
    if (!PyArg_ParseTuple(args, "(ii)ffO", &xsize, &ysize,
                          &divisor, &offset, &kernel))
        return NULL;

    /* get user-defined kernel */
    kerneldata = getlist(kernel, &kernelsize, NULL, TYPE_FLOAT32);
    if (!kerneldata)
        return NULL;
    if (kernelsize != xsize * ysize) {
        free(kerneldata);
        return ImagingError_ValueError("bad kernel size");
    }

    imOut = PyImagingNew(
        ImagingFilter(self->image, xsize, ysize, kerneldata, offset, divisor)
        );

    free(kerneldata);

    return imOut;
}

#ifdef WITH_UNSHARPMASK
static PyObject*
_gaussian_blur(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    float radius = 0;
    int passes = 3;
    if (!PyArg_ParseTuple(args, "f|i", &radius, &passes))
        return NULL;

    imIn = self->image;
    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut)
        return NULL;

    if (!ImagingGaussianBlur(imOut, imIn, radius, passes))
        return NULL;

    return PyImagingNew(imOut);
}
#endif

static PyObject*
_getpalette(ImagingObject* self, PyObject* args)
{
    PyObject* palette;
    int palettesize = 256;
    int bits;
    ImagingShuffler pack;

    char* mode = "RGB";
    char* rawmode = "RGB";
    if (!PyArg_ParseTuple(args, "|ss", &mode, &rawmode))
        return NULL;

    if (!self->image->palette) {
        PyErr_SetString(PyExc_ValueError, no_palette);
        return NULL;
    }

    pack = ImagingFindPacker(mode, rawmode, &bits);
    if (!pack) {
        PyErr_SetString(PyExc_ValueError, wrong_raw_mode);
        return NULL;
    }

    palette = PyBytes_FromStringAndSize(NULL, palettesize * bits / 8);
    if (!palette)
        return NULL;

    pack((UINT8*) PyBytes_AsString(palette),
         self->image->palette->palette, palettesize);

    return palette;
}

static PyObject*
_getpalettemode(ImagingObject* self, PyObject* args)
{
    if (!self->image->palette) {
    PyErr_SetString(PyExc_ValueError, no_palette);
    return NULL;
    }

    return PyUnicode_FromString(self->image->palette->mode);
}

static inline int
_getxy(PyObject* xy, int* x, int *y)
{
    PyObject* value;

    if (!PyTuple_Check(xy) || PyTuple_GET_SIZE(xy) != 2)
        goto badarg;

    value = PyTuple_GET_ITEM(xy, 0);
    if (PyInt_Check(value))
        *x = PyInt_AS_LONG(value);
    else if (PyFloat_Check(value))
        *x = (int) PyFloat_AS_DOUBLE(value);
    else
        goto badval;

    value = PyTuple_GET_ITEM(xy, 1);
    if (PyInt_Check(value))
        *y = PyInt_AS_LONG(value);
    else if (PyFloat_Check(value))
        *y = (int) PyFloat_AS_DOUBLE(value);
    else
        goto badval;

    return 0;

  badarg:
    PyErr_SetString(
        PyExc_TypeError,
        "argument must be sequence of length 2"
        );
    return -1;

  badval:
    PyErr_SetString(
        PyExc_TypeError,
        "an integer is required"
        );
    return -1;
}

static PyObject*
_getpixel(ImagingObject* self, PyObject* args)
{
    PyObject* xy;
    int x, y;

    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(
            PyExc_TypeError,
            "argument 1 must be sequence of length 2"
            );
        return NULL;
    }

    xy = PyTuple_GET_ITEM(args, 0);

    if (_getxy(xy, &x, &y))
        return NULL;

    if (self->access == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return getpixel(self->image, self->access, x, y);
}

static PyObject*
_histogram(ImagingObject* self, PyObject* args)
{
    ImagingHistogram h;
    PyObject* list;
    int i;
    union {
        UINT8 u[2];
        INT32 i[2];
        FLOAT32 f[2];
    } extrema;
    void* ep;
    int i0, i1;
    double f0, f1;

    PyObject* extremap = NULL;
    ImagingObject* maskp = NULL;
    if (!PyArg_ParseTuple(args, "|OO!", &extremap, &Imaging_Type, &maskp))
    return NULL;

    if (extremap) {
        ep = &extrema;
        switch (self->image->type) {
        case IMAGING_TYPE_UINT8:
            if (!PyArg_ParseTuple(extremap, "ii", &i0, &i1))
                return NULL;
            /* FIXME: clip */
            extrema.u[0] = i0;
            extrema.u[1] = i1;
            break;
        case IMAGING_TYPE_INT32:
            if (!PyArg_ParseTuple(extremap, "ii", &i0, &i1))
                return NULL;
            extrema.i[0] = i0;
            extrema.i[1] = i1;
            break;
        case IMAGING_TYPE_FLOAT32:
            if (!PyArg_ParseTuple(extremap, "dd", &f0, &f1))
                return NULL;
            extrema.f[0] = (FLOAT32) f0;
            extrema.f[1] = (FLOAT32) f1;
            break;
        default:
            ep = NULL;
            break;
        }
    } else
        ep = NULL;

    h = ImagingGetHistogram(self->image, (maskp) ? maskp->image : NULL, ep);

    if (!h)
    return NULL;

    /* Build an integer list containing the histogram */
    list = PyList_New(h->bands * 256);
    for (i = 0; i < h->bands * 256; i++) {
        PyObject* item;
        item = PyInt_FromLong(h->histogram[i]);
        if (item == NULL) {
            Py_DECREF(list);
            list = NULL;
            break;
        }
        PyList_SetItem(list, i, item);
    }

    ImagingHistogramDelete(h);

    return list;
}

#ifdef WITH_MODEFILTER
static PyObject*
_modefilter(ImagingObject* self, PyObject* args)
{
    int size;
    if (!PyArg_ParseTuple(args, "i", &size))
        return NULL;

    return PyImagingNew(ImagingModeFilter(self->image, size));
}
#endif

static PyObject*
_offset(ImagingObject* self, PyObject* args)
{
    int xoffset, yoffset;
    if (!PyArg_ParseTuple(args, "ii", &xoffset, &yoffset))
        return NULL;

    return PyImagingNew(ImagingOffset(self->image, xoffset, yoffset));
}

static PyObject*
_paste(ImagingObject* self, PyObject* args)
{
    int status;
    char ink[4];

    PyObject* source;
    int x0, y0, x1, y1;
    ImagingObject* maskp = NULL;
    if (!PyArg_ParseTuple(args, "O(iiii)|O!",
              &source,
              &x0, &y0, &x1, &y1,
              &Imaging_Type, &maskp))
    return NULL;

    if (PyImaging_Check(source))
        status = ImagingPaste(
            self->image, PyImaging_AsImaging(source),
            (maskp) ? maskp->image : NULL,
            x0, y0, x1, y1
            );

    else {
        if (!getink(source, self->image, ink))
            return NULL;
        status = ImagingFill2(
            self->image, ink,
            (maskp) ? maskp->image : NULL,
            x0, y0, x1, y1
            );
    }

    if (status < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_point(ImagingObject* self, PyObject* args)
{
    static const char* wrong_number = "wrong number of lut entries";

    int n, i;
    int bands;
    Imaging im;

    PyObject* list;
    char* mode;
    if (!PyArg_ParseTuple(args, "Oz", &list, &mode))
    return NULL;

    if (mode && !strcmp(mode, "F")) {
        FLOAT32* data;

        /* map from 8-bit data to floating point */
        n = 256;
        data = getlist(list, &n, wrong_number, TYPE_FLOAT32);
        if (!data)
            return NULL;
        im = ImagingPoint(self->image, mode, (void*) data);
        free(data);

    } else if (!strcmp(self->image->mode, "I") && mode && !strcmp(mode, "L")) {
        UINT8* data;

        /* map from 16-bit subset of 32-bit data to 8-bit */
        /* FIXME: support arbitrary number of entries (requires API change) */
        n = 65536;
        data = getlist(list, &n, wrong_number, TYPE_UINT8);
        if (!data)
            return NULL;
        im = ImagingPoint(self->image, mode, (void*) data);
        free(data);

    } else {
        INT32* data;
        UINT8 lut[1024];

        if (mode) {
            bands = getbands(mode);
            if (bands < 0)
                return NULL;
        } else
            bands = self->image->bands;

        /* map to integer data */
        n = 256 * bands;
        data = getlist(list, &n, wrong_number, TYPE_INT32);
        if (!data)
            return NULL;

        if (mode && !strcmp(mode, "I"))
            im = ImagingPoint(self->image, mode, (void*) data);
        else if (mode && bands > 1) {
            for (i = 0; i < 256; i++) {
                lut[i*4] = CLIP(data[i]);
                lut[i*4+1] = CLIP(data[i+256]);
                lut[i*4+2] = CLIP(data[i+512]);
                if (n > 768)
                    lut[i*4+3] = CLIP(data[i+768]);
            }
            im = ImagingPoint(self->image, mode, (void*) lut);
        } else {
            /* map individual bands */
            for (i = 0; i < n; i++)
                lut[i] = CLIP(data[i]);
            im = ImagingPoint(self->image, mode, (void*) lut);
        }
        free(data);
    }

    return PyImagingNew(im);
}

static PyObject*
_point_transform(ImagingObject* self, PyObject* args)
{
    double scale = 1.0;
    double offset = 0.0;
    if (!PyArg_ParseTuple(args, "|dd", &scale, &offset))
    return NULL;

    return PyImagingNew(ImagingPointTransform(self->image, scale, offset));
}

static PyObject*
_putdata(ImagingObject* self, PyObject* args)
{
    Imaging image;
    // i & n are # pixels, require py_ssize_t. x can be as large as n. y, just because.
    Py_ssize_t n, i, x, y;

    PyObject* data;
    PyObject* seq;
    PyObject* op;
    double scale = 1.0;
    double offset = 0.0;

    if (!PyArg_ParseTuple(args, "O|dd", &data, &scale, &offset))
        return NULL;

    if (!PySequence_Check(data)) {
        PyErr_SetString(PyExc_TypeError, must_be_sequence);
        return NULL;
    }

    image = self->image;

    n = PyObject_Length(data);
    if (n > (Py_ssize_t) (image->xsize * image->ysize)) {
        PyErr_SetString(PyExc_TypeError, "too many data entries");
        return NULL;
    }

    if (image->image8) {
        if (PyBytes_Check(data)) {
            unsigned char* p;
            p = (unsigned char*) PyBytes_AS_STRING(data);
            if (scale == 1.0 && offset == 0.0)
                /* Plain string data */
                for (i = y = 0; i < n; i += image->xsize, y++) {
                    x = n - i;
                    if (x > (int) image->xsize)
                        x = image->xsize;
                    memcpy(image->image8[y], p+i, x);
                }
            else
                /* Scaled and clipped string data */
                for (i = x = y = 0; i < n; i++) {
                    image->image8[y][x] = CLIP((int) (p[i] * scale + offset));
                    if (++x >= (int) image->xsize)
                        x = 0, y++;
                }
        } else {
           seq = PySequence_Fast(data, must_be_sequence);
           if (!seq) {
               PyErr_SetString(PyExc_TypeError, must_be_sequence);
               return NULL;
           }
           if (scale == 1.0 && offset == 0.0) {
               /* Clipped data */
               for (i = x = y = 0; i < n; i++) {
                   op = PySequence_Fast_GET_ITEM(seq, i);
                   image->image8[y][x] = (UINT8) CLIP(PyInt_AsLong(op));
                   if (++x >= (int) image->xsize){
                       x = 0, y++;
                   }
               }

            } else {
               /* Scaled and clipped data */
               for (i = x = y = 0; i < n; i++) {
                   PyObject *op = PySequence_Fast_GET_ITEM(seq, i);
                   image->image8[y][x] = CLIP(
                       (int) (PyFloat_AsDouble(op) * scale + offset));
                   if (++x >= (int) image->xsize){
                       x = 0, y++;
                   }
               }
           }
           PyErr_Clear(); /* Avoid weird exceptions */
        }
    } else {
        /* 32-bit images */
        seq = PySequence_Fast(data, must_be_sequence);
        if (!seq) {
            PyErr_SetString(PyExc_TypeError, must_be_sequence);
            return NULL;
        }
        switch (image->type) {
        case IMAGING_TYPE_INT32:
            for (i = x = y = 0; i < n; i++) {
                op = PySequence_Fast_GET_ITEM(seq, i);
                IMAGING_PIXEL_INT32(image, x, y) =
                    (INT32) (PyFloat_AsDouble(op) * scale + offset);
                if (++x >= (int) image->xsize){
                    x = 0, y++;
                }
            }
            PyErr_Clear(); /* Avoid weird exceptions */
            break;
        case IMAGING_TYPE_FLOAT32:
            for (i = x = y = 0; i < n; i++) {
                op = PySequence_Fast_GET_ITEM(seq, i);
                IMAGING_PIXEL_FLOAT32(image, x, y) =
                    (FLOAT32) (PyFloat_AsDouble(op) * scale + offset);
                if (++x >= (int) image->xsize){
                    x = 0, y++;
                }
            }
            PyErr_Clear(); /* Avoid weird exceptions */
            break;
        default:
            for (i = x = y = 0; i < n; i++) {
                union {
                    char ink[4];
                    INT32 inkint;
                } u;

                op = PySequence_Fast_GET_ITEM(seq, i);
                if (!op || !getink(op, image, u.ink)) {
                    return NULL;
                }
                /* FIXME: what about scale and offset? */
                image->image32[y][x] = u.inkint;
                if (++x >= (int) image->xsize){
                    x = 0, y++;
                }
            }
            PyErr_Clear(); /* Avoid weird exceptions */
            break;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef WITH_QUANTIZE

static PyObject*
_quantize(ImagingObject* self, PyObject* args)
{
    int colours = 256;
    int method = 0;
    int kmeans = 0;
    if (!PyArg_ParseTuple(args, "|iii", &colours, &method, &kmeans))
        return NULL;

    if (!self->image->xsize || !self->image->ysize) {
        /* no content; return an empty image */
        return PyImagingNew(
            ImagingNew("P", self->image->xsize, self->image->ysize)
            );
    }

    return PyImagingNew(ImagingQuantize(self->image, colours, method, kmeans));
}
#endif

static PyObject*
_putpalette(ImagingObject* self, PyObject* args)
{
    ImagingShuffler unpack;
    int bits;

    char* rawmode;
    UINT8* palette;
    int palettesize;
    if (!PyArg_ParseTuple(args, "s"PY_ARG_BYTES_LENGTH, &rawmode, &palette, &palettesize))
        return NULL;

    if (strcmp(self->image->mode, "L") != 0 && strcmp(self->image->mode, "P")) {
        PyErr_SetString(PyExc_ValueError, wrong_mode);
        return NULL;
    }

    unpack = ImagingFindUnpacker("RGB", rawmode, &bits);
    if (!unpack) {
        PyErr_SetString(PyExc_ValueError, wrong_raw_mode);
        return NULL;
    }

    if ( palettesize * 8 / bits > 256) {
        PyErr_SetString(PyExc_ValueError, wrong_palette_size);
        return NULL;
    }

    ImagingPaletteDelete(self->image->palette);

    strcpy(self->image->mode, "P");

    self->image->palette = ImagingPaletteNew("RGB");

    unpack(self->image->palette->palette, palette, palettesize * 8 / bits);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_putpalettealpha(ImagingObject* self, PyObject* args)
{
    int index;
    int alpha = 0;
    if (!PyArg_ParseTuple(args, "i|i", &index, &alpha))
        return NULL;

    if (!self->image->palette) {
        PyErr_SetString(PyExc_ValueError, no_palette);
        return NULL;
    }

    if (index < 0 || index >= 256) {
        PyErr_SetString(PyExc_ValueError, outside_palette);
        return NULL;
    }

    strcpy(self->image->palette->mode, "RGBA");
    self->image->palette->palette[index*4+3] = (UINT8) alpha;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_putpalettealphas(ImagingObject* self, PyObject* args)
{
    int i;
    UINT8 *values;
    int length;
    if (!PyArg_ParseTuple(args, "s#", &values, &length))
        return NULL;

    if (!self->image->palette) {
        PyErr_SetString(PyExc_ValueError, no_palette);
        return NULL;
    }

    if (length  > 256) {
        PyErr_SetString(PyExc_ValueError, outside_palette);
        return NULL;
    }

    strcpy(self->image->palette->mode, "RGBA");
    for (i=0; i<length; i++) {
        self->image->palette->palette[i*4+3] = (UINT8) values[i];
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_putpixel(ImagingObject* self, PyObject* args)
{
    Imaging im;
    char ink[4];

    int x, y;
    PyObject* color;
    if (!PyArg_ParseTuple(args, "(ii)O", &x, &y, &color))
        return NULL;

    im = self->image;

    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize) {
        PyErr_SetString(PyExc_IndexError, outside_image);
        return NULL;
    }

    if (!getink(color, im, ink))
        return NULL;

    if (self->access)
        self->access->put_pixel(im, x, y, ink);

    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef WITH_RANKFILTER
static PyObject*
_rankfilter(ImagingObject* self, PyObject* args)
{
    int size, rank;
    if (!PyArg_ParseTuple(args, "ii", &size, &rank))
        return NULL;

    return PyImagingNew(ImagingRankFilter(self->image, size, rank));
}
#endif

static PyObject*
_resize(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    int xsize, ysize;
    int filter = IMAGING_TRANSFORM_NEAREST;
    if (!PyArg_ParseTuple(args, "(ii)|i", &xsize, &ysize, &filter))
        return NULL;

    imIn = self->image;

    if (imIn->xsize == xsize && imIn->ysize == ysize) {
        imOut = ImagingCopy(imIn);
    }
    else if ( ! filter) {
        double a[6];

        memset(a, 0, sizeof a);
        a[1] = (double) imIn->xsize / xsize;
        a[5] = (double) imIn->ysize / ysize;

        imOut = ImagingNew(imIn->mode, xsize, ysize);

        imOut = ImagingTransformAffine(
            imOut, imIn,
            0, 0, xsize, ysize,
            a, filter, 1);
    }
    else {
        imOut = ImagingResample(imIn, xsize, ysize, filter);
    }

    return PyImagingNew(imOut);
}

static PyObject*
_rotate(ImagingObject* self, PyObject* args)
{
    Imaging imOut;
    Imaging imIn;

    double theta;
    int filter = IMAGING_TRANSFORM_NEAREST;
    if (!PyArg_ParseTuple(args, "d|i", &theta, &filter))
        return NULL;

    imIn = self->image;

    theta = fmod(theta, 360.0);
    if (theta < 0.0)
    theta += 360;

    if (filter && imIn->type != IMAGING_TYPE_SPECIAL) {
        /* Rotate with resampling filter */
        imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    (void) ImagingRotate(imOut, imIn, theta, filter);
    } else if (theta == 90.0 || theta == 270.0) {
        /* Use fast version */
        imOut = ImagingNew(imIn->mode, imIn->ysize, imIn->xsize);
        if (imOut) {
            if (theta == 90.0)
                (void) ImagingRotate90(imOut, imIn);
            else
                (void) ImagingRotate270(imOut, imIn);
        }
    } else {
        imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
        if (imOut) {
            if (theta == 0.0)
                /* No rotation: simply copy the input image */
                (void) ImagingCopy2(imOut, imIn);
            else if (theta == 180.0)
                /* Use fast version */
                (void) ImagingRotate180(imOut, imIn);
            else
                /* Use ordinary version */
                (void) ImagingRotate(imOut, imIn, theta, 0);
        }
    }

    return PyImagingNew(imOut);
}

#define IS_RGB(mode)\
    (!strcmp(mode, "RGB") || !strcmp(mode, "RGBA") || !strcmp(mode, "RGBX"))

static PyObject*
im_setmode(ImagingObject* self, PyObject* args)
{
    /* attempt to modify the mode of an image in place */

    Imaging im;

    char* mode;
    int modelen;
    if (!PyArg_ParseTuple(args, "s#:setmode", &mode, &modelen))
    return NULL;

    im = self->image;

    /* move all logic in here to the libImaging primitive */

    if (!strcmp(im->mode, mode)) {
        ; /* same mode; always succeeds */
    } else if (IS_RGB(im->mode) && IS_RGB(mode)) {
        /* color to color */
        strcpy(im->mode, mode);
        im->bands = modelen;
        if (!strcmp(mode, "RGBA"))
            (void) ImagingFillBand(im, 3, 255);
    } else {
        /* trying doing an in-place conversion */
        if (!ImagingConvertInPlace(im, mode))
            return NULL;
    }

    if (self->access)
        ImagingAccessDelete(im, self->access);
    self->access = ImagingAccessNew(im);

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject*
_transform2(ImagingObject* self, PyObject* args)
{
    static const char* wrong_number = "wrong number of matrix entries";

    Imaging imIn;
    Imaging imOut;
    int n;
    double *a;

    ImagingObject* imagep;
    int x0, y0, x1, y1;
    int method;
    PyObject* data;
    int filter = IMAGING_TRANSFORM_NEAREST;
    int fill = 1;
    if (!PyArg_ParseTuple(args, "(iiii)O!iO|ii",
                          &x0, &y0, &x1, &y1,
              &Imaging_Type, &imagep,
                          &method, &data,
                          &filter, &fill))
    return NULL;

    switch (method) {
    case IMAGING_TRANSFORM_AFFINE:
        n = 6;
        break;
    case IMAGING_TRANSFORM_PERSPECTIVE:
        n = 8;
        break;
    case IMAGING_TRANSFORM_QUAD:
        n = 8;
        break;
    default:
        n = -1; /* force error */
    }

    a = getlist(data, &n, wrong_number, TYPE_DOUBLE);
    if (!a)
        return NULL;

    imOut = self->image;
    imIn = imagep->image;

    /* FIXME: move transform dispatcher into libImaging */

    switch (method) {
    case IMAGING_TRANSFORM_AFFINE:
        imOut = ImagingTransformAffine(
            imOut, imIn, x0, y0, x1, y1, a, filter, 1
            );
        break;
    case IMAGING_TRANSFORM_PERSPECTIVE:
        imOut = ImagingTransformPerspective(
            imOut, imIn, x0, y0, x1, y1, a, filter, 1
            );
        break;
    case IMAGING_TRANSFORM_QUAD:
        imOut = ImagingTransformQuad(
            imOut, imIn, x0, y0, x1, y1, a, filter, 1
            );
        break;
    default:
        (void) ImagingError_ValueError("bad transform method");
    }

    free(a);

    if (!imOut)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_transpose(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    int op;
    if (!PyArg_ParseTuple(args, "i", &op))
    return NULL;

    imIn = self->image;

    switch (op) {
    case 0: /* flip left right */
    case 1: /* flip top bottom */
    case 3: /* rotate 180 */
        imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
        break;
    case 2: /* rotate 90 */
    case 4: /* rotate 270 */
    case 5: /* transpose */
        imOut = ImagingNew(imIn->mode, imIn->ysize, imIn->xsize);
        break;
    default:
        PyErr_SetString(PyExc_ValueError, "No such transpose operation");
        return NULL;
    }

    if (imOut)
        switch (op) {
        case 0:
            (void) ImagingFlipLeftRight(imOut, imIn);
            break;
        case 1:
            (void) ImagingFlipTopBottom(imOut, imIn);
            break;
        case 2:
            (void) ImagingRotate90(imOut, imIn);
            break;
        case 3:
            (void) ImagingRotate180(imOut, imIn);
            break;
        case 4:
            (void) ImagingRotate270(imOut, imIn);
            break;
        case 5:
            (void) ImagingTranspose(imOut, imIn);
            break;
        }

    return PyImagingNew(imOut);
}

#ifdef WITH_UNSHARPMASK
static PyObject*
_unsharp_mask(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    float radius;
    int percent, threshold;
    if (!PyArg_ParseTuple(args, "fii", &radius, &percent, &threshold))
        return NULL;

    imIn = self->image;
    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut)
        return NULL;

    if (!ImagingUnsharpMask(imOut, imIn, radius, percent, threshold))
        return NULL;

    return PyImagingNew(imOut);
}
#endif

static PyObject*
_box_blur(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    float radius;
    int n = 1;
    if (!PyArg_ParseTuple(args, "f|i", &radius, &n))
        return NULL;

    imIn = self->image;
    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut)
        return NULL;

    if (!ImagingBoxBlur(imOut, imIn, radius, n))
        return NULL;

    return PyImagingNew(imOut);
}

/* -------------------------------------------------------------------- */

static PyObject*
_isblock(ImagingObject* self, PyObject* args)
{
    return PyInt_FromLong((long) self->image->block);
}

static PyObject*
_getbbox(ImagingObject* self, PyObject* args)
{
    int bbox[4];
    if (!ImagingGetBBox(self->image, bbox)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return Py_BuildValue("iiii", bbox[0], bbox[1], bbox[2], bbox[3]);
}

static PyObject*
_getcolors(ImagingObject* self, PyObject* args)
{
    ImagingColorItem* items;
    int i, colors;
    PyObject* out;

    int maxcolors = 256;
    if (!PyArg_ParseTuple(args, "i:getcolors", &maxcolors))
        return NULL;

    items = ImagingGetColors(self->image, maxcolors, &colors);
    if (!items)
        return NULL;

    if (colors > maxcolors) {
        out = Py_None;
        Py_INCREF(out);
    } else {
        out = PyList_New(colors);
        for (i = 0; i < colors; i++) {
            ImagingColorItem* v = &items[i];
            PyObject* item = Py_BuildValue(
                "iN", v->count, getpixel(self->image, self->access, v->x, v->y)
                );
            PyList_SetItem(out, i, item);
        }
    }

    free(items);

    return out;
}

static PyObject*
_getextrema(ImagingObject* self, PyObject* args)
{
    union {
        UINT8 u[2];
        INT32 i[2];
        FLOAT32 f[2];
    } extrema;
    int status;

    status = ImagingGetExtrema(self->image, &extrema);
    if (status < 0)
        return NULL;

    if (status)
        switch (self->image->type) {
        case IMAGING_TYPE_UINT8:
            return Py_BuildValue("BB", extrema.u[0], extrema.u[1]);
        case IMAGING_TYPE_INT32:
            return Py_BuildValue("ii", extrema.i[0], extrema.i[1]);
        case IMAGING_TYPE_FLOAT32:
            return Py_BuildValue("dd", extrema.f[0], extrema.f[1]);
        }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_getprojection(ImagingObject* self, PyObject* args)
{
    unsigned char* xprofile;
    unsigned char* yprofile;
    PyObject* result;

    xprofile = malloc(self->image->xsize);
    yprofile = malloc(self->image->ysize);

    if (xprofile == NULL || yprofile == NULL) {
        free(xprofile);
        free(yprofile);
        return PyErr_NoMemory();
    }

    ImagingGetProjection(self->image, (unsigned char *)xprofile, (unsigned char *)yprofile);

    result = Py_BuildValue(PY_ARG_BYTES_LENGTH PY_ARG_BYTES_LENGTH,
                           xprofile, self->image->xsize,
                           yprofile, self->image->ysize);

    free(xprofile);
    free(yprofile);

    return result;
}

/* -------------------------------------------------------------------- */

static PyObject*
_getband(ImagingObject* self, PyObject* args)
{
    int band;

    if (!PyArg_ParseTuple(args, "i", &band))
        return NULL;

    return PyImagingNew(ImagingGetBand(self->image, band));
}

static PyObject*
_fillband(ImagingObject* self, PyObject* args)
{
    int band;
    int color;

    if (!PyArg_ParseTuple(args, "ii", &band, &color))
        return NULL;

    if (!ImagingFillBand(self->image, band, color))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_putband(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;
    int band;
    if (!PyArg_ParseTuple(args, "O!i",
                          &Imaging_Type, &imagep,
                          &band))
        return NULL;

    if (!ImagingPutBand(self->image, imagep->image, band))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

/* -------------------------------------------------------------------- */

#ifdef WITH_IMAGECHOPS

static PyObject*
_chop_invert(ImagingObject* self, PyObject* args)
{
    return PyImagingNew(ImagingNegative(self->image));
}

static PyObject*
_chop_lighter(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopLighter(self->image, imagep->image));
}

static PyObject*
_chop_darker(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopDarker(self->image, imagep->image));
}

static PyObject*
_chop_difference(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopDifference(self->image, imagep->image));
}

static PyObject*
_chop_multiply(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopMultiply(self->image, imagep->image));
}

static PyObject*
_chop_screen(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopScreen(self->image, imagep->image));
}

static PyObject*
_chop_add(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;
    float scale;
    int offset;

    scale = 1.0;
    offset = 0;

    if (!PyArg_ParseTuple(args, "O!|fi", &Imaging_Type, &imagep,
                          &scale, &offset))
        return NULL;

    return PyImagingNew(ImagingChopAdd(self->image, imagep->image,
                       scale, offset));
}

static PyObject*
_chop_subtract(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;
    float scale;
    int offset;

    scale = 1.0;
    offset = 0;

    if (!PyArg_ParseTuple(args, "O!|fi", &Imaging_Type, &imagep,
                          &scale, &offset))
        return NULL;

    return PyImagingNew(ImagingChopSubtract(self->image, imagep->image,
                        scale, offset));
}

static PyObject*
_chop_and(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopAnd(self->image, imagep->image));
}

static PyObject*
_chop_or(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopOr(self->image, imagep->image));
}

static PyObject*
_chop_xor(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopXor(self->image, imagep->image));
}

static PyObject*
_chop_add_modulo(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopAddModulo(self->image, imagep->image));
}

static PyObject*
_chop_subtract_modulo(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
        return NULL;

    return PyImagingNew(ImagingChopSubtractModulo(self->image, imagep->image));
}

#endif


/* -------------------------------------------------------------------- */

#ifdef WITH_IMAGEDRAW

static PyObject*
_font_new(PyObject* self_, PyObject* args)
{
    ImagingFontObject *self;
    int i, y0, y1;
    static const char* wrong_length = "descriptor table has wrong size";

    ImagingObject* imagep;
    unsigned char* glyphdata;
    int glyphdata_length;
    if (!PyArg_ParseTuple(args, "O!"PY_ARG_BYTES_LENGTH,
                          &Imaging_Type, &imagep,
                          &glyphdata, &glyphdata_length))
        return NULL;

    if (glyphdata_length != 256 * 20) {
        PyErr_SetString(PyExc_ValueError, wrong_length);
        return NULL;
    }

    self = PyObject_New(ImagingFontObject, &ImagingFont_Type);
    if (self == NULL)
        return NULL;

    /* glyph bitmap */
    self->bitmap = imagep->image;

    y0 = y1 = 0;

    /* glyph glyphs */
    for (i = 0; i < 256; i++) {
        self->glyphs[i].dx = S16(B16(glyphdata, 0));
        self->glyphs[i].dy = S16(B16(glyphdata, 2));
        self->glyphs[i].dx0 = S16(B16(glyphdata, 4));
        self->glyphs[i].dy0 = S16(B16(glyphdata, 6));
        self->glyphs[i].dx1 = S16(B16(glyphdata, 8));
        self->glyphs[i].dy1 = S16(B16(glyphdata, 10));
        self->glyphs[i].sx0 = S16(B16(glyphdata, 12));
        self->glyphs[i].sy0 = S16(B16(glyphdata, 14));
        self->glyphs[i].sx1 = S16(B16(glyphdata, 16));
        self->glyphs[i].sy1 = S16(B16(glyphdata, 18));
        if (self->glyphs[i].dy0 < y0)
            y0 = self->glyphs[i].dy0;
        if (self->glyphs[i].dy1 > y1)
            y1 = self->glyphs[i].dy1;
        glyphdata += 20;
    }

    self->baseline = -y0;
    self->ysize = y1 - y0;

    /* keep a reference to the bitmap object */
    Py_INCREF(imagep);
    self->ref = imagep;

    return (PyObject*) self;
}

static void
_font_dealloc(ImagingFontObject* self)
{
    Py_XDECREF(self->ref);
    PyObject_Del(self);
}

static inline int
textwidth(ImagingFontObject* self, const unsigned char* text)
{
    int xsize;

    for (xsize = 0; *text; text++)
        xsize += self->glyphs[*text].dx;

    return xsize;
}

void _font_text_asBytes(PyObject* encoded_string, unsigned char** text){
    PyObject* bytes = NULL;

    *text = NULL;

    if (PyUnicode_CheckExact(encoded_string)){
        bytes = PyUnicode_AsLatin1String(encoded_string);
    } else if (PyBytes_Check(encoded_string)) {
        bytes = encoded_string;
    }
    if (bytes) {
        *text = (unsigned char*)PyBytes_AsString(bytes);
        return;
    }

#if PY_VERSION_HEX < 0x03000000
    /* likely case here is py2.x with an ordinary string.
       but this isn't defined in Py3.x */
    if (PyString_Check(encoded_string)) {
        *text = (unsigned char *)PyString_AsString(encoded_string);
    }
#endif
}


static PyObject*
_font_getmask(ImagingFontObject* self, PyObject* args)
{
    Imaging im;
    Imaging bitmap;
    int x, b;
    int i=0;
    int status;
    Glyph* glyph;

    PyObject* encoded_string;

    unsigned char* text;
    char* mode = "";

    if (!PyArg_ParseTuple(args, "O|s:getmask",  &encoded_string, &mode)){
        return NULL;
    }

    _font_text_asBytes(encoded_string, &text);
    if (!text) {
        return NULL;
    }

    im = ImagingNew(self->bitmap->mode, textwidth(self, text), self->ysize);
    if (!im) {
        return NULL;
    }

    b = 0;
    (void) ImagingFill(im, &b);

    b = self->baseline;
    for (x = 0; text[i]; i++) {
        glyph = &self->glyphs[text[i]];
        bitmap = ImagingCrop(
            self->bitmap,
            glyph->sx0, glyph->sy0, glyph->sx1, glyph->sy1
            );
        if (!bitmap)
            goto failed;
        status = ImagingPaste(
            im, bitmap, NULL,
            glyph->dx0+x, glyph->dy0+b, glyph->dx1+x, glyph->dy1+b
            );
        ImagingDelete(bitmap);
        if (status < 0)
            goto failed;
        x = x + glyph->dx;
        b = b + glyph->dy;
    }
    return PyImagingNew(im);

  failed:
    ImagingDelete(im);
    return NULL;
}

static PyObject*
_font_getsize(ImagingFontObject* self, PyObject* args)
{
    unsigned char* text;
    PyObject* encoded_string;

    if (!PyArg_ParseTuple(args, "O:getsize", &encoded_string))
        return NULL;

    _font_text_asBytes(encoded_string, &text);
    if (!text) {
        return NULL;
    }

    return Py_BuildValue("ii", textwidth(self, text), self->ysize);
}

static struct PyMethodDef _font_methods[] = {
    {"getmask", (PyCFunction)_font_getmask, 1},
    {"getsize", (PyCFunction)_font_getsize, 1},
    {NULL, NULL} /* sentinel */
};

/* -------------------------------------------------------------------- */

static PyObject*
_draw_new(PyObject* self_, PyObject* args)
{
    ImagingDrawObject *self;

    ImagingObject* imagep;
    int blend = 0;
    if (!PyArg_ParseTuple(args, "O!|i", &Imaging_Type, &imagep, &blend))
        return NULL;

    self = PyObject_New(ImagingDrawObject, &ImagingDraw_Type);
    if (self == NULL)
        return NULL;

    /* keep a reference to the image object */
    Py_INCREF(imagep);
    self->image = imagep;

    self->ink[0] = self->ink[1] = self->ink[2] = self->ink[3] = 0;

    self->blend = blend;

    return (PyObject*) self;
}

static void
_draw_dealloc(ImagingDrawObject* self)
{
    Py_XDECREF(self->image);
    PyObject_Del(self);
}

extern int PyPath_Flatten(PyObject* data, double **xy);

static PyObject*
_draw_ink(ImagingDrawObject* self, PyObject* args)
{
    INT32 ink = 0;
    PyObject* color;
    char* mode = NULL; /* not used in this release */
    if (!PyArg_ParseTuple(args, "O|s", &color, &mode))
        return NULL;

    if (!getink(color, self->image->image, (char*) &ink))
        return NULL;

    return PyInt_FromLong((int) ink);
}

static PyObject*
_draw_arc(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink;
    int start, end;
    int op = 0;
    if (!PyArg_ParseTuple(args, "Oiii|i", &data, &start, &end, &ink))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n != 2) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain exactly 2 coordinates"
                        );
        return NULL;
    }

    n = ImagingDrawArc(self->image->image,
                       (int) xy[0], (int) xy[1],
                       (int) xy[2], (int) xy[3],
                       start, end, &ink, op
                       );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_bitmap(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int n;

    PyObject *data;
    ImagingObject* bitmap;
    int ink;
    if (!PyArg_ParseTuple(args, "OO!i", &data, &Imaging_Type, &bitmap, &ink))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n != 1) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain exactly 1 coordinate"
                        );
        return NULL;
    }

    n = ImagingDrawBitmap(
        self->image->image, (int) xy[0], (int) xy[1], bitmap->image,
        &ink, self->blend
        );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_chord(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink, fill;
    int start, end;
    if (!PyArg_ParseTuple(args, "Oiiii",
                          &data, &start, &end, &ink, &fill))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n != 2) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain exactly 2 coordinates"
                        );
        return NULL;
    }

    n = ImagingDrawChord(self->image->image,
                         (int) xy[0], (int) xy[1],
                         (int) xy[2], (int) xy[3],
                         start, end, &ink, fill, self->blend
                         );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_ellipse(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &fill))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n != 2) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain exactly 2 coordinates"
                        );
        return NULL;
    }

    n = ImagingDrawEllipse(self->image->image,
                           (int) xy[0], (int) xy[1],
                           (int) xy[2], (int) xy[3],
                           &ink, fill, self->blend
                           );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_line(ImagingDrawObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    int ink;
    if (!PyArg_ParseTuple(args, "(ii)(ii)i", &x0, &y0, &x1, &y1, &ink))
        return NULL;

    if (ImagingDrawLine(self->image->image, x0, y0, x1, y1,
                        &ink, self->blend) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_lines(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int i, n;

    PyObject *data;
    int ink;
    int width = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &width))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;

    if (width <= 1) {
        double *p = NULL;
    for (i = 0; i < n-1; i++) {
            p = &xy[i+i];
            if (ImagingDrawLine(
                    self->image->image,
                    (int) p[0], (int) p[1], (int) p[2], (int) p[3],
                    &ink, self->blend) < 0) {
                free(xy);
                return NULL;
            }
        }
        if (p) /* draw last point */
            ImagingDrawPoint(
                    self->image->image,
                    (int) p[2], (int) p[3],
                    &ink, self->blend
                );
    } else {
        for (i = 0; i < n-1; i++) {
            double *p = &xy[i+i];
            if (ImagingDrawWideLine(
                    self->image->image,
                    (int) p[0], (int) p[1], (int) p[2], (int) p[3],
                    &ink, width, self->blend) < 0) {
                free(xy);
                return NULL;
            }
        }
    }

    free(xy);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_point(ImagingDrawObject* self, PyObject* args)
{
    int x, y;
    int ink;
    if (!PyArg_ParseTuple(args, "(ii)i", &x, &y, &ink))
        return NULL;

    if (ImagingDrawPoint(self->image->image, x, y, &ink, self->blend) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_points(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int i, n;

    PyObject *data;
    int ink;
    if (!PyArg_ParseTuple(args, "Oi", &data, &ink))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;

    for (i = 0; i < n; i++) {
    double *p = &xy[i+i];
    if (ImagingDrawPoint(self->image->image, (int) p[0], (int) p[1],
                             &ink, self->blend) < 0) {
        free(xy);
        return NULL;
    }
    }

    free(xy);

    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef    WITH_ARROW

/* from outline.c */
extern ImagingOutline PyOutline_AsOutline(PyObject* outline);

static PyObject*
_draw_outline(ImagingDrawObject* self, PyObject* args)
{
    ImagingOutline outline;

    PyObject* outline_;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &outline_, &ink, &fill))
        return NULL;

    outline = PyOutline_AsOutline(outline_);
    if (!outline) {
        PyErr_SetString(PyExc_TypeError, "expected outline object");
        return NULL;
    }

    if (ImagingDrawOutline(self->image->image, outline,
                           &ink, fill, self->blend) < 0)
    return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

#endif

static PyObject*
_draw_pieslice(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink, fill;
    int start, end;
    if (!PyArg_ParseTuple(args, "Oiiii", &data, &start, &end, &ink, &fill))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n != 2) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain exactly 2 coordinates"
                        );
        return NULL;
    }

    n = ImagingDrawPieslice(self->image->image,
                            (int) xy[0], (int) xy[1],
                            (int) xy[2], (int) xy[3],
                            start, end, &ink, fill, self->blend
                            );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_polygon(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int *ixy;
    int n, i;

    PyObject* data;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &fill))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n < 2) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain at least 2 coordinates"
                        );
        return NULL;
    }

    /* Copy list of vertices to array */
    ixy = (int*) malloc(n * 2 * sizeof(int));

    for (i = 0; i < n; i++) {
        ixy[i+i] = (int) xy[i+i];
        ixy[i+i+1] = (int) xy[i+i+1];
    }

    free(xy);

    if (ImagingDrawPolygon(self->image->image, n, ixy,
                           &ink, fill, self->blend) < 0) {
        free(ixy);
        return NULL;
    }

    free(ixy);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw_rectangle(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &fill))
        return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
        return NULL;
    if (n != 2) {
        PyErr_SetString(PyExc_TypeError,
                        "coordinate list must contain exactly 2 coordinates"
                        );
        return NULL;
    }

    n = ImagingDrawRectangle(self->image->image,
                             (int) xy[0], (int) xy[1],
                             (int) xy[2], (int) xy[3],
                             &ink, fill, self->blend
                             );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef _draw_methods[] = {
#ifdef WITH_IMAGEDRAW
    /* Graphics (ImageDraw) */
    {"draw_line", (PyCFunction)_draw_line, 1},
    {"draw_lines", (PyCFunction)_draw_lines, 1},
#ifdef WITH_ARROW
    {"draw_outline", (PyCFunction)_draw_outline, 1},
#endif
    {"draw_polygon", (PyCFunction)_draw_polygon, 1},
    {"draw_rectangle", (PyCFunction)_draw_rectangle, 1},
    {"draw_point", (PyCFunction)_draw_point, 1},
    {"draw_points", (PyCFunction)_draw_points, 1},
    {"draw_arc", (PyCFunction)_draw_arc, 1},
    {"draw_bitmap", (PyCFunction)_draw_bitmap, 1},
    {"draw_chord", (PyCFunction)_draw_chord, 1},
    {"draw_ellipse", (PyCFunction)_draw_ellipse, 1},
    {"draw_pieslice", (PyCFunction)_draw_pieslice, 1},
    {"draw_ink", (PyCFunction)_draw_ink, 1},
#endif
    {NULL, NULL} /* sentinel */
};

#endif


static PyObject*
pixel_access_new(ImagingObject* imagep, PyObject* args)
{
    PixelAccessObject *self;

    int readonly = 0;
    if (!PyArg_ParseTuple(args, "|i", &readonly))
        return NULL;

    self = PyObject_New(PixelAccessObject, &PixelAccess_Type);
    if (self == NULL)
        return NULL;

    /* keep a reference to the image object */
    Py_INCREF(imagep);
    self->image = imagep;

    self->readonly = readonly;

    return (PyObject*) self;
}

static void
pixel_access_dealloc(PixelAccessObject* self)
{
    Py_XDECREF(self->image);
    PyObject_Del(self);
}

static PyObject *
pixel_access_getitem(PixelAccessObject *self, PyObject *xy)
{
    int x, y;
    if (_getxy(xy, &x, &y))
        return NULL;

    return getpixel(self->image->image, self->image->access, x, y);
}

static int
pixel_access_setitem(PixelAccessObject *self, PyObject *xy, PyObject *color)
{
    Imaging im = self->image->image;
    char ink[4];
    int x, y;

    if (self->readonly) {
        (void) ImagingError_ValueError(readonly);
        return -1;
    }

    if (_getxy(xy, &x, &y))
        return -1;

    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize) {
        PyErr_SetString(PyExc_IndexError, outside_image);
        return -1;
    }

    if (!color) /* FIXME: raise exception? */
        return 0;

    if (!getink(color, im, ink))
        return -1;

    self->image->access->put_pixel(im, x, y, ink);

    return 0;
}

/* -------------------------------------------------------------------- */
/* EFFECTS (experimental)                            */
/* -------------------------------------------------------------------- */

#ifdef WITH_EFFECTS

static PyObject*
_effect_mandelbrot(ImagingObject* self, PyObject* args)
{
    int xsize = 512;
    int ysize = 512;
    double extent[4];
    int quality = 100;

    extent[0] = -3; extent[1] = -2.5;
    extent[2] = 2;  extent[3] = 2.5;

    if (!PyArg_ParseTuple(args, "|(ii)(dddd)i", &xsize, &ysize,
                          &extent[0], &extent[1], &extent[2], &extent[3],
                          &quality))
    return NULL;

    return PyImagingNew(ImagingEffectMandelbrot(xsize, ysize, extent, quality));
}

static PyObject*
_effect_noise(ImagingObject* self, PyObject* args)
{
    int xsize, ysize;
    float sigma = 128;
    if (!PyArg_ParseTuple(args, "(ii)|f", &xsize, &ysize, &sigma))
        return NULL;

    return PyImagingNew(ImagingEffectNoise(xsize, ysize, sigma));
}

static PyObject*
_effect_spread(ImagingObject* self, PyObject* args)
{
    int dist;

    if (!PyArg_ParseTuple(args, "i", &dist))
        return NULL;

    return PyImagingNew(ImagingEffectSpread(self->image, dist));
}

#endif

/* -------------------------------------------------------------------- */
/* UTILITIES                                */
/* -------------------------------------------------------------------- */

static PyObject*
_crc32(PyObject* self, PyObject* args)
{
    unsigned char* buffer;
    int bytes;
    int hi, lo;
    UINT32 crc;

    hi = lo = 0;

    if (!PyArg_ParseTuple(args, PY_ARG_BYTES_LENGTH"|(ii)",
                          &buffer, &bytes, &hi, &lo))
        return NULL;

    crc = ((UINT32) (hi & 0xFFFF) << 16) + (lo & 0xFFFF);

    crc = ImagingCRC32(crc, (unsigned char *)buffer, bytes);

    return Py_BuildValue("ii", (crc >> 16) & 0xFFFF, crc & 0xFFFF);
}

static PyObject*
_getcodecstatus(PyObject* self, PyObject* args)
{
    int status;
    char* msg;

    if (!PyArg_ParseTuple(args, "i", &status))
        return NULL;

    switch (status) {
    case IMAGING_CODEC_OVERRUN:
        msg = "buffer overrun"; break;
    case IMAGING_CODEC_BROKEN:
        msg = "broken data stream"; break;
    case IMAGING_CODEC_UNKNOWN:
        msg = "unrecognized data stream contents"; break;
    case IMAGING_CODEC_CONFIG:
        msg = "codec configuration error"; break;
    case IMAGING_CODEC_MEMORY:
        msg = "out of memory"; break;
    default:
        Py_RETURN_NONE;
    }

    return PyUnicode_FromString(msg);
}

/* -------------------------------------------------------------------- */
/* DEBUGGING HELPERS                            */
/* -------------------------------------------------------------------- */


#ifdef WITH_DEBUG

static PyObject*
_save_ppm(ImagingObject* self, PyObject* args)
{
    char* filename;

    if (!PyArg_ParseTuple(args, "s", &filename))
        return NULL;

    if (!ImagingSavePPM(self->image, filename))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

#endif

/* -------------------------------------------------------------------- */

/* methods */

static struct PyMethodDef methods[] = {

    /* Put commonly used methods first */
    {"getpixel", (PyCFunction)_getpixel, 1},
    {"putpixel", (PyCFunction)_putpixel, 1},

    {"pixel_access", (PyCFunction)pixel_access_new, 1},

    /* Standard processing methods (Image) */
    {"convert", (PyCFunction)_convert, 1},
    {"convert2", (PyCFunction)_convert2, 1},
    {"convert_matrix", (PyCFunction)_convert_matrix, 1},
    {"convert_transparent", (PyCFunction)_convert_transparent, 1},
    {"copy", (PyCFunction)_copy, 1},
    {"copy2", (PyCFunction)_copy2, 1},
#ifdef WITH_CRACKCODE
    {"crackcode", (PyCFunction)_crackcode, 1},
#endif
    {"crop", (PyCFunction)_crop, 1},
    {"expand", (PyCFunction)_expand_image, 1},
    {"filter", (PyCFunction)_filter, 1},
    {"histogram", (PyCFunction)_histogram, 1},
#ifdef WITH_MODEFILTER
    {"modefilter", (PyCFunction)_modefilter, 1},
#endif
    {"offset", (PyCFunction)_offset, 1},
    {"paste", (PyCFunction)_paste, 1},
    {"point", (PyCFunction)_point, 1},
    {"point_transform", (PyCFunction)_point_transform, 1},
    {"putdata", (PyCFunction)_putdata, 1},
#ifdef WITH_QUANTIZE
    {"quantize", (PyCFunction)_quantize, 1},
#endif
#ifdef WITH_RANKFILTER
    {"rankfilter", (PyCFunction)_rankfilter, 1},
#endif
    {"resize", (PyCFunction)_resize, 1},
    // There were two methods for image resize before.
    // Starting from Pillow 2.7.0 stretch is depreciated.
    {"stretch", (PyCFunction)_resize, 1},
    {"rotate", (PyCFunction)_rotate, 1},
    {"transpose", (PyCFunction)_transpose, 1},
    {"transform2", (PyCFunction)_transform2, 1},

    {"isblock", (PyCFunction)_isblock, 1},

    {"getbbox", (PyCFunction)_getbbox, 1},
    {"getcolors", (PyCFunction)_getcolors, 1},
    {"getextrema", (PyCFunction)_getextrema, 1},
    {"getprojection", (PyCFunction)_getprojection, 1},

    {"getband", (PyCFunction)_getband, 1},
    {"putband", (PyCFunction)_putband, 1},
    {"fillband", (PyCFunction)_fillband, 1},

    {"setmode", (PyCFunction)im_setmode, 1},

    {"getpalette", (PyCFunction)_getpalette, 1},
    {"getpalettemode", (PyCFunction)_getpalettemode, 1},
    {"putpalette", (PyCFunction)_putpalette, 1},
    {"putpalettealpha", (PyCFunction)_putpalettealpha, 1},
    {"putpalettealphas", (PyCFunction)_putpalettealphas, 1},

#ifdef WITH_IMAGECHOPS
    /* Channel operations (ImageChops) */
    {"chop_invert", (PyCFunction)_chop_invert, 1},
    {"chop_lighter", (PyCFunction)_chop_lighter, 1},
    {"chop_darker", (PyCFunction)_chop_darker, 1},
    {"chop_difference", (PyCFunction)_chop_difference, 1},
    {"chop_multiply", (PyCFunction)_chop_multiply, 1},
    {"chop_screen", (PyCFunction)_chop_screen, 1},
    {"chop_add", (PyCFunction)_chop_add, 1},
    {"chop_subtract", (PyCFunction)_chop_subtract, 1},
    {"chop_add_modulo", (PyCFunction)_chop_add_modulo, 1},
    {"chop_subtract_modulo", (PyCFunction)_chop_subtract_modulo, 1},
    {"chop_and", (PyCFunction)_chop_and, 1},
    {"chop_or", (PyCFunction)_chop_or, 1},
    {"chop_xor", (PyCFunction)_chop_xor, 1},
#endif

#ifdef WITH_UNSHARPMASK
    /* Kevin Cazabon's unsharpmask extension */
    {"gaussian_blur", (PyCFunction)_gaussian_blur, 1},
    {"unsharp_mask", (PyCFunction)_unsharp_mask, 1},
#endif

    {"box_blur", (PyCFunction)_box_blur, 1},    

#ifdef WITH_EFFECTS
    /* Special effects */
    {"effect_spread", (PyCFunction)_effect_spread, 1},
#endif

    /* Misc. */
    {"new_array", (PyCFunction)_new_array, 1},
    {"new_block", (PyCFunction)_new_block, 1},

#ifdef WITH_DEBUG
    {"save_ppm", (PyCFunction)_save_ppm, 1},
#endif

    {NULL, NULL} /* sentinel */
};


/* attributes */

static PyObject*
_getattr_mode(ImagingObject* self, void* closure)
{
    return PyUnicode_FromString(self->image->mode);
}

static PyObject*
_getattr_size(ImagingObject* self, void* closure)
{
    return Py_BuildValue("ii", self->image->xsize, self->image->ysize);
}

static PyObject*
_getattr_bands(ImagingObject* self, void* closure)
{
    return PyInt_FromLong(self->image->bands);
}

static PyObject*
_getattr_id(ImagingObject* self, void* closure)
{
    return PyInt_FromSsize_t((Py_ssize_t) self->image);
}

static PyObject*
_getattr_ptr(ImagingObject* self, void* closure)
{
#if (PY_VERSION_HEX >= 0x02070000 && PY_VERSION_HEX < 0x03000000) || PY_VERSION_HEX >= 0x03010000
    return PyCapsule_New(self->image, IMAGING_MAGIC, NULL);
#else
    return PyCObject_FromVoidPtrAndDesc(self->image, IMAGING_MAGIC, NULL);
#endif
}

static PyObject*
_getattr_unsafe_ptrs(ImagingObject* self, void* closure)
{
    return Py_BuildValue("(ss)(si)(si)(si)(si)(si)(sn)(sn)(sn)(sn)(sn)(si)(si)(sn)",
                         "mode", self->image->mode,
                         "type", self->image->type,
                         "depth", self->image->depth,
                         "bands", self->image->bands,
                         "xsize", self->image->xsize,
                         "ysize", self->image->ysize,
                         "palette", self->image->palette,
                         "image8", self->image->image8,
                         "image32", self->image->image32,
                         "image", self->image->image,
                         "block", self->image->block,
                         "pixelsize", self->image->pixelsize,
                         "linesize", self->image->linesize,
                         "destroy", self->image->destroy
                        );
};


static struct PyGetSetDef getsetters[] = {
    { "mode",   (getter) _getattr_mode },
    { "size",   (getter) _getattr_size },
    { "bands",  (getter) _getattr_bands },
    { "id",     (getter) _getattr_id },
    { "ptr",    (getter) _getattr_ptr },
    { "unsafe_ptrs", (getter) _getattr_unsafe_ptrs },
    { NULL }
};

/* basic sequence semantics */

static Py_ssize_t
image_length(ImagingObject *self)
{
    Imaging im = self->image;

    return (Py_ssize_t) im->xsize * im->ysize;
}

static PyObject *
image_item(ImagingObject *self, Py_ssize_t i)
{
    int x, y;
    Imaging im = self->image;

    if (im->xsize > 0) {
        x = i % im->xsize;
        y = i / im->xsize;
    } else
        x = y = 0; /* leave it to getpixel to raise an exception */

    return getpixel(im, self->access, x, y);
}

static PySequenceMethods image_as_sequence = {
    (lenfunc) image_length, /*sq_length*/
    (binaryfunc) NULL, /*sq_concat*/
    (ssizeargfunc) NULL, /*sq_repeat*/
    (ssizeargfunc) image_item, /*sq_item*/
    (ssizessizeargfunc) NULL, /*sq_slice*/
    (ssizeobjargproc) NULL, /*sq_ass_item*/
    (ssizessizeobjargproc) NULL, /*sq_ass_slice*/
};


/* type description */

static PyTypeObject Imaging_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ImagingCore",        /*tp_name*/
    sizeof(ImagingObject),    /*tp_size*/
    0,                /*tp_itemsize*/
    /* methods */
    (destructor)_dealloc,    /*tp_dealloc*/
    0,                /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number */
    &image_as_sequence,         /*tp_as_sequence */
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
    getsetters,                 /*tp_getset*/
};

#ifdef WITH_IMAGEDRAW

static PyTypeObject ImagingFont_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ImagingFont",        /*tp_name*/
    sizeof(ImagingFontObject),    /*tp_size*/
    0,                /*tp_itemsize*/
    /* methods */
    (destructor)_font_dealloc,    /*tp_dealloc*/
    0,                /*tp_print*/
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
    _font_methods,              /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
};

static PyTypeObject ImagingDraw_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "ImagingDraw",        /*tp_name*/
    sizeof(ImagingDrawObject),    /*tp_size*/
    0,                /*tp_itemsize*/
    /* methods */
    (destructor)_draw_dealloc,    /*tp_dealloc*/
    0,                /*tp_print*/
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
    _draw_methods,              /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
};

#endif

static PyMappingMethods pixel_access_as_mapping = {
    (lenfunc) NULL, /*mp_length*/
    (binaryfunc) pixel_access_getitem, /*mp_subscript*/
    (objobjargproc) pixel_access_setitem, /*mp_ass_subscript*/
};

/* type description */

static PyTypeObject PixelAccess_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "PixelAccess", sizeof(PixelAccessObject), 0,
    /* methods */
    (destructor)pixel_access_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number */
    0, /*tp_as_sequence */
    &pixel_access_as_mapping, /*tp_as_mapping */
    0 /*tp_hash*/
};

/* -------------------------------------------------------------------- */

/* FIXME: this is something of a mess.  Should replace this with
   pluggable codecs, but not before PIL 1.2 */

/* Decoders (in decode.c) */
extern PyObject* PyImaging_BitDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_FliDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GifDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_HexDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_JpegDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_Jpeg2KDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_TiffLzwDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_LibTiffDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_MspDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PackbitsDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PcdDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PcxDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_RawDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_SunRleDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_TgaRleDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_XbmDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_ZipDecoderNew(PyObject* self, PyObject* args);

/* Encoders (in encode.c) */
extern PyObject* PyImaging_EpsEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GifEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_JpegEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_Jpeg2KEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PcxEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_RawEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_XbmEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_ZipEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_LibTiffEncoderNew(PyObject* self, PyObject* args);

/* Display support etc (in display.c) */
#ifdef _WIN32
extern PyObject* PyImaging_CreateWindowWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_DisplayWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_DisplayModeWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GrabScreenWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GrabClipboardWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_ListWindowsWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_EventLoopWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_DrawWmf(PyObject* self, PyObject* args);
#endif

/* Experimental path stuff (in path.c) */
extern PyObject* PyPath_Create(ImagingObject* self, PyObject* args);

/* Experimental outline stuff (in outline.c) */
extern PyObject* PyOutline_Create(ImagingObject* self, PyObject* args);

extern PyObject* PyImaging_Mapper(PyObject* self, PyObject* args);
extern PyObject* PyImaging_MapBuffer(PyObject* self, PyObject* args);

static PyMethodDef functions[] = {

    /* Object factories */
    {"alpha_composite", (PyCFunction)_alpha_composite, 1},
    {"blend", (PyCFunction)_blend, 1},
    {"fill", (PyCFunction)_fill, 1},
    {"new", (PyCFunction)_new, 1},

    {"getcount", (PyCFunction)_getcount, 1},

    /* Functions */
    {"convert", (PyCFunction)_convert2, 1},
    {"copy", (PyCFunction)_copy2, 1},

    /* Codecs */
    {"bit_decoder", (PyCFunction)PyImaging_BitDecoderNew, 1},
    {"eps_encoder", (PyCFunction)PyImaging_EpsEncoderNew, 1},
    {"fli_decoder", (PyCFunction)PyImaging_FliDecoderNew, 1},
    {"gif_decoder", (PyCFunction)PyImaging_GifDecoderNew, 1},
    {"gif_encoder", (PyCFunction)PyImaging_GifEncoderNew, 1},
    {"hex_decoder", (PyCFunction)PyImaging_HexDecoderNew, 1},
    {"hex_encoder", (PyCFunction)PyImaging_EpsEncoderNew, 1}, /* EPS=HEX! */
#ifdef HAVE_LIBJPEG
    {"jpeg_decoder", (PyCFunction)PyImaging_JpegDecoderNew, 1},
    {"jpeg_encoder", (PyCFunction)PyImaging_JpegEncoderNew, 1},
#endif
#ifdef HAVE_OPENJPEG
    {"jpeg2k_decoder", (PyCFunction)PyImaging_Jpeg2KDecoderNew, 1},
    {"jpeg2k_encoder", (PyCFunction)PyImaging_Jpeg2KEncoderNew, 1},
#endif
    {"tiff_lzw_decoder", (PyCFunction)PyImaging_TiffLzwDecoderNew, 1},
#ifdef HAVE_LIBTIFF
    {"libtiff_decoder", (PyCFunction)PyImaging_LibTiffDecoderNew, 1},
    {"libtiff_encoder", (PyCFunction)PyImaging_LibTiffEncoderNew, 1},
#endif
    {"msp_decoder", (PyCFunction)PyImaging_MspDecoderNew, 1},
    {"packbits_decoder", (PyCFunction)PyImaging_PackbitsDecoderNew, 1},
    {"pcd_decoder", (PyCFunction)PyImaging_PcdDecoderNew, 1},
    {"pcx_decoder", (PyCFunction)PyImaging_PcxDecoderNew, 1},
    {"pcx_encoder", (PyCFunction)PyImaging_PcxEncoderNew, 1},
    {"raw_decoder", (PyCFunction)PyImaging_RawDecoderNew, 1},
    {"raw_encoder", (PyCFunction)PyImaging_RawEncoderNew, 1},
    {"sun_rle_decoder", (PyCFunction)PyImaging_SunRleDecoderNew, 1},
    {"tga_rle_decoder", (PyCFunction)PyImaging_TgaRleDecoderNew, 1},
    {"xbm_decoder", (PyCFunction)PyImaging_XbmDecoderNew, 1},
    {"xbm_encoder", (PyCFunction)PyImaging_XbmEncoderNew, 1},
#ifdef HAVE_LIBZ
    {"zip_decoder", (PyCFunction)PyImaging_ZipDecoderNew, 1},
    {"zip_encoder", (PyCFunction)PyImaging_ZipEncoderNew, 1},
#endif

    /* Memory mapping */
#ifdef WITH_MAPPING
#ifdef _WIN32
    {"map", (PyCFunction)PyImaging_Mapper, 1},
#endif
    {"map_buffer", (PyCFunction)PyImaging_MapBuffer, 1},
#endif

    /* Display support */
#ifdef _WIN32
    {"display", (PyCFunction)PyImaging_DisplayWin32, 1},
    {"display_mode", (PyCFunction)PyImaging_DisplayModeWin32, 1},
    {"grabscreen", (PyCFunction)PyImaging_GrabScreenWin32, 1},
    {"grabclipboard", (PyCFunction)PyImaging_GrabClipboardWin32, 1},
    {"createwindow", (PyCFunction)PyImaging_CreateWindowWin32, 1},
    {"eventloop", (PyCFunction)PyImaging_EventLoopWin32, 1},
    {"listwindows", (PyCFunction)PyImaging_ListWindowsWin32, 1},
    {"drawwmf", (PyCFunction)PyImaging_DrawWmf, 1},
#endif

    /* Utilities */
    {"crc32", (PyCFunction)_crc32, 1},
    {"getcodecstatus", (PyCFunction)_getcodecstatus, 1},

    /* Debugging stuff */
    {"open_ppm", (PyCFunction)_open_ppm, 1},

    /* Special effects (experimental) */
#ifdef WITH_EFFECTS
    {"effect_mandelbrot", (PyCFunction)_effect_mandelbrot, 1},
    {"effect_noise", (PyCFunction)_effect_noise, 1},
    {"linear_gradient", (PyCFunction)_linear_gradient, 1},
    {"radial_gradient", (PyCFunction)_radial_gradient, 1},
    {"wedge", (PyCFunction)_linear_gradient, 1}, /* Compatibility */
#endif

    /* Drawing support stuff */
#ifdef WITH_IMAGEDRAW
    {"font", (PyCFunction)_font_new, 1},
    {"draw", (PyCFunction)_draw_new, 1},
#endif

    /* Experimental path stuff */
#ifdef WITH_IMAGEPATH
    {"path", (PyCFunction)PyPath_Create, 1},
#endif

    /* Experimental arrow graphics stuff */
#ifdef WITH_ARROW
    {"outline", (PyCFunction)PyOutline_Create, 1},
#endif

    {NULL, NULL} /* sentinel */
};

static int
setup_module(PyObject* m) {
    PyObject* d = PyModule_GetDict(m);

    /* Ready object types */
    if (PyType_Ready(&Imaging_Type) < 0)
        return -1;

#ifdef WITH_IMAGEDRAW
    if (PyType_Ready(&ImagingFont_Type) < 0)
        return -1;

    if (PyType_Ready(&ImagingDraw_Type) < 0)
        return -1;
#endif
    if (PyType_Ready(&PixelAccess_Type) < 0)
        return -1;

    ImagingAccessInit();

#ifdef HAVE_LIBJPEG
  {
    extern const char* ImagingJpegVersion(void);
    PyDict_SetItemString(d, "jpeglib_version", PyUnicode_FromString(ImagingJpegVersion()));
  }
#endif

#ifdef HAVE_OPENJPEG
  {
    extern const char *ImagingJpeg2KVersion(void);
    PyDict_SetItemString(d, "jp2klib_version", PyUnicode_FromString(ImagingJpeg2KVersion()));
  }
#endif

#ifdef HAVE_LIBZ
  /* zip encoding strategies */
  PyModule_AddIntConstant(m, "DEFAULT_STRATEGY", Z_DEFAULT_STRATEGY);
  PyModule_AddIntConstant(m, "FILTERED", Z_FILTERED);
  PyModule_AddIntConstant(m, "HUFFMAN_ONLY", Z_HUFFMAN_ONLY);
  PyModule_AddIntConstant(m, "RLE", Z_RLE);
  PyModule_AddIntConstant(m, "FIXED", Z_FIXED);
  {
    extern const char* ImagingZipVersion(void);
    PyDict_SetItemString(d, "zlib_version", PyUnicode_FromString(ImagingZipVersion()));
  }
#endif

    PyDict_SetItemString(d, "PILLOW_VERSION", PyUnicode_FromString(PILLOW_VERSION));

    return 0;
}

#if PY_VERSION_HEX >= 0x03000000
PyMODINIT_FUNC
PyInit__imaging(void) {
    PyObject* m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imaging",         /* m_name */
        NULL,               /* m_doc */
        -1,                 /* m_size */
        functions,          /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0)
        return NULL;

    return m;
}
#else
PyMODINIT_FUNC
init_imaging(void)
{
    PyObject* m = Py_InitModule("_imaging", functions);
    setup_module(m);
}
#endif

