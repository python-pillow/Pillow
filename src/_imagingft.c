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
#include "thirdparty/pythoncapi_compat.h"
#include "libImaging/Imaging.h"

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H
#include FT_BITMAP_H
#include FT_STROKER_H
#include FT_MULTIPLE_MASTERS_H
#include FT_SFNT_NAMES_H
#ifdef FT_COLOR_H
#include FT_COLOR_H
#endif

/* -------------------------------------------------------------------- */
/* error table */

#undef FTERRORS_H
#undef __FTERRORS_H__

#define FT_ERRORDEF(e, v, s) {e, s},
#define FT_ERROR_START_LIST {
#define FT_ERROR_END_LIST \
    { 0, 0 }              \
    }                     \
    ;

#ifdef HAVE_RAQM
#ifdef HAVE_RAQM_SYSTEM
#include <raqm.h>
#else
#include "thirdparty/raqm/raqm.h"
#ifdef HAVE_FRIBIDI_SYSTEM
#include <fribidi.h>
#else
#include "thirdparty/fribidi-shim/fribidi.h"
#include <hb.h>
#endif
#endif
#endif

static int have_raqm = 0;

#define LAYOUT_FALLBACK 0
#define LAYOUT_RAQM 1

typedef struct {
    int index, x_offset, x_advance, y_offset, y_advance;
    unsigned int cluster;
} GlyphInfo;

struct {
    int code;
    const char *message;
} ft_errors[] =

#include FT_ERRORS_H

    /* -------------------------------------------------------------------- */
    /* font objects */

    static FT_Library library;

typedef struct {
    PyObject_HEAD FT_Face face;
    unsigned char *font_bytes;
    int layout_engine;
} FontObject;

static PyTypeObject Font_Type;

/* round a 26.6 pixel coordinate to the nearest integer */
#define PIXEL(x) ((((x) + 32) & -64) >> 6)

static PyObject *
geterror(int code) {
    int i;

    for (i = 0; ft_errors[i].message; i++) {
        if (ft_errors[i].code == code) {
            PyErr_SetString(PyExc_OSError, ft_errors[i].message);
            return NULL;
        }
    }

    PyErr_SetString(PyExc_OSError, "unknown freetype error");
    return NULL;
}

static PyObject *
getfont(PyObject *self_, PyObject *args, PyObject *kw) {
    /* create a font object from a file name and a size (in pixels) */

    FontObject *self;
    int error = 0;

    char *filename = NULL;
    float size;
    FT_Size_RequestRec req;
    FT_Long width;
    Py_ssize_t index = 0;
    Py_ssize_t layout_engine = 0;
    unsigned char *encoding;
    unsigned char *font_bytes;
    Py_ssize_t font_bytes_size = 0;
    static char *kwlist[] = {
        "filename", "size", "index", "encoding", "font_bytes", "layout_engine", NULL
    };

    if (!library) {
        PyErr_SetString(PyExc_OSError, "failed to initialize FreeType library");
        return NULL;
    }

#if PY_MAJOR_VERSION > 3 || PY_MINOR_VERSION > 11
    PyConfig config;
    PyConfig_InitPythonConfig(&config);
    if (!PyArg_ParseTupleAndKeywords(
            args,
            kw,
            "etf|nsy#n",
            kwlist,
            config.filesystem_encoding,
            &filename,
            &size,
            &index,
            &encoding,
            &font_bytes,
            &font_bytes_size,
            &layout_engine
        )) {
        PyConfig_Clear(&config);
        return NULL;
    }
    PyConfig_Clear(&config);
#else
    if (!PyArg_ParseTupleAndKeywords(
            args,
            kw,
            "etf|nsy#n",
            kwlist,
            Py_FileSystemDefaultEncoding,
            &filename,
            &size,
            &index,
            &encoding,
            &font_bytes,
            &font_bytes_size,
            &layout_engine
        )) {
        return NULL;
    }
#endif

    self = PyObject_New(FontObject, &Font_Type);
    if (!self) {
        if (filename) {
            PyMem_Free(filename);
        }
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
            error = FT_Err_Out_Of_Memory;
        }
        if (!error) {
            memcpy(self->font_bytes, font_bytes, (size_t)font_bytes_size);
            error = FT_New_Memory_Face(
                library,
                (FT_Byte *)self->font_bytes,
                font_bytes_size,
                index,
                &self->face
            );
        }
    }

    if (!error) {
        width = size * 64;
        req.type = FT_SIZE_REQUEST_TYPE_NOMINAL;
        req.width = width;
        req.height = width;
        req.horiResolution = 0;
        req.vertResolution = 0;
        error = FT_Request_Size(self->face, &req);
    }

    if (!error && encoding && strlen((char *)encoding) == 4) {
        FT_Encoding encoding_tag =
            FT_MAKE_TAG(encoding[0], encoding[1], encoding[2], encoding[3]);
        error = FT_Select_Charmap(self->face, encoding_tag);
    }
    if (filename) {
        PyMem_Free(filename);
    }

    if (error) {
        if (self->font_bytes) {
            PyMem_Free(self->font_bytes);
            self->font_bytes = NULL;
        }
        Py_DECREF(self);
        return geterror(error);
    }

    return (PyObject *)self;
}

#ifdef HAVE_RAQM

