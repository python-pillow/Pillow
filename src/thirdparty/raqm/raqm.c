/*
 * Copyright © 2015 Information Technology Authority (ITA) <foss@ita.gov.om>
 * Copyright © 2016-2022 Khaled Hosny <khaled@aliftype.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 *
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <assert.h>
#include <string.h>

#ifdef RAQM_SHEENBIDI
#include <SheenBidi.h>
#else
#ifdef HAVE_FRIBIDI_SYSTEM
#include <fribidi.h>
#else
#include "../fribidi-shim/fribidi.h"
#endif
#endif

#include <hb.h>
#include <hb-ft.h>

#include "raqm.h"

/**
 * SECTION:raqm
 * @title: Raqm
 * @short_description: A library for complex text layout
 * @include: raqm.h
 *
 * Raqm is a light weight text layout library with strong emphasis on
 * supporting languages and writing systems that require complex text layout.
 *
 * The main object in Raqm API is #raqm_t, it stores all the states of the
 * input text, its properties, and the output of the layout process.
 *
 * To start, you create a #raqm_t object, add text and font(s) to it, run the
 * layout process, and finally query about the output. For example:
 *
 * |[<!-- language="C" -->
 * #include "raqm.h"
 *
 * int
 * main (int argc, char *argv[])
 * {
 *     const char *fontfile;
 *     const char *text;
 *     const char *direction;
 *     const char *language;
 *     int ret = 1;
 *
 *     FT_Library library = NULL;
 *     FT_Face face = NULL;
 *
 *     if (argc < 5)
 *     {
 *         printf ("Usage: %s FONT_FILE TEXT DIRECTION LANG\n", argv[0]);
 *         return 1;
 *     }
 *
 *     fontfile =  argv[1];
 *     text = argv[2];
 *     direction = argv[3];
 *     language = argv[4];
 *
 *     if (FT_Init_FreeType (&library) == 0)
 *     {
 *       if (FT_New_Face (library, fontfile, 0, &face) == 0)
 *       {
 *         if (FT_Set_Char_Size (face, face->units_per_EM, 0, 0, 0) == 0)
 *         {
 *           raqm_t *rq = raqm_create ();
 *           if (rq != NULL)
 *           {
 *             raqm_direction_t dir = RAQM_DIRECTION_DEFAULT;
 *
 *             if (strcmp (direction, "r") == 0)
 *               dir = RAQM_DIRECTION_RTL;
 *             else if (strcmp (direction, "l") == 0)
 *               dir = RAQM_DIRECTION_LTR;
 *
 *             if (raqm_set_text_utf8 (rq, text, strlen (text)) &&
 *                 raqm_set_freetype_face (rq, face) &&
 *                 raqm_set_par_direction (rq, dir) &&
 *                 raqm_set_language (rq, language, 0, strlen (text)) &&
 *                 raqm_layout (rq))
 *             {
 *               size_t count, i;
 *               raqm_glyph_t *glyphs = raqm_get_glyphs (rq, &count);
 *
 *               ret = !(glyphs != NULL || count == 0);
 *
 *               printf("glyph count: %zu\n", count);
 *               for (i = 0; i < count; i++)
 *               {
 *                   printf ("gid#%d off: (%d, %d) adv: (%d, %d) idx: %d\n",
 *                           glyphs[i].index,
 *                           glyphs[i].x_offset,
 *                           glyphs[i].y_offset,
 *                           glyphs[i].x_advance,
 *                           glyphs[i].y_advance,
 *                           glyphs[i].cluster);
 *               }
 *             }
 *
 *             raqm_destroy (rq);
 *           }
 *         }
 *
 *         FT_Done_Face (face);
 *       }
 *
 *       FT_Done_FreeType (library);
 *     }
 *
 *     return ret;
 * }
 * ]|
 * To compile this example:
 * |[<prompt>
 * cc -o test test.c `pkg-config --libs --cflags raqm`
 * ]|
 */

/* For enabling debug mode */
/*#define RAQM_DEBUG 1*/
#ifdef RAQM_DEBUG
#define RAQM_DBG(...) fprintf (stderr, __VA_ARGS__)
#else
#define RAQM_DBG(...)
#endif

#ifdef RAQM_TESTING
# define RAQM_TEST(...) printf (__VA_ARGS__)
# define SCRIPT_TO_STRING(script) \
    char buff[5]; \
    hb_tag_to_string (hb_script_to_iso15924_tag (script), buff); \
    buff[4] = '\0';
#else
# define RAQM_TEST(...)
#endif

#define RAQM_BIDI_LEVEL_IS_RTL(level) \
    ((level) & 1)

#ifdef RAQM_SHEENBIDI
  typedef SBLevel _raqm_bidi_level_t;
#else
  typedef FriBidiLevel _raqm_bidi_level_t;
#endif

typedef struct
{
  FT_Face       ftface;
  int           ftloadflags;
  hb_language_t lang;
  hb_script_t   script;
  int           spacing_after;
} _raqm_text_info;

typedef struct _raqm_run raqm_run_t;

struct _raqm
{
  int              ref_count;

  uint32_t        *text;
  uint16_t        *text_utf16;
  char            *text_utf8;
  size_t           text_len;
  size_t           text_capacity_bytes;

  _raqm_text_info *text_info;

  raqm_direction_t base_dir;
  raqm_direction_t resolved_dir;

  hb_feature_t    *features;
  size_t           features_len;

  raqm_run_t      *runs;
  raqm_run_t      *runs_pool;

  raqm_glyph_t    *glyphs;
  size_t           glyphs_capacity;

  int              invisible_glyph;
};

struct _raqm_run
{
  uint32_t       pos;
  uint32_t       len;

  hb_direction_t direction;
  hb_script_t    script;
  hb_font_t     *font;
  hb_buffer_t   *buffer;

  raqm_run_t    *next;
};

static size_t
_raqm_encoding_to_u32_index (raqm_t *rq,
                             size_t  index);

static bool
_raqm_allowed_grapheme_boundary (hb_codepoint_t l_char,
                                hb_codepoint_t r_char);

static void
_raqm_init_text_info (raqm_t *rq)
{
  hb_language_t default_lang = hb_language_get_default ();
  for (size_t i = 0; i < rq->text_len; i++)
  {
    rq->text_info[i].ftface = NULL;
    rq->text_info[i].ftloadflags = -1;
    rq->text_info[i].lang = default_lang;
    rq->text_info[i].script = HB_SCRIPT_INVALID;
    rq->text_info[i].spacing_after = 0;
  }
}

static void
_raqm_release_text_info (raqm_t *rq)
{
  if (!rq->text_info)
    return;

  for (size_t i = 0; i < rq->text_len; i++)
  {
    if (rq->text_info[i].ftface)
      FT_Done_Face (rq->text_info[i].ftface);
  }
}

static bool
_raqm_compare_text_info (_raqm_text_info a,
                         _raqm_text_info b)
{
  if (a.ftface != b.ftface)
    return false;

  if (a.ftloadflags != b.ftloadflags)
    return false;

  if (a.lang != b.lang)
    return false;

  if (a.script != b.script)
    return false;

  /* Spacing shouldn't break runs, so we don't compare them here. */

  return true;
}

static void
_raqm_free_text(raqm_t* rq)
{
  free (rq->text);
  rq->text = NULL;
  rq->text_info = NULL;
  rq->text_utf8 = NULL;
  rq->text_utf16 = NULL;
  rq->text_len = 0;
  rq->text_capacity_bytes = 0;
}

static bool
_raqm_alloc_text(raqm_t *rq,
                 size_t  len,
                 bool    need_utf8,
                 bool    need_utf16)
{
  /* Allocate contiguous memory block for texts and text_info */
  size_t mem_size = (sizeof (uint32_t) + sizeof (_raqm_text_info)) * len;
  if (need_utf8)
    mem_size += sizeof (char) * len;
  else if (need_utf16)
    mem_size += sizeof (uint16_t) * len;

  if (mem_size > rq->text_capacity_bytes)
  {
    void* new_mem = realloc (rq->text, mem_size);
    if (!new_mem)
    {
      _raqm_free_text (rq);
      return false;
    }

    rq->text_capacity_bytes = mem_size;
    rq->text = new_mem;
  }

  rq->text_info = (_raqm_text_info*)(rq->text + len);
  rq->text_utf8 = need_utf8 ? (char*)(rq->text_info + len) : NULL;
  rq->text_utf16 = need_utf16 ? (uint16_t*)(rq->text_info + len) : NULL;

  return true;
}

static raqm_run_t*
_raqm_alloc_run (raqm_t *rq)
{
  raqm_run_t *run = rq->runs_pool;
  if (run)
  {
    rq->runs_pool = run->next;
  }
  else
  {
    run = malloc (sizeof (raqm_run_t));
    run->font = NULL;
    run->buffer = NULL;
  }

  run->pos = 0;
  run->len = 0;
  run->direction = HB_DIRECTION_INVALID;
  run->script = HB_SCRIPT_INVALID;
  run->next = NULL;

  return run;
}

static void
_raqm_free_runs (raqm_run_t *runs)
{
  while (runs)
  {
    raqm_run_t *run = runs;
    runs = runs->next;

    if (run->buffer)
      hb_buffer_destroy (run->buffer);

    if (run->font)
      hb_font_destroy (run->font);

    free (run);
  }
}

/**
 * raqm_create:
 *
 * Creates a new #raqm_t with all its internal states initialized to their
 * defaults.
 *
 * Return value:
 * A newly allocated #raqm_t with a reference count of 1. The initial reference
 * count should be released with raqm_destroy() when you are done using the
 * #raqm_t. Returns `NULL` in case of error.
 *
 * Since: 0.1
 */
