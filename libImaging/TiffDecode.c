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

#ifndef uint
#define uint uint32
#endif

#include "TiffDecode.h"

void dump_state(const TIFFSTATE *state){
	TRACE(("State: Location %u size %d eof %d data: %p \n", (uint)state->loc,
		   (int)state->size, (uint)state->eof, state->data));
}

/*
  procs for TIFFOpenClient
*/

tsize_t _tiffReadProc(thandle_t hdata, tdata_t buf, tsize_t size) {
	TIFFSTATE *state = (TIFFSTATE *)hdata;
	tsize_t to_read;

	TRACE(("_tiffReadProc: %d \n", (int)size));
	dump_state(state);

	to_read = min(size, min(state->size, (tsize_t)state->eof) - (tsize_t)state->loc);
	TRACE(("to_read: %d\n", (int)to_read));

	_TIFFmemcpy(buf, (UINT8 *)state->data + state->loc, to_read);
	state->loc += (toff_t)to_read;

	TRACE( ("location: %u\n", (uint)state->loc));
	return to_read;
}

tsize_t _tiffWriteProc(thandle_t hdata, tdata_t buf, tsize_t size) {
	TIFFSTATE *state = (TIFFSTATE *)hdata;
	tsize_t to_write;

	TRACE(("_tiffWriteProc: %d \n", (int)size));
	dump_state(state);

	to_write = min(size, state->size - (tsize_t)state->loc);
	if (state->flrealloc && size>to_write) {
		tdata_t new;
		tsize_t newsize=state->size;
		while (newsize < (size + state->size)) {
			newsize += 64*1024;
			// newsize*=2; // UNDONE, by 64k chunks?
		}
		TRACE(("Reallocing in write to %d bytes\n", (int)newsize));
		new = realloc(state->data, newsize);
		if (!new) {
			// fail out
			return 0;
		}
		state->data = new;
		state->size = newsize;
		to_write = size;
	}

	TRACE(("to_write: %d\n", (int)to_write));

	_TIFFmemcpy((UINT8 *)state->data + state->loc, buf, to_write);
	state->loc += (toff_t)to_write;
	state->eof = max(state->loc, state->eof);

	dump_state(state);
	return to_write;
}

toff_t _tiffSeekProc(thandle_t hdata, toff_t off, int whence) {
	TIFFSTATE *state = (TIFFSTATE *)hdata;

	TRACE(("_tiffSeekProc: off: %u whence: %d \n", (uint)off, whence));
	dump_state(state);
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
	dump_state(state);
	return state->loc;
}

int _tiffCloseProc(thandle_t hdata) {
	TIFFSTATE *state = (TIFFSTATE *)hdata;

	TRACE(("_tiffCloseProc \n"));
	dump_state(state);

	return 0;
}


toff_t _tiffSizeProc(thandle_t hdata) {
	TIFFSTATE *state = (TIFFSTATE *)hdata;

	TRACE(("_tiffSizeProc \n"));
	dump_state(state);

	return (toff_t)state->size;
}
int _tiffMapProc(thandle_t hdata, tdata_t* pbase, toff_t* psize) {
	TIFFSTATE *state = (TIFFSTATE *)hdata;

	TRACE(("_tiffMapProc input size: %u, data: %p\n", (uint)*psize, *pbase));
	dump_state(state);

	*pbase = state->data;
	*psize = state->size;
	TRACE(("_tiffMapProc returning size: %u, data: %p\n", (uint)*psize, *pbase));
	return (1);
}

int _tiffNullMapProc(thandle_t hdata, tdata_t* pbase, toff_t* psize) {
	(void) hdata; (void) pbase; (void) psize;
	return (0);
}

void _tiffUnmapProc(thandle_t hdata, tdata_t base, toff_t size) {
	TRACE(("_tiffUnMapProc\n"));
	(void) hdata; (void) base; (void) size;
}

int ImagingLibTiffInit(ImagingCodecState state, int fp) {
	TIFFSTATE *clientstate = (TIFFSTATE *)state->context;

    TRACE(("initing libtiff\n"));
	TRACE(("filepointer: %d \n",  fp));
	TRACE(("State: count %d, state %d, x %d, y %d, ystep %d\n", state->count, state->state,
		   state->x, state->y, state->ystep));
	TRACE(("State: xsize %d, ysize %d, xoff %d, yoff %d \n", state->xsize, state->ysize,
		   state->xoff, state->yoff));
	TRACE(("State: bits %d, bytes %d \n", state->bits, state->bytes));
	TRACE(("State: context %p \n", state->context));

	clientstate->loc = 0;
	clientstate->size = 0;
	clientstate->data = 0;
	clientstate->fp = fp;
	clientstate->eof = 0;

    return 1;
}

