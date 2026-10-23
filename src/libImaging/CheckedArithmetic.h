/*
 * The Python Imaging Library
 *
 * checked arithmetic for sizes
 *
 * See the README file for information on usage and redistribution.
 */

#ifndef __CHECKED_ARITHMETIC_H__
#define __CHECKED_ARITHMETIC_H__

#include <stddef.h>
#include <stdint.h>

/* Helpers to compute sizes, such as the number of bytes to allocate, without
   overflowing. Each one stores the result in *result and returns 1, or returns
   0 and leaves *result unchanged if the result does not fit in a size_t. */

#if defined(__has_builtin)
#if __has_builtin(__builtin_add_overflow) && __has_builtin(__builtin_mul_overflow)
#define IMAGING_HAVE_OVERFLOW_BUILTINS
#endif
#elif defined(__GNUC__) && __GNUC__ >= 5
#define IMAGING_HAVE_OVERFLOW_BUILTINS
#endif

static inline int
ImagingCheckedAdd(size_t a, size_t b, size_t *result) {
#ifdef IMAGING_HAVE_OVERFLOW_BUILTINS
    size_t r;
    if (__builtin_add_overflow(a, b, &r)) {
        return 0;
    }
    *result = r;
#else
    if (a > SIZE_MAX - b) {
        return 0;
    }
    *result = a + b;
#endif
    return 1;
}

static inline int
ImagingCheckedMul(size_t a, size_t b, size_t *result) {
#ifdef IMAGING_HAVE_OVERFLOW_BUILTINS
    size_t r;
    if (__builtin_mul_overflow(a, b, &r)) {
        return 0;
    }
    *result = r;
#else
    if (b != 0 && a > SIZE_MAX / b) {
        return 0;
    }
    *result = a * b;
#endif
    return 1;
}

#endif
