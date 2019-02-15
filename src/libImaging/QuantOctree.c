/* Copyright (c) 2010 Oliver Tonnhofer <olt@bogosoft.com>, Omniscale
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
*/

/*
// This file implements a variation of the octree color quantization algorithm.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#include "QuantOctree.h"

typedef struct _ColorBucket{
   /* contains palette index when used for look up cube */
   uint32_t count;
   uint64_t r;
   uint64_t g;
   uint64_t b;
   uint64_t a;
} *ColorBucket;

typedef struct _ColorCube{
   unsigned int rBits, gBits, bBits, aBits;
   unsigned int rWidth, gWidth, bWidth, aWidth;
   unsigned int rOffset, gOffset, bOffset, aOffset;

   long size;
   ColorBucket buckets;
} *ColorCube;

#define MAX(a, b) (a)>(b) ? (a) : (b)

static ColorCube
new_color_cube(int r, int g, int b, int a) {
   ColorCube cube;

   /* malloc check ok, small constant allocation */
   cube = malloc(sizeof(struct _ColorCube));
   if (!cube) return NULL;

   cube->rBits = MAX(r, 0);
   cube->gBits = MAX(g, 0);
   cube->bBits = MAX(b, 0);
   cube->aBits = MAX(a, 0);

   /* overflow check for size multiplication below */
   if (cube->rBits + cube->gBits + cube->bBits + cube->aBits > 31) {
       free(cube);
       return NULL;
   }

   /* the width of the cube for each dimension */
   cube->rWidth = 1<<cube->rBits;
   cube->gWidth = 1<<cube->gBits;
   cube->bWidth = 1<<cube->bBits;
   cube->aWidth = 1<<cube->aBits;

   /* the offsets of each color */

   cube->rOffset = cube->gBits + cube->bBits + cube->aBits;
   cube->gOffset = cube->bBits + cube->aBits;
   cube->bOffset = cube->aBits;
   cube->aOffset = 0;

   /* the number of color buckets */
   cube->size = cube->rWidth * cube->gWidth * cube->bWidth * cube->aWidth;
   /* malloc check ok, overflow checked above */
   cube->buckets = calloc(cube->size, sizeof(struct _ColorBucket));

   if (!cube->buckets) {
      free(cube);
      return NULL;
   }
   return cube;
}

static void
free_color_cube(ColorCube cube) {
   if (cube != NULL) {
      free(cube->buckets);
      free(cube);
   }
}

static long
color_bucket_offset_pos(const ColorCube cube,
   unsigned int r, unsigned int g, unsigned int b, unsigned int a)
{
   return r<<cube->rOffset | g<<cube->gOffset | b<<cube->bOffset | a<<cube->aOffset;
}

static long
color_bucket_offset(const ColorCube cube, const Pixel *p) {
   unsigned int r = p->c.r>>(8-cube->rBits);
   unsigned int g = p->c.g>>(8-cube->gBits);
   unsigned int b = p->c.b>>(8-cube->bBits);
   unsigned int a = p->c.a>>(8-cube->aBits);
   return color_bucket_offset_pos(cube, r, g, b, a);
}

static ColorBucket
color_bucket_from_cube(const ColorCube cube, const Pixel *p) {
   unsigned int offset = color_bucket_offset(cube, p);
   return &cube->buckets[offset];
}

static void
add_color_to_color_cube(const ColorCube cube, const Pixel *p) {
   ColorBucket bucket = color_bucket_from_cube(cube, p);
   bucket->count += 1;
   bucket->r += p->c.r;
   bucket->g += p->c.g;
   bucket->b += p->c.b;
   bucket->a += p->c.a;
}

static long
count_used_color_buckets(const ColorCube cube) {
   long usedBuckets = 0;
   long i;
   for (i=0; i < cube->size; i++) {
      if (cube->buckets[i].count > 0) {
         usedBuckets += 1;
      }
   }
   return usedBuckets;
}

