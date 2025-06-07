
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

int
export_named_type(struct ArrowSchema *schema, char *format, char *name) {
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

    if (strcmp(im->arrow_band_format, "") == 0) {
        return IMAGING_ARROW_INCOMPATIBLE_MODE;
    }

    /* for now, single block images */
    if (im->blocks_count > 1) {
        return IMAGING_ARROW_MEMORY_LAYOUT;
    }

    if (im->bands == 1) {
        return export_named_type(schema, im->arrow_band_format, im->band_names[0]);
    }

    retval = export_named_type(schema, "+w:4", "");
    if (retval != 0) {
        return retval;
    }
    // if it's not 1 band, it's an int32 at the moment. 4 uint8 bands.
    schema->n_children = 1;
    schema->children = calloc(1, sizeof(struct ArrowSchema *));
    schema->children[0] = (struct ArrowSchema *)calloc(1, sizeof(struct ArrowSchema));
    retval = export_named_type(schema->children[0], im->arrow_band_format, "pixel");
    if (retval != 0) {
        free(schema->children[0]);
        free(schema->children);
        schema->release(schema);
        return retval;
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