raqm_t *
raqm_create (void)
{
  raqm_t *rq;

  rq = malloc (sizeof (raqm_t));
  if (!rq)
    return NULL;

  rq->ref_count = 1;

  rq->base_dir = RAQM_DIRECTION_DEFAULT;
  rq->resolved_dir = RAQM_DIRECTION_DEFAULT;

  rq->features = NULL;
  rq->features_len = 0;

  rq->invisible_glyph = 0;

  rq->text = NULL;
  rq->text_utf16 = NULL;
  rq->text_utf8 = NULL;
  rq->text_info = NULL;
  rq->text_capacity_bytes = 0;
  rq->text_len = 0;

  rq->runs = NULL;
  rq->runs_pool = NULL;

  rq->glyphs = NULL;
  rq->glyphs_capacity = 0;

  return rq;
}

/**
 * raqm_reference:
 * @rq: a #raqm_t.
 *
 * Increases the reference count on @rq by one. This prevents @rq from being
 * destroyed until a matching call to raqm_destroy() is made.
 *
 * Return value:
 * The referenced #raqm_t.
 *
 * Since: 0.1
 */
raqm_t *
raqm_reference (raqm_t *rq)
{
  if (rq)
    rq->ref_count++;

  return rq;
}

/**
 * raqm_destroy:
 * @rq: a #raqm_t.
 *
 * Decreases the reference count on @rq by one. If the result is zero, then @rq
 * and all associated resources are freed.
 * See raqm_reference().
 *
 * Since: 0.1
 */
void
raqm_destroy (raqm_t *rq)
{
  if (!rq || --rq->ref_count != 0)
    return;

  _raqm_release_text_info (rq);
  _raqm_free_text (rq);
  _raqm_free_runs (rq->runs);
  _raqm_free_runs (rq->runs_pool);
  free (rq->glyphs);
  free (rq->features);
  free (rq);
}

/**
 * raqm_clear_contents:
 * @rq: a #raqm_t.
 *
 * Clears internal state of previously used raqm_t object, making it ready
 * for reuse and keeping some of allocated memory to increase performance.
 *
 * Since: 0.9
 */
void
raqm_clear_contents (raqm_t *rq)
{
  if (!rq)
    return;

  _raqm_release_text_info (rq);

  /* Return allocated runs to the pool, keep hb buffers for reuse */
  raqm_run_t *run = rq->runs;
  while (run)
  {
    if (run->buffer)
      hb_buffer_reset (run->buffer);

    if (run->font)
    {
      hb_font_destroy (run->font);
      run->font = NULL;
    }

    if (!run->next)
    {
      run->next = rq->runs_pool;
      rq->runs_pool = rq->runs;
      rq->runs = NULL;
      break;
    }

    run = run->next;
  }

  rq->text_len = 0;
  rq->resolved_dir = RAQM_DIRECTION_DEFAULT;
}

/**
 * raqm_set_text:
 * @rq: a #raqm_t.
 * @text: a UTF-32 encoded text string.
 * @len: the length of @text.
 *
 * Adds @text to @rq to be used for layout. It must be a valid UTF-32 text, any
 * invalid character will be replaced with U+FFFD. The text should typically
 * represent a full paragraph, since doing the layout of chunks of text
 * separately can give improper output.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_set_text (raqm_t         *rq,
               const uint32_t *text,
               size_t          len)
{
  if (!rq || !text)
    return false;

  /* Call raqm_clear_contents to reuse this raqm_t */
  if (rq->text_len)
    return false;

  /* Empty string, don’t fail but do nothing */
  if (!len)
    return true;

  if (!_raqm_alloc_text(rq, len, false, false))
      return false;

  rq->text_len = len;
  memcpy (rq->text, text, sizeof (uint32_t) * len);
  _raqm_init_text_info (rq);

  return true;
}

static void *
_raqm_get_utf8_codepoint (const void *str,
                          uint32_t *out_codepoint)
{
  const char *s = (const char *)str;

  if (0xf0 == (0xf8 & s[0]))
  {
    *out_codepoint = ((0x07 & s[0]) << 18) | ((0x3f & s[1]) << 12) | ((0x3f & s[2]) << 6) | (0x3f & s[3]);
    s += 4;
  }
  else if (0xe0 == (0xf0 & s[0]))
  {
    *out_codepoint = ((0x0f & s[0]) << 12) | ((0x3f & s[1]) << 6) | (0x3f & s[2]);
    s += 3;
  }
  else if (0xc0 == (0xe0 & s[0]))
  {
    *out_codepoint = ((0x1f & s[0]) << 6) | (0x3f & s[1]);
    s += 2;
  }
  else
  {
    *out_codepoint = s[0];
    s += 1;
  }

  return (void *)s;
}

static size_t
_raqm_u8_to_u32 (const char *text, size_t len, uint32_t *unicode)
{
  size_t in_len = 0;
  uint32_t *out_utf32 = unicode;
  const char *in_utf8 = text;

  while ((*in_utf8 != '\0') && (in_len < len))
  {
    in_utf8 = _raqm_get_utf8_codepoint (in_utf8, out_utf32);
    ++out_utf32;
    ++in_len;
  }

  return (out_utf32 - unicode);
}

static void *
_raqm_get_utf16_codepoint (const void *str,
                          uint32_t *out_codepoint)
{
  const uint16_t *s = (const uint16_t *)str;

  if (s[0] > 0xD800 && s[0] < 0xDBFF)
  {
    if (s[1] > 0xDC00 && s[1] < 0xDFFF)
    {
      uint32_t X = ((s[0] & ((1 << 6) -1)) << 10) | (s[1] & ((1 << 10) -1));
      uint32_t W = (s[0] >> 6) & ((1 << 5) - 1);
      *out_codepoint = (W+1) << 16 | X;
      s += 2;
    }
    else
    {
      /* A single high surrogate, this is an error. */
      *out_codepoint = s[0];
      s += 1;
    }
  }
  else
  {
      *out_codepoint = s[0];
      s += 1;
  }
  return (void *)s;
}

static size_t
_raqm_u16_to_u32 (const uint16_t *text, size_t len, uint32_t *unicode)
{
  size_t in_len = 0;
  uint32_t *out_utf32 = unicode;
  const uint16_t *in_utf16 = text;

  while ((*in_utf16 != '\0') && (in_len < len))
  {
    in_utf16 = _raqm_get_utf16_codepoint (in_utf16, out_utf32);
    ++out_utf32;
    ++in_len;
  }

  return (out_utf32 - unicode);
}

/**
 * raqm_set_text_utf8:
 * @rq: a #raqm_t.
 * @text: a UTF-8 encoded text string.
 * @len: the length of @text in UTF-8 bytes.
 *
 * Same as raqm_set_text(), but for text encoded in UTF-8 encoding.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_set_text_utf8 (raqm_t     *rq,
                    const char *text,
                    size_t      len)
{
  if (!rq || !text)
    return false;

  /* Call raqm_clear_contents to reuse this raqm_t */
  if (rq->text_len)
    return false;

  /* Empty string, don’t fail but do nothing */
  if (!len)
    return true;

  if (!_raqm_alloc_text(rq, len, true, false))
      return false;

  rq->text_len = _raqm_u8_to_u32 (text, len, rq->text);
  memcpy (rq->text_utf8, text, sizeof (char) * len);
  _raqm_init_text_info (rq);

  return true;
}

/**
 * raqm_set_text_utf16:
 * @rq: a #raqm_t.
 * @text: a UTF-16 encoded text string.
 * @len: the length of @text in UTF-16 shorts.
 *
 * Same as raqm_set_text(), but for text encoded in UTF-16 encoding.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.10
 */
bool
raqm_set_text_utf16 (raqm_t     *rq,
                    const uint16_t *text,
                    size_t      len)
{
  if (!rq || !text)
    return false;

  /* Call raqm_clear_contents to reuse this raqm_t */
  if (rq->text_len)
    return false;

  /* Empty string, don’t fail but do nothing */
  if (!len)
    return true;

  if (!_raqm_alloc_text(rq, len, false, true))
      return false;

  rq->text_len = _raqm_u16_to_u32 (text, len, rq->text);
  memcpy (rq->text_utf16, text, sizeof (uint16_t) * len);
  _raqm_init_text_info (rq);

  return true;
}
/**
 * raqm_set_par_direction:
 * @rq: a #raqm_t.
 * @dir: the direction of the paragraph.
 *
 * Sets the paragraph direction, also known as block direction in CSS. For
 * horizontal text, this controls the overall direction in the Unicode
 * Bidirectional Algorithm, so when the text is mainly right-to-left (with or
 * without some left-to-right) text, then the base direction should be set to
 * #RAQM_DIRECTION_RTL and vice versa.
 *
 * The default is #RAQM_DIRECTION_DEFAULT, which determines the paragraph
 * direction based on the first character with strong bidi type (see [rule
 * P2](https://unicode.org/reports/tr9/#P2) in Unicode Bidirectional Algorithm),
 * which can be good enough for many cases but has problems when a mainly
 * right-to-left paragraph starts with a left-to-right character and vice versa
 * as the detected paragraph direction will be the wrong one, or when text does
 * not contain any characters with string bidi types (e.g. only punctuation or
 * numbers) as this will default to left-to-right paragraph direction.
 *
 * For vertical, top-to-bottom text, #RAQM_DIRECTION_TTB should be used. Raqm,
 * however, provides limited vertical text support and does not handle rotated
 * horizontal text in vertical text, instead everything is treated as vertical
 * text.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_set_par_direction (raqm_t          *rq,
                        raqm_direction_t dir)
{
  if (!rq)
    return false;

  rq->base_dir = dir;

  return true;
}

/**
 * raqm_set_language:
 * @rq: a #raqm_t.
 * @lang: a BCP47 language code.
 * @start: index of first character that should use @face.
 * @len: number of characters using @face.
 *
 * Sets a [BCP47 language
 * code](https://www.w3.org/International/articles/language-tags/) to be used
 * for @len-number of characters staring at @start.  The @start and @len are
 * input string array indices (i.e. counting bytes in UTF-8 and scaler values
 * in UTF-32).
 *
 * This method can be used repeatedly to set different languages for different
 * parts of the text.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Stability:
 * Unstable
 *
 * Since: 0.2
 */