static void
avg_color_from_color_bucket(const ColorBucket bucket, Pixel *dst) {
   float count = bucket->count;
   if (count != 0) {
       dst->c.r = (int)(bucket->r / count);
       dst->c.g = (int)(bucket->g / count);
       dst->c.b = (int)(bucket->b / count);
       dst->c.a = (int)(bucket->a / count);
   } else {
       dst->c.r = 0;
       dst->c.g = 0;
       dst->c.b = 0;
       dst->c.a = 0;
   }
}

static int
compare_bucket_count(const ColorBucket a, const ColorBucket b) {
   return b->count - a->count;
}

static ColorBucket
create_sorted_color_palette(const ColorCube cube) {
   ColorBucket buckets;
   if (cube->size > LONG_MAX / sizeof(struct _ColorBucket)) {
       return NULL;
   }
   /* malloc check ok, calloc + overflow check above for memcpy */
   buckets = calloc(cube->size, sizeof(struct _ColorBucket));
   if (!buckets) return NULL;
   memcpy(buckets, cube->buckets, sizeof(struct _ColorBucket)*cube->size);

   qsort(buckets, cube->size, sizeof(struct _ColorBucket),
         (int (*)(void const *, void const *))&compare_bucket_count);

   return buckets;
}

void add_bucket_values(ColorBucket src, ColorBucket dst) {
   dst->count += src->count;
   dst->r += src->r;
   dst->g += src->g;
   dst->b += src->b;
   dst->a += src->a;
}

/* expand or shrink a given cube to level */
static ColorCube copy_color_cube(const ColorCube cube,
   int rBits, int gBits, int bBits, int aBits)
{
   unsigned int r, g, b, a;
   long src_pos, dst_pos;
   unsigned int src_reduce[4] = {0}, dst_reduce[4] = {0};
   unsigned int width[4];
   ColorCube result;

   result = new_color_cube(rBits, gBits, bBits, aBits);
   if (!result) return NULL;

   if (cube->rBits > rBits) {
      dst_reduce[0] = cube->rBits - result->rBits;
      width[0] = cube->rWidth;
   } else {
      src_reduce[0] = result->rBits - cube->rBits;
      width[0] = result->rWidth;
   }
   if (cube->gBits > gBits) {
      dst_reduce[1] = cube->gBits - result->gBits;
      width[1] = cube->gWidth;
   } else {
      src_reduce[1] = result->gBits - cube->gBits;
      width[1] = result->gWidth;
   }
   if (cube->bBits > bBits) {
      dst_reduce[2] = cube->bBits - result->bBits;
      width[2] = cube->bWidth;
   } else {
      src_reduce[2] = result->bBits - cube->bBits;
      width[2] = result->bWidth;
   }
   if (cube->aBits > aBits) {
      dst_reduce[3] = cube->aBits - result->aBits;
      width[3] = cube->aWidth;
   } else {
      src_reduce[3] = result->aBits - cube->aBits;
      width[3] = result->aWidth;
   }

   for (r=0; r<width[0]; r++) {
      for (g=0; g<width[1]; g++) {
         for (b=0; b<width[2]; b++) {
            for (a=0; a<width[3]; a++) {
               src_pos = color_bucket_offset_pos(cube,
                                               r>>src_reduce[0],
                                               g>>src_reduce[1],
                                               b>>src_reduce[2],
                                               a>>src_reduce[3]);
               dst_pos = color_bucket_offset_pos(result,
                                               r>>dst_reduce[0],
                                               g>>dst_reduce[1],
                                               b>>dst_reduce[2],
                                               a>>dst_reduce[3]);
               add_bucket_values(
                  &cube->buckets[src_pos],
                  &result->buckets[dst_pos]
               );
            }
         }
      }
   }
   return result;
}

void
subtract_color_buckets(ColorCube cube, ColorBucket buckets, long nBuckets) {
   ColorBucket minuend, subtrahend;
   long i;
   Pixel p;
   for (i=0; i<nBuckets; i++) {
      subtrahend = &buckets[i];

      // If the subtrahend contains no buckets, there is nothing to subtract.
      if (subtrahend->count == 0) continue;

      avg_color_from_color_bucket(subtrahend, &p);
      minuend = color_bucket_from_cube(cube, &p);
      minuend->count -= subtrahend->count;
      minuend->r -= subtrahend->r;
      minuend->g -= subtrahend->g;
      minuend->b -= subtrahend->b;
      minuend->a -= subtrahend->a;
   }
}

