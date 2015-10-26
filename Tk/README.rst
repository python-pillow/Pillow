Using PIL With Tkinter
====================================================================

Starting with 1.0 final (release candidate 2 and later, to be
precise), PIL can attach itself to Tkinter in flight.  As a result,
you no longer need to rebuild the Tkinter extension to be able to
use PIL.

However, if you cannot get the this to work on your platform, you
can do it in the old way:

Adding Tkinter support
----------------------

1. Compile Python's _tkinter.c with the WITH_APPINIT and WITH_PIL
   flags set, and link it with tkImaging.c and tkappinit.c.  To
   do this, copy the former to the Modules directory, and edit
   the _tkinter line in Setup (or Setup.in) according to the
   instructions in that file.

   NOTE: if you have an old Python version, the tkappinit.c
   file is not included by default.  If this is the case, you
   will have to add the following lines to tkappinit.c, after
   the MOREBUTTONS stuff::

	{
	    extern void TkImaging_Init(Tcl_Interp* interp);
	    TkImaging_Init(interp);
	}

   This registers a Tcl command called "PyImagingPhoto", which is
   use to communicate between PIL and Tk's PhotoImage handler.

   You must also change the _tkinter line in Setup (or Setup.in)
   to something like::

    _tkinter _tkinter.c tkImaging.c tkappinit.c -DWITH_APPINIT
    -I/usr/local/include -L/usr/local/lib -ltk8.0 -ltcl8.0 -lX11

The Photoimage Booster Patch (for Windows 95/NT)
====================================================================

This patch kit boosts performance for 16/24-bit displays.  The
first patch is required on Tk 4.2 (where it fixes the problems for
16-bit displays) and later versions.  By installing both patches,
Tk's PhotoImage handling becomes much faster on both 16-bit and
24-bit displays.  The patch has been tested with Tk 4.2 and 8.0.

Here's a benchmark, made with a sample program which loads two
512x512 greyscale PGM's, and two 512x512 colour PPM's, and displays
each of them in a separate toplevel windows.  Tcl/Tk was compiled
with Visual C 4.0, and run on a P100 under Win95.  Image load times
are not included in the timings:

+----------------------+------------+-------------+----------------+
|                      | **8-bit**  |  **16-bit** |  **24-bit**    |
+----------------------+------------+-------------+----------------+
| 1. original 4.2 code | 5.52 s     |  8.57 s     |  3.79 s        |
+----------------------+------------+-------------+----------------+
| 2. booster patch     | 5.49 s     |  1.87 s     |  1.82 s        |
+----------------------+------------+-------------+----------------+
|  speedup             | None       |  4.6x       |  2.1x          |
+----------------------+------------+-------------+----------------+

Here's the patches:

1. For portability and speed, the best thing under Windows is to
treat 16-bit displays as if they were 24-bit. The Windows device
drivers take care of the rest.

.. Note::

   If you have Tk 4.1 or Tk 8.0b1, you don't have to apply this
   patch!  It only applies to Tk 4.2, Tk 8.0a[12] and Tk 8.0b2.

In ``win/tkWinImage.c``, change the following line in ``XCreateImage``::

    imagePtr->bits_per_pixel = depth;

to::

    /* ==================================================================== */
    /* The tk photo image booster patch -- patch section 1                  */
    /* ==================================================================== */

        if (visual->class == TrueColor)
        /* true colour is stored as 3 bytes: (blue, green, red) */
        imagePtr->bits_per_pixel = 24;
        else
        imagePtr->bits_per_pixel = depth;

    /* ==================================================================== */


2. The DitherInstance implementation is not good.  It's especially
bad on highend truecolour displays.  IMO, it should be rewritten from
scratch (some other day...).

Anyway, the following band-aid makes the situation a little bit
better under Windows.  This hack trades some marginal quality (no
dithering on 16-bit displays) for a dramatic performance boost.
Requires patch 1, unless you're using Tk 4.1 or Tk 8.0b1.

