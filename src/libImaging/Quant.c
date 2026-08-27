/*
 * The Python Imaging Library
 * $Id$
 *
 * image quantizer
 *
 * history:
 * 1998-09-10 tjs  Contributed
 * 1998-12-29 fl   Added to PIL 1.0b1
 * 2004-02-21 fl   Fixed bogus free() on quantization error
 * 2005-02-07 fl   Limit number of colors to 256
 *
 * Written by Toby J Sargeant <tjs@longford.cs.monash.edu.au>.
 *
 * Copyright (c) 1998 by Toby J Sargeant
 * Copyright (c) 1998-2004 by Secret Labs AB.  All rights reserved.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include <stdlib.h>

#include "QuantTypes.h"
#include "QuantOctree.h"
#include "QuantPngQuant.h"
#include "QuantHash.h"
#include "QuantHeap.h"

/* MSVC9.0 */
#ifndef UINT32_MAX
#define UINT32_MAX 0xffffffff
#endif

typedef struct {
    uint32_t scale;
} PixelHashData;

typedef struct _PixelList {
    struct _PixelList *next[3], *prev[3];
    Pixel p;
    unsigned int flag : 1;
    int count;
} PixelList;

typedef struct _BoxNode {
    struct _BoxNode *l, *r;
    PixelList *head[3], *tail[3];
    int axis;
    int volume;
    uint32_t pixelCount;
} BoxNode;

#define _SQR(x) ((x) * (x))
#define _DISTSQR(p1, p2)                            \
    _SQR((int)((p1)->c.r) - (int)((p2)->c.r)) +     \
        _SQR((int)((p1)->c.g) - (int)((p2)->c.g)) + \
        _SQR((int)((p1)->c.b) - (int)((p2)->c.b))

#define MAX_HASH_ENTRIES 65536

#define PIXEL_HASH(r, g, b)                                         \
    (((unsigned int)(r)) * 463 ^ ((unsigned int)(g) << 8) * 10069 ^ \
     ((unsigned int)(b) << 16) * 64997)

#define PIXEL_UNSCALE(p, q, s)                                  \
    ((q)->c.r = (p)->c.r << (s)), ((q)->c.g = (p)->c.g << (s)), \
        ((q)->c.b = (p)->c.b << (s))

#define PIXEL_SCALE(p, q, s)                                    \
    ((q)->c.r = (p)->c.r >> (s)), ((q)->c.g = (p)->c.g >> (s)), \
        ((q)->c.b = (p)->c.b >> (s))

static uint32_t
unshifted_pixel_hash(const HashTable *h, const Pixel pixel) {
    return PIXEL_HASH(pixel.c.r, pixel.c.g, pixel.c.b);
}

static int
unshifted_pixel_cmp(const HashTable *h, const Pixel pixel1, const Pixel pixel2) {
    if (pixel1.c.r == pixel2.c.r) {
        if (pixel1.c.g == pixel2.c.g) {
            if (pixel1.c.b == pixel2.c.b) {
                return 0;
            } else {
                return (int)(pixel1.c.b) - (int)(pixel2.c.b);
            }
        } else {
            return (int)(pixel1.c.g) - (int)(pixel2.c.g);
        }
    } else {
        return (int)(pixel1.c.r) - (int)(pixel2.c.r);
    }
}

static uint32_t
pixel_hash(const HashTable *h, const Pixel pixel) {
    PixelHashData *d = (PixelHashData *)hashtable_get_user_data(h);
    return PIXEL_HASH(
        pixel.c.r >> d->scale, pixel.c.g >> d->scale, pixel.c.b >> d->scale
    );
}

static int
pixel_cmp(const HashTable *h, const Pixel pixel1, const Pixel pixel2) {
    PixelHashData *d = (PixelHashData *)hashtable_get_user_data(h);
    uint32_t A, B;
    A = PIXEL_HASH(
        pixel1.c.r >> d->scale, pixel1.c.g >> d->scale, pixel1.c.b >> d->scale
    );
    B = PIXEL_HASH(
        pixel2.c.r >> d->scale, pixel2.c.g >> d->scale, pixel2.c.b >> d->scale
    );
    return (A == B) ? 0 : ((A < B) ? -1 : 1);
}

static void
exists_count_func(const HashTable *h, const Pixel key, uint32_t *val) {
    *val += 1;
}

static void
new_count_func(const HashTable *h, const Pixel key, uint32_t *val) {
    *val = 1;
}

static void
rehash_collide(
    const HashTable *h, Pixel *keyp, uint32_t *valp, Pixel newkey, uint32_t newval
) {
    *valp += newval;
}

/* %% */

static HashTable *
create_pixel_hash(Pixel *pixelData, uint32_t nPixels) {
    PixelHashData *d;
    HashTable *hash;
    uint32_t i;

    /* malloc check ok, small constant allocation */
    d = malloc(sizeof(PixelHashData));
    if (!d) {
        return NULL;
    }
    hash = hashtable_new(pixel_hash, pixel_cmp);
    hashtable_set_user_data(hash, d);
    d->scale = 0;
    for (i = 0; i < nPixels; i++) {
        if (!hashtable_insert_or_update_computed(
                hash, pixelData[i], new_count_func, exists_count_func
            )) {
            ;
        }
        while (hashtable_get_count(hash) > MAX_HASH_ENTRIES) {
            d->scale++;
            hashtable_rehash_compute(hash, rehash_collide);
        }
    }
    return hash;
}

