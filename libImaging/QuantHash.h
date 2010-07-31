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

#ifndef __HASH_H__
#define __HASH_H__

#include "QuantTypes.h"

HashTable hashtable_new(HashFunc,HashCmpFunc);
void hashtable_free(HashTable);
void hashtable_foreach(HashTable,IteratorFunc,void *);
void hashtable_foreach_update(HashTable,IteratorUpdateFunc,void *);
int hashtable_insert(HashTable,void *,void *);
int hashtable_update(HashTable,void *,void *);
int hashtable_lookup(const HashTable,const void *,void **);
int hashtable_lookup_or_insert(HashTable,void *,void **,void *);
int hashtable_insert_or_update_computed(HashTable,void *,ComputeFunc,ComputeFunc);
int hashtable_delete(HashTable,const void *);
int hashtable_remove(HashTable,const void *,void **,void **);
void *hashtable_set_user_data(HashTable,void *);
void *hashtable_get_user_data(const HashTable);
DestroyFunc hashtable_set_key_destroy_func(HashTable,DestroyFunc);
DestroyFunc hashtable_set_value_destroy_func(HashTable,DestroyFunc);
unsigned long hashtable_get_count(const HashTable);
void hashtable_rehash(HashTable);
void hashtable_rehash_compute(HashTable,CollisionFunc);

#endif
