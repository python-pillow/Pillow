/*
 * The Python Imaging Library
 * $Id$
 *
 * hash tables used by the image quantizer
 *
 * history:
 * 98-09-10 tjs  Contributed
 * 98-12-29 fl   Added to PIL 1.0b1
 *
 * Written by Toby J Sargeant <tjs@longford.cs.monash.edu.au>.
 *
 * Copyright (c) 1998 by Toby J Sargeant
 * Copyright (c) 1998 by Secret Labs AB
 *
 * See the README file for information on usage and redistribution.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "QuantHash.h"
#include "QuantDefines.h"

typedef struct _IntHashNode {
   struct _IntHashNode *next;
   void *key,*value;
} IntHashNode;

typedef struct _IntHashTable {
   IntHashNode **table;
   unsigned long length;
   unsigned long count;
   HashFunc hashFunc;
   HashCmpFunc cmpFunc;
   DestroyFunc keyDestroyFunc;
   DestroyFunc valDestroyFunc;
   void *userData;
} IntHashTable;

#define MIN_LENGTH 11
#define RESIZE_FACTOR 3

static int _hashtable_insert_node(IntHashTable *,IntHashNode *,int,int,CollisionFunc);
#if 0
static int _hashtable_test(IntHashTable *);
#endif

HashTable hashtable_new(HashFunc hf,HashCmpFunc cf) {
   IntHashTable *h;
   h=malloc(sizeof(IntHashTable));
   if (!h) { return NULL; }
   h->hashFunc=hf;
   h->cmpFunc=cf;
   h->keyDestroyFunc=NULL;
   h->valDestroyFunc=NULL;
   h->length=MIN_LENGTH;
   h->count=0;
   h->userData=NULL;
   h->table=malloc(sizeof(IntHashNode *)*h->length);
   if (!h->table) { free(h); return NULL; }
   memset (h->table,0,sizeof(IntHashNode *)*h->length);
   return (HashTable)h;
}

static void _hashtable_destroy(HashTable H,const void *key,const void *val,void *u) {
   IntHashTable *h=(IntHashTable *)H;
   if (h->keyDestroyFunc&&key) {
      h->keyDestroyFunc((HashTable)h,(void *)key);
   }
   if (h->valDestroyFunc&&val) {
      h->valDestroyFunc((HashTable)h,(void *)val);
   }
}

static unsigned long _findPrime(unsigned long start,int dir) {
   static int unit[]={0,1,0,1,0,0,0,1,0,1,0,1,0,1,0,0};
   unsigned long t;
   while (start>1) {
      if (!unit[start&0x0f]) {
         start+=dir;
         continue;
      }
      for (t=2;t<sqrt((double)start);t++) {
         if (!start%t) break;
      }
      if (t>=sqrt((double)start)) {
         break;
      }
      start+=dir;
   }
   return start;
}

static void _hashtable_rehash(IntHashTable *h,
                              CollisionFunc cf,
                              unsigned long newSize) {
   IntHashNode **oldTable=h->table;
   unsigned long i;
   IntHashNode *n,*nn;
   unsigned long oldSize;
   oldSize=h->length;
   h->table=malloc(sizeof(IntHashNode *)*newSize);
   if (!h->table) {
      h->table=oldTable;
      return;
   }
   h->length=newSize;
   h->count=0;
   memset (h->table,0,sizeof(IntHashNode *)*h->length);
   for (i=0;i<oldSize;i++) {
      for (n=oldTable[i];n;n=nn) {
         nn=n->next;
         _hashtable_insert_node(h,n,0,0,cf);
      }
   }
   free(oldTable);
}

static void _hashtable_resize(IntHashTable *h) {
   unsigned long newSize;
   unsigned long oldSize;
   oldSize=h->length;
   newSize=oldSize;
   if (h->count*RESIZE_FACTOR<h->length) {
      newSize=_findPrime(h->length/2-1,-1);
   } else  if (h->length*RESIZE_FACTOR<h->count) {
      newSize=_findPrime(h->length*2+1,+1);
   }
   if (newSize<MIN_LENGTH) { newSize=oldSize; }
   if (newSize!=oldSize) {
      _hashtable_rehash(h,NULL,newSize);
   }
}

#if 0
static int _hashtable_test(IntHashTable *h) {
   unsigned long i;
   int j;
   IntHashNode *n;
   for (i=0;i<h->length;i++) {
      for (n=h->table[i];n&&n->next;n=n->next) {
         j=h->cmpFunc((HashTable)h,n->key,n->next->key);
         printf ("%c",j?(j<0?'-':'+'):'=');
      }
      printf ("\n");
   }
   return 0;
}
#endif

static int _hashtable_insert_node(IntHashTable *h,IntHashNode *node,int resize,int update,CollisionFunc cf) {
   unsigned long hash=h->hashFunc((HashTable)h,node->key)%h->length;
   IntHashNode **n,*nv;
   int i;

   for (n=&(h->table[hash]);*n;n=&((*n)->next)) {
      nv=*n;
      i=h->cmpFunc((HashTable)h,nv->key,node->key);
      if (!i) {
         if (cf) {
            nv->key=node->key;
            cf((HashTable)h,&(nv->key),&(nv->value),node->key,node->value);
            free(node);
            return 1;
         } else {
            if (h->valDestroyFunc) {
               h->valDestroyFunc((HashTable)h,nv->value);
            }
            if (h->keyDestroyFunc) {
               h->keyDestroyFunc((HashTable)h,nv->key);
            }
            nv->key=node->key;
            nv->value=node->value;
            free(node);
            return 1;
         }
      } else if (i>0) {
         break;
      }
   }
   if (!update) {
      node->next=*n;
      *n=node;
      h->count++;
      if (resize) _hashtable_resize(h);
      return 1;
   } else {
      return 0;
   }
}

static int _hashtable_insert(IntHashTable *h,void *key,void *val,int resize,int update) {
   IntHashNode **n,*nv;
   IntHashNode *t;
   int i;
   unsigned long hash=h->hashFunc((HashTable)h,key)%h->length;
   
   for (n=&(h->table[hash]);*n;n=&((*n)->next)) {
      nv=*n;
      i=h->cmpFunc((HashTable)h,nv->key,key);
      if (!i) {
         if (h->valDestroyFunc) { h->valDestroyFunc((HashTable)h,nv->value); }
         nv->value=val;
         return 1;
      } else if (i>0) {
         break;
      }
   }
   if (!update) {
      t=malloc(sizeof(IntHashNode));
      if (!t) return 0;
      t->next=*n;
      *n=t;
      t->key=key;
      t->value=val;
      h->count++;
      if (resize) _hashtable_resize(h);
      return 1;
   } else {
      return 0;
   }
}

static int _hashtable_lookup_or_insert(IntHashTable *h,void *key,void **retVal,void *newVal,int resize) {
   IntHashNode **n,*nv;
   IntHashNode *t;
   int i;
   unsigned long hash=h->hashFunc((HashTable)h,key)%h->length;
   
   for (n=&(h->table[hash]);*n;n=&((*n)->next)) {
      nv=*n;
      i=h->cmpFunc((HashTable)h,nv->key,key);
      if (!i) {
         *retVal=nv->value;
         return 1;
      } else if (i>0) {
         break;
      }
   }
   t=malloc(sizeof(IntHashNode));
   if (!t) return 0;
   t->next=*n;
   *n=t;
   t->key=key;
   t->value=newVal;
   *retVal=newVal;
   h->count++;
   if (resize) _hashtable_resize(h);
   return 1;
}

int hashtable_insert_or_update_computed(HashTable H,
                                        void *key,
                                        ComputeFunc newFunc,
                                        ComputeFunc existsFunc) {
   IntHashTable *h=(IntHashTable *)H;
   IntHashNode **n,*nv;
   IntHashNode *t;
   int i;
   unsigned long hash=h->hashFunc((HashTable)h,key)%h->length;
   
   for (n=&(h->table[hash]);*n;n=&((*n)->next)) {
      nv=*n;
      i=h->cmpFunc((HashTable)h,nv->key,key);
      if (!i) {
         void *old=nv->value;
         if (existsFunc) {
            existsFunc(H,nv->key,&(nv->value));
            if (nv->value!=old) {
               if (h->valDestroyFunc) {
                  h->valDestroyFunc((HashTable)h,old);
               }
            }
         } else {
            return 0;
         }
         return 1;
      } else if (i>0) {
         break;
      }
   }
   t=malloc(sizeof(IntHashNode));
   if (!t) return 0;
   t->key=key;
   t->next=*n;
   *n=t;
   if (newFunc) {
      newFunc(H,t->key,&(t->value));
   } else {
      free(t);
      return 0;
   }
   h->count++;
   _hashtable_resize(h);
   return 1;
}

int hashtable_update(HashTable H,void *key,void *val) {
   IntHashTable *h=(IntHashTable *)H;
   return _hashtable_insert(h,key,val,1,0);
}

int hashtable_insert(HashTable H,void *key,void *val) {
   IntHashTable *h=(IntHashTable *)H;
   return _hashtable_insert(h,key,val,1,0);
}

void hashtable_foreach_update(HashTable H,IteratorUpdateFunc i,void *u) {
   IntHashTable *h=(IntHashTable *)H;
   IntHashNode *n;
   unsigned long x;

   if (h->table) {
      for (x=0;x<h->length;x++) {
         for (n=h->table[x];n;n=n->next) {
            i((HashTable)h,n->key,(void **)&(n->value),u);
         }
      }
   }
}

void hashtable_foreach(HashTable H,IteratorFunc i,void *u) {
   IntHashTable *h=(IntHashTable *)H;
   IntHashNode *n;
   unsigned long x;

   if (h->table) {
      for (x=0;x<h->length;x++) {
         for (n=h->table[x];n;n=n->next) {
            i((HashTable)h,n->key,n->value,u);
         }
      }
   }
}

void hashtable_free(HashTable H) {
   IntHashTable *h=(IntHashTable *)H;
   IntHashNode *n,*nn;
   unsigned long i;

   if (h->table) {
      if (h->keyDestroyFunc || h->keyDestroyFunc) {
         hashtable_foreach(H,_hashtable_destroy,NULL);
      }
      for (i=0;i<h->length;i++) {
         for (n=h->table[i];n;n=nn) {
            nn=n->next;
            free(n);
         }
      }
      free(h->table);
   }
   free(h);
}

DestroyFunc hashtable_set_value_destroy_func(HashTable H,DestroyFunc d) {
   IntHashTable *h=(IntHashTable *)H;
   DestroyFunc r=h->valDestroyFunc;
   h->valDestroyFunc=d;
   return r;
}

DestroyFunc hashtable_set_key_destroy_func(HashTable H,DestroyFunc d) {
   IntHashTable *h=(IntHashTable *)H;
   DestroyFunc r=h->keyDestroyFunc;
   h->keyDestroyFunc=d;
   return r;
}

static int _hashtable_remove(IntHashTable *h,
                             const void *key,
                             void **keyRet,
                             void **valRet,
                             int resize) {
   unsigned long hash=h->hashFunc((HashTable)h,key)%h->length;
   IntHashNode *n,*p;
   int i;
   
   for (p=NULL,n=h->table[hash];n;p=n,n=n->next) {
      i=h->cmpFunc((HashTable)h,n->key,key);
      if (!i) {
         if (p) p=n->next; else h->table[hash]=n->next;
         *keyRet=n->key;
         *valRet=n->value;
         free(n);
         h->count++;
         return 1;
      } else if (i>0) {
         break;
      }
   }
   return 0;
}

static int _hashtable_delete(IntHashTable *h,const void *key,int resize) {
   unsigned long hash=h->hashFunc((HashTable)h,key)%h->length;
   IntHashNode *n,*p;
   int i;
   
   for (p=NULL,n=h->table[hash];n;p=n,n=n->next) {
      i=h->cmpFunc((HashTable)h,n->key,key);
      if (!i) {
         if (p) p=n->next; else h->table[hash]=n->next;
         if (h->valDestroyFunc) { h->valDestroyFunc((HashTable)h,n->value); }
         if (h->keyDestroyFunc) { h->keyDestroyFunc((HashTable)h,n->key); }
         free(n);
         h->count++;
         return 1;
      } else if (i>0) {
         break;
      }
   }
   return 0;
}

int hashtable_remove(HashTable H,const void *key,void **keyRet,void **valRet) {
   IntHashTable *h=(IntHashTable *)H;
   return _hashtable_remove(h,key,keyRet,valRet,1);
}

int hashtable_delete(HashTable H,const void *key) {
   IntHashTable *h=(IntHashTable *)H;
   return _hashtable_delete(h,key,1);
}

void hashtable_rehash_compute(HashTable H,CollisionFunc cf) {
   IntHashTable *h=(IntHashTable *)H;
   _hashtable_rehash(h,cf,h->length);
}

void hashtable_rehash(HashTable H) {
   IntHashTable *h=(IntHashTable *)H;
   _hashtable_rehash(h,NULL,h->length);
}

int hashtable_lookup_or_insert(HashTable H,void *key,void **valp,void *val) {
   IntHashTable *h=(IntHashTable *)H;
   return _hashtable_lookup_or_insert(h,key,valp,val,1);
}

int hashtable_lookup(const HashTable H,const void *key,void **valp) {
   IntHashTable *h=(IntHashTable *)H;
   unsigned long hash=h->hashFunc((HashTable)h,key)%h->length;
   IntHashNode *n;
   int i;
   
   for (n=h->table[hash];n;n=n->next) {
      i=h->cmpFunc((HashTable)h,n->key,key);
      if (!i) {
         *valp=n->value;
         return 1;
      } else if (i>0) {
         break;
      }
   }
   return 0;
}

unsigned long hashtable_get_count(const HashTable H) {
   IntHashTable *h=(IntHashTable *)H;
   return h->count;
}

void *hashtable_get_user_data(const HashTable H) {
   IntHashTable *h=(IntHashTable *)H;
   return h->userData;
}

void *hashtable_set_user_data(HashTable H,void *data) {
   IntHashTable *h=(IntHashTable *)H;
   void *r=h->userData;
   h->userData=data;
   return r;
}