bool
raqm_set_language (raqm_t       *rq,
                   const char   *lang,
                   size_t        start,
                   size_t        len)
{
  hb_language_t language;
  size_t end;

  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  end = _raqm_encoding_to_u32_index (rq, start + len);
  start = _raqm_encoding_to_u32_index (rq, start);

  if (start >= rq->text_len || end > rq->text_len)
    return false;

  if (!rq->text_info)
    return false;

  language = hb_language_from_string (lang, -1);
  for (size_t i = start; i < end; i++)
  {
    rq->text_info[i].lang = language;
  }

  return true;
}

static bool
_raqm_add_font_feature (raqm_t       *rq,
                        hb_feature_t  fea)
{
  void* new_features;

  if (!rq)
    return false;

  new_features = realloc (rq->features,
                          sizeof (hb_feature_t) * (rq->features_len + 1));
  if (!new_features)
    return false;

  if (fea.start != HB_FEATURE_GLOBAL_START)
    fea.start = _raqm_encoding_to_u32_index (rq, fea.start);
  if (fea.end != HB_FEATURE_GLOBAL_END)
    fea.end = _raqm_encoding_to_u32_index (rq, fea.end);

  rq->features = new_features;
  rq->features[rq->features_len] = fea;
  rq->features_len++;

  return true;
}

/**
 * raqm_add_font_feature:
 * @rq: a #raqm_t.
 * @feature: (transfer none): a font feature string.
 * @len: length of @feature, -1 for `NULL`-terminated.
 *
 * Adds a font feature to be used by the #raqm_t during text layout. This is
 * usually used to turn on optional font features that are not enabled by
 * default, for example `dlig` or `ss01`, but can be also used to turn off
 * default font features.
 *
 * @feature is string representing a single font feature, in the syntax
 * understood by hb_feature_from_string().
 *
 * This function can be called repeatedly, new features will be appended to the
 * end of the features list and can potentially override previous features.
 *
 * Return value:
 * `true` if parsing @feature succeeded, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_add_font_feature (raqm_t     *rq,
                       const char *feature,
                       int         len)
{
  hb_bool_t ok;
  hb_feature_t fea;

  if (!rq)
    return false;

  ok = hb_feature_from_string (feature, len, &fea);
  if (ok)
    _raqm_add_font_feature (rq, fea);

  return ok;
}

static hb_font_t *
_raqm_create_hb_font (raqm_t *rq,
                      FT_Face face,
                      int     loadflags)
{
  hb_font_t *font = hb_ft_font_create_referenced (face);

  if (loadflags >= 0)
    hb_ft_font_set_load_flags (font, loadflags);

  return font;
}

static bool
_raqm_set_freetype_face (raqm_t *rq,
                         FT_Face face,
                         size_t  start,
                         size_t  end)
{
  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  if (start >= rq->text_len || end > rq->text_len)
    return false;

  if (!rq->text_info)
    return false;

  for (size_t i = start; i < end; i++)
  {
    if (rq->text_info[i].ftface)
        FT_Done_Face (rq->text_info[i].ftface);
    rq->text_info[i].ftface = face;
    FT_Reference_Face (face);
  }

  return true;
}

/**
 * raqm_set_freetype_face:
 * @rq: a #raqm_t.
 * @face: an #FT_Face.
 *
 * Sets an #FT_Face to be used for all characters in @rq.
 *
 * See also raqm_set_freetype_face_range().
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_set_freetype_face (raqm_t *rq,
                        FT_Face face)
{
  return _raqm_set_freetype_face (rq, face, 0, rq->text_len);
}

/**
 * raqm_set_freetype_face_range:
 * @rq: a #raqm_t.
 * @face: an #FT_Face.
 * @start: index of first character that should use @face from the input string.
 * @len: number of elements using @face.
 *
 * Sets an #FT_Face to be used for @len-number of characters staring at @start.
 * The @start and @len are input string array indices, counting elements
 * according to the underlying encoding. @start must always be aligned to the
 * start of an encoded codepoint, and @len must always end at a codepoint's
 * final element.
 *
 * This method can be used repeatedly to set different faces for different
 * parts of the text. It is the responsibility of the client to make sure that
 * face ranges cover the whole text, and is properly aligned.
 *
 * See also raqm_set_freetype_face().
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_set_freetype_face_range (raqm_t *rq,
                              FT_Face face,
                              size_t  start,
                              size_t  len)
{
  size_t end;

  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  end = _raqm_encoding_to_u32_index (rq, start + len);
  start = _raqm_encoding_to_u32_index (rq, start);

  return _raqm_set_freetype_face (rq, face, start, end);
}

static bool
_raqm_set_freetype_load_flags (raqm_t *rq,
                               int     flags,
                               size_t  start,
                               size_t  end)
{
  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  if (start >= rq->text_len || end > rq->text_len)
    return false;

  if (!rq->text_info)
    return false;

  for (size_t i = start; i < end; i++)
    rq->text_info[i].ftloadflags = flags;

  return true;
}

/**
 * raqm_set_freetype_load_flags:
 * @rq: a #raqm_t.
 * @flags: FreeType load flags.
 *
 * Sets the load flags passed to FreeType when loading glyphs, should be the
 * same flags used by the client when rendering FreeType glyphs.
 *
 * This requires version of HarfBuzz that has hb_ft_font_set_load_flags(), for
 * older version the flags will be ignored.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.3
 */
bool
raqm_set_freetype_load_flags (raqm_t *rq,
                              int     flags)
{
  return _raqm_set_freetype_load_flags(rq, flags, 0, rq->text_len);
}

/**
 * raqm_set_freetype_load_flags_range:
 * @rq: a #raqm_t.
 * @flags: FreeType load flags.
 * @start: index of first character that should use @flags.
 * @len: number of characters using @flags.
 *
 * Sets the load flags passed to FreeType when loading glyphs for @len-number
 * of characters staring at @start. Flags should be the same as used by the
 * client when rendering corresponding FreeType glyphs. The @start and @len
 * are input string array indices (i.e. counting bytes in UTF-8 and scaler
 * values in UTF-32).
 *
 * This method can be used repeatedly to set different flags for different
 * parts of the text. It is the responsibility of the client to make sure that
 * flag ranges cover the whole text.
 *
 * This requires version of HarfBuzz that has hb_ft_font_set_load_flags(), for
 * older version the flags will be ignored.
 *
 * See also raqm_set_freetype_load_flags().
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.9
 */
bool
raqm_set_freetype_load_flags_range (raqm_t *rq,
                                    int     flags,
                                    size_t  start,
                                    size_t  len)
{
  size_t end;

  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  end = _raqm_encoding_to_u32_index (rq, start + len);
  start = _raqm_encoding_to_u32_index (rq, start);

  return _raqm_set_freetype_load_flags (rq, flags, start, end);
}

static bool
_raqm_set_spacing (raqm_t *rq,
                   int    spacing,
                   bool   word_spacing,
                   size_t start,
                   size_t end)
{
  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  if (start >= rq->text_len || end > rq->text_len)
    return false;

  if (!rq->text_info)
    return false;

  for (size_t i = start; i < end; i++)
  {
    bool set_spacing = i == 0;
    if (!set_spacing)
      set_spacing = _raqm_allowed_grapheme_boundary (rq->text[i-1], rq->text[i]);

    if (set_spacing)
    {
      if (word_spacing)
      {
        if (_raqm_allowed_grapheme_boundary (rq->text[i], rq->text[i+1]))
        {
          /* CSS word seperators, word spacing is only applied on these.*/
          if (rq->text[i] == 0x0020  || /* Space */
              rq->text[i] == 0x00A0  || /* No Break Space */
              rq->text[i] == 0x1361  || /* Ethiopic Word Space */
              rq->text[i] == 0x10100 || /* Aegean Word Seperator Line */
              rq->text[i] == 0x10101 || /* Aegean Word Seperator Dot */
              rq->text[i] == 0x1039F || /* Ugaric Word Divider */
              rq->text[i] == 0x1091F)   /* Phoenician Word Separator */
          {
            rq->text_info[i].spacing_after = spacing;
          }
        }
      }
      else
      {
        rq->text_info[i].spacing_after = spacing;
      }
    }
  }

  return true;
}

/**
 * raqm_set_letter_spacing_range:
 * @rq: a #raqm_t.
 * @spacing: amount of spacing in Freetype Font Units (26.6 format).
 * @start: index of first character that should use @spacing.
 * @len: number of characters using @spacing.
 *
 * Set the letter spacing or tracking for a given range, the value
 * will be added onto the advance and offset for RTL, and the advance for
 * other directions. Letter spacing will be applied between characters, so
 * the last character will not have spacing applied after it.
 * Note that not all scripts have a letter-spacing tradition,
 * for example, Arabic does not, while Devanagari does.
 *
 * This will also add “disable `liga`, `clig`, `hlig`, `dlig`, and `calt`” font
 * features to the internal features list, so call this function after setting
 * the font features for best spacing results.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.10
 */
