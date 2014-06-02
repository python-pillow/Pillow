/*
 * The Python Imaging Library.
 * $Id$
 *
 * declarations for the TIFF LZW decoder.
 *
 * Copyright (c) Fredrik Lundh 1995-96.
 */


/* Max size for LZW code words */

#define	LZWBITS	    12

#define	LZWTABLE    (1<<LZWBITS)
#define	LZWBUFFER   (1<<LZWBITS)


typedef struct {

    /* CONFIGURATION */

    /* Filter type */
    int filter;

    /* PRIVATE CONTEXT (set by decoder) */

    /* Input bit buffer */
    INT32 bitbuffer;
    int bitcount;

    /* Code buffer */
    int codesize;
    int codemask;

    /* Constant symbol codes */
    int clear, end;

    /* Symbol history */
    int lastcode;
    unsigned char lastdata;

    /* History buffer */
    int bufferindex;
    unsigned char buffer[LZWTABLE];

    /* Symbol table */
    UINT16 link[LZWTABLE];
    unsigned char data[LZWTABLE];
    int next;

} LZWSTATE;