static void
set_lookup_value(const ColorCube cube, const Pixel *p, long value) {
   ColorBucket bucket = color_bucket_from_cube(cube, p);
   bucket->count = value;
}

uint64_t
lookup_color(const ColorCube cube, const Pixel *p) {
   ColorBucket bucket = color_bucket_from_cube(cube, p);
   return bucket->count;
}

void add_lookup_buckets(ColorCube cube, ColorBucket palette, long nColors, long offset) {
   long i;
   Pixel p;
   for (i=offset; i<offset+nColors; i++) {
      avg_color_from_color_bucket(&palette[i], &p);
      set_lookup_value(cube, &p, i);
   }
}

ColorBucket
combined_palette(ColorBucket bucketsA, long nBucketsA, ColorBucket bucketsB, long nBucketsB) {
   ColorBucket result;
   if (nBucketsA > LONG_MAX - nBucketsB ||
       (nBucketsA+nBucketsB) > LONG_MAX / sizeof(struct _ColorBucket)) {
       return NULL;
   }
   /* malloc check ok, overflow check above */
   result = calloc(nBucketsA + nBucketsB, sizeof(struct _ColorBucket));
   if (!result) {
       return NULL;
   }
   memcpy(result, bucketsA, sizeof(struct _ColorBucket) * nBucketsA);
   memcpy(&result[nBucketsA], bucketsB, sizeof(struct _ColorBucket) * nBucketsB);
   return result;
}

static Pixel *
create_palette_array(const ColorBucket palette, unsigned int paletteLength) {
   Pixel *paletteArray;
   unsigned int i;

   /* malloc check ok, calloc for overflow */
   paletteArray = calloc(paletteLength, sizeof(Pixel));
   if (!paletteArray) return NULL;

   for (i=0; i<paletteLength; i++) {
      avg_color_from_color_bucket(&palette[i], &paletteArray[i]);
   }
   return paletteArray;
}

static void
map_image_pixels(const Pixel *pixelData,
                 uint32_t nPixels,
                 const ColorCube lookupCube,
                 uint32_t *pixelArray)
{
   long i;
   for (i=0; i<nPixels; i++) {
      pixelArray[i] = lookup_color(lookupCube, &pixelData[i]);
   }
}

const int CUBE_LEVELS[8]       = {4, 4, 4, 0, 2, 2, 2, 0};
const int CUBE_LEVELS_ALPHA[8] = {3, 4, 3, 3, 2, 2, 2, 2};

