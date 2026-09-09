/*
 * The Python Imaging Library.
 * $Id: //modules/pil/libImaging/TiffDecode.c#1 $
 *
 * LibTiff-based Group3 and Group4 decoder
 *
 *
 * started modding to use non-private tiff functions to port to libtiff 4.x
 * eds 3/12/12
 *
 */

#include "Imaging.h"

#ifdef HAVE_LIBTIFF

#ifdef HAVE_UNISTD_H
#include <unistd.h> /* lseek */
#endif

#ifndef uint
#define uint uint32
#endif

#include "TiffDecode.h"

/* Convert C file descriptor to WinApi HFILE if LibTiff was compiled with tif_win32.c
 *
 * This cast is safe, as the top 32-bits of HFILE are guaranteed to be zero,
 * see
 * https://learn.microsoft.com/en-us/windows/win32/winprog64/interprocess-communication
 */
#ifndef USE_WIN32_FILEIO
#define fd_to_tiff_fd(fd) (fd)
#else
#define fd_to_tiff_fd(fd) ((int)_get_osfhandle(fd))
#endif

/*
  procs for TIFFOpenClient
*/

tsize_t
_tiffReadProc(thandle_t hdata, tdata_t buf, tsize_t size) {
    TIFFSTATE *state = (TIFFSTATE *)hdata;
    tsize_t to_read;

    if (state->loc > state->eof) {
        TIFFError(
            "_tiffReadProc",
            "Invalid Read at loc %" PRIu64 ", eof: %" PRIu64,
            state->loc,
            state->eof
        );
        return 0;
    }
    to_read = MIN(size, MIN(state->size, (tsize_t)state->eof) - (tsize_t)state->loc);

    _TIFFmemcpy(buf, (UINT8 *)state->data + state->loc, to_read);
    state->loc += (toff_t)to_read;

    return to_read;
}

tsize_t
_tiffWriteProc(thandle_t hdata, tdata_t buf, tsize_t size) {
    TIFFSTATE *state = (TIFFSTATE *)hdata;
    tsize_t to_write;

    to_write = MIN(size, state->size - (tsize_t)state->loc);
    if (state->flrealloc && size > to_write) {
        tdata_t new_data;
        tsize_t newsize = state->size;
        while (newsize < (size + state->size)) {
            if (newsize > INT_MAX - 64 * 1024) {
                return 0;
            }
            newsize += 64 * 1024;
            // newsize*=2; // UNDONE, by 64k chunks?
        }
        /* malloc check ok, overflow checked above */
        new_data = realloc(state->data, newsize);
        if (!new_data) {
            // fail out
            return 0;
        }
        state->data = new_data;
        state->size = newsize;
        to_write = size;
    }

    _TIFFmemcpy((UINT8 *)state->data + state->loc, buf, to_write);
    state->loc += (toff_t)to_write;
    state->eof = MAX(state->loc, state->eof);

    return to_write;
}

toff_t
_tiffSeekProc(thandle_t hdata, toff_t off, int whence) {
    TIFFSTATE *state = (TIFFSTATE *)hdata;

    switch (whence) {
        case 0:
            state->loc = off;
            break;
        case 1:
            state->loc += off;
            break;
        case 2:
            state->loc = state->eof + off;
            break;
    }
    return state->loc;
}

int
_tiffCloseProc(thandle_t hdata) {
    return 0;
}

toff_t
_tiffSizeProc(thandle_t hdata) {
    TIFFSTATE *state = (TIFFSTATE *)hdata;
    return (toff_t)state->size;
}

int
_tiffMapProc(thandle_t hdata, tdata_t *pbase, toff_t *psize) {
    TIFFSTATE *state = (TIFFSTATE *)hdata;
    *pbase = state->data;
    *psize = state->size;
    return (1);
}

int
_tiffNullMapProc(thandle_t hdata, tdata_t *pbase, toff_t *psize) {
    (void)hdata;
    (void)pbase;
    (void)psize;
    return (0);
}

void
_tiffUnmapProc(thandle_t hdata, tdata_t base, toff_t size) {
    (void)hdata;
    (void)base;
    (void)size;
}

int
ImagingLibTiffInit(ImagingCodecState state, int fp, uint32_t offset) {
    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;

    clientstate->loc = 0;
    clientstate->size = 0;
    clientstate->data = 0;
    clientstate->fp = fp;
    clientstate->ifd = offset;
    clientstate->eof = 0;

    return 1;
}

