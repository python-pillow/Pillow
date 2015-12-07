/*
 * PIL FreeType Driver
 *
 * a FreeType 2.X driver for PIL
 *
 * history:
 * 2001-02-17 fl  Created (based on old experimental freetype 1.0 code)
 * 2001-04-18 fl  Fixed some egcs compiler nits
 * 2002-11-08 fl  Added unicode support; more font metrics, etc
 * 2003-05-20 fl  Fixed compilation under 1.5.2 and newer non-unicode builds
 * 2003-09-27 fl  Added charmap encoding support
 * 2004-05-15 fl  Fixed compilation for FreeType 2.1.8
 * 2004-09-10 fl  Added support for monochrome bitmaps
 * 2006-06-18 fl  Fixed glyph bearing calculation
 * 2007-12-23 fl  Fixed crash in family/style attribute fetch
 * 2008-01-02 fl  Handle Unicode filenames properly
 *
 * Copyright (c) 1998-2007 by Secret Labs AB
 */

#include "Python.h"
#include "Imaging.h"

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H

#define KEEP_PY_UNICODE
#include "py3.h"

#if !defined(FT_LOAD_TARGET_MONO)
#define FT_LOAD_TARGET_MONO  FT_LOAD_MONOCHROME
#endif

/* -------------------------------------------------------------------- */
/* error table */

#undef FTERRORS_H
#undef __FTERRORS_H__

#define FT_ERRORDEF( e, v, s )  { e, s },
#define FT_ERROR_START_LIST  {
#define FT_ERROR_END_LIST    { 0, 0 } };

struct {
    int code;
    const char* message;
} ft_errors[] =

#include FT_ERRORS_H

/* -------------------------------------------------------------------- */
/* font objects */

static FT_Library library;

typedef struct {
    PyObject_HEAD
    FT_Face face;
    unsigned char *font_bytes;
} FontObject;

static PyTypeObject Font_Type;

/* round a 26.6 pixel coordinate to the nearest larger integer */
#define PIXEL(x) ((((x)+63) & -64)>>6)

static PyObject*
geterror(int code)
{
    int i;

    for (i = 0; ft_errors[i].message; i++)
        if (ft_errors[i].code == code) {
            PyErr_SetString(PyExc_IOError, ft_errors[i].message);
            return NULL;
        }

    PyErr_SetString(PyExc_IOError, "unknown freetype error");
    return NULL;
}

static PyObject*
getfont(PyObject* self_, PyObject* args, PyObject* kw)
{
    /* create a font object from a file name and a size (in pixels) */

    FontObject* self;
    int error = 0;

    char* filename = NULL;
    int size;
    int index = 0;
    unsigned char* encoding;
    unsigned char* font_bytes;
    int font_bytes_size = 0;
    static char* kwlist[] = {
        "filename", "size", "index", "encoding", "font_bytes", NULL
    };

    if (!library) {
        PyErr_SetString(
            PyExc_IOError,
            "failed to initialize FreeType library"
            );
        return NULL;
    }

    if (!PyArg_ParseTupleAndKeywords(args, kw, "eti|iss#", kwlist,
                                     Py_FileSystemDefaultEncoding, &filename,
                                     &size, &index, &encoding, &font_bytes,
                                     &font_bytes_size)) {
        return NULL;
    }

    self = PyObject_New(FontObject, &Font_Type);
    if (!self) {
        if (filename)
            PyMem_Free(filename);
        return NULL;
    }

    if (filename && font_bytes_size <= 0) {
        self->font_bytes = NULL;
        error = FT_New_Face(library, filename, index, &self->face);
    } else {
        /* need to have allocated storage for font_bytes for the life of the object.*/
        /* Don't free this before FT_Done_Face */
        self->font_bytes = PyMem_Malloc(font_bytes_size);
        if (!self->font_bytes) {
            error = 65; // Out of Memory in Freetype.
        }
        if (!error) {
            memcpy(self->font_bytes, font_bytes, (size_t)font_bytes_size);
            error = FT_New_Memory_Face(library, (FT_Byte*)self->font_bytes,
                                       font_bytes_size, index, &self->face);
        }
    }

    if (!error)
        error = FT_Set_Pixel_Sizes(self->face, 0, size);

    if (!error && encoding && strlen((char*) encoding) == 4) {
        FT_Encoding encoding_tag = FT_MAKE_TAG(
            encoding[0], encoding[1], encoding[2], encoding[3]
            );
        error = FT_Select_Charmap(self->face, encoding_tag);
    }
    if (filename)
      PyMem_Free(filename);

    if (error) {
        if (self->font_bytes) {
            PyMem_Free(self->font_bytes);
        }
        PyObject_Del(self);
        return geterror(error);
    }

    return (PyObject*) self;
}

