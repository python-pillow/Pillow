#ifdef WORDS_BIGENDIAN
#define MAKE_UINT32(u0, u1, u2, u3) \
    ((UINT32)(u3) | ((UINT32)(u2) << 8) | ((UINT32)(u1) << 16) | ((UINT32)(u0) << 24))
#define MASK_UINT32_CHANNEL_0 0xff000000
#define MASK_UINT32_CHANNEL_1 0x00ff0000
#define MASK_UINT32_CHANNEL_2 0x0000ff00
#define MASK_UINT32_CHANNEL_3 0x000000ff
#else
#define MAKE_UINT32(u0, u1, u2, u3) \
    ((UINT32)(u0) | ((UINT32)(u1) << 8) | ((UINT32)(u2) << 16) | ((UINT32)(u3) << 24))
#define MASK_UINT32_CHANNEL_0 0x000000ff
#define MASK_UINT32_CHANNEL_1 0x0000ff00
#define MASK_UINT32_CHANNEL_2 0x00ff0000
#define MASK_UINT32_CHANNEL_3 0xff000000
#endif

#define SHIFTFORDIV255(a) ((((a) >> 8) + a) >> 8)

/* like (a * b + 127) / 255), but much faster on most platforms */
#define MULDIV255(a, b, tmp) (tmp = (a) * (b) + 128, SHIFTFORDIV255(tmp))

#define DIV255(a, tmp) (tmp = (a) + 128, SHIFTFORDIV255(tmp))

#define BLEND(mask, in1, in2, tmp1) DIV255(in1 *(255 - mask) + in2 * mask, tmp1)

#define PREBLEND(mask, in1, in2, tmp1) (MULDIV255(in1, (255 - mask), tmp1) + in2)

#define CLIP8(v) ((v) <= 0 ? 0 : (v) < 256 ? (v) : 255)

/* This is to work around a bug in GCC prior 4.9 in 64 bit mode.
   GCC generates code with partial dependency which is 3 times slower.
   See: http://stackoverflow.com/a/26588074/253146 */
#if defined(__x86_64__) && defined(__SSE__) && !defined(__NO_INLINE__) && \
    !defined(__clang__) && defined(GCC_VERSION) && (GCC_VERSION < 40900)
static float __attribute__((always_inline)) inline _i2f(int v) {
    float x;
    __asm__("xorps %0, %0; cvtsi2ss %1, %0" : "=x"(x) : "r"(v));
    return x;
}
#else
static float inline _i2f(int v) { return (float)v; }
#endif
