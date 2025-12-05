
#include "Arrow.h"
#include "Imaging.h"
#include <string.h>

/* struct ArrowSchema* */
/* _arrow_schema_channel(char* channel, char* format) { */

/* } */

static void
ReleaseExportedSchema(struct ArrowSchema *array) {
    // This should not be called on already released array
    // assert(array->release != NULL);

    if (!array->release) {
        return;
    }
    if (array->format) {
        free((void *)array->format);
        array->format = NULL;
    }
    if (array->name) {
        free((void *)array->name);
        array->name = NULL;
    }
    if (array->metadata) {
        free((void *)array->metadata);
        array->metadata = NULL;
    }

    // Release children
    for (int64_t i = 0; i < array->n_children; ++i) {
        struct ArrowSchema *child = array->children[i];
        if (child->release != NULL) {
            child->release(child);
            child->release = NULL;
        }
        free(array->children[i]);
    }
    if (array->children) {
        free(array->children);
    }

    // Release dictionary
    struct ArrowSchema *dict = array->dictionary;
    if (dict != NULL && dict->release != NULL) {
        dict->release(dict);
        dict->release = NULL;
    }

    // TODO here: release and/or deallocate all data directly owned by
    // the ArrowArray struct, such as the private_data.

    // Mark array released
    array->release = NULL;
}
char *
image_band_json(Imaging im) {
    char *format = "{\"bands\": [\"%s\", \"%s\", \"%s\", \"%s\"]}";
    char *json;
    // Bands can be 4 bands * 2 characters each
    int len = strlen(format) + 8 + 1;
    int err;

    json = calloc(1, len);

    if (!json) {
        return NULL;
    }

    err = PyOS_snprintf(
        json,
        len,
        format,
        im->band_names[0],
        im->band_names[1],
        im->band_names[2],
        im->band_names[3]
    );
    if (err < 0) {
        return NULL;
    }
    return json;
}

char *
single_band_json(Imaging im) {
    char *format = "{\"bands\": [\"%s\"]}";
    char *json;
    // Bands can be 1 band * (maybe but probably not) 2 characters each
    int len = strlen(format) + 2 + 1;
    int err;

    json = calloc(1, len);

    if (!json) {
        return NULL;
    }

    err = PyOS_snprintf(json, len, format, im->band_names[0]);
    if (err < 0) {
        return NULL;
    }
    return json;
}

char *
assemble_metadata(const char *band_json) {
    /* format is
       int32: number of key/value pairs (noted N below)
       int32: byte length of key 0
       key 0 (not null-terminated)
       int32: byte length of value 0
       value 0 (not null-terminated)
       ...
       int32: byte length of key N - 1
       key N - 1 (not null-terminated)
       int32: byte length of value N - 1
       value N - 1 (not null-terminated)
    */
    const char *key = "image";
    INT32 key_len = strlen(key);
    INT32 band_json_len = strlen(band_json);

    char *buf;
    INT32 *dest_int;
    char *dest;

    buf = calloc(1, key_len + band_json_len + 4 + 1 * 8);
    if (!buf) {
        return NULL;
    }

    dest_int = (void *)buf;

    dest_int[0] = 1;
    dest_int[1] = key_len;
    dest_int += 2;
    dest = (void *)dest_int;
    memcpy(dest, key, key_len);
    dest += key_len;
    dest_int = (void *)dest;
    dest_int[0] = band_json_len;
    dest_int += 1;
    memcpy(dest_int, band_json, band_json_len);

    return buf;
}

int
export_named_type(struct ArrowSchema *schema, char *format, const char *name) {
    char *formatp;
    char *namep;
    size_t format_len = strlen(format) + 1;
    size_t name_len = strlen(name) + 1;

    formatp = calloc(format_len, 1);

    if (!formatp) {
        return IMAGING_CODEC_MEMORY;
    }

    namep = calloc(name_len, 1);
    if (!namep) {
        free(formatp);
        return IMAGING_CODEC_MEMORY;
    }

    strncpy(formatp, format, format_len);
    strncpy(namep, name, name_len);

    *schema = (struct ArrowSchema){// Type description
                                   .format = formatp,
                                   .name = namep,
                                   .metadata = NULL,
                                   .flags = 0,
                                   .n_children = 0,
                                   .children = NULL,
                                   .dictionary = NULL,
                                   // Bookkeeping
                                   .release = &ReleaseExportedSchema
    };
    return 0;
}

int
export_imaging_schema(Imaging im, struct ArrowSchema *schema) {
    int retval = 0;
    char *band_json;

    if (strcmp(im->arrow_band_format, "") == 0) {
        return IMAGING_ARROW_INCOMPATIBLE_MODE;
    }

    /* for now, single block images */
    if (im->blocks_count > 1) {
        return IMAGING_ARROW_MEMORY_LAYOUT;
    }

    if (im->bands == 1) {
        retval = export_named_type(schema, im->arrow_band_format, im->band_names[0]);
        if (retval != 0) {
            return retval;
        }
        // band related metadata
        band_json = single_band_json(im);
        if (band_json) {
            schema->metadata = assemble_metadata(band_json);
            free(band_json);
        }
        return retval;
    }

    retval = export_named_type(schema, "+w:4", "");
    if (retval != 0) {
        return retval;
    }
    // if it's not 1 band, it's an int32 at the moment. 4 uint8 bands.
    schema->n_children = 1;
    schema->children = calloc(1, sizeof(struct ArrowSchema *));
    schema->children[0] = (struct ArrowSchema *)calloc(1, sizeof(struct ArrowSchema));
    retval = export_named_type(
        schema->children[0], im->arrow_band_format, getModeData(im->mode)->name
    );
    if (retval != 0) {
        free(schema->children[0]);
        free(schema->children);
        schema->release(schema);
        return retval;
    }

    // band related metadata
    band_json = image_band_json(im);
    if (band_json) {
        // adding the metadata to the child array.
        // Accessible in pyarrow via pa.array(img).type.field(0).metadata
        // adding it to the top level is not accessible.
        schema->children[0]->metadata = assemble_metadata(band_json);
        free(band_json);
    }

    return 0;
}

