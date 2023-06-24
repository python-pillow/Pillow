/*
 * The Python Imaging Library
 * $Id$
 *
 * platform declarations for the imaging core library
 *
 * Copyright (c) Fredrik Lundh 1995-2003.
 */

#include "Python.h"

/* Check that we have an ANSI compliant compiler */
#ifndef HAVE_PROTOTYPES
#error Sorry, this library requires support for ANSI prototypes.
#endif
#ifndef STDC_HEADERS
#error Sorry, this library requires ANSI header files.
#endif

#if defined(PIL_NO_INLINE)
#define inline
#else
#if defined(_MSC_VER) && !defined(__GNUC__)
#define inline __inline
#endif
#endif

#if defined(_WIN32) || defined(__CYGWIN__) /* WIN */

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

#ifdef __CYGWIN__
#undef _WIN64
#undef _WIN32
#undef __WIN32__
#undef WIN32
#endif

#else /* not WIN */
/* For System that are not Windows, we'll need to define these. */
/* We have to define them instead of using typedef because the JPEG lib also
   defines their own types with the same names, so we need to be able to undef
   ours before including the JPEG code. */

#if __STDC_VERSION__ >= 199901L /* C99+ */

#include <stdint.h>

#define INT8 int8_t
#define UINT8 uint8_t
#define INT16 int16_t
#define UINT16 uint16_t
#define INT32 int32_t
#define UINT32 uint32_t

#else /* < C99 */

#define INT8 signed char

#if SIZEOF_SHORT == 2
#define INT16 short
#elif SIZEOF_INT == 2
#define INT16 int
#else
#error Cannot find required 16-bit integer type
#endif

#if SIZEOF_SHORT == 4
#define INT32 short
#elif SIZEOF_INT == 4
#define INT32 int
#elif SIZEOF_LONG == 4
#define INT32 long
#else
#error Cannot find required 32-bit integer type
#endif

#define UINT8 unsigned char
#define UINT16 unsigned INT16
#define UINT32 unsigned INT32

#endif /* < C99 */

#endif /* not WIN */

/* assume IEEE; tweak if necessary (patches are welcome) */
#define FLOAT16 UINT16
#define FLOAT32 float
#define FLOAT64 double

#ifdef _MSC_VER
typedef signed __int64 int64_t;
#endif

#ifdef __GNUC__
#define GCC_VERSION (__GNUC__ * 10000 + __GNUC_MINOR__ * 100 + __GNUC_PATCHLEVEL__)
#endif
