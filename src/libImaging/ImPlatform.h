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

#if defined(_WIN32) || defined(__CYGWIN__)

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

#ifdef __CYGWIN__
#undef _WIN64
#undef _WIN32
#undef __WIN32__
#undef WIN32
#endif

#else
/* For System that are not Windows, we'll need to define these. */

#if SIZEOF_SHORT == 2
#define INT16 short
#elif SIZEOF_INT == 2
#define INT16 int
#else
#define INT16 short /* most things works just fine anyway... */
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

#if SIZEOF_LONG == 8
#define INT64 long
#elif SIZEOF_LONG_LONG == 8
#define INT64 long
#endif

#define INT8 signed char
#define UINT8 unsigned char

#define UINT16 unsigned INT16
#define UINT32 unsigned INT32

#endif

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