bool
raqm_set_letter_spacing_range(raqm_t *rq,
                              int    spacing,
                              size_t start,
                              size_t len)
{
  size_t end;

  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  end = start + len - 1;

  if (spacing != 0)
  {
#define NUM_TAGS 5
    static char *tags[NUM_TAGS] = { "clig", "liga", "hlig", "dlig", "calt" };
    for (size_t i = 0; i < NUM_TAGS; i++)
    {
      hb_feature_t fea = { hb_tag_from_string(tags[i], 5), 0, start, end };
      _raqm_add_font_feature (rq, fea);
    }
#undef NUM_TAGS
  }

  start = _raqm_encoding_to_u32_index (rq, start);
  end = _raqm_encoding_to_u32_index (rq, end);

  return _raqm_set_spacing (rq, spacing, false, start, end);
}

/**
 * raqm_set_word_spacing_range:
 * @rq: a #raqm_t.
 * @spacing: amount of spacing in Freetype Font Units (26.6 format).
 * @start: index of first character that should use @spacing.
 * @len: number of characters using @spacing.
 *
 * Set the word spacing for a given range. Word spacing will only be applied to
 * 'word separator' characters, such as 'space', 'no break space' and
 * Ethiopic word separator'.
 * The value will be added onto the advance and offset for RTL, and the advance
 * for other directions.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.10
 */
bool
raqm_set_word_spacing_range(raqm_t *rq,
                            int    spacing,
                            size_t start,
                            size_t len)
{
  size_t end;

  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  end = _raqm_encoding_to_u32_index (rq, start + len);
  start = _raqm_encoding_to_u32_index (rq, start);

  return _raqm_set_spacing (rq, spacing, true, start, end);
}

/**
 * raqm_set_invisible_glyph:
 * @rq: a #raqm_t.
 * @gid: glyph id to use for invisible glyphs.
 *
 * Sets the glyph id to be used for invisible glyhphs.
 *
 * If @gid is negative, invisible glyphs will be suppressed from the output.
 *
 * If @gid is zero, invisible glyphs will be rendered as space.
 *
 * If @gid is a positive number, it will be used for invisible glyphs.
 *
 * Return value:
 * `true` if no errors happened, `false` otherwise.
 *
 * Since: 0.6
 */
bool
raqm_set_invisible_glyph (raqm_t *rq,
                          int gid)
{
  if (!rq)
    return false;

  rq->invisible_glyph = gid;
  return true;
}

static bool
_raqm_itemize (raqm_t *rq);

static bool
_raqm_shape (raqm_t *rq);

/**
 * raqm_layout:
 * @rq: a #raqm_t.
 *
 * Run the text layout process on @rq. This is the main Raqm function where the
 * Unicode Bidirectional Text algorithm will be applied to the text in @rq,
 * text shaping, and any other part of the layout process.
 *
 * Return value:
 * `true` if the layout process was successful, `false` otherwise.
 *
 * Since: 0.1
 */
bool
raqm_layout (raqm_t *rq)
{
  if (!rq)
    return false;

  if (!rq->text_len)
    return true;

  if (!rq->text_info)
    return false;

  for (size_t i = 0; i < rq->text_len; i++)
  {
      if (!rq->text_info[i].ftface)
          return false;
  }

  if (!_raqm_itemize (rq))
    return false;

  if (!_raqm_shape (rq))
    return false;

  return true;
}

static uint32_t
_raqm_u32_to_u8_index (raqm_t   *rq,
                       uint32_t  index);
static uint32_t
_raqm_u32_to_u16_index (raqm_t   *rq,
                       uint32_t  index);
/**
 * raqm_get_glyphs:
 * @rq: a #raqm_t.
 * @length: (out): output array length.
 *
 * Gets the final result of Raqm layout process, an array of #raqm_glyph_t
 * containing the glyph indices in the font, their positions and other possible
 * information.
 *
 * Return value: (transfer none):
 * An array of #raqm_glyph_t, or `NULL` in case of error. This is owned by @rq
 * and must not be freed.
 *
 * Since: 0.1
 */
raqm_glyph_t *
raqm_get_glyphs (raqm_t *rq,
                 size_t *length)
{
  size_t count = 0;

  if (!rq || !rq->runs || !length)
  {
    if (length)
      *length = 0;
    return NULL;
  }

  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
    count += hb_buffer_get_length (run->buffer);

  if (count > rq->glyphs_capacity)
  {
    void* new_mem = realloc (rq->glyphs, sizeof (raqm_glyph_t) * count);
    if (!new_mem)
    {
      *length = 0;
      return NULL;
    }

    rq->glyphs = new_mem;
    rq->glyphs_capacity = count;
  }

  *length = count;

  RAQM_TEST ("Glyph information:\n");

  count = 0;
  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
  {
    size_t len;
    hb_glyph_info_t *info;
    hb_glyph_position_t *position;

    len = hb_buffer_get_length (run->buffer);
    info = hb_buffer_get_glyph_infos (run->buffer, NULL);
    position = hb_buffer_get_glyph_positions (run->buffer, NULL);

    for (size_t i = 0; i < len; i++)
    {
      rq->glyphs[count + i].index = info[i].codepoint;
      rq->glyphs[count + i].cluster = info[i].cluster;
      rq->glyphs[count + i].x_advance = position[i].x_advance;
      rq->glyphs[count + i].y_advance = position[i].y_advance;
      rq->glyphs[count + i].x_offset = position[i].x_offset;
      rq->glyphs[count + i].y_offset = position[i].y_offset;
      rq->glyphs[count + i].ftface = rq->text_info[info[i].cluster].ftface;

      RAQM_TEST ("glyph [%d]\tx_offset: %d\ty_offset: %d\tx_advance: %d\tfont: %s\n",
          rq->glyphs[count + i].index, rq->glyphs[count + i].x_offset,
          rq->glyphs[count + i].y_offset, rq->glyphs[count + i].x_advance,
          rq->glyphs[count + i].ftface->family_name);
    }

    count += len;
  }

  if (rq->text_utf8)
  {
#ifdef RAQM_TESTING
    RAQM_TEST ("\nUTF-32 clusters:");
    for (size_t i = 0; i < count; i++)
      RAQM_TEST (" %02d", rq->glyphs[i].cluster);
    RAQM_TEST ("\n");
#endif

    for (size_t i = 0; i < count; i++)
      rq->glyphs[i].cluster = _raqm_u32_to_u8_index (rq,
                                                     rq->glyphs[i].cluster);

#ifdef RAQM_TESTING
    RAQM_TEST ("UTF-8 clusters: ");
    for (size_t i = 0; i < count; i++)
      RAQM_TEST (" %02d", rq->glyphs[i].cluster);
    RAQM_TEST ("\n");
#endif
  }
  else if (rq->text_utf16)
  {
    for (size_t i = 0; i < count; i++)
      rq->glyphs[i].cluster = _raqm_u32_to_u16_index (rq,
                                                     rq->glyphs[i].cluster);
  }
  return rq->glyphs;
}

/**
 * raqm_get_par_resolved_direction:
 * @rq: a #raqm_t.
 *
 * Gets the resolved direction of the paragraph;
 *
 * Return value:
 * The #raqm_direction_t specifying the resolved direction of text,
 * or #RAQM_DIRECTION_DEFAULT if raqm_layout() has not been called on @rq.
 *
 * Since: 0.8
 */
RAQM_API raqm_direction_t
raqm_get_par_resolved_direction (raqm_t *rq)
{
  if (!rq)
    return RAQM_DIRECTION_DEFAULT;

  return rq->resolved_dir;
}

/**
 * raqm_get_direction_at_index:
 * @rq: a #raqm_t.
 * @index: (in): character index.
 *
 * Gets the resolved direction of the character at specified index;
 *
 * Return value:
 * The #raqm_direction_t specifying the resolved direction of text at the
 * specified index, or #RAQM_DIRECTION_DEFAULT if raqm_layout() has not been
 * called on @rq.
 *
 * Since: 0.8
 */
RAQM_API raqm_direction_t
raqm_get_direction_at_index (raqm_t *rq,
                             size_t index)
{
  if (!rq)
    return RAQM_DIRECTION_DEFAULT;

  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
  {
    if (run->pos <= index && index < run->pos + run->len)
    {
      switch (run->direction)
      {
        case HB_DIRECTION_LTR:
          return RAQM_DIRECTION_LTR;
        case HB_DIRECTION_RTL:
          return RAQM_DIRECTION_RTL;
        case HB_DIRECTION_TTB:
          return RAQM_DIRECTION_TTB;
        default:
          return RAQM_DIRECTION_DEFAULT;
      }
    }
  }

  return RAQM_DIRECTION_DEFAULT;
}

static bool
_raqm_resolve_scripts (raqm_t *rq);

static hb_direction_t
_raqm_hb_dir (raqm_t *rq, _raqm_bidi_level_t level)
{
  hb_direction_t dir = HB_DIRECTION_LTR;

  if (rq->base_dir == RAQM_DIRECTION_TTB)
      dir = HB_DIRECTION_TTB;
  else if (RAQM_BIDI_LEVEL_IS_RTL(level))
      dir = HB_DIRECTION_RTL;

  return dir;
}

typedef struct
{
  size_t pos;
  size_t len;
  _raqm_bidi_level_t level;
} _raqm_bidi_run;

