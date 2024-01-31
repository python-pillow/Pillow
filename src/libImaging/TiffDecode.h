/*
 * The Python Imaging Library.
 * $Id: //modules/pil/libImaging/Tiff.h#1 $
 *
 * declarations for the LibTiff-based Group3 and Group4 decoder
 *
 */

#ifndef _TIFFIO_
#include <tiffio.h>
#endif
#ifndef _TIFF_
#include <tiff.h>
#endif

#ifndef min
#define min(x, y) ((x > y) ? y : x)
#define max(x, y) ((x < y) ? y : x)
#endif

#ifndef _PIL_LIBTIFF_
#define _PIL_LIBTIFF_

typedef struct {
    tdata_t data; /* tdata_t == void* */
    toff_t loc;   /* toff_t == uint32 */
    tsize_t size; /* tsize_t == int32 */
    int fp;
    uint32_t ifd; /* offset of the ifd, used for multipage
                   * Should be uint32 for libtiff 3.9.x
                   * uint64 for libtiff 4.0.x
                   */
    TIFF *tiff; /* Used in write */
    toff_t eof;
    int flrealloc; /* may we realloc */
} TIFFSTATE;

extern int
ImagingLibTiffInit(ImagingCodecState state, int fp, uint32_t offset);
extern int
ImagingLibTiffEncodeInit(ImagingCodecState state, char *filename, int fp);
extern int
ImagingLibTiffMergeFieldInfo(
    ImagingCodecState state, TIFFDataType field_type, int key, int is_var_length);
extern int
ImagingLibTiffSetField(ImagingCodecState state, ttag_t tag, ...);

/*
   Trace debugging
   legacy, don't enable for Python 3.x, unicode issues.
*/

/*
#define VA_ARGS(...)   __VA_ARGS__
#define TRACE(args)    fprintf(stderr, VA_ARGS args)
*/

#define TRACE(args)

#endif