static void
destroy_pixel_hash(HashTable *hash) {
    PixelHashData *d = (PixelHashData *)hashtable_get_user_data(hash);
    if (d) {
        free(d);
    }
    hashtable_free(hash);
}

/* 1. hash quantized pixels.                                                  */
/* 2. create R,G,B lists of sorted quantized pixels.                          */
/* 3. median cut.                                                             */
/* 4. build hash table from median cut boxes.                                 */
/* 5. for each pixel, compute entry in hash table, and hence median cut box.  */
/* 6. compute median cut box pixel averages.                                  */
/* 7. map each pixel to nearest average.                                      */

static int
compute_box_volume(BoxNode *b) {
    unsigned char rl, rh, gl, gh, bl, bh;
    if (b->volume >= 0) {
        return b->volume;
    }
    if (!b->head[0]) {
        b->volume = 0;
    } else {
        rh = b->head[0]->p.c.r;
        rl = b->tail[0]->p.c.r;
        gh = b->head[1]->p.c.g;
        gl = b->tail[1]->p.c.g;
        bh = b->head[2]->p.c.b;
        bl = b->tail[2]->p.c.b;
        b->volume = (rh - rl + 1) * (gh - gl + 1) * (bh - bl + 1);
    }
    return b->volume;
}

static void
hash_to_list(const HashTable *h, const Pixel pixel, const uint32_t count, void *u) {
    PixelHashData *d = (PixelHashData *)hashtable_get_user_data(h);
    PixelList **pl = (PixelList **)u;
    PixelList *p;
    int i;
    Pixel q;

    PIXEL_SCALE(&pixel, &q, d->scale);

    /* malloc check ok, small constant allocation */
    p = malloc(sizeof(PixelList));
    if (!p) {
        return;
    }

    p->flag = 0;
    p->p = q;
    p->count = count;
    for (i = 0; i < 3; i++) {
        p->next[i] = pl[i];
        p->prev[i] = NULL;
        if (pl[i]) {
            pl[i]->prev[i] = p;
        }
        pl[i] = p;
    }
}

static PixelList *
mergesort_pixels(PixelList *head, int i) {
    PixelList *c, *t, *a, *b, *p;
    if (!head || !head->next[i]) {
        if (head) {
            head->next[i] = NULL;
            head->prev[i] = NULL;
        }
        return head;
    }
    for (c = t = head; c && t;
         c = c->next[i], t = (t->next[i]) ? t->next[i]->next[i] : NULL);
    if (c) {
        if (c->prev[i]) {
            c->prev[i]->next[i] = NULL;
        }
        c->prev[i] = NULL;
    }
    a = mergesort_pixels(head, i);
    b = mergesort_pixels(c, i);
    head = NULL;
    p = NULL;
    while (a && b) {
        if (a->p.a.v[i] > b->p.a.v[i]) {
            c = a;
            a = a->next[i];
        } else {
            c = b;
            b = b->next[i];
        }
        c->prev[i] = p;
        c->next[i] = NULL;
        if (p) {
            p->next[i] = c;
        }
        p = c;
        if (!head) {
            head = c;
        }
    }
    if (a) {
        c->next[i] = a;
        a->prev[i] = c;
    } else if (b) {
        c->next[i] = b;
        b->prev[i] = c;
    }
    return head;
}

static int
box_heap_cmp(const Heap *h, const void *A, const void *B) {
    BoxNode *a = (BoxNode *)A;
    BoxNode *b = (BoxNode *)B;
    return (int)a->pixelCount - (int)b->pixelCount;
}

#define LUMINANCE(p) (77 * (p)->c.r + 150 * (p)->c.g + 29 * (p)->c.b)

static int
splitlists(
    PixelList *h[3],
    PixelList *t[3],
    PixelList *nh[2][3],
    PixelList *nt[2][3],
    uint32_t nCount[2],
    int axis,
    uint32_t pixelCount
) {
    uint32_t left;

    PixelList *l, *r, *c, *n;
    int i;
    int nRight;
    int splitColourVal;

    nCount[0] = nCount[1] = 0;
    nRight = 0;
    for (left = 0, c = h[axis]; c;) {
        left = left + c->count;
        nCount[0] += c->count;
        c->flag = 0;
        c = c->next[axis];
        if (left * 2 > pixelCount) {
            break;
        }
    }
    if (c) {
        splitColourVal = c->prev[axis]->p.a.v[axis];
        for (; c; c = c->next[axis]) {
            if (splitColourVal != c->p.a.v[axis]) {
                break;
            }
            c->flag = 0;
            nCount[0] += c->count;
        }
    }
    for (; c; c = c->next[axis]) {
        c->flag = 1;
        nRight++;
        nCount[1] += c->count;
    }
    if (!nRight) {
        for (c = t[axis], splitColourVal = t[axis]->p.a.v[axis]; c; c = c->prev[axis]) {
            if (splitColourVal != c->p.a.v[axis]) {
                break;
            }
            c->flag = 1;
            nRight++;
            nCount[0] -= c->count;
            nCount[1] += c->count;
        }
    }

    for (i = 0; i < 3; i++) {
        l = r = NULL;
        nh[0][i] = nt[0][i] = NULL;
        nh[1][i] = nt[1][i] = NULL;
        for (c = h[i]; c; c = n) {
            n = c->next[i];
            if (c->flag) { /* move pixel to right  list*/
                if (r) {
                    r->next[i] = c;
                } else {
                    nh[1][i] = c;
                }
                c->prev[i] = r;
                r = c;
            } else { /* move pixel to left list */
                if (l) {
                    l->next[i] = c;
                } else {
                    nh[0][i] = c;
                }
                c->prev[i] = l;
                l = c;
            }
        }
        if (l) {
            l->next[i] = NULL;
        }
        if (r) {
            r->next[i] = NULL;
        }
        nt[0][i] = l;
        nt[1][i] = r;
    }
    return 1;
}