int ImagingLibTiffDecode(Imaging im, ImagingCodecState state, UINT8* buffer, int bytes) {
	TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
	char *filename = "tempfile.tif";
	char *mode = "r";
	TIFF *tiff;
	int size;


	/* buffer is the encoded file, bytes is the length of the encoded file */
	/* 	it all ends up in state->buffer, which is a uint8* from Imaging.h */

    TRACE(("in decoder: bytes %d\n", bytes));
	TRACE(("State: count %d, state %d, x %d, y %d, ystep %d\n", state->count, state->state,
		   state->x, state->y, state->ystep));
	TRACE(("State: xsize %d, ysize %d, xoff %d, yoff %d \n", state->xsize, state->ysize,
		   state->xoff, state->yoff));
	TRACE(("State: bits %d, bytes %d \n", state->bits, state->bytes));
	TRACE(("Buffer: %p: %c%c%c%c\n", buffer, (char)buffer[0], (char)buffer[1],(char)buffer[2], (char)buffer[3]));
	TRACE(("State->Buffer: %c%c%c%c\n", (char)state->buffer[0], (char)state->buffer[1],(char)state->buffer[2], (char)state->buffer[3]));
	TRACE(("Image: mode %s, type %d, bands: %d, xsize %d, ysize %d \n",
		   im->mode, im->type, im->bands, im->xsize, im->ysize));
	TRACE(("Image: image8 %p, image32 %p, image %p, block %p \n",
		   im->image8, im->image32, im->image, im->block));
	TRACE(("Image: pixelsize: %d, linesize %d \n",
		   im->pixelsize, im->linesize));

	dump_state(clientstate);
	clientstate->size = bytes;
	clientstate->eof = clientstate->size;
	clientstate->loc = 0;
	clientstate->data = (tdata_t)buffer;
	clientstate->flrealloc = 0;

	dump_state(clientstate);

    TIFFSetWarningHandler(NULL);
    TIFFSetWarningHandlerExt(NULL);

	if (clientstate->fp) {
		TRACE(("Opening using fd: %d\n",clientstate->fp));
		lseek(clientstate->fp,0,SEEK_SET); // Sometimes, I get it set to the end.
		tiff = TIFFFdOpen(clientstate->fp, filename, mode);
	} else {
		TRACE(("Opening from string\n"));
		tiff = TIFFClientOpen(filename, mode,
							  (thandle_t) clientstate,
							  _tiffReadProc, _tiffWriteProc,
							  _tiffSeekProc, _tiffCloseProc, _tiffSizeProc,
							  _tiffMapProc, _tiffUnmapProc);
	}

	if (!tiff){
		TRACE(("Error, didn't get the tiff\n"));
		state->errcode = IMAGING_CODEC_BROKEN;
		return -1;
	}

	size = TIFFScanlineSize(tiff);
	TRACE(("ScanlineSize: %d \n", size));
	if (size > state->bytes) {
		TRACE(("Error, scanline size > buffer size\n"));
		state->errcode = IMAGING_CODEC_BROKEN;
		TIFFClose(tiff);
		return -1;
	}

	// Have to do this row by row and shove stuff into the buffer that way,
	// with shuffle.  (or, just alloc a buffer myself, then figure out how to get it
	// back in. Can't use read encoded stripe.

	// This thing pretty much requires that I have the whole image in one shot.
	// Prehaps a stub version would work better???
	while(state->y < state->ysize){
		if (TIFFReadScanline(tiff, (tdata_t)state->buffer, (uint32)state->y, 0) == -1) {
			TRACE(("Decode Error, row %d\n", state->y));
			state->errcode = IMAGING_CODEC_BROKEN;
			TIFFClose(tiff);
			return -1;
		}
		/* TRACE(("Decoded row %d \n", state->y)); */
		state->shuffle((UINT8*) im->image[state->y + state->yoff] +
					       state->xoff * im->pixelsize,
					   state->buffer,
					   state->xsize);

		state->y++;
	}

	TIFFClose(tiff);
	TRACE(("Done Decoding, Returning \n"));
	// Returning -1 here to force ImageFile.load to break, rather than
	// even think about looping back around.
	return -1;
}

int ImagingLibTiffEncodeInit(ImagingCodecState state, char *filename, int fp) {
	// Open the FD or the pointer as a tiff file, for writing.
	// We may have to do some monkeying around to make this really work.
	// If we have a fp, then we're good.
	// If we have a memory string, we're probably going to have to malloc, then
	// shuffle bytes into the writescanline process.
	// Going to have to deal with the directory as well.

	TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
	int bufsize = 64*1024;
	char *mode = "w";

    TRACE(("initing libtiff\n"));
	TRACE(("Filename %s, filepointer: %d \n", filename,  fp));
	TRACE(("State: count %d, state %d, x %d, y %d, ystep %d\n", state->count, state->state,
		   state->x, state->y, state->ystep));
	TRACE(("State: xsize %d, ysize %d, xoff %d, yoff %d \n", state->xsize, state->ysize,
		   state->xoff, state->yoff));
	TRACE(("State: bits %d, bytes %d \n", state->bits, state->bytes));
	TRACE(("State: context %p \n", state->context));

	clientstate->loc = 0;
	clientstate->size = 0;
	clientstate->eof =0;
	clientstate->data = 0;
	clientstate->flrealloc = 0;
	clientstate->fp = fp;

	state->state = 0;

	if (fp) {
		TRACE(("Opening using fd: %d for writing \n",clientstate->fp));
		clientstate->tiff = TIFFFdOpen(clientstate->fp, filename, mode);
	} else {
		// malloc a buffer to write the tif, we're going to need to realloc or something if we need bigger.
		TRACE(("Opening a buffer for writing \n"));
		clientstate->data = malloc(bufsize);
		clientstate->size = bufsize;
		clientstate->flrealloc=1;

		if (!clientstate->data) {
			TRACE(("Error, couldn't allocate a buffer of size %d\n", bufsize));
			return 0;
		}

		clientstate->tiff = TIFFClientOpen(filename, mode,
										   (thandle_t) clientstate,
										   _tiffReadProc, _tiffWriteProc,
										   _tiffSeekProc, _tiffCloseProc, _tiffSizeProc,
										   _tiffNullMapProc, _tiffUnmapProc); /*force no mmap*/

	}

	if (!clientstate->tiff) {
		TRACE(("Error, couldn't open tiff file\n"));
		return 0;
	}

    return 1;

}