static int
font_getchar(PyObject* string, int index, FT_ULong* char_out)
{
    if (PyUnicode_Check(string)) {
        Py_UNICODE* p = PyUnicode_AS_UNICODE(string);
        int size = PyUnicode_GET_SIZE(string);
        if (index >= size)
            return 0;
        *char_out = p[index];
        return 1;
    }

#if PY_VERSION_HEX < 0x03000000
    if (PyString_Check(string)) {
        unsigned char* p = (unsigned char*) PyString_AS_STRING(string);
        int size = PyString_GET_SIZE(string);
        if (index >= size)
            return 0;
        *char_out = (unsigned char) p[index];
        return 1;
    }
#endif

    return 0;
}

static PyObject*
font_getsize(FontObject* self, PyObject* args)
{
    int i, x, y_max, y_min;
    FT_ULong ch;
    FT_Face face;
    int xoffset, yoffset;
    FT_Bool kerning = FT_HAS_KERNING(self->face);
    FT_UInt last_index = 0;

    /* calculate size and bearing for a given string */

    PyObject* string;
    if (!PyArg_ParseTuple(args, "O:getsize", &string))
        return NULL;

#if PY_VERSION_HEX >= 0x03000000
    if (!PyUnicode_Check(string)) {
#else
    if (!PyUnicode_Check(string) && !PyString_Check(string)) {
#endif
        PyErr_SetString(PyExc_TypeError, "expected string");
        return NULL;
    }

    face = NULL;
    xoffset = yoffset = 0;
    y_max = y_min = 0;

    for (x = i = 0; font_getchar(string, i, &ch); i++) {
        int index, error;
        FT_BBox bbox;
        FT_Glyph glyph;
        face = self->face;
        index = FT_Get_Char_Index(face, ch);
        if (kerning && last_index && index) {
            FT_Vector delta;
            FT_Get_Kerning(self->face, last_index, index, ft_kerning_default,
                           &delta);
            x += delta.x;
        }

	/* Note: bitmap fonts within ttf fonts do not work, see #891/pr#960
	 *   Yifu Yu<root@jackyyf.com>, 2014-10-15
	 */
        error = FT_Load_Glyph(face, index, FT_LOAD_DEFAULT|FT_LOAD_NO_BITMAP);
        if (error)
            return geterror(error);
        if (i == 0)
            xoffset = face->glyph->metrics.horiBearingX;
        x += face->glyph->metrics.horiAdvance;

        FT_Get_Glyph(face->glyph, &glyph);
        FT_Glyph_Get_CBox(glyph, FT_GLYPH_BBOX_SUBPIXELS, &bbox);
        if (bbox.yMax > y_max)
            y_max = bbox.yMax;
        if (bbox.yMin < y_min)
            y_min = bbox.yMin;
            
        /* find max distance of baseline from top */
        if (face->glyph->metrics.horiBearingY > yoffset)
            yoffset = face->glyph->metrics.horiBearingY;
            
        last_index = index;
        FT_Done_Glyph(glyph);
    }

    if (face) {
        int offset;
        /* left bearing */
        if (xoffset < 0)
            x -= xoffset;
        else
            xoffset = 0;
        /* right bearing */
        offset = face->glyph->metrics.horiAdvance -
            face->glyph->metrics.width -
            face->glyph->metrics.horiBearingX;
        if (offset < 0)
            x -= offset;
        /* difference between the font ascender and the distance of
         * the baseline from the top */
        yoffset = PIXEL(self->face->size->metrics.ascender - yoffset);
    }

    return Py_BuildValue(
        "(ii)(ii)",
        PIXEL(x), PIXEL(y_max - y_min),
        PIXEL(xoffset), yoffset
        );
}

static PyObject*
font_getabc(FontObject* self, PyObject* args)
{
    FT_ULong ch;
    FT_Face face;
    double a, b, c;

    /* calculate ABC values for a given string */

    PyObject* string;
    if (!PyArg_ParseTuple(args, "O:getabc", &string))
        return NULL;

#if PY_VERSION_HEX >= 0x03000000
    if (!PyUnicode_Check(string)) {
#else
    if (!PyUnicode_Check(string) && !PyString_Check(string)) {
#endif
        PyErr_SetString(PyExc_TypeError, "expected string");
        return NULL;
    }

    if (font_getchar(string, 0, &ch)) {
        int index, error;
        face = self->face;
        index = FT_Get_Char_Index(face, ch);
	/* Note: bitmap fonts within ttf fonts do not work, see #891/pr#960 */
        error = FT_Load_Glyph(face, index, FT_LOAD_DEFAULT|FT_LOAD_NO_BITMAP);
        if (error)
            return geterror(error);
        a = face->glyph->metrics.horiBearingX / 64.0;
        b = face->glyph->metrics.width / 64.0;
        c = (face->glyph->metrics.horiAdvance -
             face->glyph->metrics.horiBearingX -
             face->glyph->metrics.width) / 64.0;
    } else
        a = b = c = 0.0;

    return Py_BuildValue("ddd", a, b, c);
}

static PyObject*
font_render(FontObject* self, PyObject* args)
{
    int i, x, y;
    Imaging im;
    int index, error, ascender;
    int load_flags;
    unsigned char *source;
    FT_ULong ch;
    FT_GlyphSlot glyph;
    FT_Bool kerning = FT_HAS_KERNING(self->face);
    FT_UInt last_index = 0;

    /* render string into given buffer (the buffer *must* have
       the right size, or this will crash) */
    PyObject* string;
    Py_ssize_t id;
    int mask = 0;
    int temp;
    int xx, x0, x1;
    if (!PyArg_ParseTuple(args, "On|i:render", &string, &id, &mask))
        return NULL;

#if PY_VERSION_HEX >= 0x03000000
    if (!PyUnicode_Check(string)) {
#else
    if (!PyUnicode_Check(string) && !PyString_Check(string)) {
#endif
        PyErr_SetString(PyExc_TypeError, "expected string");
        return NULL;
    }

    im = (Imaging) id;
    /* Note: bitmap fonts within ttf fonts do not work, see #891/pr#960 */
    load_flags = FT_LOAD_RENDER|FT_LOAD_NO_BITMAP;
    if (mask)
        load_flags |= FT_LOAD_TARGET_MONO;

    ascender = 0;
    for (i = 0; font_getchar(string, i, &ch); i++) {
        index = FT_Get_Char_Index(self->face, ch);
        error = FT_Load_Glyph(self->face, index, load_flags);
        if (error)
            return geterror(error);
        glyph = self->face->glyph;
        temp = (glyph->bitmap.rows - glyph->bitmap_top);
        if (temp > ascender)
            ascender = temp;
    }

    for (x = i = 0; font_getchar(string, i, &ch); i++) {
        if (i == 0 && self->face->glyph->metrics.horiBearingX < 0)
            x = -PIXEL(self->face->glyph->metrics.horiBearingX);
        index = FT_Get_Char_Index(self->face, ch);
        if (kerning && last_index && index) {
            FT_Vector delta;
            FT_Get_Kerning(self->face, last_index, index, ft_kerning_default,
                           &delta);
            x += delta.x >> 6;
        }

        error = FT_Load_Glyph(self->face, index, load_flags);
        if (error)
            return geterror(error);

        glyph = self->face->glyph;

        source = (unsigned char*) glyph->bitmap.buffer;
        xx = x + glyph->bitmap_left;
        x0 = 0;
        x1 = glyph->bitmap.width;
        if (xx < 0)
            x0 = -xx;
        if (xx + x1 > im->xsize)
            x1 = im->xsize - xx;

        if (mask) {
            /* use monochrome mask (on palette images, etc) */
            for (y = 0; y < glyph->bitmap.rows; y++) {
                int yy = y + im->ysize - (PIXEL(glyph->metrics.horiBearingY) + ascender);
                if (yy >= 0 && yy < im->ysize) {
                    /* blend this glyph into the buffer */
                    unsigned char *target = im->image8[yy] + xx;
                    int i, j, m = 128;
                    for (i = j = 0; j < x1; j++) {
                        if (j >= x0 && (source[i] & m))
                            target[j] = 255;
                        if (!(m >>= 1)) {
                            m = 128;
                            i++;
                        }
                    }
                }
                source += glyph->bitmap.pitch;
            }
        } else {
            /* use antialiased rendering */
            for (y = 0; y < glyph->bitmap.rows; y++) {
                int yy = y + im->ysize - (PIXEL(glyph->metrics.horiBearingY) + ascender);
                if (yy >= 0 && yy < im->ysize) {
                    /* blend this glyph into the buffer */
                    int i;
                    unsigned char *target = im->image8[yy] + xx;
                    for (i = x0; i < x1; i++) {
                        if (target[i] < source[i])
                            target[i] = source[i];
                    }
                }
                source += glyph->bitmap.pitch;
            }
        }
        x += PIXEL(glyph->metrics.horiAdvance);
        last_index = index;
    }

    Py_RETURN_NONE;
}

static void
font_dealloc(FontObject* self)
{
    FT_Done_Face(self->face);
    if (self->font_bytes) {
        PyMem_Free(self->font_bytes);
    }
    PyObject_Del(self);
}

static PyMethodDef font_methods[] = {
    {"render", (PyCFunction) font_render, METH_VARARGS},
    {"getsize", (PyCFunction) font_getsize, METH_VARARGS},
    {"getabc", (PyCFunction) font_getabc, METH_VARARGS},
    {NULL, NULL}
};

static PyObject*
font_getattr_family(FontObject* self, void* closure)
{
#if PY_VERSION_HEX >= 0x03000000
    if (self->face->family_name)
        return PyUnicode_FromString(self->face->family_name);
#else
    if (self->face->family_name)
        return PyString_FromString(self->face->family_name);
#endif
    Py_RETURN_NONE;
}

static PyObject*
font_getattr_style(FontObject* self, void* closure)
{
#if PY_VERSION_HEX >= 0x03000000
    if (self->face->style_name)
        return PyUnicode_FromString(self->face->style_name);
#else
    if (self->face->style_name)
        return PyString_FromString(self->face->style_name);
#endif
    Py_RETURN_NONE;
}

static PyObject*
font_getattr_ascent(FontObject* self, void* closure)
{
    return PyInt_FromLong(PIXEL(self->face->size->metrics.ascender));
}

static PyObject*
font_getattr_descent(FontObject* self, void* closure)
{
    return PyInt_FromLong(-PIXEL(self->face->size->metrics.descender));
}

static PyObject*
font_getattr_height(FontObject* self, void* closure)
{
    return PyInt_FromLong(PIXEL(self->face->size->metrics.height));
}

static PyObject*
font_getattr_x_ppem(FontObject* self, void* closure)
{
    return PyInt_FromLong(self->face->size->metrics.x_ppem);
}

static PyObject*
font_getattr_y_ppem(FontObject* self, void* closure)
{
    return PyInt_FromLong(self->face->size->metrics.y_ppem);
}


static PyObject*
font_getattr_glyphs(FontObject* self, void* closure)
{
    return PyInt_FromLong(self->face->num_glyphs);
}

static struct PyGetSetDef font_getsetters[] = {
    { "family",     (getter) font_getattr_family },
    { "style",      (getter) font_getattr_style },
    { "ascent",     (getter) font_getattr_ascent },
    { "descent",    (getter) font_getattr_descent },
    { "height",     (getter) font_getattr_height },
    { "x_ppem",     (getter) font_getattr_x_ppem },
    { "y_ppem",     (getter) font_getattr_y_ppem },
    { "glyphs",     (getter) font_getattr_glyphs },
    { NULL }
};

static PyTypeObject Font_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Font", sizeof(FontObject), 0,
    /* methods */
    (destructor)font_dealloc, /* tp_dealloc */
    0, /* tp_print */
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
    font_methods,               /*tp_methods*/
    0,                          /*tp_members*/
    font_getsetters,            /*tp_getset*/
};

static PyMethodDef _functions[] = {
    {"getfont", (PyCFunction) getfont, METH_VARARGS|METH_KEYWORDS},
    {NULL, NULL}
};

static int
setup_module(PyObject* m) {
    PyObject* d;
    PyObject* v;
    int major, minor, patch;

    d = PyModule_GetDict(m);

    /* Ready object type */
    PyType_Ready(&Font_Type);

    if (FT_Init_FreeType(&library))
        return 0; /* leave it uninitialized */

    FT_Library_Version(library, &major, &minor, &patch);

#if PY_VERSION_HEX >= 0x03000000
    v = PyUnicode_FromFormat("%d.%d.%d", major, minor, patch);
#else
    v = PyString_FromFormat("%d.%d.%d", major, minor, patch);
#endif
    PyDict_SetItemString(d, "freetype2_version", v);

    return 0;
}

#if PY_VERSION_HEX >= 0x03000000
PyMODINIT_FUNC
PyInit__imagingft(void) {
    PyObject* m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingft",       /* m_name */
        NULL,               /* m_doc */
        -1,                 /* m_size */
        _functions,         /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0)
        return NULL;

    return m;
}
#else
PyMODINIT_FUNC
init_imagingft(void)
{
    PyObject* m = Py_InitModule("_imagingft", _functions);
    setup_module(m);
}
#endif