int
_pickUnpackers(
    Imaging im,
    ImagingCodecState state,
    TIFF *tiff,
    uint16_t planarconfig,
    ImagingShuffler *unpackers
) {
    // if number of bands is 1, there is no difference with contig case
    if (planarconfig == PLANARCONFIG_SEPARATE && im->bands > 1) {
        uint16_t bits_per_sample = 8;

        TIFFGetFieldDefaulted(tiff, TIFFTAG_BITSPERSAMPLE, &bits_per_sample);
        if (bits_per_sample != 8 && bits_per_sample != 16) {
            state->errcode = IMAGING_CODEC_BROKEN;
            return -1;
        }

        // We'll pick appropriate set of unpackers depending on planar_configuration
        // It does not matter if data is RGB(A), CMYK or LUV really,
        // we just copy it plane by plane
        unpackers[0] = ImagingFindUnpacker(
            IMAGING_MODE_RGBA,
            bits_per_sample == 16 ? IMAGING_RAWMODE_R_16N : IMAGING_RAWMODE_R,
            NULL
        );
        unpackers[1] = ImagingFindUnpacker(
            IMAGING_MODE_RGBA,
            bits_per_sample == 16 ? IMAGING_RAWMODE_G_16N : IMAGING_RAWMODE_G,
            NULL
        );
        unpackers[2] = ImagingFindUnpacker(
            IMAGING_MODE_RGBA,
            bits_per_sample == 16 ? IMAGING_RAWMODE_B_16N : IMAGING_RAWMODE_B,
            NULL
        );
        unpackers[3] = ImagingFindUnpacker(
            IMAGING_MODE_RGBA,
            bits_per_sample == 16 ? IMAGING_RAWMODE_A_16N : IMAGING_RAWMODE_A,
            NULL
        );

        return im->bands;
    } else {
        unpackers[0] = state->shuffle;

        return 1;
    }
}

int
_decodeAsRGBA(Imaging im, ImagingCodecState state, TIFF *tiff) {
    // To avoid dealing with YCbCr subsampling and other complications, let libtiff
    // handle it Use a TIFFRGBAImage wrapping the tiff image, and let libtiff handle all
    // of the conversion. Metadata read from the TIFFRGBAImage could be different from
    // the metadata that the base tiff returns.

    INT32 current_row;
    UINT8 *new_data;
    UINT32 rows_per_block, row_byte_size, rows_to_read;
    int ret;
    TIFFRGBAImage img;
    char emsg[1024] = "";

    // Since using TIFFRGBAImage* functions, we can read whole tiff into rastrr in one
    // call Let's select smaller block size. Multiplying image width by (tile length OR
    // rows per strip) gives us manageable block size in pixels
    if (TIFFIsTiled(tiff)) {
        ret = TIFFGetFieldDefaulted(tiff, TIFFTAG_TILELENGTH, &rows_per_block);
    } else {
        ret = TIFFGetFieldDefaulted(tiff, TIFFTAG_ROWSPERSTRIP, &rows_per_block);
    }

    if (ret != 1 || rows_per_block == (UINT32)(-1)) {
        rows_per_block = state->ysize;
    }

    if (!(TIFFRGBAImageOK(tiff, emsg) && TIFFRGBAImageBegin(&img, tiff, 0, emsg))) {
        state->errcode = IMAGING_CODEC_BROKEN;
        // nothing to clean up, just return
        return -1;
    }

    img.orientation = ORIENTATION_TOPLEFT;
    img.req_orientation = ORIENTATION_TOPLEFT;
    img.col_offset = 0;

    /* overflow check for row byte size */
    if (INT_MAX / 4 < img.width) {
        state->errcode = IMAGING_CODEC_MEMORY;
        goto decodergba_err;
    }

    // TiffRGBAImages are 32bits/pixel.
    row_byte_size = img.width * 4;

    /* overflow check for realloc */
    if (INT_MAX / row_byte_size < rows_per_block) {
        state->errcode = IMAGING_CODEC_MEMORY;
        goto decodergba_err;
    }

    state->bytes = rows_per_block * row_byte_size;

    /* realloc to fit whole strip */
    /* malloc check above */
    new_data = realloc(state->buffer, state->bytes);
    if (!new_data) {
        state->errcode = IMAGING_CODEC_MEMORY;
        goto decodergba_err;
    }

    state->buffer = new_data;

    for (; state->y < state->ysize; state->y += rows_per_block) {
        img.row_offset = state->y;
        rows_to_read = MIN(rows_per_block, img.height - state->y);

        if (!TIFFRGBAImageGet(&img, (UINT32 *)state->buffer, img.width, rows_to_read)) {
            state->errcode = IMAGING_CODEC_BROKEN;
            goto decodergba_err;
        }

#if WORDS_BIGENDIAN
        TIFFSwabArrayOfLong((UINT32 *)state->buffer, img.width * rows_to_read);
#endif

        // iterate over each row in the strip and stuff data into image
        for (current_row = 0;
             current_row < MIN((INT32)rows_per_block, state->ysize - state->y);
             current_row++) {
            state->shuffle(
                (UINT8 *)im->image[state->y + state->yoff + current_row] +
                    state->xoff * im->pixelsize,
                state->buffer + current_row * row_byte_size,
                state->xsize
            );
        }
    }

decodergba_err:
    TIFFRGBAImageEnd(&img);
    if (state->errcode != 0) {
        return -1;
    }
    return 0;
}