static int
split(BoxNode *node) {
    unsigned char rl, rh, gl, gh, bl, bh;
    int f[3];
    int best, axis;
    int i;
    PixelList *heads[2][3];
    PixelList *tails[2][3];
    uint32_t newCounts[2];
    BoxNode *left, *right;

    rh = node->head[0]->p.c.r;
    rl = node->tail[0]->p.c.r;
    gh = node->head[1]->p.c.g;
    gl = node->tail[1]->p.c.g;
    bh = node->head[2]->p.c.b;
    bl = node->tail[2]->p.c.b;
    f[0] = (rh - rl) * 77;
    f[1] = (gh - gl) * 150;
    f[2] = (bh - bl) * 29;

    best = f[0];
    axis = 0;
    for (i = 1; i < 3; i++) {
        if (best < f[i]) {
            best = f[i];
            axis = i;
        }
    }
    node->axis = axis;
    if (!splitlists(
            node->head, node->tail, heads, tails, newCounts, axis, node->pixelCount
        )) {
        return 0;
    }
    /* malloc check ok, small constant allocation */
    left = malloc(sizeof(BoxNode));
    right = malloc(sizeof(BoxNode));
    if (!left || !right) {
        free(left);
        free(right);
        return 0;
    }
    for (i = 0; i < 3; i++) {
        left->head[i] = heads[0][i];
        left->tail[i] = tails[0][i];
        right->head[i] = heads[1][i];
        right->tail[i] = tails[1][i];
        node->head[i] = NULL;
        node->tail[i] = NULL;
    }
    left->l = left->r = NULL;
    right->l = right->r = NULL;
    left->axis = right->axis = -1;
    left->volume = right->volume = -1;
    left->pixelCount = newCounts[0];
    right->pixelCount = newCounts[1];
    node->l = left;
    node->r = right;
    return 1;
}

static BoxNode *
median_cut(PixelList *hl[3], uint32_t imPixelCount, int nPixels) {
    PixelList *tl[3];
    int i;
    BoxNode *root;
    Heap *h;
    BoxNode *thisNode;

    h = ImagingQuantHeapNew(box_heap_cmp);
    /* malloc check ok, small constant allocation */
    root = malloc(sizeof(BoxNode));
    if (!root) {
        ImagingQuantHeapFree(h);
        return NULL;
    }
    for (i = 0; i < 3; i++) {
        for (tl[i] = hl[i]; tl[i] && tl[i]->next[i]; tl[i] = tl[i]->next[i]);
        root->head[i] = hl[i];
        root->tail[i] = tl[i];
    }
    root->l = root->r = NULL;
    root->axis = -1;
    root->volume = -1;
    root->pixelCount = imPixelCount;

    ImagingQuantHeapAdd(h, (void *)root);
    while (--nPixels) {
        do {
            if (!ImagingQuantHeapRemove(h, (void **)&thisNode)) {
                goto done;
            }
        } while (compute_box_volume(thisNode) == 1);
        if (!split(thisNode)) {
            ImagingQuantHeapFree(h);
            return NULL;
        }
        ImagingQuantHeapAdd(h, (void *)(thisNode->l));
        ImagingQuantHeapAdd(h, (void *)(thisNode->r));
    }
done:
    ImagingQuantHeapFree(h);
    return root;
}

static void
free_box_tree(BoxNode *n) {
    PixelList *p, *pp;
    if (n->l) {
        free_box_tree(n->l);
    }
    if (n->r) {
        free_box_tree(n->r);
    }
    for (p = n->head[0]; p; p = pp) {
        pp = p->next[0];
        free(p);
    }
    free(n);
}

static int
annotate_hash_table(BoxNode *n, HashTable *h, uint32_t *box) {
    PixelList *p;
    PixelHashData *d = (PixelHashData *)hashtable_get_user_data(h);
    Pixel q;
    if (n->l && n->r) {
        return annotate_hash_table(n->l, h, box) && annotate_hash_table(n->r, h, box);
    }
    if (n->l || n->r) {
        return 0;
    }
    for (p = n->head[0]; p; p = p->next[0]) {
        PIXEL_UNSCALE(&(p->p), &q, d->scale);
        if (!hashtable_insert(h, q, *box)) {
            return 0;
        }
    }
    if (n->head[0]) {
        (*box)++;
    }
    return 1;
}

typedef struct {
    uint32_t *distance;
    uint32_t index;
} DistanceWithIndex;

static int
_distance_index_cmp(const void *a, const void *b) {
    DistanceWithIndex *A = (DistanceWithIndex *)a;
    DistanceWithIndex *B = (DistanceWithIndex *)b;
    if (*A->distance == *B->distance) {
        return A->index < B->index ? -1 : +1;
    }
    return *A->distance < *B->distance ? -1 : +1;
}

