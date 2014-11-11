/*
 * The Python Imaging Library
 * $Id$
 *
 * declarations for the OpenJPEG codec interface.
 *
 * Copyright (c) 2014 by Coriolis Systems Limited
 * Copyright (c) 2014 by Alastair Houghton
 */

#include <openjpeg.h>

/* -------------------------------------------------------------------- */
/* Decoder								*/
/* -------------------------------------------------------------------- */

typedef struct {
    /* CONFIGURATION */

    /* File descriptor, if available; otherwise, -1 */
    int fd;

    /* Length of data, if available; otherwise, -1 */
    off_t length;

    /* Specify the desired format */
    OPJ_CODEC_FORMAT format;

    /* Set to divide image resolution by 2**reduce. */
    int            reduce;

    /* Set to limit the number of quality layers to decode (0 = all layers) */
    int            layers;

    /* PRIVATE CONTEXT (set by decoder) */
    const char    *error_msg;

    ImagingIncrementalCodec decoder;
} JPEG2KDECODESTATE;

/* -------------------------------------------------------------------- */
/* Encoder								*/
/* -------------------------------------------------------------------- */

typedef struct {
    /* CONFIGURATION */

    /* File descriptor, if available; otherwise, -1 */
    int           fd;

    /* Specify the desired format */
    OPJ_CODEC_FORMAT format;

    /* Image offset */
    int            offset_x, offset_y;

    /* Tile information */
    int            tile_offset_x, tile_offset_y;
    int            tile_size_x, tile_size_y;

    /* Quality layers (a sequence of numbers giving *either* rates or dB) */
    int            quality_is_in_db;
    PyObject      *quality_layers;

    /* Number of resolutions (DWT decompositions + 1 */
    int            num_resolutions;

    /* Code block size */
    int            cblk_width, cblk_height;

    /* Precinct size */
    int            precinct_width, precinct_height;

    /* Compression style */
    int            irreversible;

    /* Progression order (LRCP/RLCP/RPCL/PCRL/CPRL) */
    OPJ_PROG_ORDER progression;

    /* Cinema mode */
    OPJ_CINEMA_MODE cinema_mode;

    /* PRIVATE CONTEXT (set by decoder) */
    const char    *error_msg;

    ImagingIncrementalCodec encoder;
} JPEG2KENCODESTATE;

/*
 * Local Variables:
 * c-basic-offset: 4
 * End:
 *
 */
