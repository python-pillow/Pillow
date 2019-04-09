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
  int index, x_offset, x_advance, y_offset;
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

    if (!PyArg_ParseTupleAndKeywords(args, kw, "eti|is"PY_ARG_BYTES_LENGTH"i",
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
        }
        Py_DECREF(self);
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

static size_t
text_layout_raqm(PyObject* string, FontObject* self, const char* dir, PyObject *features,
                 const char* lang, GlyphInfo **glyph_info, int mask)
{
    int i = 0;
    raqm_t *rq;
    size_t count = 0;
    raqm_glyph_t *glyphs = NULL;
    raqm_glyph_t_01 *glyphs_01 = NULL;
    raqm_direction_t direction;
    size_t start = 0;

    rq = (*p_raqm.create)();
    if (rq == NULL) {
        PyErr_SetString(PyExc_ValueError, "raqm_create() failed.");
        goto failed;
    }

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
        else if (strcmp(dir, "ttb") == 0)
            direction = RAQM_DIRECTION_TTB;
        else {
            PyErr_SetString(PyExc_ValueError, "direction must be either 'rtl', 'ltr' or 'ttb'");
            goto failed;
        }
    }

    if (!(*p_raqm.set_par_direction)(rq, direction)) {
        PyErr_SetString(PyExc_ValueError, "raqm_set_par_direction() failed");
        goto failed;
    }

    if (features != Py_None) {
        int len;
        PyObject *seq = PySequence_Fast(features, "expected a sequence");
        if (!seq) {
            goto failed;
        }

        len = PySequence_Size(seq);
        for (i = 0; i < len; i++) {
            PyObject *item = PySequence_Fast_GET_ITEM(seq, i);
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

    if (p_raqm.version == 1){
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

    if (p_raqm.version == 1){
        for (i = 0; i < count; i++) {
            (*glyph_info)[i].index = glyphs_01[i].index;
            (*glyph_info)[i].x_offset = glyphs_01[i].x_offset;
            (*glyph_info)[i].x_advance = glyphs_01[i].x_advance;
            (*glyph_info)[i].y_offset = glyphs_01[i].y_offset;
            (*glyph_info)[i].cluster = glyphs_01[i].cluster;
        }
    } else {
        for (i = 0; i < count; i++) {
            (*glyph_info)[i].index = glyphs[i].index;
            (*glyph_info)[i].x_offset = glyphs[i].x_offset;
            (*glyph_info)[i].x_advance = glyphs[i].x_advance;
            (*glyph_info)[i].y_offset = glyphs[i].y_offset;
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
        }

        (*glyph_info)[i].x_advance = glyph->metrics.horiAdvance;
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
    int i, x, y_max, y_min;
    FT_Face face;
    int xoffset, yoffset;
    const char *dir = NULL;
    const char *lang = NULL;
    size_t count;
    GlyphInfo *glyph_info = NULL;
    PyObject *features = Py_None;

    /* calculate size and bearing for a given string */

    PyObject* string;
    if (!PyArg_ParseTuple(args, "O|zOz:getsize", &string, &dir, &features, &lang))
        return NULL;

    face = NULL;
    xoffset = yoffset = 0;
    y_max = y_min = 0;

    count = text_layout(string, self, dir, features, lang, &glyph_info, 0);
    if (PyErr_Occurred()) {
        return NULL;
    }


    for (x = i = 0; i < count; i++) {
        int index, error;
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

        if (i == 0 && face->glyph->metrics.horiBearingX < 0) {
            xoffset = face->glyph->metrics.horiBearingX;
            x -= xoffset;
        }

        x += glyph_info[i].x_advance;

        if (i == count - 1)
        {
            int offset;
            offset = glyph_info[i].x_advance -
                    face->glyph->metrics.width -
                    face->glyph->metrics.horiBearingX;
            if (offset < 0)
                x -= offset;
        }

        FT_Get_Glyph(face->glyph, &glyph);
        FT_Glyph_Get_CBox(glyph, FT_GLYPH_BBOX_SUBPIXELS, &bbox);
        bbox.yMax -= glyph_info[i].y_offset;
        bbox.yMin -= glyph_info[i].y_offset;
        if (bbox.yMax > y_max)
            y_max = bbox.yMax;
        if (bbox.yMin < y_min)
            y_min = bbox.yMin;

        /* find max distance of baseline from top */
        if (face->glyph->metrics.horiBearingY > yoffset)
            yoffset = face->glyph->metrics.horiBearingY;

        FT_Done_Glyph(glyph);
    }

    if (glyph_info) {
        PyMem_Free(glyph_info);
        glyph_info = NULL;
    }

    if (face) {

        /* left bearing */
        if (xoffset < 0)
            x -= xoffset;
        else
            xoffset = 0;
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
font_render(FontObject* self, PyObject* args)
{
    int i, x, y;
    Imaging im;
    int index, error, ascender;
    int load_flags;
    unsigned char *source;
    FT_GlyphSlot glyph;
    /* render string into given buffer (the buffer *must* have
       the right size, or this will crash) */
    PyObject* string;
    Py_ssize_t id;
    int mask = 0;
    int temp;
    int xx, x0, x1;
    const char *dir = NULL;
    const char *lang = NULL;
    size_t count;
    GlyphInfo *glyph_info;
    PyObject *features = NULL;

    if (!PyArg_ParseTuple(args, "On|izOz:render", &string,  &id, &mask, &dir, &features, &lang)) {
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

    im = (Imaging) id;
    /* Note: bitmap fonts within ttf fonts do not work, see #891/pr#960 */
    load_flags = FT_LOAD_RENDER|FT_LOAD_NO_BITMAP;
    if (mask)
        load_flags |= FT_LOAD_TARGET_MONO;

    ascender = 0;
    for (i = 0; i < count; i++) {
        index = glyph_info[i].index;
        error = FT_Load_Glyph(self->face, index, load_flags);
        if (error)
            return geterror(error);

        glyph = self->face->glyph;
        temp = (glyph->bitmap.rows - glyph->bitmap_top);
        temp -= PIXEL(glyph_info[i].y_offset);
        if (temp > ascender)
            ascender = temp;
    }

    for (x = i = 0; i < count; i++) {
        if (i == 0 && self->face->glyph->metrics.horiBearingX < 0)
            x = -self->face->glyph->metrics.horiBearingX;

        index = glyph_info[i].index;
        error = FT_Load_Glyph(self->face, index, load_flags);
        if (error)
            return geterror(error);

        if (i == 0 && self->face->glyph->metrics.horiBearingX < 0) {
            x = -self->face->glyph->metrics.horiBearingX;
     }

        glyph = self->face->glyph;

        source = (unsigned char*) glyph->bitmap.buffer;
        xx = PIXEL(x) + glyph->bitmap_left;
        xx += PIXEL(glyph_info[i].x_offset);
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
                yy -= PIXEL(glyph_info[i].y_offset);
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
                yy -= PIXEL(glyph_info[i].y_offset);
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
        x += glyph_info[i].x_advance;
    }

    PyMem_Del(glyph_info);
    Py_RETURN_NONE;
}

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