static int
resort_distance_tables(
    uint32_t *avgDist, uint32_t **avgDistSortKey, Pixel *p, uint32_t nEntries
) {
    uint32_t i, j, k;
    uint32_t **skRow;
    uint32_t *skElt;

    for (i = 0; i < nEntries; i++) {
        avgDist[i * nEntries + i] = 0;
        for (j = 0; j < i; j++) {
            avgDist[j * nEntries + i] = avgDist[i * nEntries + j] =
                _DISTSQR(p + i, p + j);
        }
    }
    for (i = 0; i < nEntries; i++) {
        skRow = avgDistSortKey + i * nEntries;
        for (j = 1; j < nEntries; j++) {
            skElt = skRow[j];
            for (k = j; k && (*(skRow[k - 1]) > *(skRow[k])); k--) {
                skRow[k] = skRow[k - 1];
            }
            if (k != j) {
                skRow[k] = skElt;
            }
        }
    }
    return 1;
}

static int
build_distance_tables(
    uint32_t *avgDist, uint32_t **avgDistSortKey, Pixel *p, uint32_t nEntries
) {
    uint32_t i, j;
    DistanceWithIndex *dwi;

    for (i = 0; i < nEntries; i++) {
        avgDist[i * nEntries + i] = 0;
        avgDistSortKey[i * nEntries + i] = &(avgDist[i * nEntries + i]);
        for (j = 0; j < i; j++) {
            avgDist[j * nEntries + i] = avgDist[i * nEntries + j] =
                _DISTSQR(p + i, p + j);
            avgDistSortKey[j * nEntries + i] = &(avgDist[j * nEntries + i]);
            avgDistSortKey[i * nEntries + j] = &(avgDist[i * nEntries + j]);
        }
    }

    dwi = calloc(nEntries, sizeof(DistanceWithIndex));
    if (!dwi) {
        return 0;
    }
    for (i = 0; i < nEntries; i++) {
        for (j = 0; j < nEntries; j++) {
            dwi[j] = (DistanceWithIndex){&(avgDist[i * nEntries + j]), j};
        }
        qsort(dwi, nEntries, sizeof(DistanceWithIndex), _distance_index_cmp);
        for (j = 0; j < nEntries; j++) {
            avgDistSortKey[i * nEntries + j] = dwi[j].distance;
        }
    }
    free(dwi);
    return 1;
}

static int
map_image_pixels(
    Pixel *pixelData,
    uint32_t nPixels,
    Pixel *paletteData,
    uint32_t nPaletteEntries,
    uint32_t *avgDist,
    uint32_t **avgDistSortKey,
    uint32_t *pixelArray
) {
    uint32_t *aD, **aDSK;
    uint32_t idx;
    uint32_t i, j;
    uint32_t bestdist, bestmatch, dist;
    uint32_t initialdist;
    HashTable *h2;

    h2 = hashtable_new(unshifted_pixel_hash, unshifted_pixel_cmp);
    for (i = 0; i < nPixels; i++) {
        if (!hashtable_lookup(h2, pixelData[i], &bestmatch)) {
            bestmatch = 0;
            initialdist = _DISTSQR(paletteData + bestmatch, pixelData + i);
            bestdist = initialdist;
            initialdist <<= 2;
            aDSK = avgDistSortKey + bestmatch * nPaletteEntries;
            aD = avgDist + bestmatch * nPaletteEntries;
            for (j = 0; j < nPaletteEntries; j++) {
                idx = aDSK[j] - aD;
                if (*(aDSK[j]) <= initialdist) {
                    dist = _DISTSQR(paletteData + idx, pixelData + i);
                    if (dist < bestdist) {
                        bestdist = dist;
                        bestmatch = idx;
                    }
                } else {
                    break;
                }
            }
            hashtable_insert(h2, pixelData[i], bestmatch);
        }
        pixelArray[i] = bestmatch;
    }
    hashtable_free(h2);
    return 1;
}

static int
map_image_pixels_from_quantized_pixels(
    Pixel *pixelData,
    uint32_t nPixels,
    Pixel *paletteData,
    uint32_t nPaletteEntries,
    uint32_t *avgDist,
    uint32_t **avgDistSortKey,
    uint32_t *pixelArray,
    uint32_t *avg[3],
    uint32_t *count
) {
    uint32_t *aD, **aDSK;
    uint32_t idx;
    uint32_t i, j;
    uint32_t bestdist, bestmatch, dist;
    uint32_t initialdist;
    HashTable *h2;
    int changes = 0;

    h2 = hashtable_new(unshifted_pixel_hash, unshifted_pixel_cmp);
    for (i = 0; i < nPixels; i++) {
        if (!hashtable_lookup(h2, pixelData[i], &bestmatch)) {
            bestmatch = pixelArray[i];
            initialdist = _DISTSQR(paletteData + bestmatch, pixelData + i);
            bestdist = initialdist;
            initialdist <<= 2;
            aDSK = avgDistSortKey + bestmatch * nPaletteEntries;
            aD = avgDist + bestmatch * nPaletteEntries;
            for (j = 0; j < nPaletteEntries; j++) {
                idx = aDSK[j] - aD;
                if (*(aDSK[j]) <= initialdist) {
                    dist = _DISTSQR(paletteData + idx, pixelData + i);
                    if (dist < bestdist) {
                        bestdist = dist;
                        bestmatch = idx;
                    }
                } else {
                    break;
                }
            }
            hashtable_insert(h2, pixelData[i], bestmatch);
        }
        if (pixelArray[i] != bestmatch) {
            changes++;
            avg[0][bestmatch] += pixelData[i].c.r;
            avg[1][bestmatch] += pixelData[i].c.g;
            avg[2][bestmatch] += pixelData[i].c.b;
            avg[0][pixelArray[i]] -= pixelData[i].c.r;
            avg[1][pixelArray[i]] -= pixelData[i].c.g;
            avg[2][pixelArray[i]] -= pixelData[i].c.b;
            count[bestmatch]++;
            count[pixelArray[i]]--;
            pixelArray[i] = bestmatch;
        }
    }
    hashtable_free(h2);
    return changes;
}

