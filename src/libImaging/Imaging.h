/*
 * The Python Imaging Library
 * $Id$
 *
 * declarations for the imaging core library
 *
 * Copyright (c) 1997-2005 by Secret Labs AB
 * Copyright (c) 1995-2005 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

#include "ImPlatform.h"

#if defined(__cplusplus)
extern "C" {
#endif

#ifndef M_PI
#define M_PI 3.1415926535897932384626433832795
#endif

/* -------------------------------------------------------------------- */

/*
 * Image data organization:
 *
 * mode     bytes       byte order
 * -------------------------------
 * 1        1           1
 * L        1           L
 * P        1           P
 * I        4           I (32-bit integer, native byte order)
 * F        4           F (32-bit IEEE float, native byte order)
 * RGB      4           R, G, B, -
 * RGBA     4           R, G, B, A
 * CMYK     4           C, M, Y, K
 * YCbCr    4           Y, Cb, Cr, -
 * Lab      4           L, a, b, -
 *
 * experimental modes (incomplete):
 * LA       4           L, -, -, A
 * PA       4           P, -, -, A
 * I;16     2           I (16-bit integer, native byte order)
 *
 * "P" is an 8-bit palette mode, which should be mapped through the
 * palette member to get an output image.  Check palette->mode to
 * find the corresponding "real" mode.
 *
 * For information on how to access Imaging objects from your own C
 * extensions, see http://www.effbot.org/zone/pil-extending.htm
 */

/* Handles */

typedef struct ImagingMemoryInstance *Imaging;

typedef struct ImagingAccessInstance *ImagingAccess;
typedef struct ImagingHistogramInstance *ImagingHistogram;
typedef struct ImagingOutlineInstance *ImagingOutline;
typedef struct ImagingPaletteInstance *ImagingPalette;

/* handle magics (used with PyCObject). */
#define IMAGING_MAGIC "PIL Imaging"

/* pixel types */
#define IMAGING_TYPE_UINT8 0
#define IMAGING_TYPE_INT32 1
#define IMAGING_TYPE_FLOAT32 2
#define IMAGING_TYPE_SPECIAL 3 /* check mode for details */

#define IMAGING_MODE_LENGTH \
    6 + 1 /* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "BGR;xy") */

typedef struct {
    char *ptr;
    int size;
} ImagingMemoryBlock;

struct ImagingMemoryInstance {
    /* Format */
    char mode[IMAGING_MODE_LENGTH]; /* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK",
                                       "YCbCr", "BGR;xy") */
    int type;                       /* Data type (IMAGING_TYPE_*) */
    int depth;                      /* Depth (ignored in this version) */
    int bands;                      /* Number of bands (1, 2, 3, or 4) */
    int xsize;                      /* Image dimension. */
    int ysize;

    /* Colour palette (for "P" images only) */
    ImagingPalette palette;

    /* Data pointers */
    UINT8 **image8;  /* Set for 8-bit images (pixelsize=1). */
    INT32 **image32; /* Set for 32-bit images (pixelsize=4). */

    /* Internals */
    char **image;               /* Actual raster data. */
    char *block;                /* Set if data is allocated in a single block. */
    ImagingMemoryBlock *blocks; /* Memory blocks for pixel storage */

    int pixelsize; /* Size of a pixel, in bytes (1, 2 or 4) */
    int linesize;  /* Size of a line, in bytes (xsize * pixelsize) */

    /* Virtual methods */
    void (*destroy)(Imaging im);
};

#define IMAGING_PIXEL_1(im, x, y) ((im)->image8[(y)][(x)])
#define IMAGING_PIXEL_L(im, x, y) ((im)->image8[(y)][(x)])
#define IMAGING_PIXEL_LA(im, x, y) ((im)->image[(y)][(x)*4])
#define IMAGING_PIXEL_P(im, x, y) ((im)->image8[(y)][(x)])
#define IMAGING_PIXEL_PA(im, x, y) ((im)->image[(y)][(x)*4])
#define IMAGING_PIXEL_I(im, x, y) ((im)->image32[(y)][(x)])
#define IMAGING_PIXEL_F(im, x, y) (((FLOAT32 *)(im)->image32[y])[x])
#define IMAGING_PIXEL_RGB(im, x, y) ((im)->image[(y)][(x)*4])
#define IMAGING_PIXEL_RGBA(im, x, y) ((im)->image[(y)][(x)*4])
#define IMAGING_PIXEL_CMYK(im, x, y) ((im)->image[(y)][(x)*4])
#define IMAGING_PIXEL_YCbCr(im, x, y) ((im)->image[(y)][(x)*4])