int
_decodeTile(
    Imaging im,
    ImagingCodecState state,
    TIFF *tiff,
    int planes,
    ImagingShuffler *unpackers
) {
    INT32 x, y, tile_y, current_tile_length, current_tile_width;
    UINT32 tile_width, tile_length;
    tsize_t tile_bytes_size, row_byte_size;
    UINT8 *new_data;

    tile_bytes_size = TIFFTileSize(tiff);

    if (tile_bytes_size == 0) {
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }

    row_byte_size = TIFFTileRowSize(tiff);

    if (row_byte_size == 0 || row_byte_size > tile_bytes_size) {
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }

    /* overflow check for realloc */
    if (tile_bytes_size > INT_MAX - 1) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    TIFFGetField(tiff, TIFFTAG_TILEWIDTH, &tile_width);
    TIFFGetField(tiff, TIFFTAG_TILELENGTH, &tile_length);

    if (tile_width > INT_MAX || tile_length > INT_MAX) {
        // state->x and state->y are ints
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    if (tile_bytes_size > ((tile_length * state->bits / planes + 7) / 8) * tile_width) {
        // If the tile size as expected by LibTiff isn't what we're expecting, abort.
        // man:   TIFFTileSize returns the equivalent size for a tile of data as it
        // would be returned in a call to TIFFReadTile ...
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }

    state->bytes = tile_bytes_size;

    /* realloc to fit whole tile */
    /* malloc check above */
    new_data = realloc(state->buffer, state->bytes);
    if (!new_data) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }
    state->buffer = new_data;

    for (y = state->yoff; y < state->ysize; y += tile_length) {
        int plane;
        for (plane = 0; plane < planes; plane++) {
            ImagingShuffler shuffler = unpackers[plane];
            for (x = state->xoff; x < state->xsize; x += tile_width) {
                if (TIFFReadTile(tiff, (tdata_t)state->buffer, x, y, 0, plane) == -1) {
                    state->errcode = IMAGING_CODEC_BROKEN;
                    return -1;
                }

                current_tile_width = MIN((INT32)tile_width, state->xsize - x);
                current_tile_length = MIN((INT32)tile_length, state->ysize - y);
                // iterate over each line in the tile and stuff data into image
                for (tile_y = 0; tile_y < current_tile_length; tile_y++) {
                    shuffler(
                        (UINT8 *)im->image[tile_y + y] + x * im->pixelsize,
                        state->buffer + tile_y * row_byte_size,
                        current_tile_width
                    );
                }
            }
        }
    }

    return 0;
}