static int
map_image_pixels_from_median_box(
    Pixel *pixelData,
    uint32_t nPixels,
    Pixel *paletteData,
    uint32_t nPaletteEntries,
    HashTable *medianBoxHash,
    uint32_t *avgDist,
    uint32_t **avgDistSortKey,
    uint32_t *pixelArray
) {
    uint32_t *aD, **aDSK;
    uint32_t idx;
    uint32_t i, j;
    uint32_t bestdist, bestmatch, dist;
    uint32_t initialdist;
    HashTable *h2;
    uint32_t pixelVal;

    h2 = hashtable_new(unshifted_pixel_hash, unshifted_pixel_cmp);
    for (i = 0; i < nPixels; i++) {
        if (hashtable_lookup(h2, pixelData[i], &pixelVal)) {
            pixelArray[i] = pixelVal;
            continue;
        }
        if (!hashtable_lookup(medianBoxHash, pixelData[i], &pixelVal)) {
            return 0;
        }
        initialdist = _DISTSQR(paletteData + pixelVal, pixelData + i);
        bestdist = initialdist;
        bestmatch = pixelVal;
        initialdist <<= 2;
        aDSK = avgDistSortKey + pixelVal * nPaletteEntries;
        aD = avgDist + pixelVal * nPaletteEntries;
        for (j = 0; j < nPaletteEntries; j++) {
            idx = aDSK[j] - aD;
            if (*(aDSK[j]) <= initialdist) {
                dist = _DISTSQR(paletteData + idx, pixelData + i);
                if (dist < bestdist) {
                    bestdist = dist;
                    bestmatch = idx;
                }
            } else {
                break;
            }
        }
        pixelArray[i] = bestmatch;
        hashtable_insert(h2, pixelData[i], bestmatch);
    }
    hashtable_free(h2);
    return 1;
}

static int
compute_palette_from_median_cut(
    Pixel *pixelData,
    uint32_t nPixels,
    HashTable *medianBoxHash,
    Pixel **palette,
    uint32_t nPaletteEntries,
    BoxNode *root
) {
    uint32_t i;
    uint32_t paletteEntry;
    Pixel *p;
    uint32_t *avg[3];
    uint32_t *count;

    *palette = NULL;
    /* malloc check ok, using calloc */
    if (!(count = calloc(nPaletteEntries, sizeof(uint32_t)))) {
        return 0;
    }
    for (i = 0; i < 3; i++) {
        avg[i] = NULL;
    }
    for (i = 0; i < 3; i++) {
        /* malloc check ok, using calloc */
        if (!(avg[i] = calloc(nPaletteEntries, sizeof(uint32_t)))) {
            for (i = 0; i < 3; i++) {
                if (avg[i]) {
                    free(avg[i]);
                }
            }
            free(count);
            return 0;
        }
    }
    for (i = 0; i < nPixels; i++) {
        if (!hashtable_lookup(medianBoxHash, pixelData[i], &paletteEntry)) {
            for (i = 0; i < 3; i++) {
                free(avg[i]);
            }
            free(count);
            return 0;
        }
        if (paletteEntry >= nPaletteEntries) {
            for (i = 0; i < 3; i++) {
                free(avg[i]);
            }
            free(count);
            return 0;
        }
        avg[0][paletteEntry] += pixelData[i].c.r;
        avg[1][paletteEntry] += pixelData[i].c.g;
        avg[2][paletteEntry] += pixelData[i].c.b;
        count[paletteEntry]++;
    }
    /* malloc check ok, using calloc */
    p = calloc(nPaletteEntries, sizeof(Pixel));
    if (!p) {
        for (i = 0; i < 3; i++) {
            free(avg[i]);
        }
        free(count);
        return 0;
    }
    for (i = 0; i < nPaletteEntries; i++) {
        p[i].c.r = (int)(.5 + (double)avg[0][i] / (double)count[i]);
        p[i].c.g = (int)(.5 + (double)avg[1][i] / (double)count[i]);
        p[i].c.b = (int)(.5 + (double)avg[2][i] / (double)count[i]);
    }
    *palette = p;
    for (i = 0; i < 3; i++) {
        free(avg[i]);
    }
    free(count);
    return 1;
}

static int
recompute_palette_from_averages(
    Pixel *palette, uint32_t nPaletteEntries, uint32_t *avg[3], uint32_t *count
) {
    uint32_t i;

    for (i = 0; i < nPaletteEntries; i++) {
        palette[i].c.r = (int)(.5 + (double)avg[0][i] / (double)count[i]);
        palette[i].c.g = (int)(.5 + (double)avg[1][i] / (double)count[i]);
        palette[i].c.b = (int)(.5 + (double)avg[2][i] / (double)count[i]);
    }
    return 1;
}

static int
compute_palette_from_quantized_pixels(
    Pixel *pixelData,
    uint32_t nPixels,
    Pixel *palette,
    uint32_t nPaletteEntries,
    uint32_t *avg[3],
    uint32_t *count,
    uint32_t *qp
) {
    uint32_t i;

    memset(count, 0, sizeof(uint32_t) * nPaletteEntries);
    for (i = 0; i < 3; i++) {
        memset(avg[i], 0, sizeof(uint32_t) * nPaletteEntries);
    }
    for (i = 0; i < nPixels; i++) {
        if (qp[i] >= nPaletteEntries) {
            return 0;
        }
        avg[0][qp[i]] += pixelData[i].c.r;
        avg[1][qp[i]] += pixelData[i].c.g;
        avg[2][qp[i]] += pixelData[i].c.b;
        count[qp[i]]++;
    }
    for (i = 0; i < nPaletteEntries; i++) {
        palette[i].c.r = (int)(.5 + (double)avg[0][i] / (double)count[i]);
        palette[i].c.g = (int)(.5 + (double)avg[1][i] / (double)count[i]);
        palette[i].c.b = (int)(.5 + (double)avg[2][i] / (double)count[i]);
    }
    return 1;
}

