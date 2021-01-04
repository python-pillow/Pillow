/*
 * The Python Imaging Library.
 * $Id$
 *
 * declarations for the ZIP codecs
 *
 * Copyright (c) Fredrik Lundh 1996.
 */

#include "zlib.h"

/* modes */
#define ZIP_PNG 0            /* continuous, filtered image data */
#define ZIP_PNG_PALETTE 1    /* non-continuous data, disable filtering */
#define ZIP_TIFF_PREDICTOR 2 /* TIFF, with predictor */
#define ZIP_TIFF 3           /* TIFF, without predictor */

typedef struct {
    /* CONFIGURATION */

    /* Codec mode */
    int mode;

    /* Optimize (max compression) SLOW!!! */
    int optimize;

    /* 0 no compression, 9 best compression, -1 default compression */
    int compress_level;
    /* compression strategy Z_XXX */
    int compress_type;

    /* Predefined dictionary (experimental) */
    char *dictionary;
    int dictionary_size;

    /* PRIVATE CONTEXT (set by decoder/encoder) */

    z_stream z_stream; /* (de)compression stream */

    UINT8 *previous; /* previous line (allocated) */

    int last_output; /* # bytes last output by inflate */

    /* Compressor specific stuff */
    UINT8 *prior; /* filter storage (allocated) */
    UINT8 *up;
    UINT8 *average;
    UINT8 *paeth;

    UINT8 *output; /* output data */

    int prefix; /* size of filter prefix (0 for TIFF data) */

    int interlaced; /* is the image interlaced? (PNG) */

    int pass; /* current pass of the interlaced image (PNG) */

} ZIPSTATE;
