// Arrow C Data Interface structure definitions.
//
// These free-standing definitions are published by the Apache Arrow project
// for copying into third-party projects, under the Apache License 2.0:
// https://arrow.apache.org/docs/format/CDataInterface.html#structure-definitions
//
// Copyright The Apache Software Foundation.
// SPDX-License-Identifier: Apache-2.0
//
// Per the specification, the ARROW_C_DATA_INTERFACE guard below is kept exactly
// as-is to avoid duplicate definitions when multiple projects vendor these
// declarations.

#include <stdint.h>
#include <assert.h>

#ifndef ARROW_C_DATA_INTERFACE
#define ARROW_C_DATA_INTERFACE

#define ARROW_FLAG_DICTIONARY_ORDERED 1
#define ARROW_FLAG_NULLABLE 2
#define ARROW_FLAG_MAP_KEYS_SORTED 4

struct ArrowSchema {
    // Array type description
    const char *format;
    const char *name;
    const char *metadata;
    int64_t flags;
    int64_t n_children;
    struct ArrowSchema **children;
    struct ArrowSchema *dictionary;

    // Release callback
    void (*release)(struct ArrowSchema *);
    // Opaque producer-specific data
    void *private_data;
};

struct ArrowArray {
    // Array data description
    int64_t length;
    int64_t null_count;
    int64_t offset;
    int64_t n_buffers;
    int64_t n_children;
    const void **buffers;
    struct ArrowArray **children;
    struct ArrowArray *dictionary;

    // Release callback
    void (*release)(struct ArrowArray *);
    // Opaque producer-specific data
    void *private_data;
};

#endif  // ARROW_C_DATA_INTERFACE