int
_decodeStrip(
    Imaging im,
    ImagingCodecState state,
    TIFF *tiff,
    int planes,
    ImagingShuffler *unpackers
) {
    INT32 strip_row = 0;
    UINT8 *new_data;
    UINT32 rows_per_strip;
    int ret;
    tsize_t strip_size, row_byte_size, unpacker_row_byte_size;

    ret = TIFFGetField(tiff, TIFFTAG_ROWSPERSTRIP, &rows_per_strip);
    if (ret != 1 || rows_per_strip == (UINT32)(-1)) {
        rows_per_strip = state->ysize;
    }

    if (rows_per_strip > INT_MAX) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    strip_size = TIFFStripSize(tiff);
    if (strip_size > INT_MAX - 1) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    unpacker_row_byte_size = (state->xsize * state->bits / planes + 7) / 8;
    if (strip_size > (unpacker_row_byte_size * rows_per_strip)) {
        // If the strip size as expected by LibTiff isn't what we're expecting, abort.
        // man:   TIFFStripSize returns the equivalent size for a strip of data as it
        // would be returned in a call to TIFFReadEncodedStrip ...
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }

    state->bytes = strip_size;

    row_byte_size = TIFFScanlineSize(tiff);

    // if the unpacker calculated row size is > row byte size, (at least) the last
    // row of the strip will have a read buffer overflow.
    if (row_byte_size == 0 || unpacker_row_byte_size > row_byte_size) {
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }

    /* realloc to fit whole strip */
    /* malloc check above */
    new_data = realloc(state->buffer, state->bytes);
    if (!new_data) {
        state->errcode = IMAGING_CODEC_MEMORY;
        return -1;
    }

    state->buffer = new_data;

    for (; state->y < state->ysize; state->y += rows_per_strip) {
        int plane;
        for (plane = 0; plane < planes; plane++) {
            ImagingShuffler shuffler = unpackers[plane];
            if (TIFFReadEncodedStrip(
                    tiff,
                    TIFFComputeStrip(tiff, state->y, plane),
                    (tdata_t)state->buffer,
                    strip_size
                ) == -1) {
                state->errcode = IMAGING_CODEC_BROKEN;
                return -1;
            }

            // iterate over each row in the strip and stuff data into image
            for (strip_row = 0;
                 strip_row < MIN((INT32)rows_per_strip, state->ysize - state->y);
                 strip_row++) {
                shuffler(
                    (UINT8 *)im->image[state->y + state->yoff + strip_row] +
                        state->xoff * im->pixelsize,
                    state->buffer + strip_row * row_byte_size,
                    state->xsize
                );
            }
        }
    }

    return 0;
}

