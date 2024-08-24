
#include "Arrow.h"
#include "Imaging.h"

/* struct ArrowSchema* */
/* _arrow_schema_channel(char* channel, char* format) { */

/* } */

static void
ReleaseExportedSchema(struct ArrowSchema* array) {
  // This should not be called on already released array
  //assert(array->release != NULL);

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


static void release_uint32_type(struct ArrowSchema* schema) {
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
      .release = &release_uint32_type
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