static int
k_means(
    Pixel *pixelData,
    uint32_t nPixels,
    Pixel *paletteData,
    uint32_t nPaletteEntries,
    uint32_t *qp,
    int threshold
) {
    uint32_t *avg[3];
    uint32_t *count;
    uint32_t i;
    uint32_t *avgDist;
    uint32_t **avgDistSortKey;
    int changes;
    int built = 0;

    if (nPaletteEntries > UINT32_MAX / (sizeof(uint32_t))) {
        return 0;
    }
    /* malloc check ok, using calloc */
    if (!(count = calloc(nPaletteEntries, sizeof(uint32_t)))) {
        return 0;
    }
    for (i = 0; i < 3; i++) {
        avg[i] = NULL;
    }
    for (i = 0; i < 3; i++) {
        /* malloc check ok, using calloc */
        if (!(avg[i] = calloc(nPaletteEntries, sizeof(uint32_t)))) {
            goto error_1;
        }
    }

    /* this is enough of a check, since the multiplication n*size is done above */
    if (nPaletteEntries > UINT32_MAX / nPaletteEntries) {
        goto error_1;
    }
    /* malloc check ok, using calloc, checking n*n above */
    avgDist = calloc(nPaletteEntries * nPaletteEntries, sizeof(uint32_t));
    if (!avgDist) {
        goto error_1;
    }

    /* malloc check ok, using calloc, checking n*n above */
    avgDistSortKey = calloc(nPaletteEntries * nPaletteEntries, sizeof(uint32_t *));
    if (!avgDistSortKey) {
        goto error_2;
    }

    while (1) {
        if (!built) {
            compute_palette_from_quantized_pixels(
                pixelData, nPixels, paletteData, nPaletteEntries, avg, count, qp
            );
            if (!build_distance_tables(
                    avgDist, avgDistSortKey, paletteData, nPaletteEntries
                )) {
                goto error_3;
            }
            built = 1;
        } else {
            recompute_palette_from_averages(paletteData, nPaletteEntries, avg, count);
            resort_distance_tables(
                avgDist, avgDistSortKey, paletteData, nPaletteEntries
            );
        }
        changes = map_image_pixels_from_quantized_pixels(
            pixelData,
            nPixels,
            paletteData,
            nPaletteEntries,
            avgDist,
            avgDistSortKey,
            qp,
            avg,
            count
        );
        if (changes < 0) {
            goto error_3;
        }
        if (changes <= threshold) {
            break;
        }
    }
    if (avgDistSortKey) {
        free(avgDistSortKey);
    }
    if (avgDist) {
        free(avgDist);
    }
    for (i = 0; i < 3; i++) {
        if (avg[i]) {
            free(avg[i]);
        }
    }
    if (count) {
        free(count);
    }
    return 1;

error_3:
    if (avgDistSortKey) {
        free(avgDistSortKey);
    }
error_2:
    if (avgDist) {
        free(avgDist);
    }
error_1:
    for (i = 0; i < 3; i++) {
        if (avg[i]) {
            free(avg[i]);
        }
    }
    if (count) {
        free(count);
    }
    return 0;
}

static int
quantize(
    Pixel *pixelData,
    uint32_t nPixels,
    uint32_t nQuantPixels,
    Pixel **palette,
    uint32_t *paletteLength,
    uint32_t **quantizedPixels,
    int kmeans
) {
    PixelList *hl[3];
    HashTable *h;
    BoxNode *root;
    uint32_t i;
    uint32_t *qp;
    uint32_t nPaletteEntries;

    uint32_t *avgDist;
    uint32_t **avgDistSortKey;
    Pixel *p;

    h = create_pixel_hash(pixelData, nPixels);
    if (!h) {
        goto error_0;
    }

    hl[0] = hl[1] = hl[2] = NULL;
    hashtable_foreach(h, hash_to_list, hl);

    if (!hl[0]) {
        goto error_1;
    }

    for (i = 0; i < 3; i++) {
        hl[i] = mergesort_pixels(hl[i], i);
    }
    root = median_cut(hl, nPixels, nQuantPixels);
    if (!root) {
        goto error_1;
    }
    nPaletteEntries = 0;
    if (!annotate_hash_table(root, h, &nPaletteEntries)) {
        goto error_3;
    }
    if (!compute_palette_from_median_cut(
            pixelData, nPixels, h, &p, nPaletteEntries, root
        )) {
        goto error_3;
    }

    free_box_tree(root);
    root = NULL;

    /* malloc check ok, using calloc for overflow */
    qp = calloc(nPixels, sizeof(uint32_t));
    if (!qp) {
        goto error_4;
    }

    if (nPaletteEntries > UINT32_MAX / nPaletteEntries) {
        goto error_5;
    }
    /* malloc check ok, using calloc for overflow, check of n*n above */
    avgDist = calloc(nPaletteEntries * nPaletteEntries, sizeof(uint32_t));
    if (!avgDist) {
        goto error_5;
    }

    /* malloc check ok, using calloc for overflow, check of n*n above */
    avgDistSortKey = calloc(nPaletteEntries * nPaletteEntries, sizeof(uint32_t *));
    if (!avgDistSortKey) {
        goto error_6;
    }

    if (!build_distance_tables(avgDist, avgDistSortKey, p, nPaletteEntries)) {
        goto error_7;
    }

    if (!map_image_pixels_from_median_box(
            pixelData, nPixels, p, nPaletteEntries, h, avgDist, avgDistSortKey, qp
        )) {
        goto error_7;
    }

    if (kmeans > 0) {
        k_means(pixelData, nPixels, p, nPaletteEntries, qp, kmeans - 1);
    }

    *quantizedPixels = qp;
    *palette = p;
    *paletteLength = nPaletteEntries;

    if (avgDist) {
        free(avgDist);
    }
    if (avgDistSortKey) {
        free(avgDistSortKey);
    }
    destroy_pixel_hash(h);
    return 1;

error_7:
    if (avgDistSortKey) {
        free(avgDistSortKey);
    }
error_6:
    if (avgDist) {
        free(avgDist);
    }
error_5:
    if (qp) {
        free(qp);
    }
error_4:
    if (p) {
        free(p);
    }
error_3:
    if (root) {
        free_box_tree(root);
    }
error_1:
    destroy_pixel_hash(h);
error_0:
    *quantizedPixels = NULL;
    *paletteLength = 0;
    *palette = NULL;
    return 0;
}