static size_t
text_layout_raqm(
    PyObject *string,
    FontObject *self,
    const char *dir,
    PyObject *features,
    const char *lang,
    GlyphInfo **glyph_info
) {
    size_t i = 0, count = 0, start = 0;
    raqm_t *rq;
    raqm_glyph_t *glyphs = NULL;
    raqm_direction_t direction;

    rq = raqm_create();
    if (rq == NULL) {
        PyErr_SetString(PyExc_ValueError, "raqm_create() failed.");
        goto failed;
    }

    Py_ssize_t size;
    int set_text;
    if (PyUnicode_Check(string)) {
        Py_UCS4 *text = PyUnicode_AsUCS4Copy(string);
        size = PyUnicode_GET_LENGTH(string);
        if (!text || !size) {
            /* return 0 and clean up, no glyphs==no size,
               and raqm fails with empty strings */
            goto failed;
        }
        set_text = raqm_set_text(rq, text, size);
        PyMem_Free(text);
    } else if (PyBytes_Check(string)) {
        char *buffer;
        PyBytes_AsStringAndSize(string, &buffer, &size);
        if (!buffer || !size) {
            /* return 0 and clean up, no glyphs==no size,
               and raqm fails with empty strings */
            goto failed;
        }
        set_text = raqm_set_text_utf8(rq, buffer, size);
    } else {
        PyErr_SetString(PyExc_TypeError, "expected string or bytes");
        goto failed;
    }
    if (!set_text) {
        PyErr_SetString(PyExc_ValueError, "raqm_set_text() failed");
        goto failed;
    }
    if (lang && !raqm_set_language(rq, lang, start, size)) {
        PyErr_SetString(PyExc_ValueError, "raqm_set_language() failed");
        goto failed;
    }

    direction = RAQM_DIRECTION_DEFAULT;
    if (dir) {
        if (strcmp(dir, "rtl") == 0) {
            direction = RAQM_DIRECTION_RTL;
        } else if (strcmp(dir, "ltr") == 0) {
            direction = RAQM_DIRECTION_LTR;
        } else if (strcmp(dir, "ttb") == 0) {
            direction = RAQM_DIRECTION_TTB;
#if !defined(RAQM_VERSION_ATLEAST)
            /* RAQM_VERSION_ATLEAST was added in Raqm 0.7.0 */
            PyErr_SetString(
                PyExc_ValueError, "libraqm 0.7 or greater required for 'ttb' direction"
            );
            goto failed;
#endif
        } else {
            PyErr_SetString(
                PyExc_ValueError, "direction must be either 'rtl', 'ltr' or 'ttb'"
            );
            goto failed;
        }
    }

    if (!raqm_set_par_direction(rq, direction)) {
        PyErr_SetString(PyExc_ValueError, "raqm_set_par_direction() failed");
        goto failed;
    }

    if (features != Py_None) {
        int j, len;
        PyObject *seq = PySequence_Fast(features, "expected a sequence");
        if (!seq) {
            goto failed;
        }

        len = PySequence_Fast_GET_SIZE(seq);
        for (j = 0; j < len; j++) {
            PyObject *item = PySequence_Fast_GET_ITEM(seq, j);
            char *feature = NULL;
            Py_ssize_t size = 0;
            PyObject *bytes;

            if (!PyUnicode_Check(item)) {
                Py_DECREF(seq);
                PyErr_SetString(PyExc_TypeError, "expected a string");
                goto failed;
            }
            bytes = PyUnicode_AsUTF8String(item);
            if (bytes == NULL) {
                Py_DECREF(seq);
                goto failed;
            }
            feature = PyBytes_AS_STRING(bytes);
            size = PyBytes_GET_SIZE(bytes);
            if (!raqm_add_font_feature(rq, feature, size)) {
                Py_DECREF(seq);
                Py_DECREF(bytes);
                PyErr_SetString(PyExc_ValueError, "raqm_add_font_feature() failed");
                goto failed;
            }
            Py_DECREF(bytes);
        }
        Py_DECREF(seq);
    }

    if (!raqm_set_freetype_face(rq, self->face)) {
        PyErr_SetString(PyExc_RuntimeError, "raqm_set_freetype_face() failed.");
        goto failed;
    }

    if (!raqm_layout(rq)) {
        PyErr_SetString(PyExc_RuntimeError, "raqm_layout() failed.");
        goto failed;
    }

    glyphs = raqm_get_glyphs(rq, &count);
    if (glyphs == NULL) {
        PyErr_SetString(PyExc_ValueError, "raqm_get_glyphs() failed.");
        count = 0;
        goto failed;
    }

    (*glyph_info) = PyMem_New(GlyphInfo, count);
    if ((*glyph_info) == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyMem_New() failed");
        count = 0;
        goto failed;
    }

    for (i = 0; i < count; i++) {
        (*glyph_info)[i].index = glyphs[i].index;
        (*glyph_info)[i].x_offset = glyphs[i].x_offset;
        (*glyph_info)[i].x_advance = glyphs[i].x_advance;
        (*glyph_info)[i].y_offset = glyphs[i].y_offset;
        (*glyph_info)[i].y_advance = glyphs[i].y_advance;
        (*glyph_info)[i].cluster = glyphs[i].cluster;
    }

failed:
    raqm_destroy(rq);
    return count;
}

#endif

static size_t
text_layout_fallback(
    PyObject *string,
    FontObject *self,
    const char *dir,
    PyObject *features,
    const char *lang,
    GlyphInfo **glyph_info,
    int mask,
    int color
) {
    int error, load_flags, i;
    char *buffer = NULL;
    FT_ULong ch;
    Py_ssize_t count;
    FT_GlyphSlot glyph;
    FT_Bool kerning = FT_HAS_KERNING(self->face);
    FT_UInt last_index = 0;

    if (features != Py_None || dir != NULL || lang != NULL) {
        PyErr_SetString(
            PyExc_KeyError,
            "setting text direction, language or font features is not supported "
            "without libraqm"
        );
    }

    if (PyUnicode_Check(string)) {
        count = PyUnicode_GET_LENGTH(string);
    } else if (PyBytes_Check(string)) {
        PyBytes_AsStringAndSize(string, &buffer, &count);
    } else {
        PyErr_SetString(PyExc_TypeError, "expected string or bytes");
        return 0;
    }
    if (count == 0) {
        return 0;
    }

    (*glyph_info) = PyMem_New(GlyphInfo, count);
    if ((*glyph_info) == NULL) {
        PyErr_SetString(PyExc_MemoryError, "PyMem_New() failed");
        return 0;
    }

    load_flags = FT_LOAD_DEFAULT;
    if (mask) {
        load_flags |= FT_LOAD_TARGET_MONO;
    }
    if (color) {
        load_flags |= FT_LOAD_COLOR;
    }
    for (i = 0; i < count; i++) {
        if (buffer) {
            ch = buffer[i];
        } else {
            ch = PyUnicode_READ_CHAR(string, i);
        }
        (*glyph_info)[i].index = FT_Get_Char_Index(self->face, ch);
        error = FT_Load_Glyph(self->face, (*glyph_info)[i].index, load_flags);
        if (error) {
            geterror(error);
            return 0;
        }
        glyph = self->face->glyph;
        (*glyph_info)[i].x_offset = 0;
        (*glyph_info)[i].y_offset = 0;
        if (kerning && last_index && (*glyph_info)[i].index) {
            FT_Vector delta;
            if (FT_Get_Kerning(
                    self->face,
                    last_index,
                    (*glyph_info)[i].index,
                    ft_kerning_default,
                    &delta
                ) == 0) {
                (*glyph_info)[i - 1].x_advance += PIXEL(delta.x);
                (*glyph_info)[i - 1].y_advance += PIXEL(delta.y);
            }
        }

        (*glyph_info)[i].x_advance = glyph->metrics.horiAdvance;
        // y_advance is only used in ttb, which is not supported by basic layout
        (*glyph_info)[i].y_advance = 0;
        last_index = (*glyph_info)[i].index;
        (*glyph_info)[i].cluster = ch;
    }
    return count;
}

