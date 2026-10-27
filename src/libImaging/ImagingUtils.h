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

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#define SHIFTFORDIV255(a) ((((a) >> 8) + a) >> 8)

/* like (a * b + 127) / 255), but much faster on most platforms */
#define MULDIV255(a, b, tmp) (tmp = (a) * (b) + 128, SHIFTFORDIV255(tmp))

#define DIV255(a, tmp) (tmp = (a) + 128, SHIFTFORDIV255(tmp))

#define BLEND(mask, in1, in2, tmp1) DIV255(in1 * (255 - mask) + in2 * mask, tmp1)

#define PREBLEND(mask, in1, in2, tmp1) (MULDIV255(in1, (255 - mask), tmp1) + in2)

#define CLIP8(v) ((v) <= 0 ? 0 : (v) < 256 ? (v) : 255)

#define CLIP16(v) ((v) <= 0 ? 0 : (v) < 65536 ? (v) : 65535)

/* Overflow-checked multiplication for buffer-size calculations.
 *
 * Stores a * b in *result and returns 1 if the product overflows a
 * size_t, otherwise stores the product and returns 0.
 *
 * This replaces the open-coded "a > LIMIT / b" idiom used before
 * several allocations.  That idiom is fragile: the divisor b is often
 * itself a product (for example height * bytes_per_pixel) that can
 * overflow or be zero *before* the division runs, silently defeating
 * the check.  Multiplying in a single checked step is correct by
 * construction and easy to audit.  Callers that must fit the result in
 * a narrower type still compare *result against the relevant limit. */
static inline int
_imaging_mul_overflow(size_t a, size_t b, size_t *result) {
#if defined(__GNUC__) || defined(__clang__)
    return __builtin_mul_overflow(a, b, result);
#else
    *result = a * b;
    /* (size_t)-1 is SIZE_MAX */
    return b != 0 && a > (size_t)-1 / b;
#endif
}
