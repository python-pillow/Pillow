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

#ifndef __QUANTTYPES_H__
#define __QUANTTYPES_H__

#include <stdint.h>

typedef union {
    struct {
        unsigned char r, g, b, a;
    } c;
    struct {
        unsigned char v[4];
    } a;
    uint32_t v;
} Pixel;

#endif