static size_t
text_layout(
    PyObject *string,
    FontObject *self,
    const char *dir,
    PyObject *features,
    const char *lang,
    GlyphInfo **glyph_info,
    int mask,
    int color
) {
    size_t count;
#ifdef HAVE_RAQM
    if (have_raqm && self->layout_engine == LAYOUT_RAQM) {
        count = text_layout_raqm(string, self, dir, features, lang, glyph_info);
    } else
#endif
    {
        count = text_layout_fallback(
            string, self, dir, features, lang, glyph_info, mask, color
        );
    }
    return count;
}

static PyObject *
font_getlength(FontObject *self, PyObject *args) {
    int length;                   /* length along primary axis, in 26.6 precision */
    GlyphInfo *glyph_info = NULL; /* computed text layout */
    size_t i, count;              /* glyph_info index and length */
    int horizontal_dir;           /* is primary axis horizontal? */
    int mask = 0;                 /* is FT_LOAD_TARGET_MONO enabled? */
    int color = 0;                /* is FT_LOAD_COLOR enabled? */
    const char *mode = NULL;
    const char *dir = NULL;
    const char *lang = NULL;
    PyObject *features = Py_None;
    PyObject *string;

    /* calculate size and bearing for a given string */

    if (!PyArg_ParseTuple(
            args, "O|zzOz:getlength", &string, &mode, &dir, &features, &lang
        )) {
        return NULL;
    }

    horizontal_dir = dir && strcmp(dir, "ttb") == 0 ? 0 : 1;

    mask = mode && strcmp(mode, "1") == 0;
    color = mode && strcmp(mode, "RGBA") == 0;

    count = text_layout(string, self, dir, features, lang, &glyph_info, mask, color);
    if (PyErr_Occurred()) {
        return NULL;
    }

    length = 0;
    for (i = 0; i < count; i++) {
        if (horizontal_dir) {
            length += glyph_info[i].x_advance;
        } else {
            length -= glyph_info[i].y_advance;
        }
    }

    if (glyph_info) {
        PyMem_Free(glyph_info);
        glyph_info = NULL;
    }

    return PyLong_FromLong(length);
}

static int
bounding_box_and_anchors(
    FT_Face face,
    const char *anchor,
    int horizontal_dir,
    GlyphInfo *glyph_info,
    size_t count,
    int load_flags,
    int *width,
    int *height,
    int *x_offset,
    int *y_offset
) {
    int position; /* pen position along primary axis, in 26.6 precision */
    int advanced; /* pen position along primary axis, in pixels */
    int px, py;   /* position of current glyph, in pixels */
    int x_min, x_max, y_min, y_max; /* text bounding box, in pixels */
    int x_anchor, y_anchor;         /* offset of point drawn at (0, 0), in pixels */
    int error;
    FT_Glyph glyph;
    FT_BBox bbox; /* glyph bounding box */
    size_t i;     /* glyph_info index */
    /*
     * text bounds are given by:
     *   - bounding boxes of individual glyphs
     *   - pen line, i.e. 0 to `advanced` along primary axis
     *     this means point (0, 0) is part of the text bounding box
     */
    position = x_min = x_max = y_min = y_max = 0;
    for (i = 0; i < count; i++) {
        if (horizontal_dir) {
            px = PIXEL(position + glyph_info[i].x_offset);
            py = PIXEL(glyph_info[i].y_offset);

            position += glyph_info[i].x_advance;
            advanced = PIXEL(position);
            if (advanced > x_max) {
                x_max = advanced;
            }
        } else {
            px = PIXEL(glyph_info[i].x_offset);
            py = PIXEL(position + glyph_info[i].y_offset);

            position += glyph_info[i].y_advance;
            advanced = PIXEL(position);
            if (advanced < y_min) {
                y_min = advanced;
            }
        }

        error = FT_Load_Glyph(face, glyph_info[i].index, load_flags);
        if (error) {
            geterror(error);
            return 1;
        }

        error = FT_Get_Glyph(face->glyph, &glyph);
        if (error) {
            geterror(error);
            return 1;
        }

        FT_Glyph_Get_CBox(glyph, FT_GLYPH_BBOX_PIXELS, &bbox);
        bbox.xMax += px;
        if (bbox.xMax > x_max) {
            x_max = bbox.xMax;
        }
        bbox.xMin += px;
        if (bbox.xMin < x_min) {
            x_min = bbox.xMin;
        }
        bbox.yMax += py;
        if (bbox.yMax > y_max) {
            y_max = bbox.yMax;
        }
        bbox.yMin += py;
        if (bbox.yMin < y_min) {
            y_min = bbox.yMin;
        }

        FT_Done_Glyph(glyph);
    }

    if (anchor == NULL) {
        anchor = horizontal_dir ? "la" : "lt";
    }
    if (strlen(anchor) != 2) {
        goto bad_anchor;
    }

    x_anchor = y_anchor = 0;
    if (count) {
        if (horizontal_dir) {
            switch (anchor[0]) {
                case 'l':  // left
                    x_anchor = 0;
                    break;
                case 'm':  // middle (left + right) / 2
                    x_anchor = PIXEL(position / 2);
                    break;
                case 'r':  // right
                    x_anchor = PIXEL(position);
                    break;
                case 's':  // vertical baseline
                default:
                    goto bad_anchor;
            }
            switch (anchor[1]) {
                case 'a':  // ascender
                    y_anchor = PIXEL(face->size->metrics.ascender);
                    break;
                case 't':  // top
                    y_anchor = y_max;
                    break;
                case 'm':  // middle (ascender + descender) / 2
                    y_anchor = PIXEL(
                        (face->size->metrics.ascender + face->size->metrics.descender) /
                        2
                    );
                    break;
                case 's':  // horizontal baseline
                    y_anchor = 0;
                    break;
                case 'b':  // bottom
                    y_anchor = y_min;
                    break;
                case 'd':  // descender
                    y_anchor = PIXEL(face->size->metrics.descender);
                    break;
                default:
                    goto bad_anchor;
            }
        } else {
            switch (anchor[0]) {
                case 'l':  // left
                    x_anchor = x_min;
                    break;
                case 'm':  // middle (left + right) / 2
                    x_anchor = (x_min + x_max) / 2;
                    break;
                case 'r':  // right
                    x_anchor = x_max;
                    break;
                case 's':  // vertical baseline
                    x_anchor = 0;
                    break;
                default:
                    goto bad_anchor;
            }
            switch (anchor[1]) {
                case 't':  // top
                    y_anchor = 0;
                    break;
                case 'm':  // middle (top + bottom) / 2
                    y_anchor = PIXEL(position / 2);
                    break;
                case 'b':  // bottom
                    y_anchor = PIXEL(position);
                    break;
                case 'a':  // ascender
                case 's':  // horizontal baseline
                case 'd':  // descender
                default:
                    goto bad_anchor;
            }
        }
    }
    *width = x_max - x_min;
    *height = y_max - y_min;
    *x_offset = -x_anchor + x_min;
    *y_offset = -(-y_anchor + y_max);
    return 0;

bad_anchor:
    PyErr_Format(PyExc_ValueError, "bad anchor specified: %s", anchor);
    return 1;
}

