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

#ifndef __QUANTHEAP_H__
#define __QUANTHEAP_H__

#include "QuantTypes.h"

typedef struct _Heap Heap;

typedef int (*HeapCmpFunc)(const Heap *,const void *,const void *);

void ImagingQuantHeapFree(Heap *);
int ImagingQuantHeapRemove(Heap *,void **);
int ImagingQuantHeapAdd(Heap *,void *);
int ImagingQuantHeapTop(Heap *,void **);
Heap *ImagingQuantHeapNew(HeapCmpFunc);

#endif // __QUANTHEAP_H__
