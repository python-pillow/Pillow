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

#ifndef __QUANT_H__
#define __QUANT_H__

typedef union {
   struct {
      unsigned char r,g,b,a;
   } c;
   struct {
      unsigned char v[4];
   } a;
   unsigned long v;
} Pixel;

int quantize(Pixel *,
             unsigned long,
             unsigned long,
             Pixel **,
             unsigned long *,
             unsigned long **,
             int);

int quantize2(Pixel *,
             unsigned long,
             unsigned long,
             Pixel **,
             unsigned long *,
             unsigned long **,
             int);
#endif
