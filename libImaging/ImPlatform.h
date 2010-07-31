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

#if defined(_MSC_VER)
#ifndef WIN32
#define WIN32
#endif
/* VC++ 4.0 is a bit annoying when it comes to precision issues (like
   claiming that "float a = 0.0;" would lead to loss of precision).  I
   don't like to see warnings from my code, but since I still want to
   keep it readable, I simply switch off a few warnings instead of adding
   the tons of casts that VC++ seem to require.  This code is compiled
   with numerous other compilers as well, so any real errors are likely
   to be catched anyway. */
#pragma warning(disable: 4244) /* conversion from 'float' to 'int' */
#endif

#if defined(_MSC_VER)
#define inline __inline
#elif !defined(USE_INLINE)
#define inline
#endif

#if SIZEOF_SHORT == 2
#define	INT16 short
#elif SIZEOF_INT == 2
#define	INT16 int
#else
#define	INT16 short /* most things works just fine anyway... */
#endif

#if SIZEOF_SHORT == 4
#define	INT32 short
#elif SIZEOF_INT == 4
#define	INT32 int
#elif SIZEOF_LONG == 4
#define	INT32 long
#else
#error Cannot find required 32-bit integer type
#endif

#if SIZEOF_LONG == 8
#define	INT64 long
#elif SIZEOF_LONG_LONG == 8
#define	INT64 long
#endif

/* assume IEEE; tweak if necessary (patches are welcome) */
#define	FLOAT32 float
#define	FLOAT64 double

#define	INT8  signed char
#define	UINT8 unsigned char

#define	UINT16 unsigned INT16
#define	UINT32 unsigned INT32