In generic/tkImgPhoto.c, add the #ifdef section to the DitherInstance
function::

    /* ==================================================================== */

        for (; height > 0; height -= nLines) {
        if (nLines > height) {
            nLines = height;
        }
        dstLinePtr = (unsigned char *) imagePtr->data;
        yEnd = yStart + nLines;

    /* ==================================================================== */
    /* The tk photo image booster patch -- patch section 2                  */
    /* ==================================================================== */

    #ifdef __WIN32__
        if (colorPtr->visualInfo.class == TrueColor
            && instancePtr->gamma == 1.0) {
            /* Windows hicolor/truecolor booster */
            for (y = yStart; y < yEnd; ++y) {
            destBytePtr = dstLinePtr;
            srcPtr = srcLinePtr;
            for (x = xStart; x < xEnd; ++x) {
                destBytePtr[0] = srcPtr[2];
                destBytePtr[1] = srcPtr[1];
                destBytePtr[2] = srcPtr[0];
                destBytePtr += 3; srcPtr += 3;
            }
            srcLinePtr += lineLength;
            dstLinePtr += bytesPerLine;
            }
        } else
    #endif

    /* ==================================================================== */

        for (y = yStart; y < yEnd; ++y) {
            srcPtr = srcLinePtr;
            errPtr = errLinePtr;
            destBytePtr = dstLinePtr;

The PIL Bitmap Booster Patch
====================================================================

The pilbitmap booster patch greatly improves performance of the
ImageTk.BitmapImage constructor.  Unfortunately, the design of Tk
doesn't allow us to do this from the tkImaging interface module, so
you have to patch the Tk sources.

Once installed, the ImageTk module will automatically detect this
patch.

(Note: this patch has been tested with Tk 8.0 on Win32 only, but it
should work just fine on other platforms as well).

1. To the beginning of TkGetBitmapData (in generic/tkImgBmap.c), add
   the following stuff::

    /* ==================================================================== */

        int width, height, numBytes, hotX, hotY;
        char *p, *end, *expandedFileName;
        ParseInfo pi;
        char *data = NULL;
        Tcl_DString buffer;

    /* ==================================================================== */
    /* The pilbitmap booster patch -- patch section                         */
    /* ==================================================================== */

        char *PILGetBitmapData();

        if (string) {
            /* Is this a PIL bitmap reference? */
            data = PILGetBitmapData(string, widthPtr, heightPtr, hotXPtr, hotYPtr);
            if (data)
                return data;
        }

    /* ==================================================================== */

        pi.string = string;
        if (string == NULL) {
            if (Tcl_IsSafe(interp)) {

2. Append the following to the same file (you may wish to include
Imaging.h instead of copying the struct declaration...)::

    /* ==================================================================== */
    /* The pilbitmap booster patch -- code section                          */
    /* ==================================================================== */

    /* Imaging declaration boldly copied from Imaging.h (!) */

    typedef struct ImagingInstance *Imaging; /* a.k.a. ImagingImage :-) */

    typedef unsigned char UINT8;
    typedef int INT32;

    struct ImagingInstance {

        /* Format */
        char mode[4+1];     /* Band names ("1", "L", "P", "RGB", "RGBA", "CMYK") */
        int type;           /* Always 0 in this version */
        int depth;          /* Always 8 in this version */
        int bands;          /* Number of bands (1, 3, or 4) */
        int xsize;          /* Image dimension. */
        int ysize;

        /* Colour palette (for "P" images only) */
        void* palette;

        /* Data pointers */
        UINT8 **image8;     /* Set for 8-bit image (pixelsize=1). */
        INT32 **image32;    /* Set for 32-bit image (pixelsize=4). */

        /* Internals */
        char **image;       /* Actual raster data. */
        char *block;        /* Set if data is allocated in a single block. */

        int pixelsize;      /* Size of a pixel, in bytes (1 or 4) */
        int linesize;       /* Size of a line, in bytes (xsize * pixelsize) */

        /* Virtual methods */
        void (*im_delete)(Imaging *);

    };

    /* The pilbitmap booster patch allows you to pass PIL images to the
       Tk bitmap decoder.  Passing images this way is much more efficient
       than using the "tobitmap" method. */

    char *
    PILGetBitmapData(string, widthPtr, heightPtr, hotXPtr, hotYPtr)
        char *string;
        int *widthPtr, *heightPtr;
        int *hotXPtr, *hotYPtr;
    {
        char* data;
        char* p;
        int y;
        Imaging im;

        if (strncmp(string, "PIL:", 4) != 0)
            return NULL;

        im = (Imaging) atol(string + 4);

        if (strcmp(im->mode, "1") != 0 && strcmp(im->mode, "L") != 0)
            return NULL;

        data = p = (char *) ckalloc((unsigned) ((im->xsize+7)/8) * im->ysize);

        for (y = 0; y < im->ysize; y++) {
            char* in = im->image8[y];
            int i, m, b;
            b = 0; m = 1;
            for (i = 0; i < im->xsize; i++) {
                if (in[i] != 0)
                    b |= m;
                m <<= 1;
                if (m == 256){
                    *p++ = b;
                    b = 0; m = 1;
                }
            }
            if (m != 1)
                *p++ = b;
        }

        *widthPtr = im->xsize;
        *heightPtr = im->ysize;
        *hotXPtr = -1;
        *hotYPtr = -1;

        return data;
    }

    /* ==================================================================== */

3. Recompile Tk and relink the _tkinter module (where necessary).