#ifdef RAQM_SHEENBIDI
static _raqm_bidi_run *
_raqm_bidi_itemize (raqm_t *rq, size_t *run_count)
{
  _raqm_bidi_run *runs;
  SBAlgorithmRef bidi;
  SBParagraphRef par;
  SBUInteger par_len;
  SBLineRef line;

  SBLevel base_level = SBLevelDefaultLTR;
  SBCodepointSequence input = {
     SBStringEncodingUTF32,
     (void *) rq->text,
     rq->text_len
  };

  if (rq->base_dir == RAQM_DIRECTION_RTL)
    base_level = 1;
  else if (rq->base_dir == RAQM_DIRECTION_LTR)
    base_level = 0;

  /* paragraph */
  bidi = SBAlgorithmCreate (&input);
  par = SBAlgorithmCreateParagraph (bidi, 0, INT32_MAX, base_level);
  par_len = SBParagraphGetLength (par);

  /* lines */
  line = SBParagraphCreateLine (par, 0, par_len);
  *run_count = SBLineGetRunCount (line);

  if (SBParagraphGetBaseLevel (par) == 1)
    rq->resolved_dir = RAQM_DIRECTION_RTL;
  else
    rq->resolved_dir = RAQM_DIRECTION_LTR;

  runs = malloc (sizeof (_raqm_bidi_run) * (*run_count));
  if (runs)
  {
    const SBRun *sheenbidi_runs = SBLineGetRunsPtr(line);

    for (size_t i = 0; i < (*run_count); ++i)
    {
      runs[i].pos = sheenbidi_runs[i].offset;
      runs[i].len = sheenbidi_runs[i].length;
      runs[i].level = sheenbidi_runs[i].level;
    }
  }

  SBLineRelease (line);
  SBParagraphRelease (par);
  SBAlgorithmRelease (bidi);

  return runs;
}
#else
static void
_raqm_reverse_run (_raqm_bidi_run *run, const size_t len)
{
  assert (run);

  for (size_t i = 0; i < len / 2; i++)
  {
    _raqm_bidi_run temp = run[i];
    run[i] = run[len - 1 - i];
    run[len - 1 - i] = temp;
  }
}

static _raqm_bidi_run *
_raqm_reorder_runs (const FriBidiCharType *types,
                    const size_t len,
                    const FriBidiParType base_dir,
                    /* input and output */
                    FriBidiLevel *levels,
                    /* output */
                    size_t *run_count)
{
  FriBidiLevel level;
  FriBidiLevel last_level = -1;
  FriBidiLevel max_level = 0;
  size_t run_start = 0;
  size_t run_index = 0;
  _raqm_bidi_run *runs = NULL;
  size_t count = 0;

  if (len == 0)
  {
    *run_count = 0;
    return NULL;
  }

  assert (types);
  assert (levels);

  /* L1. Reset the embedding levels of some chars:
     4. any sequence of white space characters at the end of the line. */
  for (int i = len - 1;
       i >= 0 && FRIBIDI_IS_EXPLICIT_OR_BN_OR_WS (types[i]); i--)
  {
    levels[i] = FRIBIDI_DIR_TO_LEVEL (base_dir);
  }

  /* Find max_level of the line.  We don't reuse the paragraph
   * max_level, both for a cleaner API, and that the line max_level
   * may be far less than paragraph max_level. */
  for (int i = len - 1; i >= 0; i--)
  {
    if (levels[i] > max_level)
       max_level = levels[i];
  }

  for (size_t i = 0; i < len; i++)
  {
    if (levels[i] != last_level)
      count++;

    last_level = levels[i];
  }

  runs = malloc (sizeof (_raqm_bidi_run) * count);

  while (run_start < len)
  {
    size_t run_end = run_start;
    while (run_end < len && levels[run_start] == levels[run_end])
    {
      run_end++;
    }

    runs[run_index].pos = run_start;
    runs[run_index].level = levels[run_start];
    runs[run_index].len = run_end - run_start;
    run_start = run_end;
    run_index++;
  }

  /* L2. Reorder. */
  for (level = max_level; level > 0; level--)
  {
    for (int i = count - 1; i >= 0; i--)
    {
      if (runs[i].level >= level)
      {
        int end = i;
        for (i--; (i >= 0 && runs[i].level >= level); i--)
            ;
        _raqm_reverse_run (runs + i + 1, end - i);
      }
    }
  }

  *run_count = count;
  return runs;
}

static _raqm_bidi_run *
_raqm_bidi_itemize (raqm_t *rq, size_t *run_count)
{
  FriBidiParType par_type = FRIBIDI_PAR_ON;
  _raqm_bidi_run *runs = NULL;

  FriBidiCharType *types;
  _raqm_bidi_level_t *levels;
  int max_level = 0;
  FriBidiBracketType *btypes;

  types = calloc (rq->text_len, sizeof (FriBidiCharType));
  btypes = calloc (rq->text_len, sizeof (FriBidiBracketType));
  levels = calloc (rq->text_len, sizeof (_raqm_bidi_level_t));

  if (!types || !levels || !btypes)
    goto done;

  if (rq->base_dir == RAQM_DIRECTION_RTL)
    par_type = FRIBIDI_PAR_RTL;
  else if (rq->base_dir == RAQM_DIRECTION_LTR)
    par_type = FRIBIDI_PAR_LTR;

  fribidi_get_bidi_types (rq->text, rq->text_len, types);
  fribidi_get_bracket_types (rq->text, rq->text_len, types, btypes);
  max_level = fribidi_get_par_embedding_levels_ex (types, btypes,
                                                   rq->text_len, &par_type,
                                                   levels);

  if (par_type == FRIBIDI_PAR_RTL)
    rq->resolved_dir = RAQM_DIRECTION_RTL;
  else
    rq->resolved_dir = RAQM_DIRECTION_LTR;

  if (max_level == 0)
    goto done;

  /* Get the number of bidi runs */
  runs = _raqm_reorder_runs (types, rq->text_len, par_type, levels, run_count);

done:
  free (types);
  free (levels);
  free (btypes);

  return runs;
}
#endif

static bool
_raqm_itemize (raqm_t *rq)
{
  _raqm_bidi_run *runs = NULL;
  raqm_run_t *last;
  size_t run_count = 0;
  bool ok = true;

#ifdef RAQM_TESTING
  static char *dir_names[] = {
    "DEFAULT",
    "RTL",
    "LTR",
    "TTB"
  };

  assert (rq->base_dir < sizeof (dir_names));
  RAQM_TEST ("Direction is: %s\n\n", dir_names[rq->base_dir]);
#endif

  if (!_raqm_resolve_scripts (rq))
  {
    ok = false;
    goto done;
  }

  if (rq->base_dir == RAQM_DIRECTION_TTB)
  {
    /* Treat every thing as LTR in vertical text */
    run_count = 1;
    rq->resolved_dir = RAQM_DIRECTION_TTB;
    runs = malloc (sizeof (_raqm_bidi_run));
    if (runs)
    {
      runs->pos = 0;
      runs->len = rq->text_len;
      runs->level = 0;
    }
  }
  else
    runs = _raqm_bidi_itemize (rq, &run_count);

  if (!runs)
  {
    ok = false;
    goto done;
  }

#ifdef RAQM_TESTING
  assert (rq->resolved_dir < sizeof (dir_names));
  if (rq->base_dir == RAQM_DIRECTION_DEFAULT)
    RAQM_TEST ("Resolved direction is: %s\n\n", dir_names[rq->resolved_dir]);
  RAQM_TEST ("Number of runs before script itemization: %zu\n\n", run_count);

  RAQM_TEST ("BiDi Runs:\n");
  for (size_t i = 0; i < run_count; i++)
  {
    RAQM_TEST ("run[%zu]:\t start: %zu\tlength: %zu\tlevel: %d\n",
               i, runs[i].pos, runs[i].len, runs[i].level);
  }
  RAQM_TEST ("\n");
#endif

  last = NULL;
  for (size_t i = 0; i < run_count; i++)
  {
    raqm_run_t *run = _raqm_alloc_run (rq);
    if (!run)
    {
      ok = false;
      goto done;
    }

    if (!rq->runs)
      rq->runs = run;

    if (last)
      last->next = run;

    run->direction = _raqm_hb_dir (rq, runs[i].level);

    if (HB_DIRECTION_IS_BACKWARD (run->direction))
    {
      run->pos = runs[i].pos + runs[i].len - 1;
      run->script = rq->text_info[run->pos].script;
      run->font = _raqm_create_hb_font (rq, rq->text_info[run->pos].ftface,
          rq->text_info[run->pos].ftloadflags);
      for (int j = runs[i].len - 1; j >= 0; j--)
      {
        _raqm_text_info info = rq->text_info[runs[i].pos + j];
        if (!_raqm_compare_text_info (rq->text_info[run->pos], info))
        {
          raqm_run_t *newrun = _raqm_alloc_run (rq);
          if (!newrun)
          {
            ok = false;
            goto done;
          }
          newrun->pos = runs[i].pos + j;
          newrun->len = 1;
          newrun->direction = _raqm_hb_dir (rq, runs[i].level);
          newrun->script = info.script;
          newrun->font = _raqm_create_hb_font (rq, info.ftface,
              info.ftloadflags);
          run->next = newrun;
          run = newrun;
        }
        else
        {
          run->len++;
          run->pos = runs[i].pos + j;
        }
      }
    }
    else
    {
      run->pos = runs[i].pos;
      run->script = rq->text_info[run->pos].script;
      run->font = _raqm_create_hb_font (rq, rq->text_info[run->pos].ftface,
          rq->text_info[run->pos].ftloadflags);
      for (size_t j = 0; j < runs[i].len; j++)
      {
        _raqm_text_info info = rq->text_info[runs[i].pos + j];
        if (!_raqm_compare_text_info (rq->text_info[run->pos], info))
        {
          raqm_run_t *newrun = _raqm_alloc_run (rq);
          if (!newrun)
          {
            ok = false;
            goto done;
          }
          newrun->pos = runs[i].pos + j;
          newrun->len = 1;
          newrun->direction = _raqm_hb_dir (rq, runs[i].level);
          newrun->script = info.script;
          newrun->font = _raqm_create_hb_font (rq, info.ftface,
              info.ftloadflags);
          run->next = newrun;
          run = newrun;
        }
        else
          run->len++;
      }
    }

    last = run;
    last->next = NULL;
  }

#ifdef RAQM_TESTING
  run_count = 0;
  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
    run_count++;
  RAQM_TEST ("Number of runs after script itemization: %zu\n\n", run_count);

  run_count = 0;
  RAQM_TEST ("Final Runs:\n");
  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
  {
    SCRIPT_TO_STRING (run->script);
    RAQM_TEST ("run[%zu]:\t start: %d\tlength: %d\tdirection: %s\tscript: %s\tfont: %s\n",
               run_count++, run->pos, run->len,
               hb_direction_to_string (run->direction), buff,
               rq->text_info[run->pos].ftface->family_name);
  }
  RAQM_TEST ("\n");
#endif

done:
  free (runs);

  return ok;
}

