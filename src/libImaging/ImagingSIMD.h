/* Microsoft compiler doesn't limit intrinsics for an architecture.
   This macro is set only on x86 and means SSE2 and above including AVX2. */
#if defined(_M_X64) || _M_IX86_FP == 2
#define __SSE2__
/* However, Microsoft compiler set __AVX2__ if /arch:AVX2 option is set */
#ifdef __AVX2__
#define __SSE4_2__
#endif
#endif

/* For better readability */
#ifdef __SSE4_2__
#define __SSE4__
#endif
#ifdef __aarch64__
#define __NEON__
#endif

#ifdef __SSE2__
#include <mmintrin.h>   // MMX
#include <xmmintrin.h>  // SSE
#include <emmintrin.h>  // SSE2
#endif
#ifdef __SSE4__
#include <pmmintrin.h>  // SSE3
#include <tmmintrin.h>  // SSSE3
#include <smmintrin.h>  // SSE4.1
#include <nmmintrin.h>  // SSE4.2
#endif
#ifdef __AVX2__
#include <immintrin.h>  // AVX, AVX2
#endif
#ifdef __NEON__
#include <arm_neon.h>  // ARM NEON
#endif

#ifdef __SSE4__
static inline __m128i
mm_cvtepu8_epi32(void *ptr) {
    return _mm_cvtepu8_epi32(_mm_cvtsi32_si128(*(INT32 *)ptr));
}
#endif

#ifdef __AVX2__
static inline __m256i
mm256_cvtepu8_epi32(void *ptr) {
    return _mm256_cvtepu8_epi32(_mm_loadl_epi64((__m128i *)ptr));
}
#endif
