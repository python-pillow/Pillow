/*
 * The Python Imaging Library
 * $Id$
 *
 * platform declarations for the imaging core library
 *
 * Copyright (c) Fredrik Lundh 1995-2003.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define _USE_MATH_DEFINES
#include <math.h>

/* Check that we have an ANSI compliant compiler */
#ifndef HAVE_PROTOTYPES
#error Sorry, this library requires support for ANSI prototypes.
#endif
#ifndef STDC_HEADERS
#error Sorry, this library requires ANSI header files.
#endif

#if defined(_MSC_VER) && !defined(__GNUC__)
#define inline __inline
#endif

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#ifdef _WIN64
#define F_HANDLE "K"
#else
#define F_HANDLE "k"
#endif
#endif /* _WIN32 */

#include <stdint.h>

/* We have to define types instead of using typedef because the JPEG lib also
   defines their own types with the same names, so we need to be able to undef
   ours before including the JPEG code. */
#define INT8 int8_t
#define UINT8 uint8_t
#define INT16 int16_t
#define UINT16 uint16_t
#define INT32 int32_t
#define UINT32 uint32_t

/* assume IEEE; tweak if necessary (patches are welcome) */
#define FLOAT16 UINT16
#define FLOAT32 float
#define FLOAT64 double

#ifdef __GNUC__
#define GCC_VERSION (__GNUC__ * 10000 + __GNUC_MINOR__ * 100 + __GNUC_PATCHLEVEL__)
#endif