static PyObject *
font_getsize(FontObject *self, PyObject *args) {
    int width, height, x_offset, y_offset;
    int load_flags; /* FreeType load_flags parameter */
    int error;
    GlyphInfo *glyph_info = NULL; /* computed text layout */
    size_t count;                 /* glyph_info length */
    int horizontal_dir;           /* is primary axis horizontal? */
    int mask = 0;                 /* is FT_LOAD_TARGET_MONO enabled? */
    int color = 0;                /* is FT_LOAD_COLOR enabled? */
    const char *mode = NULL;
    const char *dir = NULL;
    const char *lang = NULL;
    const char *anchor = NULL;
    PyObject *features = Py_None;
    PyObject *string;

    /* calculate size and bearing for a given string */

    if (!PyArg_ParseTuple(
            args, "O|zzOzz:getsize", &string, &mode, &dir, &features, &lang, &anchor
        )) {
        return NULL;
    }

    horizontal_dir = dir && strcmp(dir, "ttb") == 0 ? 0 : 1;

    mask = mode && strcmp(mode, "1") == 0;
    color = mode && strcmp(mode, "RGBA") == 0;

    count = text_layout(string, self, dir, features, lang, &glyph_info, mask, color);
    if (PyErr_Occurred()) {
        return NULL;
    }

    load_flags = FT_LOAD_DEFAULT;
    if (mask) {
        load_flags |= FT_LOAD_TARGET_MONO;
    }
    if (color) {
        load_flags |= FT_LOAD_COLOR;
    }

    error = bounding_box_and_anchors(
        self->face,
        anchor,
        horizontal_dir,
        glyph_info,
        count,
        load_flags,
        &width,
        &height,
        &x_offset,
        &y_offset
    );
    if (glyph_info) {
        PyMem_Free(glyph_info);
        glyph_info = NULL;
    }
    if (error) {
        return NULL;
    }

    return Py_BuildValue("(ii)(ii)", width, height, x_offset, y_offset);
}