static void
release_const_array(struct ArrowArray *array) {
    Imaging im = (Imaging)array->private_data;

    ImagingDelete(im);

    //  Free the buffers and the buffers array
    if (array->buffers) {
        free(array->buffers);
        array->buffers = NULL;
    }
    if (array->children) {
        // undone -- does arrow release all the children recursively?
        for (int i = 0; i < array->n_children; i++) {
            if (array->children[i]->release) {
                array->children[i]->release(array->children[i]);
                array->children[i]->release = NULL;
                free(array->children[i]);
            }
        }
        free(array->children);
        array->children = NULL;
    }
    // Mark released
    array->release = NULL;
}

int
export_single_channel_array(Imaging im, struct ArrowArray *array) {
    int length = im->xsize * im->ysize;

    /* for now, single block images */
    if (im->blocks_count > 1) {
        return IMAGING_ARROW_MEMORY_LAYOUT;
    }

    if (im->lines_per_block && im->lines_per_block < im->ysize) {
        length = im->xsize * im->lines_per_block;
    }

    MUTEX_LOCK(&im->mutex);
    im->refcount++;
    MUTEX_UNLOCK(&im->mutex);
    // Initialize primitive fields
    *array = (struct ArrowArray){// Data description
                                 .length = length,
                                 .offset = 0,
                                 .null_count = 0,
                                 .n_buffers = 2,
                                 .n_children = 0,
                                 .children = NULL,
                                 .dictionary = NULL,
                                 // Bookkeeping
                                 .release = &release_const_array,
                                 .private_data = im
    };

    // Allocate list of buffers
    array->buffers = (const void **)malloc(sizeof(void *) * array->n_buffers);
    // assert(array->buffers != NULL);
    array->buffers[0] = NULL;  // no nulls, null bitmap can be omitted

    if (im->block) {
        array->buffers[1] = im->block;
    } else {
        array->buffers[1] = im->blocks[0].ptr;
    }
    return 0;
}

int
export_fixed_pixel_array(Imaging im, struct ArrowArray *array) {
    int length = im->xsize * im->ysize;

    /* for now, single block images */
    if (im->blocks_count > 1) {
        return IMAGING_ARROW_MEMORY_LAYOUT;
    }

    if (im->lines_per_block && im->lines_per_block < im->ysize) {
        length = im->xsize * im->lines_per_block;
    }

    MUTEX_LOCK(&im->mutex);
    im->refcount++;
    MUTEX_UNLOCK(&im->mutex);
    // Initialize primitive fields
    // Fixed length arrays are 1 buffer of validity, and the length in pixels.
    // Data is in a child array.
    *array = (struct ArrowArray){// Data description
                                 .length = length,
                                 .offset = 0,
                                 .null_count = 0,
                                 .n_buffers = 1,
                                 .n_children = 1,
                                 .children = NULL,
                                 .dictionary = NULL,
                                 // Bookkeeping
                                 .release = &release_const_array,
                                 .private_data = im
    };

    // Allocate list of buffers
    array->buffers = (const void **)calloc(1, sizeof(void *) * array->n_buffers);
    if (!array->buffers) {
        goto err;
    }
    // assert(array->buffers != NULL);
    array->buffers[0] = NULL;  // no nulls, null bitmap can be omitted

    // if it's not 1 band, it's an int32 at the moment. 4 uint8 bands.
    array->n_children = 1;
    array->children = calloc(1, sizeof(struct ArrowArray *));
    if (!array->children) {
        goto err;
    }
    array->children[0] = (struct ArrowArray *)calloc(1, sizeof(struct ArrowArray));
    if (!array->children[0]) {
        goto err;
    }

    MUTEX_LOCK(&im->mutex);
    im->refcount++;
    MUTEX_UNLOCK(&im->mutex);
    *array->children[0] = (struct ArrowArray){// Data description
                                              .length = length * 4,
                                              .offset = 0,
                                              .null_count = 0,
                                              .n_buffers = 2,
                                              .n_children = 0,
                                              .children = NULL,
                                              .dictionary = NULL,
                                              // Bookkeeping
                                              .release = &release_const_array,
                                              .private_data = im
    };

    array->children[0]->buffers =
        (const void **)calloc(2, sizeof(void *) * array->n_buffers);

    if (im->block) {
        array->children[0]->buffers[1] = im->block;
    } else {
        array->children[0]->buffers[1] = im->blocks[0].ptr;
    }
    return 0;

err:
    if (array->children[0]) {
        free(array->children[0]);
    }
    if (array->children) {
        free(array->children);
    }
    if (array->buffers) {
        free(array->buffers);
    }
    return IMAGING_CODEC_MEMORY;
}

int
export_imaging_array(Imaging im, struct ArrowArray *array) {
    if (strcmp(im->arrow_band_format, "") == 0) {
        return IMAGING_ARROW_INCOMPATIBLE_MODE;
    }

    if (im->bands == 1) {
        return export_single_channel_array(im, array);
    }

    return export_fixed_pixel_array(im, array);
}
