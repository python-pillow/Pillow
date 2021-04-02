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

typedef struct _HashNode {
    struct _HashNode *next;
    HashKey_t key;
    HashVal_t value;
} HashNode;

struct _HashTable {
    HashNode **table;
    uint32_t length;
    uint32_t count;
    HashFunc hashFunc;
    HashCmpFunc cmpFunc;
    void *userData;
};

#define MIN_LENGTH 11
#define RESIZE_FACTOR 3

static int
_hashtable_insert_node(HashTable *, HashNode *, int, int, CollisionFunc);

HashTable *
hashtable_new(HashFunc hf, HashCmpFunc cf) {
    HashTable *h;
    h = malloc(sizeof(HashTable));
    if (!h) {
        return NULL;
    }
    h->hashFunc = hf;
    h->cmpFunc = cf;
    h->length = MIN_LENGTH;
    h->count = 0;
    h->userData = NULL;
    h->table = malloc(sizeof(HashNode *) * h->length);
    if (!h->table) {
        free(h);
        return NULL;
    }
    memset(h->table, 0, sizeof(HashNode *) * h->length);
    return h;
}

static uint32_t
_findPrime(uint32_t start, int dir) {
    static int unit[] = {0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0};
    uint32_t t;
    while (start > 1) {
        if (!unit[start & 0x0f]) {
            start += dir;
            continue;
        }
        for (t = 2; t < sqrt((double)start); t++) {
            if (!start % t) {
                break;
            }
        }
        if (t >= sqrt((double)start)) {
            break;
        }
        start += dir;
    }
    return start;
}

static void
_hashtable_rehash(HashTable *h, CollisionFunc cf, uint32_t newSize) {
    HashNode **oldTable = h->table;
    uint32_t i;
    HashNode *n, *nn;
    uint32_t oldSize;
    oldSize = h->length;
    h->table = malloc(sizeof(HashNode *) * newSize);
    if (!h->table) {
        h->table = oldTable;
        return;
    }
    h->length = newSize;
    h->count = 0;
    memset(h->table, 0, sizeof(HashNode *) * h->length);
    for (i = 0; i < oldSize; i++) {
        for (n = oldTable[i]; n; n = nn) {
            nn = n->next;
            _hashtable_insert_node(h, n, 0, 0, cf);
        }
    }
    free(oldTable);
}

static void
_hashtable_resize(HashTable *h) {
    uint32_t newSize;
    uint32_t oldSize;
    oldSize = h->length;
    newSize = oldSize;
    if (h->count * RESIZE_FACTOR < h->length) {
        newSize = _findPrime(h->length / 2 - 1, -1);
    } else if (h->length * RESIZE_FACTOR < h->count) {
        newSize = _findPrime(h->length * 2 + 1, +1);
    }
    if (newSize < MIN_LENGTH) {
        newSize = oldSize;
    }
    if (newSize != oldSize) {
        _hashtable_rehash(h, NULL, newSize);
    }
}

static int
_hashtable_insert_node(
    HashTable *h, HashNode *node, int resize, int update, CollisionFunc cf) {
    uint32_t hash = h->hashFunc(h, node->key) % h->length;
    HashNode **n, *nv;
    int i;

    for (n = &(h->table[hash]); *n; n = &((*n)->next)) {
        nv = *n;
        i = h->cmpFunc(h, nv->key, node->key);
        if (!i) {
            if (cf) {
                nv->key = node->key;
                cf(h, &(nv->key), &(nv->value), node->key, node->value);
                free(node);
                return 1;
            } else {
                nv->key = node->key;
                nv->value = node->value;
                free(node);
                return 1;
            }
        } else if (i > 0) {
            break;
        }
    }
    if (!update) {
        node->next = *n;
        *n = node;
        h->count++;
        if (resize) {
            _hashtable_resize(h);
        }
        return 1;
    } else {
        return 0;
    }
}