static PyObject *
font_render(FontObject *self, PyObject *args) {
    int x, y;         /* pen position, in 26.6 precision */
    int px, py;       /* position of current glyph, in pixels */
    int x_min, y_max; /* text offset in 26.6 precision */
    int load_flags;   /* FreeType load_flags parameter */
    int error;
    FT_Glyph glyph;
    FT_GlyphSlot glyph_slot;
    FT_Bitmap bitmap;
    FT_Bitmap bitmap_converted; /* initialized lazily, for non-8bpp fonts */
    FT_BitmapGlyph bitmap_glyph;
    FT_Stroker stroker = NULL;
    int bitmap_converted_ready = 0; /* has bitmap_converted been initialized */
    GlyphInfo *glyph_info = NULL;   /* computed text layout */
    size_t i, count;                /* glyph_info index and length */
    int xx, yy;                     /* pixel offset of current glyph bitmap */
    int x0, x1;                     /* horizontal bounds of glyph bitmap to copy */
    unsigned int bitmap_y;          /* glyph bitmap y index */
    unsigned char *source;          /* glyph bitmap source buffer */
    unsigned char convert_scale;    /* scale factor for non-8bpp bitmaps */
    PyObject *image;
    Imaging im;
    int mask = 0;  /* is FT_LOAD_TARGET_MONO enabled? */
    int color = 0; /* is FT_LOAD_COLOR enabled? */
    float stroke_width = 0;
    PY_LONG_LONG foreground_ink_long = 0;
    unsigned int foreground_ink;
    const char *mode = NULL;
    const char *dir = NULL;
    const char *lang = NULL;
    const char *anchor = NULL;
    PyObject *features = Py_None;
    PyObject *string;
    PyObject *fill;
    float x_start = 0;
    float y_start = 0;
    int width, height, x_offset, y_offset;
    int horizontal_dir; /* is primary axis horizontal? */

    /* render string into given buffer (the buffer *must* have
       the right size, or this will crash) */

    if (!PyArg_ParseTuple(
            args,
            "OO|zzOzfzLffO:render",
            &string,
            &fill,
            &mode,
            &dir,
            &features,
            &lang,
            &stroke_width,
            &anchor,
            &foreground_ink_long,
            &x_start,
            &y_start
        )) {
        return NULL;
    }

    mask = mode && strcmp(mode, "1") == 0;
    color = mode && strcmp(mode, "RGBA") == 0;

    foreground_ink = foreground_ink_long;

#ifdef FT_COLOR_H
    if (color) {
        FT_Color foreground_color;
        FT_Byte *ink = (FT_Byte *)&foreground_ink;
        foreground_color.red = ink[0];
        foreground_color.green = ink[1];
        foreground_color.blue = ink[2];
        foreground_color.alpha =
            (FT_Byte)255; /* ink alpha is handled in ImageDraw.text */
        FT_Palette_Set_Foreground_Color(self->face, foreground_color);
    }
#endif

    count = text_layout(string, self, dir, features, lang, &glyph_info, mask, color);
    if (PyErr_Occurred()) {
        return NULL;
    }

    load_flags = stroke_width ? FT_LOAD_NO_BITMAP : FT_LOAD_DEFAULT;
    if (mask) {
        load_flags |= FT_LOAD_TARGET_MONO;
    }
    if (color) {
        load_flags |= FT_LOAD_COLOR;
    }

    horizontal_dir = dir && strcmp(dir, "ttb") == 0 ? 0 : 1;

    error = bounding_box_and_anchors(
        self->face,
        anchor,
        horizontal_dir,
        glyph_info,
        count,
        load_flags,
        &width,
        &height,
        &x_offset,
        &y_offset
    );
    if (error) {
        PyMem_Del(glyph_info);
        return NULL;
    }

    width += ceil(stroke_width * 2 + x_start);
    height += ceil(stroke_width * 2 + y_start);
    image = PyObject_CallFunction(fill, "ii", width, height);
    if (image == NULL) {
        PyMem_Del(glyph_info);
        return NULL;
    }
    PyObject *imagePtr = PyObject_GetAttrString(image, "ptr");
    im = (Imaging)PyCapsule_GetPointer(imagePtr, IMAGING_MAGIC);
    Py_XDECREF(imagePtr);

    x_offset = round(x_offset - stroke_width);
    y_offset = round(y_offset - stroke_width);
    if (count == 0 || width == 0 || height == 0) {
        PyMem_Del(glyph_info);
        return Py_BuildValue("N(ii)", image, x_offset, y_offset);
    }

    if (stroke_width) {
        error = FT_Stroker_New(library, &stroker);
        if (error) {
            geterror(error);
            goto glyph_error;
        }

        FT_Stroker_Set(
            stroker,
            (FT_Fixed)round(stroke_width * 64),
            FT_STROKER_LINECAP_ROUND,
            FT_STROKER_LINEJOIN_ROUND,
            0
        );
    }

    /*
     * calculate x_min and y_max
     * must match font_getsize or there may be clipping!
     */
    x = y = x_min = y_max = 0;
    for (i = 0; i < count; i++) {
        px = PIXEL(x + glyph_info[i].x_offset);
        py = PIXEL(y + glyph_info[i].y_offset);

        error =
            FT_Load_Glyph(self->face, glyph_info[i].index, load_flags | FT_LOAD_RENDER);
        if (error) {
            geterror(error);
            goto glyph_error;
        }

        glyph_slot = self->face->glyph;
        bitmap = glyph_slot->bitmap;

        if (glyph_slot->bitmap_top + py > y_max) {
            y_max = glyph_slot->bitmap_top + py;
        }
        if (glyph_slot->bitmap_left + px < x_min) {
            x_min = glyph_slot->bitmap_left + px;
        }

        x += glyph_info[i].x_advance;
        y += glyph_info[i].y_advance;
    }

    /* set pen position to text origin */
    x = round((-x_min + stroke_width + x_start) * 64);
    y = round((-y_max + (-stroke_width) - y_start) * 64);

    if (stroker == NULL) {
        load_flags |= FT_LOAD_RENDER;
    }

    for (i = 0; i < count; i++) {
        px = PIXEL(x + glyph_info[i].x_offset);
        py = PIXEL(y + glyph_info[i].y_offset);

        error = FT_Load_Glyph(self->face, glyph_info[i].index, load_flags);
        if (error) {
            geterror(error);
            goto glyph_error;
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
                geterror(error);
                goto glyph_error;
            }

            bitmap_glyph = (FT_BitmapGlyph)glyph;

            bitmap = bitmap_glyph->bitmap;
            xx = px + bitmap_glyph->left;
            yy = -(py + bitmap_glyph->top);
        } else {
            bitmap = glyph_slot->bitmap;
            xx = px + glyph_slot->bitmap_left;
            yy = -(py + glyph_slot->bitmap_top);
        }

        // Null buffer, is dereferenced in FT_Bitmap_Convert
        if (!bitmap.buffer && bitmap.rows) {
            PyErr_SetString(PyExc_OSError, "Bitmap missing for glyph");
            goto glyph_error;
        }

        /* convert non-8bpp bitmaps */
        switch (bitmap.pixel_mode) {
            case FT_PIXEL_MODE_MONO:
                convert_scale = 255;
                break;
            case FT_PIXEL_MODE_GRAY2:
                convert_scale = 255 / 3;
                break;
            case FT_PIXEL_MODE_GRAY4:
                convert_scale = 255 / 15;
                break;
            default:
                convert_scale = 1;
        }
        switch (bitmap.pixel_mode) {
            case FT_PIXEL_MODE_MONO:
            case FT_PIXEL_MODE_GRAY2:
            case FT_PIXEL_MODE_GRAY4:
                if (!bitmap_converted_ready) {
                    FT_Bitmap_Init(&bitmap_converted);
                    bitmap_converted_ready = 1;
                }
                error = FT_Bitmap_Convert(library, &bitmap, &bitmap_converted, 1);
                if (error) {
                    geterror(error);
                    goto glyph_error;
                }
                bitmap = bitmap_converted;
                /* bitmap is now FT_PIXEL_MODE_GRAY, fall through */
            case FT_PIXEL_MODE_GRAY:
                break;
            case FT_PIXEL_MODE_BGRA:
                if (color) {
                    break;
                }
                /* we didn't ask for color, fall through to default */
            default:
                PyErr_SetString(PyExc_OSError, "unsupported bitmap pixel mode");
                goto glyph_error;
        }

        /* clip glyph bitmap width to target image bounds */
        x0 = 0;
        x1 = bitmap.width;
        if (xx < 0) {
            x0 = -xx;
        }
        if (xx + x1 > im->xsize) {
            x1 = im->xsize - xx;
        }

        source = (unsigned char *)bitmap.buffer;
        for (bitmap_y = 0; bitmap_y < bitmap.rows; bitmap_y++, yy++) {
            /* clip glyph bitmap height to target image bounds */
            if (yy >= 0 && yy < im->ysize) {
                /* blend this glyph into the buffer */
                int k;
                unsigned char *target;
                unsigned int tmp;
                if (color) {
                    /* target[RGB] returns the color, target[A] returns the mask */
                    /* target bands get split again in ImageDraw.text */
                    target = (unsigned char *)im->image[yy] + xx * 4;
                } else {
                    target = im->image8[yy] + xx;
                }
                if (color && bitmap.pixel_mode == FT_PIXEL_MODE_BGRA) {
                    /* paste color glyph */
                    for (k = x0; k < x1; k++) {
                        unsigned int src_alpha = source[k * 4 + 3];

                        /* paste only if source has data */
                        if (src_alpha > 0) {
                            /* unpremultiply BGRa */
                            int src_red =
                                CLIP8((255 * (int)source[k * 4 + 2]) / src_alpha);
                            int src_green =
                                CLIP8((255 * (int)source[k * 4 + 1]) / src_alpha);
                            int src_blue =
                                CLIP8((255 * (int)source[k * 4 + 0]) / src_alpha);

                            /* blend required if target has data */
                            if (target[k * 4 + 3] > 0) {
                                /* blend RGBA colors */
                                target[k * 4 + 0] =
                                    BLEND(src_alpha, target[k * 4 + 0], src_red, tmp);
                                target[k * 4 + 1] =
                                    BLEND(src_alpha, target[k * 4 + 1], src_green, tmp);
                                target[k * 4 + 2] =
                                    BLEND(src_alpha, target[k * 4 + 2], src_blue, tmp);
                                target[k * 4 + 3] = CLIP8(
                                    src_alpha +
                                    MULDIV255(target[k * 4 + 3], (255 - src_alpha), tmp)
                                );
                            } else {
                                /* paste unpremultiplied RGBA values */
                                target[k * 4 + 0] = src_red;
                                target[k * 4 + 1] = src_green;
                                target[k * 4 + 2] = src_blue;
                                target[k * 4 + 3] = src_alpha;
                            }
                        }
                    }
                } else if (bitmap.pixel_mode == FT_PIXEL_MODE_GRAY) {
                    if (color) {
                        unsigned char *ink = (unsigned char *)&foreground_ink;
                        for (k = x0; k < x1; k++) {
                            unsigned int src_alpha = source[k] * convert_scale;
                            if (src_alpha > 0) {
                                if (target[k * 4 + 3] > 0) {
                                    target[k * 4 + 0] = BLEND(
                                        src_alpha, target[k * 4 + 0], ink[0], tmp
                                    );
                                    target[k * 4 + 1] = BLEND(
                                        src_alpha, target[k * 4 + 1], ink[1], tmp
                                    );
                                    target[k * 4 + 2] = BLEND(
                                        src_alpha, target[k * 4 + 2], ink[2], tmp
                                    );
                                    target[k * 4 + 3] = CLIP8(
                                        src_alpha +
                                        MULDIV255(
                                            target[k * 4 + 3], (255 - src_alpha), tmp
                                        )
                                    );
                                } else {
                                    target[k * 4 + 0] = ink[0];
                                    target[k * 4 + 1] = ink[1];
                                    target[k * 4 + 2] = ink[2];
                                    target[k * 4 + 3] = src_alpha;
                                }
                            }
                        }
                    } else {
                        for (k = x0; k < x1; k++) {
                            unsigned int src_alpha = source[k] * convert_scale;
                            if (src_alpha > 0) {
                                target[k] =
                                    target[k] > 0
                                        ? CLIP8(
                                              src_alpha +
                                              MULDIV255(
                                                  target[k], (255 - src_alpha), tmp
                                              )
                                          )
                                        : src_alpha;
                            }
                        }
                    }
                } else {
                    PyErr_SetString(PyExc_OSError, "unsupported bitmap pixel mode");
                    goto glyph_error;
                }
            }
            source += bitmap.pitch;
        }
        x += glyph_info[i].x_advance;
        y += glyph_info[i].y_advance;
        if (stroker != NULL) {
            FT_Done_Glyph(glyph);
        }
    }

    if (bitmap_converted_ready) {
        FT_Bitmap_Done(library, &bitmap_converted);
    }
    FT_Stroker_Done(stroker);
    PyMem_Del(glyph_info);
    return Py_BuildValue("N(ii)", image, x_offset, y_offset);

