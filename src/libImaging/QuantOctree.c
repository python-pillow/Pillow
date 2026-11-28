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

#include "ImagingUtils.h"
#include "QuantOctree.h"

typedef struct _ColorBucket {
    /* contains palette index when used for look up cube */
    uint32_t count;
    uint64_t r;
    uint64_t g;
    uint64_t b;
    uint64_t a;
} *ColorBucket;

typedef struct _ColorCube {
    unsigned int rBits, gBits, bBits, aBits;
    unsigned int rWidth, gWidth, bWidth, aWidth;
    unsigned int rOffset, gOffset, bOffset, aOffset;

    unsigned long size;
    ColorBucket buckets;
} *ColorCube;

static ColorCube
new_color_cube(int r, int g, int b, int a) {
    ColorCube cube;

    /* malloc check ok, small constant allocation */
    cube = malloc(sizeof(struct _ColorCube));
    if (!cube) {
        return NULL;
    }

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
    cube->rWidth = 1 << cube->rBits;
    cube->gWidth = 1 << cube->gBits;
    cube->bWidth = 1 << cube->bBits;
    cube->aWidth = 1 << cube->aBits;

    /* the offsets of each color */

    cube->rOffset = cube->gBits + cube->bBits + cube->aBits;
    cube->gOffset = cube->bBits + cube->aBits;
    cube->bOffset = cube->aBits;
    cube->aOffset = 0;

    /* the number of color buckets */
    cube->size = (unsigned long)cube->rWidth * cube->gWidth *
                 (unsigned long)cube->bWidth * cube->aWidth;
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
color_bucket_offset_pos(
    const ColorCube cube, unsigned int r, unsigned int g, unsigned int b, unsigned int a
) {
    return r << cube->rOffset | g << cube->gOffset | b << cube->bOffset |
           a << cube->aOffset;
}

static long
color_bucket_offset(const ColorCube cube, const Pixel *p) {
    unsigned int r = p->c.r >> (8 - cube->rBits);
    unsigned int g = p->c.g >> (8 - cube->gBits);
    unsigned int b = p->c.b >> (8 - cube->bBits);
    unsigned int a = p->c.a >> (8 - cube->aBits);
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

static int
has_at_least_used_color_buckets(const ColorCube cube, unsigned long threshold) {
    unsigned long usedBuckets = 0;
    unsigned long i;
    for (i = 0; i < cube->size; i++) {
        if (cube->buckets[i].count > 0) {
            usedBuckets += 1;
            if (usedBuckets >= threshold) {
                return 1;
            }
        }
    }
    return 0;
}

static unsigned long
count_used_color_buckets(const ColorCube cube) {
    unsigned long usedBuckets = 0;
    unsigned long i;
    for (i = 0; i < cube->size; i++) {
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
        dst->c.r = CLIP8((int)(bucket->r / count));
        dst->c.g = CLIP8((int)(bucket->g / count));
        dst->c.b = CLIP8((int)(bucket->b / count));
        dst->c.a = CLIP8((int)(bucket->a / count));
    } else {
        dst->c.r = 0;
        dst->c.g = 0;
        dst->c.b = 0;
        dst->c.a = 0;
    }
}

static int
compare_bucket_count(const ColorBucket a, const ColorBucket b) {
    return a->count == b->count ? 0 : (a->count > b->count ? -1 : 1);
}

static ColorBucket
create_sorted_color_palette(const ColorCube cube) {
    ColorBucket buckets;
    if (cube->size > LONG_MAX / sizeof(struct _ColorBucket)) {
        return NULL;
    }
    /* malloc check ok, calloc + overflow check above for memcpy */
    buckets = calloc(cube->size, sizeof(struct _ColorBucket));
    if (!buckets) {
        return NULL;
    }
    memcpy(buckets, cube->buckets, sizeof(struct _ColorBucket) * cube->size);

    qsort(
        buckets,
        cube->size,
        sizeof(struct _ColorBucket),
        (int (*)(void const *, void const *))&compare_bucket_count
    );

    return buckets;
}

void
add_bucket_values(ColorBucket src, ColorBucket dst) {
    dst->count += src->count;
    dst->r += src->r;
    dst->g += src->g;
    dst->b += src->b;
    dst->a += src->a;
}

/* expand or shrink a given cube to level */
static ColorCube
copy_color_cube(
    const ColorCube cube,
    unsigned int rBits,
    unsigned int gBits,
    unsigned int bBits,
    unsigned int aBits
) {
    unsigned int r, g, b, a;
    long src_pos, dst_pos;
    unsigned int src_reduce[4] = {0}, dst_reduce[4] = {0};
    unsigned int width[4];
    ColorCube result;

    result = new_color_cube(rBits, gBits, bBits, aBits);
    if (!result) {
        return NULL;
    }

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

    for (r = 0; r < width[0]; r++) {
        for (g = 0; g < width[1]; g++) {
            for (b = 0; b < width[2]; b++) {
                for (a = 0; a < width[3]; a++) {
                    src_pos = color_bucket_offset_pos(
                        cube,
                        r >> src_reduce[0],
                        g >> src_reduce[1],
                        b >> src_reduce[2],
                        a >> src_reduce[3]
                    );
                    dst_pos = color_bucket_offset_pos(
                        result,
                        r >> dst_reduce[0],
                        g >> dst_reduce[1],
                        b >> dst_reduce[2],
                        a >> dst_reduce[3]
                    );
                    add_bucket_values(
                        &cube->buckets[src_pos], &result->buckets[dst_pos]
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
    for (i = 0; i < nBuckets; i++) {
        subtrahend = &buckets[i];

        // If the subtrahend contains no buckets, there is nothing to subtract.
        if (subtrahend->count == 0) {
            continue;
        }

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

void
add_lookup_buckets(ColorCube cube, ColorBucket palette, long nColors, long offset) {
    long i;
    Pixel p;
    for (i = offset + nColors - 1; i >= offset; i--) {
        avg_color_from_color_bucket(&palette[i], &p);
        set_lookup_value(cube, &p, i);
    }
}

ColorBucket
combined_palette(
    ColorBucket bucketsA,
    unsigned long nBucketsA,
    ColorBucket bucketsB,
    unsigned long nBucketsB
) {
    ColorBucket result;
    if (nBucketsA > LONG_MAX - nBucketsB ||
        (nBucketsA + nBucketsB) > LONG_MAX / sizeof(struct _ColorBucket)) {
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
    if (!paletteArray) {
        return NULL;
    }

    for (i = 0; i < paletteLength; i++) {
        avg_color_from_color_bucket(&palette[i], &paletteArray[i]);
    }
    return paletteArray;
}

static void
map_image_pixels(
    const Pixel *pixelData,
    uint32_t nPixels,
    const ColorCube lookupCube,
    uint32_t *pixelArray
) {
    long i;
    for (i = 0; i < nPixels; i++) {
        pixelArray[i] = lookup_color(lookupCube, &pixelData[i]);
    }
}

const unsigned int CUBE_LEVELS[8] = {4, 4, 4, 0, 2, 2, 2, 0};
const unsigned int CUBE_LEVELS_ALPHA[8] = {3, 4, 3, 3, 2, 2, 2, 2};

#define MAX_TRIE_DEPTH 32
#define MAX_TRIE_LEAVES 4096
/* A full binary tree with L leaves has 2 * L - 1 nodes; allow +2 for one
   transient split before online pruning restores leaf_count <= MAX_TRIE_LEAVES. */
#define MAX_TRIE_NODES (2 * MAX_TRIE_LEAVES + 1)

typedef struct _ColorTrieNode {
    uint64_t r;
    uint64_t g;
    uint64_t b;
    uint64_t a;
    uint32_t count;
    uint32_t prefix;
    uint32_t palette_index;
    int32_t child[2];
    int32_t parent;
    int32_t next_reducible;
    int32_t prev_reducible;
    uint8_t depth;
    uint8_t is_leaf;
    uint8_t in_reducible;
} ColorTrieNode;

typedef struct _ColorTrie {
    ColorTrieNode *nodes;
    int32_t capacity;
    int32_t used;
    int32_t free_head;
    int32_t root;
    uint32_t leaf_count;
    uint8_t max_depth;
    int32_t reducible_head[MAX_TRIE_DEPTH];
    uint32_t reducible_count[MAX_TRIE_DEPTH];
} ColorTrie;

typedef struct _TrieSortEntry {
    int32_t idx;
    uint32_t count;
    uint32_t prefix;
} TrieSortEntry;

static uint32_t
spread_bits_4(uint32_t x) {
    x = (x | (x << 12)) & 0x000F000FU;
    x = (x | (x << 6)) & 0x03030303U;
    x = (x | (x << 3)) & 0x11111111U;
    return x;
}

static uint32_t
spread_bits_3(uint32_t x) {
    x = (x | (x << 8)) & 0x0000F00FU;
    x = (x | (x << 4)) & 0x000C30C3U;
    x = (x | (x << 2)) & 0x00249249U;
    return x;
}

static uint32_t
pixel_morton_code(const Pixel *p, int withAlpha) {
    if (withAlpha) {
        return (spread_bits_4(p->c.g) << 3) | (spread_bits_4(p->c.r) << 2) |
               (spread_bits_4(p->c.a) << 1) | spread_bits_4(p->c.b);
    }
    return ((spread_bits_3(p->c.g) << 2) | (spread_bits_3(p->c.r) << 1) |
            spread_bits_3(p->c.b))
           << 8;
}

/* Return the 0-based index from the MSB (0..31) of the highest set bit in diff.
   Caller guarantees diff != 0. */
static uint8_t
first_diff_bit(uint32_t diff) {
    uint8_t n = 0;
    if ((diff & 0xFFFF0000U) == 0) {
        n += 16;
        diff <<= 16;
    }
    if ((diff & 0xFF000000U) == 0) {
        n += 8;
        diff <<= 8;
    }
    if ((diff & 0xF0000000U) == 0) {
        n += 4;
        diff <<= 4;
    }
    if ((diff & 0xC0000000U) == 0) {
        n += 2;
        diff <<= 2;
    }
    if ((diff & 0x80000000U) == 0) {
        n += 1;
    }
    return n;
}

static uint32_t
mask_prefix(uint32_t code, uint8_t depth) {
    if (depth == 0) {
        return 0;
    }
    return code & (~0U << (32 - depth));
}

static int
prefix_matches(uint32_t a, uint32_t b, uint8_t depth) {
    if (depth == 0) {
        return 1;
    }
    return ((a ^ b) >> (32 - depth)) == 0;
}

static int32_t
trie_alloc_node(ColorTrie *trie) {
    int32_t idx;
    if (trie->free_head != -1) {
        idx = trie->free_head;
        trie->free_head = trie->nodes[idx].child[0];
    } else {
        if (trie->used == trie->capacity) {
            int32_t new_cap = trie->capacity * 2;
            ColorTrieNode *grown;
            if (new_cap > MAX_TRIE_NODES) {
                new_cap = MAX_TRIE_NODES;
            }
            if (new_cap <= trie->capacity) {
                return -1;
            }
            /* malloc check ok, bounded by MAX_TRIE_NODES */
            grown = realloc(trie->nodes, (size_t)new_cap * sizeof(ColorTrieNode));
            if (!grown) {
                return -1;
            }
            trie->nodes = grown;
            trie->capacity = new_cap;
        }
        idx = trie->used++;
    }
    memset(&trie->nodes[idx], 0, sizeof(ColorTrieNode));
    trie->nodes[idx].child[0] = -1;
    trie->nodes[idx].child[1] = -1;
    trie->nodes[idx].parent = -1;
    trie->nodes[idx].next_reducible = -1;
    trie->nodes[idx].prev_reducible = -1;
    return idx;
}

static void
trie_free_node(ColorTrie *trie, int32_t idx) {
    trie->nodes[idx].child[0] = trie->free_head;
    trie->free_head = idx;
}

static void
trie_add_reducible(ColorTrie *trie, int32_t idx) {
    ColorTrieNode *node = &trie->nodes[idx];
    uint8_t d = node->depth;
    int32_t head;
    if (node->in_reducible) {
        return;
    }
    head = trie->reducible_head[d];
    node->prev_reducible = -1;
    node->next_reducible = head;
    if (head != -1) {
        trie->nodes[head].prev_reducible = idx;
    }
    trie->reducible_head[d] = idx;
    trie->reducible_count[d]++;
    node->in_reducible = 1;
}

static void
trie_remove_reducible(ColorTrie *trie, int32_t idx) {
    ColorTrieNode *node = &trie->nodes[idx];
    uint8_t d = node->depth;
    if (!node->in_reducible) {
        return;
    }
    if (node->prev_reducible != -1) {
        trie->nodes[node->prev_reducible].next_reducible = node->next_reducible;
    } else {
        trie->reducible_head[d] = node->next_reducible;
    }
    if (node->next_reducible != -1) {
        trie->nodes[node->next_reducible].prev_reducible = node->prev_reducible;
    }
    node->prev_reducible = -1;
    node->next_reducible = -1;
    node->in_reducible = 0;
    trie->reducible_count[d]--;
}

static void
trie_reduce_node(ColorTrie *trie, int32_t idx) {
    ColorTrieNode *node = &trie->nodes[idx];
    int32_t c0 = node->child[0];
    int32_t c1 = node->child[1];
    int32_t parent_idx = node->parent;

    trie_remove_reducible(trie, idx);

    node->count = trie->nodes[c0].count + trie->nodes[c1].count;
    node->r = trie->nodes[c0].r + trie->nodes[c1].r;
    node->g = trie->nodes[c0].g + trie->nodes[c1].g;
    node->b = trie->nodes[c0].b + trie->nodes[c1].b;
    node->a = trie->nodes[c0].a + trie->nodes[c1].a;
    node->child[0] = -1;
    node->child[1] = -1;
    node->is_leaf = 1;

    trie_free_node(trie, c0);
    trie_free_node(trie, c1);
    trie->leaf_count--;

    if (parent_idx != -1) {
        const ColorTrieNode *parent = &trie->nodes[parent_idx];
        if (trie->nodes[parent->child[0]].is_leaf &&
            trie->nodes[parent->child[1]].is_leaf) {
            trie_add_reducible(trie, parent_idx);
        }
    }
}

static int
trie_insert_pixel(ColorTrie *trie, const Pixel *p, uint32_t code, int32_t *out_leaf) {
    int32_t idx;
    uint8_t split_depth;
    int32_t branch_idx, leaf_idx, old_parent;
    uint32_t new_bit, old_bit;

    if (trie->root == -1) {
        int32_t root = trie_alloc_node(trie);
        if (root < 0) {
            return 0;
        }
        trie->nodes[root].prefix = code;
        trie->nodes[root].depth = trie->max_depth;
        trie->nodes[root].is_leaf = 1;
        trie->nodes[root].count = 1;
        trie->nodes[root].r = p->c.r;
        trie->nodes[root].g = p->c.g;
        trie->nodes[root].b = p->c.b;
        trie->nodes[root].a = p->c.a;
        trie->root = root;
        trie->leaf_count = 1;
        *out_leaf = root;
        return 1;
    }

    idx = trie->root;
    while (!trie->nodes[idx].is_leaf) {
        uint8_t d = trie->nodes[idx].depth;
        if (!prefix_matches(code, trie->nodes[idx].prefix, d)) {
            break;
        }
        idx = trie->nodes[idx].child[(code >> (31 - d)) & 1];
    }

    if (trie->nodes[idx].is_leaf &&
        prefix_matches(code, trie->nodes[idx].prefix, trie->nodes[idx].depth)) {
        ColorTrieNode *leaf = &trie->nodes[idx];
        leaf->count += 1;
        leaf->r += p->c.r;
        leaf->g += p->c.g;
        leaf->b += p->c.b;
        leaf->a += p->c.a;
        *out_leaf = idx;
        return 1;
    }

    split_depth = first_diff_bit(code ^ trie->nodes[idx].prefix);
    branch_idx = trie_alloc_node(trie);
    if (branch_idx < 0) {
        return 0;
    }
    leaf_idx = trie_alloc_node(trie);
    if (leaf_idx < 0) {
        trie_free_node(trie, branch_idx);
        return 0;
    }

    old_parent = trie->nodes[idx].parent;
    new_bit = (code >> (31 - split_depth)) & 1;
    old_bit = 1 - new_bit;

    trie->nodes[branch_idx].prefix = mask_prefix(code, split_depth);
    trie->nodes[branch_idx].depth = split_depth;
    trie->nodes[branch_idx].is_leaf = 0;
    trie->nodes[branch_idx].parent = old_parent;
    trie->nodes[branch_idx].child[new_bit] = leaf_idx;
    trie->nodes[branch_idx].child[old_bit] = idx;

    trie->nodes[leaf_idx].prefix = code;
    trie->nodes[leaf_idx].depth = trie->max_depth;
    trie->nodes[leaf_idx].is_leaf = 1;
    trie->nodes[leaf_idx].parent = branch_idx;
    trie->nodes[leaf_idx].count = 1;
    trie->nodes[leaf_idx].r = p->c.r;
    trie->nodes[leaf_idx].g = p->c.g;
    trie->nodes[leaf_idx].b = p->c.b;
    trie->nodes[leaf_idx].a = p->c.a;

    trie->nodes[idx].parent = branch_idx;

    if (old_parent == -1) {
        trie->root = branch_idx;
    } else {
        if (trie->nodes[old_parent].child[0] == idx) {
            trie->nodes[old_parent].child[0] = branch_idx;
        } else {
            trie->nodes[old_parent].child[1] = branch_idx;
        }
        trie_remove_reducible(trie, old_parent);
    }

    if (trie->nodes[idx].is_leaf) {
        trie_add_reducible(trie, branch_idx);
    }

    trie->leaf_count++;

    if (trie->leaf_count > MAX_TRIE_LEAVES) {
        int d;
        for (d = (int)trie->max_depth - 1; d >= 0; d--) {
            if (trie->reducible_head[d] != -1) {
                trie_reduce_node(trie, trie->reducible_head[d]);
                break;
            }
        }
        *out_leaf = -1;
    } else {
        *out_leaf = leaf_idx;
    }
    return 1;
}

static int
compare_reduce_candidate(const void *a, const void *b) {
    const TrieSortEntry *ca = (const TrieSortEntry *)a;
    const TrieSortEntry *cb = (const TrieSortEntry *)b;
    if (ca->count != cb->count) {
        return ca->count < cb->count ? -1 : 1;
    }
    if (ca->prefix != cb->prefix) {
        return ca->prefix < cb->prefix ? -1 : 1;
    }
    return 0;
}

static int
compare_palette_leaf(const void *a, const void *b) {
    const TrieSortEntry *la = (const TrieSortEntry *)a;
    const TrieSortEntry *lb = (const TrieSortEntry *)b;
    if (la->count != lb->count) {
        return la->count > lb->count ? -1 : 1;
    }
    if (la->prefix != lb->prefix) {
        return la->prefix < lb->prefix ? -1 : 1;
    }
    return 0;
}

static int
trie_reduce_to(ColorTrie *trie, uint32_t target_leaves) {
    int d;
    for (d = (int)trie->max_depth - 1; d >= 0 && trie->leaf_count > target_leaves;
         d--) {
        uint32_t avail = trie->reducible_count[d];
        uint32_t need;
        if (avail == 0) {
            continue;
        }
        need = trie->leaf_count - target_leaves;
        if (avail <= need) {
            while (trie->reducible_head[d] != -1) {
                trie_reduce_node(trie, trie->reducible_head[d]);
            }
        } else {
            TrieSortEntry *cands;
            uint32_t n = 0;
            uint32_t i;
            int32_t cur;
            /* malloc check ok, avail <= MAX_TRIE_LEAVES */
            cands = malloc(avail * sizeof(TrieSortEntry));
            if (!cands) {
                return 0;
            }
            for (cur = trie->reducible_head[d]; cur != -1;
                 cur = trie->nodes[cur].next_reducible) {
                const ColorTrieNode *node = &trie->nodes[cur];
                cands[n].idx = cur;
                cands[n].count = trie->nodes[node->child[0]].count +
                                 trie->nodes[node->child[1]].count;
                cands[n].prefix = node->prefix;
                n++;
            }
            qsort(cands, n, sizeof(TrieSortEntry), compare_reduce_candidate);
            for (i = 0; i < need; i++) {
                trie_reduce_node(trie, cands[i].idx);
            }
            free(cands);
        }
    }
    return 1;
}

static int
quantize_octree_adaptive(
    const Pixel *pixelData,
    uint32_t nPixels,
    uint32_t nQuantPixels,
    Pixel **palette,
    uint32_t *paletteLength,
    uint32_t **quantizedPixels,
    int withAlpha
) {
    ColorTrie trie;
    TrieSortEntry *leaves = NULL;
    Pixel *pal = NULL;
    uint32_t *qp = NULL;
    int32_t init_cap = 256;
    int32_t stack[MAX_TRIE_DEPTH + 1];
    int top = 0;
    uint32_t i, nLeaves = 0;
    uint32_t prev_v = 0;
    int32_t prev_leaf = -1;
    uint32_t prev_pal_idx = 0;
    int has_prev = 0;

    memset(&trie, 0, sizeof(trie));
    trie.free_head = -1;
    trie.root = -1;
    trie.max_depth = withAlpha ? 32 : 24;
    for (i = 0; i < MAX_TRIE_DEPTH; i++) {
        trie.reducible_head[i] = -1;
    }

    if (nPixels < 128) {
        init_cap = (int32_t)(nPixels * 2 + 1);
        if (init_cap < 16) {
            init_cap = 16;
        }
    }
    /* malloc check ok, small bounded initial allocation */
    trie.nodes = malloc((size_t)init_cap * sizeof(ColorTrieNode));
    if (!trie.nodes) {
        goto error;
    }
    trie.capacity = init_cap;

    for (i = 0; i < nPixels; i++) {
        if (prev_leaf != -1 && pixelData[i].v == prev_v) {
            ColorTrieNode *leaf = &trie.nodes[prev_leaf];
            leaf->count += 1;
            leaf->r += pixelData[i].c.r;
            leaf->g += pixelData[i].c.g;
            leaf->b += pixelData[i].c.b;
            leaf->a += pixelData[i].c.a;
            continue;
        }
        uint32_t code = pixel_morton_code(&pixelData[i], withAlpha);
        if (!trie_insert_pixel(&trie, &pixelData[i], code, &prev_leaf)) {
            goto error;
        }
        prev_v = pixelData[i].v;
    }

    if (trie.leaf_count > nQuantPixels) {
        if (!trie_reduce_to(&trie, nQuantPixels)) {
            goto error;
        }
    }

    /* malloc check ok, leaf_count <= nQuantPixels <= 256 */
    leaves = malloc(trie.leaf_count * sizeof(TrieSortEntry));
    if (!leaves) {
        goto error;
    }

    stack[top++] = trie.root;
    while (top > 0) {
        int32_t idx = stack[--top];
        const ColorTrieNode *node = &trie.nodes[idx];
        if (node->is_leaf) {
            leaves[nLeaves].idx = idx;
            leaves[nLeaves].count = node->count;
            leaves[nLeaves].prefix = node->prefix;
            nLeaves++;
        } else {
            stack[top++] = node->child[1];
            stack[top++] = node->child[0];
        }
    }

    qsort(leaves, nLeaves, sizeof(TrieSortEntry), compare_palette_leaf);

    /* malloc check ok, calloc for overflow */
    pal = calloc(nQuantPixels, sizeof(Pixel));
    if (!pal) {
        goto error;
    }
    for (i = 0; i < nLeaves; i++) {
        ColorTrieNode *leaf = &trie.nodes[leaves[i].idx];
        uint64_t half = leaf->count / 2;
        pal[i].c.r = (unsigned char)((leaf->r + half) / leaf->count);
        pal[i].c.g = (unsigned char)((leaf->g + half) / leaf->count);
        pal[i].c.b = (unsigned char)((leaf->b + half) / leaf->count);
        pal[i].c.a = withAlpha ? (unsigned char)((leaf->a + half) / leaf->count) : 255;
        leaf->palette_index = i;
    }

    free(leaves);
    leaves = NULL;

    /* malloc check ok, calloc for overflow */
    qp = calloc(nPixels, sizeof(uint32_t));
    if (!qp) {
        goto error;
    }
    for (i = 0; i < nPixels; i++) {
        if (has_prev && pixelData[i].v == prev_v) {
            qp[i] = prev_pal_idx;
            continue;
        }
        uint32_t code = pixel_morton_code(&pixelData[i], withAlpha);
        int32_t idx = trie.root;
        while (!trie.nodes[idx].is_leaf) {
            uint8_t d = trie.nodes[idx].depth;
            idx = trie.nodes[idx].child[(code >> (31 - d)) & 1];
        }
        prev_v = pixelData[i].v;
        prev_pal_idx = trie.nodes[idx].palette_index;
        has_prev = 1;
        qp[i] = prev_pal_idx;
    }

    *palette = pal;
    *paletteLength = nQuantPixels;
    *quantizedPixels = qp;

    free(trie.nodes);
    return 1;

error:
    free(qp);
    free(pal);
    free(leaves);
    free(trie.nodes);
    return 0;
}

int
quantize_octree(
    Pixel *pixelData,
    uint32_t nPixels,
    uint32_t nQuantPixels,
    Pixel **palette,
    uint32_t *paletteLength,
    uint32_t **quantizedPixels,
    int withAlpha
) {
    ColorCube fineCube = NULL;
    ColorCube coarseCube = NULL;
    ColorCube lookupCube = NULL;
    ColorCube coarseLookupCube = NULL;
    ColorBucket paletteBucketsCoarse = NULL;
    ColorBucket paletteBucketsFine = NULL;
    ColorBucket paletteBuckets = NULL;
    uint32_t *qp = NULL;
    long i;
    unsigned long nCoarseColors, nFineColors, nAlreadySubtracted;
    const unsigned int *cubeBits;

    if (withAlpha) {
        cubeBits = CUBE_LEVELS_ALPHA;
    } else {
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
    fineCube = new_color_cube(cubeBits[0], cubeBits[1], cubeBits[2], cubeBits[3]);
    if (!fineCube) {
        goto error;
    }
    for (i = 0; i < nPixels; i++) {
        add_color_to_color_cube(fineCube, &pixelData[i]);
    }

    /* If the fixed fine cube collapses distinct colors below the requested
       palette size (e.g. RGBA images with few RGB colors and many alpha
       levels, or single-channel gradients), refine adaptively using full
       per-channel bit precision. */
    if (nPixels > 0 && !has_at_least_used_color_buckets(fineCube, nQuantPixels)) {
        free_color_cube(fineCube);
        return quantize_octree_adaptive(
            pixelData,
            nPixels,
            nQuantPixels,
            palette,
            paletteLength,
            quantizedPixels,
            withAlpha
        );
    }

    /* create coarse cube */
    coarseCube =
        copy_color_cube(fineCube, cubeBits[4], cubeBits[5], cubeBits[6], cubeBits[7]);
    if (!coarseCube) {
        goto error;
    }
    nCoarseColors = count_used_color_buckets(coarseCube);

    /* limit to nQuantPixels */
    if (nCoarseColors > nQuantPixels) {
        nCoarseColors = nQuantPixels;
    }

    /* how many space do we have in our palette for fine colors? */
    nFineColors = nQuantPixels - nCoarseColors;

    /* create fine color palette */
    paletteBucketsFine = create_sorted_color_palette(fineCube);
    if (!paletteBucketsFine) {
        goto error;
    }

    /* remove the used fine colors from the coarse cube */
    subtract_color_buckets(coarseCube, paletteBucketsFine, nFineColors);

    /* did the subtraction cleared one or more coarse bucket? */
    while (nCoarseColors > count_used_color_buckets(coarseCube)) {
        /* then we can use the free buckets for fine colors */
        nAlreadySubtracted = nFineColors;
        nCoarseColors = count_used_color_buckets(coarseCube);
        nFineColors = nQuantPixels - nCoarseColors;
        subtract_color_buckets(
            coarseCube,
            &paletteBucketsFine[nAlreadySubtracted],
            nFineColors - nAlreadySubtracted
        );
    }

    /* create our palette buckets with fine and coarse combined */
    paletteBucketsCoarse = create_sorted_color_palette(coarseCube);
    if (!paletteBucketsCoarse) {
        goto error;
    }
    paletteBuckets = combined_palette(
        paletteBucketsCoarse, nCoarseColors, paletteBucketsFine, nFineColors
    );

    free(paletteBucketsFine);
    paletteBucketsFine = NULL;
    free(paletteBucketsCoarse);
    paletteBucketsCoarse = NULL;
    if (!paletteBuckets) {
        goto error;
    }

    /* add all coarse colors to our coarse lookup cube. */
    coarseLookupCube =
        new_color_cube(cubeBits[4], cubeBits[5], cubeBits[6], cubeBits[7]);
    if (!coarseLookupCube) {
        goto error;
    }
    add_lookup_buckets(coarseLookupCube, paletteBuckets, nCoarseColors, 0);

    /* expand coarse cube (64) to larger fine cube (4k). the value of each
       coarse bucket is then present in the according 64 fine buckets. */
    lookupCube = copy_color_cube(
        coarseLookupCube, cubeBits[0], cubeBits[1], cubeBits[2], cubeBits[3]
    );
    if (!lookupCube) {
        goto error;
    }

    /* add fine colors to the lookup cube */
    add_lookup_buckets(lookupCube, paletteBuckets, nFineColors, nCoarseColors);

    /* create result pixels and map palette indices */
    /* malloc check ok, calloc for overflow */
    qp = calloc(nPixels, sizeof(Pixel));
    if (!qp) {
        goto error;
    }
    map_image_pixels(pixelData, nPixels, lookupCube, qp);

    /* convert palette buckets to RGB pixel palette */
    *palette = create_palette_array(paletteBuckets, nQuantPixels);
    if (!(*palette)) {
        goto error;
    }

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
