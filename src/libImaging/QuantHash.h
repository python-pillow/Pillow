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

#ifndef __QUANTHASH_H__
#define __QUANTHASH_H__

#include "QuantTypes.h"

typedef struct _HashTable HashTable;
typedef Pixel HashKey_t;
typedef uint32_t HashVal_t;

typedef uint32_t (*HashFunc)(const HashTable *,const HashKey_t);
typedef int (*HashCmpFunc)(const HashTable *,const HashKey_t,const HashKey_t);
typedef void (*IteratorFunc)(const HashTable *,const HashKey_t,const HashVal_t,void *);
typedef void (*IteratorUpdateFunc)(const HashTable *,const HashKey_t,HashVal_t *,void *);
typedef void (*ComputeFunc)(const HashTable *,const HashKey_t,HashVal_t *);
typedef void (*CollisionFunc)(const HashTable *,HashKey_t *,HashVal_t *,HashKey_t,HashVal_t);

HashTable * hashtable_new(HashFunc hf,HashCmpFunc cf);
void hashtable_free(HashTable *h);
void hashtable_foreach(HashTable *h,IteratorFunc i,void *u);
void hashtable_foreach_update(HashTable *h,IteratorUpdateFunc i,void *u);
int hashtable_insert(HashTable *h,HashKey_t key,HashVal_t val);
int hashtable_lookup(const HashTable *h,const HashKey_t key,HashVal_t *valp);
int hashtable_insert_or_update_computed(HashTable *h,HashKey_t key,ComputeFunc newFunc,ComputeFunc existsFunc);
void *hashtable_set_user_data(HashTable *h,void *data);
void *hashtable_get_user_data(const HashTable *h);
uint32_t hashtable_get_count(const HashTable *h);
void hashtable_rehash_compute(HashTable *h,CollisionFunc cf);

#endif // __QUANTHASH_H__