/* Stack to handle script detection */
typedef struct
{
  size_t       capacity;
  size_t       size;
  int         *pair_index;
  hb_script_t *script;
} _raqm_stack_t;

/* Special paired characters for script detection */
static size_t paired_len = 34;
static const uint32_t paired_chars[] =
{
  0x0028, 0x0029, /* ascii paired punctuation */
  0x003c, 0x003e,
  0x005b, 0x005d,
  0x007b, 0x007d,
  0x00ab, 0x00bb, /* guillemets */
  0x2018, 0x2019, /* general punctuation */
  0x201c, 0x201d,
  0x2039, 0x203a,
  0x3008, 0x3009, /* chinese paired punctuation */
  0x300a, 0x300b,
  0x300c, 0x300d,
  0x300e, 0x300f,
  0x3010, 0x3011,
  0x3014, 0x3015,
  0x3016, 0x3017,
  0x3018, 0x3019,
  0x301a, 0x301b
};

static void
_raqm_stack_free (_raqm_stack_t *stack)
{
  free (stack->script);
  free (stack->pair_index);
  free (stack);
}

/* Stack handling functions */
static _raqm_stack_t *
_raqm_stack_new (size_t max)
{
  _raqm_stack_t *stack;
  stack = calloc (1, sizeof (_raqm_stack_t));
  if (!stack)
    return NULL;

  stack->script = malloc (sizeof (hb_script_t) * max);
  if (!stack->script)
  {
    _raqm_stack_free (stack);
    return NULL;
  }

  stack->pair_index = malloc (sizeof (int) * max);
  if (!stack->pair_index)
  {
    _raqm_stack_free (stack);
    return NULL;
  }

  stack->size = 0;
  stack->capacity = max;

  return stack;
}

static bool
_raqm_stack_pop (_raqm_stack_t *stack)
{
  if (!stack->size)
  {
    RAQM_DBG ("Stack is Empty\n");
    return false;
  }

  stack->size--;

  return true;
}

static hb_script_t
_raqm_stack_top (_raqm_stack_t *stack)
{
  if (!stack->size)
  {
    RAQM_DBG ("Stack is Empty\n");
    return HB_SCRIPT_INVALID; /* XXX: check this */
  }

  return stack->script[stack->size];
}

static bool
_raqm_stack_push (_raqm_stack_t *stack,
                  hb_script_t    script,
                  int            pair_index)
{
  if (stack->size == stack->capacity)
  {
    RAQM_DBG ("Stack is Full\n");
    return false;
  }

  stack->size++;
  stack->script[stack->size] = script;
  stack->pair_index[stack->size] = pair_index;

  return true;
}

static int
_get_pair_index (const uint32_t ch)
{
  int lower = 0;
  int upper = paired_len - 1;

  while (lower <= upper)
  {
    int mid = (lower + upper) / 2;
    if (ch < paired_chars[mid])
      upper = mid - 1;
    else if (ch > paired_chars[mid])
      lower = mid + 1;
    else
      return mid;
  }

  return -1;
}

#define STACK_IS_EMPTY(script)     ((script)->size <= 0)
#define IS_OPEN(pair_index)        (((pair_index) & 1) == 0)

/* Resolve the script for each character in the input string, if the character
 * script is common or inherited it takes the script of the character before it
 * except paired characters which we try to make them use the same script. We
 * then split the BiDi runs, if necessary, on script boundaries.
 */
static bool
_raqm_resolve_scripts (raqm_t *rq)
{
  int last_script_index = -1;
  int last_set_index = -1;
  hb_script_t last_script = HB_SCRIPT_INVALID;
  _raqm_stack_t *stack = NULL;
  hb_unicode_funcs_t* unicode_funcs = hb_unicode_funcs_get_default ();

  for (size_t i = 0; i < rq->text_len; ++i)
    rq->text_info[i].script = hb_unicode_script (unicode_funcs, rq->text[i]);

#ifdef RAQM_TESTING
  RAQM_TEST ("Before script detection:\n");
  for (size_t i = 0; i < rq->text_len; ++i)
  {
    SCRIPT_TO_STRING (rq->text_info[i].script);
    RAQM_TEST ("script for ch[%zu]\t%s\n", i, buff);
  }
  RAQM_TEST ("\n");
#endif

  stack = _raqm_stack_new (rq->text_len);
  if (!stack)
    return false;

  for (int i = 0; i < (int) rq->text_len; i++)
  {
    if (rq->text_info[i].script == HB_SCRIPT_COMMON && last_script_index != -1)
    {
      int pair_index = _get_pair_index (rq->text[i]);
      if (pair_index >= 0)
      {
        if (IS_OPEN (pair_index))
        {
          /* is a paired character */
          rq->text_info[i].script = last_script;
          last_set_index = i;
          _raqm_stack_push (stack, rq->text_info[i].script, pair_index);
        }
        else
        {
          /* is a close paired character */
          /* find matching opening (by getting the last even index for current
           * odd index) */
          while (!STACK_IS_EMPTY (stack) &&
                 stack->pair_index[stack->size] != (pair_index & ~1))
          {
            _raqm_stack_pop (stack);
          }
          if (!STACK_IS_EMPTY (stack))
          {
            rq->text_info[i].script = _raqm_stack_top (stack);
            last_script = rq->text_info[i].script;
            last_set_index = i;
          }
          else
          {
            rq->text_info[i].script = last_script;
            last_set_index = i;
          }
        }
      }
      else
      {
        rq->text_info[i].script = last_script;
        last_set_index = i;
      }
    }
    else if (rq->text_info[i].script == HB_SCRIPT_INHERITED &&
             last_script_index != -1)
    {
      rq->text_info[i].script = last_script;
      last_set_index = i;
    }
    else
    {
      for (int j = last_set_index + 1; j < i; ++j)
        rq->text_info[j].script = rq->text_info[i].script;
      last_script = rq->text_info[i].script;
      last_script_index = i;
      last_set_index = i;
    }
  }

  /* Loop backwards and change any remaining Common or Inherit characters to
   * take the script if the next character.
   * https://github.com/HOST-Oman/libraqm/issues/95
   */
  for (int i = rq->text_len - 2; i >= 0;  --i)
  {
    if (rq->text_info[i].script == HB_SCRIPT_INHERITED ||
        rq->text_info[i].script == HB_SCRIPT_COMMON)
      rq->text_info[i].script = rq->text_info[i + 1].script;
  }

#ifdef RAQM_TESTING
  RAQM_TEST ("After script detection:\n");
  for (size_t i = 0; i < rq->text_len; ++i)
  {
    SCRIPT_TO_STRING (rq->text_info[i].script);
    RAQM_TEST ("script for ch[%zu]\t%s\n", i, buff);
  }
  RAQM_TEST ("\n");
#endif

  _raqm_stack_free (stack);

  return true;
}

static void
_raqm_ft_transform (int      *x,
                    int      *y,
                    FT_Matrix matrix)
{
  FT_Vector vector;
  vector.x = *x;
  vector.y = *y;

  FT_Vector_Transform (&vector, &matrix);

  *x = vector.x;
  *y = vector.y;
}