typedef struct {
    Pixel new;
    uint32_t furthestV;
    uint32_t furthestDistance;
    int secondPixel;
} DistanceData;

static void
compute_distances(const HashTable *h, const Pixel pixel, uint32_t *dist, void *u) {
    DistanceData *data = (DistanceData *)u;
    uint32_t oldDist = *dist;
    uint32_t newDist;
    newDist = _DISTSQR(&(data->new), &pixel);
    if (data->secondPixel || newDist < oldDist) {
        *dist = newDist;
        oldDist = newDist;
    }
    if (oldDist > data->furthestDistance) {
        data->furthestDistance = oldDist;
        data->furthestV = pixel.v;
    }
}

static int
quantize2(
    Pixel *pixelData,
    uint32_t nPixels,
    uint32_t nQuantPixels,
    Pixel **palette,
    uint32_t *paletteLength,
    uint32_t **quantizedPixels,
    int kmeans
) {
    HashTable *h;
    uint32_t i;
    uint32_t mean[3];
    Pixel *p;
    DistanceData data;

    uint32_t *qp;
    uint32_t *avgDist;
    uint32_t **avgDistSortKey;

    /* malloc check ok, using calloc */
    p = calloc(nQuantPixels, sizeof(Pixel));
    if (!p) {
        return 0;
    }
    mean[0] = mean[1] = mean[2] = 0;
    h = hashtable_new(unshifted_pixel_hash, unshifted_pixel_cmp);
    for (i = 0; i < nPixels; i++) {
        hashtable_insert(h, pixelData[i], 0xffffffff);
        mean[0] += pixelData[i].c.r;
        mean[1] += pixelData[i].c.g;
        mean[2] += pixelData[i].c.b;
    }
    data.new.c.r = (int)(.5 + (double)mean[0] / (double)nPixels);
    data.new.c.g = (int)(.5 + (double)mean[1] / (double)nPixels);
    data.new.c.b = (int)(.5 + (double)mean[2] / (double)nPixels);
    for (i = 0; i < nQuantPixels; i++) {
        data.furthestDistance = 0;
        data.furthestV = pixelData[0].v;
        data.secondPixel = (i == 1) ? 1 : 0;
        hashtable_foreach_update(h, compute_distances, &data);
        p[i].v = data.furthestV;
        data.new.v = data.furthestV;
    }
    hashtable_free(h);

    /* malloc check ok, using calloc */
    qp = calloc(nPixels, sizeof(uint32_t));
    if (!qp) {
        goto error_1;
    }

    if (nQuantPixels > UINT32_MAX / nQuantPixels) {
        goto error_2;
    }

    /* malloc check ok, using calloc for overflow, check of n*n above */
    avgDist = calloc(nQuantPixels * nQuantPixels, sizeof(uint32_t));
    if (!avgDist) {
        goto error_2;
    }

    /* malloc check ok, using calloc for overflow, check of n*n above */
    avgDistSortKey = calloc(nQuantPixels * nQuantPixels, sizeof(uint32_t *));
    if (!avgDistSortKey) {
        goto error_3;
    }

    if (!build_distance_tables(avgDist, avgDistSortKey, p, nQuantPixels)) {
        goto error_4;
    }

    if (!map_image_pixels(
            pixelData, nPixels, p, nQuantPixels, avgDist, avgDistSortKey, qp
        )) {
        goto error_4;
    }
    if (kmeans > 0) {
        k_means(pixelData, nPixels, p, nQuantPixels, qp, kmeans - 1);
    }

    *paletteLength = nQuantPixels;
    *palette = p;
    *quantizedPixels = qp;
    free(avgDistSortKey);
    free(avgDist);
    return 1;

error_4:
    free(avgDistSortKey);
error_3:
    free(avgDist);
error_2:
    free(qp);
error_1:
    free(p);
    return 0;
}

