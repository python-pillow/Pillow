/*
 * The Python Imaging Library
 * $Id$
 *
 * image quantizer
 *
 * Written by Toby J Sargeant <tjs@longford.cs.monash.edu.au>.
 *
 * See the README file for information on usage and redistribution.
 */

#ifndef __TYPES_H__
#define __TYPES_H__

#ifdef _MSC_VER
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
#else
#include <stdint.h>
#endif

typedef union {
   struct {
      unsigned char r,g,b,a;
   } c;
   struct {
      unsigned char v[4];
   } a;
   uint32_t v;
} Pixel;

#endif