int ImagingLibTiffSetField(ImagingCodecState state, ttag_t tag, ...){
	// after tif_dir.c->TIFFSetField.
	TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
	va_list ap;
	int status;

	va_start(ap, tag);
	status = TIFFVSetField(clientstate->tiff, tag, ap);
	va_end(ap);
	return status;
}


int ImagingLibTiffEncode(Imaging im, ImagingCodecState state, UINT8* buffer, int bytes) {
	/* One shot encoder. Encode everything to the tiff in the clientstate.
	   If we're running off of a FD, then run once, we're good, everything
	   ends up in the file, we close and we're done.

	   If we're going to memory, then we need to write the whole file into memory, then
	   parcel it back out to the pystring buffer bytes at a time.

	*/

	TIFFSTATE *clientstate = (TIFFSTATE *)state->context;
	TIFF *tiff = clientstate->tiff;

    TRACE(("in encoder: bytes %d\n", bytes));
	TRACE(("State: count %d, state %d, x %d, y %d, ystep %d\n", state->count, state->state,
		   state->x, state->y, state->ystep));
	TRACE(("State: xsize %d, ysize %d, xoff %d, yoff %d \n", state->xsize, state->ysize,
		   state->xoff, state->yoff));
	TRACE(("State: bits %d, bytes %d \n", state->bits, state->bytes));
	TRACE(("Buffer: %p: %c%c%c%c\n", buffer, (char)buffer[0], (char)buffer[1],(char)buffer[2], (char)buffer[3]));
	TRACE(("State->Buffer: %c%c%c%c\n", (char)state->buffer[0], (char)state->buffer[1],(char)state->buffer[2], (char)state->buffer[3]));
	TRACE(("Image: mode %s, type %d, bands: %d, xsize %d, ysize %d \n",
		   im->mode, im->type, im->bands, im->xsize, im->ysize));
	TRACE(("Image: image8 %p, image32 %p, image %p, block %p \n",
		   im->image8, im->image32, im->image, im->block));
	TRACE(("Image: pixelsize: %d, linesize %d \n",
		   im->pixelsize, im->linesize));

	dump_state(clientstate);

	if (state->state == 0) {
		TRACE(("Encoding line bt line"));
		while(state->y < state->ysize){
			state->shuffle(state->buffer,
						   (UINT8*) im->image[state->y + state->yoff] +
						   state->xoff * im->pixelsize,
						   state->xsize);

			if (TIFFWriteScanline(tiff, (tdata_t)(state->buffer), (uint32)state->y, 0) == -1) {
				TRACE(("Encode Error, row %d\n", state->y));
				state->errcode = IMAGING_CODEC_BROKEN;
				TIFFClose(tiff);
				if (!clientstate->fp){
					free(clientstate->data);
				}
				return -1;
			}
			state->y++;
		}

		if (state->y == state->ysize) {
			state->state=1;

			TRACE(("Flushing \n"));
			if (!TIFFFlush(tiff)) {
				TRACE(("Error flushing the tiff"));
				// likely reason is memory.
				state->errcode = IMAGING_CODEC_MEMORY;
				TIFFClose(tiff);
				if (!clientstate->fp){
					free(clientstate->data);
				}
				return -1;
			}
			TRACE(("Closing \n"));
			TIFFClose(tiff);
			// reset the clientstate metadata to use it to read out the buffer.
			clientstate->loc = 0;
			clientstate->size = clientstate->eof; // redundant?
		}
	}

	if (state->state == 1 && !clientstate->fp) {
		int read = (int)_tiffReadProc(clientstate, (tdata_t)buffer, (tsize_t)bytes);
		TRACE(("Buffer: %p: %c%c%c%c\n", buffer, (char)buffer[0], (char)buffer[1],(char)buffer[2], (char)buffer[3]));
		if (clientstate->loc == clientstate->eof) {
			TRACE(("Hit EOF, calling an end, freeing data"));
			state->errcode = IMAGING_CODEC_END;
			free(clientstate->data);
		}
		return read;
	}

	state->errcode = IMAGING_CODEC_END;
	return 0;
}
#endif
