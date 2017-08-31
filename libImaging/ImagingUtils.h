#ifdef WORDS_BIGENDIAN
    #define MAKE_UINT32(u0, u1, u2, u3) (u3 | (u2<<8) | (u1<<16) | (u0<<24))
    #define MASK_UINT32_CHANNEL_0 0xff000000
    #define MASK_UINT32_CHANNEL_1 0x00ff0000
    #define MASK_UINT32_CHANNEL_2 0x0000ff00
    #define MASK_UINT32_CHANNEL_3 0x000000ff
#else
    #define MAKE_UINT32(u0, u1, u2, u3) (u0 | (u1<<8) | (u2<<16) | (u3<<24))
    #define MASK_UINT32_CHANNEL_0 0x000000ff
    #define MASK_UINT32_CHANNEL_1 0x0000ff00
    #define MASK_UINT32_CHANNEL_2 0x00ff0000
    #define MASK_UINT32_CHANNEL_3 0xff000000
#endif


#define SHIFTFORDIV255(a)\
    ((((a) >> 8) + a) >> 8)

/* like (a * b + 127) / 255), but much faster on most platforms */
#define MULDIV255(a, b, tmp)\
    (tmp = (a) * (b) + 128, SHIFTFORDIV255(tmp))

#define DIV255(a, tmp)\
    (tmp = (a) + 128, SHIFTFORDIV255(tmp))

#define BLEND(mask, in1, in2, tmp1)\
    DIV255(in1 * (255 - mask) + in2 * mask, tmp1)

#define PREBLEND(mask, in1, in2, tmp1)\
    (MULDIV255(in1, (255 - mask), tmp1) + in2)