static bool
_raqm_shape (raqm_t *rq)
{
  hb_buffer_flags_t hb_buffer_flags = HB_BUFFER_FLAG_BOT | HB_BUFFER_FLAG_EOT;

  if (rq->invisible_glyph < 0)
    hb_buffer_flags |= HB_BUFFER_FLAG_REMOVE_DEFAULT_IGNORABLES;

  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
  {
    if (!run->buffer)
      run->buffer = hb_buffer_create ();

    hb_buffer_add_utf32 (run->buffer, rq->text, rq->text_len,
                         run->pos, run->len);
    hb_buffer_set_script (run->buffer, run->script);
    hb_buffer_set_language (run->buffer, rq->text_info[run->pos].lang);
    hb_buffer_set_direction (run->buffer, run->direction);
    hb_buffer_set_flags (run->buffer, hb_buffer_flags);

    if (rq->invisible_glyph > 0)
      hb_buffer_set_invisible_glyph (run->buffer, rq->invisible_glyph);

    hb_shape_full (run->font, run->buffer, rq->features, rq->features_len,
                   NULL);

    {
      FT_Matrix matrix;
      hb_glyph_info_t *info;
      hb_glyph_position_t *pos;
      unsigned int len;

      FT_Get_Transform (hb_ft_font_get_face (run->font), &matrix, NULL);
      pos = hb_buffer_get_glyph_positions (run->buffer, &len);
      info = hb_buffer_get_glyph_infos (run->buffer, &len);

      for (unsigned int i = 0; i < len; i++)
      {
        _raqm_ft_transform (&pos[i].x_advance, &pos[i].y_advance, matrix);
        _raqm_ft_transform (&pos[i].x_offset, &pos[i].y_offset, matrix);

        bool set_spacing = false;
        if (run->direction == HB_DIRECTION_RTL)
        {
          set_spacing = i == 0;
          if (!set_spacing)
            set_spacing = info[i].cluster != info[i-1].cluster;
        }
        else
        {
          set_spacing = i == len - 1;
          if (!set_spacing)
            set_spacing = info[i].cluster != info[i+1].cluster;
        }

        _raqm_text_info rq_info = rq->text_info[info[i].cluster];

        if (rq_info.spacing_after != 0 && set_spacing)
        {
          if (run->direction == HB_DIRECTION_TTB)
            pos[i].y_advance -= rq_info.spacing_after;
          else if (run->direction == HB_DIRECTION_RTL)
          {
            pos[i].x_advance += rq_info.spacing_after;
            pos[i].x_offset += rq_info.spacing_after;
          }
          else
            pos[i].x_advance += rq_info.spacing_after;
        }
      }
    }
  }

  return true;
}

/* Count equivalent UTF-8 bytes in codepoint */
static size_t
_raqm_count_codepoint_utf8_bytes (uint32_t chr)
{
  if (0 == ((uint32_t) 0xffffff80 & chr))
    return 1;
  else if (0 == ((uint32_t) 0xfffff800 & chr))
    return 2;
  else if (0 == ((uint32_t) 0xffff0000 & chr))
    return 3;
  else
    return 4;
}

/* Convert index from UTF-32 to UTF-8 */
static uint32_t
_raqm_u32_to_u8_index (raqm_t   *rq,
                       uint32_t  index)
{
  size_t length = 0;

  for (uint32_t i = 0; i < index; ++i)
    length += _raqm_count_codepoint_utf8_bytes (rq->text[i]);

  return length;
}

/* Convert index from UTF-8 to UTF-32 */
static size_t
_raqm_u8_to_u32_index (raqm_t   *rq,
                       size_t  index)
{
  const unsigned char *s = (const unsigned char *) rq->text_utf8;
  const unsigned char *t = s;
  size_t length = 0;

  while (((size_t) (s - t) < index) && ('\0' != *s))
  {
    if (0xf0 == (0xf8 & *s))
      s += 4;
    else if (0xe0 == (0xf0 & *s))
      s += 3;
    else if (0xc0 == (0xe0 & *s))
      s += 2;
    else
      s += 1;

    length++;
  }

  if ((size_t) (s-t) > index)
    length--;

  return length;
}

/* Count equivalent UTF-16 short in codepoint */
static size_t
_raqm_count_codepoint_utf16_short (uint32_t chr)
{
  if (chr > 0x010000)
    return 2;
  else
    return 1;
}

/* Convert index from UTF-32 to UTF-16 */
static uint32_t
_raqm_u32_to_u16_index (raqm_t   *rq,
                       uint32_t  index)
{
  size_t length = 0;

  for (uint32_t i = 0; i < index; ++i)
    length += _raqm_count_codepoint_utf16_short (rq->text[i]);

  return length;
}

/* Convert index from UTF-16 to UTF-32 */
static size_t
_raqm_u16_to_u32_index (raqm_t   *rq,
                       size_t  index)
{
  const uint16_t *s = (const uint16_t *) rq->text_utf16;
  const uint16_t *t = s;
  size_t length = 0;

  while (((size_t) (s - t) < index) && ('\0' != *s))
  {
    if (*s < 0xD800 || *s > 0xDBFF)
      s += 1;
    else
      s += 2;

    length++;
  }

  if ((size_t) (s-t) > index)
    length--;

  return length;
}

static inline size_t
_raqm_encoding_to_u32_index (raqm_t *rq,
                             size_t  index)
{
  if (rq->text_utf8)
    return _raqm_u8_to_u32_index (rq, index);
  else if (rq->text_utf16)
    return _raqm_u16_to_u32_index (rq, index);
  return index;
}

static bool
_raqm_in_hangul_syllable (hb_codepoint_t ch);

/**
 * raqm_index_to_position:
 * @rq: a #raqm_t.
 * @index: (inout): character index.
 * @x: (out): output x position.
 * @y: (out): output y position.
 *
 * Calculates the cursor position after the character at @index. If the character
 * is right-to-left, then the cursor will be at the left of it, whereas if the
 * character is left-to-right, then the cursor will be at the right of it.
 *
 * Return value:
 * `true` if the process was successful, `false` otherwise.
 *
 * Since: 0.2
 */
bool
raqm_index_to_position (raqm_t *rq,
                        size_t *index,
                        int *x,
                        int *y)
{
  /* We don't currently support multiline, so y is always 0 */
  *y = 0;
  *x = 0;

  if (rq == NULL)
    return false;

  *index = _raqm_encoding_to_u32_index (rq, *index);

  if (*index >= rq->text_len)
    return false;

  RAQM_TEST ("\n");

  while (*index < rq->text_len)
  {
    if (_raqm_allowed_grapheme_boundary (rq->text[*index], rq->text[*index + 1]))
      break;

    ++*index;
  }

  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
  {
    size_t len;
    hb_glyph_info_t *info;
    hb_glyph_position_t *position;
    len = hb_buffer_get_length (run->buffer);
    info = hb_buffer_get_glyph_infos (run->buffer, NULL);
    position = hb_buffer_get_glyph_positions (run->buffer, NULL);

    for (size_t i = 0; i < len; i++)
    {
      uint32_t curr_cluster = info[i].cluster;
      uint32_t next_cluster = curr_cluster;
      *x += position[i].x_advance;

      if (run->direction == HB_DIRECTION_LTR)
      {
        for (size_t j = i + 1; j < len && next_cluster == curr_cluster; j++)
          next_cluster = info[j].cluster;
      }
      else
      {
        for (int j = i - 1; i != 0 && j >= 0 && next_cluster == curr_cluster;
             j--)
          next_cluster = info[j].cluster;
      }

      if (next_cluster == curr_cluster)
        next_cluster = run->pos + run->len;

      if (*index < next_cluster && *index >= curr_cluster)
      {
        if (run->direction == HB_DIRECTION_RTL)
          *x -= position[i].x_advance;
        *index = curr_cluster;
        goto found;
      }
    }
  }

found:
  if (rq->text_utf8)
    *index = _raqm_u32_to_u8_index (rq, *index);
  else if (rq->text_utf16)
    *index = _raqm_u32_to_u16_index (rq, *index);
  RAQM_TEST ("The position is %d at index %zu\n",*x ,*index);
  return true;
}

/**
 * raqm_position_to_index:
 * @rq: a #raqm_t.
 * @x: x position.
 * @y: y position.
 * @index: (out): output character index.
 *
 * Returns the @index of the character at @x and @y position within text.
 * If the position is outside the text, the last character is chosen as
 * @index.
 *
 * Return value:
 * `true` if the process was successful, `false` in case of error.
 *
 * Since: 0.2
 */
bool
raqm_position_to_index (raqm_t *rq,
                        int x,
                        int y,
                        size_t *index)
{
  int delta_x = 0, current_x = 0;
  (void)y;

  if (rq == NULL)
    return false;

  if (x < 0) /* Get leftmost index */
  {
    if (rq->resolved_dir == RAQM_DIRECTION_RTL)
      *index = rq->text_len;
    else
      *index = 0;
    return true;
  }

  RAQM_TEST ("\n");

  for (raqm_run_t *run = rq->runs; run != NULL; run = run->next)
  {
    size_t len;
    hb_glyph_info_t *info;
    hb_glyph_position_t *position;
    len = hb_buffer_get_length (run->buffer);
    info = hb_buffer_get_glyph_infos (run->buffer, NULL);
    position = hb_buffer_get_glyph_positions (run->buffer, NULL);

    for (size_t i = 0; i < len; i++)
    {
      delta_x = position[i].x_advance;
      if (x < (current_x + delta_x))
      {
        bool before = false;
        if (run->direction == HB_DIRECTION_LTR)
          before = (x < current_x + (delta_x / 2));
        else
          before = (x > current_x + (delta_x / 2));

        if (before)
          *index = info[i].cluster;
        else
        {
          uint32_t curr_cluster = info[i].cluster;
          uint32_t next_cluster = curr_cluster;
          if (run->direction == HB_DIRECTION_LTR)
            for (size_t j = i + 1; j < len && next_cluster == curr_cluster; j++)
              next_cluster = info[j].cluster;
          else
          for (int j = i - 1; i != 0 && j >= 0 && next_cluster == curr_cluster;
                 j--)
              next_cluster = info[j].cluster;

          if (next_cluster == curr_cluster)
            next_cluster = run->pos + run->len;

          *index = next_cluster;
        }
        if (_raqm_allowed_grapheme_boundary (rq->text[*index],rq->text[*index + 1]))
        {
          RAQM_TEST ("The start-index is %zu  at position %d \n", *index, x);
            return true;
        }

        while (*index < (unsigned)run->pos + run->len)
        {
          if (_raqm_allowed_grapheme_boundary (rq->text[*index],
                                               rq->text[*index + 1]))
          {
            *index += 1;
            break;
          }
          *index += 1;
        }
        RAQM_TEST ("The start-index is %zu  at position %d \n", *index, x);
        return true;
      }
      else
        current_x += delta_x;
    }
  }

  /* Get rightmost index*/
  if (rq->resolved_dir == RAQM_DIRECTION_RTL)
    *index = 0;
  else
    *index = rq->text_len;

  RAQM_TEST ("The start-index is %zu  at position %d \n", *index, x);

  return true;
}

