/*
 * The Python Imaging Library
 * $Id$
 *
 * Windows DIB specifics
 *
 * Copyright (c) Secret Labs AB 1997-98.
 * Copyright (c) Fredrik Lundh 1996.
 *
 * See the README file for information on usage and redistribution.
 */

#ifdef WIN32

#if (defined(_MSC_VER) && _MSC_VER >= 1200) || (defined __GNUC__)
/* already defined in basetsd.h */
#undef INT32
#undef INT64
#undef UINT32
#endif

#include <windows.h>

#if defined(__cplusplus)
extern "C" {
#endif

struct ImagingDIBInstance {
    /* Windows interface */
    HDC dc;
    HBITMAP bitmap;
    HGDIOBJ old_bitmap;
    BITMAPINFO *info;
    UINT8 *bits;
    HPALETTE palette;
    /* Used by cut and paste */
    char mode[4];
    int xsize, ysize;
    int pixelsize;
    int linesize;
    ImagingShuffler pack;
    ImagingShuffler unpack;
};

typedef struct ImagingDIBInstance* ImagingDIB;

extern char* ImagingGetModeDIB(int size_out[2]);

extern ImagingDIB ImagingNewDIB(const char *mode, int xsize, int ysize);

extern void ImagingDeleteDIB(ImagingDIB im);

extern void ImagingDrawDIB(ImagingDIB dib, int dc, int dst[4], int src[4]);
extern void ImagingExposeDIB(ImagingDIB dib, int dc);

extern int ImagingQueryPaletteDIB(ImagingDIB dib, int dc);

extern void ImagingPasteDIB(ImagingDIB dib, Imaging im, int xy[4]);

#if defined(__cplusplus)
}
#endif

#endif
