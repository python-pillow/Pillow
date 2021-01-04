/* Sgi.h */

typedef struct {
    /* CONFIGURATION */

    /* Number of bytes per channel per pixel */
    int bpc;

    /* RLE offsets table */
    UINT32 *starttab;

    /* RLE lengths table */
    UINT32 *lengthtab;

    /* current row offset */
    UINT32 rleoffset;

    /* current row length */
    UINT32 rlelength;

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