int
ImagingLibTiffDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes
) {
    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
    char *filename = "tempfile.tif";
    char *mode = "rC";
    TIFF *tiff;
    uint16_t photometric = 0;  // init to not PHOTOMETRIC_YCBCR
    uint16_t compression;
    int readAsRGBA = 0;
    uint16_t planarconfig = 0;
    int planes = 1;
    ImagingShuffler unpackers[4];
    INT32 img_width, img_height;

    memset(unpackers, 0, sizeof(ImagingShuffler) * 4);

    /* buffer is the encoded file, bytes is the length of the encoded file */
    /*     it all ends up in state->buffer, which is a uint8* from Imaging.h */

    clientstate->size = bytes;
    clientstate->eof = clientstate->size;
    clientstate->loc = 0;
    clientstate->data = (tdata_t)buffer;
    clientstate->flrealloc = 0;

    TIFFSetWarningHandler(NULL);
    TIFFSetWarningHandlerExt(NULL);

    if (clientstate->fp) {
        lseek(clientstate->fp, 0, SEEK_SET);  // Sometimes, I get it set to the end.
        tiff = TIFFFdOpen(fd_to_tiff_fd(clientstate->fp), filename, mode);
    } else {
        tiff = TIFFClientOpen(
            filename,
            mode,
            (thandle_t)clientstate,
            _tiffReadProc,
            _tiffWriteProc,
            _tiffSeekProc,
            _tiffCloseProc,
            _tiffSizeProc,
            _tiffMapProc,
            _tiffUnmapProc
        );
    }

    if (!tiff) {
        state->errcode = IMAGING_CODEC_BROKEN;
        return -1;
    }

    if (clientstate->ifd) {
        int rv;
        uint32_t ifdoffset = clientstate->ifd;
        rv = TIFFSetSubDirectory(tiff, ifdoffset);
        if (!rv) {
            goto decode_err;
        }
    }

    TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, &img_width);
    TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &img_height);

    if (state->xsize != img_width || state->ysize != img_height) {
        state->errcode = IMAGING_CODEC_BROKEN;
        goto decode_err;
    }

    TIFFGetField(tiff, TIFFTAG_PHOTOMETRIC, &photometric);
    TIFFGetField(tiff, TIFFTAG_COMPRESSION, &compression);
    TIFFGetFieldDefaulted(tiff, TIFFTAG_PLANARCONFIG, &planarconfig);

    // Dealing with YCbCr images is complicated in case if subsampling
    // Let LibTiff read them as RGBA
    readAsRGBA = photometric == PHOTOMETRIC_YCBCR;

    if (readAsRGBA && compression == COMPRESSION_JPEG &&
        planarconfig == PLANARCONFIG_CONTIG) {
        // If using new JPEG compression, let libjpeg do RGB conversion for performance
        // reasons
        TIFFSetField(tiff, TIFFTAG_JPEGCOLORMODE, JPEGCOLORMODE_RGB);
        readAsRGBA = 0;
    }

    if (readAsRGBA) {
        _decodeAsRGBA(im, state, tiff);
    } else {
        planes = _pickUnpackers(im, state, tiff, planarconfig, unpackers);
        if (planes <= 0) {
            goto decode_err;
        }

        if (TIFFIsTiled(tiff)) {
            _decodeTile(im, state, tiff, planes, unpackers);
        } else {
            _decodeStrip(im, state, tiff, planes, unpackers);
        }

        if (!state->errcode) {
            // Check if raw mode was RGBa and it was stored on separate planes
            // so we have to convert it to RGBA
            if (planes > 3 && im->mode == IMAGING_MODE_RGBA) {
                uint16_t extrasamples;
                uint16_t *sampleinfo;
                ImagingShuffler shuffle;
                INT32 y;

                TIFFGetFieldDefaulted(
                    tiff, TIFFTAG_EXTRASAMPLES, &extrasamples, &sampleinfo
                );

                if (extrasamples >= 1 && (sampleinfo[0] == EXTRASAMPLE_UNSPECIFIED ||
                                          sampleinfo[0] == EXTRASAMPLE_ASSOCALPHA)) {
                    shuffle = ImagingFindUnpacker(
                        IMAGING_MODE_RGBA, IMAGING_RAWMODE_RGBa, NULL
                    );

                    for (y = state->yoff; y < state->ysize; y++) {
                        UINT8 *ptr = (UINT8 *)im->image[y + state->yoff] +
                                     state->xoff * im->pixelsize;
                        shuffle(ptr, ptr, state->xsize);
                    }
                }
            }
        }
    }

decode_err:
    // TIFFClose in libtiff calls tif_closeproc and TIFFCleanup
    if (clientstate->fp) {
        // Python will manage the closing of the file rather than libtiff
        // So only call TIFFCleanup
        TIFFCleanup(tiff);
    } else {
        // When tif_closeproc refers to our custom _tiffCloseProc though,
        // that is fine, as it does not close the file
        TIFFClose(tiff);
    }
    // Returning -1 here to force ImageFile.load to break, rather than
    // even think about looping back around.
    return -1;
}

int
ImagingLibTiffEncodeInit(ImagingCodecState state, char *filename, int fp) {
    // Open the FD or the pointer as a tiff file, for writing.
    // We may have to do some monkeying around to make this really work.
    // If we have a fp, then we're good.
    // If we have a memory string, we're probably going to have to malloc, then
    // shuffle bytes into the writescanline process.
    // Going to have to deal with the directory as well.

    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
    int bufsize = 64 * 1024;
    char *mode = "w";

    clientstate->loc = 0;
    clientstate->size = 0;
    clientstate->eof = 0;
    clientstate->data = 0;
    clientstate->flrealloc = 0;
    clientstate->fp = fp;

    state->state = 0;

    if (fp) {
        clientstate->tiff = TIFFFdOpen(fd_to_tiff_fd(clientstate->fp), filename, mode);
    } else {
        // calloc a buffer to write the tif, we're going to need to realloc or something
        // if we need bigger.
        /* calloc check ok, small constant allocation */
        clientstate->data = calloc(bufsize, 1);
        clientstate->size = bufsize;
        clientstate->flrealloc = 1;

        if (!clientstate->data) {
            return 0;
        }

        clientstate->tiff = TIFFClientOpen(
            filename,
            mode,
            (thandle_t)clientstate,
            _tiffReadProc,
            _tiffWriteProc,
            _tiffSeekProc,
            _tiffCloseProc,
            _tiffSizeProc,
            _tiffNullMapProc,
            _tiffUnmapProc
        ); /*force no mmap*/
    }

    if (!clientstate->tiff) {
        return 0;
    }

    return 1;
}