glyph_error:
    Py_DECREF(image);
    if (stroker != NULL) {
        FT_Done_Glyph(glyph);
    }
    if (bitmap_converted_ready) {
        FT_Bitmap_Done(library, &bitmap_converted);
    }
    FT_Stroker_Done(stroker);
    PyMem_Del(glyph_info);
    return NULL;
}

#if FREETYPE_MAJOR > 2 || (FREETYPE_MAJOR == 2 && FREETYPE_MINOR > 9) || \
    (FREETYPE_MAJOR == 2 && FREETYPE_MINOR == 9 && FREETYPE_PATCH == 1)
static PyObject *
font_getvarnames(FontObject *self) {
    int error;
    FT_UInt i, j, num_namedstyles, name_count;
    FT_MM_Var *master;
    FT_SfntName name;
    PyObject *list_names, *list_name;

    error = FT_Get_MM_Var(self->face, &master);
    if (error) {
        return geterror(error);
    }

    num_namedstyles = master->num_namedstyles;
    list_names = PyList_New(num_namedstyles);
    if (list_names == NULL) {
        FT_Done_MM_Var(library, master);
        return NULL;
    }

    int *list_names_filled = PyMem_Malloc(num_namedstyles * sizeof(int));
    if (list_names_filled == NULL) {
        Py_DECREF(list_names);
        FT_Done_MM_Var(library, master);
        return PyErr_NoMemory();
    }

    for (unsigned int i = 0; i < num_namedstyles; i++) {
        list_names_filled[i] = 0;
    }

    name_count = FT_Get_Sfnt_Name_Count(self->face);
    for (i = 0; i < name_count; i++) {
        error = FT_Get_Sfnt_Name(self->face, i, &name);
        if (error) {
            PyMem_Free(list_names_filled);
            Py_DECREF(list_names);
            FT_Done_MM_Var(library, master);
            return geterror(error);
        }

        for (j = 0; j < num_namedstyles; j++) {
            if (list_names_filled[j]) {
                continue;
            }

            if (master->namedstyle[j].strid == name.name_id) {
                list_name = Py_BuildValue("y#", name.string, name.string_len);
                if (list_name == NULL) {
                    PyMem_Free(list_names_filled);
                    Py_DECREF(list_names);
                    FT_Done_MM_Var(library, master);
                    return NULL;
                }
                PyList_SetItem(list_names, j, list_name);
                list_names_filled[j] = 1;
                break;
            }
        }
    }

    PyMem_Free(list_names_filled);
    FT_Done_MM_Var(library, master);
    return list_names;
}

