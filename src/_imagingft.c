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

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "Imaging.h"

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H
#include FT_STROKER_H
#include FT_MULTIPLE_MASTERS_H
#include FT_SFNT_NAMES_H

#define KEEP_PY_UNICODE
#include "py3.h"

#if !defined(_MSC_VER)
#include <dlfcn.h>
#endif

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

#include <raqm.h>

#define LAYOUT_FALLBACK 0
#define LAYOUT_RAQM 1

typedef struct
{
  int index, x_offset, x_advance, y_offset, y_advance;
  unsigned int cluster;
} GlyphInfo;

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
    int layout_engine;
} FontObject;

static PyTypeObject Font_Type;

typedef bool (*t_raqm_version_atleast)(unsigned int major,
                                       unsigned int minor,
                                       unsigned int micro);
typedef raqm_t* (*t_raqm_create)(void);
typedef int (*t_raqm_set_text)(raqm_t         *rq,
                               const uint32_t *text,
                               size_t          len);
typedef bool (*t_raqm_set_text_utf8) (raqm_t     *rq,
                                      const char *text,
                                      size_t      len);
typedef bool (*t_raqm_set_par_direction) (raqm_t          *rq,
                                          raqm_direction_t dir);
typedef bool (*t_raqm_set_language) (raqm_t     *rq,
                                     const char *lang,
                                     size_t      start,
                                     size_t      len);
typedef bool (*t_raqm_add_font_feature)  (raqm_t     *rq,
                                          const char *feature,
                                          int         len);
typedef bool (*t_raqm_set_freetype_face) (raqm_t *rq,
                                          FT_Face face);
typedef bool (*t_raqm_layout) (raqm_t *rq);
typedef raqm_glyph_t* (*t_raqm_get_glyphs) (raqm_t *rq,
                                            size_t *length);
typedef raqm_glyph_t_01* (*t_raqm_get_glyphs_01) (raqm_t *rq,
                                            size_t *length);
typedef void (*t_raqm_destroy) (raqm_t *rq);

typedef struct {
    void* raqm;
    int version;
    t_raqm_version_atleast version_atleast;
    t_raqm_create create;
    t_raqm_set_text set_text;
    t_raqm_set_text_utf8 set_text_utf8;
    t_raqm_set_par_direction set_par_direction;
    t_raqm_set_language set_language;
    t_raqm_add_font_feature add_font_feature;
    t_raqm_set_freetype_face set_freetype_face;
    t_raqm_layout layout;
    t_raqm_get_glyphs get_glyphs;
    t_raqm_get_glyphs_01 get_glyphs_01;
    t_raqm_destroy destroy;
} p_raqm_func;

static p_raqm_func p_raqm;


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

