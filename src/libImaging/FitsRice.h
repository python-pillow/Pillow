/* State for the FITS RICE_1 integer decoder. */

typedef struct {
    int bytepix;
    int blocksize;
    int output_bytes;
    int fsbits;
    int fsmax;
    Py_ssize_t remaining;

    UINT32 mask;
    UINT32 lastpix;
    UINT32 quotient;
    UINT32 difference;
    uint64_t bitbuffer;
    int bitcount;
    int blockleft;
    int fs;
} FITSRICESTATE;