#define IMAGING_PIXEL_UINT8(im, x, y) ((im)->image8[(y)][(x)])
#define IMAGING_PIXEL_INT32(im, x, y) ((im)->image32[(y)][(x)])
#define IMAGING_PIXEL_FLOAT32(im, x, y) (((FLOAT32 *)(im)->image32[y])[x])

struct ImagingAccessInstance {
    const char *mode;
    void *(*line)(Imaging im, int x, int y);
    void (*get_pixel)(Imaging im, int x, int y, void *pixel);
    void (*put_pixel)(Imaging im, int x, int y, const void *pixel);
};

struct ImagingHistogramInstance {
    /* Format */
    char mode[IMAGING_MODE_LENGTH]; /* Band names (of corresponding source image) */
    int bands;                      /* Number of bands (1, 3, or 4) */

    /* Data */
    long *histogram; /* Histogram (bands*256 longs) */
};

struct ImagingPaletteInstance {
    /* Format */
    char mode[IMAGING_MODE_LENGTH]; /* Band names */

    /* Data */
    UINT8 palette[1024]; /* Palette data (same format as image data) */

    INT16 *cache;   /* Palette cache (used for predefined palettes) */
    int keep_cache; /* This palette will be reused; keep cache */
};

typedef struct ImagingMemoryArena {
    int alignment;     /* Alignment in memory of each line of an image */
    int block_size;    /* Preferred block size, bytes */
    int blocks_max;    /* Maximum number of cached blocks */
    int blocks_cached; /* Current number of blocks not associated with images */
    ImagingMemoryBlock *blocks_pool;
    int stats_new_count;        /* Number of new allocated images */
    int stats_allocated_blocks; /* Number of allocated blocks */
    int stats_reused_blocks;    /* Number of blocks which were retrieved from a pool */
    int stats_reallocated_blocks; /* Number of blocks which were actually reallocated
                                     after retrieving */
    int stats_freed_blocks;       /* Number of freed blocks */
} * ImagingMemoryArena;

/* Objects */
/* ------- */

extern struct ImagingMemoryArena ImagingDefaultArena;
extern int
ImagingMemorySetBlocksMax(ImagingMemoryArena arena, int blocks_max);
extern void
ImagingMemoryClearCache(ImagingMemoryArena arena, int new_size);

extern Imaging
ImagingNew(const char *mode, int xsize, int ysize);
extern Imaging
ImagingNewDirty(const char *mode, int xsize, int ysize);
extern Imaging
ImagingNew2Dirty(const char *mode, Imaging imOut, Imaging imIn);
extern void
ImagingDelete(Imaging im);

extern Imaging
ImagingNewBlock(const char *mode, int xsize, int ysize);

extern Imaging
ImagingNewPrologue(const char *mode, int xsize, int ysize);
extern Imaging
ImagingNewPrologueSubtype(const char *mode, int xsize, int ysize, int structure_size);

extern void
ImagingCopyPalette(Imaging destination, Imaging source);

extern void
ImagingHistogramDelete(ImagingHistogram histogram);

extern void
ImagingAccessInit(void);
extern ImagingAccess
ImagingAccessNew(Imaging im);
extern void
_ImagingAccessDelete(Imaging im, ImagingAccess access);
#define ImagingAccessDelete(im, access) /* nop, for now */

extern ImagingPalette
ImagingPaletteNew(const char *mode);
extern ImagingPalette
ImagingPaletteNewBrowser(void);
extern ImagingPalette
ImagingPaletteDuplicate(ImagingPalette palette);
extern void
ImagingPaletteDelete(ImagingPalette palette);

extern int
ImagingPaletteCachePrepare(ImagingPalette palette);
extern void
ImagingPaletteCacheUpdate(ImagingPalette palette, int r, int g, int b);
extern void
ImagingPaletteCacheDelete(ImagingPalette palette);

#define ImagingPaletteCache(p, r, g, b) \
    p->cache[(r >> 2) + (g >> 2) * 64 + (b >> 2) * 64 * 64]

