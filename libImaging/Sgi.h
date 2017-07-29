/* Sgi.h */
#include <stdint.h>

typedef struct {

    /* CONFIGURATION */

    /* Number of bytes per channel per pixel */
    int bpc;

    /* RLE offsets table */
    uint32_t *starttab;

    /* RLE lengths table */
    uint32_t *lengthtab;

    /* current row offset */
    uint32_t rleoffset;

    /* current row length */
    uint32_t rlelength;

    /* RLE table size */
    int tablen;

    /* RLE table index */
    int tabindex;

    /* buffer index */
    int bufindex;

    /* current row index */
    int rowno;

    /* current channel index */
    int channo;

    /* image data size from file descriptor */
    long bufsize;

} SGISTATE;