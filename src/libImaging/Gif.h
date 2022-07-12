/*
 * The Python Imaging Library.
 * $Id$
 *
 * Declarations for a fast, suspendable GIF decoder.
 *
 * Copyright (c) Fredrik Lundh 1995-96.
 */

/* Max size for a LZW code word. */

#define GIFBITS     12

#define GIFTABLE    (1<<GIFBITS)
#define GIFBUFFER   (1<<GIFBITS)

typedef struct {
    /* CONFIGURATION */

    /* Initial number of bits. The caller should clear all fields in
       this structure and set this field before calling the decoder
       the first time. */
    int bits;

    /* If set, this is an interlaced image.  Process it the following way:
     * 1st pass: start at top line, lines are 8 pixels high, step 8 pixels
     * 2nd pass: start at line 4, lines are 4 pixels high, step 8 pixels
     * 3rd pass: start at line 2, lines are 2 pixels high, step 4 pixels
     * 4th pass: start at line 1, lines are 1 pixels high, step 2 pixels
     */
    int interlace;

    /* The transparent palette index, or -1 for no transparency */
    int transparency;

    /* PRIVATE CONTEXT (set by decoder) */

    /* Interlace parameters */
    int step, repeat;

    /* Input bit buffer */
    INT32 bitbuffer;
    int bitcount;
    int blocksize;

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
    unsigned char buffer[GIFTABLE];

    /* Symbol table */
    UINT16 link[GIFTABLE];
    unsigned char data[GIFTABLE];
    int next;

} GIFDECODERSTATE;

/* For GIF LZW encoder. */
#define TABLE_SIZE  8192

typedef struct {
    /* CONFIGURATION */

    /* Initial number of bits. The caller should clear all fields in
       this structure and set this field before calling the encoder
       the first time. */
    int bits;

    /* NOTE: the expanding encoder ignores this field */

    /* If set, write an interlaced image (see above) */
    int interlace;

    /* PRIVATE CONTEXT (set by encoder) */

    /* Interlace parameters */
    int step;

    /* For GIF LZW encoder. */
    UINT32 put_state;
    UINT32 entry_state;
    UINT32 clear_code, end_code, next_code, max_code;
    UINT32 code_width, code_bits_left, buf_bits_left;
    UINT32 code_buffer;
    UINT32 head, tail;
    int probe;
    UINT32 code;
    UINT32 codes[TABLE_SIZE];

} GIFENCODERSTATE;