static int
setraqm(void)
{
    /* set the static function pointers for dynamic raqm linking */
    p_raqm.raqm = NULL;

    /* Microsoft needs a totally different system */
#if !defined(_MSC_VER)
    p_raqm.raqm = dlopen("libraqm.so.0", RTLD_LAZY);
    if (!p_raqm.raqm) {
        p_raqm.raqm = dlopen("libraqm.dylib", RTLD_LAZY);
    }
#else
    p_raqm.raqm = LoadLibrary("libraqm");
#endif

    if (!p_raqm.raqm) {
        return 1;
    }

#if !defined(_MSC_VER)
    p_raqm.version_atleast = (t_raqm_version_atleast)dlsym(p_raqm.raqm, "raqm_version_atleast");
    p_raqm.create = (t_raqm_create)dlsym(p_raqm.raqm, "raqm_create");
    p_raqm.set_text = (t_raqm_set_text)dlsym(p_raqm.raqm, "raqm_set_text");
    p_raqm.set_text_utf8 = (t_raqm_set_text_utf8)dlsym(p_raqm.raqm, "raqm_set_text_utf8");
    p_raqm.set_par_direction = (t_raqm_set_par_direction)dlsym(p_raqm.raqm, "raqm_set_par_direction");
    p_raqm.set_language = (t_raqm_set_language)dlsym(p_raqm.raqm, "raqm_set_language");
    p_raqm.add_font_feature = (t_raqm_add_font_feature)dlsym(p_raqm.raqm, "raqm_add_font_feature");
    p_raqm.set_freetype_face = (t_raqm_set_freetype_face)dlsym(p_raqm.raqm, "raqm_set_freetype_face");
    p_raqm.layout = (t_raqm_layout)dlsym(p_raqm.raqm, "raqm_layout");
    p_raqm.destroy = (t_raqm_destroy)dlsym(p_raqm.raqm, "raqm_destroy");
    if(dlsym(p_raqm.raqm, "raqm_index_to_position")) {
        p_raqm.get_glyphs = (t_raqm_get_glyphs)dlsym(p_raqm.raqm, "raqm_get_glyphs");
        p_raqm.version = 2;
    } else {
        p_raqm.version = 1;
        p_raqm.get_glyphs_01 = (t_raqm_get_glyphs_01)dlsym(p_raqm.raqm, "raqm_get_glyphs");
    }
    if (dlerror() ||
        !(p_raqm.create &&
          p_raqm.set_text &&
          p_raqm.set_text_utf8 &&
          p_raqm.set_par_direction &&
          p_raqm.set_language &&
          p_raqm.add_font_feature &&
          p_raqm.set_freetype_face &&
          p_raqm.layout &&
          (p_raqm.get_glyphs || p_raqm.get_glyphs_01) &&
          p_raqm.destroy)) {
        dlclose(p_raqm.raqm);
        p_raqm.raqm = NULL;
        return 2;
    }
#else
    p_raqm.version_atleast = (t_raqm_version_atleast)GetProcAddress(p_raqm.raqm, "raqm_version_atleast");
    p_raqm.create = (t_raqm_create)GetProcAddress(p_raqm.raqm, "raqm_create");
    p_raqm.set_text = (t_raqm_set_text)GetProcAddress(p_raqm.raqm, "raqm_set_text");
    p_raqm.set_text_utf8 = (t_raqm_set_text_utf8)GetProcAddress(p_raqm.raqm, "raqm_set_text_utf8");
    p_raqm.set_par_direction = (t_raqm_set_par_direction)GetProcAddress(p_raqm.raqm, "raqm_set_par_direction");
    p_raqm.set_language = (t_raqm_set_language)GetProcAddress(p_raqm.raqm, "raqm_set_language");
    p_raqm.add_font_feature = (t_raqm_add_font_feature)GetProcAddress(p_raqm.raqm, "raqm_add_font_feature");
    p_raqm.set_freetype_face = (t_raqm_set_freetype_face)GetProcAddress(p_raqm.raqm, "raqm_set_freetype_face");
    p_raqm.layout = (t_raqm_layout)GetProcAddress(p_raqm.raqm, "raqm_layout");
    p_raqm.destroy = (t_raqm_destroy)GetProcAddress(p_raqm.raqm, "raqm_destroy");
    if(GetProcAddress(p_raqm.raqm, "raqm_index_to_position")) {
        p_raqm.get_glyphs = (t_raqm_get_glyphs)GetProcAddress(p_raqm.raqm, "raqm_get_glyphs");
        p_raqm.version = 2;
    } else {
        p_raqm.version = 1;
        p_raqm.get_glyphs_01 = (t_raqm_get_glyphs_01)GetProcAddress(p_raqm.raqm, "raqm_get_glyphs");
    }
    if (!(p_raqm.create &&
          p_raqm.set_text &&
          p_raqm.set_text_utf8 &&
          p_raqm.set_par_direction &&
          p_raqm.set_language &&
          p_raqm.add_font_feature &&
          p_raqm.set_freetype_face &&
          p_raqm.layout &&
          (p_raqm.get_glyphs || p_raqm.get_glyphs_01) &&
          p_raqm.destroy)) {
        FreeLibrary(p_raqm.raqm);
        p_raqm.raqm = NULL;
        return 2;
    }
#endif

    return 0;
}

static PyObject*
getfont(PyObject* self_, PyObject* args, PyObject* kw)
{
    /* create a font object from a file name and a size (in pixels) */

    FontObject* self;
    int error = 0;

    char* filename = NULL;
    Py_ssize_t size;
    Py_ssize_t index = 0;
    Py_ssize_t layout_engine = 0;
    unsigned char* encoding;
    unsigned char* font_bytes;
    Py_ssize_t font_bytes_size = 0;
    static char* kwlist[] = {
        "filename", "size", "index", "encoding", "font_bytes",
        "layout_engine", NULL
    };

    if (!library) {
        PyErr_SetString(
            PyExc_IOError,
            "failed to initialize FreeType library"
            );
        return NULL;
    }

    if (!PyArg_ParseTupleAndKeywords(args, kw, "etn|ns"PY_ARG_BYTES_LENGTH"n",
                                     kwlist,
                                     Py_FileSystemDefaultEncoding, &filename,
                                     &size, &index, &encoding, &font_bytes,
                                     &font_bytes_size, &layout_engine)) {
        return NULL;
    }

    self = PyObject_New(FontObject, &Font_Type);
    if (!self) {
        if (filename)
            PyMem_Free(filename);
        return NULL;
    }

    self->face = NULL;
    self->layout_engine = layout_engine;

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
            self->font_bytes = NULL;
        }
        Py_DECREF(self);
        return geterror(error);
    }

    return (PyObject*) self;
}

