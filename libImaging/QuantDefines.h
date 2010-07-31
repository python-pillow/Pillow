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

#ifndef __DEFINES_H__
#define __DEFINES_H__

#if 0

void *newMalloc(size_t,const char *,const char *,int);
void newFree(void *,const char *,const char *,int);
void print_malloc_stats();
#define malloc(x) newMalloc(x,__FILE__,__FUNCTION__,__LINE__)
#define free(x) newFree(x,__FILE__,__FUNCTION__,__LINE__)

#endif

#endif