int quantize_octree(Pixel *pixelData,
          uint32_t nPixels,
          uint32_t nQuantPixels,
          Pixel **palette,
          uint32_t *paletteLength,
          uint32_t **quantizedPixels,
          int withAlpha)
{
   ColorCube fineCube = NULL;
   ColorCube coarseCube = NULL;
   ColorCube lookupCube = NULL;
   ColorCube coarseLookupCube = NULL;
   ColorBucket paletteBucketsCoarse = NULL;
   ColorBucket paletteBucketsFine = NULL;
   ColorBucket paletteBuckets = NULL;
   uint32_t *qp = NULL;
   long i;
   long nCoarseColors, nFineColors, nAlreadySubtracted;
   const int *cubeBits;

   if (withAlpha) {
       cubeBits = CUBE_LEVELS_ALPHA;
   }
   else {
       cubeBits = CUBE_LEVELS;
   }

   /*
   Create two color cubes, one fine grained with 8x16x8=1024
   colors buckets and a coarse with 4x4x4=64 color buckets.
   The coarse one guarantees that there are color buckets available for
   the whole color range (assuming nQuantPixels > 64).

   For a quantization to 256 colors all 64 coarse colors will be used
   plus the 192 most used color buckets from the fine color cube.
   The average of all colors within one bucket is used as the actual
   color for that bucket.

    For images with alpha the cubes gets a forth dimension,
    8x16x8x8 and 4x4x4x4.
   */

   /* create fine cube */
   fineCube = new_color_cube(cubeBits[0], cubeBits[1],
                             cubeBits[2], cubeBits[3]);
   if (!fineCube) goto error;
   for (i=0; i<nPixels; i++) {
      add_color_to_color_cube(fineCube, &pixelData[i]);
   }

   /* create coarse cube */
   coarseCube = copy_color_cube(fineCube, cubeBits[4], cubeBits[5],
                                          cubeBits[6], cubeBits[7]);
   if (!coarseCube) goto error;
   nCoarseColors = count_used_color_buckets(coarseCube);

   /* limit to nQuantPixels */
   if (nCoarseColors > nQuantPixels)
      nCoarseColors = nQuantPixels;

   /* how many space do we have in our palette for fine colors? */
   nFineColors = nQuantPixels - nCoarseColors;

   /* create fine color palette */
   paletteBucketsFine = create_sorted_color_palette(fineCube);
   if (!paletteBucketsFine) goto error;

   /* remove the used fine colors from the coarse cube */
   subtract_color_buckets(coarseCube, paletteBucketsFine, nFineColors);

   /* did the subtraction cleared one or more coarse bucket? */
   while (nCoarseColors > count_used_color_buckets(coarseCube)) {
      /* then we can use the free buckets for fine colors */
      nAlreadySubtracted = nFineColors;
      nCoarseColors = count_used_color_buckets(coarseCube);
      nFineColors = nQuantPixels - nCoarseColors;
      subtract_color_buckets(coarseCube, &paletteBucketsFine[nAlreadySubtracted],
                             nFineColors-nAlreadySubtracted);
   }

   /* create our palette buckets with fine and coarse combined */
   paletteBucketsCoarse = create_sorted_color_palette(coarseCube);
   if (!paletteBucketsCoarse) goto error;
   paletteBuckets = combined_palette(paletteBucketsCoarse, nCoarseColors,
                                     paletteBucketsFine, nFineColors);

   free(paletteBucketsFine);
   paletteBucketsFine = NULL;
   free(paletteBucketsCoarse);
   paletteBucketsCoarse = NULL;
   if (!paletteBuckets) goto error;

   /* add all coarse colors to our coarse lookup cube. */
   coarseLookupCube = new_color_cube(cubeBits[4], cubeBits[5],
                                     cubeBits[6], cubeBits[7]);
   if (!coarseLookupCube) goto error;
   add_lookup_buckets(coarseLookupCube, paletteBuckets, nCoarseColors, 0);

   /* expand coarse cube (64) to larger fine cube (4k). the value of each
      coarse bucket is then present in the according 64 fine buckets. */
   lookupCube = copy_color_cube(coarseLookupCube, cubeBits[0], cubeBits[1],
                                                  cubeBits[2], cubeBits[3]);
   if (!lookupCube) goto error;

   /* add fine colors to the lookup cube */
   add_lookup_buckets(lookupCube, paletteBuckets, nFineColors, nCoarseColors);

   /* create result pixels and map palette indices */
   /* malloc check ok, calloc for overflow */
   qp = calloc(nPixels, sizeof(Pixel));
   if (!qp) goto error;
   map_image_pixels(pixelData, nPixels, lookupCube, qp);

   /* convert palette buckets to RGB pixel palette */
   *palette = create_palette_array(paletteBuckets, nQuantPixels);
   if (!(*palette)) goto error;

   *quantizedPixels = qp;
   *paletteLength = nQuantPixels;

   free_color_cube(coarseCube);
   free_color_cube(fineCube);
   free_color_cube(lookupCube);
   free_color_cube(coarseLookupCube);
   free(paletteBuckets);
   return 1;

error:
   /* everything is initialized to NULL
      so we are safe to call free */
   free(qp);
   free_color_cube(lookupCube);
   free_color_cube(coarseLookupCube);
   free(paletteBuckets);
   free(paletteBucketsCoarse);
   free(paletteBucketsFine);
   free_color_cube(coarseCube);
   free_color_cube(fineCube);
   return 0;
}
