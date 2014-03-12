/*
 * The Python Imaging Library
 * $Id$
 *
 * declarations for the OpenJPEG codec interface.
 *
 * Copyright (c) 2014 by Coriolis Systems Limited
 * Copyright (c) 2014 by Alastair Houghton
 */

#include <openjpeg-2.0/openjpeg.h>

/* -------------------------------------------------------------------- */
/* Decoder								*/

typedef struct {
    /* CONFIGURATION */

    /* Output mode */
    char           mode[8];

    /* Specify the desired format */
    OPJ_CODEC_FORMAT format;

    /* Set to divide image resolution by 2**reduce. */
    int            reduce;

    /* Set to limit the number of quality layers to decode (0 = all layers) */
    int            layers;

    /* PRIVATE CONTEXT (set by decoder) */
    const char    *error_msg;

    ImagingIncrementalDecoder decoder;

    opj_stream_t  *stream;
} JPEG2KSTATE;

/*
 * Local Variables:
 * c-basic-offset: 4
 * End:
 *
 */
