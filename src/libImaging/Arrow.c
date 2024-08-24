
#include "Arrow.h"
#include "Imaging.h"
#include <string.h>

/* struct ArrowSchema* */
/* _arrow_schema_channel(char* channel, char* format) { */

/* } */

static void
ReleaseExportedSchema(struct ArrowSchema* array) {
  // This should not be called on already released array
  //assert(array->release != NULL);

  if (!array->release) {
    return;
  }
  if (array->format) {
    free((void*)array->format);
    array->format = NULL;
  }
  if (array->name) {
    free((void*)array->name);
    array->name = NULL;
  }

  // Release children
  for (int64_t i = 0; i < array->n_children; ++i) {
    struct ArrowSchema* child = array->children[i];
    if (child->release != NULL) {
      child->release(child);
      //assert(child->release == NULL);
    }
  }

  // Release dictionary
  struct ArrowSchema* dict = array->dictionary;
  if (dict != NULL && dict->release != NULL) {
    dict->release(dict);
    //assert(dict->release == NULL);
  }

  // TODO here: release and/or deallocate all data directly owned by
  // the ArrowArray struct, such as the private_data.

  // Mark array released
  array->release = NULL;
}



int export_named_type(struct ArrowSchema* schema,
                       char* format,
                       char* name) {

  char* formatp;
  char* namep;
  size_t format_len = strlen(format) + 1;
  size_t name_len = strlen(name) + 1;

  formatp = calloc(format_len, 1);

  if (!formatp) {
    return 1;
  }

  namep = calloc(name_len, 1);
  if (!namep){
    free(formatp);
    return 1;
  }

  strlcpy(formatp, format, format_len);
  strlcpy(namep, name, name_len);

  *schema = (struct ArrowSchema) {
    // Type description
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

int export_imaging_schema(Imaging im, struct ArrowSchema* schema) {
  int retval = 0;

  if (strcmp(im->arrow_band_format, "") == 0) {
    return 1;
  }

  if (im->bands == 1) {
    return export_named_type(schema, im->arrow_band_format, im->band_names[0]);
  }

  retval = export_named_type(schema, "+s", "");
  if (retval) {
    return retval;
  }
  // if it's not 1 band, it's an int32 at the moment. 4 unint8 bands.
  schema->n_children = 4;
  schema->children = calloc(4, sizeof(struct ArrowSchema*));
  for (int i=0; i<4; i++) {
    schema->children[i] =
      (struct ArrowSchema*)calloc(1, sizeof(struct ArrowSchema));
    if (export_named_type(schema->children[i], im->arrow_band_format, im->band_names[i])) {
      /* error recovery */
      for (int j=i-1; i>=0; i--) {
        schema->children[j]->release(schema->children[j]);
        free(schema->children[j]);
      }
      return 2;
    }
  }
  return 0;
}

static void release_simple_type(struct ArrowSchema* schema) {
   // Mark released
   schema->release = NULL;
}

void export_uint32_type(struct ArrowSchema* schema) {
   *schema = (struct ArrowSchema) {
      // Type description
      .format = "I",
      .name = "",
      .metadata = NULL,
      .flags = 0,
      .n_children = 0,
      .children = NULL,
      .dictionary = NULL,
      // Bookkeeping
      .release = &release_simple_type
   };
}


static void release_uint32_array(struct ArrowArray* array) {
   //assert(array->n_buffers == 2);
   // Free the buffers and the buffers array
   free((void *) array->buffers[1]);
   free(array->buffers);
   // Mark released
   array->release = NULL;
}

void export_uint32_array(const uint32_t* data, int64_t nitems,
                         struct ArrowArray* array) {
   // Initialize primitive fields
   *array = (struct ArrowArray) {
      // Data description
      .length = nitems,
      .offset = 0,
      .null_count = 0,
      .n_buffers = 2,
      .n_children = 0,
      .children = NULL,
      .dictionary = NULL,
      // Bookkeeping
      .release = &release_uint32_array
   };
   // Allocate list of buffers
   array->buffers = (const void**) malloc(sizeof(void*) * array->n_buffers);
   //assert(array->buffers != NULL);
   array->buffers[0] = NULL;  // no nulls, null bitmap can be omitted
   array->buffers[1] = data;
}

static void release_const_array(struct ArrowArray* array) {
  Imaging im = (Imaging)array->private_data;
   im->arrow_borrow--;
   ImagingDelete(im);

   //assert(array->n_buffers == 2);
   // Free the buffers and the buffers array
   free(array->buffers);
   // Mark released
   array->release = NULL;
}


void export_imaging_array(Imaging im, struct ArrowArray* array) {
  int length = im->xsize * im->ysize;

  /* undone -- for now, single block images */
  //assert (im->block_count = 0 || im->block_count = 1);

  if (im->lines_per_block && im->lines_per_block < im->ysize) {
    length = im->xsize * im->lines_per_block;
  }

  im->arrow_borrow++;
  // Initialize primitive fields
  *array = (struct ArrowArray) {
      // Data description
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
   array->buffers = (const void**) malloc(sizeof(void*) * array->n_buffers);
   //assert(array->buffers != NULL);
   array->buffers[0] = NULL;  // no nulls, null bitmap can be omitted

   if (im->block) {
     array->buffers[1] = im->block;
   } else {
     array->buffers[1] = im->blocks[0].ptr;
   }
}