Imaging
ImagingQuantize(Imaging im, int colors, int mode, int kmeans) {
    int i, j;
    int x, y, v;
    UINT8 *pp;
    Pixel *p;
    Pixel *palette;
    uint32_t paletteLength;
    int result;
    uint32_t *newData;
    Imaging imOut;
    int withAlpha = 0;
    ImagingSectionCookie cookie;

    if (!im) {
        return ImagingError_ModeError();
    }
    if (colors < 1 || colors > 256) {
        /* FIXME: for colors > 256, consider returning an RGB image
           instead (see @PIL205) */
        return (Imaging)ImagingError_ValueError("bad number of colors");
    }

    if (im->mode != IMAGING_MODE_L && im->mode != IMAGING_MODE_P &&
        im->mode != IMAGING_MODE_RGB && im->mode != IMAGING_MODE_RGBA) {
        return ImagingError_ModeError();
    }

    /* only octree and imagequant supports RGBA */
    if (im->mode == IMAGING_MODE_RGBA && mode != 2 && mode != 3) {
        return ImagingError_ModeError();
    }

    // Hoisted here as these are invariant over the loops below.
    int xsize = im->xsize, ysize = im->ysize;

    if (xsize > INT_MAX / ysize) {
        return ImagingError_MemoryError();
    }
    /* malloc check ok, using calloc for final overflow, x*y above */
    p = calloc(xsize * ysize, sizeof(Pixel));
    if (!p) {
        return ImagingError_MemoryError();
    }

    /* collect statistics */

    /* FIXME: maybe we could load the hash tables directly from the
       image data? */

    if (im->mode == IMAGING_MODE_L) {
        /* grayscale */

        /* FIXME: converting a "L" image to "P" with 256 colors
           should be done by a simple copy... */

        for (i = y = 0; y < ysize; y++) {
            UINT8 *in = im->image8[y];
            for (x = 0; x < xsize; x++, i++) {
                p[i].c.r = p[i].c.g = p[i].c.b = in[x];
                p[i].c.a = 255;
            }
        }

    } else if (im->mode == IMAGING_MODE_P) {
        /* palette */

        pp = im->palette->palette;

        for (i = y = 0; y < ysize; y++) {
            UINT8 *in = im->image8[y];
            for (x = 0; x < xsize; x++, i++) {
                v = in[x];
                p[i].c.r = pp[v * 4 + 0];
                p[i].c.g = pp[v * 4 + 1];
                p[i].c.b = pp[v * 4 + 2];
                p[i].c.a = pp[v * 4 + 3];
            }
        }

    } else if (im->mode == IMAGING_MODE_RGB || im->mode == IMAGING_MODE_RGBA) {
        /* true colour */

        withAlpha = im->mode == IMAGING_MODE_RGBA;
        int transparency = 0;
        unsigned char r = 0, g = 0, b = 0;
        for (i = y = 0; y < ysize; y++) {
            INT32 *in = im->image32[y];
            for (x = 0; x < xsize; x++, i++) {
                p[i].v = in[x];
                if (withAlpha) {
                    if (p[i].c.a == 0) {
                        if (transparency == 0) {
                            transparency = 1;
                            r = p[i].c.r;
                            g = p[i].c.g;
                            b = p[i].c.b;
                        } else {
                            /* Set all subsequent transparent pixels
                            to the same colour as the first */
                            p[i].c.r = r;
                            p[i].c.g = g;
                            p[i].c.b = b;
                        }
                    }
                } else {
                    p[i].c.a = 255;
                }
            }
        }

    } else {
        free(p);
        return (Imaging)ImagingError_ValueError("internal error");
    }

    ImagingSectionEnter(&cookie);

    switch (mode) {
        case 0:
            /* median cut */
            result = quantize(
                p, xsize * ysize, colors, &palette, &paletteLength, &newData, kmeans
            );
            break;
        case 1:
            /* maximum coverage */
            result = quantize2(
                p, xsize * ysize, colors, &palette, &paletteLength, &newData, kmeans
            );
            break;
        case 2:
            result = quantize_octree(
                p, xsize * ysize, colors, &palette, &paletteLength, &newData, withAlpha
            );
            break;
        case 3:
#ifdef HAVE_LIBIMAGEQUANT
            result = quantize_pngquant(
                p, xsize, ysize, colors, &palette, &paletteLength, &newData, withAlpha
            );
#else
            result = -1;
#endif
            break;
        default:
            result = 0;
            break;
    }

    free(p);
    ImagingSectionLeave(&cookie);

    if (result > 0) {
        imOut = ImagingNewDirty(IMAGING_MODE_P, xsize, ysize);
        if (!imOut) {
            free(newData);
            free(palette);
            return NULL;
        }
        ImagingSectionEnter(&cookie);

        for (i = y = 0; y < ysize; y++) {
            for (x = 0; x < xsize; x++) {
                imOut->image8[y][x] = (unsigned char)newData[i++];
            }
        }

        free(newData);

        imOut->palette->size = (int)paletteLength;
        pp = imOut->palette->palette;

        for (i = j = 0; i < (int)paletteLength; i++) {
            *pp++ = palette[i].c.r;
            *pp++ = palette[i].c.g;
            *pp++ = palette[i].c.b;
            if (withAlpha) {
                *pp = palette[i].c.a;
            }
            pp++;
        }

        if (withAlpha) {
            imOut->palette->mode = IMAGING_MODE_RGBA;
        }

        free(palette);
        ImagingSectionLeave(&cookie);

        return imOut;

    } else {
        if (result == -1) {
            return (Imaging)ImagingError_ValueError(
                "dependency required by this method was not "
                "enabled at compile time"
            );
        }

        return (Imaging)ImagingError_ValueError("quantization error");
    }
}
