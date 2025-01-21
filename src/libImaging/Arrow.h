#include <stdint.h>
#include <assert.h>

// Apache License 2.0.
// Source apache arrow project
// https://arrow.apache.org/docs/format/CDataInterface.html

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