typedef enum
{
  RAQM_GRAPHEM_CR,
  RAQM_GRAPHEM_LF,
  RAQM_GRAPHEM_CONTROL,
  RAQM_GRAPHEM_EXTEND,
  RAQM_GRAPHEM_REGIONAL_INDICATOR,
  RAQM_GRAPHEM_PREPEND,
  RAQM_GRAPHEM_SPACING_MARK,
  RAQM_GRAPHEM_HANGUL_SYLLABLE,
  RAQM_GRAPHEM_OTHER
} _raqm_grapheme_t;

static _raqm_grapheme_t
_raqm_get_grapheme_break (hb_codepoint_t ch,
                          hb_unicode_general_category_t category);

static bool
_raqm_allowed_grapheme_boundary (hb_codepoint_t l_char,
                                 hb_codepoint_t r_char)
{
  hb_unicode_general_category_t l_category;
  hb_unicode_general_category_t r_category;
  _raqm_grapheme_t l_grapheme, r_grapheme;
  hb_unicode_funcs_t* unicode_funcs = hb_unicode_funcs_get_default ();

  l_category = hb_unicode_general_category (unicode_funcs, l_char);
  r_category = hb_unicode_general_category (unicode_funcs, r_char);
  l_grapheme = _raqm_get_grapheme_break (l_char, l_category);
  r_grapheme = _raqm_get_grapheme_break (r_char, r_category);

  if (l_grapheme == RAQM_GRAPHEM_CR && r_grapheme == RAQM_GRAPHEM_LF)
    return false; /*Do not break between a CR and LF GB3*/
  if (l_grapheme == RAQM_GRAPHEM_CONTROL || l_grapheme == RAQM_GRAPHEM_CR ||
      l_grapheme == RAQM_GRAPHEM_LF || r_grapheme == RAQM_GRAPHEM_CONTROL ||
      r_grapheme == RAQM_GRAPHEM_CR || r_grapheme == RAQM_GRAPHEM_LF)
    return true; /*Break before and after CONTROL GB4, GB5*/
  if (r_grapheme == RAQM_GRAPHEM_HANGUL_SYLLABLE)
    return false; /*Do not break Hangul syllable sequences. GB6, GB7, GB8*/
  if (l_grapheme == RAQM_GRAPHEM_REGIONAL_INDICATOR &&
      r_grapheme == RAQM_GRAPHEM_REGIONAL_INDICATOR)
    return false; /*Do not break between regional indicator symbols. GB8a*/
  if (r_grapheme == RAQM_GRAPHEM_EXTEND)
    return false; /*Do not break before extending characters. GB9*/
  /*Do not break before SpacingMarks, or after Prepend characters.GB9a, GB9b*/
  if (l_grapheme == RAQM_GRAPHEM_PREPEND)
    return false;
  if (r_grapheme == RAQM_GRAPHEM_SPACING_MARK)
    return false;
  return true; /*Otherwise, break everywhere. GB1, GB2, GB10*/
}

static _raqm_grapheme_t
_raqm_get_grapheme_break (hb_codepoint_t ch,
                          hb_unicode_general_category_t category)
{
  _raqm_grapheme_t gb_type;

  gb_type = RAQM_GRAPHEM_OTHER;
  switch ((int)category)
  {
    case HB_UNICODE_GENERAL_CATEGORY_FORMAT:
      if (ch == 0x200C || ch == 0x200D)
        gb_type = RAQM_GRAPHEM_EXTEND;
      else
        gb_type = RAQM_GRAPHEM_CONTROL;
      break;

    case HB_UNICODE_GENERAL_CATEGORY_CONTROL:
      if (ch == 0x000D)
        gb_type = RAQM_GRAPHEM_CR;
      else if (ch == 0x000A)
        gb_type = RAQM_GRAPHEM_LF;
      else
        gb_type = RAQM_GRAPHEM_CONTROL;
      break;

    case HB_UNICODE_GENERAL_CATEGORY_SURROGATE:
    case HB_UNICODE_GENERAL_CATEGORY_LINE_SEPARATOR:
    case HB_UNICODE_GENERAL_CATEGORY_PARAGRAPH_SEPARATOR:
    case HB_UNICODE_GENERAL_CATEGORY_UNASSIGNED:
      if ((ch >= 0xFFF0 && ch <= 0xFFF8) ||
          (ch >= 0xE0000 && ch <= 0xE0FFF))
        gb_type = RAQM_GRAPHEM_CONTROL;
      break;

    case HB_UNICODE_GENERAL_CATEGORY_NON_SPACING_MARK:
    case HB_UNICODE_GENERAL_CATEGORY_ENCLOSING_MARK:
    case HB_UNICODE_GENERAL_CATEGORY_SPACING_MARK:
      if (ch != 0x102B && ch != 0x102C && ch != 0x1038 &&
          (ch < 0x1062 || ch > 0x1064) && (ch < 0x1067 || ch > 0x106D) &&
          ch != 0x1083 && (ch < 0x1087 || ch > 0x108C) && ch != 0x108F &&
          (ch < 0x109A || ch > 0x109C) && ch != 0x1A61 && ch != 0x1A63 &&
          ch != 0x1A64 && ch != 0xAA7B && ch != 0xAA70 && ch != 0x11720 &&
          ch != 0x11721) /**/
        gb_type = RAQM_GRAPHEM_SPACING_MARK;

      else if (ch == 0x09BE || ch == 0x09D7 ||
          ch == 0x0B3E || ch == 0x0B57 || ch == 0x0BBE || ch == 0x0BD7 ||
          ch == 0x0CC2 || ch == 0x0CD5 || ch == 0x0CD6 ||
          ch == 0x0D3E || ch == 0x0D57 || ch == 0x0DCF || ch == 0x0DDF ||
          ch == 0x1D165 || (ch >= 0x1D16E && ch <= 0x1D172))
        gb_type = RAQM_GRAPHEM_EXTEND;
      break;

    case HB_UNICODE_GENERAL_CATEGORY_OTHER_LETTER:
      if (ch == 0x0E33 || ch == 0x0EB3)
        gb_type = RAQM_GRAPHEM_SPACING_MARK;
      break;

    case HB_UNICODE_GENERAL_CATEGORY_OTHER_SYMBOL:
      if (ch >= 0x1F1E6 && ch <= 0x1F1FF)
        gb_type = RAQM_GRAPHEM_REGIONAL_INDICATOR;
      break;

    default:
      gb_type = RAQM_GRAPHEM_OTHER;
      break;
  }

  if (_raqm_in_hangul_syllable (ch))
    gb_type = RAQM_GRAPHEM_HANGUL_SYLLABLE;

  return gb_type;
}

static bool
_raqm_in_hangul_syllable (hb_codepoint_t ch)
{
  (void)ch;
  return false;
}

/**
 * raqm_version:
 * @major: (out): Library major version component.
 * @minor: (out): Library minor version component.
 * @micro: (out): Library micro version component.
 *
 * Returns library version as three integer components.
 *
 * Since: 0.7
 **/
void
raqm_version (unsigned int *major,
              unsigned int *minor,
              unsigned int *micro)
{
  *major = RAQM_VERSION_MAJOR;
  *minor = RAQM_VERSION_MINOR;
  *micro = RAQM_VERSION_MICRO;
}

/**
 * raqm_version_string:
 *
 * Returns library version as a string with three components.
 *
 * Return value: library version string.
 *
 * Since: 0.7
 **/
const char *
raqm_version_string (void)
{
  return RAQM_VERSION_STRING;
}

/**
 * raqm_version_atleast:
 * @major: Library major version component.
 * @minor: Library minor version component.
 * @micro: Library micro version component.
 *
 * Checks if library version is less than or equal the specified version.
 *
 * Return value:
 * `true` if library version is less than or equal the specified version,
 * `false` otherwise.
 *
 * Since: 0.7
 **/
bool
raqm_version_atleast (unsigned int major,
                      unsigned int minor,
                      unsigned int micro)
{
  return RAQM_VERSION_ATLEAST (major, minor, micro);
}

/**
 * RAQM_VERSION_ATLEAST:
 * @major: Library major version component.
 * @minor: Library minor version component.
 * @micro: Library micro version component.
 *
 * Checks if library version is less than or equal the specified version.
 *
 * Return value:
 * `true` if library version is less than or equal the specified version,
 * `false` otherwise.
 *
 * Since: 0.7
 **/

/**
 * RAQM_VERSION_STRING:
 *
 * Library version as a string with three components.
 *
 * Since: 0.7
 **/

/**
 * RAQM_VERSION_MAJOR:
 *
 * Library major version component.
 *
 * Since: 0.7
 **/

/**
 * RAQM_VERSION_MINOR:
 *
 * Library minor version component.
 *
 * Since: 0.7
 **/

/**
 * RAQM_VERSION_MICRO:
 *
 * Library micro version component.
 *
 * Since: 0.7
 **/
