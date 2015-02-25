/*
 * The Python Imaging Library.
 *
 * declarations for the WebP codec interface.
 */

#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>

/* -------------------------------------------------------------------- */
/* Decoder								*/

typedef struct {

    /* CONFIGURATION */

    /* Decoder output mode (input to the shuffler). */
    char rawmode[IMAGING_MODE_LENGTH];

    /* Original image information. */
    int has_alpha;
    int width, height;

    /* PRIVATE CONTEXT (set by decoder) */

    WebPDecoderConfig  config;
    WebPIDecoder      *decoder;

} WEBPSTATE;

