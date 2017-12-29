/*
 * The Python Imaging Library
 * $Id$
 *
 * heap data type used by the image quantizer
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
#include <limits.h>

#include "QuantHeap.h"

struct _Heap {
   void **heap;
   int heapsize;
   int heapcount;
   HeapCmpFunc cf;
};

#define INITIAL_SIZE 256

// #define DEBUG

#ifdef DEBUG
static int _heap_test(Heap *);
#endif

void ImagingQuantHeapFree(Heap *h) {
   free(h->heap);
   free(h);
}

static int _heap_grow(Heap *h,int newsize) {
   void *newheap;
   if (!newsize) newsize=h->heapsize<<1;
   if (newsize<h->heapsize) return 0;
   if (newsize > INT_MAX / sizeof(void *)){
       return 0;
   }
   /* malloc check ok, using calloc for overflow, also checking
      above due to memcpy below*/
   newheap=calloc(newsize, sizeof(void *));
   if (!newheap) return 0;
   memcpy(newheap,h->heap,sizeof(void *)*h->heapsize);
   free(h->heap);
   h->heap=newheap;
   h->heapsize=newsize;
   return 1;
}

#ifdef DEBUG
static int _heap_test(Heap *h) {
   int k;
   for (k=1;k*2<=h->heapcount;k++) {
      if (h->cf(h,h->heap[k],h->heap[k*2])<0) {
         printf ("heap is bad\n");
         return 0;
      }
      if (k*2+1<=h->heapcount && h->cf(h,h->heap[k],h->heap[k*2+1])<0) {
         printf ("heap is bad\n");
         return 0;
      }
   }
   return 1;
}
#endif

int ImagingQuantHeapRemove(Heap* h,void **r) {
   int k,l;
   void *v;

   if (!h->heapcount) {
      return 0;
   }
   *r=h->heap[1];
   v=h->heap[h->heapcount--];
   for (k=1;k*2<=h->heapcount;k=l) {
      l=k*2;
      if (l<h->heapcount) {
         if (h->cf(h,h->heap[l],h->heap[l+1])<0) {
            l++;
         }
      }
      if (h->cf(h,v,h->heap[l])>0) {
         break;
      }
      h->heap[k]=h->heap[l];
   }
   h->heap[k]=v;
#ifdef DEBUG
   if (!_heap_test(h)) { printf ("oops - heap_remove messed up the heap\n"); exit(1); }
#endif
   return 1;
}

int ImagingQuantHeapAdd(Heap *h,void *val) {
   int k;
   if (h->heapcount==h->heapsize-1) {
      _heap_grow(h,0);
   }
   k=++h->heapcount;
   while (k!=1) {
      if (h->cf(h,val,h->heap[k/2])<=0) {
         break;
      }
      h->heap[k]=h->heap[k/2];
      k>>=1;
   }
   h->heap[k]=val;
#ifdef DEBUG
   if (!_heap_test(h)) { printf ("oops - heap_add messed up the heap\n"); exit(1); }
#endif
   return 1;
}

int ImagingQuantHeapTop(Heap *h,void **r) {
   if (!h->heapcount) {
      return 0;
   }
   *r=h->heap[1];
   return 1;
}

Heap *ImagingQuantHeapNew(HeapCmpFunc cf) {
   Heap *h;

   /* malloc check ok, small constant allocation */
   h=malloc(sizeof(Heap));
   if (!h) return NULL;
   h->heapsize=INITIAL_SIZE;
   /* malloc check ok, using calloc for overflow */
   h->heap=calloc(h->heapsize, sizeof(void *));
   if (!h->heap) {
       free(h);
       return NULL;
   }
   h->heapcount=0;
   h->cf=cf;
   return h;
}