extern Imaging
ImagingQuantize(Imaging im, int colours, int mode, int kmeans);

/* Threading */
/* --------- */

typedef void *ImagingSectionCookie;

extern void
ImagingSectionEnter(ImagingSectionCookie *cookie);
extern void
ImagingSectionLeave(ImagingSectionCookie *cookie);

/* Exceptions */
/* ---------- */

extern void *
ImagingError_OSError(void);
extern void *
ImagingError_MemoryError(void);
extern void *
ImagingError_ModeError(void); /* maps to ValueError by default */
extern void *
ImagingError_Mismatch(void); /* maps to ValueError by default */
extern void *
ImagingError_ValueError(const char *message);
extern void
ImagingError_Clear(void);

/* Transform callbacks */
/* ------------------- */

/* standard transforms */
#define IMAGING_TRANSFORM_AFFINE 0
#define IMAGING_TRANSFORM_PERSPECTIVE 2
#define IMAGING_TRANSFORM_QUAD 3

/* standard filters */
#define IMAGING_TRANSFORM_NEAREST 0
#define IMAGING_TRANSFORM_BOX 4
#define IMAGING_TRANSFORM_BILINEAR 2
#define IMAGING_TRANSFORM_HAMMING 5
#define IMAGING_TRANSFORM_BICUBIC 3
#define IMAGING_TRANSFORM_LANCZOS 1

typedef int (*ImagingTransformMap)(double *X, double *Y, int x, int y, void *data);
typedef int (*ImagingTransformFilter)(void *out, Imaging im, double x, double y);

/* Image Manipulation Methods */
/* -------------------------- */

