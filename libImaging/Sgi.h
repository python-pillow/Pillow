/* Sgi.h */

typedef struct {

    /* CONFIGURATION */

    /* Number of bytes per pixel per channel */
    int bpc;

    /* Number of UINT32 data in RLE tables */
    int tablen;

    /* Current row index */
    int rowno;

    /* Current channel index */
    int channo;

    /* Offsets table */
    uint32_t* starttab;

    /* Lengths table */
    uint32_t* lengthtab;

    /* Offsets table index */
    int starttabidx;

    /* Lengths table index */
    int lengthtabidx;

} SGISTATE;