int
ImagingLibTiffMergeFieldInfo(
    ImagingCodecState state, TIFFDataType field_type, int key, int is_var_length
) {
    // Refer to libtiff docs (http://www.simplesystems.org/libtiff/addingtags.html)
    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
    uint32_t n;

    // custom fields added with ImagingLibTiffMergeFieldInfo are only used for
    // decoding, ignore readcount;
    int readcount = is_var_length ? TIFF_VARIABLE : 1;
    // we support writing a single value, or a variable number of values
    int writecount = is_var_length ? TIFF_VARIABLE : 1;
    // whether the first value should encode the number of values.
    int passcount = (is_var_length && field_type != TIFF_ASCII) ? 1 : 0;

    TIFFFieldInfo info[] = {
        {key,
         readcount,
         writecount,
         field_type,
         FIELD_CUSTOM,
         1,
         passcount,
         "CustomField"}
    };

    n = sizeof(info) / sizeof(info[0]);

    return TIFFMergeFieldInfo(clientstate->tiff, info, n);
}

int
ImagingLibTiffSetField(ImagingCodecState state, ttag_t tag, ...) {
    // after tif_dir.c->TIFFSetField.
    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
    va_list ap;
    int status;

    va_start(ap, tag);
    status = TIFFVSetField(clientstate->tiff, tag, ap);
    va_end(ap);
    return status;
}

int
ImagingLibTiffEncodeCleanup(ImagingCodecState state) {
    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
    TIFF *tiff = clientstate->tiff;

    if (!tiff) {
        return 0;
    }
    // TIFFClose in libtiff calls tif_closeproc and TIFFCleanup
    if (clientstate->fp) {
        // Python will manage the closing of the file rather than libtiff
        // So only call TIFFCleanup
        TIFFCleanup(tiff);
    } else {
        // When tif_closeproc refers to our custom _tiffCloseProc though,
        // that is fine, as it does not close the file
        TIFFClose(tiff);
    }
    return 0;
}

int
ImagingLibTiffEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes) {
    /* One shot encoder. Encode everything to the tiff in the clientstate.
       If we're running off of a FD, then run once, we're good, everything
       ends up in the file, we close and we're done.

       If we're going to memory, then we need to write the whole file into memory, then
       parcel it back out to the pystring buffer bytes at a time.

    */

    TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
    TIFF *tiff = clientstate->tiff;

    if (state->state == 0) {
        while (state->y < state->ysize) {
            state->shuffle(
                state->buffer,
                (UINT8 *)im->image[state->y + state->yoff] +
                    state->xoff * im->pixelsize,
                state->xsize
            );

            if (TIFFWriteScanline(
                    tiff, (tdata_t)(state->buffer), (uint32_t)state->y, 0
                ) == -1) {
                state->errcode = IMAGING_CODEC_BROKEN;

                if (clientstate->fp) {
                    TIFFCleanup(tiff);
                    clientstate->tiff = NULL;
                } else {
                    free(clientstate->data);
                }
                return -1;
            }
            state->y++;
        }

        if (state->y == state->ysize) {
            state->state = 1;

            if (!TIFFFlush(tiff)) {
                // likely reason is memory.
                state->errcode = IMAGING_CODEC_MEMORY;
                if (!clientstate->fp) {
                    free(clientstate->data);
                }
                return -1;
            }
            // reset the clientstate metadata to use it to read out the buffer.
            clientstate->loc = 0;
            clientstate->size = clientstate->eof;  // redundant?
        }
    }

    if (state->state == 1 && !clientstate->fp) {
        int read =
            (int)_tiffReadProc((thandle_t)clientstate, (tdata_t)buffer, (tsize_t)bytes);

        if (clientstate->loc == clientstate->eof) {
            state->errcode = IMAGING_CODEC_END;
            free(clientstate->data);
        }
        return read;
    }

    state->errcode = IMAGING_CODEC_END;
    return 0;
}

const char *
ImagingTiffVersion(void) {
    return TIFFGetVersion();
}

#endif
