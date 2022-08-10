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

rgba decode_565(UINT16 x);