static int
font_getchar(PyObject* string, int index, FT_ULong* char_out)
{
#if (PY_VERSION_HEX < 0x03030000) || (defined(PYPY_VERSION_NUM))
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
#else
    if (PyUnicode_Check(string)) {
        if (index >= PyUnicode_GET_LENGTH(string))
            return 0;
        *char_out = PyUnicode_READ_CHAR(string, index);
        return 1;
    }
#endif

    return 0;
}

static size_t
text_layout_raqm(PyObject* string, FontObject* self, const char* dir, PyObject *features,
                 const char* lang, GlyphInfo **glyph_info, int mask)
{
    size_t i = 0, count = 0, start = 0;
    raqm_t *rq;
    raqm_glyph_t *glyphs = NULL;
    raqm_glyph_t_01 *glyphs_01 = NULL;
    raqm_direction_t direction;

    rq = (*p_raqm.create)();
    if (rq == NULL) {
        PyErr_SetString(PyExc_ValueError, "raqm_create() failed.");
        goto failed;
    }

#if (PY_VERSION_HEX < 0x03030000) || (defined(PYPY_VERSION_NUM))
    if (PyUnicode_Check(string)) {
        Py_UNICODE *text = PyUnicode_AS_UNICODE(string);
        Py_ssize_t size = PyUnicode_GET_SIZE(string);
        if (! size) {
            /* return 0 and clean up, no glyphs==no size,
               and raqm fails with empty strings */
            goto failed;
        }
        if (!(*p_raqm.set_text)(rq, (const uint32_t *)(text), size)) {
            PyErr_SetString(PyExc_ValueError, "raqm_set_text() failed");
            goto failed;
        }
        if (lang) {
            if (!(*p_raqm.set_language)(rq, lang, start, size)) {
                PyErr_SetString(PyExc_ValueError, "raqm_set_language() failed");
                goto failed;
            }
        }
    }
#if PY_VERSION_HEX < 0x03000000
    else if (PyString_Check(string)) {
        char *text = PyString_AS_STRING(string);
        int size = PyString_GET_SIZE(string);
        if (! size) {
            goto failed;
        }
        if (!(*p_raqm.set_text_utf8)(rq, text, size)) {
            PyErr_SetString(PyExc_ValueError, "raqm_set_text_utf8() failed");
            goto failed;
        }
        if (lang) {
            if (!(*p_raqm.set_language)(rq, lang, start, size)) {
                PyErr_SetString(PyExc_ValueError, "raqm_set_language() failed");
                goto failed;
            }
        }
    }
#endif
#else
    if (PyUnicode_Check(string)) {
        Py_UCS4 *text = PyUnicode_AsUCS4Copy(string);
        Py_ssize_t size = PyUnicode_GET_LENGTH(string);
        if (!text || !size) {
            /* return 0 and clean up, no glyphs==no size,
               and raqm fails with empty strings */
            goto failed;
        }
        int set_text = (*p_raqm.set_text)(rq, (const uint32_t *)(text), size);
        PyMem_Free(text);
        if (!set_text) {
            PyErr_SetString(PyExc_ValueError, "raqm_set_text() failed");
            goto failed;
        }
        if (lang) {
            if (!(*p_raqm.set_language)(rq, lang, start, size)) {
                PyErr_SetString(PyExc_ValueError, "raqm_set_language() failed");
                goto failed;
            }
        }
    }
#endif
    else {
        PyErr_SetString(PyExc_TypeError, "expected string");
        goto failed;
    }

    direction = RAQM_DIRECTION_DEFAULT;
    if (dir) {
        if (strcmp(dir, "rtl") == 0)
            direction = RAQM_DIRECTION_RTL;
        else if (strcmp(dir, "ltr") == 0)
            direction = RAQM_DIRECTION_LTR;
        else if (strcmp(dir, "ttb") == 0) {
            direction = RAQM_DIRECTION_TTB;
            if (p_raqm.version_atleast == NULL || !(*p_raqm.version_atleast)(0, 7, 0)) {
                PyErr_SetString(PyExc_ValueError, "libraqm 0.7 or greater required for 'ttb' direction");
                goto failed;
            }
        } else {
            PyErr_SetString(PyExc_ValueError, "direction must be either 'rtl', 'ltr' or 'ttb'");
            goto failed;
        }
    }

    if (!(*p_raqm.set_par_direction)(rq, direction)) {
        PyErr_SetString(PyExc_ValueError, "raqm_set_par_direction() failed");
        goto failed;
    }

    if (features != Py_None) {
        int j, len;
        PyObject *seq = PySequence_Fast(features, "expected a sequence");
        if (!seq) {
            goto failed;
        }

        len = PySequence_Size(seq);
        for (j = 0; j < len; j++) {
            PyObject *item = PySequence_Fast_GET_ITEM(seq, j);
            char *feature = NULL;
            Py_ssize_t size = 0;
            PyObject *bytes;

#if PY_VERSION_HEX >= 0x03000000
            if (!PyUnicode_Check(item)) {
#else
            if (!PyUnicode_Check(item) && !PyString_Check(item)) {
#endif
                PyErr_SetString(PyExc_TypeError, "expected a string");
                goto failed;
            }

            if (PyUnicode_Check(item)) {
                bytes = PyUnicode_AsUTF8String(item);
                if (bytes == NULL)
                    goto failed;
                feature = PyBytes_AS_STRING(bytes);
                size = PyBytes_GET_SIZE(bytes);
            }
#if PY_VERSION_HEX < 0x03000000
            else {
                feature = PyString_AsString(item);
                size = PyString_GET_SIZE(item);
            }
#endif
            if (!(*p_raqm.add_font_feature)(rq, feature, size)) {
                PyErr_SetString(PyExc_ValueError, "raqm_add_font_feature() failed");
                goto failed;
            }
        }
    }

    if (!(*p_raqm.set_freetype_face)(rq, self->face)) {
        PyErr_SetString(PyExc_RuntimeError, "raqm_set_freetype_face() failed.");
        goto failed;
    }

    if (!(*p_raqm.layout)(rq)) {
        PyErr_SetString(PyExc_RuntimeError, "raqm_layout() failed.");
        goto failed;
    }

    if (p_raqm.version == 1) {
        glyphs_01 = (*p_raqm.get_glyphs_01)(rq, &count);
        if (glyphs_01 == NULL) {
            PyErr_SetString(PyExc_ValueError, "raqm_get_glyphs() failed.");
            count = 0;
            goto failed;
        }
    } else { /* version == 2 */
        glyphs = (*p_raqm.get_glyphs)(rq, &count);
        if (glyphs == NULL) {
            PyErr_SetString(PyExc_ValueError, "raqm_get_glyphs() failed.");
            count = 0;
            goto failed;
        }
    }

    (*glyph_info) = PyMem_New(GlyphInfo, count);
    if ((*glyph_info) == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyMem_New() failed");
        count = 0;
        goto failed;
    }

    if (p_raqm.version == 1) {
        for (i = 0; i < count; i++) {
            (*glyph_info)[i].index = glyphs_01[i].index;
            (*glyph_info)[i].x_offset = glyphs_01[i].x_offset;
            (*glyph_info)[i].x_advance = glyphs_01[i].x_advance;
            (*glyph_info)[i].y_offset = glyphs_01[i].y_offset;
            (*glyph_info)[i].y_advance = glyphs_01[i].y_advance;
            (*glyph_info)[i].cluster = glyphs_01[i].cluster;
        }
    } else {
        for (i = 0; i < count; i++) {
            (*glyph_info)[i].index = glyphs[i].index;
            (*glyph_info)[i].x_offset = glyphs[i].x_offset;
            (*glyph_info)[i].x_advance = glyphs[i].x_advance;
            (*glyph_info)[i].y_offset = glyphs[i].y_offset;
            (*glyph_info)[i].y_advance = glyphs[i].y_advance;
            (*glyph_info)[i].cluster = glyphs[i].cluster;
        }
    }

failed:
    (*p_raqm.destroy)(rq);
    return count;
}

static size_t
text_layout_fallback(PyObject* string, FontObject* self, const char* dir, PyObject *features,
                     const char* lang, GlyphInfo **glyph_info, int mask)
{
    int error, load_flags;
    FT_ULong ch;
    Py_ssize_t count;
    FT_GlyphSlot glyph;
    FT_Bool kerning = FT_HAS_KERNING(self->face);
    FT_UInt last_index = 0;
    int i;

    if (features != Py_None || dir != NULL || lang != NULL) {
      PyErr_SetString(PyExc_KeyError, "setting text direction, language or font features is not supported without libraqm");
    }
#if PY_VERSION_HEX >= 0x03000000
    if (!PyUnicode_Check(string)) {
#else
    if (!PyUnicode_Check(string) && !PyString_Check(string)) {
#endif
        PyErr_SetString(PyExc_TypeError, "expected string");
        return 0;
    }

    count = 0;
    while (font_getchar(string, count, &ch)) {
       count++;
    }
    if (count == 0) {
        return 0;
    }

    (*glyph_info) = PyMem_New(GlyphInfo, count);
    if ((*glyph_info) == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyMem_New() failed");
        return 0;
    }

    load_flags = FT_LOAD_RENDER|FT_LOAD_NO_BITMAP;
    if (mask) {
        load_flags |= FT_LOAD_TARGET_MONO;
    }
    for (i = 0; font_getchar(string, i, &ch); i++) {
        (*glyph_info)[i].index = FT_Get_Char_Index(self->face, ch);
        error = FT_Load_Glyph(self->face, (*glyph_info)[i].index, load_flags);
        if (error) {
            geterror(error);
            return 0;
        }
        glyph = self->face->glyph;
        (*glyph_info)[i].x_offset=0;
        (*glyph_info)[i].y_offset=0;
        if (kerning && last_index && (*glyph_info)[i].index) {
            FT_Vector delta;
            if (FT_Get_Kerning(self->face, last_index, (*glyph_info)[i].index,
                           ft_kerning_default,&delta) == 0)
            (*glyph_info)[i-1].x_advance += PIXEL(delta.x);
            (*glyph_info)[i-1].y_advance += PIXEL(delta.y);
        }

        (*glyph_info)[i].x_advance = glyph->metrics.horiAdvance;
        (*glyph_info)[i].y_advance = glyph->metrics.vertAdvance;
        last_index = (*glyph_info)[i].index;
        (*glyph_info)[i].cluster = ch;
    }
    return count;
}

static size_t
text_layout(PyObject* string, FontObject* self, const char* dir, PyObject *features,
            const char* lang, GlyphInfo **glyph_info, int mask)
{
    size_t count;

    if (p_raqm.raqm && self->layout_engine == LAYOUT_RAQM) {
        count = text_layout_raqm(string, self, dir, features, lang, glyph_info,  mask);
    } else {
        count = text_layout_fallback(string, self, dir, features, lang, glyph_info, mask);
    }
    return count;
}

static PyObject*
font_getsize(FontObject* self, PyObject* args)
{
    int x_position, x_max, x_min, y_max, y_min;
    FT_Face face;
    int xoffset, yoffset;
    int horizontal_dir;
    const char *dir = NULL;
    const char *lang = NULL;
    size_t i, count;
    GlyphInfo *glyph_info = NULL;
    PyObject *features = Py_None;

    /* calculate size and bearing for a given string */

    PyObject* string;
    if (!PyArg_ParseTuple(args, "O|zOz:getsize", &string, &dir, &features, &lang))
        return NULL;

    count = text_layout(string, self, dir, features, lang, &glyph_info, 0);
    if (PyErr_Occurred()) {
        return NULL;
    }

    face = NULL;
    xoffset = yoffset = 0;
    x_position = x_max = x_min = y_max = y_min = 0;

    horizontal_dir = dir && strcmp(dir, "ttb") == 0 ? 0 : 1;
    for (i = 0; i < count; i++) {
        int index, error, offset, x_advanced;
        FT_BBox bbox;
        FT_Glyph glyph;
        face = self->face;
        index = glyph_info[i].index;
        /* Note: bitmap fonts within ttf fonts do not work, see #891/pr#960
         *   Yifu Yu<root@jackyyf.com>, 2014-10-15
         */
        error = FT_Load_Glyph(face, index, FT_LOAD_DEFAULT|FT_LOAD_NO_BITMAP);
        if (error)
            return geterror(error);

        if (i == 0) {
            if (horizontal_dir) {
                if (face->glyph->metrics.horiBearingX < 0) {
                    xoffset = face->glyph->metrics.horiBearingX;
                    x_position -= xoffset;
                }
            } else {
                if (face->glyph->metrics.vertBearingY < 0) {
                    yoffset = face->glyph->metrics.vertBearingY;
                    y_max -= yoffset;
                }
            }
        }

        FT_Get_Glyph(face->glyph, &glyph);
        FT_Glyph_Get_CBox(glyph, FT_GLYPH_BBOX_SUBPIXELS, &bbox);
        if (horizontal_dir) {
            x_position += glyph_info[i].x_advance;

            x_advanced = x_position;
            offset = glyph_info[i].x_advance -
                    face->glyph->metrics.width -
                    face->glyph->metrics.horiBearingX;
            if (offset < 0)
                x_advanced -= offset;
            if (x_advanced > x_max)
                x_max = x_advanced;

            bbox.yMax += glyph_info[i].y_offset;
            bbox.yMin += glyph_info[i].y_offset;
            if (bbox.yMax > y_max)
                y_max = bbox.yMax;
            if (bbox.yMin < y_min)
                y_min = bbox.yMin;

            // find max distance of baseline from top
            if (face->glyph->metrics.horiBearingY > yoffset)
                yoffset = face->glyph->metrics.horiBearingY;
        } else {
            y_max -= glyph_info[i].y_advance;

            if (i == count - 1) {
                // trim end gap from final glyph
                int offset;
                offset = -glyph_info[i].y_advance -
                        face->glyph->metrics.height -
                        face->glyph->metrics.vertBearingY;
                if (offset < 0)
                    y_max -= offset;
            }

            if (bbox.xMax > x_max)
                x_max = bbox.xMax;
            if (i == 0 || bbox.xMin < x_min)
                x_min = bbox.xMin;
        }

        FT_Done_Glyph(glyph);
    }

    if (glyph_info) {
        PyMem_Free(glyph_info);
        glyph_info = NULL;
    }

    if (face) {
        if (horizontal_dir) {
            // left bearing
            if (xoffset < 0)
                x_max -= xoffset;
            else
                xoffset = 0;

            /* difference between the font ascender and the distance of
             * the baseline from the top */
            yoffset = PIXEL(self->face->size->metrics.ascender - yoffset);
        } else {
            // top bearing
            if (yoffset < 0)
                y_max -= yoffset;
            else
                yoffset = 0;
        }
    }

    return Py_BuildValue(
        "(ii)(ii)",
        PIXEL(x_max - x_min), PIXEL(y_max - y_min),
        PIXEL(xoffset), yoffset
        );
}

static PyObject*
font_render(FontObject* self, PyObject* args)
{
    int x;
    unsigned int y;
    Imaging im;
    int index, error, ascender, horizontal_dir;
    int load_flags;
    unsigned char *source;
    FT_Glyph glyph;
    FT_GlyphSlot glyph_slot;
    FT_Bitmap bitmap;
    FT_BitmapGlyph bitmap_glyph;
    int stroke_width = 0;
    FT_Stroker stroker = NULL;
    FT_Int left;
    /* render string into given buffer (the buffer *must* have
       the right size, or this will crash) */
    PyObject* string;
    Py_ssize_t id;
    int mask = 0;
    int temp;
    int xx, x0, x1;
    int yy;
    unsigned int bitmap_y;
    const char *dir = NULL;
    const char *lang = NULL;
    size_t i, count;
    GlyphInfo *glyph_info;
    PyObject *features = NULL;

    if (!PyArg_ParseTuple(args, "On|izOzi:render", &string,  &id, &mask, &dir, &features, &lang,
                                                   &stroke_width)) {
        return NULL;
    }

    glyph_info = NULL;
    count = text_layout(string, self, dir, features, lang, &glyph_info, mask);
    if (PyErr_Occurred()) {
        return NULL;
    }
    if (count == 0) {
        Py_RETURN_NONE;
    }

    if (stroke_width) {
        error = FT_Stroker_New(library, &stroker);
        if (error) {
            return geterror(error);
        }

        FT_Stroker_Set(stroker, (FT_Fixed)stroke_width*64, FT_STROKER_LINECAP_ROUND, FT_STROKER_LINEJOIN_ROUND, 0);
    }

    im = (Imaging) id;
    /* Note: bitmap fonts within ttf fonts do not work, see #891/pr#960 */
    load_flags = FT_LOAD_NO_BITMAP;
    if (stroker == NULL) {
        load_flags |= FT_LOAD_RENDER;
    }
    if (mask) {
        load_flags |= FT_LOAD_TARGET_MONO;
    }

    ascender = 0;
    for (i = 0; i < count; i++) {
        index = glyph_info[i].index;
        error = FT_Load_Glyph(self->face, index, load_flags);
        if (error) {
            return geterror(error);
        }

        glyph_slot = self->face->glyph;
        bitmap = glyph_slot->bitmap;

        temp = bitmap.rows - glyph_slot->bitmap_top;
        temp -= PIXEL(glyph_info[i].y_offset);
        if (temp > ascender)
            ascender = temp;
    }

    x = y = 0;
    horizontal_dir = dir && strcmp(dir, "ttb") == 0 ? 0 : 1;
    for (i = 0; i < count; i++) {
        index = glyph_info[i].index;
        error = FT_Load_Glyph(self->face, index, load_flags);
        if (error) {
            return geterror(error);
        }

        glyph_slot = self->face->glyph;
        if (stroker != NULL) {
            error = FT_Get_Glyph(glyph_slot, &glyph);
            if (!error) {
                error = FT_Glyph_Stroke(&glyph, stroker, 1);
            }
            if (!error) {
                FT_Vector origin = {0, 0};
                error = FT_Glyph_To_Bitmap(&glyph, FT_RENDER_MODE_NORMAL, &origin, 1);
            }
            if (error) {
                return geterror(error);
            }

            bitmap_glyph = (FT_BitmapGlyph)glyph;

            bitmap = bitmap_glyph->bitmap;
            left = bitmap_glyph->left;

            FT_Done_Glyph(glyph);
        } else {
            bitmap = glyph_slot->bitmap;
            left = glyph_slot->bitmap_left;
        }

        if (horizontal_dir) {
            if (i == 0 && glyph_slot->metrics.horiBearingX < 0) {
                x = -glyph_slot->metrics.horiBearingX;
            }
            xx = PIXEL(x) + left;
            xx += PIXEL(glyph_info[i].x_offset) + stroke_width;
        } else {
            if (glyph_slot->metrics.vertBearingX < 0) {
                x = -glyph_slot->metrics.vertBearingX;
            }
            xx = im->xsize / 2 - bitmap.width / 2;
        }

        x0 = 0;
        x1 = bitmap.width;
        if (xx < 0)
            x0 = -xx;
        if (xx + x1 > im->xsize)
            x1 = im->xsize - xx;

        source = (unsigned char*) bitmap.buffer;
        for (bitmap_y = 0; bitmap_y < bitmap.rows; bitmap_y++) {
            if (horizontal_dir) {
                yy = bitmap_y + im->ysize - (PIXEL(glyph_slot->metrics.horiBearingY) + ascender);
                yy -= PIXEL(glyph_info[i].y_offset) + stroke_width * 2;
            } else {
                yy = bitmap_y + PIXEL(y + glyph_slot->metrics.vertBearingY) + ascender;
                yy += PIXEL(glyph_info[i].y_offset);
            }
            if (yy >= 0 && yy < im->ysize) {
                // blend this glyph into the buffer
                unsigned char *target = im->image8[yy] + xx;
                if (mask) {
                    // use monochrome mask (on palette images, etc)
                    int j, k, m = 128;
                    for (j = k = 0; j < x1; j++) {
                        if (j >= x0 && (source[k] & m))
                            target[j] = 255;
                        if (!(m >>= 1)) {
                            m = 128;
                            k++;
                        }
                    }
                } else {
                    // use antialiased rendering
                    int k;
                    for (k = x0; k < x1; k++) {
                        if (target[k] < source[k])
                            target[k] = source[k];
                    }
                }
            }
            source += bitmap.pitch;
        }
        x += glyph_info[i].x_advance;
        y -= glyph_info[i].y_advance;
    }

    FT_Stroker_Done(stroker);
    PyMem_Del(glyph_info);
    Py_RETURN_NONE;
}

#if FREETYPE_MAJOR > 2 ||\
    (FREETYPE_MAJOR == 2 && FREETYPE_MINOR > 9) ||\
    (FREETYPE_MAJOR == 2 && FREETYPE_MINOR == 9 && FREETYPE_PATCH == 1)
    static PyObject*
    font_getvarnames(FontObject* self, PyObject* args)
    {
        int error;
        FT_UInt i, j, num_namedstyles, name_count;
        FT_MM_Var *master;
        FT_SfntName name;
        PyObject *list_names, *list_name;

        error = FT_Get_MM_Var(self->face, &master);
        if (error)
            return geterror(error);

        num_namedstyles = master->num_namedstyles;
        list_names = PyList_New(num_namedstyles);

        name_count = FT_Get_Sfnt_Name_Count(self->face);
        for (i = 0; i < name_count; i++) {
            error = FT_Get_Sfnt_Name(self->face, i, &name);
            if (error)
                return geterror(error);

            for (j = 0; j < num_namedstyles; j++) {
                if (PyList_GetItem(list_names, j) != NULL)
                    continue;

                if (master->namedstyle[j].strid == name.name_id) {
                    list_name = Py_BuildValue(PY_ARG_BYTES_LENGTH,
                                              name.string, name.string_len);
                    PyList_SetItem(list_names, j, list_name);
                    break;
                }
            }
        }

        FT_Done_MM_Var(library, master);

        return list_names;
    }

    static PyObject*
    font_getvaraxes(FontObject* self, PyObject* args)
    {
        int error;
        FT_UInt i, j, num_axis, name_count;
        FT_MM_Var* master;
        FT_Var_Axis axis;
        FT_SfntName name;
        PyObject *list_axes, *list_axis, *axis_name;
        error = FT_Get_MM_Var(self->face, &master);
        if (error)
            return geterror(error);

        num_axis = master->num_axis;
        name_count = FT_Get_Sfnt_Name_Count(self->face);

        list_axes = PyList_New(num_axis);
        for (i = 0; i < num_axis; i++) {
            axis = master->axis[i];

            list_axis = PyDict_New();
            PyDict_SetItemString(list_axis, "minimum",
                                 PyInt_FromLong(axis.minimum / 65536));
            PyDict_SetItemString(list_axis, "default",
                                 PyInt_FromLong(axis.def / 65536));
            PyDict_SetItemString(list_axis, "maximum",
                                 PyInt_FromLong(axis.maximum / 65536));

            for (j = 0; j < name_count; j++) {
                error = FT_Get_Sfnt_Name(self->face, j, &name);
                if (error)
                    return geterror(error);

                if (name.name_id == axis.strid) {
                    axis_name = Py_BuildValue(PY_ARG_BYTES_LENGTH,
                                              name.string, name.string_len);
                    PyDict_SetItemString(list_axis, "name", axis_name);
                    break;
                }
            }

            PyList_SetItem(list_axes, i, list_axis);
        }

        FT_Done_MM_Var(library, master);

        return list_axes;
    }

    static PyObject*
    font_setvarname(FontObject* self, PyObject* args)
    {
        int error;

        int instance_index;
        if (!PyArg_ParseTuple(args, "i", &instance_index))
            return NULL;

        error = FT_Set_Named_Instance(self->face, instance_index);
        if (error)
            return geterror(error);

        Py_INCREF(Py_None);
        return Py_None;
    }

    static PyObject*
    font_setvaraxes(FontObject* self, PyObject* args)
    {
        int error;

        PyObject *axes, *item;
        Py_ssize_t i, num_coords;
        FT_Fixed *coords;
        FT_Fixed coord;
        if (!PyArg_ParseTuple(args, "O", &axes))
            return NULL;

        if (!PyList_Check(axes)) {
            PyErr_SetString(PyExc_TypeError, "argument must be a list");
            return NULL;
        }

        num_coords = PyObject_Length(axes);
        coords = malloc(2 * sizeof(coords));
        if (coords == NULL) {
            return PyErr_NoMemory();
        }
        for (i = 0; i < num_coords; i++) {
            item = PyList_GET_ITEM(axes, i);
            if (PyFloat_Check(item))
                coord = PyFloat_AS_DOUBLE(item);
            else if (PyInt_Check(item))
                coord = (float) PyInt_AS_LONG(item);
            else if (PyNumber_Check(item))
                coord = PyFloat_AsDouble(item);
            else {
                free(coords);
                PyErr_SetString(PyExc_TypeError, "list must contain numbers");
                return NULL;
            }
            coords[i] = coord * 65536;
        }

        error = FT_Set_Var_Design_Coordinates(self->face, num_coords, coords);
        free(coords);
        if (error)
            return geterror(error);

        Py_INCREF(Py_None);
        return Py_None;
    }
#endif

static void
font_dealloc(FontObject* self)
{
    if (self->face) {
        FT_Done_Face(self->face);
    }
    if (self->font_bytes) {
        PyMem_Free(self->font_bytes);
    }
    PyObject_Del(self);
}

static PyMethodDef font_methods[] = {
    {"render", (PyCFunction) font_render, METH_VARARGS},
    {"getsize", (PyCFunction) font_getsize, METH_VARARGS},
#if FREETYPE_MAJOR > 2 ||\
    (FREETYPE_MAJOR == 2 && FREETYPE_MINOR > 9) ||\
    (FREETYPE_MAJOR == 2 && FREETYPE_MINOR == 9 && FREETYPE_PATCH == 1)
    {"getvarnames", (PyCFunction) font_getvarnames, METH_VARARGS },
    {"getvaraxes", (PyCFunction) font_getvaraxes, METH_VARARGS },
    {"setvarname", (PyCFunction) font_setvarname, METH_VARARGS},
    {"setvaraxes", (PyCFunction) font_setvaraxes, METH_VARARGS},
#endif
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


    setraqm();
    v = PyBool_FromLong(!!p_raqm.raqm);
    PyDict_SetItemString(d, "HAVE_RAQM", v);

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