static PyObject *
font_getvaraxes(FontObject *self) {
    int error;
    FT_UInt i, j, num_axis, name_count;
    FT_MM_Var *master;
    FT_Var_Axis axis;
    FT_SfntName name;
    PyObject *list_axes, *list_axis, *axis_name;
    error = FT_Get_MM_Var(self->face, &master);
    if (error) {
        return geterror(error);
    }

    num_axis = master->num_axis;
    name_count = FT_Get_Sfnt_Name_Count(self->face);

    list_axes = PyList_New(num_axis);
    if (list_axes == NULL) {
        FT_Done_MM_Var(library, master);
        return NULL;
    }
    for (i = 0; i < num_axis; i++) {
        axis = master->axis[i];

        list_axis = PyDict_New();
        if (list_axis == NULL) {
            Py_DECREF(list_axes);
            FT_Done_MM_Var(library, master);
            return NULL;
        }
        PyObject *minimum = PyLong_FromLong(axis.minimum / 65536);
        PyDict_SetItemString(list_axis, "minimum", minimum ? minimum : Py_None);
        Py_XDECREF(minimum);

        PyObject *def = PyLong_FromLong(axis.def / 65536);
        PyDict_SetItemString(list_axis, "default", def ? def : Py_None);
        Py_XDECREF(def);

        PyObject *maximum = PyLong_FromLong(axis.maximum / 65536);
        PyDict_SetItemString(list_axis, "maximum", maximum ? maximum : Py_None);
        Py_XDECREF(maximum);

        for (j = 0; j < name_count; j++) {
            error = FT_Get_Sfnt_Name(self->face, j, &name);
            if (error) {
                Py_DECREF(list_axis);
                Py_DECREF(list_axes);
                FT_Done_MM_Var(library, master);
                return geterror(error);
            }

            if (name.name_id == axis.strid) {
                axis_name = Py_BuildValue("y#", name.string, name.string_len);
                if (axis_name == NULL) {
                    Py_DECREF(list_axis);
                    Py_DECREF(list_axes);
                    FT_Done_MM_Var(library, master);
                    return NULL;
                }
                PyDict_SetItemString(list_axis, "name", axis_name);
                Py_DECREF(axis_name);
                break;
            }
        }

        PyList_SetItem(list_axes, i, list_axis);
    }

    FT_Done_MM_Var(library, master);

    return list_axes;
}

