/* Bit.h */

typedef struct {
    /* CONFIGURATION */

    /* Number of bits per pixel */
    int bits;

    /* Line padding (0 or 8) */
    int pad;

    /* Fill order */
    /* 0=msb/msb, 1=msbfill/lsbshift, 2=lsbfill/msbshift, 3=lsb/lsb */
    int fill;

    /* Signed integers (0=unsigned, 1=signed) */
    int sign;

    /* Lookup table (not implemented) */
    unsigned long lutsize;
    FLOAT32 *lut;

    /* INTERNAL */
    unsigned long mask;
    unsigned long signmask;
    unsigned long bitbuffer;
    int bitcount;

} BITSTATE;