static int
_hashtable_insert(HashTable *h, HashKey_t key, HashVal_t val, int resize, int update) {
    HashNode **n, *nv;
    HashNode *t;
    int i;
    uint32_t hash = h->hashFunc(h, key) % h->length;

    for (n = &(h->table[hash]); *n; n = &((*n)->next)) {
        nv = *n;
        i = h->cmpFunc(h, nv->key, key);
        if (!i) {
            nv->value = val;
            return 1;
        } else if (i > 0) {
            break;
        }
    }
    if (!update) {
        t = malloc(sizeof(HashNode));
        if (!t) {
            return 0;
        }
        t->next = *n;
        *n = t;
        t->key = key;
        t->value = val;
        h->count++;
        if (resize) {
            _hashtable_resize(h);
        }
        return 1;
    } else {
        return 0;
    }
}

int
hashtable_insert_or_update_computed(
    HashTable *h, HashKey_t key, ComputeFunc newFunc, ComputeFunc existsFunc) {
    HashNode **n, *nv;
    HashNode *t;
    int i;
    uint32_t hash = h->hashFunc(h, key) % h->length;

    for (n = &(h->table[hash]); *n; n = &((*n)->next)) {
        nv = *n;
        i = h->cmpFunc(h, nv->key, key);
        if (!i) {
            if (existsFunc) {
                existsFunc(h, nv->key, &(nv->value));
            } else {
                return 0;
            }
            return 1;
        } else if (i > 0) {
            break;
        }
    }
    t = malloc(sizeof(HashNode));
    if (!t) {
        return 0;
    }
    t->key = key;
    t->next = *n;
    *n = t;
    if (newFunc) {
        newFunc(h, t->key, &(t->value));
    } else {
        free(t);
        return 0;
    }
    h->count++;
    _hashtable_resize(h);
    return 1;
}

int
hashtable_insert(HashTable *h, HashKey_t key, HashVal_t val) {
    return _hashtable_insert(h, key, val, 1, 0);
}

void
hashtable_foreach_update(HashTable *h, IteratorUpdateFunc i, void *u) {
    HashNode *n;
    uint32_t x;

    if (h->table) {
        for (x = 0; x < h->length; x++) {
            for (n = h->table[x]; n; n = n->next) {
                i(h, n->key, &(n->value), u);
            }
        }
    }
}

void
hashtable_foreach(HashTable *h, IteratorFunc i, void *u) {
    HashNode *n;
    uint32_t x;

    if (h->table) {
        for (x = 0; x < h->length; x++) {
            for (n = h->table[x]; n; n = n->next) {
                i(h, n->key, n->value, u);
            }
        }
    }
}

void
hashtable_free(HashTable *h) {
    HashNode *n, *nn;
    uint32_t i;

    if (h->table) {
        for (i = 0; i < h->length; i++) {
            for (n = h->table[i]; n; n = nn) {
                nn = n->next;
                free(n);
            }
        }
        free(h->table);
    }
    free(h);
}

void
hashtable_rehash_compute(HashTable *h, CollisionFunc cf) {
    _hashtable_rehash(h, cf, h->length);
}

int
hashtable_lookup(const HashTable *h, const HashKey_t key, HashVal_t *valp) {
    uint32_t hash = h->hashFunc(h, key) % h->length;
    HashNode *n;
    int i;

    for (n = h->table[hash]; n; n = n->next) {
        i = h->cmpFunc(h, n->key, key);
        if (!i) {
            *valp = n->value;
            return 1;
        } else if (i > 0) {
            break;
        }
    }
    return 0;
}

uint32_t
hashtable_get_count(const HashTable *h) {
    return h->count;
}

void *
hashtable_get_user_data(const HashTable *h) {
    return h->userData;
}

void *
hashtable_set_user_data(HashTable *h, void *data) {
    void *r = h->userData;
    h->userData = data;
    return r;
}
