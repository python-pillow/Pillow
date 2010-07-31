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

typedef void *HashTable;
typedef void *Heap;

typedef unsigned long (*HashFunc)(const HashTable,const void *);
typedef int (*HashCmpFunc)(const HashTable,const void *,const void *);
typedef void (*IteratorFunc)(const HashTable,const void *,const void *,void *);
typedef void (*IteratorUpdateFunc)(const HashTable,const void *,void **,void *);
typedef void (*DestroyFunc)(const HashTable,void *);
typedef void (*ComputeFunc)(const HashTable,const void *,void **);
typedef void (*CollisionFunc)(const HashTable,void **,void **,void *,void *);

typedef int (*HeapCmpFunc)(const Heap,const void *,const void *);

#endif
