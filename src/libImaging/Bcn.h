typedef struct {
    char *pixel_format;
} BCNSTATE;

typedef struct {
    UINT8 r, g, b, a;
} rgba;

typedef struct {
    UINT8 l;
} lum;

typedef struct {
    FLOAT32 r, g, b;
} rgb32f;

typedef struct {
    UINT16 c0, c1;
    UINT32 lut;
} bc1_color;

typedef struct {
    UINT8 a0, a1;
    UINT8 lut[6];
} bc3_alpha;

typedef struct {
    INT8 a0, a1;
    UINT8 lut[6];
} bc5s_alpha;

#define BIT_MASK(bit_count) ((1 << (bit_count)) - 1)
#define SET_BITS(target, bit_offset, bit_count, value) \
    target |= (((value) & BIT_MASK(bit_count)) << (bit_offset))
#define GET_BITS(source, bit_offset, bit_count) \
    ((source) & (BIT_MASK(bit_count) << (bit_offset))) >> (bit_offset)
#define SWAP(TYPE, A, B) \
    do {                 \
        TYPE TMP = A;    \
        (A) = B;         \
        (B) = TMP;       \
    } while (0)