extern Imaging
ImagingAlphaComposite(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingBlend(Imaging imIn1, Imaging imIn2, float alpha);
extern Imaging
ImagingCopy(Imaging im);
extern Imaging
ImagingConvert(Imaging im, const char *mode, ImagingPalette palette, int dither);
extern Imaging
ImagingConvertInPlace(Imaging im, const char *mode);
extern Imaging
ImagingConvertMatrix(Imaging im, const char *mode, float m[]);
extern Imaging
ImagingConvertTransparent(Imaging im, const char *mode, int r, int g, int b);
extern Imaging
ImagingCrop(Imaging im, int x0, int y0, int x1, int y1);
extern Imaging
ImagingExpand(Imaging im, int x, int y, int mode);
extern Imaging
ImagingFill(Imaging im, const void *ink);
extern int
ImagingFill2(
    Imaging into, const void *ink, Imaging mask, int x0, int y0, int x1, int y1);
extern Imaging
ImagingFillBand(Imaging im, int band, int color);
extern Imaging
ImagingFillLinearGradient(const char *mode);
extern Imaging
ImagingFillRadialGradient(const char *mode);
extern Imaging
ImagingFilter(Imaging im, int xsize, int ysize, const FLOAT32 *kernel, FLOAT32 offset);
extern Imaging
ImagingFlipLeftRight(Imaging imOut, Imaging imIn);
extern Imaging
ImagingFlipTopBottom(Imaging imOut, Imaging imIn);
extern Imaging
ImagingGaussianBlur(Imaging imOut, Imaging imIn, float radius, int passes);
extern Imaging
ImagingGetBand(Imaging im, int band);
extern Imaging
ImagingMerge(const char *mode, Imaging bands[4]);
extern int
ImagingSplit(Imaging im, Imaging bands[4]);
extern int
ImagingGetBBox(Imaging im, int bbox[4]);
typedef struct {
    int x, y;
    INT32 count;
    INT32 pixel;
} ImagingColorItem;
extern ImagingColorItem *
ImagingGetColors(Imaging im, int maxcolors, int *colors);
extern int
ImagingGetExtrema(Imaging im, void *extrema);
extern int
ImagingGetProjection(Imaging im, UINT8 *xproj, UINT8 *yproj);
extern ImagingHistogram
ImagingGetHistogram(Imaging im, Imaging mask, void *extrema);
extern Imaging
ImagingModeFilter(Imaging im, int size);
extern Imaging
ImagingNegative(Imaging im);
extern Imaging
ImagingOffset(Imaging im, int xoffset, int yoffset);
extern int
ImagingPaste(Imaging into, Imaging im, Imaging mask, int x0, int y0, int x1, int y1);
extern Imaging
ImagingPoint(Imaging im, const char *tablemode, const void *table);
extern Imaging
ImagingPointTransform(Imaging imIn, double scale, double offset);
extern Imaging
ImagingPutBand(Imaging im, Imaging imIn, int band);
extern Imaging
ImagingRankFilter(Imaging im, int size, int rank);
extern Imaging
ImagingRotate90(Imaging imOut, Imaging imIn);
extern Imaging
ImagingRotate180(Imaging imOut, Imaging imIn);
extern Imaging
ImagingRotate270(Imaging imOut, Imaging imIn);
extern Imaging
ImagingTranspose(Imaging imOut, Imaging imIn);
extern Imaging
ImagingTransverse(Imaging imOut, Imaging imIn);
extern Imaging
ImagingResample(Imaging imIn, int xsize, int ysize, int filter, float box[4]);
extern Imaging
ImagingReduce(Imaging imIn, int xscale, int yscale, int box[4]);
extern Imaging
ImagingTransform(
    Imaging imOut,
    Imaging imIn,
    int method,
    int x0,
    int y0,
    int x1,
    int y1,
    double *a,
    int filter,
    int fill);
extern Imaging
ImagingUnsharpMask(Imaging imOut, Imaging im, float radius, int percent, int threshold);
extern Imaging
ImagingBoxBlur(Imaging imOut, Imaging imIn, float radius, int n);
extern Imaging
ImagingColorLUT3D_linear(
    Imaging imOut,
    Imaging imIn,
    int table_channels,
    int size1D,
    int size2D,
    int size3D,
    INT16 *table);

extern Imaging
ImagingCopy2(Imaging imOut, Imaging imIn);
extern Imaging
ImagingConvert2(Imaging imOut, Imaging imIn);

/* Channel operations */
/* any mode, except "F" */
extern Imaging
ImagingChopLighter(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopDarker(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopDifference(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopMultiply(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopScreen(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopAdd(Imaging imIn1, Imaging imIn2, float scale, int offset);
extern Imaging
ImagingChopSubtract(Imaging imIn1, Imaging imIn2, float scale, int offset);
extern Imaging
ImagingChopAddModulo(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopSubtractModulo(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopSoftLight(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopHardLight(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingOverlay(Imaging imIn1, Imaging imIn2);

/* "1" images only */
extern Imaging
ImagingChopAnd(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopOr(Imaging imIn1, Imaging imIn2);
extern Imaging
ImagingChopXor(Imaging imIn1, Imaging imIn2);

/* Graphics */
extern int
ImagingDrawArc(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink,
    int width,
    int op);
extern int
ImagingDrawBitmap(Imaging im, int x0, int y0, Imaging bitmap, const void *ink, int op);
extern int
ImagingDrawChord(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink,
    int fill,
    int width,
    int op);
extern int
ImagingDrawEllipse(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    const void *ink,
    int fill,
    int width,
    int op);
extern int
ImagingDrawLine(Imaging im, int x0, int y0, int x1, int y1, const void *ink, int op);
extern int
ImagingDrawWideLine(
    Imaging im, int x0, int y0, int x1, int y1, const void *ink, int width, int op);
extern int
ImagingDrawPieslice(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink,
    int fill,
    int width,
    int op);
extern int
ImagingDrawPoint(Imaging im, int x, int y, const void *ink, int op);
extern int
ImagingDrawPolygon(Imaging im, int points, int *xy, const void *ink, int fill, int op);
extern int
ImagingDrawRectangle(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    const void *ink,
    int fill,
    int width,
    int op);

/* Level 2 graphics (WORK IN PROGRESS) */
extern ImagingOutline
ImagingOutlineNew(void);
extern void
ImagingOutlineDelete(ImagingOutline outline);

extern int
ImagingDrawOutline(
    Imaging im, ImagingOutline outline, const void *ink, int fill, int op);

extern int
ImagingOutlineMove(ImagingOutline outline, float x, float y);
extern int
ImagingOutlineLine(ImagingOutline outline, float x, float y);
extern int
ImagingOutlineCurve(
    ImagingOutline outline, float x1, float y1, float x2, float y2, float x3, float y3);
extern int
ImagingOutlineTransform(ImagingOutline outline, double a[6]);

extern int
ImagingOutlineClose(ImagingOutline outline);

/* Special effects */
extern Imaging
ImagingEffectSpread(Imaging imIn, int distance);
extern Imaging
ImagingEffectNoise(int xsize, int ysize, float sigma);
extern Imaging
ImagingEffectMandelbrot(int xsize, int ysize, double extent[4], int quality);

/* File I/O */
/* -------- */

/* Built-in drivers */
extern Imaging
ImagingOpenPPM(const char *filename);
extern int
ImagingSavePPM(Imaging im, const char *filename);

/* Codecs */
typedef struct ImagingCodecStateInstance *ImagingCodecState;
typedef int (*ImagingCodec)(
    Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);

extern int
ImagingBcnDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingBitDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingEpsEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingFliDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingGifDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingGifEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingHexDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
#ifdef HAVE_LIBJPEG
extern int
ImagingJpegDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingJpegDecodeCleanup(ImagingCodecState state);
extern int
ImagingJpegUseJCSExtensions(void);

extern int
ImagingJpegEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
#endif
#ifdef HAVE_OPENJPEG
extern int
ImagingJpeg2KDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingJpeg2KDecodeCleanup(ImagingCodecState state);
extern int
ImagingJpeg2KEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingJpeg2KEncodeCleanup(ImagingCodecState state);
#endif
#ifdef HAVE_LIBTIFF
extern int
ImagingLibTiffDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingLibTiffEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
#endif
#ifdef HAVE_LIBMPEG
extern int
ImagingMpegDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
#endif
extern int
ImagingMspDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingPackbitsDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingPcdDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingPcxDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingPcxEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingRawDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingRawEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingSgiRleDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingSunRleDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingTgaRleDecode(
    Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingTgaRleEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingXbmDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingXbmEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
#ifdef HAVE_LIBZ
extern int
ImagingZipDecode(Imaging im, ImagingCodecState state, UINT8 *buffer, Py_ssize_t bytes);
extern int
ImagingZipDecodeCleanup(ImagingCodecState state);
extern int
ImagingZipEncode(Imaging im, ImagingCodecState state, UINT8 *buffer, int bytes);
extern int
ImagingZipEncodeCleanup(ImagingCodecState state);
#endif

typedef void (*ImagingShuffler)(UINT8 *out, const UINT8 *in, int pixels);

/* Public shufflers */
extern void
ImagingPackBGR(UINT8 *out, const UINT8 *in, int pixels);
extern void
ImagingUnpackYCC(UINT8 *out, const UINT8 *in, int pixels);
extern void
ImagingUnpackYCCA(UINT8 *out, const UINT8 *in, int pixels);

extern void
ImagingConvertRGB2YCbCr(UINT8 *out, const UINT8 *in, int pixels);
extern void
ImagingConvertYCbCr2RGB(UINT8 *out, const UINT8 *in, int pixels);

extern ImagingShuffler
ImagingFindUnpacker(const char *mode, const char *rawmode, int *bits_out);
extern ImagingShuffler
ImagingFindPacker(const char *mode, const char *rawmode, int *bits_out);

struct ImagingCodecStateInstance {
    int count;
    int state;
    int errcode;
    int x, y;
    int ystep;
    int xsize, ysize, xoff, yoff;
    ImagingShuffler shuffle;
    int bits, bytes;
    UINT8 *buffer;
    void *context;
    PyObject *fd;
};

/* Codec read/write python fd */
extern Py_ssize_t
_imaging_read_pyFd(PyObject *fd, char *dest, Py_ssize_t bytes);
extern Py_ssize_t
_imaging_write_pyFd(PyObject *fd, char *src, Py_ssize_t bytes);
extern int
_imaging_seek_pyFd(PyObject *fd, Py_ssize_t offset, int whence);
extern Py_ssize_t
_imaging_tell_pyFd(PyObject *fd);

/* Errcodes */
#define IMAGING_CODEC_END 1
#define IMAGING_CODEC_OVERRUN -1
#define IMAGING_CODEC_BROKEN -2
#define IMAGING_CODEC_UNKNOWN -3
#define IMAGING_CODEC_CONFIG -8
#define IMAGING_CODEC_MEMORY -9

#include "ImagingUtils.h"
extern UINT8 *clip8_lookups;

#if defined(__cplusplus)
}
#endif