static PyObject *
font_setvarname(FontObject *self, PyObject *args) {
    int error;

    int instance_index;
    if (!PyArg_ParseTuple(args, "i", &instance_index)) {
        return NULL;
    }

    error = FT_Set_Named_Instance(self->face, instance_index);
    if (error) {
        return geterror(error);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
font_setvaraxes(FontObject *self, PyObject *args) {
    int error;

    PyObject *axes, *item;
    Py_ssize_t i, num_coords;
    FT_Fixed *coords;
    FT_Fixed coord;
    if (!PyArg_ParseTuple(args, "O", &axes)) {
        return NULL;
    }

    if (!PyList_Check(axes)) {
        PyErr_SetString(PyExc_TypeError, "argument must be a list");
        return NULL;
    }

    num_coords = PyObject_Length(axes);
    coords = (FT_Fixed *)malloc(num_coords * sizeof(FT_Fixed));
    if (coords == NULL) {
        return PyErr_NoMemory();
    }
    for (i = 0; i < num_coords; i++) {
        item = PyList_GetItemRef(axes, i);
        if (item == NULL) {
            free(coords);
            return NULL;
        }

        if (PyFloat_Check(item)) {
            coord = PyFloat_AS_DOUBLE(item);
        } else if (PyLong_Check(item)) {
            coord = (float)PyLong_AS_LONG(item);
        } else if (PyNumber_Check(item)) {
            coord = PyFloat_AsDouble(item);
        } else {
            Py_DECREF(item);
            free(coords);
            PyErr_SetString(PyExc_TypeError, "list must contain numbers");
            return NULL;
        }
        Py_DECREF(item);
        coords[i] = coord * 65536;
    }

    error = FT_Set_Var_Design_Coordinates(self->face, num_coords, coords);
    free(coords);
    if (error) {
        return geterror(error);
    }

    Py_INCREF(Py_None);
    return Py_None;
}
#endif

static void
font_dealloc(FontObject *self) {
    if (self->face) {
        FT_Done_Face(self->face);
    }
    if (self->font_bytes) {
        PyMem_Free(self->font_bytes);
    }
    PyObject_Del(self);
}

static PyMethodDef font_methods[] = {
    {"render", (PyCFunction)font_render, METH_VARARGS},
    {"getsize", (PyCFunction)font_getsize, METH_VARARGS},
    {"getlength", (PyCFunction)font_getlength, METH_VARARGS},
#if FREETYPE_MAJOR > 2 || (FREETYPE_MAJOR == 2 && FREETYPE_MINOR > 9) || \
    (FREETYPE_MAJOR == 2 && FREETYPE_MINOR == 9 && FREETYPE_PATCH == 1)
    {"getvarnames", (PyCFunction)font_getvarnames, METH_NOARGS},
    {"getvaraxes", (PyCFunction)font_getvaraxes, METH_NOARGS},
    {"setvarname", (PyCFunction)font_setvarname, METH_VARARGS},
    {"setvaraxes", (PyCFunction)font_setvaraxes, METH_VARARGS},
#endif
    {NULL, NULL}
};

static PyObject *
font_getattr_family(FontObject *self, void *closure) {
    if (self->face->family_name) {
        return PyUnicode_FromString(self->face->family_name);
    }
    Py_RETURN_NONE;
}

static PyObject *
font_getattr_style(FontObject *self, void *closure) {
    if (self->face->style_name) {
        return PyUnicode_FromString(self->face->style_name);
    }
    Py_RETURN_NONE;
}

static PyObject *
font_getattr_ascent(FontObject *self, void *closure) {
    return PyLong_FromLong(PIXEL(self->face->size->metrics.ascender));
}

static PyObject *
font_getattr_descent(FontObject *self, void *closure) {
    return PyLong_FromLong(-PIXEL(self->face->size->metrics.descender));
}

static PyObject *
font_getattr_height(FontObject *self, void *closure) {
    return PyLong_FromLong(PIXEL(self->face->size->metrics.height));
}

static PyObject *
font_getattr_x_ppem(FontObject *self, void *closure) {
    return PyLong_FromLong(self->face->size->metrics.x_ppem);
}

static PyObject *
font_getattr_y_ppem(FontObject *self, void *closure) {
    return PyLong_FromLong(self->face->size->metrics.y_ppem);
}

static PyObject *
font_getattr_glyphs(FontObject *self, void *closure) {
    return PyLong_FromLong(self->face->num_glyphs);
}

static struct PyGetSetDef font_getsetters[] = {
    {"family", (getter)font_getattr_family},
    {"style", (getter)font_getattr_style},
    {"ascent", (getter)font_getattr_ascent},
    {"descent", (getter)font_getattr_descent},
    {"height", (getter)font_getattr_height},
    {"x_ppem", (getter)font_getattr_x_ppem},
    {"y_ppem", (getter)font_getattr_y_ppem},
    {"glyphs", (getter)font_getattr_glyphs},
    {NULL}
};

static PyTypeObject Font_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "Font", /*tp_name*/
    sizeof(FontObject),                    /*tp_basicsize*/
    0,                                     /*tp_itemsize*/
    /* methods */
    (destructor)font_dealloc, /*tp_dealloc*/
    0,                        /*tp_vectorcall_offset*/
    0,                        /*tp_getattr*/
    0,                        /*tp_setattr*/
    0,                        /*tp_as_async*/
    0,                        /*tp_repr*/
    0,                        /*tp_as_number*/
    0,                        /*tp_as_sequence*/
    0,                        /*tp_as_mapping*/
    0,                        /*tp_hash*/
    0,                        /*tp_call*/
    0,                        /*tp_str*/
    0,                        /*tp_getattro*/
    0,                        /*tp_setattro*/
    0,                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,       /*tp_flags*/
    0,                        /*tp_doc*/
    0,                        /*tp_traverse*/
    0,                        /*tp_clear*/
    0,                        /*tp_richcompare*/
    0,                        /*tp_weaklistoffset*/
    0,                        /*tp_iter*/
    0,                        /*tp_iternext*/
    font_methods,             /*tp_methods*/
    0,                        /*tp_members*/
    font_getsetters,          /*tp_getset*/
};

static PyMethodDef _functions[] = {
    {"getfont", (PyCFunction)getfont, METH_VARARGS | METH_KEYWORDS}, {NULL, NULL}
};

static int
setup_module(PyObject *m) {
    PyObject *d;
    PyObject *v;
    int major, minor, patch;

    d = PyModule_GetDict(m);

    /* Ready object type */
    PyType_Ready(&Font_Type);

    if (FT_Init_FreeType(&library)) {
        return 0; /* leave it uninitialized */
    }

    FT_Library_Version(library, &major, &minor, &patch);

    v = PyUnicode_FromFormat("%d.%d.%d", major, minor, patch);
    PyDict_SetItemString(d, "freetype2_version", v ? v : Py_None);
    Py_XDECREF(v);

#ifdef HAVE_RAQM
#if defined(HAVE_RAQM_SYSTEM) || defined(HAVE_FRIBIDI_SYSTEM)
    have_raqm = 1;
#else
    load_fribidi();
    have_raqm = !!p_fribidi;
#endif
#else
    have_raqm = 0;
#endif

    /* if we have Raqm, we have all three (but possibly no version info) */
    v = PyBool_FromLong(have_raqm);
    PyDict_SetItemString(d, "HAVE_RAQM", v);
    PyDict_SetItemString(d, "HAVE_FRIBIDI", v);
    PyDict_SetItemString(d, "HAVE_HARFBUZZ", v);
    Py_DECREF(v);
    if (have_raqm) {
        v = NULL;
#ifdef RAQM_VERSION_MAJOR
        v = PyUnicode_FromString(raqm_version_string());
#endif
        PyDict_SetItemString(d, "raqm_version", v ? v : Py_None);
        Py_XDECREF(v);

        v = NULL;
#ifdef FRIBIDI_MAJOR_VERSION
        {
            const char *a = strchr(fribidi_version_info, ')');
            const char *b = strchr(fribidi_version_info, '\n');
            if (a && b && a + 2 < b) {
                v = PyUnicode_FromStringAndSize(a + 2, b - (a + 2));
            }
        }
#endif
        PyDict_SetItemString(d, "fribidi_version", v ? v : Py_None);
        Py_XDECREF(v);

        v = NULL;
#ifdef HB_VERSION_STRING
        v = PyUnicode_FromString(hb_version_string());
#endif
        PyDict_SetItemString(d, "harfbuzz_version", v ? v : Py_None);
        Py_XDECREF(v);
    }

    return 0;
}

PyMODINIT_FUNC
PyInit__imagingft(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingft", /* m_name */
        NULL,         /* m_doc */
        -1,           /* m_size */
        _functions,   /* m_methods */
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
